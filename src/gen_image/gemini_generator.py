"""Image generation backend using Google Gemini."""

import os
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .styles import StylePreset, get_style_prompt_prefix

console = Console()


class GeminiGenerator:
    """Handles image generation using Google Gemini."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gemini-3.1-flash-image-preview"
    ):
        """Initialize generator with API key."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY "
                "environment variable or pass api_key parameter."
            )
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model

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
        """Generate an image from a prompt."""
        # Build full prompt with style prefix
        style_prefix = get_style_prompt_prefix(style)
        full_prompt = f"{style_prefix}{prompt}"

        # Convert size to aspect ratio
        aspect_ratio = self._size_to_aspect_ratio(size)

        # Estimated cost (Gemini pricing)
        cost = 0.039

        # Show prompt preview if requested
        if show_prompt or dry_run:
            self._display_prompt_preview(full_prompt, aspect_ratio, cost, dry_run)

        if dry_run:
            return {
                "dry_run": True,
                "prompt": full_prompt,
                "cost": cost,
                "quality": quality,
                "size": size,
                "aspect_ratio": aspect_ratio,
            }

        # Display generation configuration
        if not show_prompt:
            self._display_generation_info(output_path, aspect_ratio, cost)

        # Generate image with progress indicator
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Generating image...", total=None)

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                    ),
                )

            # Extract image from response
            if not response.candidates or not response.candidates[0].content.parts:
                raise ValueError("No image generated in response")

            image_part = None
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_part = part
                    break

            if not image_part:
                raise ValueError("No image data found in response")

            # Save image
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(image_part.inline_data.data)

            return {
                "cost": cost,
                "quality": quality,
                "size": size,
                "aspect_ratio": aspect_ratio,
                "prompt": full_prompt,
                "output_path": str(output_path) if output_path else None,
            }

        except Exception as e:
            raise self._handle_error(e) from e

    def _size_to_aspect_ratio(self, size: str) -> str:
        """Convert size string to Gemini aspect ratio."""
        size_to_ratio = {
            "1024x1024": "1:1",
            "1792x1024": "16:9",
            "1024x1792": "9:16",
        }
        return size_to_ratio.get(size, "1:1")

    def _display_generation_info(self, output_path: Path, aspect_ratio: str, cost: float):
        """Display generation configuration before starting."""
        console.print()
        console.print("Generation Configuration", style="bold cyan")
        console.print("━" * 60)
        console.print(f"Model: {self.model_name}")
        console.print("Provider: Google")
        console.print(f"Output: {output_path}")
        console.print(f"Aspect Ratio: {aspect_ratio}")
        console.print(f"Estimated cost: ${cost:.2f}")
        console.print("━" * 60)
        console.print()

    def _display_prompt_preview(
        self, prompt: str, aspect_ratio: str, cost: float, is_dry_run: bool
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
        console.print(f"Model: {self.model_name}")
        console.print("Provider: Google")
        console.print(f"Aspect Ratio: {aspect_ratio}")
        console.print(f"Estimated cost: ${cost:.2f}")
        console.print()

        if is_dry_run:
            console.print("Remove --dry-run to generate this image.", style="yellow")
        elif prompt:
            console.print("Proceeding with generation...", style="dim")

    def _handle_error(self, error: Exception) -> RuntimeError:
        """Map a Google AI error to a helpful, user-facing RuntimeError.

        The message is also printed for interactive use; the returned error is
        meant to be raised by the caller (``raise self._handle_error(e) from e``)
        so the original cause is preserved.
        """
        error_message = str(error).strip()
        low = error_message.lower()

        if "quota" in low or "rate" in low:
            msg = (
                "Google AI quota or rate limit exceeded. Check your quota and billing "
                "in Google AI Studio."
            )
        elif "invalid" in low and "key" in low:
            msg = (
                "Invalid Google API key. Set GEMINI_API_KEY or GOOGLE_API_KEY "
                "(get a key at https://aistudio.google.com/apikey)."
            )
        elif "safety" in low or "blocked" in low:
            msg = (
                "Prompt blocked by Google safety filters. Try rephrasing to avoid "
                "violent, harmful, or otherwise sensitive content."
            )
        elif not error_message:
            msg = "Google AI request failed with no details."
        else:
            msg = f"Google AI request failed: {error_message}"

        console.print(f"[red]❌ {msg}[/red]")
        return RuntimeError(msg)
