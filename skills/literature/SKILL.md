---
name: literature
description: "Use when you need academic literature discovery, synthesis, or bibliography management. Supports standalone searches and end-to-end project pipelines with vault sync and auto-commit."
allowed-tools: Bash(curl*), Bash(wget*), Bash(mkdir*), Bash(ls*), Bash(uv*), Bash(cd*), Bash(git*), Bash(cat*), Bash(date*), Bash(scholarly*), Bash(paperpile*), Bash(taskflow-cli*), Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Task, Agent
argument-hint: "[topic-query] or <topic-slug> for full pipeline"
---

# Literature Skill

Comprehensive academic literature workflow: discover, verify, organise, synthesise. Uses parallel sub-agents to search multiple sources, verify citations, and fetch PDFs concurrently.

> **Web alternative**: a lighter-weight version of this workflow runs at [literature.example.com](https://literature.example.com) (`packages/literature-workspace/`) — keyword/file-upload search across biblio-sources + RefPile, with Sonnet-driven synthesis. Useful for collaborators (CF Access auth) or quick discovery sessions where you don't need vault sync, DOI hard-gating, or pipeline mode. Use the CLI skill when you need verified citations entering a `.bib` file or full Phase 5 synthesis with negative-evidence + cross-cluster analysis.

## Hard Rules

### Existential — block submission

These rules protect against the highest-cost failure modes. Violation invalidates the output.

1. **Every citation must be verified to exist before inclusion.** Never include a paper you cannot find via web search. Hallucinated citations are worse than no citations.
2. **Every DOI must be programmatically verified before entering any `.bib` file.** Sub-agents hallucinate plausible-looking DOIs that resolve to wrong papers (correct journal prefix, wrong suffix). The only reliable verification is `scholarly scholarly-verify-dois` with title-matching (Phase 3). A DOI that resolves to a different title is WRONG — treat it the same as a missing DOI.
3. **The narrative synthesis ALWAYS lives at `docs/literature-review/literature_summary.md`.** Never in `paper/`, `paper-*/`, or any Overleaf-synced directory. The `paper/` directory is LaTeX-only. Markdown files there leak onto Overleaf and pollute the submission folder. Canonical filename: `literature_summary.md` (never `_synthesis.md`, `synthesis.md`, ad-hoc names).

---

### Format — catch in review

These rules govern style and consistency. Violation produces fixable artefacts, not invalid claims.

4. **Library-first.** Always check Paperpile via `paperpile search-library` BEFORE any external search (Phase 1). Papers already held should be reused, not re-discovered.
5. **Prefer the published version over preprints.** If a paper is found on arXiv, SSRN, NBER, or any working paper series, search for a published journal/conference version via `scholarly scholarly-search`. Cite a preprint only if no published version exists. Enforced in Phase 2 (discovery), Phase 3 (verify), and Phase 4 (`/bib-validate` runs the full preprint staleness check).
6. **Better BibTeX-format keys** (e.g., `Author2016-xx`). When merging into an existing `.bib`, match existing keys. Never generate custom keys (`AuthorYear`, `AuthorKamenica2017`, etc.) unless explicitly told otherwise.
7. **Match causal language to study design.** Reserve causal verbs ("causes", "increases", "reduces") for designs that warrant causal inference (experiments, RCTs, credible quasi-experiments). For observational work use "is associated with", "predicts", "correlates with". Match the language to the design — not the authors' own claims. State disagreements precisely; do not flatten into "the literature is mixed."
8. **Python: always `uv run python`.** Never bare `python`, `python3`, `pip`, `pip3`.

> Known corrections (notation, method, citation, domain) are auto-injected from `MEMORY.md` via the LEARN-tag-routing protocol at invocation. See `shared/learn-tag-routing.md`.

---

## Sprint Contract — Output Handoff



**Protocol:**

1. **Pre-commitment (Phase 1.4 hook).** Before generating the search plan, load the contract and paraphrase all 5 acceptance dimensions (D1 `bib_completeness`, D2 `dedup`, D3 `coverage_attestation`, D4 `venue_aligned`, D5 `freshness`). The paraphrase anchors output against the criteria rather than rationalising backwards. Skip in standalone mode where no downstream consumer is declared.


3. **Self-check (Phase 4.3 hook).** Before signalling pipeline completion, verify each dimension against its `verification_rule`. F1 (DOI verification fails, severity 90) or F2 (generated-key pattern with no DOI, severity 70) triggers `producer_decision=revise_before_handoff` — re-run Phase 3 verification, do not hand off.

4. **Failure-mode cross-reference** ([`docs/reference/failure-modes.md`](../../docs/reference/failure-modes.md)): contract F1 → taxonomy F1 fabricated citation (⛔ hard fail); contract F2 → taxonomy F4 invented bib key (⚠️ soft fail).

5. **Override ladder.** Round 1: re-run `paperpile search-library` + `scholarly scholarly-verify-dois`. Round 2: dispatch the `claim-verify` agent. Round 3: human review of the literature report.

Full schema + protocol: [`docs/reference/sprint-contract-protocol.md`](../../docs/reference/sprint-contract-protocol.md).

---

## Modes

| Mode | Invocation | What it does |
|------|-----------|-------------|
| **Standalone** | `/literature [topic query]` | Search + verify + bib + synthesis. No project context needed. |
| **Pipeline** | `/literature <topic-slug>` | Full cycle: resolve project → search → verify → bib → bib-validate gate → vault sync → auto-commit. |
| **Deep** | `/literature --deep [query]` | Standalone or pipeline + iterative gap-filling loop after Phase 3. Also triggered by "deep", "thorough", or "comprehensive review" in the query. |
| **Autonomous** | `/literature --autonomous <slug>` (or `-y`) | Pipeline + run end-to-end without inter-phase pauses. Stackable with `--deep`. Hard gates still run; defaults used at every choice point. See "Autonomy" below. |

**Mode detection:** if the argument matches an atlas topic slug (`~/vault/atlas/<slug>.md`), run in Pipeline mode. Otherwise, Standalone. When in doubt, ask. Deep is a flag on either base mode. Autonomous is a flag on either base mode.

**Pipeline mode — project context resolution:** find the atlas topic file (`find ~/vault/atlas/ -name "<topic-slug>.md"`), read frontmatter (`title`, `project_path`, `outputs`, `connected_topics`), resolve `PROJECT="$(cat ~/.config/task-mgmt/research-root)/<project_path>"`, locate the `.bib` file (ask if multiple). Report context and wait for confirmation before Phase 1 — **unless `--autonomous` is set**, in which case ambiguity is resolved by picking the largest `.bib` file in the project (typically `paper-*/paper/references.bib` or `docs/literature-review/literature_summary.bib`) and logging the choice.

## Autonomy

Per the global `--autonomous` / `-y` convention defined in `~/.claude/rules/phased-work.md` § "Autonomy flag convention". When set:

- **No Phase 1.4 search-plan confirmation** — emit the plan to the session log and proceed
- **No Phase 2.2 dedup/rank pause** — apply default filters and continue
- **No Phase 3.5 deep-loop "continue?" prompts** — run up to 3 iterations (default), stop when <3 new papers per iteration
- **No Phase 4.3 bib-validate "review and continue" pause** — `/bib-validate` still runs as a hard gate; warnings are logged and reported at the end; only `F1 fabricated citation` or `F2 invented bib key` block the run
- **No `AskUserQuestion` mid-run** — every choice point uses the recommended/default option and logs the decision
- **Auto-commit at end** in pipeline mode (subject to Phase 4.6 verifier)
- **Single end-of-run report** is the only mandatory user-facing output

Hard correctness gates that still fire even with `--autonomous`:
- DOI verification (Phase 3 Step 1/4) with title-match — fabricated DOIs are F1/blocker
- **Paperpile membership resolution (Phase 3 Step 5) — `lookup-by-doi` on every verified DOI; never tag `NEW` off a topic-search miss**
- Sprint-contract D1–D5 self-check (Phase 4.3 hook)
- Phase 4.6 outputs-manifest verifier (manifests must verify or commit is blocked)
- The forbid-list for sub-agents (still applied)

Recommended invocations:

```
/literature --autonomous effort-weighted-yield                # pipeline, end-to-end, standard depth
/literature --deep --autonomous effort-weighted-yield         # exhaustive, end-to-end
/literature -y effort-weighted-yield                          # short form
```

---

## Optional Enrichment

Five enrichment passes that fire conditionally. They do not get their own phase headers — each integrates into a base phase as noted.

| Enrichment | Trigger | Integrates after | Reference |
|-----------|---------|-----------------|-----------|
| **Perplexity grounding** | `OPENROUTER_API_KEY` set; advisory real-time grounding wanted | Phase 1.2 (pre-search) | [`references/perplexity-grounding.md`](references/perplexity-grounding.md) |
| **CLI council search** | Broad reviews (20+ papers) or interdisciplinary topics | Phase 2.1 (parallel search) | [`references/council-cli-search.md`](references/council-cli-search.md) |
| **Snowball search** | Phase 2 returned <15 papers OR broad review | Phase 2.1 (parallel search) | [`references/snowball-search.md`](references/snowball-search.md) |
| **SciSciNet enrichment** | `curl -sf http://localhost:8500/health` succeeds | Phase 2.3 (rank), before Phase 3 | [`references/scisciinet-enrichment.md`](references/scisciinet-enrichment.md) |
| **Iterative deep loop** | Deep mode (`--deep` or keyword); ≥5 verified papers | Phase 3 (verify), before Phase 4 | [`references/deep-loop-protocol.md`](references/deep-loop-protocol.md) |

Output from any enrichment must still pass the Phase 3 DOI gate before entering the `.bib`.

---

## Architecture

Sub-agents handle independent, parallelisable work (search, verification, PDF download). Merging, deduplication, and synthesis stay with the orchestrator because they need the full picture. Full agent prompt templates: [`references/agent-templates.md`](references/agent-templates.md).

---

## Phase 1: Prep

> standalone: yes (skip 1.3, 1.4) | pipeline: yes | deep: yes

### 1.1 Session log + checkpoint

Literature searches are context-heavy. Always run `/session-log` to create a recovery checkpoint per [`shared/checkpoint-resumability.md`](../shared/checkpoint-resumability.md). Pipeline mode writes a JSON checkpoint after each phase so a crash resumes from the last completed phase, not from scratch.

### 1.2 Pre-search check

Find existing `.bib` files in project root, `/references`, `/bib`, `/bibliography`. Then:

1. Parse existing entries to avoid duplicates and understand context.
2. Identify gaps — note if the bibliography skews toward certain years/methods.
3. Compile the list of existing citation keys to pass to sub-agents.
4. **Mandatory: check Paperpile.** Call `paperpile search-library` for the topic (and `paperpile get-items-by-label` if a relevant label exists) to *discover* what the library already holds and reuse those citation keys. This is topic discovery, **not** a membership test. **Membership/`NEW` tagging is decided authoritatively by DOI** (`paperpile lookup-by-doi`) in **Phase 3 Step 5** (the integrity gate), per [`shared/reference-resolution.md`](../shared/reference-resolution.md) § Membership Check — never default a paper to `NEW` because this topic search missed it. A topic-search hit here is a reuse *hint*; a topic-search miss proves nothing. If `paperpile` CLI is unavailable, log a warning and continue.
5. **Resolve topic label** via `paperpile get-labels` for the current topic. Used in Phase 4 sync reporting.
6. **Check source availability** via `scholarly source-status --json` (OpenAlex always; Scopus/WoS if API keys are set). Report so search agents know coverage.
7. **Check scout-audit reports.** Glob `~/vault/reports/scout/portfolio/*<topic-slug>*.md` and `*<topic-keyword>*.md`. If a recent (≤90 days) report exists, parse the **Closest prior works** and **Most likely scoopers** sections — feed authors/papers/groups directly to Phase 2 search agents as seeds. This avoids re-discovering what scout already surfaced.
8. **Cold-start branch.** If steps 4–7 yield <3 papers AND project status is `Idea` or `Drafting` (read from atlas topic frontmatter or skip if standalone), enter **scaffold-seeded mode**:
   - Search the project for a canonical scaffold document (`to-sort/*scaffold*.md`, `to-sort/*sketch*.md`, or `docs/*scaffold*.md`). Read it for the canonical reference list.
   - For canonical CS/ML references explicitly named in the scaffold (e.g. "Ghorbani-Zou Data Shapley ICML 2019"), use `scholarly arxiv-get-paper --arxiv-id <id>` directly when arXiv IDs are known — broad `scholarly-search` returns high-citation noise (climate, hydrogen) on generic ML queries like "data shapley".
   - For DOI-only known references, use Crossref via `scholarly scholarly-verify-dois` (faster + more reliable than search for targeted lookups; see [`reference_mcp_scholarly_search.md`](../../memory/reference_mcp_scholarly_search.md)).
   - **Flag synthesis output** in `literature_summary.md` with a header banner: `> **Phase-1 seed synthesis** — scaffold-derived references only; broader external discovery deferred to next iteration.` This signals to downstream consumers that the bib is intentionally narrow.
   - Skip Phase 2's full parallel search; jump straight to Phase 3 verification on the scaffold-named references.

Steps 4–7 are not optional — every literature search must check the library AND scout reports before external discovery. Step 8 fires conditionally and bypasses Phase 2 noise for cold-start projects.

For parsing `scholarly` CLI JSON output (mixes stderr log lines with stdout JSON), use the helper in [`references/scholarly-output-parsing.md`](references/scholarly-output-parsing.md).

### 1.3 Concept validation gate (pipeline mode only)

Run [`shared/concept-validation-gate.md`](../shared/concept-validation-gate.md) on the topic concept plan. If the plan fails (missing RQ, no theoretical framing, generic AI voice, <300 words, <3 references), pause and request a stronger concept plan before proceeding. Standalone mode skips this — free-form queries don't have a concept plan to validate.

### 1.4 Search plan + method-fitness gate (pipeline mode only)


Present the search plan and wait for confirmation: restate the RQ, list 3-6 queries grouped by **Track A (Substantive) / Track B (Empirical comparanda) / Track C (Methodological precedents)**, list seed authors/venues, propose `year_min` / `year_max` filters (propagated to every search call via `--year-from/--year-to`), flag book coverage if topic has major book-length treatments. Full structure: [`references/search-plan.md`](references/search-plan.md).

After plan approval, run [`shared/method-fitness-gate.md`](../shared/method-fitness-gate.md). If the method does not fit the RQ, escalate per [`shared/escalation-protocol.md`](../shared/escalation-protocol.md) — do not proceed to expensive search until the gate passes. Standalone mode skips both: free-form queries imply exploratory intent.

---

## Phase 2: Search

> standalone: yes | pipeline: yes | deep: yes (later expanded by 4.5 loop)

### 2.1 Parallel search

CLI pre-fetch via `scholarly` commands (search, similar-works, author-papers, arxiv-search, exa-search-papers) writing to `/tmp/lit-search/*.json`, then spawn 2-3 Explore agents in parallel (Google Scholar, bibliometric, S2/arXiv, domain-specific). Both `scholarly` and `paperpile` CLIs work inside sub-agents — pre-fetch or let agents shell out. Full CLI list, output paths, configuration: [`references/phase-2-search.md`](references/phase-2-search.md). Agent prompts: [`references/agent-templates.md#phase-2-search-agent-templates`](references/agent-templates.md#phase-2-search-agent-templates).

If CLI council enrichment fires here, run it as an additional parallel agent. If snowball enrichment fires, run it after primary search, before 2.2.

### 2.2 Deduplicate, classify, rank

1. Merge results from all search agents.
2. Remove duplicates — match on title similarity and DOI.
3. **Field-framework extraction** for each candidate: Setting / Population / Method / Data / DV / IV / Key finding / Mechanism / Boundary. Always run, even if partial — feeds ranking, gap analysis, synthesis, and `/hypothesis-generation`. Definitions: [`references/field-framework.md`](references/field-framework.md).
4. Rank by relevance, citation count, recency.
5. Select top N to verify (typically 25-30 candidates for 20-25 verified).
6. Assign batches of ~5 for verification.

If SciSciNet enrichment fires, run it on the ranked pool: adds `disruption_score`, `novelty_score`, `is_hit_1pct` flags; re-rank to boost hits and high-disruption papers.

---

## Phase 3: Verify

> standalone: yes | pipeline: yes | deep: yes + iterative loop (4.5)

This phase IS the integrity gate per [`shared/integrity-gates.md`](../shared/integrity-gates.md). No reference may enter the `.bib` without passing here.

Seven-step protocol:

1. **Batch DOI pre-verification** via `scholarly scholarly-verify-dois --json` — title-match check is mandatory (off-by-one DOI suffix hallucinations are the dominant failure mode). One CLI call accepts up to 50 DOIs; if you have more, see Dispatch Rule below before splitting.
2. **Find correct DOIs** for flagged papers via Crossref API → `scholarly-search` → web search (in order of reliability).
3. **Manual verification** of remaining papers — spawn general-purpose agents in parallel, ~5 papers each. Template: [`references/agent-templates.md#phase-4-verification-agent-template`](references/agent-templates.md#phase-4-verification-agent-template).
4. **Final DOI gate** — re-run `scholarly-verify-dois` on all DOIs entering the `.bib`. Papers without DOIs get `% NO DOI`. Subject to the same Dispatch Rule.
5. **Paperpile membership resolution (HARD — do not skip, do not infer from the Phase 1 topic search).** For **every** verified DOI, run `paperpile lookup-by-doi --doi <DOI> --json` to decide held-vs-`NEW`. This is the *only* authoritative membership test — `paperpile search-library` (Phase 1.2 step 4) is lossy topic discovery and a search miss is **not** evidence of absence. **Batch ≥6 DOIs via a single Bash sub-agent** that loops the lookups and returns a merged `{doi: citekey-or-null}` map (per the Dispatch Rule below). For each match, reuse the returned Paperpile citekey and pull the canonical entry with `paperpile export-bib --citekeys <key> --json`; for each non-match, tag genuinely `NEW` and stage for import. Mark every assembled entry `% IN PAPERPILE (<key>)` or `% NEW`, and report the held/NEW split count. Full protocol: [`shared/reference-resolution.md`](../shared/reference-resolution.md) § Membership Check. **Failure mode this closes:** defaulting a held paper to `NEW` because the Phase 1 topic search missed it (incident 2026-06-03 — 6 held papers mislabelled `NEW`, caught only by the user; reused keys were diluted and NEW-staging over-counted).
6. **Confidence grades** — A (DOI + full metadata), B (stable identifier, no DOI), C (single non-canonical source).
7. **Working paper inclusion test** — include only if ≥2 of: high citations, established author, top venue, sole source for concept, verifiable forthcoming status.

Full protocol: [`references/phase-4-verification.md`](references/phase-4-verification.md).

#### Dispatch Rule (Steps 1, 4 & 5)

Per [`_shared/cli-dispatch-policy.md`](../_shared/cli-dispatch-policy.md): if Step 1 or Step 4 would require **2 or more** `scholarly-verify-dois` calls (i.e. >50 DOIs total), dispatch a single Bash sub-agent that runs all batched calls and writes merged JSON to `/tmp/lit-verify.json`. Main context reads only the merged result, never the raw CLI output. **Step 5 membership lookups follow the same rule:** ≥6 `paperpile lookup-by-doi` calls dispatch to one Bash sub-agent returning a merged `{doi: citekey-or-null}` map to `/tmp/lit-membership.json`. For the bulk-threshold rationale, see `~/.claude/rules/subagent-prompt-discipline.md` § Bulk-Operation Dispatch Rule.

### 3.5 Iterative deep loop (deep mode only)

Prerequisites: ≥5 verified papers. Each iteration: (1) gap analysis with era-gated checks for terminology/paradigm shifts, (2) targeted search via `scholarly` + Explore sub-agents, (3) merge + dedup, (4) verify new papers via the seven-step protocol above (including Step 5 Paperpile membership resolution). Convergence: 3 iterations OR <3 genuinely new papers per iteration OR user says "enough". Full protocol: [`references/deep-loop-protocol.md`](references/deep-loop-protocol.md). Agent prompts: [`references/agent-templates.md#phase-45-deep-loop-agent-templates`](references/agent-templates.md#phase-45-deep-loop-agent-templates).

---

## Phase 4: Finalise

> standalone: 4.1–4.4, 4.6 | pipeline: all | deep: same as base mode

### 4.1 PDF download

Check Paperpile via `paperpile search-library` — papers with attached PDFs are SKIP, others DOWNLOAD. Spawn Bash agents in parallel (3-5 papers each) for the DOWNLOAD set. Best-effort — many papers are paywalled. Template: [`references/agent-templates.md#phase-5-pdf-download-agent-template`](references/agent-templates.md#phase-5-pdf-download-agent-template).

### 4.2 Assemble bibliography

Two outputs required:

1. `docs/literature-review/literature_summary.bib` — always created, standalone, self-contained.
2. Project canonical bib (e.g. `paper/references.bib`) — merge into it if it exists.

Rules: Better BibTeX-format keys; **reuse Paperpile keys for entries the Phase 3 Step 5 membership check found held** (do not regenerate keys for held papers, do not re-stage them as `NEW`); only VERIFIED papers; list ALL authors (never "et al."); seed each entry via `scholarly scholarly-paper-detail`; add `% Confidence: A/B/C`, `% IN PAPERPILE (<key>)` or `% NEW`, and `% WP criteria:` comments where applicable; every entry needs a connection note in `literature_summary.md`. The Paperpile import-staging file must contain **only** entries the Step 5 check tagged `NEW`. Full format: [`references/bibliography-format.md`](references/bibliography-format.md).

Each output gets a [`shared/material-passport.md`](../shared/material-passport.md) header (origin skill, mode, version, produced timestamp) so downstream consumers can detect staleness.


### 4.3 Validate bibliography (HARD GATE)

**Do not proceed to 4.4 or Phase 5 until `/bib-validate` has been invoked and the report reviewed.** Phase 3 verifies papers exist; `/bib-validate` catches a different class (missing BibTeX fields, preprint staleness, DOI problems, author formatting, unused entries). Running synthesis before validation means the narrative may reference entries with broken metadata that survive into the paper.

Mandatory on every `/literature` invocation (standalone, pipeline, deep) every time new entries are added.

**Sprint Contract self-check hook (pipeline mode).** After `/bib-validate` passes, run each contract dimension's `verification_rule` (D1–D5). Any F1 (DOI verification fails) or F2 (generated-key pattern with no DOI) triggers `producer_decision=revise_before_handoff` — go back to Phase 3, do NOT proceed to 4.4. Escalate via the 3-round override ladder if revision still fails.

### 4.4 Sync to reference managers

Sync new references to Paperpile (primary reference manager); handle migration candidates and post-run maintenance. Append a sync breadcrumb to `.planning/state.md` or `.context/current-focus.md`. Full steps + breadcrumb format: [`references/reference-manager-sync.md`](references/reference-manager-sync.md).

### 4.5 Pipeline completion (pipeline mode only)

After 4.3 passes (bib-validate clean) and 4.4 completes: (1) vault sync via `taskflow-cli`, (2) knowledge wiki filing if `knowledge/` exists. Standalone mode skips this entirely. Full steps: [`references/pipeline-completion.md`](references/pipeline-completion.md).

### 4.6 Output verification (before commit)

Before any auto-commit, emit an outputs manifest and run the shared verifier per [`_shared/verify-outputs.md`](../_shared/verify-outputs.md):

1. Write manifest to `<project>/.claude/state/outputs-manifest-<UTC-timestamp>.json` listing every file this skill claims to have written, paths relative to the project root.
2. Run:

   ```bash
   python3 "$HOME/.claude/skills/_shared/verify_outputs.py" \
       --manifest "$MANIFEST" \
       --project-root "$PROJECT_ROOT"
   ```

3. If the verifier exits non-zero, **do not commit**. Surface the missing-files list and stop. The verifier logs an `error` entry to `~/.claude/ecc/skill-outcomes.jsonl`.

Closes the "hallucinated outputs" failure class (commit `b2cff75`, 2026-04-18).

### 4.7 Auto-commit (pipeline mode only)

Hard gate: commit only if 4.3 (bib-validate clean) and 4.6 (outputs manifest verified) both passed. Standalone mode skips. Commit template: [`references/pipeline-completion.md`](references/pipeline-completion.md).

---

## Phase 5: Synthesise

> standalone: yes | pipeline: yes | deep: yes (informed by deep-loop findings)

Output: `docs/literature-review/literature_summary.md`. Never write synthesis to `paper/` (Hard Rule 3). If `docs/literature-review/` does not exist, `mkdir -p` first.

Seven steps: (1) identify themes, (2) map intellectual lineage, (3) note current debates, (4) structured gap analysis (methodological / population-context / conceptual, each with "why it matters"), (5) negative evidence per cluster (mandatory — state explicitly if absent), (6) cross-cluster synthesis (tensions + implications), (7) Priority Reading Order (5–7 papers: review → foundational → frontier → gap/controversy).

Output types: narrative summary, literature deck, annotated bibliography, concise field synthesis (~400 words for "quick synthesis" requests). Use `[VERIFY]` tags for uncertain attributions (resolve before publication). For comprehensive reviews, run through `council-cli` for multi-model synthesis. Full protocol: [`references/synthesis.md`](references/synthesis.md).

---

## Sub-Agent Guidelines

1. **Launch independent agents in a single message** for parallelism.
2. **Be explicit in prompts** — sub-agents have no context. Include skip lists of existing citation keys.
3. **Maximum 3 parallel agents at a time.** Spawn in waves, write results to disk between waves. Each agent writes to a temp file (e.g., `/tmp/lit-search/agent-N.json`) rather than returning large payloads in-context. Summarise from files to avoid context overflow.
4. **Right agent type:** `Explore` for search, `general-purpose` for verification, `Bash` for downloads.
5. **Batch sizes:** 5 papers per verification agent, 3-5 per PDF agent.
6. **Tolerate partial failures** — continue with what you have.

---

## Cross-References

See [`references/related-skills.md`](references/related-skills.md) for cross-references, bibliometric API guides, and arXiv full-text reading instructions.

## Citation Contract

<!-- paperpile-citation-contract -->
1. Paperpile is the only source of truth for committed citation keys and BibTeX metadata.
2. Before writing `\cite{key}`, verify with `paperpile get-item key` and `paperpile export-bib key`.
3. Resolve unknowns in order: DOI lookup → Paperpile substring search → `refpile` semantic search → Paperpile verify.
4. A DOI miss is **not** non-membership; continue with title/author search and refpile.
5. If unresolved, write `\CiteTodo{slug}{title/author/year/DOI hint}` — never a guessed key.
6. Drafting sub-agents must not write/edit the active `.bib`; only the orchestrator regenerates it from Paperpile exports.
7. Stage genuine new refs under `.paperpile-import/` for manual Paperpile import; don't cite until Paperpile mints the key.
8. Run `scripts/bib/citation_lint.py` before commit; zero placeholders, zero non-Paperpile keys, zero hand-authored metadata.

See `rules/paperpile-citations.md` for the full workflow.
