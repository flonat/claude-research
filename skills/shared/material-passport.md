# Material Passport — Artifact Provenance Protocol

> Tracks provenance, lineage, and staleness of research artifacts across pipeline stages. Enables automatic detection of when downstream work needs re-verification due to upstream changes.

## Principle

**Every artifact should know where it came from and when it was last verified.** When an upstream artifact changes (bibliography updated, data re-processed, method revised), downstream artifacts that depend on it become stale. Without explicit tracking, stale artifacts silently propagate — a revised bibliography doesn't trigger re-synthesis of the literature review, a corrected dataset doesn't invalidate old regression tables.

## When This Applies

- Multi-stage research pipelines (literature → synthesis → paper → review → revision)
- Any project where outputs from one skill feed into another
- Post-revision cycles where integrity must be re-verified

## Passport Schema

Every artifact produced by a skill or agent carries metadata (in YAML frontmatter, JSON sidecar, or inline comment):

```yaml
_passport:
  origin_skill: literature          # Which skill produced this
  origin_mode: pipeline             # Which mode of the skill
  version: v2                       # Monotonic version (never reused)
  produced: 2026-04-11T14:30:00Z    # When this version was created
  verified: 2026-04-11T14:45:00Z    # When last integrity-checked (null if never)
  verification_status: VERIFIED     # VERIFIED | UNVERIFIED | STALE
  upstream:                         # What this artifact depends on
    - artifact: references.bib
      version: v3
      hash: abc123                  # First 7 chars of SHA-256 (for change detection)
    - artifact: search-results.json
      version: v1
      hash: def456
```

## Staleness Detection

An artifact becomes **STALE** when any of its upstream dependencies change:

```
IF upstream.hash != current_hash(upstream.artifact):
    downstream.verification_status = STALE
    downstream.verified = null
```

### Staleness Propagation

Staleness cascades. If A depends on B, and B depends on C:
- C changes → B becomes STALE → A becomes STALE
- B is re-verified → B becomes VERIFIED → A remains STALE (must be independently re-verified)

### What Triggers Staleness

| Event | Artifacts affected |
|-------|-------------------|
| `.bib` file modified | Literature synthesis, paper sections citing it |
| Data file modified | All regression tables, figures, claims citing that data |
| Method changed | All results produced by old method |
| Paper section rewritten | Review reports referencing that section (during revision) |
| New papers added to bibliography | Synthesis may be incomplete |

## Version Labels

Version labels are skill-specific and monotonically increasing:

| Artifact | Label format | Example |
|----------|-------------|---------|
| Bibliography | `bib_v{N}` | `bib_v3` |
| Literature synthesis | `synthesis_v{N}` | `synthesis_v2` |
| Paper draft | `draft_v{N}` | `draft_v4` |
| Review report | `review_v{N}` | `review_v1` |
| Regression tables | `tables_v{N}` | `tables_v2` |

Labels are never reused. A revised draft is `draft_v5`, not `draft_v4_revised`.

## How Skills Use This

### Producer responsibility

When a skill produces an artifact:
1. Assign a version label (increment from last version of same artifact type)
2. Record upstream dependencies with their current hashes
3. Set `verification_status: UNVERIFIED` (unless the skill includes built-in verification)
4. Write passport to artifact frontmatter or sidecar file

### Consumer responsibility

When a skill reads an artifact as input:
1. Check its passport's `verification_status`
2. If STALE or UNVERIFIED: warn the user before proceeding
3. If verified but `verified` timestamp is >7 days old: suggest re-verification

### Verification responsibility

When an integrity gate or review agent verifies an artifact:
1. Update `verified` timestamp
2. Set `verification_status: VERIFIED`
3. Record which checks were performed

## Lightweight Implementation

For projects that don't need full passport tracking, a minimal version:

### Option A: Frontmatter annotation (for .md files)

```yaml
---
title: Literature Synthesis
_version: synthesis_v2
_produced: 2026-04-11
_depends_on: [references.bib@v3, search-results.json@v1]
_status: VERIFIED
---
```

### Option B: Sidecar file (for .bib, .tex, data files)

Create `{filename}.passport.yml` alongside the artifact:

```yaml
artifact: references.bib
version: bib_v3
produced: 2026-04-11T14:30:00Z
verified: 2026-04-11T14:45:00Z
status: VERIFIED
upstream: []
downstream:
  - literature-synthesis.md@synthesis_v2
  - paper/introduction.tex@draft_v4
```

### Option C: Project-level registry (simplest)

Single file at `{project}/.planning/artifacts.yml`:

```yaml
artifacts:
  references.bib:
    version: bib_v3
    modified: 2026-04-11
    status: VERIFIED
  synthesis.md:
    version: synthesis_v2
    modified: 2026-04-10
    status: STALE  # bib changed after synthesis was written
    depends_on: [references.bib@bib_v2]  # note: depends on v2, current is v3
```

## Integration Points

| Skill | Role |
|-------|------|
| `/literature` | Producer of .bib and synthesis. Sets passport on output. |
| `/bib-validate` | Verifier. Updates passport status to VERIFIED on pass. |
| `paper-critic` | Consumer + verifier. Flags STALE artifacts as blocking issues. |
| `integrity-gates` | Verifier. Runs gates and updates passport status. |
| `/computational-experiments` | Producer of tables/figures. Sets passport with data dependencies. |
| `/audit-project-research` | Auditor. Scans all passports for STALE artifacts. |

## When to Skip

- Quick one-off searches (standalone `/literature`)
- Early exploration where nothing is "produced" yet
- Projects without multi-stage pipelines
- When the user says "don't bother tracking this"

## Why This Matters

Without provenance tracking:
- A corrected bibliography doesn't trigger re-synthesis of the literature review
- A revised paper section doesn't invalidate the review report
- A new data cut doesn't flag old regression tables as stale
- The user discovers staleness manually, weeks later, when something doesn't add up

With provenance tracking:
- Staleness is detected automatically at the point of consumption
- Re-verification is targeted (only stale artifacts, not everything)
- Audit skills can report "3 artifacts are stale" instead of requiring full re-checks
