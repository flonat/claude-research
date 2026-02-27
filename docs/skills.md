# Skills

> 38 reusable workflow definitions available across all projects.

Skills are structured instruction sets (`SKILL.md` files) that turn Claude into a specialised tool for specific tasks — from compiling LaTeX to bootstrapping research projects.

## Overview

| Skill | Description |
|-------|-------------|
| `beamer-deck` | Generate academic Beamer presentations with multi-agent review. Builds original themes, applies rhetoric principles, iterates until zero warnings |
| `code-archaeology` | Systematically review and understand old code, data, and analysis files. For reviving old projects, auditing inherited code, or preparing for R&R |
| `code-review` | Quality review for R and Python research scripts. 11-category scorecard covering reproducibility, structure, domain correctness, cross-language verification, and more. Report-only — never edits source files |
| `consolidate-memory` | Consolidate MEMORY.md files: prune duplicates, merge overlapping entries, generate abstractions, and remove stale knowledge. Inspired by npcsh sleep/dream cycles |
| `context-status` | Show current context status and session health.\nUse to check how much context has been used, whether auto-compact is\napproaching, and what state will be preserved |
| `creation-guard` | Pre-flight duplicate check before creating new skills or agents. Prevents duplicates and suggests iterations. MUST be invoked before writing any new artifact definition |
| `devils-advocate` | Challenge research assumptions and identify weaknesses in arguments. Stress-test papers before submission or revision |
| `init-project` | Bootstrap a new research project. Interview for details, scaffold directory structure, create Overleaf symlink, initialise git, and create project context files |
| `init-project-course` | Bootstrap a university course/module folder: scan existing content, interview, organise into lectures/workshops/assessments structure, and create CLAUDE.md. For taught modules with recurring components |
| `init-project-light` | Bootstrap a lightweight project: scan existing files, brief interview, create CLAUDE.md, and suggest basic organisation. No git, no Overleaf, no Notion pipeline |
| `init-project-research` | Bootstrap a research project: interview for details, scaffold directory, create Overleaf symlink, init git, and sync with context library and Notion |
| `insights-deck` | Generate timestamped Claude Code insights report and Beamer presentation. Runs /insights, archives HTML, then builds a rhetoric-driven deck from the findings |
| `interview-me` | Interactive interview to formalise a research idea into a structured specification with hypotheses and empirical strategy. Conversational — asks questions one at a time |
| `latex` | LaTeX document compilation and management. When Claude needs to compile LaTeX documents (.tex files) for papers, presentations, or other academic content |
| `latex-autofix` | LaTeX compilation with autonomous error resolution. Build artifacts go to out/, PDF is copied back to source directory. Parses logs, auto-fixes known errors (missing packages, font conflicts, citation issues, bad paths, stale cache), and runs citation audit on success |
| `latex-health-check` | Compile all LaTeX projects, auto-fix known errors, and check cross-project consistency. Self-healing build agent for the multi-project research ecosystem |
| `learn` | Extract reusable knowledge from the current session into a persistent skill.\nUse when you discover something non-obvious, create a workaround, or develop\na multi-step workflow that future sessions would benefit from |
| `lessons-learned` | Structured post-mortem after incidents, mistakes, or stuck sessions. Transforms problems into systematic improvements (skills, guards, docs, hooks). Use when something went wrong or 'how do we prevent this' |
| `literature` | Academic literature discovery, synthesis, and bibliography management. Find papers, verify citations, create .bib files, download PDFs, and synthesize literature narratives. Includes OpenAlex, Scopus, and Web of Science API integration for structured scholarly queries |
| `multi-perspective` | Explore a research question from multiple independent perspectives with diverse epistemic priors. Spawns parallel agents with distinct disciplinary lenses, then synthesises findings |
| `pipeline-manifest` | Build a pipeline manifest mapping scripts to inputs, outputs, and paper figures/tables. Optionally add structured headers to scripts |
| `pre-submission-report` | Run all quality checks and produce a single dated report before submission or sharing |
| `process-reviews` | Process referee comments from a reviews PDF into standardised tracking files: comment tracker, review analysis, and LaTeX verbatim transcription |
| `project-deck` | Create presentation decks to communicate project status. For supervisor meetings, coauthor handoffs, or documenting progress |
| `project-safety` | Set up safety rules and folder structures for research projects. Prevent accidental data loss when Claude reorganizes files |
| `proofread` | Academic proofreading for LaTeX papers. Grammar, notation consistency, citation format, tone, LaTeX issues, citation voice balance, and TikZ diagram review. Report-only — never edits source files |
| `python-env` | Python environment management with uv. ALWAYS use uv for package management, never pip directly |
| `quarto-deck` | Generate Reveal.js HTML presentations from Markdown. Applies rhetoric principles (assertion titles, one idea per slide, narrative arc). Best for teaching, informal talks, and web-shareable decks |
| `save-context` | Save information from conversations to the user's task management context library. Use when the user says: 'save this to my context', 'remember this', 'add to my profile', 'update my current focus', 'add this person to my contacts', 'save this project info', or any variation of wanting to persist information for future AI sessions |
| `session-log` | Create timestamped progress logs for research sessions. Detects multi-project sessions and creates separate logs per project. Enables continuity between Claude sessions |
| `session-recap` | End-of-session checklist. Checks for uncommitted changes, offers to update focus, project docs, context, and session log. Replaces the old stop hook |
| `split-pdf` | Download, split, and deeply read academic PDFs. Use when asked to read, review, or summarize an academic paper. Splits PDFs into 4-page chunks, reads them in small batches, and produces structured reading notes — avoiding context window crashes and shallow comprehension |
| `sync-notion` | Sync the current project's state to the central context library and Notion. Updates projects/_index.md, current-focus.md, and the Research Pipeline database entry |
| `system-audit` | Run parallel system audits across skills, hooks, agents, rules, bibliographies, conventions, and documentation freshness. Report-only — never modifies files |
| `task-management` | the user's personal task management system. Use for: daily planning, weekly reviews, meeting action extraction, task creation in Notion, progress tracking, and research pipeline management. Triggers: 'plan my day', 'what should I work on', 'extract actions', 'weekly review', 'what's overdue', 'update my tasks' |
| `update-focus` | Update current-focus.md with a structured session summary. Preserves the document's rich structure: weekly focus, session history rotation, open loops, mental state. Use at end of work sessions or when the stop hook nudges |
| `update-project-doc` | Update a project's own documentation (CLAUDE.md, README.md, docs/*.md) to reflect its current state. Detects stale file trees, timestamps, counts, and next steps. Includes a leanness audit: flags CLAUDE.md > 200 lines, sections > 15 lines of reference material, and SKILL.md > 300 lines — with auto-extraction to docs/ or references/ |
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
