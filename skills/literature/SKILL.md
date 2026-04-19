---
name: literature
description: "Use when you need academic literature discovery, synthesis, or bibliography management. Supports standalone searches and end-to-end project pipelines with vault sync and auto-commit."
allowed-tools: Bash(curl*), Bash(wget*), Bash(mkdir*), Bash(ls*), Bash(uv*), Bash(cd*), Bash(git*), Bash(cat*), Bash(date*), Bash(scholarly*), Bash(paperpile*), Bash(taskflow-cli*), Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Task, Agent, Skills_by_label
argument-hint: "[topic-query] or <topic-slug> for full pipeline"
---

# Literature Skill

**CRITICAL RULE: Every citation must be verified to exist before inclusion.** Never include a paper you cannot find via web search. Hallucinated citations are worse than no citations.

**DOI INTEGRITY RULE: Every DOI must be programmatically verified before entering any `.bib` file.** Sub-agents hallucinate plausible-looking DOIs that resolve to wrong papers (e.g., correct journal prefix, wrong suffix). The ONLY reliable verification is `scholarly scholarly-verify-dois` with title-matching (see Phase 4). A DOI that resolves to a different title than expected is WRONG — treat it the same as a missing DOI.

**CITATION KEY RULE: ALWAYS use Better BibTeX-format keys (e.g., `Author2016-xx`).** When merging into an existing `.bib`, match existing keys. Never generate custom keys (`AuthorYear`, `AuthorKamenica2017`, etc.) or retain non-standard keys unless the user explicitly says otherwise.

**Python:** Always use `uv run python`. Never bare `python`, `python3`, `pip`, or `pip3`.

**LIBRARY-FIRST RULE: ALWAYS check Paperpile BEFORE any external search.** Call `paperpile search-library` for the topic in Phase 1. Do not skip this even if no `.bib` file exists yet. Papers already in either library should be reused, not re-discovered.

**PREPRINT RULE: Always prefer the published version.** If a paper is found on arXiv, SSRN, NBER, or any working paper series, search for a published journal/conference version using `scholarly scholarly-search`. Only cite a preprint if no published version can be found. This applies at every phase: Phase 2 (discovery), Phase 4 (verification), and Phase 6b (bib-validate runs the full preprint staleness check from `bib-validate/references/preprint-check.md`).

**CAUSAL LANGUAGE RULE: Match the strength of language to the study design.** Reserve causal verbs ("causes", "increases", "reduces", "leads to") for findings from designs that warrant causal inference (experiments, RCTs, credible quasi-experiments with clear identification). For observational/correlational work, use: "is associated with", "predicts", "correlates with". When summarising a paper in the narrative or bibliography annotations, match the language to the design — not to the authors' own claims. State disagreements precisely: who claims what, on what evidence. Do not flatten into "the literature is mixed."

> Comprehensive academic literature workflow: discover, verify, organize, synthesize.
> Uses parallel sub-agents to search multiple sources, verify citations, and fetch PDFs concurrently.
> Supports two modes: **standalone** (free-form query) and **pipeline** (topic-slug for full project-aware cycle with vault sync and auto-commit).

## Modes

| Mode | Invocation | What it does |
|------|-----------|-------------|
| **Standalone** | `/literature [topic query]` | Search + verify + bib + synthesis. No project context needed. |
| **Pipeline** | `/literature <topic-slug>` | Full cycle: resolve project → search → verify → bib → bib-validate gate → vault sync → auto-commit |
| **Deep** | `/literature --deep [query]` | Standalone or pipeline + iterative gap-filling loop (Phase 4.5). Also triggered by "deep", "thorough", or "comprehensive review" in the query. |

**How to detect mode:** If the argument matches an atlas topic slug (check `~/Research-Vault/atlas/` for a matching `.md` file), run in Pipeline mode. Otherwise, run in Standalone mode. When in doubt, ask.

## Shared References

- Concept validation gate: `shared/concept-validation-gate.md` — validate concept before synthesis
- Method-fitness gate: `shared/method-fitness-gate.md` — validate RQ-method alignment before search (pipeline mode only)
- Integrity gates: `shared/integrity-gates.md` — pipeline-blocking verification checkpoints
- Material passport: `shared/material-passport.md` — artifact provenance and staleness tracking
- Checkpoint resumability: `shared/checkpoint-resumability.md` — save/resume on crash (pipeline mode)
- LEARN tag routing: `shared/learn-tag-routing.md` — auto-inject corrections at invocation
- Escalation protocol: `shared/escalation-protocol.md` — escalate when research question is vague

