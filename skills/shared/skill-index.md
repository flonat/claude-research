# Skill Index

> Compact discovery table for all skills. Scan this when checking for duplicates,
> answering "what skills do I have for X?", or deciding where a new skill fits.

## By Category

### Ideation (3)

| Skill | Purpose |
|-------|---------|
| `interview-me` | Interactive interview to formalise a research idea into a structured spec |
| `devils-advocate` | Multi-turn debate to challenge assumptions and stress-test arguments |
| `multi-perspective` | Parallel agents with distinct disciplinary lenses explore a question |

### Literature (2)

| Skill | Purpose |
|-------|---------|
| `literature` | Academic search, citation verification, .bib management, OpenAlex API |
| `split-pdf` | Deep-read papers via 4-page chunks with structured notes |

### Writing (1)

| Skill | Purpose |
|-------|---------|
| `proofread` | 7-category LaTeX proofreading scorecard (report only) |
| `voice-analyzer` | Analyze writing samples to create a portable voice profile (VOICE.md) |
| `voice-editor` | Edit content to match a voice profile (6-pass workflow, 4 editing modes) |

### Presentation (8)

| Skill | Purpose |
|-------|---------|
| `beamer-deck` | Rhetoric-driven Beamer slides with multi-agent review |
| `quarto-deck` | Reveal.js HTML presentations (teaching, informal talks) |
| `quarto-course` | Quarto course websites with slides and exercises |
| `project-deck` | Status decks for supervisor meetings and handoffs |
| `insights-deck` | Claude Code usage insights as a Beamer presentation |
| `latex-posters` | Research posters in LaTeX (beamerposter, tikzposter, baposter) |
| `translate-to-quarto` | Translate Beamer LaTeX slides to Quarto RevealJS |
| `pptx` | Create, read, edit, or manipulate PowerPoint files |

### LaTeX & Bibliography (7)

| Skill | Purpose |
|-------|---------|
| `latex` | Basic LaTeX compilation with latexmk |
| `latex-autofix` | **Default compiler** — auto-fixes errors, citation audit on success |
| `latex-health-check` | Compile all projects, auto-fix, check cross-project consistency |
| `audit-template-compliance` | Compare preamble against working paper template (report + apply) |
| `bib-validate` | Cross-reference \cite{} keys against .bib files (report only) |
| `bib-parse` | Extract citations from a PDF and generate a validated `.bib` file |
| `latex-scaffold` | Convert Markdown draft into buildable LaTeX project (md→tex) |

### Submission (5)

| Skill | Purpose |
|-------|---------|
| `pre-submission-report` | All quality checks in one dated report |
| `retarget-journal` | Switch paper to different journal (rename, reformat, rekey) |
| `process-reviews` | Referee comments PDF into tracking files |
| `synthesise-reviews` | Synthesise parallel review reports into a prioritised revision plan |
| `brief-compliance-check` | Check LaTeX submission against assessment brief (deliverables, word limits, required files) |

### Project Setup & Session (15)

| Skill | Purpose |
|-------|---------|
| `init-project-research` | Full project scaffold (interview, git, Overleaf, Notion) |
| `init-project-course` | Course/module folder scaffold |
| `init-project-light` | Lightweight scaffold (CLAUDE.md only, no git/Notion) |
| `project-safety` | Safety rules and folder structures to prevent data loss |
| `session-log` | Timestamped progress logs for session continuity |
| `session-recap` | End-of-session checklist (git, focus, docs, log) |
| `update-focus` | Structured update to current-focus.md |
| `context-status` | On-demand session health check |
| `save-context` | Save information to context library files |
| `task-management` | Daily planning, weekly reviews, meeting actions, Notion |
| `ideas` | Capture improvement ideas for the infrastructure |
| `consolidate-memory` | Prune, merge, and abstract MEMORY.md entries |
| `update-project-doc` | Update a project's own docs to reflect current state |
| `sync-notion` | Sync project state to context library and Notion |
| `init-project-orchestration` | Add project agents, commands, and planning to a research project |

### Code & Analysis (8)

