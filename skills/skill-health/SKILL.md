---
name: skill-health
description: "Use when you need a dashboard of skill invocation counts, success rates, failure patterns, and health status. Reads JSONL logs and qualitative observations. Reporting only — never auto-modifies skills."
allowed-tools: Bash(uv*, cat*, wc*, sort*, uniq*, head*, tail*, jq*, date*, mkdir*, ls*), Read, Write, Glob, Grep
argument-hint: "[--skill <name>] [--health failing|watch|healthy] [--period 7d|30d|all] [--failures-only]"
---

# Skill Health

Run the skill health assessment and present results.

## Process

1. Mine session logs for new skill invocation data:
   ```bash
   uv run python .scripts/skill-log-miner.py
   ```

2. Run the health assessment script:
   ```bash
   uv run python .scripts/skill-health.py
   ```

2. Present the table output to the user.

3. If there are **failing** or **watch** skills, highlight them and suggest investigation:
   - For failing skills: "This skill has a 30%+ error rate. Check the top error classes."
   - For watch skills: "This skill has a 10%+ error rate. Monitor over the next week."

4. If the user asks for detail on a specific skill:
   ```bash
   uv run python .scripts/skill-health.py --skill <name>
   ```

5. If asked to run maintenance:
   ```bash
   uv run python .scripts/skill-health.py --purge
   ```

## Filters

- `--health failing|declining|watch|healthy|insufficient_data|low_observability`
- `--activity active|regular|dormant`
- `--top N` — top N most-used
- `--all-time` — ignore rolling window
- `--json` — machine-readable output

## Trend Detection

The health script computes **7-day vs 30-day windowed success rates** per skill:
- **Declining**: 7d success rate dropped 10%+ below 30d rate → early warning
- **Improving**: 7d rate is 10%+ above 30d rate → recovering
- **Stable**: rates within 10% of each other

A skill is classified as `declining` health status when the trend is `worsening` but the absolute error rate hasn't yet crossed the `watch` (10%) or `failing` (30%) thresholds. This catches degradation early.

## Qualitative Observations

After presenting the quantitative report, check `~/.claude/skill-observations/log.md` for any OPEN observations relevant to the skills shown. Mention them briefly: "There are also N qualitative observations pending review."

## Weekly Review Trigger

Check `~/.claude/skill-observations/last-review-date.txt`. If older than 7 days, suggest running the weekly review protocol.

## Label Distribution

When `ratings.jsonl` contains label data, show a per-skill label breakdown:

```
Label distribution (last 30d):
  literature:    2× incomplete, 1× incorrect
  proofread:     1× scope-creep
  figure:        3× excellent
```

Highlight skills with 2+ occurrences of the same negative label — these are candidates for `/feedback-review`.

## Failures-Only Mode

```
/skill-health --failures-only
```

Skip the overview. Show only:
1. All error/partial entries in the period, grouped by skill
2. Error note patterns (cluster similar error messages)
3. Label patterns from ratings (cluster by label type)
4. Suggested investigation order (most frequent failures first)

## Label Reconciliation (signal vs noise vs blind spots)

`skill-health.py` reconciles every logged label against the on-disk skill list (`skills/**/SKILL.md`) and partitions into three buckets so the health table reflects reality, not telemetry noise:

- **Recognized** — logged labels that are real on-disk skills. *Only these populate the health table and the `skills` JSON key* (so downstream consumers like `/feedback-review` get clean input).
- **Blind spots** (`blind_spots`) — on-disk skills with **zero** outcome/observation data. Invisible to health classification; surfaced explicitly so coverage gaps are visible rather than silently absent.
- **Unrecognized labels** (`unrecognized_labels`) — logged names that are **not** on-disk skills: agents (`paper-critic`, `claim-verify`, …) that have their own review-state path, rules logged as skills (`plan-first`, …), renamed/removed skills (`latex-autofix`, `validate-bib`, …), and freeform session labels. Excluded from health; listed with invocation counts for triage.

The text report prints a Coverage line + both lists below the table; `--json` adds `blind_spots`, `unrecognized_labels`, and reconciliation counts under `meta`. Reconciliation is suppressed when `--health`/`--activity`/`--top` filters are active (those are drill-downs, not the full picture).

## Dead Skill Detection

Cross-reference skills in `skills/*/SKILL.md` against invocation logs. Skills with zero invocations over 60+ days are flagged as **dormant**. This is informational — do not auto-deprecate. The user decides whether dormant skills should be archived or are simply awaiting their use case.

## Report Output

Save dashboard reports to `log/audits/skill-health-YYYY-MM-DD.md` for historical tracking.

## What This Skill Does NOT Do

- **Never modifies skill definitions** — that's `/feedback-review`
- **Never auto-deprecates skills** — reports low usage, lets the user decide
- **Never deletes log files** — read-only
- **Never proposes fixes** — reports problems, not solutions

## Integration

| System | Relationship |
|--------|-------------|
| `skill-outcome-logging` rule | Produces outcome data (success/error/partial) |
| `skill-observer` hook | Produces invocation events |
| `/rate` skill | Produces explicit user ratings |
| `quality-score-logger` hook | Produces review agent scores |
| `/feedback-review` | Acts on problems this skill surfaces |
| Weekly system audit (Sat 06:00) | Can invoke this automatically |
| `shared/worker-critic-protocol.md` | Worker-critic pass quality feeds into scores |
