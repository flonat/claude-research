# Review: K-Dense-AI/claude-scientific-writer

> Reviewed 2026-02-24. Repo: https://github.com/K-Dense-AI/claude-scientific-writer (856 stars)

## What It Is

A monolithic scientific document generation tool combining Claude with real-time literature search (Perplexity via OpenRouter) and AI diagram generation (Nano Banana Pro). Available as Claude Code plugin, CLI, or Python API. MIT-licensed.

## Architecture

- **24 skills**: writing, research-lookup, peer-review, citation-management, clinical-reports, research-grants, latex-posters, scientific-slides, hypothesis-generation, market-research-reports, scientific-schematics, infographics, literature-review, venue-templates, etc.
- **External APIs**: Perplexity Sonar Pro Search (literature), Nano Banana Pro (diagrams), Parallel Web API (general web search/extraction)
- **LaTeX-first** output with BibTeX citations by default
- **Multi-pass writing**: skeleton → research per section → write → verify citations → compile → PDF review via image conversion
- **Version management**: v1_draft.tex, v2_draft.tex, etc. — never overwrites previous versions
- All research results saved to `sources/` folder for auditability and context recovery

## Key Strengths

- **Citation verification loop**: research before writing, verify every BibTeX entry has complete metadata (DOI, volume, pages), web-search for missing fields
- **Peer review**: quantitative ScholarEval framework (8-dimension scoring)
- **Figure generation**: minimum counts per document type, mandatory graphical abstract
- **Full lifecycle**: hypothesis → writing → review → revision
- **Structured output pipeline** with progress tracking and summary reports

## Overlap with Our Setup

| Their Feature | Our Equivalent |
|---------------|---------------|
| `research-lookup` + `citation-management` | `/literature` skill + `.mcp-server-biblio` |
| `peer-review` / `scholar-evaluation` | `referee2-reviewer`, `paper-critic`, `domain-reviewer` agents |
| `venue-templates` | Topic Finder `venues.json` + framing workflow |
| `latex-posters` / `scientific-slides` | `/beamer-deck`, `/quarto-deck` |

## Key Differences from Our Approach

- **Monolithic vs modular**: one tool does everything; ours is skills + agents + standalone apps
- **External API-heavy**: requires Perplexity, Nano Banana Pro, Parallel Web API keys (more cost)
- **"Never stop" philosophy**: their CLAUDE.md says "NEVER ask 'would you like me to continue?'"; ours has plan-first discipline and phase boundaries
- **No novelty scoring or venue-specific framing**: that's unique to our Topic Finder
- **Heavy CLAUDE.md**: ~500 lines of instructions; ours follows lean-claude-md rule
- **No design-before-results discipline**: no equivalent to our research design rules

## Ideas Worth Borrowing

1. **Citation metadata verification loop** — after BibTeX creation, systematically search for missing DOI/volume/pages. Could enhance `/validate-bib`.
4. **PDF review via image conversion** — convert PDF to images and visually inspect each page for formatting issues. Could add as a step in `/latex-autofix`.
5. **Progress logging per section** — timestamped logs of word count and citation count per section during writing. Lighter version could fit our session logging.
