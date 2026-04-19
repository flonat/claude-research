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
| `atlas-coherence` | Map portfolio as a network: clusters, bridges, orphans, sequencing |
| `interdisciplinary-bridge` | Import concepts from adjacent fields to solve open problems |
| `future-research-agenda` | Generate provocative, fundable future research directions |
| `atlas-audit` | Full audit of all topics across 4 systems |
| `atlas-deploy` | Compile atlas.json from topic files, commit, and deploy atlas web app to Fly.io |

### Literature (12)

| Skill | Purpose |
|-------|---------|
| `literature` | Academic search, citation verification, .bib management, OpenAlex API, end-to-end literature pipeline |
| `split-pdf` | Deep-read papers via 4-page chunks with structured notes |
| `gather-readings` | Copy PDFs from Paperpile into project articles/ folder |
| `theory-mapper` | Map theoretical landscape across a corpus of papers |
| `method-audit` | Compare data collection methods and spot biases |
| `evolution-timeline` | Chronological narrative of field evolution |
| `quote-mining` | Extract exact quotes with page numbers and argument mapping |
| `weakness-scanner` | Find weakest arguments and logical flaws across a literature |
| `replication-audit` | Audit replication status of key findings |
| `compile-knowledge` | Compile raw inputs (literature, meetings, logs) into a per-project knowledge wiki |
| `knowledge-lint` | Check compiled knowledge for contradictions, uncited claims, missing connections |
| `store-insight` | File a single research finding or insight into the project's knowledge wiki |

### Writing (1)

| Skill | Purpose |
|-------|---------|
| `proofread` | 7-category LaTeX proofreading scorecard (report only) |
| `claim-verify` | Verify cited claims against actual source papers |
| `voice-analyzer` | Analyze writing samples to create a portable voice profile (VOICE.md) |
| `voice-editor` | Edit content to match a voice profile (6-pass workflow, 4 editing modes) |
| `journal-voice` | Extract journal writing patterns and conventions into JOURNAL-VOICE.md |
| `review-response` | Systematic reviewer response drafting with classification, strategy, and tone checks |

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

### LaTeX & Bibliography (8)

| Skill | Purpose |
|-------|---------|
| `latex` | **Default compiler** — autonomous error resolution, citation audit, quality scoring |
| `latex-health-check` | Compile all projects, auto-fix, check cross-project consistency |
| `latex-template` | Compare preamble against working paper template (report + apply) |
| `bib-validate` | Cross-reference \cite{} keys against .bib files (report only) |
| `bib-filter` | Filter a .bib file to only entries actually cited in a .tex project |
| `bib-parse` | Extract citations from a PDF and generate a validated `.bib` file |
| `bib-coverage` | Compare a project .bib against a Paperpile label to find uncited papers |
| `latex-scaffold` | Convert Markdown draft into buildable LaTeX project (md→tex) |

### Submission (5)

| Skill | Purpose |
|-------|---------|
| `pre-submission-report` | All quality checks in one dated report |
| `retarget-journal` | Switch paper to different journal (rename, reformat, rekey) |
| `strategic-revision` | Referee comments PDF into DAG-validated revision master plan |
| `synthesise-reviews` | Synthesise parallel review reports into a prioritised revision plan |
| `brief-compliance-check` | Check LaTeX submission against assessment brief (deliverables, word limits, required files) |

### Project Setup & Session (18)

| Skill | Purpose |
|-------|---------|
| `init-project-research` | Full project scaffold (interview, git, Overleaf, vault) |
| `init-project-course` | Course/module folder scaffold |
| `init-project-light` | Lightweight scaffold (CLAUDE.md only, no git/vault) |
| `init-project-orchestration` | Add project agents, commands, and planning to a research project |
| `project-safety` | Safety rules and folder structures to prevent data loss |
| `session-log` | Timestamped progress logs for session continuity |
| `session-close` | End-of-session closing protocol with auto-detection (general or research) |
| `update-focus` | Structured update to current-focus.md |
| `session-health` | On-demand session health check |
| `save-context` | Save information to context library files |
| `task-management` | Daily planning, weekly reviews, meeting actions, vault |
| `ideas` | Capture improvement ideas for the infrastructure |
| `memory-cleanup` | Prune, merge, and abstract MEMORY.md entries |
| `update-project-doc` | Update a project's own docs to reflect current state |
| `checkpoint` | Save session state to survive context compaction or handoff between sessions |
| `restore` | Restore session state from a checkpoint after compaction or in a new session |
| `email-digest` | Email digest from Gmail |
| `decision-toolkit` | Structured decision-making for methodology, venue, or framework choices |

