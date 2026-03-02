# Computational Many-Analysts

> How the many-analysts design relates to multi-perspective analysis, when to combine them, and the verification hierarchy. Read when deciding between qualitative perspective diversity and quantitative specification diversity.

## Multi-Perspective vs Many-Analysts

These are complementary, not competing, approaches to robustness:

| Dimension | Multi-Perspective | Many-Analysts |
|-----------|------------------|---------------|
| **Question** | "Should we use DiD at all?" | "Given DiD, how sensitive is the ATT to covariate choice?" |
| **What varies** | Disciplinary lens, theoretical framework, method preference | Implementation choices within a fixed method |
| **Nature of diversity** | Qualitative — different ways of seeing | Quantitative — different specifications of the same model |
| **Output** | Agreement/tension map, blind spots | Forest plot, spread-to-SE ratio |
| **When in pipeline** | Early — before committing to an approach | Late — after locking the estimator, before submission |
| **Agent design** | Personas with distinct priors | Identical instructions, independent isolation |

**Key distinction:** Multi-perspective agents are deliberately given different epistemic priors (behavioural economist vs econometrician vs sociologist). Many-analyst agents receive identical instructions and differ only through emergent discretionary choices.

## When to Combine

Use `/multi-perspective` first, then many-analysts:

1. **Stage 1 — Multi-Perspective:** "What identification strategy should we use for this policy evaluation?" Spawn disciplinary perspectives to debate DiD vs synthetic control vs IV.
2. **Lock the approach** based on the synthesis (agreements, resolved tensions).
3. **Stage 2 — Many-Analysts:** "Given DiD with Callaway & Sant'Anna, how sensitive is the ATT to covariate choice?" Run N isolated agents on the same dataset with the locked estimator.
4. **Report both:** The multi-perspective analysis justifies the methodological choice; the many-analysts spread quantifies remaining researcher degrees of freedom.

**When NOT to combine:**
- If the method choice is uncontested (e.g., randomised experiment → just run many-analysts on specification choices)
- If you're at the conceptual stage and haven't collected data yet (multi-perspective only)
- If the only question is "does my code run correctly?" (neither — use `/code-review`)

## The Convex Cost Problem

Cunningham (2026, Post 21) observes that AI productivity gains are superlinear in mess:

> "5x productivity → >5x mess."

**Stock pollutants** grow convex: excess files, duplicate outputs, hard-coded results, branching pipelines. Each additional agent run adds output that must be verified, organised, and synthesised.

**Three binding constraints in human-AI research:**

| Constraint | Description | Implication |
|------------|-------------|-------------|
| **Verification** | Human must check that agent output is correct | Scales linearly at best; often sublinearly as fatigue sets in |
| **Attention** | Resist automating the learning process itself | Running 15 agents is easy; understanding why they diverged is hard |
| **Congestion** | Finding things in your own output | More agents = more output directories, more figures, more specs to track |

**For many-analysts designs:** The value is in the diagnostic (forest plot, covariate heatmap), not in the individual outputs. Design the pipeline to produce the diagnostic automatically — don't manually inspect each agent's work.

## Verification Hierarchy

Karpathy's claim: "The new skill is verification, not generation." This creates a natural hierarchy of verification tools:

| Level | Tool | What it checks | Cost |
|-------|------|----------------|------|
| 1. Code correctness | Multi-language audit (R + Python + Stata) | Same specification → same estimate across languages | Medium |
| 2. Specification sensitivity | Many-analysts design | Same estimator → estimate spread across specification choices | Medium-high |
| 3. Method sensitivity | Multi-perspective analysis | Different disciplines → different recommended approaches | High |
| 4. Adversarial review | `referee2-reviewer` agent | Everything a hostile reviewer could exploit | High |

Each level subsumes the one below: if agents can't reproduce the same estimate across languages (Level 1), there's no point measuring specification sensitivity (Level 2).

**Standard reporting:** Include the forest plot from Level 2 in the robustness appendix. Reference the multi-perspective synthesis in the methodology discussion. Adversarial review (Level 4) is a pre-submission internal tool, not reported.

## Connection to Council Mode

The `/multi-perspective` council mode (using `cli-council` with multiple LLM providers) adds genuine model diversity on top of persona diversity. The many-analysts design adds specification diversity on top of that. They operate on different axes:

| Axis | What varies | Tool |
|------|-------------|------|
| Model diversity | LLM provider (Claude, GPT, Gemini) | Council mode |
| Persona diversity | Disciplinary lens and epistemic prior | `/multi-perspective` standard mode |
| Specification diversity | Implementation choices within a fixed method | Many-analysts design |

All three can run on the same research question, each contributing a different kind of robustness evidence.
