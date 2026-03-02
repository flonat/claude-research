# Project Documentation Conventions

> Shared conventions for outward-facing documentation: project READMEs, user manuals, architecture docs, deploy guides, and in-app help. Ensures consistency across Topic Finder, council packages, and future projects.
>
> Companion to `system-documentation.md` (which covers internal Task Management docs like CLAUDE.md, SKILL.md, and component catalogues).

---

## Governed Documents

Every document governed by these conventions carries a tag on its first line:

- **Markdown:** `<!-- Governed by: skills/shared/project-documentation.md -->`
- **LaTeX:** `% Governed by: skills/shared/project-documentation.md`

### Registry

| Project | File | Type |
|---------|------|------|
| Topic Finder | `README.md` | README |
| Topic Finder | `docs/user-manual.md` | User manual |
| Topic Finder | `docs/architecture.md` | Architecture |
| Topic Finder | `deploy/README.md` | Deploy guide |
| Topic Finder | `docs/user-manual.tex` | LaTeX manual |
| Topic Finder | `docs/topic-finder-overview/topic-finder-overview.tex` | Beamer deck |
| Task Management | `docs/user-manual/user-manual.tex` | LaTeX manual |
| Task Management | `docs/setup-overview/setup-overview.tex` | Beamer deck |
| Task Management | `docs/setup-overview/setup-overview-public.tex` | Beamer deck (public) |
| Task Management | `public/public-repo/README.md` | README (public) |
| Task Management | `public/public-repo/docs/getting-started.md` | Getting started |
| Task Management | `public/public-repo/docs/council-mode.md` | Feature guide |
| Task Management | `public/public-repo/docs/biblio-setup.md` | Setup guide |
| Task Management | `public/public-repo/docs/notion-setup.md` | Setup guide |

### Tagging Protocol

When **creating** new outward-facing documentation (README, user manual, architecture doc, deploy guide, Beamer deck, or LaTeX manual):

1. Add the appropriate tag as the very first line of the file
2. Add the file to the registry table above

When **auditing** a project's documentation (via `/sync-topic-finder-doc`, `/update-project-doc`, or manually):

1. Grep for `Governed by: skills/shared/project-documentation.md` across all `.md` and `.tex` files
2. Flag any outward-facing docs that lack the tag — these are candidates for tagging
3. Do not tag internal docs (CLAUDE.md, SKILL.md, `.context/` files, `log/` files, `docs/skills.md`, etc.) — those are governed by `system-documentation.md`

---

## The Documentation Suite

Every software project should have a README. Larger projects add docs as they grow. This table defines what each file covers and when to create it.

| Document | Create when | Audience | Covers |
|----------|------------|----------|--------|
| `README.md` | Always | Everyone | What it does, quick start, project structure |
| `docs/user-manual.md` | Web UI or CLI with 3+ workflows | End users | Every feature, step-by-step, with examples |
| `docs/architecture.md` | 5+ source files or non-obvious design | Maintainers | Service layers, data flow, design patterns |
| `deploy/README.md` | Remote deployment exists | DevOps / self | Infrastructure, secrets, CI/CD |
| In-app help (`/help` + tips) | Web UI exists | End users | Same content as user manual, rendered in-app |

**Principle:** Each document serves a distinct audience. If two docs say the same thing, one should be a pointer to the other.

---

## README.md

The README is the front door. It answers: *What is this? How do I run it? Where do I go for more?*

### Required Sections (in order)

```markdown
# Project Name

Brief description (1-3 sentences). What it does and who it's for.

**Live:** [url](url) (if hosted)

## What It Does

Feature summary — 3-6 bullet points or short subsections.
Each feature: one sentence of what + one sentence of how.

## Architecture

ASCII diagram showing the high-level data flow.
Keep to one diagram. Label external services and data stores.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend   | FastAPI + Python 3.13 |
| Frontend  | Jinja2 + HTMX + Tailwind |
| ...       | ... |

## Local Development

### Prerequisites
- Bullet list of required tools with version constraints

### Setup
```bash
# Numbered steps, copy-pasteable
uv venv
uv pip install -e ".[dev]"
cp .env.example .env
```

### CLI Usage (if applicable)
Concrete examples with real arguments:
```bash
tool-name subcommand "real example argument"
tool-name subcommand "another example" --flag value
```

## Documentation

| Document | What it covers |
|----------|---------------|
| [`docs/user-manual.md`](docs/user-manual.md) | Full user guide |
| [`docs/architecture.md`](docs/architecture.md) | Technical internals |
| ... | ... |

## Project Structure

Annotated file tree — comments explain non-obvious entries.

## Related Repos (if applicable)

| Repo | What it does |
|------|-------------|
| [org/repo](url) | One-line description |
```

