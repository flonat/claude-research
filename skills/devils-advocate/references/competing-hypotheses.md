# Competing Hypotheses Checklist

Structured process for generating and evaluating rival explanations before locking a research design. Complements the `design-before-results` rule (`.claude/rules/design-before-results.md`) by specifying HOW to formulate competing explanations, not just that you should. Adapted from K-Dense's hypothesis-generation skill and quality criteria framework.

## When to Use

- Before locking a research design (pre-registration, analysis plan)
- When `/devils-advocate` is invoked on a research question
- During early-stage paper planning (idea -> literature review transition)
- When reviewing a paper that presents only one explanation

## The 3-Step Process

### Step 1: Generate 3-5 Competing Hypotheses

Each hypothesis must provide a **mechanistic explanation** -- specify HOW and WHY the effect occurs, not just WHAT happens.

**Requirements:**
- Each must be distinguishable from the others (different mechanisms, not different magnitudes)
- Include at least one "null" or status-quo explanation (e.g., "observed pattern is an artefact of selection")

**Generation strategies:**
- Apply known mechanisms from analogous settings (e.g., anchoring from behavioural econ to MCDM)
- Consider different levels of explanation: individual (cognitive) -> group (social) -> market (structural) -> institutional (regulatory)
- Question existing assumptions: what if the causal direction is reversed? What if it is confounded?
- Combine mechanisms in novel ways (e.g., bounded rationality + social conformity)

### Step 2: Evaluate Against 7 Quality Criteria

| Criterion | Definition | H1 | H2 | H3 | H4 | H5 |
|-----------|-----------|----|----|----|----|-----|
| **Testability** | Can it be empirically tested with available methods? | | | | | |
| **Falsifiability** | What specific observations would disprove it? | | | | | |
| **Parsimony** | Is it the simplest explanation consistent with evidence? | | | | | |
| **Explanatory power** | How much of the phenomenon does it account for? | | | | | |
| **Scope** | Does it generalise beyond the specific case? | | | | | |
| **Consistency** | Does it align with established theory and evidence? | | | | | |
| **Novelty** | Does it offer new insight beyond existing accounts? | | | | | |

Rate each cell as **Strong** / **Moderate** / **Weak**.

Hypotheses scoring Weak on Testability or Falsifiability should be revised or dropped.

### Step 3: Design Distinguishing Tests

- For each pair of hypotheses (H_i, H_j), identify at least one prediction where they diverge
- Prioritise predictions that are most feasible to test (data availability, ethical constraints, cost)
- Identify "critical experiments" that eliminate the most hypotheses simultaneously
- Format: "If H1 is correct but H2 is not, we should observe X but not Y"

## Common Pitfalls

- **Just-so stories:** plausible narrative without testable predictions -- if you cannot specify what would falsify it, it is not a hypothesis
- **Unfalsifiable claims:** built-in escape clauses ("it depends on context", "moderating factors may apply")
- **Single-hypothesis lock-in:** committing to one explanation before considering alternatives, then seeking only confirmatory evidence
- **Over-complexity:** invoking unnecessary mechanisms when a simpler account suffices (violates parsimony)

## Worked Example

**Research question:** Why do decision-makers deviate from optimal stopping rules in sequential search (e.g., hiring, investment screening)?

**Competing hypotheses:**

- **H1 (Cognitive load):** Tracking running optima exceeds working-memory capacity; DMs fall back on satisficing heuristics. Mechanism: individual-level cognitive constraint.
- **H2 (Social accountability):** DMs stop early to justify choices to stakeholders ("I chose the best I saw") rather than risk continued search with uncertain payoff. Mechanism: group-level social pressure.
- **H3 (Null -- rational adaptation):** Deviations reflect rational updating given non-stationary option quality or unknown distributions; no bias is present. Mechanism: Bayesian learning under uncertainty.

| Criterion | H1 | H2 | H3 |
|-----------|-----|-----|-----|
| Testability | Strong | Strong | Moderate |
| Falsifiability | Strong | Strong | Weak |
| Parsimony | Strong | Moderate | Strong |
| Explanatory power | Moderate | Moderate | Moderate |
| Scope | Strong | Moderate | Strong |
| Consistency | Strong | Strong | Strong |
| Novelty | Weak | Moderate | Weak |

**Distinguishing predictions:**

- **H1 vs H2:** Manipulate accountability (solo vs committee decision). If H1 dominates, deviation rates are unchanged; if H2, deviations decrease when accountability is removed.
- **H1 vs H3:** Vary cognitive load (dual-task paradigm). If H1, higher load increases deviation; if H3, load is irrelevant.
- **H2 vs H3:** Provide full distributional information. If H3, deviations disappear with known distributions; if H2, they persist because the social motive remains.
- **Critical test:** Dual-task + no-accountability + known-distribution condition -- eliminates all three simultaneously.
