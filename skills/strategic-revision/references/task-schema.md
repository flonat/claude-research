# Task Schema for DAG Validation

This document specifies the JSON format used by `dag_validator.py`. The file is first generated in Phase 7 (dependency mapping) with `"block": "?"` placeholders, validated in Phase 8 (structural gate check), then updated with block assignments from Phase 9 before the Phase 11 full analysis.

## File: `revision_tasks.json`

A JSON object where each key is a task ID and each value is a task descriptor.

## Schema

```json
{
  "<task_id>": {
    "category": "STRUCTURAL | ARGUMENTATIVE | EMPIRICAL | CLARIFICATION | EDITORIAL",
    "block": "A | B | C | D | E",
    "description": "Short imperative description of the task",
    "depends_on": ["<upstream_task_id>", ...],
    "collateral_risks": [
      {"task_id": "<affected_task_id>", "risk": "Description of the risk"}
    ]
  }
}
```

An optional wrapper format is also accepted:

```json
{
  "tasks": {
    "<task_id>": { ... }
  }
}
```

## Field Definitions

| Field | Type | Required | Source Phase | Notes |
|-------|------|----------|-------------|-------|
| task_id (key) | string | Yes | Phase 1 SourceID | Unique identifier for each task |
| category | string | Yes | Phase 2 | One of: STRUCTURAL, ARGUMENTATIVE, EMPIRICAL, CLARIFICATION, EDITORIAL |
| block | string | Yes | Phase 4 | Execution block letter (A, B, C, D, E) |
| description | string | Yes | Phase 1 | Short imperative action description |
| depends_on | list of strings | Yes (can be `[]`) | Phase 3, Table 1 | Task IDs this task is blocked by |
| collateral_risks | list of objects | No | Phase 3, Table 2 | Tasks that may be affected if this task's results change |

## Task ID Conventions

Use the SourceID from Phase 1 as the basis, adapted for JSON keys:

- Replace dots with underscores: `R1.a1` becomes `R1_a1`
- Optionally prefix with block letter: `A_R1_a1` for a Block A task
- Use consistent format throughout — pick one convention and apply it to all tasks

Examples:
- `EiC_1a`, `R1_b2`, `R2_c1` (simple underscore replacement)
- `A1_size_control`, `C5_integrate_theory` (descriptive, block-prefixed)

Consistency matters more than the specific convention.

## Handling Deduplication

When Phase 1 identified duplicate requests across reviewers (e.g., `R2.c1 = EiC.3a`), use only one task ID for the deduplicated task. Mention both SourceIDs in the description field:

```json
"A_EiC_3a": {
  "category": "EMPIRICAL",
  "block": "A",
  "description": "Add continuous firm size to Model 1 (EiC.3a = R2.c1)",
  "depends_on": []
}
```

## Tasks Without Dependencies

Tasks with no upstream blockers use an empty list: `"depends_on": []`. These appear in Batch 1 (the first parallel execution group) and can begin immediately.

## Collateral Risks

Collateral risks are informational — they do NOT create structural edges in the DAG. The validator stores them as node attributes for reporting but does not use them in cycle detection or topological sorting.

```json
"A1_size_control": {
  "category": "EMPIRICAL",
  "block": "A",
  "description": "Add continuous firm size variable to RQ1",
  "depends_on": [],
  "collateral_risks": [
    {
      "task_id": "C12_null_findings",
      "risk": "If size variable changes Table 3 significance, null-finding explanations need revision"
    }
  ]
}
```

## Worked Example

Given these Phase 3 tables:

**Phase 3, Table 1 — Upstream Blockers:**

| Downstream Task | Blocked By | Rationale |
|-----------------|------------|-----------|
| R1.5 (Rewrite discussion) | R1.2 (New regressions) | Need results before interpretation |
| R2.3 (Update conclusion) | R1.5 (Rewrite discussion) | Conclusion follows discussion |

**Phase 3, Table 2 — Collateral Risks:**

| If You Do This Task | It May Affect | Risk |
|---------------------|---------------|------|
| R1.2 (New regressions) | R1.5 (Rewrite discussion) | New controls may change coefficient significance |

**Phase 2 classifications:** R1.2 = EMPIRICAL, R1.5 = ARGUMENTATIVE, R2.3 = STRUCTURAL

**Phase 4 block assignments:** R1.2 = Block A, R1.5 = Block C, R2.3 = Block D

**Resulting `revision_tasks.json`:**

```json
{
  "A_R1_2": {
    "category": "EMPIRICAL",
    "block": "A",
    "description": "Run new regressions with added controls",
    "depends_on": [],
    "collateral_risks": [
      {
        "task_id": "C_R1_5",
        "risk": "New controls may change coefficient significance"
      }
    ]
  },
  "C_R1_5": {
    "category": "ARGUMENTATIVE",
    "block": "C",
    "description": "Rewrite discussion section with new results",
    "depends_on": ["A_R1_2"]
  },
  "D_R2_3": {
    "category": "STRUCTURAL",
    "block": "D",
    "description": "Update conclusion to match revised discussion",
    "depends_on": ["C_R1_5"]
  }
}
```

This produces a DAG with critical path: `A_R1_2 -> C_R1_5 -> D_R2_3` (3 tasks, 1 parallel batch per task).
