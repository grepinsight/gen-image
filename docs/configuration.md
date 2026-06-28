# Configuration

gen-image reads a TOML config at `~/.config/gen-image/config.toml` (honoring `XDG_CONFIG_HOME`).
A default is created on first run. View and edit it with:

```bash
gen-image --show-config
gen-image --edit-config      # opens in $EDITOR
```

## Example

```toml
[general]
# Optional: path to your notes/vault root (used to resolve relative output paths)
# vault_path = "/path/to/your/notes"

# Default attachments directory (relative to vault_path, or absolute)
attachments_dir = "attachments"

# Default style preset
default_style = "educational-cartoon"

[api]
provider = "gemini"                         # "gemini" or "openai"
model = "gemini-3.1-flash-image-preview"
quality = "standard"                        # "standard" or "hd"
size = "1024x1024"

[costs]
budget_limit = 10.0                         # monthly USD cap (omit for no cap)
warn_at_percent = 80                        # warn once spend crosses this %

[output]
auto_copy_wikilink = true                   # copy ![[file.png]] to the clipboard
```

## API keys

Keys are **not** stored in this config. Provide them via the environment or the gitignored
`~/.config/gen-image/.env` file (see [Installation](installation.md)). Recognized keys:
`GEMINI_API_KEY`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`.

## Wikilink output

`auto_copy_wikilink` controls the Obsidian convenience: when enabled, a successful generation
copies `![[<filename>.png]]` to your clipboard. Set it to `false` if you don't use Markdown
wikilinks.
