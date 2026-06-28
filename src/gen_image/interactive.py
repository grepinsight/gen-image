"""Interactive mode for guided image generation."""

from pathlib import Path
from typing import Dict, Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt

from .styles import StylePreset

console = Console()


class InteractiveSession:
    """Manages interactive image generation session."""

    def __init__(self):
        """Initialize interactive session."""
        self.session_data = {}

    def run(self) -> Optional[Dict]:
        """
        Run interactive session to gather generation parameters.

        Returns:
            Dictionary with generation parameters, or None if cancelled
        """
        console.print("\n[bold cyan]Welcome to gen-image interactive mode![/bold cyan]\n")

        # Step 1: Choose generation type
        generation_type = self._choose_generation_type()
        if not generation_type:
            return None

        # Step 2: Gather type-specific parameters
        if generation_type == "educational":
            params = self._educational_flow()
        elif generation_type == "mnemonic":
            params = self._mnemonic_flow()
        elif generation_type == "diagram":
            params = self._diagram_flow()
        else:  # custom
            params = self._custom_flow()

        if not params:
            return None

        # Step 3: Output path
        output_path = self._get_output_path(params.get("suggested_filename"))
        if not output_path:
            return None

        params["output_path"] = output_path

        # Step 4: Confirm generation
        if not self._confirm_generation(params):
            return None

        return params

    def _choose_generation_type(self) -> Optional[str]:
        """Let user choose what type of image to create."""
        console.print("What do you want to create?")
        console.print("1. Educational concept illustration")
        console.print("2. Mnemonic image for language learning")
        console.print("3. Visual diagram/flowchart")
        console.print("4. Custom prompt")
        console.print()

        choice = Prompt.ask("Choice", choices=["1", "2", "3", "4"], default="1")

        type_map = {
            "1": "educational",
            "2": "mnemonic",
            "3": "diagram",
            "4": "custom",
        }

        return type_map.get(choice)

    def _educational_flow(self) -> Optional[Dict]:
        """Guided flow for educational concept illustrations."""
        console.print("\n[bold]Creating an educational illustration[/bold]\n")

        concept = Prompt.ask("What concept are you explaining?")
        if not concept:
            return None

        metaphor = Prompt.ask("What's the core metaphor or visual analogy?")
        if not metaphor:
            return None

        emotion = Prompt.ask(
            "What emotion should the image convey?",
            default="clarity",
            show_default=True,
        )

        color = Prompt.ask(
            "Primary color?",
            choices=["red", "blue", "green", "yellow", "purple", "auto"],
            default="auto",
            show_default=True,
        )

        elements = Prompt.ask(
            "Any specific elements to include?\n(comma-separated, or press enter to skip)",
            default="",
        )

        # Build prompt from template
        prompt = f"""[Style: Educational cartoon - bright, vibrant colors]

Create a memorable educational illustration showing {concept}.

Visual metaphor: {metaphor}

The image should:
- Convey the feeling of {emotion}
- Use bright colors (#51cf66 green, #4dabf7 blue, #ffd43b yellow palette)
"""

        if color != "auto":
            prompt += f"- Use {color} as the dominant color\n"

        if elements:
            prompt += f"- Include these elements: {elements}\n"

        prompt += """
Technical requirements:
- Simple, uncluttered composition
- Clear visual metaphors
- No text in the image
- Slightly humorous but instructive
- One surprising element for memorability
"""

        # Generate suggested filename
        concept_slug = concept.lower().replace(" ", "-")[:30]
        suggested_filename = f"{concept_slug}.png"

        return {
            "prompt": prompt.strip(),
            "style": StylePreset.CUSTOM,  # Using custom prompt
            "suggested_filename": suggested_filename,
            "type": "educational",
        }

    def _mnemonic_flow(self) -> Optional[Dict]:
        """Guided flow for mnemonic images."""
        console.print("\n[bold]Creating a mnemonic image[/bold]\n")

        word = Prompt.ask("What word/phrase are you memorizing?")
        if not word:
            return None

        pronunciation = Prompt.ask("How is it pronounced? (romaji/phonetic)")

        meaning = Prompt.ask("What does it mean?")

        concept = Prompt.ask("Visual mnemonic concept\n(describe the absurd/memorable scene)")

        # Build prompt
        prompt = f"""[Style: Mnemonic - absurd and memorable]

Create a memorable mnemonic image for "{word}" ({pronunciation}).

Meaning: {meaning}

Visual concept: {concept}

The image should:
- Use visual wordplay connecting pronunciation to meaning
- Include surprising/unexpected elements
- Be emotionally engaging (humor, surprise)
- Help create a strong memory association between "{pronunciation}" and "{meaning}"

Technical requirements:
- No text in the image
- Absurd enough to be memorable but clear enough to be instructive
- Bright, vibrant colors
- One central memorable hook
"""

        suggested_filename = f"{pronunciation.lower().replace(' ', '-')}.png"

        return {
            "prompt": prompt.strip(),
            "style": StylePreset.CUSTOM,
            "suggested_filename": suggested_filename,
            "type": "mnemonic",
        }

    def _diagram_flow(self) -> Optional[Dict]:
        """Guided flow for diagrams."""
        console.print("\n[bold]Creating a visual diagram[/bold]\n")

        subject = Prompt.ask("What system/process are you visualizing?")
        if not subject:
            return None

        components = Prompt.ask("What are the main components?\n(comma-separated)")

        relationships = Prompt.ask("How do they relate?\n(e.g., 'A flows to B, B controls C')")

        prompt = f"""[Style: Infographic diagram - clean and organized]

Create a clear infographic-style visualization of {subject}.

Main components: {components}

Relationships: {relationships}

The image should:
- Use hierarchical layout
- Color-code components
- Include flow indicators (arrows, connections)
- Preserve spatial relationships
- Be simple and professional

Technical requirements:
- No text in the image
- Clean, organized layout
- Clear visual language
"""

        suggested_filename = f"{subject.lower().replace(' ', '-')}-diagram.png"

        return {
            "prompt": prompt.strip(),
            "style": StylePreset.CUSTOM,
            "suggested_filename": suggested_filename,
            "type": "diagram",
        }

    def _custom_flow(self) -> Optional[Dict]:
        """Guided flow for custom prompts."""
        console.print("\n[bold]Custom prompt[/bold]\n")

        prompt = Prompt.ask("Enter your full prompt")
        if not prompt:
            return None

        style = Prompt.ask(
            "Style preset",
            choices=["educational-cartoon", "mnemonic", "diagram-alternative", "custom"],
            default="educational-cartoon",
            show_default=True,
        )

        # Extract first few words for filename
        words = prompt.split()[:3]
        suggested_filename = "-".join(words).lower() + ".png"
        suggested_filename = "".join(c for c in suggested_filename if c.isalnum() or c in "-.")

        return {
            "prompt": prompt,
            "style": StylePreset(style),
            "suggested_filename": suggested_filename,
            "type": "custom",
        }

    def _get_output_path(self, suggested: Optional[str] = None) -> Optional[Path]:
        """Get output path from user."""
        console.print()

        if suggested:
            default_path = f"./{suggested}"
            console.print(f"Suggested filename: [cyan]{suggested}[/cyan]")
        else:
            default_path = "./image.png"

        path_str = Prompt.ask(
            "Output path\n(absolute or relative to current directory)",
            default=default_path,
            show_default=True,
        )

        if not path_str:
            return None

        return Path(path_str)

    def _confirm_generation(self, params: Dict) -> bool:
        """Show final confirmation before generating."""
        console.print()
        console.print("[bold cyan]Ready to generate![/bold cyan]")
        console.print("=" * 60)

        # Show prompt preview
        console.print("\n[bold]Prompt:[/bold]")
        preview = params["prompt"][:200]
        if len(params["prompt"]) > 200:
            preview += "..."
        console.print(preview)

        console.print(f"\n[bold]Output:[/bold] {params['output_path']}")
        console.print(f"[bold]Style:[/bold] {params['style']}")
        console.print("[bold]Cost:[/bold] ~$0.04 (standard quality)")
        console.print()

        return Confirm.ask("Generate this image?", default=True)


def run_interactive_session() -> Optional[Dict]:
    """Run interactive session and return parameters."""
    session = InteractiveSession()
    return session.run()
