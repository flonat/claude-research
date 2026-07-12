# Rules

> 18 neutral policy files rendered into client-appropriate guidance.

Canonical rules live in `rules/`. Claude receives rule files; Codex receives applicable guidance through `AGENTS.md`.

## Overview

| Rule | File | What it does |
|------|------|-------------|
| Audit Before Fix | `audit-before-fix.md` | When running audits, report ALL findings before fixing ANY of them. |
| Respect Client Guidance Ownership | `client-guidance-ownership.md` | Respect Client Guidance Ownership |
| Design Before Results | `design-before-results.md` | Lock the research design before examining point estimates. |
| Verify Every Reference Before Writing | `doi-verification.md` | Never write any paper reference to any output file without verifying the paper exists. |
| LaTeX Hygiene | `latex-hygiene.md` | LaTeX Hygiene |
| Keep Guidance Files Lean | `lean-guidance-files.md` | Client guidance files are loaded into context repeatedly—every line costs tokens and attention. |
| Record Learnings with [LEARN] Tags | `learn-tags.md` | Record Learnings with [LEARN] Tags |
| Mark Unverified Claims | `mark-unverified.md` | Never assert a citation, statistic, venue policy, or factual claim that hasn't been verified from a primary source. |
| No Hard-Coded Results in LaTeX | `no-hardcoded-results.md` | Never hard-code computed results directly into `.tex` files. |
| Overleaf Separation — No Code or Data in Paper Directories | `overleaf-separation.md` | The `paper/` directory (Overleaf symlink inside `paper-{venue}/paper/`) is for LaTeX source files ONLY. |
| Paper-vs-Code Consistency Check | `paper-code-consistency.md` | Before committing edits to §experiments or §methods, grep the actual code against the prose claim. |
| Plan Before Implementing | `plan-first.md` | Plan Before Implementing |
| Always Use uv for Python | `python-uv.md` | Never use bare `python`, `python3`, or `pip`. |
| Read Documentation Before Searching | `read-docs-first.md` | Never explore when documentation already answers your question. |
| Scope Discipline | `scope-discipline.md` | Only make changes the user explicitly requested. |
| Severity Gradient | `severity-gradient.md` | Calibrate critique intensity to the document's maturity. |
| Spec Compliance Before Quality Review | `spec-before-quality.md` | Validate that the specification is met before assessing quality. |
| Sub-Agent Write Guard | `subagent-write-guard.md` | Sub-agents must not run `git commit`, `git push`, `latexmk`, or any other write/build command without explicit authorisation in the prompt. |

## How Rules Work

- Claude-compatible rules install as managed copies under `~/.claude/rules/`
- Codex-compatible rules are rendered into its guidance surface
- Missing client metadata fails contract validation

## Creating New Rules

1. Create a `.md` file in `rules/`
2. Write clear, directive instructions (imperative mood)
3. Include "When This Applies" and "When to Skip" sections

Rules should be short and focused — one concern per file.
