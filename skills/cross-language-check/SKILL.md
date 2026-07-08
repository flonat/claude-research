---
name: cross-language-check
description: "Use when you need to replicate a quantitative analysis in a second language (R↔Python↔Stata↔Julia) to verify correctness. Level 1 of the verification hierarchy."
allowed-tools: Bash(uv*, Rscript*, stata*, julia*, diff*, mkdir*, ls*, cp*), Read, Write, Edit, Glob, Grep, Agent
argument-hint: "<script-path> [--target r|python|stata|julia]"
---

# Cross-Language Replication Check

> Level 1 of the verification hierarchy: same specification → same estimate across languages. If two independent implementations disagree, at least one has a bug.

## Output Path

Per `rules/review-artefact-routing.md` (auto-loads in research projects (path-scoped to `paper-*/` and `paper/`)):

- **Source slug:** `cross-language-check`
- **Write reports to:** `reviews/<scope>/cross-language-check/<YYYY-MM-DD-HHMM>.md` inside the project, where `<scope>` is the paper slug (e.g., `paper-jtp`) for paper-level checks or `_project` for project-level checks. Path is relative to the research project root, not the Task-Management repo.
- **Never** at project root (`./CRITIC-REPORT.md`-style filenames are forbidden — pre-rule layout).
- **Idempotency:** if today's file exists, append a same-day descriptor (`{date}-revision.md`, `{date}-r2.md`, `{date}-pre-submission.md`) — never overwrite.
- **Index update:** if `reviews/INDEX.md` exists, write a one-line entry under "Latest per source" pointing at the new file. Otherwise `/review-recap` will rebuild the index next time it runs.
- **Infrastructure repos** (Task-Management, atlas-workspace, etc.): this section does not apply — the path-scoped rule won't load there.


## When to Use

- Before submitting a paper with quantitative results
- When you suspect a subtle bug in estimation code
- After refactoring analysis scripts
- As a robustness check that reviewers increasingly expect
- When switching languages for a collaborator

## When NOT to Use

- Pure simulation code with no statistical estimation → `/computational-experiments`
- The analysis is trivial (descriptive stats only) — not worth the overhead
- The source script uses language-specific packages with no equivalent (e.g., bespoke Bayesian MCMC)

## Workflow

### Phase 1: Parse Source Script

1. **Read the source script** — identify language, packages, estimation calls
2. **Extract the specification:**
   - Data loading and cleaning steps
   - Variable construction and transformations
   - Estimation command(s) with exact formula/model specification
   - Standard error clustering, weights, fixed effects
   - Sample restrictions and filters
3. **Identify key outputs** — point estimates, standard errors, p-values, confidence intervals, N
4. **Flag untranslatable elements** — language-specific features that may need adaptation (e.g., R formula syntax, Stata factor variables, Python sklearn pipelines)

### Phase 2: Choose Target Language

If `--target` is specified, use that. Otherwise:

| Source | Default target | Rationale |
|--------|---------------|-----------|
| R | Python | Widest package overlap |
| Python | R | Strongest econometrics ecosystem |
| Stata | R | Both strong on panel/causal methods |
| Julia | Python | Closest syntax mapping |

Ask the user to confirm if the default seems wrong for the specific analysis.

### Phase 3: Translate

Write the replication script to `code/replication/` (or `src/replication/`):

```
code/replication/{original_name}_{target_lang}.{ext}
```

Translation rules:
1. **Mirror the specification exactly** — same formula, same controls, same sample restrictions
2. **Use equivalent packages** (see `shared/multi-language-conventions.md` for mappings)
3. **Match output format** — both scripts should produce a CSV with columns: `estimate`, `se`, `pvalue`, `ci_lower`, `ci_upper`, `n`, `model_label`
4. **Document every adaptation** — comment blocks explaining where the translation required judgment calls
5. **Use the same data file** — both scripts read from the same cleaned dataset

### Phase 4: Run Both & Compare

1. Run the source script, capture output CSV
2. Run the replication script, capture output CSV
3. **Comparison thresholds:**

