# 11 Checklist Categories

Detailed specifications for Phase 2 baseline checklist.

## 1. Reproducibility

| Check | Pass Criteria |
|-------|--------------|
| Random seeds | `set.seed()` / `random.seed()` / `np.random.seed()` set before any stochastic operation |
| Relative paths | No hardcoded absolute paths (e.g., `/Users/username/...` or `C:\...`) |
| Working directory | Script does not `setwd()` / `os.chdir()` — uses project-relative paths |
| Session info | Script prints session info at end (`sessionInfo()` / `sys.version`) or documents environment |
| HPC SHA logging | If project has `hpc/*.sbatch`: every sbatch writes `git-sha.txt` + `git-status.txt` to `OUT_DIR` before `srun` (pins results to code version). Missing SHA log = P1 reproducibility deduction. See [`docs/guides/hpc.md`](../../docs/guides/hpc.md). |
| HPC account/partition | If `*.sbatch` present: `--account=wbs` set, partition matches workload (compute/gpu/hmem/devel), no hardcoded user paths |

## 2. Script Structure

| Check | Pass Criteria |
|-------|--------------|
| Header | Script begins with comment block: purpose, author, date, inputs, outputs |
| Sections | Code organised into labelled sections (comments or `# ---- Section ----`) |
| Imports at top | All `library()` / `import` statements at the top of the file |
| Reasonable length | Single script < 500 lines; longer scripts should be split |

## 3. Output Hygiene

| Check | Pass Criteria |
|-------|--------------|
| No print pollution | No stray `print()` / `cat()` / `message()` dumping to console |
| Outputs saved | Key results saved to files, not just printed |
| Clean console | Running the script does not produce walls of text |

## 4. Function Quality

| Check | Pass Criteria |
|-------|--------------|
| Documentation | Functions have comments explaining purpose, inputs, outputs |
| Naming | Function names are descriptive verbs (`estimate_ate`, not `f1`) |
| Defaults | Reasonable defaults for optional parameters |
| No side effects | Functions don't modify global state |

## 5. Domain Correctness

| Check | Pass Criteria |
|-------|--------------|
| Estimator matches paper | The estimator used matches what the paper claims |
| Weights | If weighted: weights sum to expected value, correct application |
| Standard errors | Clustering / HC / bootstrap matches paper specification |
| Sample restrictions | Filters match the paper's sample description |
| Variable construction | Variables constructed as described in the paper |

## 6. Figure Quality

| Check | Pass Criteria |
|-------|--------------|
| Dimensions specified | Figure size set explicitly (not default) |
| Transparency/resolution | Appropriate for publication (300+ DPI for raster, vector preferred) |
| Saved to file | Figures saved with `ggsave()` / `plt.savefig()`, not just displayed |
| Labels | Axes labelled, legend present where needed, title informative |
| Colour | Colourblind-friendly palette; not relying on red/green distinction |

## 7. Data Persistence

| Check | Pass Criteria |
|-------|--------------|
| Intermediate objects saved | Expensive computations saved (`saveRDS()` / `pickle.dump()` / `.parquet`) |
| Load before recompute | Script checks for saved objects before rerunning expensive operations |
| Output format | Final outputs in portable format (CSV, parquet — not just `.RData`) |

## 8. Dependencies

| Check | Pass Criteria |
|-------|--------------|
| Declared at top | All `library()` / `import` at the start of the script |
| Versions documented | `renv.lock` / `requirements.txt` / `pyproject.toml` exists |
| No unnecessary packages | Each loaded package is actually used |
| Installation instructions | README or comment explains how to set up the environment |

## 9. Python-Specific

*Score N/A if no Python files.*

| Check | Pass Criteria |
|-------|--------------|
| Type hints | Functions have type annotations for parameters and return values |
| Docstrings | Functions have docstrings (not just comments) |
| uv usage | Uses `uv` for environment management (per project conventions) |
| f-strings | Uses f-strings, not `.format()` or `%` formatting |

## 10. R-Specific

*Score N/A if no R files.*

| Check | Pass Criteria |
|-------|--------------|
| tidyverse consistency | Doesn't mix base R and tidyverse for the same operation |
| Assignment operator | Uses `<-` not `=` for assignment |
| Boolean values | Uses `TRUE`/`FALSE`, not `T`/`F` |
| Pipe consistency | Uses one pipe style consistently (`%>%` or `\|>`) |

## 11. Cross-Language Verification

*Score N/A if the project has no numerical results or only uses one language.*

| Check | Pass Criteria |
|-------|--------------|
| Replication directory | `code/replication/` (or equivalent) exists with cross-language scripts |
| Two-language coverage | Key numerical results reproduced in a second language |
| Result comparison | Scripts compare outputs and report discrepancies (tolerance-based) |
| Precision threshold | Numerical outputs compared to 6+ decimal places |
| Documentation | README explains what is being replicated and acceptable tolerance |
