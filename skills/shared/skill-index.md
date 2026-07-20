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
| `future-research-agenda` | Generate provocative, fundable future research directions from a corpus |
| `atlas-audit` | Full audit of all topics across 4 systems |
| `atlas-deploy` | Manual-only schema validation + Mac Mini launchd restart for `atlas-workspace` (atlas.example.com). No compile/push step — atlas-workspace reads vault directly via Syncthing. |
| `hypothesis-generation` | Generate competing testable hypotheses from observations with experimental designs and predictions |
| `bridges` | Find cross-project connections: shared methods, overlapping papers, conceptual bridges via Paperpile vector search + atlas metadata |
| `idea-pivot` | Structured reframe for a below-threshold research idea (nested: research/) |

### Literature (20)

| Skill | Purpose |
|-------|---------|
| `literature` | Academic search, citation verification, .bib management, end-to-end literature pipeline (Phase 3b: SciSciNet enrichment) |
| `journals-biz` | Build Scopus ISSN boolean queries filtered by business/economics journal rankings (AJG/CABS, FT50). First in the `journals-*` family — see `log/ideas.md` for sibling proposals |
| `split-pdf` | Deep-read academic papers via 4-page chunks with structured notes |
| `paper-reading` | Read, visually inspect, explain, critique, and teach one academic article end to end; persist a lightweight Research Vault dossier |
| `gather-readings` | Copy PDFs from Paperpile into project articles/ folder for corpus analysis |
| `theory-mapper` | Map theoretical landscape across a corpus of papers |
| `method-audit` | Compare data collection methods and spot biases across papers |
| `evolution-timeline` | Chronological narrative of how a field's thinking evolved |
| `quote-mining` | Extract exact quotes with page numbers and argument mapping |
| `weakness-scanner` | Find weakest arguments and logical flaws across a literature |
| `replication-audit` | Audit replication status of key findings in a literature |
| `compile-knowledge` | Compile raw inputs (literature, meetings, logs) into a per-project knowledge wiki |
| `store-insight` | File a single research finding or insight into the project's knowledge wiki |
| `knowledge-lint` | Check compiled knowledge for contradictions, uncited claims, missing connections |
| `wiki-grow` | Auto-promote project knowledge articles into vault wiki concepts (Saturday cron; de-links unresolvable wikilinks) |
| `wiki-curate` | Read-only vault wiki audit — overlap clusters, tag coverage, backref health |
| `wiki-merge` | Collapse a wiki overlap cluster — merge bodies, rewrite wikilinks, denylist folded slugs |
| `sciscinet` | Query SciSciNet bibliometric database: field trends, venue intelligence, author networks, paper enrichment (disruption/novelty), citation graphs, raw SQL |
| `threat-search` | Adversarial literature review — find papers that threaten an idea (nested: research/) |
| `reading-note` | Capture pasted PDF highlights / reading notes for a paper and file them onto the atlas topic (`## Reading notes`) |

### Writing (1)

| Skill | Purpose |
|-------|---------|
| `proofread` | 7-category LaTeX proofreading scorecard (report only) |
| `journal-voice` | Extract writing patterns and editorial voice from a target journal |
| `review-response` | Systematic reviewer response drafting with classification, strategy, and tone checks |
| `voice-analyzer` | Analyze writing samples to create a portable voice profile and style guide |
| `voice-editor` | Edit content to match a voice profile (6-pass workflow, 4 editing modes) |
| `figure` | Generate publication-quality academic figures (statistical plots, TikZ diagrams, multi-pass pipeline) |

### Theory & Proof (6)

| Skill | Purpose |
|-------|---------|
| `math-proof` | Write one complete, gap-free mathematical proof in a single careful pass — state-before-show, every term signed, full intermediate steps |
| `proof-readability` | Post-verification exposition pass for already-verified proofs — 6 layers (architecture, signposting, line-level justification, notation, …) |
| `numerical-check` | R1 verification — falsify a self-authored monotonicity/threshold/comparative-static/closed-form claim by seeded Monte-Carlo sweep (dense sampling, interior grid, characterize violators) |
| `symbolic-check` | R2 verification — prove/refute an algebra/derivative/limit/closed-form step via sympy (`.equals()` True/False/None) |
| `lean-check` | R3 verification — machine-check a lemma in Lean 4 + mathlib (`lake build`, no-`sorry`); toolchain at `~/lean-verify/mathlib_verify` |
| `verify-math` | Umbrella — route a result's claims to R0–R3 and aggregate one verification report |

