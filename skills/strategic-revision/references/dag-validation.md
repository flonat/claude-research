# DAG Validation — Validator Usage

> Detailed usage for the NetworkX-based `dag_validator.py` script. The script is used in two phases of the merged `strategic-revision` skill:
>
> - **Phase 8** — structural gate check (`--validate-only` mode). Confirms the graph is acyclic before Phase 9 sequencing. Fail-fast.
> - **Phase 11** — full computational analysis. Produces parallel batches, critical path, bottlenecks, and block-level validation used to annotate the execution roadmap.
>
> See [phases.md](phases.md) for how these phases fit into the overall protocol.

---

## Prerequisites

- Phase 7 (dependency mapping) must be complete and `plan/revision_tasks.json` must exist
- Python ≥ 3.10 and `networkx` available (`uv pip install networkx`)
- Copy `dag_validator.py` from `skills/strategic-revision/scripts/` into the plan directory before running

---

## Validate-only mode (Phase 8)

Runs a cycle check and exits. Use this to fail fast before investing effort in Phase 9 sequencing.

```bash
cd correspondence/referee-reviews/{venue}-round{n}/plan
python dag_validator.py revision_tasks.json --validate-only
```

Output:
- **PASSED** — graph is acyclic. Proceed to Phase 9.
- **FAILED** — cycle exists. Output shows the cycle path (e.g., `A -> B -> C -> A`).

### If the validator reports a cycle

Return to Phase 7 tables and resolve:

| Common Cause | Fix |
|-------------|-----|
| Collateral risk encoded as hard dependency | Move from `depends_on` to `collateral_risks` — risks are informational, not structural |
| Bidirectional dependency (A blocks B AND B blocks A) | Determine which task truly must come first; remove the reverse edge |
| Transitive chain through merged tasks | Split the merged task into two sequential tasks, or remove the redundant edge |
| Copy-paste error in task IDs | Verify IDs match exactly between `depends_on` references and task keys |

Regenerate `revision_tasks.json` and re-run `--validate-only`. Repeat until PASSED.

Record the outcome in the master plan:

```markdown
### Phase 8: Structural Validation

DAG validated: N tasks, M dependencies, no circular dependencies detected.
Proceed to Phase 9.
```

---

## Full analysis mode (Phase 11)

By this point Phase 9 has assigned execution blocks, so `revision_tasks.json` should have real `block` values (A-E), not `"?"` placeholders.

```bash
# Default output path
python dag_validator.py revision_tasks.json

# Custom output path
python dag_validator.py revision_tasks.json --output my_analysis.json
```

The script produces:
- **Console output** — structured summary (task count, batches, critical path, bottlenecks, block analysis)
- **JSON file** — `revision_dag_analysis.json` with complete analysis data including `impact_details` for high-impact tasks

### If the script fails

| Error | Fix |
|-------|-----|
| File not found | Verify `revision_tasks.json` exists in the working directory |
| Invalid JSON | Check for syntax errors (trailing commas, unquoted keys) |
| Unknown task in `depends_on` | A task references a dependency that does not exist as a key — fix the task ID or add the missing task |
| Cycle detected | Should not occur if Phase 8 passed. If it does, a Phase 9 edit introduced a new dependency. Return to Phase 8 and re-validate. |

---

## Integrating results into the master plan

Read `revision_dag_analysis.json` and add the following subsections to `REVISION_MASTER_PLAN.md` under a "Phase 11" heading.

### Parallel Execution Schedule

From the `parallel_batches` field:

```markdown
### Parallel Execution Schedule (Computationally Derived)

**Batch 1** (N tasks — no prerequisites, can begin immediately):
- task_id_1: description [Block X] CATEGORY
- task_id_2: description [Block X] CATEGORY

**Batch 2** (N tasks — requires Batch 1 completion):
- task_id_3: description [Block X] CATEGORY
...
```

Compare with Phase 9 block assignments. If the computational batches show that tasks from different blocks can run in parallel, note this as an optimization opportunity.

### Critical Path

From the `critical_path` field:

```markdown
### Critical Path (Computationally Derived)

Length: N sequential tasks (minimum revision timeline)

1. task_id_1 — description
2. task_id_2 — description
   ...
N. task_id_N — description

Any delay on these tasks delays the entire revision. Prioritize accordingly.
```

If the computational critical path differs from the Phase 9 manually identified sequence, note the discrepancy and recommend following the computational result.

### Bottleneck Tasks

From the `bottlenecks` field:

```markdown
### Bottleneck Tasks (High Downstream Impact)

| Task | Block | Direct Dependents | Total Downstream | Description |
|------|-------|-------------------|------------------|-------------|
```

Cross-reference with Phase 10 process risks. Bottlenecks that also appear in the risk table carry compounded risk and deserve explicit mitigation strategies.

### Block Validation

From the `block_analysis` field. For each block, report:
- Number of tasks and internal edges
- Whether any tasks have external dependencies on later blocks (which would indicate a block ordering problem)

If the block analysis reveals that a Block C task depends on a Block D task, flag this as a block ordering issue that must be resolved.

---

## Updating the Phase 9 execution roadmap

After integrating Phase 11 results, revise the Phase 9 ASCII execution roadmap:

1. **Annotate critical path tasks** with `[CP]` marker
2. **Annotate bottleneck tasks** with `[BN]` marker
3. **Add parallel execution notes** where batches show tasks from different blocks can run simultaneously
4. **Adjust block boundaries** if computational analysis reveals that the manual block assignments create unnecessary sequential constraints

### Example updated roadmap

```
BLOCK A ─── Empirical Foundation ──────────────────────► GO/NO-GO
  A1: Size control [CP][BN]                                  │
  A2: Analyst coverage [BN]                                  │
  A3: Institutional ownership                                │
  A4: NB/Poisson robustness            ← parallel with A1-A3 │
  A5: Comment letter control                                 │
                                                             ▼
BLOCK B ─── Sub-Analyses & Robustness ─────────────────► New Tables
  B1: Pre/post textual similarity      ← parallel with B2-B6 │
  ...
```

The updated roadmap reflects both the domain-driven block logic (Phase 9) and the computational optimization (Phase 11). Where they agree, confidence is high. Where they disagree, the computational result takes precedence for scheduling purposes, while the domain logic may still be relevant for narrative coherence.
