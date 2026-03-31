# Project Documentation Conventions

> Shared conventions for outward-facing documentation: project READMEs, user manuals, architecture docs, deploy guides, and in-app help. Ensures consistency across Scout, council packages, and future projects.
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
| Scout | `README.md` | README |
| Scout | `docs/user-manual.md` | User manual |
| Scout | `docs/architecture.md` | Architecture |
| Scout | `deploy/README.md` | Deploy guide |
| Scout | `docs/user-manual.tex` | LaTeX manual |
| Scout | `docs/scout-overview/scout-overview.tex` | Beamer deck |
| Task Management | `docs/user-manual/user-manual.tex` | LaTeX manual |
| Task Management | `docs/setup-overview/setup-overview.tex` | Beamer deck |
| Task Management | `docs/setup-overview/setup-overview-public.tex` | Beamer deck (public) |
| Task Management | `public/public-repo/README.md` | README (public) |
| Task Management | `public/public-repo/docs/getting-started.md` | Getting started |
| Task Management | `public/public-repo/docs/council-mode.md` | Feature guide |
| Task Management | `public/public-repo/docs/biblio-setup.md` | Setup guide |
| Task Management | `public/public-repo/docs/setup.md (legacy)` | Setup guide |

### Tagging Protocol

When **creating** new outward-facing documentation (README, user manual, architecture doc, deploy guide, Beamer deck, or LaTeX manual):

1. Add the appropriate tag as the very first line of the file
2. Add the file to the registry table above

When **auditing** a project's documentation (via `/sync-repo scout`, `/update-project-doc`, or manually):

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

## Content Conventions

Detailed conventions for each document type: [`project-documentation-content.md`](project-documentation-content.md)

Covers: README required sections, user manual structure, per-workflow pattern, architecture doc structure, deploy guide structure, in-app help system, library/package READMEs, CLI example conventions.

## Format Conventions

Detailed conventions for formatting and presentation: [`project-documentation-format.md`](project-documentation-format.md)

Covers: ASCII diagrams, env var tables, tone by audience, LaTeX preamble and commands, Beamer decks (colour palette, TikZ, bullet styles), public/anonymized variants (sync markers, anonymization rules), automated validation (`validate_docs.py` pattern).

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
