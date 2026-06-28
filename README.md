# gen-image

Generate **educational, illustrative images from the command line** using OpenAI
(`gpt-image-2`, DALL·E 3, …) or Google Gemini image models. One command turns a prompt into a
saved PNG, with style presets and reusable templates tuned for learning material.

It works anywhere you want images on disk. If you keep an [Obsidian](https://obsidian.md) vault
(or any Markdown notes), gen-image can also print and copy a ready-to-paste `![[wikilink]]` for
the file, but that integration is entirely optional.

## Why gen-image?

There are plenty of ways to call an image model from a terminal. They cluster into three groups,
and gen-image deliberately sits in the gap between them:

- **Thin DALL·E/OpenAI CLIs** ([dallecli](https://github.com/raiyanyahya/dallecli),
  [openai-cli-art](https://github.com/ghostofpokemon/openai-cli-art), the official `openai` CLI)
  are raw passthroughs: prompt in, PNG out. Single provider, no opinion about *what* you're
  making, no cost tracking, no reuse.
- **Obsidian plugins** ([AI Assistant](https://github.com/qgrail/obsidian-ai-assistant),
  [obsidian-ai-images](https://github.com/microtower00/obsidian-ai-images)) are convenient but
  GUI-locked inside the editor, not scriptable, and have no budget discipline.
- **Mega multi-provider LLM CLIs** ([aichat](https://github.com/sigoden/aichat), `llm`) do
  everything, so image generation is an afterthought bolted onto a chat pipeline with no domain
  tuning.

gen-image's job is narrower and sharper: **opinionated, cost-aware, scriptable image generation
tuned for material that teaches.** It trades breadth for taste.

| | Thin DALL·E CLIs | Obsidian plugins | aichat / `llm` | **gen-image** |
|---|---|---|---|---|
| Purpose-tuned style presets | ✗ raw | ✗ raw | ✗ raw | ✓ educational / mnemonic / diagram / first-person |
| Reusable templates (variable substitution) | ✗ | ✗ | ✗ | ✓ |
| Cost discipline (estimate, budget cap, history, stats, dry-run) | mostly ✗ | ✗ | partial | ✓ first-class |
| Scriptable CLI | ✓ | ✗ GUI-locked | ✓ | ✓ |
| Multi-provider, image-focused | ✗ OpenAI only | mixed | ✓ kitchen-sink | ✓ Gemini + OpenAI, curated |
| PKM output without lock-in | ✗ | ✗ lock-in | ✗ | ✓ optional wikilink |

The three things nothing else combines:

1. **Style presets are baked-in prompt engineering, not passthrough.** `--style educational-cartoon`
   encodes a tested prompt for memorable, text-free explanatory art. See [`GALLERY/`](GALLERY/GALLERY.md)
   for the same concept rendered across every preset.
2. **Cost is a feature.** Per-image estimates, monthly budget caps, a history log, `--stats`, and
   `--dry-run` mean you can run it daily without dreading the bill.
3. **CLI, not plugin.** Runs in cron, scripts, and any editor; the Obsidian wikilink is convenience,
   never a requirement.

The honest tradeoff: the moat is taste, not technology. A determined user could paste a good prompt
into any thin CLI and approximate the presets. The value is in the curation, the cost habits, and
the learning-focused defaults being there by default. If you want raw breadth or in-editor clicking,
the tools above serve you better.

## Highlights

- **Two providers**: Google Gemini (default) and OpenAI, selectable via config.
- **Style presets** built for explanation: `educational-cartoon`, `mnemonic`,
  `diagram-alternative`, `first-person`, `custom`.
- **Templates** with variable substitution for repeatable prompts (e.g. vocab mnemonics).
- **Cost-aware**: per-image cost estimates, monthly budget limits, generation history.
- **Interactive mode**, a TOML config, and `--dry-run` for zero-cost previews.

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/)
- An API key for at least one provider:
  [Google AI Studio](https://aistudio.google.com/apikey) or
  [OpenAI](https://platform.openai.com/api-keys)

## Install

```bash
git clone https://github.com/grepinsight/gen-image.git
cd gen-image
uv sync
uv tool install .      # exposes the `gen-image` command on your PATH
gen-image --help
```

## Setup

Set a key for your provider. Gemini is the default:

```bash
export GOOGLE_API_KEY="..."      # or GEMINI_API_KEY
# to use OpenAI instead:
export OPENAI_API_KEY="sk-..."
gen-image --edit-config          # set provider = "openai"
```

### Persistent key (recommended for non-interactive callers)

A shell `export` only lives for that session, so cron jobs and scripts won't see it. Put the key
in a durable, gitignored file at `~/.config/gen-image/.env` (chmod 600) and gen-image loads it
automatically on every run:

```bash
mkdir -p ~/.config/gen-image
printf 'GEMINI_API_KEY=%s\n' "your-key-here" > ~/.config/gen-image/.env
chmod 600 ~/.config/gen-image/.env
```

The loader accepts `KEY=value`, an optional `export ` prefix, and quoted values, and skips
blank/comment lines. **An exported environment variable always wins** over the file. Recognized
keys: `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`.

## Usage

### Basic generation

```bash
gen-image "A cartoon librarian locking a book in a safe" --output ownership.png
```

### Style presets

```bash
gen-image "Technical concept..." --style educational-cartoon --output img.png   # default
gen-image "Visual wordplay..."   --style mnemonic            --output vocab.png
gen-image "System architecture..." --style diagram-alternative --output diagram.png
gen-image "Late-night trading desk, a screen reading -50%..." --style first-person --output scene.png
gen-image --list-styles
```

### Templates

```bash
gen-image --list-templates
gen-image --show-template mnemonic-vocab

gen-image --template mnemonic-vocab \
  --var word="語りかける" \
  --var romaji="katarikakeru" \
  --var meaning="to address, to speak to" \
  --var concept="words as birds flying to the ear" \
  --output vocab.png

gen-image --edit-template my-custom-template   # create/edit in $EDITOR
```

### Options

```bash
gen-image "..." --output img.png --quality hd          # higher quality, costs more
gen-image "..." --output img.png --size 1792x1024      # landscape (or 1024x1792 portrait)
gen-image "..." --output img.png --show-prompt         # preview the full prompt
gen-image "..." --output img.png --dry-run             # no API call, no cost
```

### Interactive, config, history

```bash
gen-image --interactive          # guided prompts
gen-image --show-config          # view config
gen-image --edit-config          # edit config in $EDITOR
gen-image --list-models          # list available models per provider
gen-image --history              # generation history
gen-image --history-search rust  # search history
gen-image --stats                # cost statistics
```

## Providers

### Gemini (default)

- **Models**: `gemini-3.1-flash-image-preview` (default), `gemini-3-pro-image-preview`,
  `gemini-2.5-flash-image`
- **Cost**: ~$0.039 per image
- **Key**: `GEMINI_API_KEY` or `GOOGLE_API_KEY`

### OpenAI

- **Models**: `gpt-image-2`, `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini`,
  `dall-e-3` (legacy)
- **Cost**: $0.04 (standard) / $0.08 (HD)
- **Key**: `OPENAI_API_KEY`

> [!NOTE]
> gen-image calls **paid** third-party APIs (OpenAI / Google) with **your own** key and is billed
> to your account. These are official provider SDKs; gen-image is an independent wrapper and is not
> affiliated with OpenAI or Google. Model names and pricing change over time, so check each
> provider's current docs.

## Output

```
✅ Image generated successfully

File: attachments/ownership.png
Size: 1024x1024
Cost: $0.04

Wikilink:
![[ownership.png]]
✓ Copied to clipboard
```

- If the output file already exists, gen-image auto-increments (`file-1.png`, `file-2.png`, …).
- The `![[wikilink]]` is convenience for Obsidian/Markdown users and can be disabled in config.

## Development

```bash
just test     # pytest suite
just lint     # ruff
```

Documentation site (MkDocs):

```bash
uv tool install mkdocs --with mkdocs-material
mkdocs serve     # http://127.0.0.1:8000
```

## License

[MIT](LICENSE).
