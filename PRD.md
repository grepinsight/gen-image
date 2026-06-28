# PRD: gen-image - Educational Image Generator for Obsidian

## Problem Statement

Evergreen notes need memorable, instructive, and engaging images to improve recall and make abstract concepts concrete. Current workflow requires:
1. Leaving the note editor
2. Opening separate image generation tools
3. Managing prompts manually
4. Downloading and organizing files
5. Manually formatting wikilinks

This breaks flow and creates friction that discourages adding visual aids to notes.

## Vision

A **zero-friction CLI** that generates educational images optimized for learning, saves them to the vault, and returns ready-to-paste wikilinks—all in one command.

**Core principle**: Keep user in their editor. The tool should feel like an extension of the note-writing process, not a separate task.

## Target Users

**Primary**: Knowledge workers building personal knowledge bases (PKM enthusiasts, students, researchers)
- Writing evergreen notes on technical concepts
- Creating mnemonic aids for language learning
- Explaining complex ideas with visual metaphors
- Building reusable educational materials

**Use cases**:
1. **Technical concept illustration** - "I just wrote about Rust ownership. I need a cartoon showing the reading room metaphor."
2. **Mnemonic creation** - "I need a memorable image for this Japanese vocabulary word."
3. **Diagram alternative** - "This is too complex for mermaid. I need a visual."
4. **Recurring patterns** - "I generate similar images often. I need templates."

## Core Requirements

### 1. Simple CLI Interface

```bash
# Inline prompt (80% use case - quick and direct)
gen-image "A cartoon librarian locking a book in a safe" --output ownership.png

# Template-based (20% use case - reusable patterns)
gen-image --template mnemonic --var word=語りかける

# Prompt from file (edge case - complex multi-line prompts)
gen-image --prompt-file ./custom-prompt.txt --style educational-cartoon

# Interactive mode (learning/exploration)
gen-image --interactive
```

**Why this interface?**
- Inline prompt is fastest for one-offs (optimized for common case)
- Templates for recurring patterns (DRY principle)
- Prompt files for complex/multi-paragraph prompts
- Interactive mode lowers learning curve

### 2. Built-in Style Presets

**Preset: `educational-cartoon` (default)**
```
Style: Bright, vibrant cartoon illustration
Purpose: Explain technical concepts memorably
Characteristics:
  - Clear visual metaphors
  - Bright colors (#51cf66, #4dabf7, #ffd43b palette)
  - Simple, uncluttered composition
  - No text in image (text in caption instead)
  - Slightly humorous but instructive
```

**Preset: `mnemonic`**
```
Style: Absurd but memorable visual puns
Purpose: Language learning memory aids
Characteristics:
  - Sound-alike visual wordplay
  - Surprising/unexpected elements
  - Emotionally engaging (humor, surprise)
  - Cultural elements when appropriate
```

**Preset: `diagram-alternative`**
```
Style: Infographic-style visual explanation
Purpose: Complex systems/relationships
Characteristics:
  - Hierarchical layout
  - Color-coded components
  - Flow indicators (arrows, connections)
  - Spatial relationships preserved
```

**Preset: `custom`**
```
Purpose: Full control over style
Characteristics: User provides complete style specification
```

