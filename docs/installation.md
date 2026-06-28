# Installation

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/)
- An API key for at least one provider:
  [Google AI Studio](https://aistudio.google.com/apikey) or
  [OpenAI](https://platform.openai.com/api-keys)

## From source

```bash
git clone https://github.com/grepinsight/gen-image.git
cd gen-image
uv sync
uv tool install .      # exposes the `gen-image` command on your PATH
gen-image --help
```

## Set a provider key

Gemini is the default provider:

```bash
export GOOGLE_API_KEY="..."      # or GEMINI_API_KEY
```

To use OpenAI instead:

```bash
export OPENAI_API_KEY="sk-..."
gen-image --edit-config          # set provider = "openai"
```

## Persistent key (for non-interactive callers)

A shell `export` only lives for that session, so cron jobs and scripts won't see it. Put the key
in a durable, gitignored file at `~/.config/gen-image/.env` (chmod 600); gen-image loads it
automatically on every run:

```bash
mkdir -p ~/.config/gen-image
printf 'GEMINI_API_KEY=%s\n' "your-key-here" > ~/.config/gen-image/.env
chmod 600 ~/.config/gen-image/.env
```

The loader accepts `KEY=value`, an optional `export ` prefix, and quoted values, and skips
blank/comment lines. **An exported environment variable always wins** over the file. Recognized
keys: `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`.
