"""Image generation backend using OpenAI DALL-E 3."""

import os
from pathlib import Path
from typing import Optional

import httpx
from openai import OpenAI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .styles import StylePreset, get_style_prompt_prefix

console = Console()


class ImageGenerator:
    """Handles image generation using OpenAI DALL-E 3."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-image-1"):
        """Initialize generator with API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        style: StylePreset = StylePreset.EDUCATIONAL_CARTOON,
        quality: str = "standard",
        size: str = "1024x1024",
        output_path: Path = None,
        show_prompt: bool = False,
        dry_run: bool = False,
    ) -> dict:
        """
        Generate an image from a prompt.

        Args:
            prompt: User's image description
            style: Style preset to apply
            quality: Image quality ("standard" or "hd")
            size: Image dimensions ("1024x1024", "1792x1024", or "1024x1792")
            output_path: Where to save the image
            show_prompt: If True, display the full prompt before generating
            dry_run: If True, show what would be generated without calling API

        Returns:
            Dictionary with generation details (url, cost, etc.)
        """
        # Build full prompt with style prefix
        style_prefix = get_style_prompt_prefix(style)
        full_prompt = f"{style_prefix}{prompt}"

        # Map quality for gpt-image models (use different quality scale)
        if self.model.startswith("gpt-image"):
            quality_map = {"standard": "medium", "hd": "high"}
            api_quality = quality_map.get(quality, quality)
        else:
            api_quality = quality

        # Calculate estimated cost
        cost = 0.04 if quality == "standard" else 0.08
        if size != "1024x1024":
            cost *= 1.5  # Larger sizes cost more

        # Show prompt preview if requested
        if show_prompt or dry_run:
            self._display_prompt_preview(full_prompt, quality, size, cost, dry_run)

        if dry_run:
            return {
                "dry_run": True,
                "prompt": full_prompt,
                "cost": cost,
                "quality": quality,
                "size": size,
            }

        # Display generation configuration
        if not show_prompt:  # Only show if we didn't already show prompt preview
            self._display_generation_info(output_path, quality, size, cost)

        # Generate image with progress indicator
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Generating image...", total=None)

                response = self.client.images.generate(
                    model=self.model,
                    prompt=full_prompt,
                    size=size,
                    quality=api_quality,
                    n=1,
                )

            image_data = response.data[0]

            # Save image (gpt-image models return b64_json, dall-e returns url)
            if output_path:
                if image_data.b64_json:
                    import base64

                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(base64.b64decode(image_data.b64_json))
                elif image_data.url:
                    self._download_image(image_data.url, output_path)
                else:
                    raise ValueError("No image data in response")

            return {
                "cost": cost,
                "quality": quality,
                "size": size,
                "prompt": full_prompt,
                "output_path": str(output_path) if output_path else None,
            }

        except Exception as e:
            raise self._handle_error(e) from e

    def _display_generation_info(self, output_path: Path, quality: str, size: str, cost: float):
        """Display generation configuration before starting."""
        console.print()
        console.print("Generation Configuration", style="bold cyan")
        console.print("━" * 60)
        console.print(f"Model: {self.model}")
        console.print("Provider: OpenAI")
        console.print(f"Output: {output_path}")
        console.print(f"Size: {size}")
        console.print(f"Quality: {quality}")
        console.print(f"Estimated cost: ${cost:.2f}")
        console.print("━" * 60)
        console.print()

    def _display_prompt_preview(
        self, prompt: str, quality: str, size: str, cost: float, is_dry_run: bool
    ):
        """Display the prompt that will be sent to the API."""
        console.print()
        console.print(
            "Prompt Preview" if is_dry_run else "Generated Prompt",
            style="bold cyan",
        )
        console.print("━" * 60)
        console.print(prompt)
        console.print("━" * 60)
        console.print()
        console.print(f"Model: {self.model}")
        console.print("Provider: OpenAI")
        console.print(f"Size: {size}")
        console.print(f"Quality: {quality}")
        console.print(f"Estimated cost: ${cost:.2f}")
        console.print()

        if is_dry_run:
            console.print("Remove --dry-run to generate this image.", style="yellow")
        elif prompt:
            console.print("Proceeding with generation...", style="dim")

    def _download_image(self, url: str, output_path: Path):
        """Download image from URL and save to path."""
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.content)

    def _handle_error(self, error: Exception) -> RuntimeError:
        """Map an OpenAI error to a helpful, user-facing RuntimeError.

        The message is also printed for interactive use; the returned error is
        meant to be raised by the caller (``raise self._handle_error(e) from e``)
        so the original cause is preserved.
        """
        error_message = str(error).strip()
        low = error_message.lower()

        if "rate_limit" in low or "rate limit" in low:
            msg = "OpenAI rate limit reached. Try again in about a minute."
        elif "invalid" in low and "key" in low:
            msg = (
                "Invalid OpenAI API key. Set the OPENAI_API_KEY environment variable "
                "(get a key at https://platform.openai.com/api-keys)."
            )
        elif "content_policy" in low or "content policy" in low or "safety" in low:
            msg = (
                "Prompt rejected by the OpenAI content policy. Try rephrasing to avoid "
                "violence, real public figures, or copyrighted characters."
            )
        elif not error_message:
            msg = "OpenAI request failed with no details."
        else:
            msg = f"OpenAI request failed: {error_message}"

        console.print(f"[red]❌ {msg}[/red]")
        return RuntimeError(msg)