### Presentation (10)

| Skill | Purpose |
|-------|---------|
| `talk-deck` | Build a conference/seminar talk deck in the `paper-{venue}/talk/` convention — scaffold + rhetoric-driven Beamer deck (`user-beamer`) |
| `talk-page` | Generate a conference-talk landing page at `links.example.com/{venue}{year}` — mobile-first HTML, QR code, matching thank-you slide |
| `beamer-deck` | Rhetoric-driven Beamer slides using `user-beamer.sty` unified template with multi-agent review |
| `quarto-deck` | Reveal.js HTML presentations (teaching, informal talks) |
| `quarto-course` | Quarto course websites with slides and exercises |
| `project-deck` | Status decks for supervisor meetings and handoffs |
| `insights-deck` | Claude Code usage insights as a Beamer presentation |
| `latex-posters` | Research posters in LaTeX (beamerposter, tikzposter, baposter) |
| `translate-to-quarto` | Translate Beamer LaTeX slides to Quarto RevealJS |
| `pptx` | Create, read, edit, or manipulate PowerPoint files |

### LaTeX & Bibliography (13)

| Skill | Purpose |
|-------|---------|
| `latex-polish` | Deep visual-quality review after `latex` clean build — source-pathology lint + vision check of rendered PDF pages |
| `bib-rekey` | Rekey a project `.bib` to Paperpile canonical citekeys (preserving entry content), then remap every `\cite` in the `.tex` |
| `latex` | **Default compiler** — autonomous error resolution, citation audit, quality scoring |
| `latex-health-check` | Compile all projects, auto-fix, check cross-project consistency |
| `latex-template` | Compare preamble against working paper template (report + apply) |
| `latex-scaffold` | Convert Markdown draft into buildable LaTeX project (md→tex) |
| `bib-validate` | Cross-reference `\cite{}` keys against .bib files + Paperpile library; deep mode flags likely-fabricated entries (LLM hallucination detection) (report only) |
| `bib-parse` | Extract citations from a PDF, generate validated `.bib`, stage for Paperpile import. Phase 1.5 skeleton-confirmation gate for ≥10 references |
| `bib-filter` | Filter a .bib file to only entries actually cited in a .tex project |
| `bib-coverage` | Compare project `.bib` against a Paperpile project/topic folder to find uncited papers and unfiled references |
| `tikz` | Audit and repair residual TikZ visual collisions (overlapping labels, arrows crossing boxes) using mathematical gap/Bézier calculations — no eyeballing |
| `orcid-fill` | Insert ORCID iDs into a paper's `\author{}` block from vault people frontmatter; doc-class-aware macro choice (`\orcidID`/`\orcid`/`\orcidlink`); idempotent |
| `latex-diff` | Compare two versions of a LaTeX doc (files / dirs / git revisions) — human summary + severity-graded semantic changes |

### Submission (11)

| Skill | Purpose |
|-------|---------|
| `camera-ready` | Convert an accepted anonymous submission to camera-ready + implement accepted reviews (de-anonymise, copyright, section numbers, optional appendix moves, QA) |
| `venue-fork` | Fork a paper into a second-venue submission variant — CFP concurrency check, new Overleaf project, doc-class conversion, page-budget refit to appendices, writeback |
| `anonymous-artifact` | Push the in-tree `github-repo/` artifact to a private GitHub repo, mint an anonymous.4open.science URL (semi-automated), and write back to vault submission, paper LaTeX, and atlas. Three-layer sanitization. |
| `pre-submission-report` | All quality checks in one dated report |
| `retarget-journal` | Switch paper to different journal (rename, reformat, rekey) |
| `strategic-revision` | Referee comments PDF → DAG-validated revision master plan (atomic parsing, dependency graph, critical path, blocks A-E, venue strategy) |
| `synthesise-reviews` | Synthesise parallel review reports into a prioritised revision plan |
| `brief-compliance-check` | Check LaTeX submission against assessment brief (deliverables, word limits, required files) |
| `research-grants` | UK-first research grant proposals (UKRI: ESRC/EPSRC/AHRC; Leverhulme; British Academy; Horizon Europe ERC/MSCA) — scheme selection, Case for Support, FEC budgeting, impact narrative |
| `preprint` | Create a preprint / working-paper variant of an existing paper; forks the Overleaf project with `your-template` template and wires a local symlink |
| `archive-paper-draft` | Archive a paper draft after deferral/rejection/withdrawal: snapshot to `archive/`, drop Overleaf symlink, prompt to delete Overleaf project |

