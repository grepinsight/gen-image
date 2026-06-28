"""CLI interface for gen-image."""

from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.prompt import Confirm
from typing_extensions import Annotated

from .config import ConfigManager, load_config_env
from .cost_tracker import CostTracker
from .gemini_generator import GeminiGenerator
from .generator import ImageGenerator
from .interactive import run_interactive_session
from .styles import StylePreset, list_styles
from .templates import TemplateManager
from .utils import copy_to_clipboard, get_unique_filename

# Load API keys from ~/.config/gen-image/.env so non-interactive callers
# (launchd, dream cron, skills) get the provider key without a shell export.
# Real environment exports still win (see config.load_config_env).
load_config_env()

app = typer.Typer(
    name="gen-image",
    help="Educational image generator (OpenAI + Google Gemini)",
    add_completion=False,
)
console = Console()


AVAILABLE_MODELS = {
    "gemini": [
        ("gemini-3.1-flash-image-preview", "Latest, fast, up to 4K"),
        ("gemini-3-pro-image-preview", "Studio quality, reasoning, best text rendering"),
        ("gemini-2.5-flash-image", "Legacy"),
    ],
    "openai": [
        ("gpt-image-2", "Latest (2026-04-21), best quality"),
        ("gpt-image-1.5", "Strong quality, prior flagship"),
        ("gpt-image-1", "Standard"),
        ("gpt-image-1-mini", "Cost-effective"),
        ("dall-e-3", "Legacy, EOL May 2026"),
    ],
}


def _display_models(config):
    """Display all available image models."""
    current_provider = config.api.provider
    current_model = config.api.model

    console.print()
    console.print("[bold cyan]Available Image Models[/bold cyan]")
    console.print("=" * 55)

    for provider, models in AVAILABLE_MODELS.items():
        console.print(f"\n[bold]{provider.upper()}[/bold]")
        for model_id, description in models:
            active = model_id == current_model and provider == current_provider
            marker = " [green]<-- active[/green]" if active else ""
            console.print(f"  {model_id:42} {description}{marker}")

    console.print()
    console.print(f"Current: [bold]{current_provider}[/bold] / [bold]{current_model}[/bold]")
    console.print("Change: gen-image --edit-config")
    console.print()


def parse_vars(var_list: List[str]) -> Dict[str, str]:
    """Parse --var key=value arguments into dict."""
    variables = {}
    for var_str in var_list:
        if "=" not in var_str:
            raise ValueError(f"Invalid --var format: '{var_str}'. Use: --var key=value")
        key, value = var_str.split("=", 1)
        variables[key.strip()] = value.strip()
    return variables


