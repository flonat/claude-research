---
name: pre-submission-report
description: "Run all quality checks and produce a single dated report before submission or sharing."
allowed-tools: Bash(latexmk*, mkdir*, ls*, wc*), Read, Write, Edit, Glob, Grep, Task, Skill
argument-hint: "[path/to/main.tex or no arguments to auto-detect]"
---

# Pre-Submission Report

> Aggregates all quality checks into one dated report. Run before submitting to a journal/conference or sharing with collaborators.

## When to Use

- Before submitting a paper to a venue
- Before sharing a draft with supervisors or co-authors
- When the user says "pre-submission check", "is this ready?", "run everything"

## Input

- A `.tex` file path, or auto-detect `paper/main.tex` in the current project

## Critical Rule

**Python:** Always use `uv run python` or `uv pip install`. Never bare `python`, `python3`, `pip`, or `pip3`. Include this in any sub-agent prompts.

## Steps

### 1. Locate the Paper

If no argument provided, search for the main `.tex` file:
1. Check `paper/main.tex`
2. Check `paper/*.tex` for a file containing `\begin{document}`
3. Ask the user if ambiguous

### 2. Run Quality Checks

Run these sequentially (each depends on a clean state):

1. **Compilation** — invoke `/latex-autofix` on the main `.tex` file. Record pass/fail and any remaining warnings.
2. **Citation audit** — invoke `/validate-bib`. Record missing, unused, and suspect keys.
3. **Adversarial review** — launch `paper-critic` agent (via Task tool). Capture the CRITIC-REPORT.md score and findings.

### 3. Aggregate Report

Save to `log/quality-reports/YYYY-MM-DD_<project-name>.md`:

```markdown
# Pre-Submission Quality Report

**Project:** <project name>
**Date:** YYYY-MM-DD
**File:** <path to main.tex>
**Target:** <venue from project CLAUDE.md, or "not specified">

---

## Overall Score: XX/100 — [Verdict]

Verdict uses the quality scoring framework:
- 90-100: Publication-ready
- 80-89: Minor revisions needed
- 70-79: Significant revisions needed
- Below 70: Not ready

---

## Compilation

- **Status:** PASS / FAIL
- **Warnings:** <count>
- **Details:** <brief summary of any issues>

## Citations

- **Missing keys:** <count> — <list>
- **Unused keys:** <count> — <list>
- **Suspect entries:** <count> — <list>

## Adversarial Review

- **Score:** XX/100
- **Key findings:**
  - <finding 1>
  - <finding 2>
  - ...

## Research Quality Score

Load `skills/shared/research-quality-rubric.md` and report the weighted aggregate (X.X / 5.0) with verdict.

## Remaining Issues

| # | Severity | Category | Issue |
|---|----------|----------|-------|
| 1 | High/Medium/Low | Compilation/Citation/Content | <description> |

## Recommendation

**[Submit / Revise / Not ready]**

<1-2 sentence summary of what needs to happen before submission>
```

### 4. Present Summary

Display the report path and the summary table to the user. If the recommendation is "Submit", congratulate. If "Revise", list the top 3 issues to fix first.

## Error Handling

- If compilation fails after `/latex-autofix`, still run the remaining checks. Mark compilation as FAIL in the report.
- If `paper-critic` agent fails, note it in the report and base the overall score on compilation + citations only.
- Always produce the report file, even if some checks failed.

## Integration

| Skill/Agent | Role in this workflow |
|-------------|---------------------|
| `/latex-autofix` | Compilation + auto-fix |
| `/validate-bib` | Citation cross-reference |
| `paper-critic` agent | Adversarial content review |
| `quality-scoring.md` | Verdict thresholds |
