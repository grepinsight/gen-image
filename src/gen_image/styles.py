"""Style preset definitions for image generation."""

from enum import Enum
from typing import Dict


class StylePreset(str, Enum):
    """Available style presets."""

    EDUCATIONAL_CARTOON = "educational-cartoon"
    MNEMONIC = "mnemonic"
    DIAGRAM_ALTERNATIVE = "diagram-alternative"
    FIRST_PERSON = "first-person"
    CUSTOM = "custom"


STYLE_DEFINITIONS: Dict[StylePreset, Dict[str, str]] = {
    StylePreset.EDUCATIONAL_CARTOON: {
        "name": "Educational Cartoon",
        "purpose": "Explain technical concepts memorably",
        "characteristics": "Bright colors, clear metaphors, no text",
        "best_for": "Rust ownership, algorithms, system design",
        "prompt_prefix": (
            "[Style: Educational cartoon - bright, vibrant colors]\n\n"
            "Create a clear, instructive cartoon illustration. "
            "Use bright colors (#51cf66 green, #4dabf7 blue, #ffd43b yellow palette). "
            "Simple, uncluttered composition with clear visual metaphors. "
            "No text in the image. Slightly humorous but instructive.\n\n"
        ),
    },
    StylePreset.MNEMONIC: {
        "name": "Mnemonic",
        "purpose": "Language learning memory aids",
        "characteristics": "Absurd visual puns, surprising elements",
        "best_for": "Vocabulary words, concepts with sound-alike words",
        "prompt_prefix": (
            "[Style: Mnemonic - absurd and memorable]\n\n"
            "Create a memorable mnemonic image with absurd visual wordplay. "
            "Include surprising/unexpected elements for emotional engagement "
            "(humor, surprise). No text in the image. "
            "Focus on creating strong memory associations.\n\n"
        ),
    },
    StylePreset.DIAGRAM_ALTERNATIVE: {
        "name": "Diagram Alternative",
        "purpose": "Complex systems/relationships",
        "characteristics": "Infographic style, color-coded, spatial layout",
        "best_for": "Architectures, workflows, hierarchies",
        "prompt_prefix": (
            "[Style: Infographic diagram - clean and organized]\n\n"
            "Create a clear infographic-style visual explanation. "
            "Use hierarchical layout with color-coded components. "
            "Include flow indicators (arrows, connections). "
            "Preserve spatial relationships. Simple, professional style.\n\n"
        ),
    },
    StylePreset.FIRST_PERSON: {
        "name": "First-Person POV",
        "purpose": "Immersive 'you are there' decision-moment scenes",
        "characteristics": "POV camera, hands at frame bottom, legible readouts, tense lighting",
        "best_for": "Lead-with-WHY scenarios, the moment of realization, experiential detail",
        "prompt_prefix": (
            "[Style: First-person POV photograph - immersive and photoreal]\n\n"
            "Render as a photorealistic first-person point-of-view photograph, as if the "
            "viewer's own eyes are the camera. The viewer's hands rest at the bottom of the "
            "frame (on a desk, keyboard, steering wheel, or holding the relevant object). "
            "Include the foreground props the viewer would actually see: a screen or readout "
            "showing the key numbers/output, and a notebook or printout with the question "
            "being asked. Use tense decision-moment lighting (late evening, screen glow, "
            "shallow depth of field). Any on-screen and on-paper text should be legible and "
            "specific. Put the viewer inside the moment of realization, not observing it from "
            "the outside.\n\n"
        ),
    },
    StylePreset.CUSTOM: {
        "name": "Custom",
        "purpose": "Full control over style",
        "characteristics": "User provides complete style specification",
        "best_for": "Special cases requiring specific styling",
        "prompt_prefix": "",  # No prefix, user provides everything
    },
}


def get_style_prompt_prefix(style: StylePreset) -> str:
    """Get the prompt prefix for a given style preset."""
    return STYLE_DEFINITIONS[style]["prompt_prefix"]


def list_styles() -> str:
    """Generate formatted list of available styles."""
    output = ["Style Presets", "=" * 13, ""]

    for style in StylePreset:
        definition = STYLE_DEFINITIONS[style]
        default_marker = " (default)" if style == StylePreset.EDUCATIONAL_CARTOON else ""
        output.append(f"{style.value}{default_marker}")
        output.append(f"  Purpose: {definition['purpose']}")
        output.append(f"  Characteristics: {definition['characteristics']}")
        output.append(f"  Best for: {definition['best_for']}")
        output.append("")

    output.append('Usage: gen-image --style <preset> "your prompt"')
    return "\n".join(output)