### Shared Flags Table

When the CLI has flags shared across subcommands, document them once in a table after the examples:

```markdown
| Flag | Description |
|------|-------------|
| `--source`, `-s` | Data source: `openalex`, `scopus`, `wos`, or `multi` |
| `--model`, `-m` | LLM model in OpenRouter format |
| `--output`, `-o` | Save output to a file |
```

---

## User Manual

The user manual is the comprehensive how-to guide. It answers: *How do I use each feature? What do the results mean?*

### Structure

```markdown
# Project Name — User Manual

Description of the app and its two interfaces (web + CLI).

## Overview

What the tool does in 2-3 paragraphs. Include a workflow diagram
showing how the features connect.

## Getting Started

### Hosted Version
URL + auth info.

### Local Version
Brief setup (pointer to README for full instructions).

## [Workflow Sections]

One `##` section per major workflow or feature group.
Within each, use `###` for individual workflows numbered sequentially:

### 1. Feature Name

**Purpose:** One sentence.

**How to use:**
1. Step-by-step instructions
2. With concrete examples
3. And expected outcomes

**What you get:**
Description of the output, with field explanations.

**CLI equivalent:**
```bash
tool-name subcommand "example"
```

## [Configuration / Settings Sections]

### Environment Variables

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `OPENROUTER_API_KEY` | LLM access via OpenRouter | Yes | — |
| `SCOPUS_API_KEY` | Scopus bibliometric data | No | — |

### [Other config topics]

## Limitations and Caveats
## Costs (if API-based)
```

### Per-Workflow Pattern

Every workflow section follows the same internal structure:

1. **URL** — the route path (web apps only): `**URL:** /discover`
2. **Purpose** — one sentence
3. **How to use** — numbered steps (typically 3-5)
4. **What you get** — bullet list with **bold** key outputs and inline descriptions
5. **CLI equivalent** — command example
6. **Behind the scenes** (optional) — what happens technically
7. **Tips** (optional) — power-user advice

This consistency lets users learn the pattern once and apply it to every workflow.

### Limitations and Caveats

Include a numbered list of honest constraints. Each item: **bold limitation** followed by explanation in the same paragraph.

```markdown
## Limitations and Caveats

1. **LLM outputs are advisory** — always verify suggestions against primary literature.
2. **Bibliometric coverage varies by source** — OpenAlex has broader coverage but less metadata than Scopus.
```

Target 4-8 items. Cover: accuracy caveats, coverage gaps, cost implications, known failure modes.

### Workflow Diagram

Place a single ASCII diagram early in the manual showing how workflows connect:

```
Discovery ──→ Novelty ──→ Suggest ──→ Framing
                  │
                  └──→ Acceptance ──→ Refinement
```

Use `──→` for forward flow, `│` and `└──→` for branches. Label each node with the workflow name only (no descriptions in the diagram).

---

## Architecture Doc

The architecture doc is the technical reference for maintainers. It answers: *How does this work internally? Where do I look to change X?*

### Structure

```markdown
# Project Name — Architecture

> Technical reference for maintainers. For usage, see the [user manual](user-manual.md).

## System Overview

ASCII diagram: end-to-end data flow from user input to output.
Show external services, internal layers, and data stores.

## [Layer Sections]

One `##` per architectural layer (e.g., Service Layer, LLM Service,
Database, Web Layer). Within each:

### Interface / ABC

Table of methods:
| Method | Returns | Purpose |
|--------|---------|---------|

### Implementations

Description of each concrete implementation.

### Design Pattern

Name the pattern (Adapter, Decorator, Composite, etc.)
and explain why it was chosen.

## Data Flow

