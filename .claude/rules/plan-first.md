# Rule: Plan Before Implementing

## When This Applies

- Multi-file edits (touching 3+ files)
- New features or significant additions
- Unclear or ambiguous scope
- Refactoring existing code or structure

## When to Skip

- Single-file fixes (typos, one-line bugs)
- Running existing skills (`/proofread`, `/bib-validate`, etc.)
- Informational questions ("What does this function do?")
- Updating context files (`.context/current-focus.md`)

## Assumption Check (Medium Tasks)

For tasks that don't need a full plan but involve choices that could go wrong (1-2 files, clear goal, ambiguous *how*). This is the gap where most "wrong approach" friction occurs.

**When this applies:**
- Edits where output location, format, naming, or convention could be ambiguous
- Any task where you're choosing between options without being told which
- Merging, moving, or renaming files where the target path isn't explicit
- Tasks where scope boundaries are fuzzy ("fix this" — just the bug, or also surrounding issues?)

**What to do:**
Before making changes, state in 2-4 lines:
1. What you're about to do and which files you'll touch
2. Key assumptions (target paths, format, naming conventions, scope boundaries)

Then **wait for confirmation**. One word from the user ("yes", "go", thumbs up) is enough. No saved plan file needed.

**Example assumptions:** "output to `paper/figures/`, not `output/`"; "BBT-format keys from existing .bib"; "Beamer not reveal-md"; "only the 3 lines you mentioned, not the surrounding block".

**Skip the check when:** instruction is fully explicit; direct follow-up where assumptions were already confirmed; the user says "just do it".

## Quick Mode

For experimental/exploratory tasks: skip full planning.

**Triggers:** "quick", "try this", "experiment", "prototype", "just see if", "skip planning"; single-file script exploration.

**What changes:** no plan file, no approval; orchestrator threshold drops to 60/100; must-haves are runs cleanly + correct results + goal documented at top; skip docs/tests/style/session-log.

**What stays:** verification, learn tags, all safety rules. Kill switch: "stop" or "abandon" any time, no cleanup. Escalation: if it succeeds, normal plan-first + orchestrator resumes.

## Protocol

1. **Draft a plan** before writing any code or making changes
2. **Save the plan** — see "Where plans live" below
3. **Get approval** — present the plan to the user and wait for confirmation
4. **Implement via orchestrator** — see `orchestrator-protocol.md` for the verify/review/fix/score loop. For tasks where the orchestrator doesn't apply (see its "When to Skip"), implement directly, noting any deviations.

### Where plans live (two tiers)

In research projects (and any repo where `log/` is gitignored) plans split by durability:

| Tier | Path | Purpose | Tracked? |
|------|------|---------|----------|
| **Working draft** | `log/plans/YYYY-MM-DD_description.md` | Iterating before approval | No (gitignored) |
| **Approved plan** | `docs/plans/YYYY-MM-DD-description.md` | Final, durable across commits/machines/sessions | **Yes** |

**Decision rule:** small/medium plans → write straight to `docs/plans/` once approved. Large multi-phase plans → draft in `log/plans/`, iterate, then distill to `docs/plans/` when approved. Don't keep both indefinitely. The chat checklist (with confirmation) counts as approval; the plan file is the durable artifact.

### Plan Format

Plan template, phase boundaries, dependency notation, mid-pipeline entry, parallel activation, and re-entry/invalidation: `docs/reference/plan-format.md` in Task Management.

## Session Recovery

When starting a new session or after context compression:

1. Read the most recent file in `docs/plans/` (durable, approved plan) — this is the canonical record
2. If none, read the most recent file in `log/plans/` (working draft)
3. Read the most recent file in `log/`
4. Read `.context/current-focus.md`

This provides enough context to continue without re-explaining.

## Execution Stall Detector

When a plan already exists (in `docs/plans/`, `log/plans/`, or stated by the user), enforce execution momentum:

- **2-message rule:** If 2 consecutive messages pass after a plan is confirmed and no file has been edited, STOP reading/auditing and start implementing immediately. Print: "Stall detected — starting execution now."
- **No re-planning approved plans:** Do not re-read, re-audit, or re-draft a plan that the user has already approved. Start from step 1 and make changes.
- **File-edit-first:** When implementing, make the first file change within your next response. Read only the files you need to edit, not the entire project.

This rule exists because planning loops were the single biggest friction source across 232 sessions (53 wrong-approach events, multiple full sessions lost to re-planning without a single edit).

## Important

- **Never `/clear`** — rely on auto-compression to manage context
- Plans are living documents — update them if scope changes mid-implementation
- Quick plans (3-5 lines) are fine for medium tasks; full format for large ones