### Project Setup & Session (27)

| Skill | Purpose |
|-------|---------|
| `init-project-research` | Full project scaffold (interview, git, Overleaf, Atlas topic, vault pipeline entry) |
| `init-project-course` | Course/module folder scaffold |
| `init-project-light` | Lightweight scaffold (CLAUDE.md only, no git/vault) |
| `init-project-orchestration` | Add project agents, commands, and planning to a research project |
| `init-paper-book` | Scaffold a new educational companion book for a paper; vault-rendered via atlas, deployed to `books.example.com/<slug>/` |
| `project-safety` | Safety rules and folder structures to prevent data loss |
| `session-log` | Timestamped progress logs for session continuity |
| `session-close` | End-of-session closing protocol — auto-detects project type (general vs research) and runs appropriate checks |
| `update-focus` | Structured update to current-focus.md |
| `session-health` | On-demand session health check |
| `project-status` | Per-project recap to resume work: venue, deadlines, where you left off, recent activity, open issues, next 3 actions. Read-only synthesis from CLAUDE.md + atlas + vault + reviews/INDEX.md + logs + git |
| `handoff` | Persistent shared handoff for Claude→Claude, Codex→Codex, and cross-client/cross-machine continuation |
| `codex-handoff` | Target-specific `$handoff` alias for a receiving Codex session |
| `claude-handoff` | Target-specific `$handoff` alias for a receiving Claude session |
| `sync-ai-infra` | Diagnose, render, import, and deploy shared Claude/Codex infrastructure on either machine |
| `save-context` | Save information to context library files |
| `task-management` | Daily planning, weekly reviews, meeting actions, vault |
| `ideas` | Capture improvement ideas for the infrastructure |
| `memory-cleanup` | Prune, merge, and abstract MEMORY.md entries |
| `update-project-doc` | Update a project's own docs to reflect current state |
| `checkpoint` | Save session state to survive context compaction or handoff between sessions |
| `restore` | Restore session state from a checkpoint after compaction or in a new session |
| `email-digest` | Scan Gmail labels, score/deduplicate, generate categorised markdown digest |
| `decision-toolkit` | Structured decision-making frameworks with bias checking and scenario analysis |
| `file-organizer` | Organize files and directories: analyze, deduplicate, restructure with safety checks |
| `portfolio-briefing` | Monday-morning research portfolio briefing: atlas state, deadlines, stale-but-active projects, novelty-reviewer deltas, suggested venue retargets |
| `process-inbox` | Triage the maintenance inbox at `atlas.example.com/inbox` interactively; action each item (done/drop/snooze) with side-effects to atlas, vault submissions, venue files, tasks |

### Code & Analysis (11)

| Skill | Purpose |
|-------|---------|
| `cross-language-check` | Cross-language replication: same specification in a second language (R/Python/Stata/Julia), compare estimates within 0.1% tolerance |
| `code-archaeology` | Review and document old code, data, and analysis files |
| `pipeline-manifest` | Map scripts to inputs, outputs, and paper figures/tables |
| `python-env` | Python environment management (enforces uv) |
| `audit-project-research` | Audit project against init-project-research template |
| `audit-paper-book` | Sync a paper-book companion to a revised paper; detect bib / figure / numeric / structural / Overleaf-link drift |
| `audit-project-course` | Audit course folder against init-project-course template |
| `webapp-testing` | Playwright-based web app testing with server lifecycle management. *From Anthropic.* |
| `frontend-design` | Distinctive, production-grade frontend interfaces (anti-AI-slop aesthetics). *From Anthropic.* |
| `playwright-cli` | Automate browser interactions, test web pages, and work with Playwright tests |
| `test-iterate-loop` | Autonomously iterate on a code project until tests pass: root-cause failures, apply minimal fixes, retry. Generic over Python/R/Julia/HPC |

### Experimental & Data (14)

