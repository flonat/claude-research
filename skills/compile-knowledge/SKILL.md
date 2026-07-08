---
name: compile-knowledge
description: "Use when you need to compile raw inputs (literature, meeting notes, session logs, code findings) into a per-project knowledge wiki. Supports --autonomous / -y for end-to-end runs without prompts (used by the Saturday wiki-grow cron)."
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(mkdir*), Agent
argument-hint: "[project-path] [--autonomous|-y] (no args = CWD)"
---

# Compile Knowledge

> Reads raw inputs from a project and compiles/updates a `knowledge/` wiki — a collection of LLM-maintained markdown articles that synthesise everything known about the project's domain.

## When to Use

- After a literature review to consolidate findings
- After a series of sessions on a project to build up the knowledge base
- When starting work on a project and wanting to understand the state of knowledge
- Periodically to keep the knowledge wiki fresh

## When NOT to Use

- For structural project audits — use `/audit-project-research`
- For atlas topic metadata — that stays in the vault
- For session-specific notes — those go in `log/`

---

## Architecture

The knowledge wiki lives at `<project>/knowledge/`:

```
knowledge/
  _index.md          ← auto-maintained index with brief summaries
  concept-name.md    ← one article per concept
  concept-name-2.md
```

**The LLM owns this directory.** the user rarely edits it directly. The value is in the compilation — connecting dots across sources that no single document contains.

---

## Modes

| Mode | Invocation | Behaviour |
|------|-----------|-----------|
| **Interactive** (default) | `/compile-knowledge [project-path]` | Phases run normally; mid-run nudges allowed where useful; end-of-run summary requires no confirmation but the user can inspect output and re-run. |
| **Autonomous** | `/compile-knowledge [project-path] --autonomous` (or `-y`) | End-to-end run with zero prompts. All decisions take the documented default. Single end-of-run summary is the only user-facing output. Used by the Saturday `wiki-grow` cron to refresh project knowledge before the wiki-promotion pass. |

### Autonomous-mode defaults (every choice point)

When `--autonomous` / `-y` is set, the skill takes these defaults silently:

| Choice point | Default |
|-------------|---------|
| Project path unresolved (CWD not a research project) | **Fail** with a single one-line error to stderr. Do not prompt for path. |
| No sources found in Phase 1 | Skip remaining phases; emit `No sources to compile.` and exit clean. |
| Concept granularity uncertain | Prefer **400-600 word articles**, specific scope over generic. Err on the side of fewer, sharper concepts. |
| Article exists but scope shifted | **Update in place** when overlap ≥50% with new finding; create new article only when genuinely orthogonal. |
| Contradictions between sources | **Flag explicitly in prose** ("Source A says X, Source B says Y") — never silently pick a side. |
| Source can't be parsed (encoding, malformed) | Log to the Gaps section in `_index.md`; continue with remaining sources. |
| Atlas topic match in Phase 5 is 0 or >1 | Skip silently (already documented in Phase 5.4). |
| Article exceeds 1000 words | **Split** into two articles by sub-theme; never truncate findings. |

### Autonomous-mode does NOT change

- Knowledge-article quality contract: every claim must cite its source. Unverifiable claims get `[UNVERIFIED]` per the global rule.
- Phase 5 atlas frontmatter sync: still writes `knowledge_last_compiled` on every run.
- Read-only access to `data/raw/` per the global data-sensitivity rule.
- Per-project `MEMORY.md` / `CLAUDE.md` are NEVER edited by this skill.

