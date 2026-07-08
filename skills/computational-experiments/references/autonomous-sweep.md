# Autonomous Sweep — Parallel Self-Correcting Agents

## When to Use

- Large sweep campaigns (10+ configs) where manual debug-fix-rerun cycles waste hours
- Experiments with known failure modes (shape mismatches, degenerate solutions, NaN gradients)
- When the user says "run all experiments autonomously", "hands-off sweep", or "self-correcting"

## Architecture

```
Main context (coordinator)
├── Read sweep configs from experiments/configs/*.yaml
├── Classify configs into batches (max 4 parallel agents)
├── Spawn Agent per batch
│   ├── For each config in batch:
│   │   ├── Run experiment (timeout enforced)
│   │   ├── Check output (correctness assertions)
│   │   ├── If PASS → log success, generate figure
│   │   ├── If FAIL → diagnose → fix → retry (max 3 cycles)
│   │   └── If 3 FAILS → log unresolved, move on
│   └── Write batch results to results/<batch-id>.json
├── Aggregate all batch results
├── Report summary
└── Generate combined figures if all passed
```

## Agent Prompt Template

Each sub-agent receives:

```
You are running experiment batch <N> of <total>.

Configs to run:
<list of config file paths>

For EACH config:

1. Run: `timeout 120s uv run python scripts/run_experiment.py --config <config>`
2. Check stdout/stderr for these failure signatures:
   - "shape mismatch" or "ValueError.*shape" → shape error
   - "empty" or "size 0" → empty array
   - "nan" or "inf" → degenerate solution
   - "KeyError" or "AttributeError" → code bug
   - timeout (exit code 124) → config too expensive
3. If success:
   - Verify output files exist and are non-empty
   - Log: {"config": "<name>", "status": "success", "time_s": <N>}
4. If failure:
   - Read the error, identify root cause
   - Apply a targeted fix (NOT a workaround — fix the actual bug)
   - Commit the fix: git commit -m "fix: <description> for <config>"
   - Re-run (up to 3 attempts total)
   - If still failing after 3 attempts:
     Log: {"config": "<name>", "status": "unresolved", "error": "<type>", "attempts": 3}
5. After all configs: generate figures for successful runs
   - `uv run python scripts/make_figures.py --configs <successful-configs>`

Write ALL results to: results/batch-<N>-results.json

## Scope of action — DO NOT do these things

This sub-agent's authorised scope is exactly: run the assigned configs,
fix legitimate code bugs that block them, commit those fixes, generate
figures for successes, write batch results to the assigned JSON.

Do NOT do any of the following:

- Do NOT edit `.context/`, `MEMORY.md`, `CLAUDE.md`, or any project
  documentation file. The coordinator handles project state.
- Do NOT edit configs in `experiments/configs/` to "make a config work"
  — that changes the experiment, not just fixes a bug. If a config is
  fundamentally broken, log it as `unresolved` and move on.
- Do NOT edit code outside what's needed to fix the specific bug
  blocking your assigned configs. No drive-by refactors, no "while I'm
  here" cleanups in unrelated files.
- Do NOT push (`git push`). Only the coordinator pushes.
- Do NOT run experiments outside your assigned batch.

Stay in your batch. Coordinator decides scope.
```

## Failure Classification

| Signature | Category | Typical fix |
|-----------|----------|-------------|
| `shape mismatch` / `ValueError.*shape` | Data shape | Check array dimensions at creation point |
| `empty` / `size 0` | Empty result | Add guard for degenerate input |
| `nan` / `inf` | Numerical instability | Add epsilon, clip values, check log(0) |
| `KeyError` / `AttributeError` | Code bug | Fix the reference — likely a config key or renamed field |
| Exit code 124 | Timeout | Reduce iterations/budget in config or skip |
| `MemoryError` | OOM | Reduce batch size in config or skip |

## Coordinator Aggregation

After all agents complete:

```python
# Aggregate results
results = []
for batch_file in glob("results/batch-*-results.json"):
    results.extend(json.load(open(batch_file)))

summary = {
    "total": len(results),
    "success": sum(1 for r in results if r["status"] == "success"),
    "fixed": sum(1 for r in results if r.get("attempts", 1) > 1 and r["status"] == "success"),
    "unresolved": sum(1 for r in results if r["status"] == "unresolved"),
    "total_time_s": sum(r.get("time_s", 0) for r in results),
}
```

Present as:
```
Autonomous sweep complete:
  Total configs: N
  Succeeded: N (M required fixes)
  Unresolved: N
  Total time: Xm Ys

Unresolved configs:
  - <config>: <error type> (3 attempts)
```

## Constraints

- **Max 4 parallel agents** — more causes context overflow and diminishing returns
- **Max 3 retry cycles per config** — prevents infinite fix loops
- **Timeout per experiment: 120s default** — override via config `timeout_s` field
- **Agents must NOT modify shared code** simultaneously — each agent's fixes must be on independent code paths. If two agents need to fix the same file, run them sequentially.
- **Commit each fix** — even if later discarded. Git history captures the diagnosis.

## Integration with Existing Modes

| Existing mode | Relationship |
|---------------|-------------|
| **Experiment** (Phase 3) | Sequential sweep — use for small campaigns (<10 configs) |
| **Explore** (Phase 3E) | Adaptive search — use when the design space is unknown |
| **Autonomous** (this) | Parallel sweep with self-correction — use for large known campaigns |

The coordinator should suggest the right mode:
- <10 configs, no known issues → Experiment mode
- Unknown design space → Explore mode
- 10+ configs, or known failure-prone experiments → Autonomous mode
