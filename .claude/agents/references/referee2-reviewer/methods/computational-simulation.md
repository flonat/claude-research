# Computational / Simulation Checklist

> Load when the paper uses: agent-based models, Monte Carlo simulations, numerical experiments, calibrated models, or computational experiments.

## Critical Red Flags

| Issue | What to check | Severity |
|-------|--------------|----------|
| **Overfitting to parameters** | Do results hold only for specific parameter values? Are conclusions driven by calibration choices? | Critical if claims are general but evidence is parameter-specific |
| **Insufficient sensitivity analysis** | One parameter sweep is not enough. All key parameters must be varied, ideally jointly | Major if only univariate sweeps |
| **No empirical validation** | Do simulated patterns match any empirical data? Is there a calibration target? | Major if the paper claims empirical relevance |
| **Convergence not verified** | How do they know the simulation ran long enough? Stationarity checks? | Major |

## Standard Checks

### Model Specification
- [ ] Model assumptions clearly stated and justified
- [ ] Simplifying assumptions acknowledged with discussion of what they rule out
- [ ] Relationship to existing theoretical models clarified
- [ ] Agent decision rules or behavioural assumptions grounded in theory or evidence

### Parameterisation
- [ ] Parameter values sourced (empirically calibrated, literature-derived, or assumed)
- [ ] Baseline parameters clearly distinguished from varied parameters
- [ ] Parameter ranges for sweeps justified (not arbitrary)
- [ ] Key parameters identified and sensitivity to each reported

### Execution
- [ ] Number of replications per configuration reported
- [ ] Random seeds documented (for reproducibility)
- [ ] Convergence diagnostics reported (burn-in, stationarity)
- [ ] Computational cost noted (important for replication feasibility)

### Results
- [ ] Results presented across parameter range, not just "best" configuration
- [ ] Sensitivity analysis covers all key parameters
- [ ] Joint parameter variation (not just one-at-a-time)
- [ ] Summary statistics with confidence intervals across replications
- [ ] Phase transitions or tipping points identified and characterised

### Validation
- [ ] Stylised facts reproduced (if empirically motivated)
- [ ] Out-of-sample validation attempted
- [ ] Comparison to analytical solutions where available
- [ ] Boundary cases tested (extreme parameters, edge conditions)

## Common Mistakes to Flag

1. Presenting results from one parameter configuration as general findings
2. Claiming mechanism discovery from simulation alone (simulation shows *consistency*, not *causation*)
3. Cherry-picking replications or configurations that support the narrative
4. Insufficient replications for stochastic models (N=10 is rarely enough)
5. No code or data availability for replication
6. Conflating model predictions with empirical predictions

## Probing Questions

See `skills/shared/method-probing-questions.md` — section: Simulation / Agent-Based Models.
