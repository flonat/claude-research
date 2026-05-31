---
paths:
  - "**/*.tex"
  - "**/*.py"
  - "**/*.R"
---

# Rule: Spec Compliance Before Quality Review

## Principle

**Validate that the specification is met before assessing quality.** A beautifully written paper with the wrong estimand is worse than a rough draft with the right one. Spec compliance is a prerequisite for quality review — never reverse the order.

## The Two-Stage Gate

| Stage | Question | Agent/Check | Blocks if failed |
|-------|----------|-------------|-----------------|
| **1. Spec compliance** | "Did we do what was asked?" | Check against locked design/brief | Yes — quality review is meaningless on wrong spec |
| **2. Quality review** | "Did we do it well?" | `paper-critic`, `proofread`, `code-review` | Depends on severity |

## What Counts as "Spec"

| Context | The spec is... |
|---------|---------------|
| Research paper | Locked estimand, identification strategy, analysis plan (per `design-before-results` rule) |
| Coursework/submission | Assessment brief requirements (word count, structure, marking criteria) |
| Code implementation | The agreed plan in `log/plans/` or the user's explicit instructions |
| Presentation | The agreed outline, audience, and key messages |
| Skill/agent creation | The user's stated requirements and trigger conditions |

## When This Applies

- Before running `paper-critic`, `proofread`, or `pre-submission-report` on a research paper — first verify the estimand and methodology match the locked design
- Before running `brief-compliance-check` — the brief IS the spec, so this skill already embodies Stage 1
- Before running `code-review` — first verify the code implements the agreed plan, not a different approach
- When the orchestrator protocol reaches the review step — spec check is a pre-gate

## When to Skip

- No spec exists yet (exploratory/discovery phase) — quality review alone is fine
- The task is mechanical (compilation, formatting, bibliography) — no spec to validate
- the user explicitly says "just check quality, spec is fine"

## How to Apply

1. Before launching a quality review agent, ask: **"Is there a locked spec for this work?"**
2. If yes, verify the output matches it (estimand correct? brief requirements met? plan followed?)
3. If spec is violated, **stop and flag** — do not proceed to quality review
4. If spec is met, proceed to quality review normally

## Why This Matters

Quality review on the wrong spec legitimises scope creep. A reviewer who grades polish on a paper with the wrong estimand implicitly validates the wrong estimand. Separating the two stages prevents this — and catches design drift before it's buried under layers of editorial polish.
