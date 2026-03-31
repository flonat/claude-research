# Project Documentation — Content Conventions

> Conventions for README, user manual, architecture, deploy guide, and in-app help content.
> Split from [`project-documentation.md`](project-documentation.md) for leanness.

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

- Classes: `` `ScoutOrchestrator` ``
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
- `/sync-repo scout` checks during manual audits

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
