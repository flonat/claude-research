# Strategic Revision — 11-Phase Detailed Protocol

> Full step-by-step procedure for the merged `strategic-revision` skill. Read the SKILL.md first for the overview; this file is the operational manual.
>
> **Source legend:** FB = the user's ingestion layer. JS = Jukka Sihvonen's analytical layer (https://github.com/jusi-aalto/strategic-revision). Both = merged.

---

## Phase 1 (FB): Setup

**Goal:** scaffold the output directories and copy (never move) the source PDF.

1. Gather inputs. If not provided, ask via `AskUserQuestion`:
   - Reviews PDF path — try auto-discovery first (`to-sort/*.pdf`, then `correspondence/referee-reviews/{venue}-round{n}/*.pdf`, then `correspondence/referee-reviews/*.pdf`)
   - Project path — auto-detect from cwd if a `CLAUDE.md` or `paper*/` is present
   - Venue slug (e.g., `ejor`, `facct-2026`)
   - Revision round (integer, default 1)
   - Response deadline (date or "TBD")
   - Coordinating author

2. Resolve the output root:
   ```
   <project>/correspondence/referee-reviews/{venue}-round{n}/
   ```

3. Check for overwrite. If the directory exists and contains outputs, version new outputs (`comment-tracker-v2.md`, `REVISION_MASTER_PLAN-v2.md`). Always flag before writing.

4. Create the scaffold:
   ```bash
   mkdir -p correspondence/referee-reviews/{venue}-round{n}/reviews
   mkdir -p correspondence/referee-reviews/{venue}-round{n}/analysis
   mkdir -p correspondence/referee-reviews/{venue}-round{n}/plan
   ```

5. Copy (never move) the source PDF:
   ```bash
   cp "<source-pdf>" correspondence/referee-reviews/{venue}-round{n}/reviews-original.pdf
   ```

6. Create an empty `rebuttal.md` placeholder for the user's response draft.

---

## Phase 2 (FB): Read Reviews

**Goal:** extract structured per-reviewer data in memory before writing anything to disk.

1. Read `reviews-original.pdf` with the `Read` tool. If the PDF exceeds 10 pages, use the `pages` parameter to read in chunks.

2. For each reviewer (R1, R2, R3, EiC, AE), extract into memory:
   - Reviewer label (R1, R2, ...) and any explicit role (Associate Editor, Editor-in-Chief)
   - Summary paragraph (if provided)
   - Numbered comments or paragraphs — preserve the reviewer's own numbering
   - Any explicit requests for revision
   - Any positive comments (to acknowledge in the response)

3. If the PDF is a decision letter + attached reviews, distinguish them:
   - **Decision letter** (EiC, AE) usually comes first and highlights key concerns
   - **Attached reviews** follow

4. Note any DONE markers if the file is a Round 2+ (i.e., reviewer confirms earlier fix). Flag these for exclusion from active planning.

---

## Phase 3 (FB): Individual Reviewer Files

**Goal:** produce one markdown file per reviewer in `reviews/`.

For each reviewer, write `reviews/reviewer-{N}.md` (or `reviews/editor.md`, `reviews/associate-editor.md`):

```markdown
# Reviewer {N} — {role if any}

## Summary
{reviewer's own summary, verbatim if short, paraphrased-then-marked if long}

## Comments

### {N}.1
{full comment text}

### {N}.2
{full comment text}

...
```

Rules:
- Preserve reviewer's numbering when present
- Do not merge distinct comments
- Flag any comments where reviewer-provided numbering is ambiguous — handled in Phase 5 with SourceIDs

---

## Phase 4 (FB): LaTeX Verbatim Transcription

**Goal:** produce a compilable `reviewer-comments-verbatim.tex` that a co-author can read on paper.

1. Copy the LaTeX template from `templates/referee-comments/reviewer-comments-verbatim.tex` into `analysis/`.

2. Fill in the document preamble (venue, round, date, deadline).

3. For each reviewer, transcribe **verbatim** — never paraphrase. If the PDF has strange formatting or OCR errors, fix the OCR but flag with a comment in the `.tex` source.

4. LaTeX escape rules: `&` → `\&`, `%` → `\%`, `$` → `\$`, `_` → `\_`, `#` → `\#`, `~` → `\textasciitilde{}`, `^` → `\textasciicircum{}`, `\` → `\textbackslash{}`.

5. Compile to verify:
   ```bash
   cd correspondence/referee-reviews/{venue}-round{n}/analysis
   latexmk -pdf -interaction=nonstopmode reviewer-comments-verbatim.tex
   ```

6. Build artefacts must end up in `out/` (the `.latexmkrc` enforces this). If compilation fails, fix and retry — **Phase 5 cannot begin until this file compiles cleanly.**

---

## Phase 5 (JS): Atomic Parsing ("Raw Data")

**Goal:** extract every distinct referee request as its own row, no matter how small.

Work from both the in-memory reviewer data (Phase 2) and the individual reviewer files (Phase 3). Build a flat table of atomic tasks.

### Output format

Markdown table in `analysis/comment-tracker.md` (Phase 6 adds columns):

| SourceID | Quote | Atomic Task |
|----------|-------|-------------|
| R1.a1 | "verbatim or abbreviated quote" | Imperative action verb + specific deliverable |

### Rules

- **SourceID convention:** `{Reviewer}.{CommentNumber}{SubLetter}` — e.g., `R1.a1`, `EiC.2b`, `R2.d3`. Use letters for sub-requests within the same comment.
- If a single paragraph contains 3 distinct requests, create 3 rows — never collapse.
- Quote column: reviewer's own words (abbreviated if long, preserve meaning).
- Atomic Task column: restate in imperative form ("Add…", "Rewrite…", "Run…", "Justify…", "Create…").
- If a task is marked DONE in a Round 2+ file, note it and exclude from active planning.
- Cross-reference duplicates across reviewers in a later column (e.g., "= EiC.3a").

---

## Phase 6 (Both): Classification

**Goal:** tag each atomic task with both the 5-category taxonomy (Sihvonen) and the R&R routing (FB). The two axes are orthogonal.

### Axis 1 — Category (Sihvonen, 5-cat)

| Tag | Category | Description | Examples |
|-----|----------|-------------|----------|
| 🔴 | STRUCTURAL | Moving sections, cutting text, reorganizing | Relocate interviews to intro; cut tangential material |
| 🟠 | ARGUMENTATIVE | Changing theory, narrative, logical framing, contribution | Reframe contribution; integrate disclosure theory; strengthen motivation |
| 🟡 | EMPIRICAL | New regressions, data work, robustness tests, variables | Add control variable; run sub-sample analysis; test alternative model |
| 🟢 | CLARIFICATION | Definitions, explaining confusing text, justifications | Define "cybersecurity governance"; justify measure choice; explain null finding |
| 🔵 | EDITORIAL | Formatting, typos, figure labels, terminology consistency | Fix Figure 2 labels; standardize terminology; add table notes |

### Axis 2 — R&R Routing (FB)

See [rr-routing.md](rr-routing.md) for signal words and routing protocols.

| Routing | When |
|---------|------|
| **NEW ANALYSIS** | Requires new estimation, data work, robustness checks |
| **CLARIFICATION** | Text revision sufficient — no new analysis |
| **DISAGREE** | Author push-back — flag for user, never auto-respond |
| **MINOR** | Typos, formatting, citation fixes |

### Output

Extend `analysis/comment-tracker.md` with two new columns:

| SourceID | Quote | Atomic Task | Category | R&R Routing | Priority |
|----------|-------|-------------|----------|-------------|----------|

Append a summary counts table at the bottom (e.g., "🔴 STRUCTURAL: 3 | 🟠 ARGUMENTATIVE: 8 | 🟡 EMPIRICAL: 5 | 🟢 CLARIFICATION: 12 | 🔵 EDITORIAL: 4"; "NEW ANALYSIS: 5 | CLARIFICATION: 15 | DISAGREE: 2 | MINOR: 10").

### Typical correlations

- STRUCTURAL ↔ usually CLARIFICATION routing (text rearrangement)
- EMPIRICAL ↔ usually NEW ANALYSIS
- ARGUMENTATIVE + DISAGREE → rebuttal-heavy revision — flag for strategic coaching (Phase 10)

---

## Phase 7 (JS): Dependency Mapping ("DAG")

**Goal:** build the Directed Acyclic Graph of task dependencies. Produce `revision_tasks.json` (input for the validator).

### Relationship types

1. **Upstream Blocker** (hard dependency — `depends_on` in JSON): "I cannot do Task B until Task A is finished."
   - Cannot rewrite Discussion until new regressions are done
   - Cannot create measure-mapping table until each measure is conceptually justified
   - Cannot tighten front-end until decisions about what moves in/out are made

2. **Collateral Risk** (informational — `collateral_risks` in JSON): "If I do Task A, it might make Task B irrelevant or contradictory."
   - Adding a new control variable may change coefficient significance, invalidating current interpretations
   - Pre/post textual similarity may show firms just relocated text, undermining contribution

### Output tables (add to `REVISION_MASTER_PLAN.md`)

**Table 1: Upstream Blockers**

| Downstream Task | Blocked By (Upstream) | Impact / Rationale |
|-----------------|-----------------------|--------------------|

**Table 2: Collateral Risks**

| If You Do This Task… | It May Affect… | Risk Description |
|-----------------------|----------------|------------------|

### Output JSON

Write `plan/revision_tasks.json` per the schema in [task-schema.md](task-schema.md). At this point set `"block": "?"` as placeholder — Phase 9 fills in the execution block.

### Common dependency patterns in empirical papers

- New control variables → re-run regressions → re-interpret results → rewrite discussion
- Theory reframing → rewrite introduction → rewrite conclusion
- New sub-analyses → inform alternative explanations → revise discussion
- Structural moves (relocate sections) → tighten other sections → final narrative pass
- The overall narrative reframe is ALWAYS the final capstone task

---

## Phase 8 (JS): Structural DAG Validation ("Gate Check")

**Goal:** confirm the graph is acyclic before investing effort in Phase 9 sequencing. Fail-fast gate.

### Procedure

1. Copy the validator into the plan directory:
   ```bash
   cp skills/strategic-revision/scripts/dag_validator.py \
      correspondence/referee-reviews/{venue}-round{n}/plan/
   ```

2. Ensure `networkx` is installed:
   ```bash
   uv pip install networkx
   ```

3. Run in validate-only mode:
   ```bash
   cd correspondence/referee-reviews/{venue}-round{n}/plan
   python dag_validator.py revision_tasks.json --validate-only
   ```

4. Interpret:
   - **PASSED** — graph is acyclic. Proceed to Phase 9.
   - **FAILED** — cycle exists. Output shows cycle path (e.g., `A -> B -> C -> A`).

### If cycles detected

Return to Phase 7 tables and resolve:

| Common Cause | Fix |
|-------------|-----|
| Collateral risk encoded as hard dependency | Move from `depends_on` to `collateral_risks` — risks are informational, not structural |
| Bidirectional dependency (A blocks B AND B blocks A) | Determine which task truly must come first; remove the reverse edge |
| Transitive chain through merged tasks | Split the merged task into two sequential tasks, or remove the redundant edge |
| Copy-paste error in task IDs | Verify IDs match exactly between `depends_on` references and task keys |

Regenerate `revision_tasks.json` and re-run `--validate-only`. Repeat until PASSED.

### Record in the master plan

```markdown
### Phase 8: Structural Validation

DAG validated: N tasks, M dependencies, no circular dependencies detected.
Proceed to Phase 9.
```

---

## Phase 9 (JS): Critical Path Sequencing ("Schedule")

**Goal:** group tasks into sequential Execution Blocks A-E based on the DAG. Violations of the critical path are not permitted.

### Standard Block Sequence

| Block | Name | Contents | Gate |
|-------|------|----------|------|
| **A** | Empirical Foundation | Core variable changes, new controls, re-estimation of main regressions | **GO/NO-GO**: If key conclusions change, escalate to authors before proceeding |
| **B** | Sub-Analyses & Robustness | Cross-sectional tests, sub-samples, alternative specifications, robustness checks | Results feed into Block C interpretations |
| **C** | Theoretical Reframing | Theory integration, contribution restatement, measure justifications, null-finding explanations | Must incorporate Block A & B results |
| **D** | Narrative Construction | Structural reorganization, section moves, rewriting Intro/Discussion/Conclusion | Depends on settled theory (C) and stable results (A, B) |
| **E** | Polish | Figures, tables, formatting, terminology audit | Last |

### Adaptation

- Paper has no empirical component → skip Block A, start at C
- Theory is primary concern → expand Block C, potentially merge A+B
- Paper is primarily editorial → compress to Blocks D+E

### Output

For each block, add a table to `REVISION_MASTER_PLAN.md`:

| Priority | Task ID(s) | Action | Rationale |
|----------|-----------|--------|-----------|

End Phase 9 with an ASCII execution roadmap showing the block flow. Phase 11 will annotate this with `[CP]` (critical path) and `[BN]` (bottleneck) markers.

Also: **update `revision_tasks.json`** — replace the `"block": "?"` placeholders with the assigned block letters (A, B, C, D, E).

---

## Phase 10 (Both): Risk & Conflict Resolution + Strategic Coaching

### 10.1 Reviewer Conflicts (JS)

Identify direct conflicts (e.g., R1 says "Expand section," R2 says "Cut section").

| Conflict ID | R1 Position | R2 Position | Resolution Strategy |
|-------------|-------------|-------------|---------------------|

Resolution strategies:
- **Cut-and-replace**: Remove what R2 dislikes, add what R1 wants (net-neutral length)
- **Appendix**: Move detailed material to appendix (satisfies both)
- **Strategic choice + defend**: Pick one direction, explain in response letter why
- **Reframe**: Find a framing that satisfies both without contradiction

### 10.2 Process Risks (JS)

| Risk ID | Description | Likelihood | Impact | Mitigation |
|---------|-------------|-----------|--------|------------|

Common process risks in empirical paper revisions:
- New control variable changes main results
- Sub-sample analysis has insufficient power
- Data for requested variable is unavailable
- Excluding observations reduces sample substantially
- Alternative model produces divergent results
- Paper length increases beyond journal limits

### 10.3 Strategic Decisions (JS)

Identify decisions that require author input (not autonomous resolution).

| Decision | Options | Recommendation |
|----------|---------|----------------|

Always provide a clear recommendation with rationale, but flag these for the authors rather than deciding unilaterally.

### 10.4 Strategic Coaching (FB)

For each **Major** or **Critical** comment (skip Minor/Editorial), walk the user through:

1. **Understanding:** reviewer's core concern — methodology, theory, or framing?
2. **Position:** Agree / Partially agree / Disagree (with core rebuttal if Disagree)
3. **Risk:** likelihood of reviewer escalation if pushed back on
4. **Response sketch:** one-sentence strategy (not full response)

Record in `analysis/comment-tracker.md` with two more columns: **Position** + **Strategy**.

Rules:
- Only Major/Critical get coaching. Minor/Editorial auto-classify as Agree.
- The user can say "skip coaching" to auto-classify all remaining as Agree.
- Maximum 2 rounds of dialogue per comment.
- **Do not write the actual response letter** — that remains the user's job.

---

## Phase 11 (Both): Computational Optimization + Review Analysis

### 11.1 Computational Analysis (JS)

Run the validator in full mode:

```bash
cd correspondence/referee-reviews/{venue}-round{n}/plan
python dag_validator.py revision_tasks.json
# produces revision_dag_analysis.json
```

Read `revision_dag_analysis.json` and integrate results into `REVISION_MASTER_PLAN.md`:

#### Parallel Execution Schedule

From the `parallel_batches` field:

```markdown
**Batch 1** (N tasks — no prerequisites, can begin immediately):
- task_id_1: description [Block X] CATEGORY
- task_id_2: description [Block X] CATEGORY

**Batch 2** (N tasks — requires Batch 1 completion):
- ...
```

Where batches mix tasks from different Phase 9 blocks, flag as optimization opportunity.

#### Critical Path

From the `critical_path` field:

```markdown
Length: N sequential tasks (minimum revision timeline)

1. task_id_1 — description
2. task_id_2 — description
   ...
N. task_id_N — description
```

If the computational critical path differs from the Phase 9 manually identified sequence, recommend following the computational result for scheduling (but keep domain logic for narrative coherence).

#### Bottleneck Tasks

From the `bottlenecks` field:

| Task | Block | Direct Dependents | Total Downstream | Description |
|------|-------|-------------------|------------------|-------------|

Cross-reference with Phase 10 process risks. Bottlenecks that also appear in the risk table carry compounded risk → explicit mitigation strategies.

#### Block Validation

From the `block_analysis` field. For each block report: task count, internal edges, external dependencies. A Block C task depending on a Block D task is a block ordering issue — must be resolved.

#### Updated roadmap

Revise the Phase 9 ASCII roadmap:
- Annotate critical path tasks with `[CP]`
- Annotate bottleneck tasks with `[BN]`
- Add parallel execution notes where batches cross blocks
- Adjust block boundaries if computational analysis reveals unnecessary sequential constraints

### 11.2 Venue Strategy & Review Analysis (FB)

Populate `analysis/review-analysis.md` using `templates/referee-comments/review-analysis.md`:

- **Overview:** 1-paragraph strategic read of the decision — likely acceptance probability for current venue after revision
- **Strategy A (minimal revision):** venues that would accept the paper as-is despite reviewer concerns
- **Strategy B (substantial revision):** equal-or-higher prestige venues worth targeting if authors invest in major revision
- **Conferences:** check CORE rankings via `.context/resources/venue-rankings.md` (CSV: `.context/resources/venue-rankings/core_2026.csv`)
- **Journals:** check CABS AJG via `.context/resources/venue-rankings.md` (CSV: `.context/resources/venue-rankings/abs_ajg_2024.csv`). For SJR, query Elsevier Serial Title API (`SCOPUS_API_KEY` required). Flag journals below CABS 3 only with strong rationale.
- **Recommendation table:** 3-5 venues ranked with rationale. First option should always be "revise for current venue" if acceptance probability >~30%.
- **Key Decision:** frame the core trade-off (speed vs. impact, minimal vs. substantial effort).

---

## Completion checklist

Before reporting the skill run complete:

- [ ] `reviews-original.pdf` copied (source PDF untouched)
- [ ] `reviews/reviewer-{N}.md` files written for every reviewer
- [ ] `analysis/reviewer-comments-verbatim.tex` compiles cleanly
- [ ] `analysis/comment-tracker.md` has atomic tasks with Category + R&R + Priority + Position + Strategy
- [ ] `analysis/review-analysis.md` has venue strategy and recommendation table
- [ ] `plan/revision_tasks.json` validates acyclic (Phase 8 PASSED)
- [ ] `plan/revision_dag_analysis.json` generated
- [ ] `plan/REVISION_MASTER_PLAN.md` includes all six Sihvonen tables, blocks A-E, coaching notes, and annotated roadmap
- [ ] `rebuttal.md` exists (empty placeholder) — user writes the response letter separately

Report to the user: counts per reviewer, counts per category/routing, critical path length, bottleneck count, and the GO/NO-GO flag if Block A has high-risk empirical tasks.
