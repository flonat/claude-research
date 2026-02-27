# Rule: Keep CLAUDE.md Lean

## Principle

**CLAUDE.md is loaded into context every session — every line costs tokens.** It should contain only instructions Claude needs on every entry. Everything else belongs in dedicated files that Claude reads on demand.

## What Belongs in CLAUDE.md

- Safety rules and file-protection policies
- Folder structure (compact tree)
- Conventions (compilation, tooling, citation format)
- Symlink paths and setup commands
- Session continuity pointers (`.context/`, `log/`)
- One-line summaries of reference material with relative links

## What Does NOT Belong in CLAUDE.md

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

- **CLAUDE.md > 200 lines:** Review for extractable content.
- **Any section > 15 lines of reference material** (not safety rules or conventions): Extract to `docs/` and replace with a pointer.
- **Duplicated content:** If the same information exists in another file, keep only the pointer in CLAUDE.md.

## Applies To

All projects — research, code, infrastructure, personal. The principle is universal: CLAUDE.md is an instruction file, not a knowledge base.
