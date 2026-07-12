---
paths:
  - "**/CLAUDE.md"
  - "**/GLOBAL-CLAUDE.md"
  - "**/AGENTS.md"
---

# Rule: Keep Guidance Files Lean

## Principle

**Client guidance files are loaded into context repeatedly—every line costs tokens and attention.** `CLAUDE.md`, `AGENTS.md`, and generated global guidance should contain only instructions needed on entry. Everything else belongs in dedicated files read on demand.

## What Belongs in Entry Guidance

- Safety rules and file-protection policies
- Folder structure (compact tree)
- Conventions (compilation, tooling, citation format)
- Symlink paths and setup commands
- Session continuity pointers (`.context/`, `log/`)
- One-line summaries of reference material with relative links

## What Does NOT Belong in Entry Guidance

- Full assessment/submission guidelines → `docs/`
- Detailed literature notes → `docs/literature-review/`
- Action plans or timelines → standalone `.md` at project root or `docs/`
- Long reference lists (>10 entries) → `docs/` or `.bib` files
- Ethics materials, reviewer feedback → `docs/`
- Anything that duplicates content already in another project file

## The Pointer Pattern

When reference material exists elsewhere, use a one-line summary + link:

```markdown
## Assessment Criteria

60 CATS, max 15,000 words, submission early August. Must be publication-ready.

Full guidelines: [`docs/portfolio-guidelines.md`](docs/portfolio-guidelines.md)
```

## Thresholds

- **Project `CLAUDE.md` or `AGENTS.md` > 200 lines or 1,500 words:** Review for extractable content.
- **Generated global guidance > 1,500 words:** Move workflow-specific rules to an on-demand index while keeping safety summaries loaded.
- **Any section > 15 lines of reference material** (not safety rules or conventions): Extract to `docs/` and replace with a pointer.
- **Duplicated content:** If the same information exists in another file, keep only the pointer in the entry guidance.

## Applies To

All projects and both clients. The principle is universal: an entry guidance file is an instruction router, not a knowledge base.
