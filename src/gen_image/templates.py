"""Template system for reusable image prompts."""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console

console = Console()


class TemplateManager:
    """Manages prompt templates with variable substitution."""

    def __init__(self, custom_templates_dir: Optional[Path] = None):
        """Initialize template manager."""
        # Built-in templates (shipped with package)
        self.builtin_dir = Path(__file__).parent.parent.parent / "templates"

        # Custom templates (user's config)
        if custom_templates_dir:
            self.custom_dir = custom_templates_dir
        else:
            config_home = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
            self.custom_dir = Path(config_home) / "gen-image" / "templates"

        # Ensure custom dir exists
        self.custom_dir.mkdir(parents=True, exist_ok=True)

    def list_templates(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        List all available templates.

        Returns:
            Dict with 'builtin' and 'custom' lists of (name, description) tuples
        """
        templates = {"builtin": [], "custom": []}

        # List built-in templates
        if self.builtin_dir.exists():
            for template_file in sorted(self.builtin_dir.glob("*.txt")):
                name = template_file.stem
                description = self._get_template_description(template_file)
                templates["builtin"].append((name, description))

        # List custom templates
        for template_file in sorted(self.custom_dir.glob("*.txt")):
            name = template_file.stem
            description = self._get_template_description(template_file)
            templates["custom"].append((name, description))

        return templates

    def _get_template_description(self, template_file: Path) -> str:
        """Extract description from template file (first comment line)."""
        try:
            content = template_file.read_text()
            # Look for first line starting with #
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("#") and not line.startswith("##"):
                    return line.lstrip("#").strip()
            return "No description"
        except Exception:
            return "Error reading template"

    def get_template_path(self, name: str) -> Optional[Path]:
        """Get path to template file. Custom templates override built-in."""
        # Check custom first
        custom_path = self.custom_dir / f"{name}.txt"
        if custom_path.exists():
            return custom_path

        # Check built-in
        builtin_path = self.builtin_dir / f"{name}.txt"
        if builtin_path.exists():
            return builtin_path

        return None

    def load_template(self, name: str) -> str:
        """Load template content by name."""
        template_path = self.get_template_path(name)
        if not template_path:
            raise ValueError(f"Template '{name}' not found")

        return template_path.read_text()

    def get_required_variables(self, template_content: str) -> List[str]:
        """Extract required variables from template content."""
        # Find all {{variable}} patterns
        pattern = r"\{\{(\w+)\}\}"
        variables = re.findall(pattern, template_content)
        return sorted(set(variables))

    def expand_template(self, name: str, variables: Dict[str, str]) -> str:
        """
        Expand template with provided variables.

        Args:
            name: Template name
            variables: Dict of variable_name -> value

        Returns:
            Expanded template content

        Raises:
            ValueError: If template not found or required variables missing
        """
        content = self.load_template(name)
        required = self.get_required_variables(content)

        # Check for missing variables
        missing = [var for var in required if var not in variables]
        if missing:
            raise ValueError(
                f"Missing required variables for template '{name}': {', '.join(missing)}"
            )

        # Substitute variables
        result = content
        for var, value in variables.items():
            result = result.replace(f"{{{{{var}}}}}", value)

        return result

    def show_template(self, name: str) -> str:
        """Generate formatted display of template details."""
        template_path = self.get_template_path(name)
        if not template_path:
            return f"Template '{name}' not found"

        content = self.load_template(name)
        required = self.get_required_variables(content)
        is_custom = template_path.parent == self.custom_dir

        output = []
        output.append(f"Template: {name}")
        output.append(f"Location: {template_path}")
        output.append(f"Type: {'Custom' if is_custom else 'Built-in'}")
        output.append("━" * 60)

        if required:
            output.append("Required variables:")
            for var in required:
                output.append(f"  - {var}")
        else:
            output.append("No variables required")

        output.append("")
        output.append("Template content:")
        output.append("━" * 60)
        output.append(content)
        output.append("━" * 60)

        return "\n".join(output)

    def edit_template(self, name: str, create_if_missing: bool = False) -> bool:
        """
        Open template in editor.

        Args:
            name: Template name
            create_if_missing: Create new template if doesn't exist

        Returns:
            True if successful, False otherwise
        """
        template_path = self.get_template_path(name)

        # Handle built-in templates - copy to custom first
        if template_path and template_path.parent == self.builtin_dir:
            console.print("[yellow]Built-in template. Creating custom copy...[/yellow]")
            custom_path = self.custom_dir / f"{name}.txt"
            custom_path.write_text(template_path.read_text())
            template_path = custom_path
            console.print(f"Copied to: {template_path}")

        # Create new template if needed
        if not template_path:
            if not create_if_missing:
                console.print(f"[red]Template '{name}' not found[/red]")
                return False

            # Create scaffold
            template_path = self.custom_dir / f"{name}.txt"
            scaffold = self._create_template_scaffold(name)
            template_path.write_text(scaffold)
            console.print(f"[green]Created new template: {template_path}[/green]")

        # Open in editor
        editor = self._get_editor()
        try:
            subprocess.run([editor, str(template_path)], check=True)
            return True
        except subprocess.CalledProcessError:
            console.print(f"[red]Failed to open editor: {editor}[/red]")
            return False
        except FileNotFoundError:
            console.print(f"[red]Editor not found: {editor}[/red]")
            console.print("Set $EDITOR environment variable")
            return False

    def _get_editor(self) -> str:
        """Get editor command from environment or use fallback."""
        editor = os.getenv("EDITOR")
        if editor:
            return editor

        # Try common editors in order
        for cmd in ["nvim", "vim", "vi", "nano"]:
            try:
                subprocess.run(["which", cmd], capture_output=True, check=True)
                return cmd
            except subprocess.CalledProcessError:
                continue

        return "vi"  # Last resort

    def _create_template_scaffold(self, name: str) -> str:
        """Create a basic template scaffold for new templates."""
        return f"""# Template: {name}
# Variables: {{{{var1}}}}, {{{{var2}}}}
# Style: educational-cartoon | mnemonic | diagram-alternative | custom

[Style: educational-cartoon]

{{{{prompt_content}}}}

Technical requirements:
- No text in image
- {{{{additional_requirements}}}}
"""