## When to Use

- Starting a new research project
- Writing a literature review section
- Building a reading list on a topic
- Finding specific citations
- Creating annotated bibliographies
- End-to-end literature pipeline for a research topic (pipeline mode)

---

## Pipeline Mode: Project Context Resolution

**Only in pipeline mode** (topic slug argument). Skip entirely in standalone mode. Find the atlas topic file (`find ~/Research-Vault/atlas/ -name "<topic-slug>.md"`), read frontmatter (`title`, `project_path`, `outputs`, `connected_topics`), resolve `PROJECT="$(cat ~/.config/task-mgmt/research-root)/<project_path>"`, locate the `.bib` file (ask if multiple), report context and wait for confirmation before proceeding to Phase 0.

---

## Architecture: Orchestrator + Sub-Agents

Phases: 0 session-log → 1 pre-search → 1.25 Perplexity (opt) → 1.5 search plan gate → 2 parallel search → 2b CLI council (opt) → 2.5 snowball (opt) → 3 dedup/rank → 3b SciSciNet (opt) → 4 parallel verification → 4.5 deep loop (opt) → 5 PDF download → 6 assemble bib → 6b validate → 6c sync → 6d pipeline completion → 7 synthesis.

**Key principle:** Sub-agents handle independent, parallelizable work. Merging, deduplication, and synthesis stay with the orchestrator because they need the full picture.

**Full agent prompt templates for all phases:** [`references/agent-templates.md`](references/agent-templates.md)

---

## Phase 0: Session Log & Compact (Mandatory)

Literature searches are context-heavy. **Always** run `/session-log` before starting to create a recovery checkpoint.

---

## Phase 1: Pre-Search Check (Direct)

Check for existing `.bib` files in project root, `/references`, `/bib`, `/bibliography`:

1. Parse existing entries to avoid duplicates and understand context
2. Identify gaps — note if bibliography skews toward certain years/methods
3. Compile list of existing citation keys to pass to sub-agents
4. **MANDATORY: Check Paperpile library** — call `paperpile search-library` for the search topic. Also call `paperpile get-items-by-label` if a relevant label exists. This finds papers the user already has, preventing re-discovery of known work. Mark these as **ALREADY IN PAPERPILE** and reuse their citation keys. If the `paperpile` CLI is unavailable, log a warning and continue — but always attempt the call.
5. **Resolve topic label** — call `paperpile get-labels` to find the label for the current topic. This label is used in Phase 6c for reporting.
7. **Check source availability** — run `scholarly source-status --json` to see which sources are active (OpenAlex always; Scopus and WoS if API keys are set). Report this so search agents know what coverage to expect.

**Steps 4 and 5 are NOT optional.** Every literature search must check both reference managers before external discovery. This prevents re-discovering papers already in the library and identifies migration candidates early.

---

## Phase 1.25: Perplexity Real-Time Grounding (Optional)

Advisory-only real-time grounding via Perplexity Sonar Pro (OpenRouter). Surfaces current terminology, named actors, and flashpoint debates that OpenAlex/Scopus/WoS miss due to indexing lag. **Hard gate:** skip silently if `OPENROUTER_API_KEY` is not set. Output feeds Phase 1.5 — never enters `.bib` directly. Every named paper must still pass the Phase 4 DOI gate.

Full protocol (gate check, curl invocation, output usage, cost): [`references/perplexity-grounding.md`](references/perplexity-grounding.md)

---

## Phase 1.5: Search Plan & Confirmation Gate (Both Modes)

Present a search plan and wait for confirmation before launching any searches. Restate the RQ, list 3-6 queries grouped by **Track A (Substantive)** / **Track B (Empirical comparanda)** / **Track C (Methodological precedents)**, list seed authors/venues, note scope boundaries, and propose optional `year_min` / `year_max` filters (propagated to every Phase 2/4.5 search call via `--year-from/--year-to`). Flag book coverage if topic has major book-length treatments (political theory, area studies, organisational behaviour) — API search underrepresents books.