Per-workflow sequence showing which services are called:
1. User submits form
2. Route handler extracts parameters
3. Orchestrator calls data source
4. ...

## Configuration

### Environment Variables

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|

### Settings Class

Reference to config file, list of fields.

## Deployment

Brief pointer to deploy guide. Include the Dockerfile stage
summary if it helps understanding.

## Design Patterns

Summary table:
| Pattern | Where | Why |
|---------|-------|-----|
| Adapter | services/ | Normalize 3 different APIs |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
```

### Class and Method References

When referencing code, use backtick-quoted names that match the source exactly:

- Classes: `` `TopicFinderOrchestrator` ``
- Methods: `` `discover_topics()` ``
- Files: `` `services/llm.py` ``

These references should be validated automatically (see `validate_docs.py` pattern).

---

## Deploy Guide

The deploy guide covers infrastructure. It answers: *How do I deploy this? What secrets do I need?*

### Structure

```markdown
# Deployment Guide

## Architecture Overview

ASCII diagram showing deployment topology:
user → CDN/proxy → compute → database.

## [Platform Section] (e.g., Fly.io, Railway, AWS)

### Configuration
Relevant config files (fly.toml, docker-compose.yml, etc.)
Use a Setting | Value | Why table for config file options.

### Secrets
| Secret | Where to set | Purpose |
|--------|-------------|---------|

### CI/CD
Pipeline description with trigger conditions.

## Docker
Dockerfile stage breakdown (if multi-stage).

## Secrets Reference
Single comprehensive table of all secrets across all services.

## Monitoring & Errors
Sentry, logging, health checks.

## Troubleshooting
Common issues with symptoms and fixes.
```

### Section Ordering

Follow this progression: high-level architecture → concrete setup → infrastructure details → troubleshooting.

1. Architecture Overview (ASCII diagram)
2. What Gets Deployed (components table)
3. Live URLs
4. Platform Setup (prerequisites, first-time, commands)
5. CI/CD Pipeline
6. Docker Configuration
7. Secrets Reference (single comprehensive table)
8. External Services (DNS, CDN, auth)
9. Monitoring
10. Troubleshooting

---

## In-App Help System

When a project has a web UI, the user manual should be accessible directly within the app.

### Architecture

```
docs/user-manual.md  ──→  help_content.py  ──→  /help page (full manual)
                                │
                                └──→  WORKFLOW_TIPS  ──→  contextual tips (per page)
```

**Single source of truth:** The `/help` page loads `user-manual.md` at runtime and renders it as HTML. No content duplication — edit the markdown, the web page updates.

### Full Help Page

- Render the full user manual as HTML with a sticky TOC sidebar
- TOC built from `##` and `###` headings
- Anchor IDs derived from heading slugs (lowercase, strip non-alphanumeric, hyphens for spaces)
- Add a "Help" link to the main navigation bar

### Contextual Workflow Tips

Each workflow page gets a collapsible tip with:
- **Title:** "How to use [Workflow Name]"
- **Tip text:** 2-3 sentences explaining what to do and what to expect
- **Link:** "Full documentation →" pointing to `/help#section-slug`

Tips are defined in a `WORKFLOW_TIPS` dict keyed by workflow name, with `title`, `tip`, and `section` (the slug).

### Keeping It In Sync

Section slugs in `WORKFLOW_TIPS` must match actual heading slugs in `user-manual.md`. Validate this automatically:
- CI script checks slug integrity on every push
- `/sync-topic-finder-doc` checks during manual audits

---

## ASCII Diagrams

### Direction Conventions

| Flow type | Direction | Example |
|-----------|-----------|---------|
| Data/request flow | Left-to-right | `User ──→ API ──→ DB` |
| Stage progression | Top-to-bottom | Stage 1 → Stage 2 → Stage 3 |
| Architecture layers | Top-to-bottom | Frontend → Backend → Database |
| Workflow chains | Left-to-right with branches | `A ──→ B ──→ C` with `└──→ D` |

### Symbol Legend

```
──→     directional flow
│       vertical connection
├──     branch (continuing)
└──     branch (terminal)
┌─┐     box corners (for containers)
▼ ▲     vertical arrows
```

### Labelling

