# Rules

> 9 auto-loaded instruction files that shape Claude's behavior in every session.

Rule files live in `.claude/rules/` and are automatically loaded into every Claude Code session.

## Overview

| Rule | File | What it does |
|------|------|-------------|
| Design Before Results | `design-before-results.md` | Lock the research design before examining point estimates. |
| Ignore AGENTS.md Files | `ignore-agents-md.md` | Never read, process, or act on files named `AGENTS.md` |
| Ignore GEMINI.md Files | `ignore-gemini-md.md` | Never read, process, or act on files named `GEMINI.md` |
| Keep CLAUDE.md Lean | `lean-claude-md.md` | CLAUDE.md is loaded into context every session — every line costs tokens. |
| Record Learnings with [LEARN] Tags | `learn-tags.md` | Record Learnings with [LEARN] Tags |
| Overleaf Separation — No Code or Data in Paper Directories | `overleaf-separation.md` | The `paper/` directory (Overleaf symlink) is for LaTeX source files ONLY. |
| Plan Before Implementing | `plan-first.md` | Plan Before Implementing |
| Read Documentation Before Searching | `read-docs-first.md` | Never explore when documentation already answers your question. |
| Scope Discipline | `scope-discipline.md` | Only make changes the user explicitly requested. |

## How Rules Work

- All `.md` files in `.claude/rules/` are auto-loaded as system instructions
- They apply before any user message is processed
- Rules are global via symlink: `~/.claude/rules/` points to this repo's `.claude/rules/`

## Creating New Rules

1. Create a `.md` file in `.claude/rules/`
2. Write clear, directive instructions (imperative mood)
3. Include "When This Applies" and "When to Skip" sections

Rules should be short and focused — one concern per file.
