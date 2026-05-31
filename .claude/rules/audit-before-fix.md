# Rule: Audit Before Fix

## Principle

**When running audits, report ALL findings before fixing ANY of them.** Fixing issues one by one without seeing the full picture leads to missed structural problems — redundant directories, inconsistent sub-projects, or cascading issues that a single fix can't address.

## Protocol

### 1. Scan and collect

Run the full audit. Collect all findings into a single report.

### 2. Classify and present

Present findings grouped by severity:
- **Structural anomalies** — redundant directories, missing sub-projects, orphaned files, inconsistent naming
- **Consistency gaps** — mismatched counts, stale references, broken cross-links
- **Convention violations** — files in wrong locations, missing configs, naming issues

### 3. Wait for triage

Let the user review the full list before fixing anything. He may:
- Reprioritise (fix the structural issue first, it might resolve 3 smaller ones)
- Skip some (not worth fixing now)
- Flag things Claude missed (the real problem is X, not Y)

### 4. Fix in order

After triage, fix in the agreed order. Report each fix as completed.

## When This Applies

- `/audit-project-research`, `/atlas-audit`, `/system-audit`
- Any task that involves "check and fix" or "audit and repair"
- When Claude notices multiple issues during routine work

## When to Skip

- Single known issue with explicit fix instruction ("fix the broken symlink at X")
- Compilation errors during `/latex` (fix-compile-retry loop is the design)
- the user says "just fix everything you find"

## Why This Matters

Fixing issues before seeing the full picture caused multiple sessions where Claude fixed all listed items without noticing redundant paper directories or missing sub-project checks — the user had to point out the real structural issue after the surface-level fixes were already applied.

## Failure modes prevented

- **E3** fix-before-inventory — see [`docs/reference/failure-modes.md`](../docs/reference/failure-modes.md)