If any of the above fails (e.g. an `[UNVERIFIED]` flag couldn't be applied due to a write error), include the failure in the end-of-run summary rather than blocking.

---

## Phase 1: Locate Project and Scan Sources

1. Resolve project path (CWD or argument)
2. Scan for raw inputs:

| Source | Location | What to extract |
|--------|----------|----------------|
| Literature reviews | `docs/literature-review/` | Paper summaries, key findings, research gaps |
| Meeting notes | `meeting-notes/` or `to-sort/` recaps | Decisions, insights, action items |
| Session logs | `log/` | Research progress, discoveries, pivots |
| MEMORY.md | Project root | Notation, decisions, pitfalls, domain corrections |
| Atlas topic file | `~/vault/atlas/<theme>/<slug>.md` | Status, connected topics, research questions |
| Code README/comments | `code/`, `src/` | What the code does, key algorithms |
| Paper sections | `paper-*/paper/*.tex` | Current argument structure, contributions |
| `.context/project-recap.md` | `.context/` | Project overview, current state |

3. Report source inventory:
   ```
   Sources found:
     Literature:  12 papers in docs/literature-review/
     Sessions:    8 logs in log/
     Memory:      14 entries in MEMORY.md
     Paper:       3 sections drafted
     Code:        2 scripts in code/python/
   ```

## Phase 2: Identify Concepts

Read all sources and extract a concept list — the key ideas, methods, datasets, theories, and phenomena that the project deals with.

**Concept granularity:** Each concept should be specific enough to warrant its own article (~200-1000 words). Too broad = useless summary. Too narrow = fragmented.

Examples of good concepts:
- `mechanism-design-for-audits.md` (a specific method applied to the project's domain)
- `collusion-detection-methods.md` (a family of techniques relevant to the project)
- `eu-ets-carbon-market.md` (institutional context)
- `callaway-santanna-estimator.md` (a specific estimator used)

Examples of bad concepts:
- `introduction.md` (too structural — that's the paper's job)
- `regression.md` (too generic)
- `table-3.md` (too narrow)

## Phase 3: Compile Articles

For each concept, create or update `knowledge/<concept-name>.md`:

```markdown
# <Concept Name>

> One-sentence summary of what this concept is and why it matters to the project.

## Key Findings

- Bullet points synthesising what is known from all sources
- Each finding should cite its source: (Author Year) or (session log YYYY-MM-DD)
- Flag contradictions: "Source A says X, but Source B says Y"

## Open Questions

- What is not yet known or resolved
- Questions that emerged from the literature but aren't answered
- Methodological choices that remain open

## Sources

| Source | Type | Key contribution |
|--------|------|-----------------|
| Author (Year) | Paper | Finding X |
| Session 2026-03-15 | Log | Discovered Y |
| MEMORY.md | Decision | Chose Z because... |

## Related

- [[other-concept]] — how they connect
- Atlas: `<topic-slug>` — link to atlas topic if relevant
```

**Rules:**
- Be specific and factual — no filler prose
- Cite sources for every claim
- Flag contradictions explicitly rather than silently picking one side
- Keep articles between 200-1000 words
- Use `[[wikilink]]` syntax for cross-references between knowledge articles

## Phase 4: Update Index

Write or update `knowledge/_index.md`:

```markdown
# Knowledge Index

> Auto-maintained by `/compile-knowledge`. Last updated: YYYY-MM-DD.
> N articles, ~X words total.

## Articles

| Article | Summary | Sources | Last updated |
|---------|---------|---------|-------------|
| [Concept A](concept-a.md) | One-line summary | 3 papers, 2 sessions | YYYY-MM-DD |
| [Concept B](concept-b.md) | One-line summary | 1 paper, 1 decision | YYYY-MM-DD |

## Source Coverage

| Source type | Count | Compiled into articles |
|------------|-------|----------------------|
| Papers | 12 | 10 (2 not yet compiled) |
| Session logs | 8 | 5 (3 not yet compiled) |
| Memory entries | 14 | 12 |

## Gaps

- [List concepts that should exist but don't yet]
- [Sources not yet compiled into any article]
```

## Phase 5: Atlas frontmatter sync

After writing `_index.md`, also update the atlas topic frontmatter so the
project's compile date is discoverable from outside the project (e.g. by
`/session-close`, the wiki promotion cron, atlas-workspace).

1. Resolve the atlas topic: `grep -rl "project_path:.*$(basename "$PWD")" ~/vault/atlas/`
2. If a single match is found, set or update the frontmatter field
   `knowledge_last_compiled: YYYY-MM-DD` (today's date in UTC).
3. If the field already exists, overwrite. If absent, insert before the
   closing `---`.
4. If 0 or >1 atlas topic files match, skip silently and log to the
   end-of-run summary (`Atlas frontmatter sync: skipped — N matches`).

The field is consumed by:

- `/session-close` (info-only freshness line via
  `references/research-checks.md` § 18)
- The Saturday `wiki-grow` cron (uses the date to schedule re-promotion)
- atlas-workspace (could surface in topic-page metadata row in future)

## Phase 6: Incremental Mode

When run on a project that already has `knowledge/`:

1. Detect new sources since last compilation (check `_index.md` last-updated date vs source file modification dates)
2. Only process new/modified sources
3. Update existing articles with new findings (append, don't rewrite)
4. Create new articles only for genuinely new concepts
5. Update `_index.md`
6. Update atlas frontmatter `knowledge_last_compiled` (Phase 5)

Report:
```
Knowledge updated:
  Articles updated: 3 (concept-a, concept-b, concept-c)
  Articles created: 1 (new-concept)
  Sources processed: 4 new since last compile
  Total: N articles, ~X words
```

---

## Output

Print summary after compilation:
```
Knowledge compiled for <project-name>:
  Articles: N (M new, K updated)
  Total words: ~X
  Sources compiled: Y / Z total
  Gaps: [list any uncompiled sources]
  Index: knowledge/_index.md
```

---

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/store-insight` | Lightweight single-finding filer — called by other skills |
| `/knowledge-lint` | Checks compiled knowledge for inconsistencies |
| `/literature` (pipeline mode) | Produces literature reviews that feed into compilation |
| `/session-close` | Extracts session insights and files them via `/store-insight` |
