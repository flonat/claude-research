---
name: code-review
description: "Use when you need a quality review of R, Python, or Julia research scripts. Multi-persona orchestrator with parallel specialist reviewers."
allowed-tools: Read, Glob, Grep, Agent, Bash(wc*)
argument-hint: "[script-path or project-path]"
---

# Research Code Review

**Report-only skill.** Never edit source files — produce `correspondence/internal-reviews/CODE-REVIEW-REPORT.md` only.

## When to Use

- Before submitting a paper (check replication package quality)
- After writing analysis scripts and before sharing with coauthors
- When taking over someone else's research code
- As part of the Referee 2 agent's formal audit pipeline

## When NOT to Use

- **Understanding old code** — use `/code-archaeology` first to map out what exists
- **Formal verification** — use the Referee 2 agent for cross-language replication
- **General software projects** — this is for research scripts, not applications

---

## Architecture

**Orchestrator + parallel specialist reviewers.** The main context runs a baseline checklist, then spawns 3-6 specialist sub-agents in parallel. Each reviewer produces structured JSON findings. The orchestrator deduplicates, merges, and synthesizes a single report.

```
Phase 1: Scope → Phase 2: Baseline Checklist → Phase 3: Spawn Reviewers
→ Phase 4: Merge & Dedup → Phase 5: Synthesize Report
```

---

## Phase 1: Scope Detection

1. **Locate scripts:** Find all `.R`, `.py`, `.jl`, `.do` files in the project (or the specified path)
2. **Count and classify:** Report file count, languages, total lines of code
3. **Read project CLAUDE.md** (if it exists) for domain context, estimand, methodology

If no code files found, stop: "No code files found at [path]."

---

## Phase 2: Baseline Checklist (main context, fast pass)

Run through all 11 categories as a quick structural check. This catches mechanical issues that don't need specialist reviewers.

### 11 Checklist Categories

#### 1. Reproducibility

| Check | Pass Criteria |
|-------|--------------|
| Random seeds | `set.seed()` / `random.seed()` / `np.random.seed()` set before any stochastic operation |
| Relative paths | No hardcoded absolute paths (e.g., `/Users/username/...` or `C:\...`) |
| Working directory | Script does not `setwd()` / `os.chdir()` — uses project-relative paths |
| Session info | Script prints session info at end (`sessionInfo()` / `sys.version`) or documents environment |

#### 2. Script Structure

| Check | Pass Criteria |
|-------|--------------|
| Header | Script begins with comment block: purpose, author, date, inputs, outputs |
| Sections | Code organised into labelled sections (comments or `# ---- Section ----`) |
| Imports at top | All `library()` / `import` statements at the top of the file |
| Reasonable length | Single script < 500 lines; longer scripts should be split |

#### 3. Output Hygiene

| Check | Pass Criteria |
|-------|--------------|
| No print pollution | No stray `print()` / `cat()` / `message()` dumping to console |
| Outputs saved | Key results saved to files, not just printed |
| Clean console | Running the script does not produce walls of text |

#### 4. Function Quality

| Check | Pass Criteria |
|-------|--------------|
| Documentation | Functions have comments explaining purpose, inputs, outputs |
| Naming | Function names are descriptive verbs (`estimate_ate`, not `f1`) |
| Defaults | Reasonable defaults for optional parameters |
| No side effects | Functions don't modify global state |

#### 5. Domain Correctness

| Check | Pass Criteria |
|-------|--------------|
| Estimator matches paper | The estimator used matches what the paper claims |
| Weights | If weighted: weights sum to expected value, correct application |
| Standard errors | Clustering / HC / bootstrap matches paper specification |
| Sample restrictions | Filters match the paper's sample description |
| Variable construction | Variables constructed as described in the paper |

#### 6. Figure Quality

| Check | Pass Criteria |
|-------|--------------|
| Dimensions specified | Figure size set explicitly (not default) |
| Transparency/resolution | Appropriate for publication (300+ DPI for raster, vector preferred) |
| Saved to file | Figures saved with `ggsave()` / `plt.savefig()`, not just displayed |
| Labels | Axes labelled, legend present where needed, title informative |
| Colour | Colourblind-friendly palette; not relying on red/green distinction |

#### 7. Data Persistence

