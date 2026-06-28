# Providers & cost

gen-image supports two providers. Choose one with `gen-image --edit-config` (set `provider`),
and per-provider model with the same config.

## Gemini (default)

- **Models**: `gemini-3.1-flash-image-preview` (default), `gemini-3-pro-image-preview`,
  `gemini-2.5-flash-image`
- **Cost**: ~$0.039 per image
- **Key**: `GEMINI_API_KEY` or `GOOGLE_API_KEY`

## OpenAI

- **Models**: `gpt-image-2`, `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini`
- **Cost**: $0.04 (standard) / $0.08 (HD)
- **Key**: `OPENAI_API_KEY`

!!! warning "You are billed by the provider"
    gen-image calls **paid** APIs with **your own** key; every generation is billed to your
    OpenAI or Google account. Use `--dry-run` to preview a prompt and cost with no API call, and
    set a monthly budget in the config to get warnings and a hard stop.

## Budgets

The config supports a monthly budget limit and a warning threshold. When a generation would push
the month's spend over the limit, gen-image warns (and asks to confirm) before calling the API.
See [Configuration](configuration.md).

## Model names change

Provider model lineups and pricing change over time. Run `gen-image --list-models` to see what
this version knows about, and check the provider's own docs for the current catalog.
