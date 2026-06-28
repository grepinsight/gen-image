# Changelog

All notable changes to gen-image are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com); this project uses semantic versioning.

## [0.4.0]: 2026-06-28

### Added
- New `first-person` style preset: an immersive, photoreal first-person POV scene (hands at the
  frame bottom, legible on-screen readouts, decision-moment lighting) that drops the viewer inside
  the moment of realization. Use it for "lead with WHY" scenarios and experiential illustrations:
  `gen-image "..." --style first-person`. Previously this had to be hand-written via `--style custom`.

## [0.3.0]: 2026-06-28

### Changed
- Repositioned as a general-purpose CLI: image generation is the headline, and the Obsidian
  wikilink output is now a documented optional convenience rather than the framing.
- `_handle_error` in both generators now returns a helpful `RuntimeError` (raised by the caller
  with the original cause preserved) instead of printing and re-raising the raw exception, so
  every API failure surfaces a clear, non-empty message.

### Added
- MkDocs documentation site and an MIT license.

### Removed
- Stale `tests/test_cli_overrides.py`, which tested a `--model`/`--provider`/`compare`/`--ref`
  flag surface that the current CLI no longer exposes.

## [0.2.0]: 2026-06-23

### Added
- Auto-load API keys from `~/.config/gen-image/.env` on every run (`config.load_config_env`). Non-interactive callers (cron jobs, scripts shelling out to `gen-image`) no longer need a shell `export` to resolve `GEMINI_API_KEY` / `GOOGLE_API_KEY` / `OPENAI_API_KEY`. An exported environment variable still takes precedence over the file. Zero new dependency (tiny stdlib parser; handles `export ` prefix, quotes, comments, blanks).
- `config.config_dir()` helper to resolve the config directory (honors `XDG_CONFIG_HOME`).

### Changed
- `ConfigManager` now resolves its config path via `config_dir()` (single source of truth).