| Skill | Purpose |
|-------|---------|
| `locked-llm-experiment` | Scaffold a pre-locked, gate-enforced LLM scoring experiment — design-lock doc, hash-bound corpus, model lockfile gating runs, refusals/parse-fails as analysed outcomes |
| `data-analysis` | End-to-end analysis pipeline (EDA, estimation, publication output) across R/Python/Stata/Julia |
| `computational-experiments` | Scaffold, run, and publish computational research experiments (algorithm skeletons, config-driven sweeps, seed-deterministic runners, publication figures) |
| `experiment-design` | Experimental and survey design: power analysis, PAP, QSF parsing, survey construction |
| `causal-design` | Identification strategy design and audit (DiD/IV/RDD/SC/event study) |
| `synthetic-data` | Generate structurally realistic synthetic datasets for pilot testing and power analysis |
| `event-studies` | DiD and event study implementation in R: TWFE vs modern estimators, plotting, diagnostics |
| `replication-package` | Replication package assembly, anonymization, and audit (replaces export-project-clean/anon) |
| `econ-data` | Fetch economic data from FRED, World Bank, Eurostat, ECB, OECD, EEX APIs using R |
| `r-econometrics` | General R econometrics: OLS, IV, panel, RDD, robust SEs, modelsummary table export |
| `econ-plots` | Economics-standard ggplot2 visualisations: coefficient plots, binscatter, RDD, density, marginal effects |
| `ethics-review` | Assess ethical risks: participant safety, data privacy, GDPR, AI ethics, ethics committee readiness |
| `figure-feedback` | Vision-based structured feedback on generated figures (PDF/PNG/SVG): correctness, anomalies, publication readiness |
| `preregister` | OSF-Standard or AsPredicted preregistration before data collection |

### Sync & Deploy (10)

| Skill | Purpose |
|-------|---------|
| `sync-repo` | Sync docs with system state for atlas, refpile, or private repos |
| `sync-public-repo` | Sync to public repo (flonat-research), then commit public repo |
| `sync-public-review` | Interactive review and editing of public sync allowlists |
| `sync-friends-repo` | Regenerate the friends distribution from private rules |
| `sync-resources` | Pull latest from cloned resource repos |
| `sync-permissions` | Sync global permissions into projects |
| `full-commit` | Commit and push the registry-selected maintain-and-push set with leak guard |
| `release` | Full publication pipeline: sync, version bump, commit, tag, publish |
| `amend-recent-commits` | Rewrite messages of recent git commits without `rebase -i` (which is blocked in the harness) |
| `pre-commit-audit` | Fast pre-commit safety scan: file size, anonymity (author/affiliation strings in tex/bib), hardcoded secrets |

### Audit & Quality (14)

| Skill | Purpose |
|-------|---------|
| `pages-audit` | Functional/data-integrity audit of atlas web pages — BFS link crawl + invariants (taxonomy canon, review-state freshness, count parity); cron-able, optional --semantic pass |
| `tidy-project-reviews` | Retrofit project to `review-artefact-routing` rule: move stray `*-REPORT.md` / `*-REVIEW.md` files into `reviews/<source>/YYYY-MM-DD.md` with provenance classification (AI vs human). `git mv` preserves history. Read-only `--dry-run` by default. |
| `review-recap` | Per-paper retrospective inventory of review skills + agents already run. Coverage matrix, aggregate open issues, pre-submission gap check. Read-only stdout. |
| `system-audit` | Parallel audits across skills, hooks, agents, rules, docs |
| `external-audit` | External LLM audit of any repo (atlas, refpile, private, public, friends) via Codex/Gemini |
| `repo-doc-audit` | Documentation quality audit for any repo (atlas, refpile, private, public, friends) |
| `docs-consistency` | Cross-cutting doc review: count consistency, component coverage, stale refs, public-private sync, user manual |
| `skill-health` | See invocation counts, success rates, and health status for skills |
| `feedback-review` | Review accumulated feedback signals and generate skill improvement proposals |
| `multi-repo-audit` | Orchestrates system-audit + per-repo repo-doc-audit in parallel across all infrastructure repos; produces consolidated dashboard with cross-repo inconsistency checks |
| `ui-critic` | Scored adversarial audit of a web package's UI: rendered page capture + four parallel specialist sub-agents (hierarchy/theme, accessibility, HTMX patterns/copy, aesthetic) with fixer-actionable report |
| `code-suite` | Parallel multi-angle code-side audit before replication: code-review + code-paper-auditor + reproducibility-auditor in parallel + auto-synthesise |
| `review-cluster` | Mid-draft adversarial review: paper-critic + domain-reviewer + claim-verify + blindspot in parallel, then auto-synthesise into a prioritised revision plan |

