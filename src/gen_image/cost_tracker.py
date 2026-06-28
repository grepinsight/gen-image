"""Cost tracking and generation history."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table

console = Console()


class CostTracker:
    """Tracks generation history and costs."""

    def __init__(self, history_file: Optional[Path] = None):
        """Initialize cost tracker."""
        if history_file:
            self.history_file = history_file
        else:
            config_home = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
            config_dir = Path(config_home) / "gen-image"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.history_file = config_dir / "history.jsonl"

    def log_generation(
        self,
        prompt: str,
        output_path: str,
        cost: float,
        provider: str = "openai",
        model: str = "dall-e-3",
        quality: str = "standard",
        size: str = "1024x1024",
        template: Optional[str] = None,
        template_vars: Optional[Dict[str, str]] = None,
    ):
        """Log a generation to history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt[:200],  # Truncate long prompts
            "output_path": output_path,
            "cost": cost,
            "provider": provider,
            "model": model,
            "quality": quality,
            "size": size,
        }

        if template:
            entry["template"] = template
            if template_vars:
                entry["template_vars"] = template_vars

        # Append to JSONL file
        with open(self.history_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_history(self, limit: Optional[int] = None, search: Optional[str] = None) -> List[Dict]:
        """
        Get generation history.

        Args:
            limit: Maximum number of entries to return (most recent first)
            search: Search term to filter by (searches prompt and output_path)

        Returns:
            List of history entries
        """
        if not self.history_file.exists():
            return []

        entries = []
        with open(self.history_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    # Filter by search term if provided
                    if search:
                        search_lower = search.lower()
                        if not (
                            search_lower in entry.get("prompt", "").lower()
                            or search_lower in entry.get("output_path", "").lower()
                            or search_lower in entry.get("template", "").lower()
                        ):
                            continue
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue

        # Return most recent first
        entries.reverse()

        if limit:
            return entries[:limit]
        return entries

    def get_stats(self) -> Dict:
        """Get aggregate statistics."""
        entries = self.get_history()

        if not entries:
            return {
                "total_generations": 0,
                "total_cost": 0.0,
                "this_month_cost": 0.0,
                "this_month_count": 0,
            }

        total_cost = sum(e.get("cost", 0.0) for e in entries)
        total_count = len(entries)

        # Calculate this month's stats
        current_month = datetime.now().strftime("%Y-%m")
        this_month_entries = [
            e for e in entries if e.get("timestamp", "").startswith(current_month)
        ]
        this_month_cost = sum(e.get("cost", 0.0) for e in this_month_entries)
        this_month_count = len(this_month_entries)

        # Find most recent and most expensive
        most_recent = entries[0] if entries else None
        most_expensive = max(entries, key=lambda e: e.get("cost", 0.0)) if entries else None

        return {
            "total_generations": total_count,
            "total_cost": total_cost,
            "this_month_cost": this_month_cost,
            "this_month_count": this_month_count,
            "most_recent": most_recent,
            "most_expensive": most_expensive,
        }

    def display_history(self, limit: int = 10, search: Optional[str] = None):
        """Display history in formatted table."""
        entries = self.get_history(limit=limit, search=search)

        if not entries:
            console.print("[yellow]No generation history found[/yellow]")
            return

        table = Table(title="Recent Generations")
        table.add_column("Date", style="cyan")
        table.add_column("Output", style="green")
        table.add_column("Cost", justify="right", style="yellow")
        table.add_column("Details", style="dim")

        for entry in entries:
            timestamp = entry.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                date_str = timestamp[:16]

            output = Path(entry.get("output_path", "")).name
            cost = f"${entry.get('cost', 0.0):.2f}"

            # Build details string
            details_parts = []
            if entry.get("template"):
                details_parts.append(f"template:{entry['template']}")
            else:
                prompt = entry.get("prompt", "")[:40]
                details_parts.append(f"{prompt}...")

            provider = entry.get("provider", "openai")
            model = entry.get("model", "dall-e-3")
            quality = entry.get("quality", "standard")
            size = entry.get("size", "1024x1024")
            details_parts.append(f"{provider}/{model}")
            details_parts.append(f"{quality},{size}")

            details = " | ".join(details_parts)

            table.add_row(date_str, output, cost, details)

        console.print(table)

    def display_stats(self):
        """Display aggregate statistics."""
        stats = self.get_stats()

        if stats["total_generations"] == 0:
            console.print("[yellow]No generation history found[/yellow]")
            return

        console.print("\n[bold cyan]Generation Statistics[/bold cyan]")
        console.print("=" * 40)
        console.print(f"Total images: {stats['total_generations']}")
        console.print(f"Total cost: ${stats['total_cost']:.2f}")
        console.print(
            f"This month: ${stats['this_month_cost']:.2f} ({stats['this_month_count']} images)"
        )
        console.print()

        if stats["most_expensive"]:
            entry = stats["most_expensive"]
            console.print(
                f"Most expensive: ${entry.get('cost', 0.0):.2f} "
                f"({entry.get('quality', 'standard')} {entry.get('size', '1024x1024')})"
            )

        if stats["most_recent"]:
            entry = stats["most_recent"]
            timestamp = entry.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                date_str = timestamp

            console.print(f"Most recent: {date_str} - ${entry.get('cost', 0.0):.2f}")

        console.print()

    def clear_history(self):
        """Clear all history."""
        if self.history_file.exists():
            self.history_file.unlink()
            console.print("[green]History cleared[/green]")
        else:
            console.print("[yellow]No history to clear[/yellow]")
