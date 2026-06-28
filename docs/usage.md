# Usage

## Basic generation

```bash
gen-image "A cartoon librarian locking a book in a safe" --output ownership.png
```

## Common options

```bash
gen-image "..." --output img.png --quality hd          # higher quality, costs more
gen-image "..." --output img.png --size 1792x1024      # landscape (or 1024x1792 portrait)
gen-image "..." --output img.png --show-prompt         # preview the full prompt
gen-image "..." --output img.png --dry-run             # no API call, no cost
```

Valid sizes are `1024x1024`, `1792x1024`, and `1024x1792`. If the output file already exists,
gen-image auto-increments (`file-1.png`, `file-2.png`, …).

## Interactive mode

```bash
gen-image --interactive      # guided prompts: type, concept, output path, confirm
```

## Configuration

```bash
gen-image --show-config      # view current config
gen-image --edit-config      # edit config in $EDITOR (provider, budget, defaults)
gen-image --list-models      # list available models per provider
```

## History & cost

```bash
gen-image --history                  # generation history
gen-image --history-search rust      # search history
gen-image --history-limit 25         # cap history results
gen-image --stats                    # cost statistics
```

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

The `![[wikilink]]` is a convenience for Obsidian/Markdown users and can be disabled in config.