| Skill | Purpose |
|-------|---------|
| `code-review` | 11-category scorecard for R/Python scripts (report only) |
| `code-archaeology` | Review and document old code, data, and analysis files |
| `pipeline-manifest` | Map scripts to inputs, outputs, and paper figures/tables |
| `python-env` | Python environment management (enforces uv) |
| `audit-project-research` | Audit project against init-project-research template |
| `audit-project-course` | Audit course folder against init-project-course template |
| `webapp-testing` | Playwright-based web app testing with server lifecycle management. *From Anthropic.* |
| `frontend-design` | Distinctive, production-grade frontend interfaces. *From Anthropic.* |

### Experimental & Data (6)

| Skill | Purpose |
|-------|---------|
| `data-analysis` | End-to-end analysis pipeline (EDA, estimation, publication output) across R/Python/Stata/Julia |
| `computational-experiments` | Scaffold, run, and publish computational research experiments (algorithm skeletons, config-driven sweeps, seed-deterministic runners, publication figures) |
| `experiment-design` | Experimental and survey design: power analysis, PAP, QSF parsing, survey construction |
| `causal-design` | Identification strategy design and audit (DiD/IV/RDD/SC/event study) |
| `synthetic-data` | Generate structurally realistic synthetic datasets for pilot testing and power analysis |
| `replication-package` | Replication package assembly, anonymization, and audit (replaces export-project-clean/anon) |

### Infrastructure (25)

| Skill | Purpose |
|-------|---------|
| `learn` | Extract session knowledge into a new persistent skill |
| `creation-guard` | Pre-flight duplicate check before creating new skills/agents |
| `lessons-learned` | Structured post-mortem for incidents and stuck sessions |
| `system-audit` | Parallel audits across skills, hooks, agents, rules, docs |
| `audit-atlas-portfolio` | Full audit of all topics across 4 systems |
| `sync-private-doc` | Propagate counts across all private Task Management docs |
| `sync-public-doc` | Sync private infrastructure to the public repo (claude-research) |
| `sync-refpile-doc` | Sync RefPile docs with actual codebases (extension, dashboard, MCP) |
| `sync-resources` | Pull latest from cloned resource repos |
| `sync-permissions` | Sync global permissions into projects |
| `sync-scout-doc` | Sync Scout + council package docs |
| `review-public-sync` | Interactive review and editing of public sync allowlists |
| `full-commit` | Commit and push all 8 global repos with leak guard |
| `publish` | Full publication pipeline: sync, bump, commit, tag, publish |
| `skill-creator` | Create, iterate, and benchmark skills with eval viewer. *From Anthropic.* |
| `mcp-builder` | Guide for creating MCP servers (Python/FastMCP or TypeScript). *From Anthropic.* |
| `external-private-audit` | Qualitative architecture audit of Task Management via external LLM CLI (Codex/Gemini) |
| `external-public-audit` | Qualitative audit of public repo and sync script via external LLM CLI (Codex/Gemini) |
| `external-refpile-audit` | Qualitative architecture audit of RefPile monorepo via external LLM CLI (Codex/Gemini) |
| `external-scout-audit` | Qualitative architecture and security audit of Scout app via external LLM CLI (Codex/Gemini) |
| `refpile-development` | Update and manage RefPile development topic documents |
| `deploy-atlas` | Compile atlas.json from topic files, commit, and deploy atlas web app to Fly.io |
| `scaffold-atlas-topics` | Add new research topics to the atlas (topic files, themes, Notion, Dropbox, docs) |
| `radar` | Search the web for Claude Code updates, AI workflow patterns, and MCP ecosystem news |
| `radar-integrate` | Convert saved radar tips into infrastructure changes |

### Document Formats (3)

| Skill | Purpose |
|-------|---------|
| `docx` | Create, read, edit, or manipulate Word documents |
| `pdf` | Read, extract, combine, split, rotate, watermark PDF files |
| `xlsx` | Create, read, edit spreadsheets (.xlsx, .csv, .tsv) |

---

**Total: 88 skills across 11 categories.**
