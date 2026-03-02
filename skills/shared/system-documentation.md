# System Documentation Conventions

> Formatting, structure, and style conventions for Task Management infrastructure documentation: CLAUDE.md, SKILL.md, rules, component catalogues (`docs/`), and shared resources.
>
> Companion to `project-documentation.md` (which covers outward-facing docs like READMEs, user manuals, and architecture references).

## Document Types and Purposes

| Document | Audience | Purpose | Tone |
|----------|----------|---------|------|
| `CLAUDE.md` | Claude (AI) | Session instructions — what to do and how | Imperative, terse |
| `README.md` | Human developers | Project overview, quick start, navigation | Friendly, scannable |
| `SKILL.md` | Claude (AI) | Step-by-step workflow protocol | Imperative, procedural |
| `docs/*.md` | Human + AI | Detailed reference material | Neutral, thorough |
| `user-manual.md` | End users | Feature docs, how-to guides | Approachable, example-driven |
| `architecture.md` | Maintainers | Technical internals, data flow, design decisions | Precise, factual |

---

## Markdown Formatting

### Header Hierarchy

```markdown
# Document Title        ← one per file, matches the file's purpose
## Major Section        ← top-level topic divisions
### Subsection          ← details within a section
#### Rarely deeper      ← only for deeply nested reference material
```

Never skip levels (e.g., `#` → `###`). Use `##` as the primary structural unit — most navigation (TOCs, anchors, `/help` slugs) keys off `##` headings.

### Opening Context Block

Every document starts with a title, then a blockquote summarising what the file is and who it's for:

```markdown
# Document Title

> One-liner explaining what this document covers and when to read it.
```

For reference files shared across skills, add a second line noting which skills consume it:

```markdown
> Shared reference for `/skill-a`, `/skill-b`, and `/skill-c`.
```

### Tables

Use tables for structured reference material — indices, mappings, rubrics, configuration:

```markdown
| Column A | Column B | Column C |
|----------|----------|----------|
| value    | value    | value    |
```

- Left-align text columns, right-align numeric columns
- Bold header-row values only when the table is a rubric or decision matrix
- Prefer tables over bullet lists when items have 2+ parallel attributes
- Keep cell content concise — one line per cell, no paragraphs inside cells

### Code Blocks

Always use fenced code blocks with language tags:

````markdown
```python
def example():
    pass
```

```bash
uv run python script.py
```

```latex
\section{Introduction}
```

```yaml
name: skill-name
description: "What it does"
```
````

For inline code: use backticks for file names (`` `config.py` ``), class names (`` `Settings` ``), method names (`` `discover_topics()` ``), env vars (`` `OPENROUTER_API_KEY` ``), and CLI commands (`` `uv run python` ``).

### Lists

- **Numbered lists** for sequential steps (protocols, workflows, order of operations)
- **Bullet lists** for non-sequential items (features, alternatives, notes)
- **Nested bullets** for elaboration — one level deep only; if deeper nesting is needed, restructure as a subsection
- **Checklists** (`- [ ]`) only in plans and session logs, never in reference docs

### Cross-References

```markdown
Full details: [`docs/architecture.md`](docs/architecture.md)
See [`references/drift-checks.md`](references/drift-checks.md)
```

Always use relative paths. Always include both the display text (the file name) and the link. For skills, use the forward-slash notation: `/skill-name`.

### Horizontal Rules

Use `---` to separate major conceptual blocks within a section. Do not use between every subsection — only between distinct topics or phases.

---

## Document Structure Patterns

### CLAUDE.md (AI Context File)

```markdown
# Claude Context for [Project Name]

> One-liner about the project.

## [Safety/Protection Rules]     ← always first if present
## File Structure                ← compact tree, annotated
## Conventions                   ← project-specific rules
## [Domain-Specific Sections]    ← what Claude needs to know
## Session Continuity            ← pointers to .context/, log/
```

**Key constraints:**
- **Max 200 lines.** Extract anything longer than 15 lines of reference material to `docs/` with a one-line pointer (see `lean-claude-md` rule).
- **Instructions, not knowledge.** CLAUDE.md tells Claude what to do and where to look — it doesn't store the knowledge itself.
- **Pointer pattern:** `Full guidelines: [\`docs/file.md\`](docs/file.md)`

### README.md (Human Overview)

```markdown
# Project Name

Brief description (1-3 sentences).

## What It Does / Overview       ← the "why" and "what"
## Getting Started / Setup       ← quick start for new users
## Project Structure             ← compact file tree
## Documentation                 ← links to docs/ files
## [Key Sections]                ← project-specific
```

**Key constraints:**
- **Max 150 lines** for most projects (300 for the Task Management root).
- Overlap with `user-manual.md` or `docs/` should be a summary + link, not duplication.
- Quick start instructions must be copy-pasteable.

### SKILL.md (Workflow Protocol)

```yaml
---
name: skill-name
description: "One-line description of what the skill does."
allowed-tools: Read, Edit, Write, Glob, Grep, Bash(pattern*), AskUserQuestion
argument-hint: <topic> [--flag]
---
```

```markdown
# Skill Title

> Audit sentence explaining what this skill does and when to use it.

## When to Use
## When NOT to Use
## Protocol                      ← numbered steps
### Step 1: [Action]
### Step 2: [Action]
## [Reference Tables]
## Cross-References              ← links to related skills
```

**Key constraints:**
- **Max 300 lines.** Extract long reference tables, rubrics, or examples to `references/` with a pointer.
- Steps are imperative: "Read the file", "Compare against", "Flag mismatches".
- Include a `When NOT to Use` section to prevent misapplication.

### Docs Files (Reference Material)

No strict template — structure follows the content. But follow these conventions:

