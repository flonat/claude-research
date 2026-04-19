---
name: strategic-revision
description: "Use when you receive referee comments for a paper (R&R, revise-and-resubmit) and need a DAG-validated revision master plan — atomic task extraction, dependency mapping, computational critical-path analysis, execution blocks, venue strategy. Merges /parse-reviews ingestion with Sihvonen's strategic-revision architecture."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(mkdir*), Bash(cp*), Bash(ls*), Bash(latexmk*), Bash(python*), Bash(uv*), AskUserQuestion, Task
argument-hint: "[path-to-reviews-pdf or no arguments for guided setup]"
---

# Strategic Revision — From Referee PDF to DAG-Validated Master Plan

Read a referee comments PDF and produce:
1. Standardised tracking files (per-reviewer markdown, LaTeX verbatim, comment tracker, review analysis)
2. A computationally validated revision master plan (atomic tasks, DAG, execution blocks A-E, critical path, bottlenecks)

**Provenance:** DAG validation + critical-path architecture adapted from Jukka Sihvonen's strategic-revision skill (https://github.com/jusi-aalto/strategic-revision). the user's ingestion layer (correspondence scaffolding, LaTeX verbatim, R&R routing, venue strategy, coaching) retained.

## When to Use

- Received reviewer reports for a paper (journal or conference)
- Starting an R&R cycle and need to set up tracking + plan revision strategy
- Want both structured referee artifacts AND a dependency-mapped action roadmap

## When NOT to Use

- Writing the actual response letter (use generated response blocks as a starting point, then write manually)
- Reviewing someone else's paper (use `/proofread` or `peer-reviewer` agent)
- Internal review synthesis only — use `/synthesise-reviews` instead

## Inputs

Gather via interview if not provided:

1. **Reviews PDF path** — auto-discovered or user-provided (see below)
2. **Project path** — root of the research project (auto-detect from cwd if possible)
3. **Venue slug** — e.g., `ejor`, `facct-2026`, `management-science`
4. **Revision round** — integer, default 1
5. **Response deadline** — date if known, otherwise "TBD"
6. **Coordinating author** — who is leading the response

### PDF Auto-Discovery

Search for the reviews PDF in this order. Use the first match; if multiple PDFs found at a location, list them and ask the user to pick.

1. `to-sort/*.pdf` — most likely landing spot after download
2. `correspondence/referee-reviews/{venue}-round{n}/*.pdf`
3. `correspondence/referee-reviews/*.pdf`
4. Ask the user for the path if nothing found

## Output Location

```
correspondence/referee-reviews/{venue}-round{n}/
├── reviews-original.pdf              (copy of input PDF — source NEVER moved)
├── rebuttal.md                       (empty — for response draft)
├── reviews/                          (individual reviewer files)
│   ├── reviewer-1.md
│   └── ...
├── analysis/
│   ├── comment-tracker.md            (atomic comment matrix with R&R + 5-cat classification)
│   ├── review-analysis.md            (strategic overview + venue strategy)
│   └── reviewer-comments-verbatim.tex (LaTeX transcription)
└── plan/
    ├── REVISION_MASTER_PLAN.md       (six-phase Sihvonen plan — atomic tasks, DAG, blocks, risks)
    ├── revision_tasks.json           (DAG input — see references/task-schema.md)
    └── revision_dag_analysis.json    (computational output — parallel batches, critical path, bottlenecks)
```

**Source PDF preservation:** The original PDF is only ever **copied** to `reviews-original.pdf`. Never move, rename, or delete the source.

**Principle:** `correspondence/` holds exchanges with reviewers. Internal review work goes in `docs/{venue}/internal-reviews/`.

**No-overwrite rule:** If outputs already exist, version them (`comment-tracker-v2.md`, `REVISION_MASTER_PLAN-v2.md`). Always flag before writing.

## Protocol — 11 Phases

The skill runs 11 sequential phases. Detailed step-by-step procedure: [references/phases.md](references/phases.md).

| # | Phase | Output | Source |
|---|-------|--------|--------|
| 1 | **Setup** | Scaffolded directories + copied PDF | FB |
| 2 | **Read Reviews** | Structured per-reviewer data in memory | FB |
| 3 | **Individual Reviewer Files** | `reviews/reviewer-{N}.md` | FB |
| 4 | **LaTeX Verbatim Transcription** | `reviewer-comments-verbatim.tex` (compiled) | FB |
| 5 | **Atomic Parsing** | Every distinct request as own SourceID (`R1.a3`, `EiC.2b`) | JS |
| 6 | **Classification** | 5-cat (STRUCTURAL/ARGUMENTATIVE/EMPIRICAL/CLARIFICATION/EDITORIAL) + R&R routing (NEW ANALYSIS / CLARIFICATION / DISAGREE / MINOR) | Both |
| 7 | **Dependency Mapping (DAG)** | Upstream Blockers + Collateral Risks tables → `revision_tasks.json` | JS |
| 8 | **Structural DAG Validation** | `dag_validator.py --validate-only` gate check | JS |
| 9 | **Critical Path Sequencing** | Execution Blocks A-E + GO/NO-GO gate after Block A | JS |
| 10 | **Risk & Conflict Resolution + Coaching** | Reviewer conflicts, process risks, interactive coaching (Major/Critical only) | Both |
| 11 | **Computational Optimization + Review Analysis** | Parallel batches, critical path, bottlenecks + venue strategy (CABS/CORE/SJR) | Both |

**JS = Sihvonen phases. FB = the user phases. Both = merged.**

### Phase Dependencies