| Check | Pass Criteria |
|-------|--------------|
| Intermediate objects saved | Expensive computations saved (`saveRDS()` / `pickle.dump()` / `.parquet`) |
| Load before recompute | Script checks for saved objects before rerunning expensive operations |
| Output format | Final outputs in portable format (CSV, parquet — not just `.RData`) |

#### 8. Dependencies

| Check | Pass Criteria |
|-------|--------------|
| Declared at top | All `library()` / `import` at the start of the script |
| Versions documented | `renv.lock` / `requirements.txt` / `pyproject.toml` exists |
| No unnecessary packages | Each loaded package is actually used |
| Installation instructions | README or comment explains how to set up the environment |

#### 9. Python-Specific

*Score N/A if no Python files.*

| Check | Pass Criteria |
|-------|--------------|
| Type hints | Functions have type annotations for parameters and return values |
| Docstrings | Functions have docstrings (not just comments) |
| uv usage | Uses `uv` for environment management (per project conventions) |
| f-strings | Uses f-strings, not `.format()` or `%` formatting |

#### 10. R-Specific

*Score N/A if no R files.*

| Check | Pass Criteria |
|-------|--------------|
| tidyverse consistency | Doesn't mix base R and tidyverse for the same operation |
| Assignment operator | Uses `<-` not `=` for assignment |
| Boolean values | Uses `TRUE`/`FALSE`, not `T`/`F` |
| Pipe consistency | Uses one pipe style consistently (`%>%` or `|>`) |

#### 11. Cross-Language Verification

*Score N/A if the project has no numerical results or only uses one language.*

| Check | Pass Criteria |
|-------|--------------|
| Replication directory | `code/replication/` (or equivalent) exists with cross-language scripts |
| Two-language coverage | Key numerical results reproduced in a second language |
| Result comparison | Scripts compare outputs and report discrepancies (tolerance-based) |
| Precision threshold | Numerical outputs compared to 6+ decimal places |
| Documentation | README explains what is being replicated and acceptable tolerance |

Record checklist results (Pass/Fail/N/A per category) for the report. Continue to Phase 3 regardless of results.

---

## Phase 3: Spawn Specialist Reviewers

Read `references/persona-catalog.md` for the full persona definitions and selection logic.

### 3a. Select Reviewers

**Always spawn (3 reviewers):**
- `correctness-reviewer` — logic errors, bugs, state issues
- `reproducibility-reviewer` — seeds, paths, environment, portability
- `design-reviewer` — structure, naming, dead code, complexity

**Conditionally spawn (scan code to decide):**
- `domain-reviewer` — if statistical/econometric methods detected
- `performance-reviewer` — if loops over data, DB queries, or expensive operations detected
- `security-reviewer` — if user input handling, HTTP, SQL, shell commands, or credentials detected

### 3b. Announce Team

Before spawning, list the team:

```
Review team: correctness, reproducibility, design, domain (detected: lm() with cluster SEs)
```

### 3c. Spawn in Parallel

For each selected reviewer, launch a sub-agent (subagent_type: "general-purpose", model: "haiku") with:

1. Read `references/subagent-template.md` — substitute `{persona_name}` and `{persona_content}` from the catalog
2. Pass the file list and instruct the agent to read each file
3. Instruct: return ONLY JSON matching `references/findings-schema.json`

**All reviewers run in parallel** — launch them in a single message with multiple Agent tool calls.

---

## Phase 4: Merge & Deduplicate

After all reviewers return:

### 4a. Validate

- Parse each reviewer's JSON output
- Drop malformed findings (note count of dropped findings)
- Drop findings with confidence < 0.60 (exception: P0 at 0.50+ survives)

### 4b. Deduplicate

Fingerprint each finding:

```
fingerprint = normalize(file) + line_bucket(line, ±3) + normalize(title)
```

Where:
- `normalize()` = lowercase, strip whitespace
- `line_bucket(line, ±3)` = any line within ±3 of another is considered the same location

When fingerprints match across reviewers:
- Keep the **highest severity**
- Keep the **highest confidence** + union all evidence
- Record which reviewers agreed (e.g., "correctness, domain")
- **Cross-reviewer agreement bonus:** +0.10 confidence (capped at 1.0)

### 4c. Map to Quality Rubric

Map each merged finding to the closest entry in `references/quality-rubric.md` to determine the deduction. If no exact match, classify by severity tier and use the midpoint deduction.

