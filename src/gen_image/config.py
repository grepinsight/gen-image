"""Configuration management."""

import os
import subprocess
from pathlib import Path
from typing import Optional

import toml
from pydantic import BaseModel, Field
from rich.console import Console

console = Console()


def config_dir() -> Path:
    """Resolve the gen-image config directory (honors XDG_CONFIG_HOME)."""
    config_home = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return Path(config_home) / "gen-image"


def load_config_env() -> None:
    """Load `~/.config/gen-image/.env` into os.environ for any caller.

    The provider generators read their API keys from the process environment
    (GEMINI_API_KEY / GOOGLE_API_KEY / OPENAI_API_KEY). Non-interactive callers
    (launchd jobs, the dream cron, skills shelling out to `gen-image`) do not
    inherit an interactive shell's exports, so the key has to come from a
    durable file. We parse the config-dir `.env` ourselves (no python-dotenv
    dependency) and only set keys that are not already present, so a real
    environment export always wins.

    Silently does nothing if the file is absent or unreadable -- callers that
    pass an explicit api_key, or already have the key exported, are unaffected.
    """
    env_path = config_dir() / ".env"
    try:
        lines = env_path.read_text().splitlines()
    except OSError:
        return
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        # Strip an optional leading `export ` and surrounding quotes.
        if key.startswith("export "):
            key = key[len("export ") :].strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


class GeneralConfig(BaseModel):
    """General configuration."""

    vault_path: Optional[str] = None
    attachments_dir: str = "attachments"
    default_style: str = "educational-cartoon"


class APIConfig(BaseModel):
    """API configuration."""

    provider: str = "gemini"
    model: str = "gemini-3.1-flash-image-preview"
    quality: str = "standard"
    size: str = "1024x1024"


class CostsConfig(BaseModel):
    """Cost tracking configuration."""

    budget_limit: Optional[float] = None  # Monthly budget in USD
    warn_at_percent: int = Field(default=80, ge=0, le=100)  # Warn at 80% of budget


class OutputConfig(BaseModel):
    """Output configuration."""

    auto_copy_wikilink: bool = True
    naming_pattern: str = "{topic}-{timestamp}"  # Future: customizable


class Config(BaseModel):
    """Main configuration."""

    general: GeneralConfig = Field(default_factory=GeneralConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    costs: CostsConfig = Field(default_factory=CostsConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)


class ConfigManager:
    """Manages configuration file."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager."""
        if config_path:
            self.config_path = config_path
        else:
            self.config_path = config_dir() / "config.toml"

        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Config:
        """Load configuration from file or return defaults."""
        if not self.config_path.exists():
            return Config()

        try:
            data = toml.load(self.config_path)
            return Config(**data)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to load config: {e}[/yellow]")
            console.print("[yellow]Using default configuration[/yellow]")
            return Config()

    def save(self, config: Config):
        """Save configuration to file."""
        data = config.model_dump()
        with open(self.config_path, "w") as f:
            toml.dump(data, f)

    def create_default(self):
        """Create default configuration file with comments."""
        default_content = """# gen-image configuration
# Location: ~/.config/gen-image/config.toml

[general]
# Optional: path to your notes/vault root (used to resolve relative output paths)
# vault_path = "/path/to/your/notes"

# Default attachments directory (relative to vault or absolute)
attachments_dir = "attachments"

# Default style preset
default_style = "educational-cartoon"

[api]
# Image generation provider ("gemini" or "openai")
provider = "gemini"

# Model to use
# - Gemini: "gemini-3.1-flash-image-preview" (default)
# - OpenAI: "gpt-image-1" (default), "gpt-image-1.5" (latest)
model = "gemini-3.1-flash-image-preview"

# Default quality ("standard" or "hd" for OpenAI, ignored for Gemini)
quality = "standard"

# Default size (1024x1024, 1792x1024, or 1024x1792)
size = "1024x1024"

[costs]
# Monthly budget limit in USD (null = no limit)
# budget_limit = 10.00

# Warn when budget usage reaches this percentage
warn_at_percent = 80

[output]
# Automatically copy wikilink to clipboard after generation
auto_copy_wikilink = true

# Naming pattern for auto-generated filenames
# (currently only "{topic}-{timestamp}" is supported)
naming_pattern = "{topic}-{timestamp}"
"""
        self.config_path.write_text(default_content)

    def edit(self):
        """Open config file in editor."""
        if not self.config_path.exists():
            console.print("[yellow]Config file doesn't exist. Creating default...[/yellow]")
            self.create_default()
            console.print(f"[green]Created: {self.config_path}[/green]")

        editor = self._get_editor()
        try:
            subprocess.run([editor, str(self.config_path)], check=True)

            # Validate after editing
            try:
                self.load()
                console.print("[green]✓ Configuration is valid[/green]")
            except Exception as e:
                console.print(f"[red]❌ Configuration error: {e}[/red]")
                console.print("[yellow]Please fix the errors and try again[/yellow]")

        except subprocess.CalledProcessError:
            console.print(f"[red]Failed to open editor: {editor}[/red]")
        except FileNotFoundError:
            console.print(f"[red]Editor not found: {editor}[/red]")
            console.print("Set $EDITOR environment variable")

    def _get_editor(self) -> str:
        """Get editor command from environment or use fallback."""
        editor = os.getenv("EDITOR")
        if editor:
            return editor

        # Try common editors
        for cmd in ["nvim", "vim", "vi", "nano"]:
            try:
                subprocess.run(["which", cmd], capture_output=True, check=True)
                return cmd
            except subprocess.CalledProcessError:
                continue

        return "vi"

    def show(self):
        """Display current configuration."""
        config = self.load()

        console.print("\n[bold cyan]Configuration[/bold cyan]")
        console.print("=" * 40)
        console.print(f"Config file: {self.config_path}")
        console.print()

        console.print("[bold][general][/bold]")
        console.print(f"vault_path = {config.general.vault_path or '(not set)'}")
        console.print(f"attachments_dir = {config.general.attachments_dir}")
        console.print(f"default_style = {config.general.default_style}")
        console.print()

        console.print("[bold][api][/bold]")
        console.print(f"provider = {config.api.provider}")
        console.print(f"model = {config.api.model}")
        console.print(f"quality = {config.api.quality}")
        console.print(f"size = {config.api.size}")
        console.print()

        console.print("[bold][costs][/bold]")
        if config.costs.budget_limit:
            console.print(f"budget_limit = ${config.costs.budget_limit:.2f}")
        else:
            console.print("budget_limit = (no limit)")
        console.print(f"warn_at_percent = {config.costs.warn_at_percent}%")
        console.print()

        console.print("[bold][output][/bold]")
        console.print(f"auto_copy_wikilink = {config.output.auto_copy_wikilink}")
        console.print(f"naming_pattern = {config.output.naming_pattern}")
        console.print()

        console.print("Edit config: gen-image --edit-config")
        console.print()