| Metric | Threshold | Verdict |
|--------|-----------|---------|
| Point estimates | Differ by < 0.1% | PASS |
| Point estimates | Differ by 0.1–1% | WARN — likely rounding or optimizer differences |
| Point estimates | Differ by > 1% | FAIL — investigate |
| Standard errors | Differ by < 1% | PASS |
| Standard errors | Differ by 1–5% | WARN — check SE type (robust, clustered, HC1 vs HC3) |
| Standard errors | Differ by > 5% | FAIL — likely different SE computation |
| Sample size N | Must be identical | FAIL if different — data filtering diverged |

4. **Generate comparison table** saved to `code/replication/comparison.md`:

```markdown
| Model | Estimate (source) | Estimate (replica) | Diff (%) | SE (source) | SE (replica) | Diff (%) | N match | Verdict |
```

### Phase 5: Diagnose Discrepancies

If any FAIL or WARN:

1. **Check N first** — if sample sizes differ, the data pipeline diverged (most common source of bugs)
2. **Check SE type** — HC1 vs HC3 vs clustered vs bootstrap defaults differ across languages
3. **Check optimizer** — MLE/GLM may converge to different optima with different starting values
4. **Check missing value handling** — `NA` dropping rules differ (R drops per-variable, Stata drops listwise, Python varies)
5. **Check factor variable encoding** — reference category defaults differ across languages

Report the root cause, not just the symptom.

### Phase 6: Report

Save to `code/replication/cross-language-report.md`:

```markdown
# Cross-Language Replication Report

**Source:** {source_path} ({source_language})
**Replica:** {replica_path} ({target_language})
**Date:** {date}

## Summary
- Models checked: N
- PASS: N | WARN: N | FAIL: N

## Comparison Table
[from Phase 4]

## Discrepancies
[from Phase 5, if any]

## Verdict
[REPLICATED | REPLICATED WITH NOTES | FAILED — action required]
```

## Common Package Mappings

| Task | R | Python | Stata | Julia |
|------|---|--------|-------|-------|
| OLS + FE | `fixest::feols` | `linearmodels.PanelOLS` | `reghdfe` | `FixedEffectModels.reg` |
| IV | `fixest::feols` (iv syntax) | `linearmodels.IV2SLS` | `ivregress 2sls` | `FixedEffectModels.reg` |
| DiD | `did::att_gt` | `differences` | `csdid` | — |
| Clustered SE | `vcov = ~cluster` | `cov_type='clustered'` | `vce(cluster var)` | `Vcov.cluster(:var)` |
| Logit/Probit | `glm(family=binomial)` | `statsmodels.Logit` | `logit` | `GLM.jl` |

## Log to REVIEW-STATE.md (final step)

Write the comparison report to `reviews/<scope>/cross-language-check/<YYYY-MM-DD-HHMM>.md` (where `<scope>` is the paper slug for paper-level checks or `_project` for project-level checks; `mkdir -p reviews/<scope>/cross-language-check/` first). Then append a row to the project's `REVIEW-STATE.md`:

```bash
bash ~/.claude/skills/_shared/review-state-log.sh \
  --check cross-language-check \
  --paper "<paper-{venue} dir, or — for project-level cross-language checks>" \
  --verdict "<MATCH|DIVERGENCE>" \
  --score "<pass-count>/<total-comparisons>" \
  --open-issues "<fail-count>/<total-comparisons>" \
  --report "reviews/<scope>/cross-language-check/<YYYY-MM-DD-HHMM>.md" \
  --notes "<one-line: e.g. 'all match within tol'; or 'IV SE differs in §4'>" \
  [--trigger "pre-submission-report|review-cluster"]
```

- Verdict: MATCH if every comparison passes (within tolerance); DIVERGENCE if any FAIL.
- Score: PASS count / total comparisons.
- Open issues: FAIL count / total at run time.
- Trigger: pass orchestrator name only if invoked as a sub-agent. Otherwise omit.

Schema: `~/Task-Management/docs/reference/review-state-schema.md`.

## Cross-References

| Resource | When read |
|----------|-----------|
| `shared/multi-language-conventions.md` | Phase 3 (language-specific style) |
| `multi-perspective/references/computational-many-analysts.md` | Context (verification hierarchy) |
| `/code-review` skill | Phase 6 (optionally review both scripts) |
| `/replication-package` skill | After (include both scripts in replication materials) |
