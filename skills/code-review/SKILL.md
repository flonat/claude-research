---
name: code-review
description: "Quality review for R and Python research scripts. 11-category scorecard covering reproducibility, structure, domain correctness, cross-language verification, and more. Report-only — never edits source files."
allowed-tools: Read, Glob, Grep
argument-hint: [script-path or project-path]
---

# Research Code Review

**Report-only skill.** Never edit source files — produce `CODE-REVIEW-REPORT.md` only.

## When to Use

- Before submitting a paper (check replication package quality)
- After writing analysis scripts and before sharing with coauthors
- When taking over someone else's research code
- As part of the Referee 2 agent's formal audit pipeline

## When NOT to Use

- **Understanding old code** — use `/code-archaeology` first to map out what exists
- **Formal verification** — use the Referee 2 agent for cross-language replication
- **General software projects** — this is for research scripts, not applications

## Workflow

1. **Locate scripts**: Find all `.R`, `.py`, `.do`, `.jl` files in the project
2. **Read each script** carefully
3. **Score each category** (Pass / Fail / N/A)
4. **Produce report**: Write `CODE-REVIEW-REPORT.md` in the project directory

## 11 Review Categories

### 1. Reproducibility

| Check | Pass Criteria |
|-------|--------------|
| Random seeds | `set.seed()` / `random.seed()` / `np.random.seed()` set before any stochastic operation |
| Relative paths | No hardcoded absolute paths (e.g., `/Users/username/...` or `C:\...`) |
| Working directory | Script does not `setwd()` / `os.chdir()` — uses project-relative paths |
| Session info | Script prints session info at end (`sessionInfo()` / `sys.version`) or documents environment |

### 2. Script Structure

| Check | Pass Criteria |
|-------|--------------|
| Header | Script begins with comment block: purpose, author, date, inputs, outputs |
| Sections | Code organised into labelled sections (comments or `# ---- Section ----`) |
| Imports at top | All `library()` / `import` statements at the top of the file |
| Reasonable length | Single script < 500 lines; longer scripts should be split |

### 3. Output Hygiene

| Check | Pass Criteria |
|-------|--------------|
| No print pollution | No stray `print()` / `cat()` / `message()` dumping to console |
| Outputs saved | Key results saved to files, not just printed |
| Clean console | Running the script does not produce walls of text |

### 4. Function Quality

| Check | Pass Criteria |
|-------|--------------|
| Documentation | Functions have comments explaining purpose, inputs, outputs |
| Naming | Function names are descriptive verbs (`estimate_ate`, not `f1`) |
| Defaults | Reasonable defaults for optional parameters |
| No side effects | Functions don't modify global state |

### 5. Domain Correctness

| Check | Pass Criteria |
|-------|--------------|
| Estimator matches paper | The estimator used matches what the paper claims |
| Weights | If weighted: weights sum to expected value, correct application |
| Standard errors | Clustering / HC / bootstrap matches paper specification |
| Sample restrictions | Filters match the paper's sample description |
| Variable construction | Variables constructed as described in the paper |

### 6. Figure Quality

| Check | Pass Criteria |
|-------|--------------|
| Dimensions specified | Figure size set explicitly (not default) |
| Transparency/resolution | Appropriate for publication (300+ DPI for raster, vector preferred) |
| Saved to file | Figures saved with `ggsave()` / `plt.savefig()`, not just displayed |
| Labels | Axes labelled, legend present where needed, title informative |
| Colour | Colourblind-friendly palette; not relying on red/green distinction |

### 7. Data Persistence

| Check | Pass Criteria |
|-------|--------------|
| Intermediate objects saved | Expensive computations saved (`saveRDS()` / `pickle.dump()` / `.parquet`) |
| Load before recompute | Script checks for saved objects before rerunning expensive operations |
| Output format | Final outputs in portable format (CSV, parquet — not just `.RData`) |

### 8. Dependencies

| Check | Pass Criteria |
|-------|--------------|
| Declared at top | All `library()` / `import` at the start of the script |
| Versions documented | `renv.lock` / `requirements.txt` / `pyproject.toml` exists |
| No unnecessary packages | Each loaded package is actually used |
| Installation instructions | README or comment explains how to set up the environment |

### 9. Python-Specific

*Score N/A if no Python files.*

| Check | Pass Criteria |
|-------|--------------|
| Type hints | Functions have type annotations for parameters and return values |
| Docstrings | Functions have docstrings (not just comments) |
| uv usage | Uses `uv` for environment management (per project conventions) |
| f-strings | Uses f-strings, not `.format()` or `%` formatting |

### 10. R-Specific

*Score N/A if no R files.*

| Check | Pass Criteria |
|-------|--------------|
| tidyverse consistency | Doesn't mix base R and tidyverse for the same operation |
| Assignment operator | Uses `<-` not `=` for assignment |
| Boolean values | Uses `TRUE`/`FALSE`, not `T`/`F` |
| Pipe consistency | Uses one pipe style consistently (`%>%` or `|>`) |

### 11. Cross-Language Verification

