# Rule: Read Documentation Before Searching

## Principle

**Never explore when documentation already answers your question.** Broad codebase searches (Glob, Grep, web searches) burn tokens and time. Project docs exist precisely to avoid this.

## On Every New Session

Before doing any work, read these files **in order** (they are fast reads, not searches). The `startup-context-loader.sh` hook auto-loads most of these, but follow the pointers in case you need more detail:

1. `CLAUDE.md` — already auto-loaded, but follow its pointers
2. `.context/current-focus.md` — what the user is working on NOW
3. `.context/projects/_index.md` — overview of all projects
4. `MEMORY.md` (if it exists) — structured knowledge tables and `[LEARN]` corrections
5. The latest file in `log/` — where the last session left off
6. The latest file in `log/plans/` (if any) — where the last plan left off

This takes seconds and prevents minutes of aimless searching.

## Before Any Search

When you need information about the project, check in this order:

1. **CLAUDE.md and .context/ files** — they cover identity, projects, workflows, conventions
2. **Project-specific docs** (README.md, docs/ folder) — they cover that project's structure
3. **Existing code comments and docstrings** — read the relevant file directly
4. **Only then** use Grep/Glob for targeted searches
5. **Web search is a last resort** — never search the web for something already documented locally

## Anti-Patterns (Do NOT Do These)

- Globbing for `**/*.md` across the entire repo to "find" documentation you were already told about
- Grepping for keywords when CLAUDE.md explicitly lists where things are
- Using the Explore agent to "understand the codebase" when `.context/` files describe it
- Web-searching for tool usage or conventions that are documented in project files
- Reading 10+ files "to understand context" when current-focus.md summarizes it

## For Other Projects (Not Task Management)

When starting a session in a research project:

1. Read that project's `CLAUDE.md` (if it exists)
2. Read that project's `MEMORY.md` (if it exists) — notation, decisions, pitfalls
3. Read that project's `README.md` (if it exists)
4. Check for a `docs/` folder
5. Only then explore the file tree

## Why This Matters

the user's context library (`.context/`) is specifically designed to give you everything you need upfront. Ignoring it to do your own research wastes tokens and produces worse results because you miss the curated context.
