# Explore Loop (Adaptive Experiment Protocol)

> Autonomous modify → run → evaluate → keep/discard loop for design space exploration.
> Inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch). Read during Phase 3E.

## When to Use

- Design space is unknown or too large for a pre-specified grid
- You want the agent to adaptively search based on what works
- Simulation parameters, algorithm hyperparameters, or architectural choices need tuning
- User says "explore", "try things", "see what works", "iterate"

## When NOT to Use (Use Phase 3 Instead)

- Design space is well-defined and you want exhaustive coverage → grid sweep
- You need statistical guarantees (all seeds, all configs) → pre-specified sweep
- Results must be reproducible from a single config file → YAML sweep

## Setup

### 1. Branch

```bash
git checkout -b experiments/<tag>
```

Tag convention: `MMMDD-description` (e.g. `mar14-auction-format-search`).

### 2. Results Log

Create `results.tsv` in the project root (tab-separated, NOT comma-separated):

```tsv
commit	metric	metric_name	status	description
```

| Column | Type | Description |
|--------|------|-------------|
| `commit` | string | Short git hash (7 chars) |
| `metric` | float | Primary metric value (0.0 for crashes) |
| `metric_name` | string | What the metric measures (e.g. `val_bpb`, `collusion_rate`, `regret`) |
| `status` | string | `keep`, `discard`, or `crash` |
| `description` | string | Short text describing what this experiment tried |

### 3. Identify Scope

Before starting, determine:

- **Target file(s):** Which file(s) the agent modifies (ideally 1–2 files max)
- **Run command:** How to execute the experiment (e.g. `uv run python src/simulate.py`)
- **Primary metric:** What to optimise (lower or higher is better)
- **Time budget per run:** Wall-clock limit (default: 5 minutes)
- **Experiment budget:** Max number of iterations (default: 20, or "until interrupted")

## The Loop

```
LOOP:
  1. Review results.tsv — what has been tried, what worked, what didn't
  2. Propose a single change to the target file(s)
     - Informed by prior outcomes
     - One change per iteration (never stack untested changes)
  3. Apply the change
  4. git add <target files> && git commit -m "<short description>"
  5. Run: timeout <budget>s uv run python <script> > run.log 2>&1
  6. Extract metric: grep "^<metric_name>:" run.log (or parse output)
  7. Evaluate:
     - If metric improved → STATUS = keep
     - If metric same or worse → STATUS = discard
     - If run crashed → STATUS = crash
  8. Append to results.tsv
  9. If discard or crash → git reset --hard HEAD~1
  10. If crash → read tail of run.log, attempt fix once, else move on
  CONTINUE until: user interrupts, budget exhausted, or stalled
```

### Stall Detection

Stop the loop (and report to user) if:

- **5 consecutive discards** with no keep in between
- **3 consecutive crashes** on different ideas
- **3 consecutive failures on the same approach** — escalate, don't retry (see "3+ Fix Escalation Rule")
- Metric has not improved in the last **10 iterations**

At stall, summarise: "Explored N ideas, K kept, best metric = X. Stalled after M consecutive discards. Consider: changing the search direction, relaxing constraints, or switching to a grid sweep on the promising region."

## Decision Principles

### What to Try

1. **Start with the obvious:** Default parameters, known-good configurations
2. **One variable at a time:** Change one thing, measure, decide
3. **Informed by history:** If increasing X helped, try increasing it more. If approach A crashed, don't retry A.
4. **Alternate exploration and exploitation:** Mix bold changes (new architecture, different algorithm) with refinements (tuning the best-so-far)
5. **Try removals:** Simplifying code/parameters while maintaining metric is a win

### Simplicity Criterion

All else being equal, simpler is better:

- A small improvement that adds significant complexity → likely discard
- Equal metric with fewer parameters/simpler code → keep
- Removing a component with no metric loss → definitely keep

### Crash Handling

- **Trivial fix** (typo, missing import, wrong path): fix and re-run, count as same iteration
- **Fundamental issue** (OOM, algorithmic bug): discard, log as crash, move on
- **Never spend more than 2 attempts** fixing a crashed experiment

### 3+ Fix Escalation Rule

If **3 consecutive iterations fail** (any mix of discard and crash) while trying to make the same kind of change work:

1. **STOP.** Do not attempt fix #4.
2. **Question the approach.** The pattern of repeated failure signals an architectural mismatch, not a parameter tuning problem. Ask:
   - Is the underlying algorithm/environment fundamentally unsuited to this change?
   - Are successive fixes revealing new coupling or shared state problems?
   - Would a different approach achieve the same goal more simply?
3. **Log the escalation** in `results.tsv` with description: `ESCALATION: 3+ failures on <approach> — switched direction`
4. **Switch direction entirely.** Try a fundamentally different idea, not a variation of the failing one.

Signs you're hitting an architectural wall (not just bad parameters):
- Each fix reveals a new problem in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

This rule prevents the most common explore loop failure mode: sinking 10+ iterations into a dead-end approach through incremental tweaks.

## Output

### results.tsv (Example)

```tsv
commit	metric	metric_name	status	description
a1b2c3d	0.450	collusion_rate	keep	baseline — uniform price auction
b2c3d4e	0.380	collusion_rate	keep	switch to discriminatory pricing
c3d4e5f	0.395	collusion_rate	discard	add reserve price (no improvement over discriminatory)
d4e5f6g	0.000	collusion_rate	crash	Vickrey with 100 agents (OOM)
e5f6g7h	0.340	collusion_rate	keep	discriminatory + random tie-breaking
```

### Summary Report

At end of exploration (or on user request), produce:

```markdown
## Explore Summary: <tag>

- **Iterations:** N total (K kept, D discarded, C crashed)
- **Best metric:** X (commit <hash>, "<description>")
- **Baseline:** Y (improvement: Z%)
- **Branch:** experiments/<tag> — current HEAD is best-so-far
- **Key findings:**
  - <What worked and why>
  - <What didn't work>
  - <Suggested next steps — grid sweep on promising region, etc.>
```

## Integration with Other Phases

- **After explore → Phase 3 (sweep):** Use the best configuration found as the centre of a grid sweep for rigorous evaluation
- **After explore → Phase 4 (figures):** Generate plots from `results.tsv` showing exploration trajectory
- **After explore → Phase 5 (audit):** The `results.tsv` + git log provides a full audit trail

## Git Workflow

```
main
  └── experiments/mar14-collusion-params
        ├── commit: baseline
        ├── commit: switch to discriminatory (kept)
        ├── commit: add tie-breaking (kept)
        └── HEAD = best-so-far
```

- The branch accumulates only **kept** changes (discards are reverted)
- `results.tsv` is **untracked** (not committed) — it's the experiment journal
- When exploration is done, optionally merge to main or cherry-pick the best commits
