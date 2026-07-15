# Review index schema

Each project may keep an append-only review log at `reviews/INDEX.md`. Review
skills and agents append one row per run; reports live beneath
`reviews/<scope>/<check>/`.

## Canonical row

```markdown
| Paper | Check | Last Run | Verdict | Score | Open Issues | Source | Trigger | Report | Notes |
```

| Column | Meaning |
|---|---|
| Paper | Paper slug, or `—` for a project-level review |
| Check | Skill or agent slug |
| Last Run | Local `YYYY-MM-DD HH:MM` timestamp |
| Verdict | Workflow-specific result such as `PASS` or `NEEDS REVISION` |
| Score | Optional `n/100` score, otherwise `—` |
| Open Issues | Snapshot such as `3/12`, otherwise `—` |
| Source | `skill`, `agent`, `manual`, or `recap-inferred` |
| Trigger | `direct` or the invoking orchestrator slug |
| Report | Project-relative report path, otherwise `—` |
| Notes | One line with no pipe character |

Reports use:

```text
reviews/<scope>/<check>/<YYYY-MM-DD-HHMM>.md
```

Use `_project` as the path scope when the Paper column is `—`. Never overwrite
an earlier report or rewrite an earlier index row: later runs append new
evidence. A legacy root `REVIEW-STATE.md` is read-only migration input and must
not receive new rows.

The installed `_shared/review-state-log.sh` helper implements this contract.
The installed `_shared/stamp-directive-spec.md` defines the strict YAML block
used when a delegated reviewer cannot append the row itself.