**Why presets?**
- Consistency across notes (coherent visual language)
- Faster prompting (don't repeat style requirements)
- Better results (tested prompts that work well)
- Learnable system (user understands what each preset does)

**Tradeoff**: Presets limit creative control vs full custom prompts. Resolution: Default to presets for consistency, allow override with `--style custom` for special cases.

### 3. Template System

**Location**: `~/.config/gen-image/templates/`

**Built-in templates**:
- `educational-metaphor.txt` - For technical concept illustrations
- `mnemonic-vocab.txt` - For language learning
- `visual-comparison.txt` - For A vs B explanations

**Template format** (simple variable substitution):
```
Style: {{style_preset}}

Create a memorable illustration showing {{concept}}.

Visual metaphor: {{metaphor}}

The image should:
- Use {{primary_color}} as the dominant color
- Include {{key_elements}}
- Convey the feeling of {{emotion}}

Technical requirements:
- No text in image
- Simple, clear composition
- One surprising element for memorability
```

**Usage**:
```bash
gen-image --template educational-metaphor \
  --var concept="Rust BufReader ownership" \
  --var metaphor="librarian locking book in safe" \
  --var primary_color="blue" \
  --var key_elements="librarian, book, safe, reading room" \
  --var emotion="trust and safety"
```

**Why templates?**
- Reusable patterns (Japanese vocab images all use same structure)
- Iteration and refinement (improve template over time)
- Shareable (export successful templates)
- Consistency (same pattern = same quality)

**Tradeoff**: Templates add complexity vs inline prompts. Resolution: Make templates optional. Inline is default, templates for power users.

### 4. Output Path Handling

**Core principle: Be explicit, not magical. User controls where files go.**

**Path resolution**:
```bash
# Full absolute path - use as-is
gen-image "..." --output /path/to/your/notes/attachments/ownership.png

# Relative path - relative to current working directory
gen-image "..." --output ./images/ownership.png
gen-image "..." --output ownership.png  # saves to current directory

# Just filename - save to current directory
gen-image "..." --output ownership.png  # → ./ownership.png

# No output specified - error, must be explicit
gen-image "..."
❌ Error: --output is required
Usage: gen-image PROMPT --output PATH
```

**Why explicit paths?**
- ✅ No surprises - you know exactly where the file goes
- ✅ Works anywhere - not tied to Obsidian vault structure
- ✅ Scriptable - predictable behavior for automation
- ❌ More typing - but clarity > convenience

**Optional: Vault path shorthand (convenience, not default)**:
```bash
# Set vault path once
export VAULT_PATH="$HOME/notes"

# Then use ~ shorthand
gen-image "..." --output ~/attachments/ownership.png
# Expands to: $VAULT_PATH/attachments/ownership.png
```

**File naming when only directory specified**:
```bash
# Auto-generate filename based on prompt
gen-image "A cartoon librarian..." --output ./attachments/
# → ./attachments/cartoon-librarian-1729468800.png

# Topic extracted from prompt (first 3 meaningful words, kebab-cased)
# Timestamp appended for uniqueness
```

**Conflict resolution**:
- If file exists: append `-1`, `-2`, etc.
- Never silently overwrite
- Show clear message: "File exists, saving as ownership-1.png"

**Output format**:
```bash
$ gen-image "A cartoon librarian..." --output ownership.png

[Generating image... (10s)]
✅ Image generated successfully

File: /path/to/your/notes/attachments/ownership.png
Size: 1024x1024
Cost: $0.04

Wikilink (copy to clipboard):
![[ownership.png]]
```

**Why this design?**
- Auto-detection reduces configuration (user just sets VAULT_PATH once)
- Smart naming makes files discoverable later
- Wikilink format is immediately usable (paste directly in note)
- Cost visibility prevents surprise bills

**Tradeoff**: Auto-magic vs explicit control. Resolution: Smart defaults with clear override options.

### 5. Image Generation Backend

**Provider**: OpenAI DALL-E 3

**Why DALL-E 3?**
- Consistent quality (critical for educational images)
- Strong prompt following (complex requirements like "no text" actually work)
- Simple API (no complex model management)
- Fast iteration (no local setup/GPU needed)

**Why NOT alternatives?**
- ❌ Stable Diffusion: Requires more prompt engineering, less consistent, local setup overhead
- ❌ Midjourney: Discord-based, not CLI-friendly, harder to automate
- ❌ DALL-E 2: Lower quality than DALL-E 3

**API configuration**:
```bash
export OPENAI_API_KEY="sk-..."
export OBSIDIAN_VAULT_PATH="$HOME/notes"
```

**Parameters**:
- `quality`: "standard" (default) | "hd"
  - Standard: Faster, cheaper ($0.040/image), sufficient for most use cases
  - HD: More detail ($0.080/image), use for complex diagrams
- `size`: "1024x1024" (default) | "1792x1024" (landscape) | "1024x1792" (portrait)
  - Square: General purpose
  - Landscape: Wide diagrams, process flows
  - Portrait: Tall lists, hierarchies

**Tradeoff**: Cost vs quality. Resolution: Default to standard quality (80% of use cases), allow HD override for special cases.

### 6. Cost Management

**Features**:
1. **Pre-flight cost estimate**:
   ```bash
   $ gen-image "..." --dry-run

   Would generate:
   - Model: DALL-E 3
   - Size: 1024x1024
   - Quality: standard
   - Estimated cost: $0.04

   Prompt preview:
   [Style: Educational cartoon]
   A cartoon librarian locking a book in a safe...

   Run without --dry-run to generate.
   ```

2. **Generation history log**:
   - Location: `~/.config/gen-image/history.jsonl`
   - Format: One JSON object per line
   ```json
   {"timestamp": "2025-10-20T10:30:00Z", "prompt": "...", "cost": 0.04, "file": "ownership.png", "model": "dall-e-3"}
   ```

3. **Cost tracking command**:
   ```bash
   $ gen-image --stats

   Generation Statistics
   =====================
   Total images: 47
   Total cost: $2.16
   This month: $0.48 (12 images)

   Most expensive: 2025-10-15 (HD landscape) - $0.12
   Most recent: 2025-10-20 (standard square) - $0.04
   ```

4. **Budget warnings**:
   ```bash
   $ gen-image --budget-limit 5.00  # Set monthly limit

   Warning: You've spent $4.80 this month (limit: $5.00)
   This generation ($0.04) will put you at $4.84
   Continue? [y/N]
   ```

**Why cost tracking?**
- API costs add up silently
- Budget awareness prevents surprises
- History enables prompt refinement (see what worked)
- Dry-run prevents accidental expensive generations

**Tradeoff**: Complexity vs control. Resolution: Make tracking automatic (zero config), make budget limits optional.

### 7. Discoverability and Debugging

**Critical principle: Make the invisible visible. User should never have to guess what's available or what will happen.**

#### Template Discovery and Editing

```bash
# List all available templates
$ gen-image --list-templates

Available Templates
===================
Built-in:
  educational-metaphor    For technical concept illustrations
  mnemonic-vocab          For language learning
  visual-comparison       For A vs B explanations

Custom (in ~/.config/gen-image/templates/):
  rust-ownership          Your custom Rust concept template
  japanese-verb           Your custom verb mnemonic template

Usage: gen-image --template <name> --var key=value...
Edit: gen-image --edit-template <name>
```

```bash
# Show what variables a template needs
$ gen-image --template mnemonic-vocab --show-template

Template: mnemonic-vocab
Location: ~/.config/gen-image/templates/mnemonic-vocab.txt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Required variables:
  - word: The Japanese word (kanji/kana)
  - romaji: Pronunciation
  - meaning: English meaning
  - concept: Visual mnemonic concept

Optional variables:
  - cultural_element: Japanese cultural element to include (default: none)
  - primary_color: Dominant color (default: auto)

Preview with example values:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Style: Mnemonic - absurd and memorable]

Create a memorable mnemonic image for the Japanese word "{{word}}" ({{romaji}}).

Meaning: {{meaning}}

Visual concept: {{concept}}
...
```

**Template editing**:
```bash
# Edit existing template in neovim
$ gen-image --edit-template mnemonic-vocab
# Opens: ~/.config/gen-image/templates/mnemonic-vocab.txt in neovim

# Edit custom template
$ gen-image --edit-template rust-ownership
# Opens: ~/.config/gen-image/templates/rust-ownership.txt in neovim

# Create new template (if doesn't exist, creates from scaffold)
$ gen-image --edit-template my-new-template
Template 'my-new-template' doesn't exist. Create it? [Y/n]: y
Creating template scaffold...
# Opens new file with basic template structure

# Edit built-in template (creates custom copy)
$ gen-image --edit-template educational-metaphor
Built-in template. Create custom copy to edit? [Y/n]: y
Copied to: ~/.config/gen-image/templates/educational-metaphor.txt
# Opens custom copy in neovim
# Note: Custom templates override built-ins with same name
```

**Editor selection**:
```bash
# Respects $EDITOR environment variable
export EDITOR="nvim"  # Use neovim
export EDITOR="vim"   # Use vim
export EDITOR="code --wait"  # Use VS Code

# Fallback order if $EDITOR not set:
# 1. nvim (if available)
# 2. vim
# 3. vi
# 4. nano
```

**Template scaffold for new templates**:
```
# Template: {{template_name}}
# Variables: {{var1}}, {{var2}}
# Style: educational-cartoon | mnemonic | diagram-alternative | custom

[Style: {{style}}]

{{prompt_content}}

Technical requirements:
- No text in image
- {{additional_requirements}}
```

#### Provider Discovery and Selection

```bash
# List available providers and their status
$ gen-image --list-providers

Image Generation Providers
===========================
✅ openai (active, configured)
   - Model: DALL-E 3
   - Quality: standard | hd
   - Sizes: 1024x1024, 1792x1024, 1024x1792
   - Cost: $0.04 (standard), $0.08 (hd)
   - API key: Configured ✓

⚠ stable-diffusion (available, not configured)
   - Model: SDXL
   - Requires: REPLICATE_API_KEY or local setup
   - Cost: ~$0.002/image (Replicate)
   - Setup: gen-image config --provider stable-diffusion

❌ local (not available)
   - Requires local Stable Diffusion installation
   - Setup guide: gen-image --help local-setup

Current default: openai
Change default: gen-image config --default-provider <name>
Override for one command: gen-image --provider <name> ...
```

**Inline provider override**:
```bash
# Use default provider (from config)
gen-image "..." --output img.png

# Override provider for this generation only
gen-image --provider openai "..." --output img.png
gen-image --provider stable-diffusion "..." --output img.png

# Override provider AND model-specific options
gen-image --provider openai --quality hd --size 1792x1024 "..." --output img.png

# Show what each provider supports
gen-image --provider openai --help
gen-image --provider stable-diffusion --help
```

**Provider-specific flags**:
```bash
# OpenAI-specific
--quality standard|hd       # Image quality (default: standard)
--size 1024|1792x1024|1024x1792  # Image dimensions

# Stable Diffusion-specific (future)
--steps 50                  # Inference steps
--guidance 7.5              # CFG scale
--seed 42                   # Random seed for reproducibility

# Note: Provider must be specified or set as default
# Incompatible flags are ignored with warning
```

#### Prompt Preview and Debugging

```bash
# See the exact prompt that will be sent (without generating)
$ gen-image "A cartoon librarian..." --show-prompt

Generated Prompt (will be sent to DALL-E 3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Style: Educational cartoon - bright, vibrant colors]

A cartoon librarian locking a book in a safe. Use bright
colors (#51cf66, #4dabf7, #ffd43b palette). Clear visual
metaphor, simple composition, no text in image, slightly
humorous but instructive.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provider: openai (DALL-E 3)
Size: 1024x1024
Quality: standard
Estimated cost: $0.04

Add --dry-run to skip generation
Remove --show-prompt to hide this and generate
```

```bash
# Combine with dry-run to preview everything
$ gen-image --template mnemonic-vocab \
    --var word="語りかける" \
    --var romaji="katarikakeru" \
    --var meaning="to address, to speak to" \
    --var concept="words transforming into birds flying to someone's ear" \
    --dry-run

Template Expansion
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Template: mnemonic-vocab
Variables:
  word = 語りかける
  romaji = katarikakeru
  meaning = to address, to speak to
  concept = words transforming into birds flying to someone's ear

Generated Prompt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Style: Mnemonic - absurd and memorable]

Create a memorable mnemonic image for the Japanese word
"語りかける" (katarikakeru).

Meaning: to address, to speak to

Visual concept: words transforming into birds flying to
someone's ear

Include surprising/unexpected elements. Emotionally engaging
(humor, surprise). No text in image.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Would generate with:
  Provider: openai (DALL-E 3)
  Size: 1024x1024
  Quality: standard
  Cost: $0.04
  Output: attachments/katarikakeru-1729468800.png

Remove --dry-run to generate this image.
```

#### Style Discovery

```bash
# List all style presets
$ gen-image --list-styles

Style Presets
=============
educational-cartoon (default)
  Purpose: Explain technical concepts memorably
  Characteristics: Bright colors, clear metaphors, no text
  Best for: Rust ownership, algorithms, system design

mnemonic
  Purpose: Language learning memory aids
  Characteristics: Absurd visual puns, surprising elements
  Best for: Vocabulary words, concepts with sound-alike words

diagram-alternative
  Purpose: Complex systems/relationships
  Characteristics: Infographic style, color-coded, spatial layout
  Best for: Architectures, workflows, hierarchies

custom
  Purpose: Full control over style
  Usage: Provide complete style specification in prompt

Usage: gen-image --style <preset> "your prompt"
```

#### Configuration Inspection and Editing

```bash
# Show current configuration
$ gen-image --show-config

Configuration
=============
Config file: ~/.config/gen-image/config.toml

[general]
vault_path = /path/to/your/notes
attachments_dir = attachments
default_style = educational-cartoon

[api]
provider = openai ✓ configured
model = dall-e-3
quality = standard
size = 1024x1024

[costs]
budget_limit = 10.00
warn_at_percent = 80
current_month_spend = 2.48

[output]
auto_copy_wikilink = true
naming_pattern = {topic}-{timestamp}

Edit config: gen-image --edit-config
Reset to defaults: gen-image config --reset
```

**Configuration editing**:
```bash
# Edit config file in $EDITOR
$ gen-image --edit-config
# Opens: ~/.config/gen-image/config.toml in $EDITOR

# If config doesn't exist, creates default
$ gen-image --edit-config
Config file doesn't exist. Create default? [Y/n]: y
Creating default config...
# Opens new config.toml with all defaults commented with explanations
```

**Note**: All editing commands (`--edit-template`, `--edit-config`) respect `$EDITOR`:
- Falls back to nvim → vim → vi → nano if `$EDITOR` not set
- Waits for editor to close before continuing
- Validates syntax after editing (for config.toml)

#### Generation History Inspection

```bash
# Show recent generations with their prompts
$ gen-image --history --limit 5

Recent Generations
==================
2025-10-20 10:30:15 | ownership.png | $0.04
  Prompt: "A cartoon librarian locking a book in a safe..."
  Provider: openai/dall-e-3 (standard, 1024x1024)

2025-10-19 14:22:03 | katari.png | $0.04
  Template: mnemonic-vocab (word=語りかける)
  Provider: openai/dall-e-3 (standard, 1024x1024)

2025-10-18 09:15:42 | memory-layout.png | $0.12
  Prompt: "A cross-section view of memory layout..."
  Provider: openai/dall-e-3 (hd, 1792x1024)

...

Total: 47 generations, $2.16 spent
View full history: gen-image --history --all
Search history: gen-image --history --search "rust"
```

**Why these features?**
- **Discoverability**: No guessing what templates/styles/providers exist
- **Debugging**: See exact prompt before spending money
- **Learning**: Understand how templates expand
- **Confidence**: Know what will happen before it happens
- **Iteration**: Easy to refine prompts based on preview

**Tradeoff**: More commands to learn vs trial-and-error. Resolution: Make discovery commands memorable (`--list-*` pattern) and include in `--help`.

### 8. Interactive Mode

For learning and exploration:

```bash
$ gen-image --interactive

Welcome to gen-image interactive mode!

What do you want to create?
1. Educational concept illustration
2. Mnemonic image for language learning
3. Visual diagram/flowchart
4. Custom prompt

Choice [1-4]: 1

Great! Let's create an educational illustration.

What concept are you explaining?
> Rust BufReader ownership semantics

What's the core metaphor or visual analogy?
> A librarian locking a book in a reading room safe

What emotion should the image convey?
(trust, excitement, caution, clarity, etc.)
> trust and safety

Primary color?
(red, blue, green, yellow, purple, or 'auto')
> blue

Any specific elements to include?
(comma-separated, or press enter to skip)
> librarian, book, safe, reading room, access card

Perfect! Here's the generated prompt:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Style: Educational cartoon with bright blue tones]

Create a memorable educational illustration showing Rust BufReader
ownership semantics. The visual metaphor is a librarian locking a
book in a reading room safe.

Include: librarian, book, safe, reading room, access card

The image should convey trust and safety. Use bright, vibrant colors
with blue as the dominant color. No text in the image. One surprising
element for memorability.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generate this image? [Y/n]: y

[Generating... ████████████████████████ 100%]

✅ Saved to: attachments/bufreader-ownership-1729468800.png

Wikilink: ![[bufreader-ownership-1729468800.png]]

Want to generate another? [y/N]: n
```

**Why interactive mode?**
- Lowers learning curve (new users)
- Teaches prompt structure (shows what makes a good prompt)
- Prevents blank-slate paralysis (guided questions)
- Refinement loop (easy to iterate)

**Tradeoff**: Interactive is slower than direct CLI. Resolution: Both modes coexist. Interactive for learning, CLI for speed.

## Technical Architecture

### Stack
- **Language**: Python 3.11+
- **Dependencies**:
  - `openai` - Official OpenAI SDK
  - `typer` - CLI framework (clean, typed)
  - `rich` - Terminal output (progress bars, formatting)
  - `pydantic` - Config validation
  - `httpx` - HTTP client (for image downloads)

### Project Structure
```
99-Python-Tools/gen-image/
├── pyproject.toml              # uv package config
├── README.md                   # User documentation
├── PRD.md                      # This file
├── IMPLEMENTATION_PLAN.md      # Staged implementation plan
├── src/
│   └── gen_image/
│       ├── __init__.py
│       ├── cli.py              # Typer CLI interface
│       ├── generator.py        # DALL-E API integration
│       ├── templates.py        # Template system
│       ├── styles.py           # Style preset definitions
│       ├── cost_tracker.py     # Cost logging and analysis
│       ├── vault.py            # Obsidian integration
│       └── config.py           # Configuration management
├── templates/                  # Built-in prompt templates
│   ├── educational-metaphor.txt
│   ├── mnemonic-vocab.txt
│   └── visual-comparison.txt
└── tests/
    ├── test_cli.py
    ├── test_generator.py
    └── test_templates.py
```

### Configuration File

`~/.config/gen-image/config.toml`:
```toml
[general]
vault_path = "/path/to/your/notes"
attachments_dir = "attachments"
default_style = "educational-cartoon"

[api]
provider = "openai"
model = "dall-e-3"
quality = "standard"
size = "1024x1024"

[costs]
budget_limit = null  # null = no limit
warn_at_percent = 80  # warn when 80% of budget used

[output]
auto_copy_wikilink = true  # copy to clipboard
naming_pattern = "{topic}-{timestamp}"
```

### Error Handling

**API Errors**:
```python
# Rate limit
if error.code == "rate_limit_exceeded":
    print("[yellow]⚠ Rate limit reached. Try again in 60 seconds.[/yellow]")

# Auth failure
if error.code == "invalid_api_key":
    print("[red]❌ Invalid OpenAI API key.[/red]")
    print("Set OPENAI_API_KEY environment variable")
    print("Get your key at: https://platform.openai.com/api-keys")

# Content policy
if error.code == "content_policy_violation":
    print("[red]❌ Prompt violates OpenAI content policy[/red]")
    print("Try rephrasing to avoid:")
    print("- Violence, harmful content")
    print("- Political/public figures")
    print("- Copyrighted characters")
```

**Network Errors**:
- Timeout: Retry with exponential backoff (max 3 attempts)
- Connection failure: Clear error message with troubleshooting steps

**Validation Errors**:
- Invalid file path: Check exists, writable
- Missing variables in template: List required vars
- Unknown style preset: List available presets

## Success Criteria

**V1 (MVP - Week 1)**:
- [ ] Generate image from inline prompt
- [ ] Save to specified output path
- [ ] Return wikilink format
- [ ] Educational-cartoon style preset works
- [ ] Cost estimate shown after generation
- [ ] Basic error handling

**V2 (Usable - Week 2)**:
- [ ] Auto-detect vault attachments folder
- [ ] All 3 style presets implemented
- [ ] Template system working
- [ ] Generation history logged
- [ ] Stats command shows cost tracking
- [ ] Dry-run mode

**V3 (Polished - Week 3)**:
- [ ] Interactive mode
- [ ] Budget limits and warnings
- [ ] Smart file naming (extract topic from prompt)
- [ ] Conflict resolution (don't overwrite)
- [ ] Auto-copy wikilink to clipboard
- [ ] Full test coverage

**V4 (Beautiful - Week 4)**:
- [ ] Rich terminal output (colors, progress bars)
- [ ] Helpful error messages with suggestions
- [ ] Comprehensive README with examples
- [ ] Built-in template refinement (show prompt preview)
- [ ] Config file support
- [ ] Shell completion (bash/zsh)

## Key Design Tradeoffs

### 1. MCP Server vs CLI Tool

**Decision**: CLI tool

**Why**:
- ✅ **Simpler to build**: No MCP protocol overhead
- ✅ **Easier to debug**: Standard CLI patterns
- ✅ **More flexible**: Works in any terminal, not just Claude
- ✅ **Better for automation**: Easy to script, integrate with other tools
- ❌ Requires leaving Claude Code to run command

**Alternative considered**: MCP server for in-editor generation
- Would enable Claude to generate images during conversation
- But adds complexity (protocol, server management)
- Use case doesn't require tight integration (async workflow is fine)

**Resolution**: Build CLI first. If tight integration becomes critical, wrap CLI in MCP server later.

### 2. Image Provider Lock-in

**Decision**: Start with DALL-E 3, design for future providers

**Why**:
- ✅ Best quality today
- ✅ Simple API
- ❌ Vendor lock-in
- ❌ Recurring costs

**Mitigation**:
- Abstract generation behind `Generator` interface
- Future: Add `StableDiffusionGenerator`, `LocalGenerator`
- Config: `provider = "openai" | "stable-diffusion" | "local"`

**When to add alternatives**:
- Cost becomes prohibitive (>$20/month)
- Quality requirements change
- Privacy concerns (local model needed)

### 3. Prompt Engineering: Presets vs Full Control

**Decision**: Opinionated presets as default, allow override

**Why**:
- ✅ **Consistency**: All educational images have same style
- ✅ **Better results**: Tested prompts work reliably
- ✅ **Faster workflow**: No need to specify style each time
- ❌ **Less flexibility**: Can't do everything

**Resolution**:
- 3 presets cover 90% of use cases
- `--style custom` + full prompt for remaining 10%
- Document when to use which preset

### 4. Cost Tracking: Automatic vs Opt-in

**Decision**: Automatic logging, opt-in budget limits

**Why**:
- ✅ **Zero config**: Works out of box
- ✅ **No surprises**: User sees costs
- ✅ **Privacy-respecting**: Local logs only
- ❌ **Storage overhead**: history.jsonl grows

**Mitigation**:
- Rotate logs monthly
- Provide `gen-image --clear-history` command
- Keep logs minimal (no full prompts by default)

### 5. Template Complexity: Simple vs Powerful

**Decision**: Simple variable substitution, not full templating engine

**Why**:
- ✅ **Learnable**: Anyone can write templates
- ✅ **Predictable**: No complex logic
- ✅ **Sufficient**: Covers actual use cases
- ❌ **Limited**: Can't do conditionals, loops

**Not needed for this use case**:
- Templates are for structure, not logic
- Complex prompts can use prompt files
- If needed later, upgrade to Jinja2

**Resolution**: Start simple. Add power features only if proven necessary.

## Non-Goals (What This Is NOT)

1. **Not an image editor** - Generates images, doesn't edit them (use separate tools)
2. **Not a DAM system** - Doesn't organize/tag existing images (Obsidian handles that)
3. **Not a batch processor** - Optimized for single image generation, not bulk operations
4. **Not a prompt tuner** - No automatic prompt optimization (user iterates manually)
5. **Not a social sharing tool** - No upload to imgur, Twitter, etc.

## Future Considerations (Post-V4)

**Potential enhancements** (only if proven valuable):
- Prompt history with regenerate option
- Visual diff between prompt iterations
- Local model support (Stable Diffusion)
- Batch generation from CSV
- Integration with existing mnemonic-image workflow
- Claude Code MCP wrapper
- Web UI for non-CLI users

**Current stance**: Ship V4 first. Let real usage inform priorities.

## Success Metrics

How we'll know this works:

1. **Adoption**: Used at least 5x/week in note-writing
2. **Quality**: 80%+ of generated images kept (not regenerated)
3. **Speed**: <30s from idea to image in note (including thinking time)
4. **Cost**: <$10/month for typical usage
5. **Satisfaction**: User prefers this workflow over alternatives

## Timeline

**Week 1**: V1 MVP (inline prompts, basic generation)
**Week 2**: V2 Usable (templates, cost tracking, vault integration)
**Week 3**: V3 Polished (interactive mode, smart naming)
**Week 4**: V4 Beautiful (rich output, error handling, docs)

**Total**: 4 weeks to production-ready V4

## Open Questions for User

Before implementation, clarify:

1. **Attachments folder**: Where should images be saved by default?
   - Option A: Vault root `/attachments/`
   - Option B: Per-note folder (like Obsidian's default)
   - Option C: Configurable per-generation

2. **Cost budget**: What's acceptable monthly spend?
   - Light usage: <$5/month (~100 images)
   - Medium usage: $5-20/month (~100-500 images)
   - Heavy usage: >$20/month

3. **Style preference**: Which style is most important for V1?
   - Educational-cartoon (for technical notes)
   - Mnemonic (for language learning)
   - Diagram-alternative (for systems/processes)

4. **Interactive mode priority**: Essential for V1 or nice-to-have for V3?

---

## Appendix: Example Generations

### Example 1: Educational Concept

**Prompt**:
```bash
gen-image --style educational-cartoon \
  "A friendly cartoon librarian with a warm smile is carefully locking a \
  large book into a secure safe inside a cozy reading room. The librarian \
  holds an access card labeled 'BufReader'. The safe is transparent showing \
  the book safely stored inside. The reading room has a comfortable desk with \
  a notepad (internal buffer). Bright blue and green color scheme, simple \
  composition, no text in image." \
  --output bufreader-ownership.png
```

**Expected result**: Clear visual metaphor for ownership transfer, memorable and instructive

### Example 2: Mnemonic

**Prompt**:
```bash
gen-image --template mnemonic \
  --var word="語りかける" \
  --var concept="Someone's words (語) transforming into colorful birds \
    that fly toward (かける) another person's ear, representing 'to address/speak to'" \
  --output katari.png
```

**Expected result**: Absurd but memorable visual pun connecting sound to meaning

### Example 3: Diagram Alternative

**Prompt**:
```bash
gen-image --style diagram-alternative \
  "A cross-section view of a multi-story building showing memory layout. \
  Ground floor: Stack frame with BufReader struct. Second floor: Heap with \
  Vec<u8> buffer array. Arrows showing ownership relationships. Color-coded: \
  stack (blue), heap (yellow), file descriptor (red). Simple architectural \
  drawing style." \
  --size 1792x1024 \
  --output memory-layout.png
```

**Expected result**: Clear spatial representation of memory structure

---

**This PRD represents V5 thinking**:
- **Intentional**: Every choice explained
- **Coherent**: All pieces fit together
- **Polished**: Edge cases handled
- **Necessary**: No gold-plating, essential features only
- **Effortless**: Looks simple, hides complexity
