---
name: wiki-grow
description: "Use when you want to auto-promote project knowledge articles into vault wiki concepts. Saturday cron job — runs the corpus scanner, picks candidates above threshold, copies each source article into ~/vault/concepts/ with auto_generated frontmatter so it surfaces immediately on topic pages. Can also be run interactively for a dry-run preview."
allowed-tools: Bash, Read
argument-hint: "--dry-run (default) | --autonomous to actually write"
---

# Wiki Grow — Autonomous Concept Promotion

> Saturday-cron worker that grows `~/vault/concepts/` from
> existing project knowledge articles. Designed for **zero cognitive
> load**: it surfaces results in the Maintenance Inbox; suppression is
> a single line in a `.denylist` file. the user never has to decide
> "promote this y/n" at the moment of running.

## When to Use

- The Saturday 06:45 cron runs it automatically. Don't invoke manually
  unless you want to:
  - **Preview** what would be promoted: `/wiki-grow --dry-run`
  - **Force a run** after curating the denylist or scaffolding new
    knowledge: `/wiki-grow --autonomous`

## When NOT to Use

- For per-project knowledge compilation — that's `/compile-knowledge`.
- For checking which concepts already exist — that's just
  `~/vault/concepts/` or the wiki at `wiki.example.com`.
- For tearing down a concept — delete the file and add the slug to the
  denylist (one line each).

---

## Architecture

Three components, all in this repo:

| File | Role |
|------|------|
| `scripts/wiki-promote-scan.py` | Inventory scanner. Walks vault concepts + project knowledge folders + atlas/book prose. Outputs `/tmp/wiki-promote-scan.{md,json}` with corpus mention counts and the wikilink graph. |
| `scripts/wiki-grow.py` | Orchestrator. Reads the scan, applies thresholds, copies candidates into `~/vault/concepts/<slug>.md` with auto-generated frontmatter and a draft banner. At copy time, `[[wikilinks]]` whose targets resolve to no vault file (atlas/concepts/venues/people/themes — same semantics as atlas-workspace's `dead_wikilinks()` validator) are converted to plain text; links between slugs co-promoted in the same run survive. Added 2026-06-12 after verbatim copies created 38 dead links on the wiki. |
| `scripts/weekly-wiki-grow.sh` | Launchd-callable shell wrapper. Cron entrypoint. |
| `~/Library/LaunchAgents/com.example.weekly-wiki-grow.plist` | Saturday 06:45 schedule. |

---

## Promotion Thresholds

A slug is promoted on a given run if **all** of the following hold:

1. The slug appears as a project knowledge file in at least one
   `<project>/knowledge/` directory.
2. The slug is mentioned in **≥3 corpus documents** (atlas topics +
   book chapters + project CLAUDE.md files), per the scanner's
   Section D ("escaped scope" — present beyond the origin project).
3. No vault concept already exists at `~/vault/concepts/<slug>.md`.
4. The slug is **not** in `~/vault/concepts/.denylist`.

Run cap: at most **8 candidates per run** (`MAX_CANDIDATES_PER_RUN` in
`wiki-grow.py`). Excess candidates roll over to the next Saturday — by
which time the denylist has had a chance to filter them.

---

## Stub Format

Each promoted concept gets:

```markdown
---
title: <Concept Name>
slug: <slug>
type: concept
auto_generated: true
source_project: <project-slug>
source_path: /full/path/to/knowledge/<slug>.md
promoted_on: 'YYYY-MM-DD'
corpus_mentions_at_promotion: N
related_topics: []
---

> **Auto-promoted draft.** Seeded from `<project>/knowledge/<slug>.md`
> on YYYY-MM-DD (corpus mentions at promotion: N). Body is verbatim
> from the source — refine for project-agnostic use when read. To
> remove, add the slug to `~/vault/concepts/.denylist`.

<body verbatim from project knowledge article, leading H1 stripped>
```

The `auto_generated: true` flag causes the concept overview page on
`wiki.example.com` to render a small amber "auto-promoted draft" badge
next to the title — the visual contract that distinguishes machine
seeds from human-curated entries.

---

## Suppression — the Denylist

Single source of truth: `~/vault/concepts/.denylist`. One
slug per line; `#` lines are comments.

When a denylisted slug is encountered:

- Scanner still picks it up (it's part of the corpus).
- Orchestrator skips it during candidate generation.
- The slug never gets a vault concept stub, no matter how many corpus
  mentions accumulate.

To stop the noise from a slug you've decided isn't a concept:

```
# ~/vault/concepts/.denylist
prompt-sensitivity      # too narrow — covered by llm-as-judge
threat-models           # generic — never promote
```

If you change your mind, remove the line. The next Saturday run will
re-promote on threshold.

---

## Output

Per-run summary in `~/vault/inbox/wiki-grow-YYYY-MM-DD.md`:

```
# Wiki promotion run (YYYY-MM-DD)

- Promoted: **3** new concepts to `~/vault/concepts/`
- Skipped (already in vault): 6
- Skipped (denylist): 2
- Below threshold (3+ mentions): 12

## Promoted slugs
- [`strategic-classification`](https://wiki.example.com/concept/strategic-classification) (14 mentions, from example-project-e)
- ...
```

The maintenance inbox (`atlas.example.com/inbox`) surfaces this file as
a single line "Wiki grew: N concept(s) auto-promoted" so you have
weekly signal without weekly triage work.

---

## Modes

| Mode | Invocation | Behaviour |
|------|-----------|-----------|
| **Dry-run** (default) | `uv run python scripts/wiki-grow.py` | Prints the candidate plan, writes nothing. Safe to run ad-hoc. |
| **Autonomous** | `uv run python scripts/wiki-grow.py --autonomous` | Writes stubs + inbox summary. Used by cron. |

`--autonomous` here matches the global flag convention (`--autonomous` /
`-y`) — see `rules/phased-work.md`.

---

## When the LLM Layer Lands

v1 of this skill is deterministic copy + banner — no LLM dispatch per
candidate. Project-specific framing in stub bodies is acceptable
short-term cost in exchange for fast, idempotent, zero-key cron runs.

When the LLM refinement step is added (v2), it will replace the body
of `_promote_one()` in `wiki-grow.py` with a sub-agent dispatch that
reads the source article and writes a project-agnostic version. The
stub frontmatter (`auto_generated: true`, etc.) stays the same so
existing pages don't need migration.

---

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/compile-knowledge` | Upstream — writes the project knowledge articles wiki-grow promotes from. Must run first to seed candidates. |
| `/atlas-audit` | Checks vault concept coverage as part of its routine audits. |
| `/process-inbox` | Triages the weekly summary item. |
