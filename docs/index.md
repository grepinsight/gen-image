# gen-image

**Generate educational, illustrative images from the command line** using OpenAI
(`gpt-image-2`, …) or Google Gemini image models. One command turns a prompt into a
saved PNG, with style presets and reusable templates tuned for learning material.

It works anywhere you want images on disk. If you keep an [Obsidian](https://obsidian.md) vault
(or any Markdown notes), gen-image can also print and copy a ready-to-paste `![[wikilink]]` for
the file, but that integration is entirely optional.

## Highlights

- **Two providers**: Google Gemini (default) and OpenAI, selectable via config.
- **Style presets** built for explanation: `educational-cartoon`, `mnemonic`,
  `diagram-alternative`, `custom`.
- **Templates** with variable substitution for repeatable prompts.
- **Cost-aware**: per-image cost estimates, monthly budget limits, generation history.
- **Interactive mode**, a TOML config, and `--dry-run` for zero-cost previews.

!!! note
    gen-image calls **paid** third-party APIs (OpenAI / Google) with **your own** key and is
    billed to your account. It uses the official provider SDKs and is an independent wrapper, not
    affiliated with OpenAI or Google. Model names and pricing change over time, so check each
    provider's current docs.

## At a glance

```bash
gen-image "A cartoon librarian locking a book in a safe" --output ownership.png
```

Continue with [Installation](installation.md).
