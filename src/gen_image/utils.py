"""Utility functions for file handling and naming."""

import re
import subprocess
from pathlib import Path


def extract_topic_from_prompt(prompt: str, max_words: int = 3) -> str:
    """
    Extract a topic slug from prompt for filename.

    Args:
        prompt: The image generation prompt
        max_words: Maximum number of words to extract

    Returns:
        Kebab-case slug suitable for filename
    """
    # Remove style markers and common prefixes
    text = prompt
    text = re.sub(r"\[Style:.*?\]", "", text)
    text = re.sub(r"^(Create|Generate|Make|Draw)(\s+a|\s+an)?\s+", "", text, flags=re.IGNORECASE)

    # Split into words and filter
    words = text.split()
    meaningful_words = []

    # Skip common words
    skip_words = {
        "a",
        "an",
        "the",
        "of",
        "for",
        "with",
        "in",
        "on",
        "at",
        "to",
        "and",
        "or",
        "but",
        "that",
        "this",
        "is",
        "are",
        "was",
        "were",
    }

    for word in words:
        # Clean word
        clean = re.sub(r"[^\w\s-]", "", word.lower())
        if clean and clean not in skip_words and len(meaningful_words) < max_words:
            meaningful_words.append(clean)

    if not meaningful_words:
        return "image"

    # Join with hyphens
    slug = "-".join(meaningful_words)

    # Limit length
    if len(slug) > 50:
        slug = slug[:50].rsplit("-", 1)[0]  # Cut at word boundary

    return slug


def get_unique_filename(base_path: Path) -> Path:
    """
    Get unique filename by auto-incrementing if file exists.

    Args:
        base_path: Desired file path

    Returns:
        Unique path (original or with -1, -2, etc. appended)
    """
    if not base_path.exists():
        return base_path

    # Split into stem and suffix
    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent

    # Try incrementing
    counter = 1
    while True:
        new_name = f"{stem}-{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

        # Safety check
        if counter > 1000:
            raise ValueError("Too many file conflicts (> 1000)")


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard.

    Args:
        text: Text to copy

    Returns:
        True if successful, False otherwise
    """
    try:
        # macOS
        subprocess.run(
            ["pbcopy"],
            input=text.encode("utf-8"),
            check=True,
            capture_output=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    try:
        # Linux with xclip
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text.encode("utf-8"),
            check=True,
            capture_output=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    try:
        # Linux with xsel
        subprocess.run(
            ["xsel", "--clipboard", "--input"],
            input=text.encode("utf-8"),
            check=True,
            capture_output=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    # Windows (if needed later)
    # Could use pyperclip or win32clipboard

    return False