*Score N/A if the project has no numerical results or only uses one language.*

| Check | Pass Criteria |
|-------|--------------|
| Replication directory | `code/replication/` (or equivalent) exists with cross-language scripts |
| Two-language coverage | Key numerical results reproduced in a second language (e.g., R results verified in Python or vice versa) |
| Result comparison | Scripts compare outputs and report discrepancies (tolerance-based, not exact match) |
| Precision threshold | Numerical outputs compared to 6+ decimal places — discrepancies at lower precision indicate real bugs |
| Documentation | README or comments explain what is being replicated and acceptable tolerance |

#### Why Cross-Language Replication Works

Different languages produce different hallucination patterns when AI-assisted. An error in a Python implementation is unlikely to appear identically in R (or vice versa), making discrepancies easy to spot. This is the core insight from Scott Cunningham's Referee 2 protocol.

#### How to Set Up

1. Create `code/replication/` with scripts that independently implement key numerical results in a second language
2. Write a comparison script that loads outputs from both languages and reports discrepancies at 6+ decimal places
3. Document what is being replicated, which results are covered, and the acceptable tolerance (e.g., 1e-6 for coefficients, 1e-4 for standard errors)

## Confidence Filtering

- Only report issues where you are >80% confident they are genuine problems
- Consolidate similar findings (e.g., 5 instances of the same naming issue = 1 finding with count)
- For borderline cases, note uncertainty: "Possible issue (medium confidence): ..."
- Never pad the report with low-confidence observations to appear thorough

## Scorecard

| # | Category | Result | Notes |
|---|----------|--------|-------|
| 1 | Reproducibility | Pass/Fail | |
| 2 | Script structure | Pass/Fail | |
| 3 | Output hygiene | Pass/Fail | |
| 4 | Function quality | Pass/Fail | |
| 5 | Domain correctness | Pass/Fail | |
| 6 | Figure quality | Pass/Fail | |
| 7 | Data persistence | Pass/Fail | |
| 8 | Dependencies | Pass/Fail | |
| 9 | Python-specific | Pass/Fail/N/A | |
| 10 | R-specific | Pass/Fail/N/A | |
| 11 | Cross-language verification | Pass/Fail/N/A | |

**Overall: X/11 Pass** (adjust denominator for N/A categories)

## Quality Scoring

Apply numeric quality scoring using the shared framework and skill-specific rubric:

- **Framework:** [`../shared/quality-scoring.md`](../shared/quality-scoring.md) — severity tiers, thresholds, verdict rules
- **Rubric:** [`references/quality-rubric.md`](references/quality-rubric.md) — issue-to-deduction mappings for this skill

Start at 100, deduct per issue found, apply verdict. Insert the Score Block into the report after the scorecard.

## Report Format

```markdown
# Code Review Report

**Project:** [path]
**Date:** YYYY-MM-DD
**Scripts reviewed:** [list]
**Languages:** R / Python / Both

## Scorecard

[Table above, filled in]

## Detailed Findings

### Category 1: Reproducibility
**Result: Pass/Fail**

[Specific findings with file:line references]

### Category 2: Script Structure
...

[Continue for all 11 categories]

## Priority Fixes

1. [Most important issue — what to fix first]
2. [Second most important]
3. [Third]

## Quality Score

| Metric | Value |
|--------|-------|
| **Score** | XX / 100 |
| **Verdict** | Ship / Ship with notes / Revise / Revise (major) / Blocked |

### Deductions

| # | Issue | Tier | Deduction | Category |
|---|-------|------|-----------|----------|
| 1 | [description] | [tier] | -X | [category] |
| | **Total deductions** | | **-XX** | |

## Positive Observations

[Things done well — important for morale and learning]
```

## Council Mode (Optional)

For complex codebases or high-stakes replication packages, run the code review across multiple LLM providers. Different models have different strengths: some excel at spotting statistical errors, others at code structure or reproducibility issues.

**Trigger:** "Council code review" or "thorough code review"

**How it works:**
1. Each model independently scores all 11 categories against the same scripts
2. Cross-review: models evaluate each other's findings — catching false positives and missed issues
3. Chairman synthesis: produces a single `CODE-REVIEW-REPORT.md` with the union of confirmed findings

**Invocation (CLI backend):**
```bash
cd packages/cli-council
uv run python -m cli_council \
    --prompt-file /tmp/code-review-prompt.txt \
    --context-file /tmp/scripts-content.txt \
    --output-md /tmp/code-review-council.md \
    --chairman claude \
    --timeout 180
```

See `skills/shared/council-protocol.md` for the full orchestration protocol.

**Value:** Moderate to high — most valuable for domain correctness (Category 5) and cross-language verification (Category 11), where different models may catch different statistical or logical errors.

## Cross-References

- **`/code-archaeology`** — For understanding unfamiliar code before reviewing it
- **Referee 2 agent** — For formal cross-language replication and verification (Category 11 flags the absence; Referee 2 does the actual replication)
- **`/proofread`** — For the paper that accompanies this code