- Start with `# Title` + blockquote context
- Use `##` sections as the main structural unit
- Include a navigation aid for long files (table of contents or section index at the top)
- Architecture docs should include ASCII diagrams for data flow and system overview
- API/configuration docs should use tables for parameter lists

### Component Catalogues (`docs/skills.md`, `docs/hooks.md`, etc.)

The Task Management `docs/` folder uses a consistent pattern for documenting collections of infrastructure components (skills, hooks, agents, rules, resources, scripts).

```markdown
# Component Type (plural)

> {count} {component type} + one-sentence description of what they are.

Brief intro paragraph: what the component is, where it lives, how it's configured.

## Overview

| Component | Category | Description |
|-----------|----------|-------------|
| `name`    | ...      | ...         |

---

## Component Details

### 1. Component Name (optional metadata)

What it does, when it applies, and how it works.
```

**Conventions:**
- **Count in blockquote:** Every catalogue opens with the actual count. This count must match reality — `/sync-private-doc` propagates count changes across files.
- **Overview table first:** A compact table listing every item before any details. Columns vary by component type (see below).
- **Numbered detail sections:** Each component gets a `###` subsection.
- **Cross-file count consistency:** Counts appear in CLAUDE.md, README.md, `docs/system.md`, and the catalogue file. All must agree.

**Catalogue-specific columns:**

| Catalogue | Required columns |
|-----------|-----------------|
| Skills (`docs/skills.md`) | Skill, Category, Description |
| Hooks (`docs/hooks.md`) | Hook, Event, Matcher, Script, What it does |
| Agents (`docs/agents.md`) | Agent, Purpose |
| Rules (`docs/rules.md`) | Rule, File, What it does |
| Resources (`docs/resources.md`) | Category, Author, Repo, What it provides |

### System Overview (`docs/system.md`)

Not a component catalogue but an architectural overview of the entire Task Management system. Uses:

- ASCII diagram showing the full system layout
- Numbered `##` sections for each major subsystem (context library, skills, hooks, etc.)
- Component count references that stay in sync with the individual catalogues
- File structure table mapping paths to purposes

---

## Writing Conventions

### Voice and Tone

| Context | Voice | Example |
|---------|-------|---------|
| CLAUDE.md, SKILL.md, rules | Imperative | "Read the config file. Compare against the source." |
| README.md, user-manual | Second person | "You can configure the model with `--model`." |
| Architecture docs | Third person, present tense | "The orchestrator wires the data source to the LLM service." |
| Session logs | Past tense, first person plural | "We implemented the validation script." |

### Conciseness

- Lead with the information, not the setup. Not "It should be noted that X" — just "X".
- One idea per paragraph. If a paragraph covers two distinct points, split it.
- Prefer tables over prose for structured information (3+ items with parallel attributes).
- Delete filler: "basically", "simply", "just", "in order to", "it is important to note that".

### Terminology

Use these terms consistently across all documentation:

| Term | Meaning | Not |
|------|---------|-----|
| Skill | Reusable workflow definition in `skills/` | "command", "script", "macro" |
| Agent | Independent Claude instance with fresh context | "sub-agent", "worker" |
| Hook | Automated script triggered by Claude Code events | "trigger", "listener" |
| Rule | Behavioural constraint, auto-loaded every session | "policy", "guideline" |
| Resource | Cloned external repo in `resources/` | "dependency", "library" |
| Workflow | A sequence of steps within a skill | "process", "pipeline" (unless actually a data pipeline) |
| Drift | Documentation claiming something that code no longer supports | "stale", "outdated" (less precise) |

### Numbers and Counts

- Spell out numbers one through nine in prose; use digits for 10+.
- Always verify counts by listing actual files — never trust cached numbers in docs.
- When a count appears in multiple files, update all of them (or use `/sync-private-doc`).

### File Paths

- Use backtick-quoted relative paths: `` `src/services/llm.py` ``
- In file trees, use the standard tree notation:

```
project/
├── src/
│   ├── main.py
│   └── config.py
├── docs/
│   └── architecture.md
└── README.md
```

- Annotate tree entries with brief descriptions when the name isn't self-explanatory:

```
├── bootstrap.py         # Shared init logic — used by CLI + web
├── config.py            # Settings + re-exports from llm-council
```

---

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|--------------|-------------|-----|
| Duplicating content across files | Goes stale independently, contradicts itself | Keep detail in one file, use pointers elsewhere |
| Hardcoding counts in prose | Requires manual updates across 8+ files | Use verifiable counts or link to the source |
| Writing CLAUDE.md as a knowledge base | Burns tokens every session | Extract to `docs/`, leave a one-line pointer |
| Paragraphs inside table cells | Unreadable, breaks rendering | Keep cells to one line; use a subsection instead |
| Deep nesting (4+ bullet levels) | Cognitive overload, hard to scan | Restructure as subsections or a table |
| Mixing imperative and descriptive voice | Confusing — is this an instruction or a description? | Match voice to document type (see table above) |
| Undated session-specific content in reference docs | Reference docs should be timeless | Session details go in `log/`, not `docs/` |

---

## Checklist for New Documents

Before considering a document complete:

1. **Opening context block** — title + blockquote describing purpose and audience
2. **Header hierarchy** — no skipped levels, `##` as primary structure
3. **Tables for structured data** — not bullet-list parades
4. **Code blocks tagged** — every fenced block has a language identifier
5. **Cross-references linked** — related files and skills linked, not just named
6. **Within line limits** — CLAUDE.md < 200, README < 150, SKILL.md < 300
7. **No duplication** — information lives in one canonical place with pointers
8. **Terminology matches** — uses standard terms from the terminology table
9. **Voice matches document type** — imperative for instructions, descriptive for reference
10. **File paths are relative** — no absolute paths in documentation
