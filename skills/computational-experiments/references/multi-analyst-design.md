# Multi-Analyst Design

> Many-analysts as a robustness diagnostic: same data + estimator, controlled discretion points, compare estimate spread. Read when designing robustness checks or quantifying researcher degrees of freedom.

## Concept

A many-analysts design runs N independent analysts on the same dataset and research question, then compares estimates. The spread across analysts quantifies **researcher degrees of freedom** — how much the result depends on implementation choices rather than the data.

Traditional many-analysts studies (Silberzahn et al. 2018, Huntington-Klein et al. 2021) recruit human teams. The computational variant replaces human analysts with isolated AI agents, collapsing marginal cost to near zero while preserving the key property: each analyst makes independent discretionary choices.

**When to use:**
- After locking the main specification, as a robustness appendix
- Before submission, to quantify how sensitive results are to implementation choices
- When a reviewer might ask "would different researchers get the same answer?"
- To identify which discretionary nodes drive the most variation

**When NOT to use:**
- As a substitute for a pre-registered analysis plan (this is diagnostic, not confirmatory)
- When the estimator itself is contested (use `/multi-perspective` for that)
- For exploratory analysis where the research question isn't yet fixed

## Isolation Protocol

Each agent must be fully independent — no shared memory, no access to other agents' output.

**Setup (from Cunningham 2026):**

```bash
# Create N isolated temp directories
for i in $(seq 1 $N); do
    WORKDIR=$(mktemp -d)
    cp data.csv "$WORKDIR/"
    cp instructions.md "$WORKDIR/"
    # Launch agent in isolation
    cd "$WORKDIR" && claude -p "$(cat instructions.md)" > output_$i.md &
done
wait
```

**Key isolation requirements:**
- Each agent runs in its own temp directory
- No shared history, memory, or context files
- One instructions file per agent (same file for all)
- Prior agent outputs archived before next launch (if running sequentially)
- No access to the researcher's own analysis or preferred specification

**Instructions file should specify:**
- Dataset and variable descriptions
- Research question and estimand
- Estimator family (e.g., "use Callaway & Sant'Anna DiD")
- What to report (point estimate, SE, confidence interval, specification details)

**Instructions file should NOT specify:**
- Which covariates to include
- Trimming rules
- Specific software package
- Any implementation choice you want to measure variation on

## Discretionary Nodes

A discretionary node is any implementation choice where reasonable analysts might disagree. The many-analysts design reveals which nodes drive variation.

**Cunningham's DiD experiment (15 agents, Callaway & Sant'Anna):**

| Decision | Agreement | Notes |
|----------|-----------|-------|
| Control group (not-yet-treated) | 15/15 | Structural — follows from estimator choice |
| Base period (universal) | 15/15 | Structural |
| Balanced cohorts | 15/15 | Structural |
| Trimming | 15/15 | Structural |
| Doubly robust estimator | 15/15 | Structural |
| **Covariate selection** | **Varied** | **Drove all estimate variation** |

**Covariate inclusion rates:**

| Covariate | Included by | Rate |
|-----------|-------------|------|
| Log GDP per capita | 14/15 | 93% |
| Population | 12/15 | 80% |
| Poverty rate | 10/15 | 67% |
| Health spending | 7/15 | 47% |
| Bolsa Familia | 2/15 | 13% |
| Geographic variables | 1/15 | 7% |

**Key finding:** Structural decisions were unanimous. All variation came from covariate selection — specifically, where agents drew the confounder/mediator boundary. Same reasoning framework, different thresholds for inclusion.

**Common discretionary nodes by estimator:**

| Estimator | Key discretionary nodes |
|-----------|----------------------|
| DiD (CS) | Covariates, control group definition, base period, trimming |
| IV | Instrument choice, first-stage specification, weak instrument threshold |
| RDD | Bandwidth, kernel, polynomial order, donut hole |
| Synthetic control | Donor pool, matching variables, pre-treatment period |
| OLS | Control variables, functional form, sample restrictions |

## Output Diagnostics

### Forest Plot

The primary output: each agent's point estimate ± CI, ordered by magnitude, with the pooled estimate shown.

```
Agent 1  |----●----|
Agent 2     |---●---|
Agent 3  |------●------|
...
Pooled        |--●--|
```

Generate with the standard figure pipeline (`scripts/make_all_figures.py` → `paper/figures/`).

### Covariate Heatmap

Binary matrix: agents × covariates. Reveals clustering in covariate choice and correlates with estimate ordering.

### Spread-to-SE Ratio

From Huntington-Klein et al. (2021): compare the standard deviation of estimates across analysts to the average standard error reported by each analyst.

```
spread_to_SE = SD(point_estimates) / mean(standard_errors)
```

- **Ratio ≈ 1:** Reported uncertainty captures true uncertainty (good)
- **Ratio >> 1:** Researcher degrees of freedom contribute more uncertainty than sampling variation (concerning)
- Huntington-Klein found SD was 3-4x the average SE in their economics experiment

### Per-Package Comparison

If agents use different software packages (e.g., Stata's `csdid` vs R's `did`), compare estimates within and across packages to separate software effects from specification effects.

## Literature

| Paper | Design | Key finding |
|-------|--------|-------------|
| Silberzahn et al. (2018) | 29 teams, soccer red cards | Same data → estimates ranged from "no effect" to "large effect"; 69% found significant |
| Huntington-Klein et al. (2021) | 7 economists, same dataset | SD of estimates was 3-4x the average SE; huge variation in specification choices |
| Menkveld et al. (2024) | "Non-standard errors" — 164 teams | Documented systematic variation across analyst teams in finance |
| Borjas & Breznau (2025) | Immigration & wages | Political ideology predicted the sign of estimated effects |
| Cunningham (2026, Substack) | 15 AI agents, DiD | First computational many-analysts design; covariate selection drove all variation |

## Connection to Existing Infrastructure

The many-analysts design uses the same **sweep/runner pattern** from `experiment-patterns.md`, but with agent isolation instead of seed variation:

| Dimension | Standard sweep | Many-analysts |
|-----------|---------------|---------------|
| What varies | Seeds, hyperparameters | Analyst discretion (covariates, specification) |
| What's fixed | Algorithm, config | Data, estimand, estimator family |
| Isolation | Per-seed RNG | Per-agent temp directory |
| Output | Convergence curves | Forest plot, covariate heatmap |
| Aggregation | Mean ± std across seeds | Spread-to-SE ratio, inclusion rates |

The runner infrastructure (config → run → collect → aggregate) applies directly. The key difference is that variation comes from agent discretion rather than stochastic seeds.