- Label every box with its service/component name
- Label arrows only when the relationship isn't obvious (e.g., "OAuth", "REST API")
- Add parenthetical notes for data stores: `SQLite (results + cache)`
- Keep diagrams under 15 lines — split into multiple diagrams if needed

---

## Environment Variable Documentation

Use this table format everywhere env vars are documented:

```markdown
| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `OPENROUTER_API_KEY` | LLM access via OpenRouter | Yes | — |
| `OPENALEX_API_KEY` | OpenAlex bibliometric data | Yes | — |
| `SCOPUS_API_KEY` | Scopus search (optional) | No | — |
| `SCOPUS_INST_TOKEN` | Scopus institutional token | No | — |
| `WOS_API_KEY` | Web of Science search | No | — |
| `WOS_API_TIER` | WoS API tier (`starter`/`expanded`) | No | `starter` |
```

**Rules:**
- Required column: "Yes" or "No" — never blank
- Default column: the actual default value, or "—" if none
- Group by service (API keys together, app config together)
- In READMEs, show env vars inside bash code blocks with comments. In reference docs, use the table.
- `.env.example` must include every variable with a comment

---

## Library/Package READMEs

For standalone packages (llm-council, cli-council), the README serves as the API reference.

### Structure

```markdown
# Package Name

One-line description of what the package does.

## How It Works / The Protocol

Diagram or numbered steps showing the core algorithm.

## Installation

```bash
pip install package-name
```

## Quick Start

Minimal working example — the fewest lines to get a result:
```python
from package import Client
result = await Client().run("input")
print(result.summary)
```

## Usage

### CLI
```bash
python -m package "input" --flag value
```

### Python API
Longer example with configuration options.

## Configuration

Prerequisites table (for CLI tools):
| Backend | Install | Auth |
|---------|---------|------|

Or env var table (for API-based packages).

## Output

Describe the return type and its key fields.

## [Additional Sections]
```

### Code Examples

- Use **real arguments** in examples, not placeholders (`"human-AI collaboration"` not `"your topic here"`)
- Show the **import path** explicitly — never assume the reader knows the package structure
- Include the **return type** and how to access key fields
- For CLI tools, show **progressive complexity**: simplest invocation first, then flags

### CLI Example Conventions

- **No `$` prefix** — commands shown as-is, not prefixed with `$` or `>`
- **Language tag required** — always use ` ```bash ` for shell commands
- **Output on separate lines** — if showing output, separate from the command with a blank line or comment
- **Flags after arguments** — `tool-name subcommand "query" --flag value`
- **Quotes for multi-word arguments** — `"human-AI collaboration"` not `human-AI collaboration`
- **Shared flags in a table** — when multiple subcommands share flags, document them once in a separate table rather than repeating per-command

---

## Tone by Audience

| Audience | Tone | Patterns |
|----------|------|----------|
| End users (user manual) | Approachable, instructional | "You can...", "Enter your...", "Results include..." |
| Developers (README) | Crisp, feature-focused | Active verbs: "Get", "Fetch", "Run", "Configure" |
| Maintainers (architecture) | Technical, precise | Third person: "The orchestrator wires...", "Requests flow through..." |
| Adopters (public repo) | Welcoming, honest | "Built for...", explicit audience statement |

---

## LaTeX Documentation

When a document exists in both markdown and LaTeX (e.g., user manual in `.md` and `.tex`), the markdown is the source of truth for content. The LaTeX version adds typographic polish.

### Standard Preamble (Article Style)

```latex
\documentclass[11pt,a4paper]{article}

