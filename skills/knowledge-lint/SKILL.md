---
name: knowledge-lint
description: "Use when you need to check compiled knowledge for contradictions, uncited claims, missing connections, stale articles, and orphaned concepts."
allowed-tools: Read, Glob, Grep, Write, Agent
argument-hint: "[project-path] or no arguments for CWD"
---

# Knowledge Lint

> Substantive consistency checks on the compiled knowledge wiki. Produces `correspondence/internal-reviews/KNOWLEDGE-LINT-REPORT.md`.

## Output Path

Per `rules/review-artefact-routing.md` (auto-loads in research projects (path-scoped to `paper-*/` and `paper/`)):

- **Source slug:** `knowledge-lint`
- **Write reports to:** `reviews/_project/knowledge-lint/YYYY-MM-DD-HHMM.md` inside the project. Path is relative to the research project root, not the Task-Management repo.
- **Never** at project root (`./CRITIC-REPORT.md`-style filenames are forbidden — pre-rule layout).
- **Idempotency:** if today's file exists, append a same-day descriptor (`{date}-revision.md`, `{date}-r2.md`, `{date}-pre-submission.md`) — never overwrite.
- **Index update:** if `reviews/INDEX.md` exists, write a one-line entry under "Latest per source" pointing at the new file. Otherwise `/review-recap` will rebuild the index next time it runs.
- **Infrastructure repos** (Task-Management, atlas-workspace, etc.): this section does not apply — the path-scoped rule won't load there.


## When to Use

- After running `/compile-knowledge` to verify integrity
- Before writing a paper section to check the knowledge base is solid
- Periodically (monthly) to catch drift
- When switching between projects to verify knowledge is current

## When NOT to Use

- If no `knowledge/` directory exists — run `/compile-knowledge` first
- For structural project audits — use `/audit-project-research`
- For bibliography validation — use `/bib-validate`

---

## Pre-Check

1. Verify `knowledge/` exists and has at least 2 articles (linting a single article is pointless)
2. If missing: "No knowledge directory found. Run `/compile-knowledge` first."

---

## Checks

### 1. Contradictions

Scan all articles for claims about the same concept that disagree:

| Check | How |
|-------|-----|
| Same concept, different claims | Compare Key Findings sections across articles that share wikilinks |
| Method disagreements | Check if two articles recommend different approaches for the same problem |
| Factual conflicts | Cross-reference dates, numbers, definitions across articles |

Report format:
```
CONTRADICTION: concept-a.md says "X increases Y" but concept-b.md says "X has no effect on Y"
  Source A: Author (2023) — concept-a.md line 15
  Source B: Author (2024) — concept-b.md line 22
  Resolution needed: check which paper's context applies
```

### 2. Uncited Claims

Scan Key Findings sections for assertions without source attribution:

| Check | How |
|-------|-----|
| Missing citations | Findings that don't reference a paper, session log, or decision |
| Vague citations | "Some studies show..." without specific references |
| Self-referential | Citing another knowledge article instead of a primary source |

### 3. Missing Connections

Check for concepts that should link to each other but don't:

| Check | How |
|-------|-----|
| Shared keywords | Two articles mention the same method/dataset/author but don't cross-reference |
| Atlas connections | Atlas topic has `connected_topics` that don't have corresponding knowledge articles |
| Orphaned articles | Articles with zero incoming wikilinks from other articles |

### 4. Staleness

| Check | How |
|-------|-----|
| Stale articles | Last updated > 90 days ago AND project has had session activity since |
| Source drift | New papers in `docs/literature-review/` not compiled into any article |
| Memory drift | New `[LEARN]` entries in MEMORY.md not reflected in knowledge articles |
| Session drift | Recent session logs mention findings not in any knowledge article |

### 5. Coverage Gaps

| Check | How |
|-------|-----|
| Key paper not compiled | Papers cited in `paper-*/paper/*.tex` but not in any knowledge article |
| Method not documented | Estimators/methods used in code but not explained in knowledge |
| Concepts mentioned but not defined | Terms used across multiple articles without a dedicated article |

### 6. Promotion readiness (advisory)

Project knowledge articles are the upstream source that `/wiki-grow`
promotes into vault concepts (`~/vault/concepts/`). Articles
that escape their origin project (mentioned in ≥3 corpus docs) get
auto-promoted as `status: draft` and later curated to the **concept
anatomy** (`packages/atlas-vault/schema.md` → "Concept File Schema"):
a lead `## In one line` definition, encyclopedia-voice body, and a
`## In my portfolio` section for project-specific prose.

This is advisory, not a hard check — project knowledge lives in the
project's own voice and needn't conform. But flagging an article that
**leads with a crisp, project-agnostic definition** as "promotion-ready"
(vs. one that opens mid-analysis) helps: the cleaner the lead, the
cheaper the eventual draft→curated pass. Note such articles in
Recommendations; don't rewrite them here.

---

## Report

Write `correspondence/internal-reviews/KNOWLEDGE-LINT-REPORT.md` (create directory with `mkdir -p` if needed):

```markdown
# Knowledge Lint Report

**Project:** [name]
**Date:** YYYY-MM-DD
**Articles scanned:** N
**Total words:** ~X

## Summary

| Check | Issues | Severity |
|-------|--------|----------|
| Contradictions | N | High |
| Uncited claims | N | Medium |
| Missing connections | N | Low |
| Staleness | N | Medium |
| Coverage gaps | N | Medium |

## Contradictions (High)

[List each with source references and suggested resolution]

## Uncited Claims (Medium)

[List each with article and line]

## Missing Connections (Low)

[List pairs that should link]

## Staleness (Medium)

[List stale articles with last-updated date and evidence of new activity]

## Coverage Gaps (Medium)

[List uncompiled sources and undocumented concepts]

## Recommendations

1. [Most impactful fix]
2. [Second]
3. [Third]
```

---

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/compile-knowledge` | Run this first to build/update the wiki |
| `/store-insight` | Use to fix individual gaps found by lint |
| `/atlas-coherence` | Complementary — checks topic-level connections, not article-level |
| `/wiki-curate` | Downstream — audits the vault concepts these articles promote into (anatomy, lifecycle, overlap) |