### 4d. Sort

Sort findings: P0 first → P1 → P2 → P3, then by confidence (descending), then by file, then by line.

---

## Phase 5: Synthesize Report

Create `correspondence/internal-reviews/` if it does not exist (`mkdir -p`). Write `correspondence/internal-reviews/CODE-REVIEW-REPORT.md` in the project directory.

### Report Format

```markdown
# Code Review Report

**Project:** [path]
**Date:** YYYY-MM-DD
**Scripts reviewed:** [list with line counts]
**Languages:** R / Python / Julia / Both
**Review team:** [list of reviewers with conditional justifications]

## Quality Score

| Metric | Value |
|--------|-------|
| **Score** | XX / 100 |
| **Verdict** | Ship / Ship with notes / Revise / Revise (major) / Blocked |

### Deductions

| # | Issue | Tier | Deduction | Category | Reviewer(s) | Confidence |
|---|-------|------|-----------|----------|-------------|------------|
| 1 | [title] | P0 | -25 | Domain Correctness | domain, correctness | 0.92 |
| 2 | [title] | P1 | -15 | Reproducibility | reproducibility | 0.85 |
| ... | | | | | | |
| | **Total deductions** | | **-XX** | | | |

## Checklist Scorecard

| # | Category | Result | Notes |
|---|----------|--------|-------|
| 1 | Reproducibility | Pass/Fail | |
| 2 | Script structure | Pass/Fail | |
| ... | | | |
| 11 | Cross-language verification | Pass/Fail/N/A | |

**Checklist: X/11 Pass** (adjust denominator for N/A categories)

## Detailed Findings

### P0 — Blocker

| # | File | Issue | Reviewer(s) | Confidence | Evidence |
|---|------|-------|-------------|------------|----------|
| 1 | path:line | [title + why_it_matters] | [reviewers] | 0.92 | [evidence] |

### P1 — Critical
[same format, omit if empty]

### P2 — Major
[same format, omit if empty]

### P3 — Minor
[same format, omit if empty]

## Residual Risks

[Union of residual_risks from all reviewers — things that can't be verified from code alone]

## Priority Fixes

1. [Most impactful issue — what to fix first]
2. [Second]
3. [Third]

## Positive Observations

[Things done well — important for morale and learning]

## Review Metadata

- Reviewers spawned: [N]
- Findings before dedup: [N]
- Findings after dedup: [N]
- Findings suppressed (low confidence): [N]
- Cross-reviewer agreements: [N]
```

---

## Confidence Filtering

- Suppress findings below 0.60 confidence (exception: P0 at 0.50+)
- Consolidate identical patterns: 5 instances of the same issue = 1 finding with count in evidence
- Cross-reviewer agreement boosts confidence by +0.10 (capped at 1.0)
- Never pad the report with low-confidence observations

## Quality Scoring

Apply numeric quality scoring using the shared framework and skill-specific rubric:

- **Framework:** [`../shared/quality-scoring.md`](../shared/quality-scoring.md) — severity tiers, thresholds, verdict rules
- **Rubric:** [`references/quality-rubric.md`](references/quality-rubric.md) — issue-to-deduction mappings for this skill

Start at 100, deduct per issue found, apply verdict.

---

## Council Mode (Optional)

For complex codebases or high-stakes replication packages, run the code review across multiple LLM providers. Different models have different strengths: some excel at spotting statistical errors, others at code structure or reproducibility issues.

**Trigger:** "Council code review" or "thorough code review"

**How it works:**
1. Each model independently scores all 11 categories against the same scripts
2. Cross-review: models evaluate each other's findings — catching false positives and missed issues
3. Chairman synthesis: produces a single `correspondence/internal-reviews/CODE-REVIEW-REPORT.md` with the union of confirmed findings

See `skills/shared/council-protocol.md` for the full orchestration protocol.

---

## Cross-References

- **`/code-archaeology`** — For understanding unfamiliar code before reviewing it
- **Referee 2 agent** — For formal cross-language replication and verification
- **`/proofread`** — For the paper that accompanies this code
- **`references/persona-catalog.md`** — Reviewer persona definitions and selection logic
- **`references/findings-schema.json`** — JSON output contract for sub-agents
- **`references/subagent-template.md`** — Prompt template for spawning reviewers