- Phases 1-4 (ingestion) must complete before Phase 5 begins
- Phase 8 is a **hard gate**: cycles → return to Phase 7, do not advance to Phase 9
- Phase 11 requires the Phase 9 block assignments before running full DAG analysis
- Phase 10 coaching runs only on Major/Critical comments (skip Minor/Editorial)

## DAG Validation Quick Reference

**Phase 8 (structural gate):**
```bash
cd correspondence/referee-reviews/{venue}-round{n}/plan
python dag_validator.py revision_tasks.json --validate-only
```

**Phase 11 (full analysis):**
```bash
python dag_validator.py revision_tasks.json
# Produces revision_dag_analysis.json
```

Copy `dag_validator.py` from `skills/strategic-revision/scripts/` into the plan directory before running. Requires `networkx` (`uv pip install networkx` if missing).

Full validator documentation: [references/dag-validation.md](references/dag-validation.md).
Task JSON schema: [references/task-schema.md](references/task-schema.md).
R&R routing rules: [references/rr-routing.md](references/rr-routing.md).

## Classification: Two Axes

Every atomic task gets **both** classifications recorded in the comment tracker:

**Category (5-cat, Sihvonen):** structural intent of the change
- 🔴 STRUCTURAL — moves, cuts, reorganizations
- 🟠 ARGUMENTATIVE — theory, narrative, logical framing
- 🟡 EMPIRICAL — new regressions, data work, robustness
- 🟢 CLARIFICATION — definitions, justifications, explanations
- 🔵 EDITORIAL — formatting, typos, figures, terminology

**R&R Routing (FB):** workflow routing
- **NEW ANALYSIS** — needs code/data work
- **CLARIFICATION** — textual fix only
- **DISAGREE** — author push-back with rebuttal
- **MINOR** — trivial or editorial

The two axes are orthogonal: a STRUCTURAL task is usually a CLARIFICATION routing; an EMPIRICAL task is usually NEW ANALYSIS; ARGUMENTATIVE with DISAGREE signals a rebuttal-heavy revision.

## Strategic Coaching (Phase 10)

For each **Major** or **Critical** comment, walk the user through:

1. **Understanding:** reviewer's core concern — methodology, theory, or framing?
2. **Position:** Agree / Partially agree / Disagree (with core rebuttal if Disagree)
3. **Risk:** likelihood of reviewer escalation if pushed back on
4. **Response sketch:** one-sentence strategy (not full response)

Record in the comment tracker with two new columns: **Position** + **Strategy**.

Rules:
- Only Major/Critical get coaching. Minor/Editorial auto-classify as Agree.
- the user can say "skip coaching" to auto-classify all remaining as Agree.
- Maximum 2 rounds of dialogue per comment.
- Do not write the actual response letter — that remains the user's job.

## Venue Strategy (Phase 11)

Populate the Publication Strategy section of `review-analysis.md`:

- **Strategy A (minimal revision):** venues that would accept the paper as-is despite reviewer concerns
- **Strategy B (substantial revision):** equal-or-higher prestige venues worth targeting if authors invest in addressing major concerns
- **Conferences:** check CORE rankings via `.context/resources/venue-rankings.md` (CSV: `.context/resources/venue-rankings/core_2026.csv`)
- **Journals:** check CABS AJG via `.context/resources/venue-rankings.md` (CSV: `.context/resources/venue-rankings/abs_ajg_2024.csv`). For SJR, query Elsevier Serial Title API (`SCOPUS_API_KEY` required). Flag journals below CABS 3 only with strong rationale.
- **Recommendation table:** 3-5 venues ranked with rationale. First option should always be "revise for current venue" if acceptance probability >~30%.
- **Key Decision:** frame the core trade-off (speed vs. impact, minimal vs. substantial effort).

## Critical Rules

1. **Verbatim means verbatim.** Never paraphrase reviewer text in `reviewer-comments-verbatim.tex`. Copy exactly.
2. **Every comment gets a SourceID.** No reviewer concern is lost. If in doubt, give it its own ID.
3. **Atomic tasks only.** If a paragraph contains 3 distinct requests, create 3 rows — never collapse.
4. **No invented requests.** Every task traces to a verbatim quote.
5. **Don't overwrite.** Version outputs if present.
6. **Compile the LaTeX.** `reviewer-comments-verbatim.tex` must build cleanly before Phase 5.
7. **Phase 8 is a hard gate.** Cycles block Phase 9. Fix the DAG, re-run validation.
8. **Phase 11 is mandatory.** Do not skip computational optimization — parallel batches and critical path override manual sequencing where they conflict.
9. **Don't write response letters.** The skill produces plans and trackers; writing the rebuttal is the user's job.
10. **GO/NO-GO gate after Block A.** If empirical foundation changes key conclusions, escalate to authors before advancing.

## Templates

Located in `templates/referee-comments/`:
- `comment-tracker.md` — atomic matrix with R&R columns
- `review-analysis.md` — strategic overview template
- `reviewer-comments-verbatim.tex` — LaTeX transcription template

## Cross-References

- `/proofread` — proofread the response letter before submission
- `/bib-validate` — run after revision to check bibliography
- `/pre-submission-report` — full quality check before resubmission
- `paper-critic` agent — self-review of the revised paper
- `/synthesise-reviews` — merge internal review agent reports (different use case — not referee comments)
- `references/phases.md` — detailed 11-phase protocol
- `references/rr-routing.md` — R&R routing signal words
- `references/dag-validation.md` — DAG validator usage + Phase 6 details
- `references/task-schema.md` — `revision_tasks.json` JSON schema
- `scripts/dag_validator.py` — NetworkX-based DAG validator (copy to plan dir before running)