### Skill Lifecycle (5)

| Skill | Purpose |
|-------|---------|
| `skill-extract` | Extract session knowledge into a new persistent skill |
| `skill-preflight` | Pre-flight duplicate check before creating new skills/agents |
| `skill-creator` | Create, iterate, and benchmark skills with eval viewer and description optimizer. *From Anthropic.* |
| `rate` | Rate the last skill invocation (good/needs-work) to feed feedback synthesis |
| `paper-to-agent` | Turn a paper's method + code into a reusable agent or skill (nested: research/) |

### Machine & Radar (4)

| Skill | Purpose |
|-------|---------|
| `machine-inventory` | Audit machine environment (Homebrew, dotfiles, credentials, dev tools, nested repos, MCP servers) |
| `machine-evaluation` | Holistic review of machine setup from snapshots: missing tools, redundant apps, cross-machine parity |
| `radar` | Search the web for Claude Code updates, AI workflow patterns, new repos, and MCP ecosystem news |
| `radar-integrate` | Convert saved radar tips into infrastructure changes (new skills, rules, cloned repos) |

### Infrastructure (10)

| Skill | Purpose |
|-------|---------|
| `chatgpt-pro` | Ask GPT-5.5 Pro (web-UI-only extended-thinking model) a hard question with a tight, secret-free file set, via the headless Oracle daemon on the Mac Mini. Safety preflight before every send |
| `email-triage` | Batch-analyse recurring system-email noise — cluster by emitter, recommend silencing/fixing |
| `tailscale-mosh-recover` | Diagnose + recover headless Mac mini mosh after Tailscale update/restart. Two layers: daemon health (GUI-vs-Homebrew dual-install, switch to launchd) + stale `mosh-server` cleanup on old Tailscale IP. Symptoms include "could not get canonical name", "Tailscale.CLIError error 1" |
| `postmortem` | Structured post-mortem for incidents and stuck sessions |
| `rename-project-research` | Rename an atlas topic slug across all connected files (topics, themes, paperpile, merge-reviewed) |
| `mcp-builder` | Guide for creating MCP servers (Python/FastMCP or TypeScript). *From Anthropic.* |
| `wire-shared-package` | Wire a shared Python package as an editable dependency across projects |
| `scheduled-job` | Create, diagnose, or manage scheduled launchd jobs on the Mac Mini |
| `plan-to-issues` | Convert an approved plan into GitHub issues with dependencies (nested: engineering/) |
| `swarm-setup` | Multi-agent orchestration via GitHub issues, branches, PRs (nested: engineering/) |

### Document Formats (3)

| Skill | Purpose |
|-------|---------|
| `docx` | Create, read, edit, or manipulate Word documents |
| `pdf` | Read, extract, combine, split, rotate, watermark PDF files |
| `xlsx` | Create, read, edit spreadsheets (.xlsx, .csv, .tsv) |

### Meetings (8)

| Skill | Purpose |
|-------|---------|
| `meetings-debrief` | Post-meeting debrief — compare outcomes to prep intentions |
| `meetings-prep` | Interactive meeting preparation with relationship briefs |
| `meetings-recap` | Daily digest of meetings — decisions, action items, themes |
| `meetings-weekly` | Weekly meeting synthesis — themes, decision arcs, stale commitments |
| `meetings-search` | Search past meeting transcripts and voice memos |
| `meetings-list` | List recent meetings and voice memos |
| `meetings-verify` | Verify minutes setup — model, mic, directories |
| `meetings-cleanup` | Manage old recordings — archive, delete, disk space |

### Teaching (2)

| Skill | Purpose |
|-------|---------|
| `grade-assignment` | Grade banded-rubric student submissions (e.g., PB130 Mixed Methods Poster) with two-tier output (instructor + student feedback), parallel isolated review, and calibration pass |
| `course-reading-list` | Parse a syllabus, extract topics + learning outcomes, search scholarly + Paperpile per section, produce Markdown reading list with summaries and discussion questions |

**Total: 199 skills across 18 categories.**

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
| `reference-resolution.md` | Logic for resolving Paperpile membership, citekeys, metadata, and topic folders |
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