Full structure, presentation template, filter propagation, and book coverage rule: [`references/search-plan.md`](references/search-plan.md)

---

## Phase 2: Parallel Search (Sub-Agents)

CLI pre-fetch via `scholarly` commands (search, similar-works, author-papers, arxiv-search, exa-search-papers) writing to `/tmp/lit-search/*.json`, then spawn 2-3 Explore agents in parallel (Google Scholar, bibliometric, S2/arXiv, domain-specific). Both `scholarly` and `paperpile` CLIs work inside sub-agents — pre-fetch or let agents shell out directly.

Full CLI command list, output paths, and agent configuration: [`references/phase-2-search.md`](references/phase-2-search.md) | Agent prompt templates: [`references/agent-templates.md#phase-2-search-agent-templates`](references/agent-templates.md#phase-2-search-agent-templates)

---

## Phase 2b: CLI Council Search (Optional)

Multi-model literature search via `cli-council` — runs the same query through Gemini, Codex, and Claude for maximum recall. Use for broad reviews (20+ papers) or interdisciplinary topics.

**Full invocation, prompt template, and post-processing:** [references/cli-council-search.md](references/cli-council-search.md#phase-2b-cli-council-search-optional)

---

## Phase 2.5: Snowball Search (Optional — Main Context)

Uses S2's citation graph to expand the candidate pool. Pick 3-5 seed papers, run forward (`scholarly scholarly-citations`) and backward (`scholarly scholarly-references`) snowballing, filter to ≥5 citations, merge into Phase 3 pool. Use for broad reviews or when Phase 2 returned <15 papers. Enrich top candidates with `scholarly scholarly-paper-detail` for TLDR summaries.

Full protocol: [`references/snowball-search.md`](references/snowball-search.md)

---

## Phase 3: Deduplicate, Classify, and Rank (Direct)

1. **Merge** results from all search agents (Phase 2 + Phase 2b if used)
2. **Remove duplicates** — match on title similarity and DOI
3. **Field-framework extraction** — for each candidate, extract structured fields (Setting / Population / Method / Data / DV / IV / Key finding / Mechanism / Boundary). Always, even partial — feeds ranking, gap analysis, synthesis, and `/hypothesis-generation`.
4. **Rank** by relevance, citation count, and recency
5. **Select top N** to verify (typically 25-30 candidates for 20-25 verified)
6. **Assign batches** of ~5 for verification

Full field definitions, downstream uses, and breadcrumb format: [`references/field-framework.md`](references/field-framework.md)

---

## Phase 3b: SciSciNet Enrichment (Direct — Optional)

Additive enrichment via local SciSciNet API — adds `disruption_score`, `novelty_score`, `conventionality_score`, `fields`, and `is_hit_1pct`/`is_hit_5pct` flags to each candidate. Skip silently if `curl -sf http://localhost:8500/health` fails. Re-rank: boost `is_hit_1pct` and high `disruption_score` papers; prioritise high-conventionality papers for background sections.

Full protocol (curl invocation, re-ranking rules, coverage note, breadcrumb): [`references/scisciinet-enrichment.md`](references/scisciinet-enrichment.md)

---

## Phase 4: Parallel Verification (Sub-Agents)

Hard DOI gate. Six-step protocol:

1. **Batch DOI pre-verification** via `scholarly scholarly-verify-dois --json` — title-match check is mandatory (off-by-one DOI suffix hallucinations are the dominant failure mode)
2. **Find correct DOIs** for flagged papers via Crossref API → `scholarly-search` → web search (in order of reliability)
3. **Manual verification** of remaining papers — spawn general-purpose agents in parallel, ~5 papers each, using [`references/agent-templates.md`](references/agent-templates.md#phase-4-verification-agent-template)
4. **Final DOI gate** — re-run `scholarly-verify-dois` on all DOIs entering the `.bib`. Papers without DOIs flagged as `% NO DOI`.
5. **Assign confidence grades** — A (DOI + full metadata), B (stable identifier, no DOI), C (single non-canonical source)
6. **Working paper inclusion test** — include only if ≥2 of: high citations, established author, top venue, sole source for concept, verifiable forthcoming status

Full six-step protocol, title-matching rules, confidence grade criteria, and WP inclusion test: [`references/phase-4-verification.md`](references/phase-4-verification.md)

---

## Phase 4.5: Iterative Deep Loop (Optional)

**Trigger:** "deep", "--deep", "thorough", or "comprehensive review". Runs after Phase 4, before Phase 5. Prerequisites: ≥5 verified papers.

Each iteration: (1) gap analysis with era-gated checks for terminology/paradigm shifts, (2) targeted search via `scholarly` CLI + Explore sub-agents, (3) merge + dedup, (4) verify new papers. Convergence: 3 iterations OR <3 genuinely new papers per iteration OR user says "enough".

Full protocol: [`references/deep-loop-protocol.md`](references/deep-loop-protocol.md) | Agent templates: [`references/agent-templates.md#phase-45-deep-loop-agent-templates`](references/agent-templates.md#phase-45-deep-loop-agent-templates)

---

## Phase 5: Parallel PDF Download (Sub-Agents)

First, check Paperpile via `paperpile search-library` — mark papers with attached PDFs as SKIP, others as DOWNLOAD. Then spawn Bash agents in parallel (3-5 papers each) for the DOWNLOAD set. Best-effort — many papers are paywalled. Agent template: [`references/agent-templates.md#phase-5-pdf-download-agent-template`](references/agent-templates.md#phase-5-pdf-download-agent-template)

---

## Phase 6: Assemble Bibliography (Direct)

**Two outputs required:**

1. **`docs/literature-review/literature_summary.bib`** — always created, standalone, self-contained
2. **Project canonical bib** (e.g. `paper/references.bib`) — merge into it if it exists

Key rules: Better BibTeX-format keys (`Author2016-xx`); reuse Paperpile keys for entries already held; only VERIFIED papers; list ALL authors (never "et al."); seed each entry via `scholarly scholarly-paper-detail`; add `% Confidence: A/B/C` and `% WP criteria:` comments where applicable; every entry needs a connection note in `literature_summary.md`.

Full BibTeX format, rules, and connection-note protocol: [`references/bibliography-format.md`](references/bibliography-format.md)

---

## Phase 6b: Validate Bibliography (Mandatory)

After assembling the `.bib`, always run `/bib-validate`. Phase 4 verifies papers exist; `/bib-validate` catches a different class of issues (missing BibTeX fields, preprint staleness, DOI problems, author formatting, unused entries). Not optional — run every time new entries are added.

---

## Phase 6c: Sync to Reference Managers

Sync new references to Paperpile (primary reference manager); handles migration candidates and post-run maintenance. Append a Phase 6c breadcrumb to `.planning/state.md` or `.context/current-focus.md`.

Full steps + breadcrumb format: [`references/reference-manager-sync.md`](references/reference-manager-sync.md)

---

## Phase 6d: Pipeline Completion (Pipeline Mode Only)

Skip entirely in standalone mode. After Phase 6b passes (bib-validate clean) and Phase 6c completes: (1) vault sync via `taskflow-cli`, (2) knowledge wiki filing (if `knowledge/` exists), (3) auto-commit hard gate (only if bib-validate clean), (4) final summary.

Full steps (taskflow commands, knowledge filing, commit template, final summary format): [`references/pipeline-completion.md`](references/pipeline-completion.md)

---

## Phase 7: Synthesize Narrative (Direct or CLI Council)

Seven steps: (1) identify themes, (2) map intellectual lineage, (3) note current debates, (4) structured gap analysis (methodological / population-context / conceptual, each with "why it matters"), (5) negative evidence per cluster (mandatory — state explicitly if absent), (6) cross-cluster synthesis (tensions + implications), (7) Priority Reading Order (5–7 papers: review → foundational → frontier → gap/controversy).

Output types: narrative summary, literature deck, annotated bibliography, concise field synthesis (~400 words for "quick synthesis" requests). Use `[VERIFY]` tags for uncertain attributions (resolve before publication). For comprehensive reviews, run through `cli-council` for multi-model synthesis.

Full protocol (seven steps, concise field synthesis structure, [VERIFY] tags, multi-model invocation, `literature_summary.md` structure, output file tree): [`references/synthesis.md`](references/synthesis.md)

---

## Sub-Agent Guidelines

0. **Python: ALWAYS use `uv run python`.** Include this in every sub-agent prompt.
1. **Launch independent agents in a single message** for parallelism
2. **Be explicit in prompts** — sub-agents have no context
3. **Include skip lists** of existing citation keys
4. **Batch sizes:** 5 papers per verification agent, 3-5 per PDF agent
5. **Maximum 3 parallel agents at a time** — spawn in waves, write results to disk between waves. Each agent should write to a temp file (e.g., `/tmp/lit-search/agent-N.json`) rather than returning large payloads in-context. Summarise from files to avoid context overflow.
6. **Right agent type:** `Explore` for search, `general-purpose` for verification, `Bash` for downloads
7. **Tolerate partial failures** — continue with what you have

---

## Bibliometric API Structured Queries

Four bibliometric sources available via the `scholarly` CLI (and direct APIs as fallback). Includes CLI command table, OpenAlex workflows, Scopus query syntax, and WoS API tiers.

Full reference: [`references/bibliometric-apis.md`](references/bibliometric-apis.md) | API guides: [OpenAlex](references/openalex-api-guide.md), [Scopus](references/scopus-api-guide.md), [WoS](references/wos-api-guide.md)

---

## Reading Full Paper Text from arXiv

Download arXiv LaTeX source for full-text reading (equations, methodology, exact phrasing). Only works for arXiv papers with source available — for journal-only papers, use `/split-pdf`.

**Full instructions:** [references/cli-council-search.md](references/cli-council-search.md#reading-full-paper-text-from-arxiv)

---

## Cross-References

| Skill / Package | When to use instead/alongside |
|-------|-------------------------------|
| `/interview-me` | Develop a specific idea before searching |
| `/bib-validate` | **Mandatory** after assembling `.bib` (Phase 6b) — metadata quality, preprint staleness, DOI checks |
| `/bib-coverage` | Compare project `.bib` vs Paperpile label — find uncited papers and unfiled references |
| `/split-pdf` | Deep-read a paper found during search |
| `/gather-readings` | Run after literature to download PDFs for new papers |
| `/bib-coverage` | Run after literature to check uncited papers |
| `cli-council` | Multi-model search (Phase 2b) and synthesis (Phase 7) — `packages/cli-council/` |
| `paperpile` CLI | Search personal Paperpile library, extract PDF text/annotations, export BibTeX. Use in Phase 1 to check what's already in the library before searching externally. GROBID tools (`parse_pdf_metadata`, `parse_pdf_references`) extract structured metadata and bibliographies from PDFs — use after downloading to auto-extract refs without manual reading |
| `shared/reference-resolution.md` | Canonical lookup + filing sequence used by Phase 1 and Phase 6c |
| arXiv MCP tools | `scholarly arxiv-search`, `scholarly arxiv-get-paper`, `scholarly arxiv-search-category` — preprint search. See [references/arxiv-api-guide.md](references/arxiv-api-guide.md) |
| Exa MCP tools | `scholarly exa-search`, `scholarly exa-search-papers`, `scholarly exa-get-contents` — semantic web search, grey literature. Requires `EXA_API_KEY` |
| Deep loop protocol | [references/deep-loop-protocol.md](references/deep-loop-protocol.md) — iterative gap analysis + targeted search |
| `shared/worker-critic-protocol.md` | Inline review of synthesis output before reporting done |
| `shared/sources-cache.md` | Cache search results to avoid redundant API calls across sessions |

---

## Output Verification (Guard)

This skill writes files. Before any auto-commit, emit an outputs manifest and run the shared verifier. See [`skills/_shared/verify-outputs.md`](../_shared/verify-outputs.md) for the full protocol.

**Required tail steps** (before `git commit`):

1. Write manifest to `<project>/.claude/state/outputs-manifest-<UTC-timestamp>.json` listing every file this skill claims to have written in this invocation (paths relative to the project root).
2. Run:

   ```bash
   python3 "$HOME/.claude/skills/_shared/verify_outputs.py" \
       --manifest "$MANIFEST" \
       --project-root "$PROJECT_ROOT"
   ```

3. If the verifier exits non-zero, **do not commit** — surface the missing-files list to the user and stop. The verifier has already logged an `error` entry to `~/.claude/ecc/skill-outcomes.jsonl`, which feeds the launcher dashboard.

**Why:** closes the "hallucinated outputs" failure class (commit `b2cff75`, 2026-04-18).
