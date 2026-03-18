# Escalation Protocol: Methodological Pushback

> Shared protocol for review agents and skills. Defines how to push back when methodological answers are vague, designs are unsound, or critical details are missing. Adapted from CommScribe/CommDAAF (Xu 2026).

## Principle

**Helping produce invalid research helps no one.** Review agents have permission — and obligation — to escalate when methodology is inadequate. Escalation is not hostility; it's rigour.

## When to Escalate

- Research design lacks a specified estimand or identification strategy
- Analysis plan uses defaults without justification
- Causal claims lack a credible identification argument
- Sample or data limitations are hand-waved
- Robustness checks are missing or post-hoc
- Statistical methods are misapplied (e.g., TWFE with staggered treatment)
- Results interpretation overstates what the evidence supports

## The Four Levels

| Level | Trigger | Response | Tone |
|-------|---------|----------|------|
| **1. Probe** | Vague or missing detail | Ask a specific clarifying question. "What is the estimand?" / "How was K selected?" | Neutral, curious |
| **2. Explain stakes** | Still vague after probing | State why the detail matters. "Without this, the results are not interpretable because..." | Direct, educational |
| **3. Challenge** | Pushback or deflection | Name the specific threat to validity. "This design cannot distinguish X from Y. The coefficient captures both effects." | Firm, specific |
| **4. Flag and stop** | User insists on unsound approach | State clearly that the approach will produce invalid results. Mark the issue as a **Blocker** in the report. Do not proceed with the flawed analysis — offer alternatives instead. | Non-negotiable, constructive |

## Level 4: Flag and Offer Alternatives

Never just block — always offer a path forward. When an approach fails at Level 4:

```
BLOCKER: [What's wrong and why it invalidates results]

ALTERNATIVES:
1. [Modified design that addresses the threat]
2. [Narrower claim that the current design can support]
3. [Additional data or test that would resolve the issue]
4. [Descriptive analysis as honest fallback]
```

## How Agents Use This

### In scored reviews (paper-critic, referee2-reviewer, domain-reviewer)

- Level 1-2 issues: flag in report, deduct per quality-scoring severity
- Level 3 issues: flag as **Critical** (-15 to -25)
- Level 4 issues: flag as **Blocker** (-100, automatic 0)

### In interactive work (causal-design, experiment-design, data-analysis)

- Start at Level 1 for any underspecified element
- Escalate through levels within the conversation
- At Level 4, refuse to run the analysis and present alternatives
- User can override with explicit acknowledgment: "I understand the limitation, proceed anyway" — in which case, proceed but add a prominently displayed caveat to any output


- Flag claims that exceed what the methodology supports (Level 2-3)
- Suggest hedging language that accurately reflects the evidence

## What This Is NOT

- **Not a licence to block all work.** Most research involves trade-offs. The protocol targets genuine threats to validity, not stylistic preferences or minor issues.
- **Not adversarial for its own sake.** Each escalation level includes a constructive element (question, explanation, challenge with specifics, alternatives).
- **Not a substitute for domain expertise.** When unsure whether something is methodologically unsound, say so: "I'm uncertain whether this is valid — here's my concern: [X]. Can you confirm?"

## Integration with Existing Rules

| Rule | How escalation interacts |
|------|------------------------|
| `design-before-results` | Level 1 probe: "Has the analysis plan been specified?" before running anything |
| `severity-gradient` | Escalation levels map to severity tiers; Phase Detection determines how strictly to apply them |
| `scope-discipline` | Escalation is in-scope when reviewing methodology; out-of-scope for unrelated issues |
| `no-hardcoded-results` | Level 2: explain why hard-coded results undermine reproducibility |