### Code & Analysis (8)

| Skill | Purpose |
|-------|---------|
| `code-review` | 11-category scorecard for R/Python scripts (report only) |
| `cross-language-check` | Replicate analysis in a second language (R↔Python↔Stata↔Julia) to verify correctness |
| `code-archaeology` | Review and document old code, data, and analysis files |
| `pipeline-manifest` | Map scripts to inputs, outputs, and paper figures/tables |
| `python-env` | Python environment management (enforces uv) |
| `audit-project-research` | Audit project against init-project-research template |
| `audit-project-course` | Audit course folder against init-project-course template |
| `webapp-testing` | Playwright-based web app testing with server lifecycle management. *From Anthropic.* |
| `frontend-design` | Distinctive, production-grade frontend interfaces. *From Anthropic.* |

### Experimental & Data (12)

| Skill | Purpose |
|-------|---------|
| `data-analysis` | End-to-end analysis pipeline (EDA, estimation, publication output) across R/Python/Stata/Julia |
| `computational-experiments` | Scaffold, run, and publish computational research experiments (algorithm skeletons, config-driven sweeps, seed-deterministic runners, publication figures) |
| `experiment-design` | Experimental and survey design: power analysis, PAP, QSF parsing, survey construction |
| `causal-design` | Identification strategy design and audit (DiD/IV/RDD/SC/event study) |
| `synthetic-data` | Generate structurally realistic synthetic datasets for pilot testing and power analysis |
| `replication-package` | Replication package assembly, anonymization, and audit (replaces export-project-clean/anon) |
| `econ-data` | Fetch economic data from FRED, World Bank, Eurostat, ECB, OECD, and EEX APIs |
| `econ-plots` | Economics-standard ggplot2 plots: coefficient, binscatter, RDD, decomposition |
| `r-econometrics` | R regression and econometrics: OLS, IV, panel, RDD, robust SEs |
| `event-studies` | DiD and event study implementation in R (TWFE vs modern estimators) |
| `code-paper-audit` | Systematic 6-phase code-paper consistency audit |
| `ethics-review` | Assess ethical risks: participant safety, data privacy, GDPR, AI ethics, ethics committee readiness |

### Sync & Deploy (8)

| Skill | Purpose |
|-------|---------|
| `sync-repo` | Sync docs with system state for atlas, biblio, taskflow, or private repos |
| `sync-public-repo` | Sync private infrastructure to the public repo (claude-research) |
| `sync-public-review` | Interactive review and editing of public sync allowlists |
| `sync-friends-repo` | Regenerate the friends-repo starter kit from private rules |
| `sync-resources` | Pull latest from cloned resource repos |
| `sync-permissions` | Sync global permissions into projects |
| `full-commit` | Commit and push all 11 global repos with leak guard |
| `release` | Full publication pipeline: sync, bump, commit, tag, publish |

### Audit & Quality (6)

| Skill | Purpose |
|-------|---------|
| `system-audit` | Parallel audits across skills, hooks, agents, rules, docs |
| `external-audit` | External LLM audit of any repo (atlas, biblio, taskflow, private, public, friends, paperpile, scholarly, biblio-sources, council) |
| `repo-doc-audit` | Documentation quality audit for any repo (atlas, biblio, taskflow, private, public, friends, paperpile, scholarly, biblio-sources, council) |
| `docs-consistency` | Cross-cutting doc review: count consistency, component coverage, stale refs, public-private sync, user manual |
| `skill-health` | Skill health dashboard: invocation counts, success rates, health status |

### Skill Lifecycle (3)

| Skill | Purpose |
|-------|---------|
| `skill-extract` | Extract session knowledge into a new persistent skill |
| `skill-preflight` | Pre-flight duplicate check before creating new skills/agents |
| `skill-creator` | Create, iterate, and benchmark skills with eval viewer. *From Anthropic.* |

### Machine & Radar (4)

| Skill | Purpose |
|-------|---------|
| `machine-inventory` | Audit machine environment (Homebrew, dotfiles, credentials, dev tools, nested repos, MCP) |
| `machine-evaluation` | Holistic review of machine setup from snapshots: missing tools, redundant apps, cross-machine parity |
| `radar` | Search the web for Claude Code updates, AI workflow patterns, and MCP ecosystem news |
| `radar-integrate` | Convert saved radar tips into infrastructure changes |

