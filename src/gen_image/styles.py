"""Style preset definitions for image generation."""

from enum import Enum
from typing import Dict


class StylePreset(str, Enum):
    """Available style presets."""

    EDUCATIONAL_CARTOON = "educational-cartoon"
    MNEMONIC = "mnemonic"
    DIAGRAM_ALTERNATIVE = "diagram-alternative"
    FIRST_PERSON = "first-person"
    MANGA_STRIP = "manga-strip"
    VINTAGE_BLUEPRINT = "vintage-blueprint"
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
    StylePreset.MANGA_STRIP: {
        "name": "Manga Strip",
        "purpose": "Step-by-step educational storytelling",
        "characteristics": "2x4 panel comic grid, sequential narrative, clear reading order",
        "best_for": "Workflows, procedures, before/after sequences, walkthroughs",
        "prompt_prefix": (
            "[Style: Educational manga strip - sequential panels]\n\n"
            "Compose as a clean comic strip on a 2x4 grid of equal panels with visible "
            "gutters, read left-to-right then top-to-bottom. Each panel advances one step of "
            "the narrative, with a consistent character or object carried across panels for "
            "continuity. Flat, friendly line art with a limited color palette. Keep any panel "
            "captions or labels short, legible, and in clear sans-serif. The sequence should "
            "read as a self-explanatory walkthrough even without prose.\n\n"
        ),
    },
    StylePreset.VINTAGE_BLUEPRINT: {
        "name": "Vintage Blueprint",
        "purpose": "Inventions, underlying principles, and design rationale",
        "characteristics": "Patent-style technical drawing, aged paper, callouts and annotations",
        "best_for": "History of a technology, how-it-works cross-sections, why-this-design",
        "prompt_prefix": (
            "[Style: Vintage patent blueprint - technical draftsmanship]\n\n"
            "Render as an antique patent-style technical drawing: precise line work on aged "
            "blueprint or cream parchment, fine hatching and cross-section views. Add numbered "
            "callout leaders and small handwritten-style annotation labels naming the parts. "
            "Include a title-block aesthetic in a corner. Monochrome or duotone (blueprint blue, "
            "or sepia ink on cream). The drawing should explain the mechanism and the rationale "
            "behind the design, like a figure from an old patent filing.\n\n"
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
