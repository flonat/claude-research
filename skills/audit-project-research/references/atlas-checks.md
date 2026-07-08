# Phase 6 — Atlas drift checks

> Audit init's Phase 7 (Atlas Sync) outputs. Skip if no Atlas topic file was found in Phase 1.

| Check | What to compare | Severity |
|-------|----------------|----------|
| Slug match | CLAUDE.md `**Slug:**` vs atlas filename | Degraded if mismatch |
| Status match | CLAUDE.md status vs atlas `status:` | Info (CLAUDE.md is typically more current) |
| Venue match | CLAUDE.md venues vs atlas `outputs[].venue` | Degraded if mismatch |
| Paper dirs vs atlas outputs | Count and names of `paper*` directories vs `outputs:` array | Degraded if mismatch — **outputs drift** |
| Co-authors match | CLAUDE.md co-authors vs atlas `co_authors:` | Info if mismatch |
| Open questions resolved | Atlas open questions that are now answered by project state | Info |

When paper directory count or venues don't match atlas `outputs:`, the report **must** include this remediation block:

```
⚠ Outputs drift detected — update both systems:
  1. Atlas topic file: update `outputs:` array in
     ~/vault/atlas/<theme>/<slug>.md
  2. Vault submissions: add/remove submission entries in
     ~/vault/submissions/
```