\usepackage{geometry}       % Margins (2.5cm all sides)
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}        % Modern serif font (not Computer Modern)
\usepackage{microtype}      % Typographic refinement
\usepackage{parskip}        % Paragraph spacing, no indents
\usepackage{hyperref}       % Clickable links
\usepackage{xcolor}         % Custom colours
\usepackage{booktabs}       % Professional tables (\toprule, \midrule, \bottomrule)
\usepackage{longtable}      % Multi-page tables
\usepackage{enumitem}       % List customisation
\usepackage{listings}       % Code blocks
\usepackage[skins,breakable]{tcolorbox}  % Callout boxes
\usepackage{tikz}           % Diagrams
```

### Custom Commands

Define these reusable commands in the preamble for consistency:

```latex
\newcommand{\code}[1]{\texttt{\small #1}}           % Inline code
\newcommand{\filepath}[1]{\texttt{\small #1}}        % File paths
\newcommand{\skill}[1]{\texttt{/#1}}                 % Skill references
\newcommand{\hook}[1]{\texttt{#1}}                   % Hook references
\newcommand{\keyterm}[1]{\textbf{#1}}                % Key terminology
```

### Colour Palette for Callout Boxes

```latex
\definecolor{accentgreen}{HTML}{059669}   % Tip boxes
\definecolor{accentamber}{HTML}{D97706}   % Warning boxes
\definecolor{accentred}{HTML}{DC2626}     % Error/critical boxes
\definecolor{codebg}{HTML}{F3F4F6}        % Code background
\definecolor{codeframe}{HTML}{D1D5DB}     % Code border

\newtcolorbox{tipbox}[1][]{
    colback=accentgreen!5, colframe=accentgreen!60,
    fonttitle=\bfseries, title={#1}, sharp corners, boxrule=0.5pt}
\newtcolorbox{warnbox}[1][]{
    colback=accentamber!5, colframe=accentamber!60,
    fonttitle=\bfseries, title={#1}, sharp corners, boxrule=0.5pt}
```

### Table Formatting

- Use `booktabs` rules: `\toprule`, `\midrule`, `\bottomrule` — never vertical lines
- Column spec: `@{}lp{7cm}@{}` (remove outer padding, left column, paragraph column)
- Multi-page tables: `\begin{longtable}` with `\endhead` for repeating headers
- Always `\centering` within table environments

### md/tex Parity

When both formats exist, structural parity is required: every `##` heading in the markdown should have a corresponding `\section{}` in LaTeX. Content can differ slightly (LaTeX adds figures, better formatting), but the section structure must match. Validate with `validate_docs.py` check 2.

---

## Beamer Presentation Docs

Projects may include Beamer decks in `docs/` (e.g., `docs/topic-finder-overview/`, `docs/setup-overview/`). These are outward-facing documentation, not just slides.

### Standard Setup

```latex
\documentclass[aspectratio=169,11pt]{beamer}
\setbeamertemplate{navigation symbols}{}     % No nav clutter
\setbeamertemplate{footline}[frame number]   % Frame numbers only
```

- **Aspect ratio:** Always 16:9 (`aspectratio=169`)
- **Navigation symbols:** Disabled
- **Footline:** Frame number only (or custom three-part: author | title | X/Y)

### Colour Palette

Define a cohesive palette of 5-8 colours in the preamble. Established palette:

| Colour | Hex | Use |
|--------|-----|-----|
| `Midnight` | `1A1A2E` | Dark backgrounds, body text |
| `DeepBlue` | `16213E` | Frame title backgrounds |
| `RoyalBlue` | `0F3460` | Structure, bullet markers |
| `Coral` | `E94560` | Alerts, emphasis |
| `CloudWhite` | `FAFBFC` | Main background |
| `SoftGray` | `BDC3C7` | Subtitles, subdued text |
| `LightBlue` | `D6EAF8` | TikZ box fills |
| `SlateGray` | `5D6D7E` | Arrows, secondary elements |

### Frame Title Conventions

- Use **substantive claims**, not labels: "62 skills cover the full research lifecycle" not "Skills Overview"
- Optional subtitle for framing questions: "Every new AI session starts from zero"
- Keep titles to one line

### TikZ Diagram Styling

```latex
\begin{tikzpicture}[
    node distance=0.6cm and 0.8cm,
    box/.style={draw=SlateGray, rounded corners=3pt,
                minimum width=2.0cm, minimum height=0.75cm,
                align=center, fill=#1, text=Midnight},
    box/.default={LightBlue},
    arr/.style={-{Stealth[length=2mm]}, thick, color=SlateGray},
]
```

- Rounded corners (3pt), minimum dimensions, centred text
- Colour-code by component type (e.g., `Coral!20` for interfaces, `CloudWhite` for core, `SoftGray!30` for external)
- Stealth arrowheads, thick strokes

### Code Blocks in Beamer

Use small monospace fonts — slides need compact code:

```latex
\begin{lstlisting}[language={}, basicstyle=\ttfamily\fontsize{6.5}{8}\selectfont]
```

### Bullet Styles

- Level 1: `\tiny$\blacksquare$` in primary colour (filled square)
- Level 2: `\scriptsize$\blacktriangleright$` in secondary colour (right triangle)
- Enumerate: `\insertenumlabel.` in primary colour

---

## Public/Anonymized Variants

When a document has both private and public versions (e.g., `setup-overview.tex` and `setup-overview-public.tex`), follow these conventions.

### What to Anonymize

| Private | Public replacement |
|---------|-------------------|
| Author name | Generic descriptor ("PhD researcher") or GitHub handle |
| Institution names | Remove entirely |
| Exact component counts | Remove or genericize ("30+", "Skills" without number) |
| Specific project names | "Multiple active research projects" |
| Notion references | "Task manager" (generic) |
| Date in `\date{}` | GitHub URL or "Open-source" descriptor |

### Sync Markers

For auto-generated or synced content in public markdown files, use HTML comment markers:

```markdown
<!-- MARKER-NAME:START -->
<!-- auto-generated by script-name.py — do not edit manually -->
[content here]
<!-- MARKER-NAME:END -->
```

- Marker names: UPPERCASE-HYPHENATED (`COMPONENT-TABLE`, `SKILLS-SUMMARY`, `FILE-TREE`)
- Attribution line after START: `auto-generated by ...` or `synced from private ...`
- Warning: `do not edit manually`

### Private LaTeX Headers

```latex
% ============================================================
% Document Title — Description
% Author · Month Year
% ============================================================
```

### Public LaTeX Headers

```latex
% ============================================================
% Document Title — Public Version (Format)
% Generated during sync — DO NOT EDIT MANUALLY
% Edit source-file.tex and re-run sync-script.sh
% ============================================================
```

---

## Automated Validation

Projects with documentation in multiple formats or locations should include a validation script that catches drift automatically.

### The `validate_docs.py` Pattern

- **Stdlib-only** — no venv needed, runs anywhere Python is installed
- **Location:** `scripts/validate_docs.py` in the project root
- **Severity levels:** FAIL (blocks CI) and WARN (informational, `--strict` promotes to FAIL)
- **Flags:** `--strict` (treat warnings as failures), `--check N` (run only check N)
- **Paths:** All resolved relative to script location — no hardcoded absolute paths
- **CI integration:** Run before tests in the CI pipeline

### Common Checks

| Check | Severity | What it catches |
|-------|----------|----------------|
| Help slug integrity | FAIL | WORKFLOW_TIPS slugs that don't match user-manual headings |
| md/tex section parity | WARN | Structural divergence between markdown and LaTeX versions |
| File path references | FAIL | Backtick-quoted paths in docs that don't exist on disk |
| Class/method references | FAIL | Code references in architecture docs that don't match source |
| Count accuracy | WARN | Claimed counts vs actual (data sources, templates, etc.) |
| Env var completeness | WARN | Settings fields missing from documentation |

---

## Checklist for New Project Documentation

Before shipping any project documentation:

1. **README exists** with all required sections
2. **Live URL** linked prominently if hosted
3. **ASCII diagram** shows end-to-end flow
4. **Tech stack table** lists every major dependency
5. **Setup is copy-pasteable** — tested from a clean state
6. **CLI examples use real arguments** — no `$` prefix, no placeholders
7. **Env vars documented** in consistent table format
8. **File tree annotated** — comments explain non-obvious entries
9. **Pointer table** links to detailed docs (user manual, architecture, deploy)
10. **User manual** follows per-workflow pattern (URL → purpose → how to use → what you get)
11. **Limitations section** with honest caveats (numbered, bold constraint + explanation)
12. **In-app help** loads user manual at runtime (no content duplication)
13. **LaTeX versions** use standard preamble, custom commands, booktabs tables
14. **md/tex parity** — section structure matches between formats
15. **Beamer decks** use 16:9, consistent colour palette, substantive frame titles
16. **Public variants** anonymized (no names, no exact counts, sync markers for auto-generated content)
17. **Validation script** checks for drift between docs and code
