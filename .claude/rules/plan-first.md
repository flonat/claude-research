# Rule: Plan Before Implementing

## When This Applies

- Multi-file edits (touching 3+ files)
- New features or significant additions
- Unclear or ambiguous scope
- Refactoring existing code or structure

## When to Skip

- Single-file fixes (typos, one-line bugs)
- Running existing skills (`/proofread`, `/validate-bib`, etc.)
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

**Examples of assumptions worth stating:**
- "I'll write output to `paper/figures/`, not `output/`"
- "I'll use Paperpile-format keys from the existing .bib"
- "I'll compile with Beamer, not reveal-md"
- "I'll edit only the 3 lines you mentioned, not the surrounding block"
- "I'll put the report in the current project directory, not the Research Projects root"

**When to skip the assumption check:**
- the user's instruction is fully explicit (exact file paths, exact format, exact scope)
- The task is a direct follow-up where assumptions were already confirmed
- the user says "just do it" or similar

## Quick Mode

When the task is clearly experimental or exploratory, skip the full planning protocol.

**Triggers** (any of these):
- the user says "quick", "try this", "experiment", "prototype", "just see if"
- Task is a single-file script exploration or simulation test
- the user explicitly says "skip planning"

**What changes:**
- Skip plan-first (no plan file, no approval step)
- Orchestrator still runs but threshold drops to 60/100 (vs 80/90 normally)
- Must-haves: code runs, results are correct, goal documented in a comment at the top
- Not needed: docs, tests, perfect style, session log

**What stays:** Verification (code must run), learn tags, all safety rules.

**Kill switch:** the user can say "stop" or "abandon" at any point — no guilt, no cleanup needed.

**Escalation:** If the exploration succeeds and the user wants to build on it, normal plan-first + orchestrator rules resume.

## Protocol

1. **Draft a plan** before writing any code or making changes
2. **Save the plan** to `log/plans/YYYY-MM-DD_description.md`
3. **Get approval** — present the plan to the user and wait for confirmation
4. **Implement via orchestrator** — see `orchestrator-protocol.md` for the verify/review/fix/score loop. For tasks where the orchestrator doesn't apply (see its "When to Skip"), implement directly, noting any deviations.

### Plan Format

```markdown
# Plan: [Short Description]

## Context
[Why this is needed]

## Changes
[List of files to create/modify with brief descriptions]

## Order of Operations
1. Write session log (`/session-log`)
2. Update project context (`/update-focus` or `/save-context`)
3. [Implementation steps...]

## Risks / Open Questions
[Anything that could go wrong or needs clarification]
```

## Phase Boundaries

When a plan spans 2+ distinct activities (e.g., code + experiments + writing), split into phases with explicit stop points:

1. Each phase gets its own session (or section of a session)
2. At each phase boundary, create `HANDOFF.md` in the project root summarising:
   - What was accomplished
   - What outputs exist and where
   - What the next phase should use
3. Run `/session-log` at each boundary, not just at session end
4. Do NOT start the next phase without the user's go-ahead

Signs a plan needs phases: 5+ implementation steps, multiple distinct tool chains (Python + LaTeX), or estimated context usage that could hit compression.

## Session Recovery

When starting a new session or after context compression:

1. Read the most recent file in `log/plans/`
2. Read the most recent file in `log/`
3. Read `.context/current-focus.md`

This provides enough context to continue without re-explaining.

## Execution Stall Detector

When a plan already exists (in `log/plans/` or stated by the user), enforce execution momentum:

- **2-message rule:** If 2 consecutive messages pass after a plan is confirmed and no file has been edited, STOP reading/auditing and start implementing immediately. Print: "Stall detected — starting execution now."
- **No re-planning approved plans:** Do not re-read, re-audit, or re-draft a plan that the user has already approved. Start from step 1 and make changes.
- **File-edit-first:** When implementing, make the first file change within your next response. Read only the files you need to edit, not the entire project.

This rule exists because planning loops were the single biggest friction source across 232 sessions (53 wrong-approach events, multiple full sessions lost to re-planning without a single edit).

## Important

- **Never `/clear`** — rely on auto-compression to manage context
- Plans are living documents — update them if scope changes mid-implementation
- Quick plans (3-5 lines) are fine for medium tasks; full format for large ones
