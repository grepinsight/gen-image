# Reference / Cast System, Design Spec

- **Project:** gen-image CLI
- **Date:** 2026-06-28
- **Status:** Draft, awaiting review
- **Increment:** 1 of 2 (this spec). Increment 2 is the image-input verbs (`edit`, `restyle`, `compose`, `annotate`), which reuse the core built here.

## Goal

Let a user pin down a visual subject once (a character, an object, a style anchor) and feature it **consistently** across many later generations. The motivating use case: create a `professor` persona, then have that same professor appear in illustration after illustration so a whole note set shares a coherent cast.

## Validation (done before this spec)

The mechanism (reference image + instruction passed back into the model) was verified live on 2026-06-28 with `gemini-3.1-flash-image-preview`. A generated professor was successfully re-featured, identity intact, across two different scenes (lecture, library). Localized `edit`, `restyle`, `annotate`, and `compose` were also confirmed. `variations` (no DALL·E-2 access) and true `upscale` (no native endpoint) are **not** supported and are out of scope.

## Scope

**In (increment 1):**
- A shared image-input core: `edit_image(inputs: list[Path], instruction: str, ...)` on both `GeminiGenerator` and `OpenAIGenerator`. Internal foundation; not yet surfaced as verbs.
- `ref` subcommand group: `add` (generate-and-cache, or `--from <file>` import), `list`, `show`, `rm`.
- Sticky pins: `ref pin <name>`, `ref unpin [name]`, `ref status`.
- `--ref <name>` (repeatable) and `--no-ref` on the default generate command.
- Active-reference echo on every generation that applies one.
- On-disk reference store + JSON manifest.

**Out (later / cut):**
- The four image-input verbs (increment 2).
- `variations`, `upscale` (not natively supported).

## CLI surface (Option A: real subcommands, back-compat preserved)

The current flat `gen-image [PROMPT]` becomes a Typer app with `invoke_without_command=True`: a bare `gen-image "prompt"` still runs generation (back-compat), while named subcommands are added alongside.

```
gen-image "lecturing at a chalkboard" --ref professor      # generate, conditioned on a ref
gen-image "..." --ref professor --ref robot                # multiple refs in one scene
gen-image "..." --no-ref                                   # ignore any pinned refs this call

gen-image ref add professor "white-bearded cartoon professor, round glasses, tweed, bow tie"
gen-image ref add robot --from ./my-robot.png              # import existing image
gen-image ref list
gen-image ref show professor
gen-image ref rm professor
gen-image ref pin professor                                # sticky: applies to later gens
gen-image ref unpin                                        # clear all pins
gen-image ref status                                       # what's pinned right now
```

## Data model

```
$GEN_IMAGE_REF_DIR  (default: ~/.config/gen-image/refs/)
  professor.png
  robot.png
  refs.json
```

`refs.json`:
```json
{
  "refs": {
    "professor": {
      "file": "professor.png",
      "source": "generated",          // "generated" | "imported"
      "prompt": "white-bearded ...",  // null for imported
      "model": "gemini-3.1-flash-image-preview",
      "aspect": "16:9",
      "created_at": "2026-06-28T18:40:00"
    }
  },
  "pinned": ["professor"]
}
```

## Reference resolution rules

Effective references for a generation, in precedence order:
1. If `--no-ref` is given, use **none**.
2. Else if one or more `--ref` are given, use **exactly those** (explicit overrides pins).
3. Else use whatever is in `pinned` (possibly empty).

When the effective set is non-empty, the CLI prints `(using ref: professor, robot)` before generating, so a pin is never silently applied. Unknown ref name is a hard error listing available refs.

## Provider routing

- **Gemini (default, recommended for consistency):** `generate_content(contents=[Part.from_bytes(ref1), ..., Part.from_text(wrapped_prompt)])`. The wrapped prompt prepends a consistency directive: "Feature the provided reference subject(s) exactly; keep their design identical. Scene: <user prompt>."
- **OpenAI:** `images.edit(image=<ref(s)>, prompt=wrapped_prompt)`. Single-ref is straightforward; multi-ref support depends on SDK version and degrades with a clear message if unavailable.
- Provider/model selection reuses the existing `config.api.model`.

## Aspect & style pinning

The demo showed aspect/style can drift across reference reuse. Mitigations:
- Carry the generation's `--size` (aspect) into the request; default to the reference's stored `aspect` if `--size` is unset.
- Carry `--style` through; default reference generation (`ref add`) to a neutral, identity-focused framing so the cached reference is reusable.

## Reuse of existing modules (no reinvention)

- `cost_tracker.py`: `ref add` and every `--ref` generation record cost (which refs used).
- history: log refs used per generation.
- `utils.py`: wikilink/output path logic, unchanged.
- `styles.py`: available to `ref add` and to increment-2 `restyle`.

## Error handling

- Missing ref name → error + `ref list` of available names.
- `--from` file missing / not an image → clear error.
- Provider can't honor multi-ref → explain and suggest Gemini.
- Budget exceeded → existing budget-cap behavior applies.

## Testing

- Unit tests with mocked SDK clients: each `ref` subcommand, resolution precedence (`--ref` / `--no-ref` / pinned), manifest read/write, echo output.
- **Back-compat regression:** the existing 49 tests must stay green through the callback to `invoke_without_command` migration. This is the main risk.
- One opt-in live test (real API) behind an env var, excluded from CI.

## Trade-offs

- **Sticky pin convenience vs hidden state.** Pins make the "throughout subsequent generations" flow frictionless but introduce state a user can forget. Mitigated by echoing the active ref on every call and a `ref status` command and `--no-ref` escape hatch.
- **Subcommands (A) vs flags (B).** Chose A for discoverability and scaling to many verbs; cost is Typer back-compat plumbing to keep bare `gen-image "prompt"` working.
- **One shared `edit_image` core vs per-verb methods.** Chose shared for DRY (references + all four future verbs ride it); cost is the core must stay general enough for every caller.
- **Files (PNG + JSON) vs a database for the store.** Chose files for inspectability and zero dependencies; cost is no concurrent-write safety (acceptable for a single-user CLI).
- **Image-input conditioning vs fine-tuning/embeddings for consistency.** Chose image-input: works today, no training, no per-character cost; the price is occasional aspect/style drift, addressed by the pinning rules above.

## Locked decisions

- All four verbs will ship eventually; build order is **references first** (this spec), then `edit`/`restyle`, then `compose`/`annotate`.
- CLI shape: **Option A** (real subcommands).
- Reuse UX: **both** `--ref` and sticky `pin`, with echo + `--no-ref`.