### Infrastructure (5)

| Skill | Purpose |
|-------|---------|
| `postmortem` | Structured post-mortem for incidents and stuck sessions |
| `rename-project-research` | Rename an Atlas topic slug across all systems |
| `mcp-builder` | Guide for creating MCP servers (Python/FastMCP or TypeScript). *From Anthropic.* |
| `wire-shared-package` | Wire a shared Python package as an editable dependency across projects |
| `scheduled-job` | Create, diagnose, or manage scheduled launchd jobs on the Mac Mini |

### Document Formats (3)

| Skill | Purpose |
|-------|---------|
| `docx` | Create, read, edit, or manipulate Word documents |
| `pdf` | Read, extract, combine, split, rotate, watermark PDF files |
| `xlsx` | Create, read, edit spreadsheets (.xlsx, .csv, .tsv) |

### Meetings (11)

| Skill | Purpose |
|-------|---------|
| `minutes-record` | Start or stop recording a meeting, call, or voice memo |
| `minutes-debrief` | Post-meeting debrief — compare outcomes to prep intentions |
| `minutes-prep` | Interactive meeting preparation with relationship briefs |
| `minutes-recap` | Daily digest of meetings — decisions, action items, themes |
| `minutes-weekly` | Weekly meeting synthesis — themes, decision arcs, stale commitments |
| `minutes-search` | Search past meeting transcripts and voice memos |
| `minutes-list` | List recent meetings and voice memos |
| `minutes-note` | Add timestamped notes during or after a recording |
| `minutes-verify` | Verify minutes setup — model, mic, directories |
| `minutes-setup` | Guided first-time setup for minutes |
| `minutes-cleanup` | Manage old recordings — archive, delete, disk space |

---

**Total: 156 skills across 16 categories.**

---

## Shared References (not skills — cross-cutting protocols)

Files in `skills/shared/` that multiple skills and agents reference. These are not invocable skills — they are guidance documents read on demand.

### Methodological Protocols

| File | Purpose | Used by |
|------|---------|---------|
| `escalation-protocol.md` | 4-level methodological pushback (Probe → Explain → Challenge → Flag) | paper-critic, referee2-reviewer, domain-reviewer, data-analysis, causal-design, experiment-design |
| `method-probing-questions.md` | Mandatory pre-analysis questions by method (12 paradigms) | data-analysis, causal-design, experiment-design, referee2-reviewer, domain-reviewer |
| `distribution-diagnostics.md` | DV distribution checks + model selection decision tree | data-analysis, referee2-reviewer, domain-reviewer |
| `engagement-stratified-sampling.md` | Engagement-tier sampling for social media data | data-analysis, experiment-design, referee2-reviewer |
| `intercoder-reliability.md` | Per-category reliability + LLM annotation validation | data-analysis, experiment-design, referee2-reviewer, domain-reviewer |

### Skill Architecture

| File | Purpose |
|------|---------|
| `quality-scoring.md` | Shared scoring framework for quality reports |
| `progressive-disclosure.md` | Pattern for splitting large skills into core + references |
| `skill-design-patterns.md` | Structural patterns for skill architecture |
| `rhetoric-principles.md` | Presentation rhetoric for deck skills |
| `multi-language-conventions.md` | R/Python/Stata/Julia conventions for analysis skills |
| `reference-resolution.md` | Logic for resolving Paperpile labels and topic references |
| `research-quality-rubric.md` | Research quality rubric for review agents |
| `council-protocol.md` | Multi-model council deliberation protocol |
| `external-audit-protocol.md` | Protocol for external LLM audits |
| `paid-api-safety.md` | Cost guardrails for paid API calls |
| `mcp-degradation.md` | Graceful degradation when MCP tools are unavailable |
| `project-documentation.md` | Project documentation conventions (index) |
| `project-documentation-content.md` | Content conventions (README, manual, architecture, deploy) |
| `project-documentation-format.md` | Format conventions (ASCII, LaTeX, Beamer, public variants) |
| `system-documentation.md` | System documentation conventions |
| `tikz-rules.md` | TikZ diagram conventions |
| `palettes.md` | Colour palettes for visualisations |
| `skill-index.md` | This file |
