# Skills

> 46 reusable workflow definitions available across all projects.

Skills are structured instruction sets (`SKILL.md` files) that turn Claude into a specialised tool for specific tasks — from compiling LaTeX to bootstrapping research projects.

## Overview

| Skill | Description |
|-------|-------------|
| `beamer-deck` | Use when you need to create an academic Beamer presentation with original theme and multi-agent review |
| `bib-validate` | Cross-reference \\cite{} keys against .bib files or embedded \\bibitem entries. Finds missing, unused, and typo'd citation keys. Deep verification mode spawns parallel agents for DOI/metadata validation at scale. Fix mode auto-adds missing entries to Paperpile |
| `code-archaeology` | Use when you need to review and understand old code, data, or analysis files |
| `code-review` | Use when you need a quality review of R, Python, or Julia research scripts. Multi-persona orchestrator with parallel specialist reviewers |
| `consolidate-memory` | Use when you need to prune duplicates and merge overlapping entries in MEMORY.md files |
| `context-status` | Use when you need to check current context status and session health |
| `creation-guard` | Use when you need a pre-flight duplicate check before creating new skills or agents |
| `devils-advocate` | Use when you need to challenge research assumptions or stress-test arguments |
| `handoff` | Use when you need to pass state to the next session in the current working directory. Writes a handoff.md file that the next session's SessionStart hook will read and delete |
| `init-project` | Bootstrap a new research project. Interview for details, scaffold directory structure, create Overleaf symlink, initialise git, and create project context files |
| `init-project-course` | Use when you need to bootstrap a university course or module folder |
| `init-project-light` | Use when you need to bootstrap a lightweight project with minimal structure |
| `init-project-research` | Use when you need to bootstrap a full research project with directory scaffold and Overleaf symlink |
| `insights-deck` | Use when you need a timestamped Claude Code insights report and Beamer presentation |
| `interview-me` | Use when you need to conduct a structured interview to extract knowledge or preferences |
| `latex` | Use when you need to compile a LaTeX document — includes autonomous error resolution, citation audit, and quality scoring |
| `latex-autofix` | Use when you need to compile LaTeX with autonomous error resolution and citation audit |
| `latex-health-check` | Use when you need to compile all LaTeX projects and check cross-project consistency |
| `learn` | Extract reusable knowledge from the current session into a persistent skill.\nUse when you discover something non-obvious, create a workaround, or develop\na multi-step workflow that future sessions would benefit from |
| `lessons-learned` | Use when you need a structured post-mortem after incidents, mistakes, or stuck sessions |
| `literature` | Use when you need academic literature discovery, synthesis, or bibliography management. Supports standalone searches and end-to-end project pipelines with vault sync and auto-commit |
| `memory-cleanup` | Use when you need to prune duplicates and merge overlapping entries in MEMORY.md files |
| `multi-perspective` | Use when you need to explore a research question from multiple independent perspectives |
| `parse-reviews` | Use when you need to process referee comments from a reviews PDF into tracking files |
| `pipeline-manifest` | Use when you need to map scripts to their inputs, outputs, and paper figures/tables |
| `postmortem` | Use when you need a structured post-mortem after incidents, mistakes, or stuck sessions |
| `pre-submission-report` | Use when you need all quality checks run before submission, producing a single dated report |
| `process-reviews` | Use when you need to process referee comments from a reviews PDF into tracking files |
| `project-deck` | Use when you need to create a presentation deck to communicate project status |
| `project-safety` | Use when you need to set up safety rules and folder structures for a research project |
| `proofread` | Use when you need academic proofreading of a LaTeX paper (11 check categories) |
| `python-env` | Use when you need Python environment management with uv (install, create venv, manage deps) |
| `quarto-deck` | Use when you need to generate a Reveal.js HTML presentation from Markdown |
| `save-context` | Use when you need to save information from the current conversation to the context library |
| `session-health` | Use when you need to check current context status and session health |
| `session-log` | Use when you need to create a timestamped progress log for a research session |
| `skill-extract` | Extract reusable knowledge from the current session into a persistent skill.\nUse when you discover something non-obvious, create a workaround, or develop\na multi-step workflow that future sessions would benefit from |
| `skill-preflight` | Use when you need a pre-flight duplicate check before creating new skills or agents |
| `split-pdf` | Use when you need to download, split, and deeply read an academic PDF that is NOT in Paperpile (for Paperpile items, prefer paperpile get-pdf-text directly) |
| `strategic-revision` | Use when you receive referee comments for a paper (R&R, revise-and-resubmit) and need a DAG-validated revision master plan — atomic task extraction, dependency mapping, computational critical-path analysis, execution blocks, venue strategy. Merges /parse-reviews ingestion with Sihvonen's strategic-revision architecture |
| `sync-notion` | Use when you need to sync the current project's state to the context library and Notion |
| `system-audit` | Use when you need to run parallel audits across skills, hooks, agents, rules, and conventions |
| `task-management` | Use when you need help with daily planning, weekly reviews, meeting actions, or vault task queries |
| `update-focus` | Use when you need to update current-focus.md with a structured session summary |
| `update-project-doc` | Use when you need to update a project's own CLAUDE.md, README.md, or docs/ to reflect current state |
| `validate-bib` | Cross-reference \\cite{} keys against .bib files or embedded \\bibitem entries. Finds missing, unused, and typo'd citation keys. Deep verification mode spawns parallel agents for DOI/metadata validation at scale. Read-only in standard mode |

## Using Skills

| Method | Example |
|--------|---------|
| Slash command | `/latex-autofix` |
| Natural language | "Compile my paper" or "Proofread this" |

## Skill Structure

Each skill is a directory in `skills/` containing a `SKILL.md` file with:

1. **YAML frontmatter** — name, description, and allowed tools
2. **Markdown body** — structured instructions Claude follows

## Creating New Skills

1. Create a directory: `skills/<skill-name>/`
2. Add a `SKILL.md` with YAML frontmatter and markdown instructions
3. The skill is immediately available via `/skill-name`

See any existing skill for the format.