@app.command()
def generate(
    prompt: Annotated[
        Optional[str],
        typer.Argument(help="Image description/prompt"),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o", help="Output file path (required unless using info commands)"
        ),
    ] = None,
    template: Annotated[
        Optional[str],
        typer.Option("--template", "-t", help="Use template for prompt"),
    ] = None,
    var: Annotated[
        Optional[List[str]],
        typer.Option("--var", help="Template variable (format: key=value)"),
    ] = None,
    style: Annotated[
        StylePreset,
        typer.Option("--style", "-s", help="Style preset to use"),
    ] = StylePreset.EDUCATIONAL_CARTOON,
    quality: Annotated[
        str,
        typer.Option("--quality", "-q", help="Image quality (standard or hd)"),
    ] = "standard",
    size: Annotated[
        str,
        typer.Option("--size", help="Image dimensions"),
    ] = "1024x1024",
    show_prompt: Annotated[
        bool,
        typer.Option("--show-prompt", help="Display the full prompt before generating"),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be generated without calling API"),
    ] = False,
    # Discovery commands
    list_styles_flag: Annotated[
        bool,
        typer.Option("--list-styles", help="List all available style presets"),
    ] = False,
    list_templates: Annotated[
        bool,
        typer.Option("--list-templates", help="List all available templates"),
    ] = False,
    show_template: Annotated[
        Optional[str],
        typer.Option("--show-template", help="Show template details"),
    ] = None,
    edit_template: Annotated[
        Optional[str],
        typer.Option("--edit-template", help="Edit template in $EDITOR"),
    ] = None,
    # History commands
    history: Annotated[
        bool,
        typer.Option("--history", help="Show generation history"),
    ] = False,
    history_limit: Annotated[
        int,
        typer.Option("--history-limit", help="Limit history results"),
    ] = 10,
    history_search: Annotated[
        Optional[str],
        typer.Option("--history-search", help="Search history"),
    ] = None,
    stats: Annotated[
        bool,
        typer.Option("--stats", help="Show cost statistics"),
    ] = False,
    # V3 commands
    interactive: Annotated[
        bool,
        typer.Option("--interactive", "-i", help="Interactive mode (guided prompts)"),
    ] = False,
    show_config: Annotated[
        bool,
        typer.Option("--show-config", help="Show current configuration"),
    ] = False,
    edit_config: Annotated[
        bool,
        typer.Option("--edit-config", help="Edit configuration in $EDITOR"),
    ] = False,
    list_models: Annotated[
        bool,
        typer.Option("--list-models", help="List all available image models"),
    ] = False,
):
    """
    Generate an educational image from a text prompt.

    Examples:
        # Basic generation
        gen-image "A cartoon librarian..." --output ownership.png

        # With style preset
        gen-image --style mnemonic "Words as birds..." --output vocab.png

        # Using template
        gen-image --template mnemonic-vocab \\
          --var word=語りかける \\
          --var romaji=katarikakeru \\
          --var meaning="to address" \\
          --var concept="words as birds" \\
          --output vocab.png

        # Discovery
        gen-image --list-templates
        gen-image --show-template mnemonic-vocab
        gen-image --edit-template my-template

        # History
        gen-image --history
        gen-image --stats
    """
    tm = TemplateManager()
    tracker = CostTracker()
    config_mgr = ConfigManager()
    config = config_mgr.load()

    # Handle config commands first
    if show_config:
        config_mgr.show()
        return

    if edit_config:
        config_mgr.edit()
        return

    if list_models:
        _display_models(config)
        return

    # Handle interactive mode
    if interactive:
        params = run_interactive_session()
        if not params:
            console.print("[yellow]Cancelled[/yellow]")
            return

        # Use parameters from interactive session
        final_prompt = params["prompt"]
        style = params["style"]
        output = params["output_path"]
        # Proceed with generation using these params
        # (rest of generation logic will use these)
    else:
        final_prompt = None  # Will be determined later

    # Handle discovery commands
    if list_styles_flag:
        console.print(list_styles())
        return

    if list_templates:
        templates = tm.list_templates()
        console.print("\n[bold cyan]Available Templates[/bold cyan]")
        console.print("=" * 40)

        if templates["builtin"]:
            console.print("\n[bold]Built-in:[/bold]")
            for name, desc in templates["builtin"]:
                console.print(f"  {name:25} {desc}")

        if templates["custom"]:
            console.print(f"\n[bold]Custom (in {tm.custom_dir}):[/bold]")
            for name, desc in templates["custom"]:
                console.print(f"  {name:25} {desc}")

        if not templates["builtin"] and not templates["custom"]:
            console.print("[yellow]No templates found[/yellow]")

        console.print("\nUsage: gen-image --template <name> --var key=value...")
        console.print("Edit: gen-image --edit-template <name>")
        return

    if show_template:
        result = tm.show_template(show_template)
        console.print(result)
        return

    if edit_template:
        success = tm.edit_template(edit_template, create_if_missing=True)
        if not success:
            raise typer.Exit(1)
        return

    # Handle history commands
    if history:
        tracker.display_history(limit=history_limit, search=history_search)
        return

    if stats:
        tracker.display_stats()
        return

    # From here on, we're generating an image

    # Determine the prompt (either from arg or template)
    final_prompt = prompt
    template_vars = None

    if template:
        # Template-based generation
        if var:
            template_vars = parse_vars(var)
        else:
            template_vars = {}

        try:
            final_prompt = tm.expand_template(template, template_vars)
        except ValueError as e:
            console.print(f"[red]❌ Template error: {e}[/red]")
            raise typer.Exit(1)

    # Validate required arguments for generation
    if not final_prompt:
        console.print("[red]❌ Error: PROMPT is required (or use --template)[/red]")
        console.print("Usage: gen-image PROMPT --output PATH")
        console.print("   or: gen-image --template NAME --var key=value --output PATH")
        console.print('\nExample: gen-image "A cartoon librarian..." --output image.png')
        raise typer.Exit(1)

    if not output and not dry_run:
        console.print("[red]❌ Error: --output is required[/red]")
        console.print("Usage: gen-image PROMPT --output PATH")
        console.print(
            "\nSpecify where to save the image:\n"
            "  --output /full/path/to/file.png  (absolute path)\n"
            "  --output ./relative/path.png     (relative to current directory)\n"
            "  --output image.png               (save to current directory)"
        )
        raise typer.Exit(1)

    # Validate size
    valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
    if size not in valid_sizes:
        console.print(f"[red]❌ Error: Invalid size '{size}'[/red]")
        console.print(f"Valid sizes: {', '.join(valid_sizes)}")
        raise typer.Exit(1)

    # Validate quality
    if quality not in ["standard", "hd"]:
        console.print(f"[red]❌ Error: Invalid quality '{quality}'[/red]")
        console.print("Valid qualities: standard, hd")
        raise typer.Exit(1)

    # Handle file conflicts with auto-increment
    if output and output.exists() and not dry_run:
        output = get_unique_filename(output)
        console.print(f"[yellow]⚠ File exists, saving as: {output.name}[/yellow]")

    # Check budget before generating (if configured)
    if config.costs.budget_limit and not dry_run:
        stats = tracker.get_stats()

        # Calculate estimated cost based on provider
        if config.api.provider == "gemini":
            estimated_cost = 0.039  # Gemini 2.5 Flash Image
        else:  # openai
            estimated_cost = 0.04 if quality == "standard" else 0.08
            if size != "1024x1024":
                estimated_cost *= 1.5

        new_total = stats["this_month_cost"] + estimated_cost
        if new_total > config.costs.budget_limit:
            console.print("[red]❌ Budget exceeded![/red]")
            console.print(f"Monthly limit: ${config.costs.budget_limit:.2f}")
            console.print(f"Current spend: ${stats['this_month_cost']:.2f}")
            console.print(f"This generation: ${estimated_cost:.2f}")
            console.print(f"Would exceed by: ${new_total - config.costs.budget_limit:.2f}")
            if not Confirm.ask("Continue anyway?", default=False):
                raise typer.Exit(0)
        elif new_total > (config.costs.budget_limit * config.costs.warn_at_percent / 100):
            percent_used = (new_total / config.costs.budget_limit) * 100
            console.print(
                f"[yellow]⚠ Budget warning: {percent_used:.0f}% of monthly limit[/yellow]"
            )
            console.print(f"Spend: ${new_total:.2f} / ${config.costs.budget_limit:.2f}")

    try:
        # Initialize generator based on config provider
        if config.api.provider == "gemini":
            generator = GeminiGenerator(model=config.api.model)
        elif config.api.provider == "openai":
            generator = ImageGenerator(model=config.api.model)
        else:
            console.print(f"[red]❌ Unknown provider: {config.api.provider}[/red]")
            console.print("Valid providers: gemini, openai")
            raise typer.Exit(1)

        # Generate image
        result = generator.generate(
            prompt=final_prompt,
            style=style if not template else StylePreset.CUSTOM,  # Templates define their own style
            quality=quality,
            size=size,
            output_path=output if not dry_run else None,
            show_prompt=show_prompt,
            dry_run=dry_run,
        )

        if dry_run:
            console.print()
            if template:
                console.print(f"Template: {template}")
                if template_vars:
                    console.print("Variables:")
                    for k, v in template_vars.items():
                        console.print(f"  {k} = {v}")
                console.print()
            console.print(f"Would save to: {output}")
            console.print("\nRemove --dry-run to generate this image.")
            return

        # Log to history
        tracker.log_generation(
            prompt=result["prompt"],
            output_path=result["output_path"],
            cost=result["cost"],
            quality=result["quality"],
            size=result["size"],
            template=template,
            template_vars=template_vars,
        )

        # Display success message
        console.print()
        console.print("✅ Image generated successfully", style="bold green")
        console.print()
        console.print(f"File: {result['output_path']}")
        console.print(f"Size: {result['size']}")
        console.print(f"Cost: ${result['cost']:.2f}")
        console.print()

        # Generate and copy wikilink
        wikilink = f"![[{output.name}]]"
        console.print("Wikilink:", style="bold")
        console.print(wikilink, style="cyan")

        if config.output.auto_copy_wikilink:
            if copy_to_clipboard(wikilink):
                console.print("[dim]✓ Copied to clipboard[/dim]")
            else:
                console.print("[dim]⚠ Could not copy to clipboard[/dim]")
        console.print()

    except ValueError as e:
        console.print(f"[red]❌ Configuration error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Failed to generate image: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
