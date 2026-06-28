# Styles & templates

## Style presets

Each preset wraps your prompt with instructions tuned for a kind of explanatory image.

| Style | Use it for |
|---|---|
| `educational-cartoon` (default) | friendly, clear illustrations of a concept |
| `mnemonic` | memorable visual wordplay for language/vocab learning |
| `diagram-alternative` | an illustrative stand-in for a dry diagram |
| `first-person` | an immersive "you are there" POV scene at the decision moment |
| `custom` | no preset wrapping; your prompt is used verbatim |

```bash
gen-image "Technical concept..."   --style educational-cartoon --output img.png
gen-image "Visual wordplay..."     --style mnemonic            --output vocab.png
gen-image "System architecture..." --style diagram-alternative --output diagram.png
gen-image "Trading desk at midnight, a screen reading -50%..." --style first-person --output scene.png
gen-image --list-styles
```

The `first-person` preset renders a photorealistic point-of-view photograph: the viewer's hands at
the bottom of the frame, foreground props (a screen with the key readout, a notebook with the
question), and tense decision-moment lighting. You supply the subject; the preset supplies the POV
framing and the moment-of-realization mood. Because it leans on legible on-screen text, keep the
text-capable model selected (the default `gemini-3-pro-image-preview`).

## Templates

Templates are reusable prompts with `{{variable}}` placeholders, so a repeatable shape (like a
vocabulary mnemonic) is filled in per call.

```bash
gen-image --list-templates
gen-image --show-template mnemonic-vocab

gen-image --template mnemonic-vocab \
  --var word="語りかける" \
  --var romaji="katarikakeru" \
  --var meaning="to address, to speak to" \
  --var concept="words as birds flying to the ear" \
  --output vocab.png
```

Built-in templates: `educational-metaphor`, `mnemonic-vocab`, `visual-comparison`.

Create or edit your own (stored under your config directory) in `$EDITOR`:

```bash
gen-image --edit-template my-custom-template
```
