---
name: process-reviews
description: "Use when you need to process referee comments from a reviews PDF into tracking files."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(mkdir*), Bash(cp*), Bash(ls*), Bash(latexmk*), AskUserQuestion, Task
argument-hint: "[path-to-reviews-pdf or no arguments for guided setup]"
---

# Process Referee Comments

Read a reviews PDF and generate three standardised output files for managing an R&R response.

## When to Use

- Received reviewer reports for a paper (journal or conference)
- Starting an R&R cycle and need to set up tracking infrastructure
- Want to standardise an existing ad-hoc review response

## When NOT to Use

- Writing the actual response letter (use the generated `comment-tracker.md` response blocks as a starting point, then write the letter manually)
- Reviewing someone else's paper (use `/proofread` or the `peer-reviewer` agent)

## Inputs

Gather via interview if not provided:

1. **Reviews PDF path** — auto-discovered or user-provided (see below)
2. **Project path** — root of the research project (auto-detect from cwd if possible)
3. **Venue slug** — short identifier, e.g., `ejor`, `facct-2026`, `management-science`
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

Review correspondence goes under `correspondence/referee-reviews/`, with an `analysis/` subfolder for derived work:

```
correspondence/referee-reviews/{venue}-round{n}/
├── reviews-original.pdf              (copy of input PDF — source is NEVER moved/deleted)
├── rebuttal.md                       (empty — for response draft)
├── reviews/                          (individual reviewer files)
│   ├── reviewer-1.md
│   ├── reviewer-2.md
│   └── ...
└── analysis/
    ├── comment-tracker.md            (atomic comment matrix)
    ├── review-analysis.md            (strategic overview)
    └── reviewer-comments-verbatim.tex (LaTeX transcription)
```

**Source PDF preservation:** The original reviews PDF is only ever **copied** to `reviews-original.pdf`. Never move, rename, or delete the source file from its original location (e.g., `to-sort/`, Downloads, etc.). The user decides when to clean up the original.

**Principle:** `correspondence/` holds exchanges with reviewers (their comments, your rebuttal). Internal review work (e.g., referee2 agent reports) goes in `docs/{venue}/internal-reviews/`.

If the round directory already exists (e.g., from manual setup), do NOT overwrite existing files. Instead:
- If `comment-tracker.md` already exists, name the new one `comment-tracker-v2.md` (or next version)
- If `reviewer-comments-verbatim.tex` already exists, name the new one `reviewer-comments-verbatim-v2.tex`
- Always flag existing files to the user before writing

## Protocol

### Phase 1: Setup

1. Confirm inputs (PDF path, project path, venue, round, deadline, lead author)
2. Create the directory structure under `correspondence/referee-reviews/{venue}-round{n}/`
3. Copy the reviews PDF to `correspondence/referee-reviews/{venue}-round{n}/reviews-original.pdf`

### Phase 2: Read the Reviews

1. Read the reviews PDF using the Read tool (supports PDF natively)
2. For large PDFs (>10 pages), read in page ranges (e.g., pages 1-10, then 11-20)
3. Extract for each reviewer:
   - Reviewer identifier (name, number, or anonymous ID)
   - Recommendation / score (if provided)
   - Whether revision is allowed
   - General assessment text
   - Individual comments (each as a separate item)

### Phase 3: Generate Individual Review Markdown Files

Create one markdown file per reviewer in `reviews/`:

1. Create the `reviews/` subdirectory
2. For each reviewer, write `reviews/reviewer-{n}.md` containing:
   - **Header:** reviewer identifier, recommendation/score, whether revision is allowed
   - **General Assessment:** full verbatim text of the reviewer's overall assessment
   - **Individual Comments:** each comment as a numbered item with its assigned ID (`R{n}-C{m}`), verbatim text, and section/page reference if mentioned
3. Use this template for each file:

```markdown
# Reviewer {N}

**Recommendation:** {recommendation or score}
**Revision allowed:** {Yes / No / Not stated}

## General Assessment

{verbatim general assessment text}

## Comments

### R{N}-C1 {optional: section/page reference}

{verbatim comment text}

### R{N}-C2 ...

{verbatim comment text}
```

4. If files already exist in `reviews/`, follow the same versioning convention as other outputs (flag and version)

### Phase 4: Generate LaTeX Verbatim Transcription

Using the template from `templates/referee-comments/reviewer-comments-verbatim.tex`:

1. Create one `\section{}` per reviewer with comment count and recommendation
2. Place general assessment in a `genbox` environment
3. For each specific comment:
   - Assign an ID: `R{reviewer}-C{comment}` (sequential within each reviewer)
   - Identify the section/page reference if the reviewer mentions one
   - Place the full verbatim text in the comment table
4. If a single reviewer paragraph contains multiple distinct concerns, split into separate IDs and add a `\textit{\footnotesize Split: ...}` note
5. If any IDs are derived (split from a larger comment or inferred), add them to a Derived IDs appendix section
6. Compile with `latexmk` to verify it builds cleanly

### Phase 5: Generate Comment Tracker

Using the template from `templates/referee-comments/comment-tracker.md`:

1. Fill in the Triage Summary table
2. Populate the Comment Matrix — one row per atomic comment:
   - **ID:** matching the LaTeX verbatim IDs
   - **Reviewer:** reviewer number
   - **Comment:** short verbatim quote (first ~100 chars in quotes)
   - **Type:** classify as Major / Minor / Editorial / Question / Praise
   - **R&R Classification:** classify as NEW ANALYSIS / CLARIFICATION / DISAGREE / MINOR (see `references/rr-routing.md` for decision rules and signal words)
   - **Priority:** assign Critical / High / Medium / Low based on:
     - Critical = threatens acceptance if not addressed
     - High = significant concern, must address
     - Medium = reasonable concern, should address
     - Low = minor or editorial
   - **Action:** leave blank (for the user to fill)
   - **Owner:** leave blank
   - **Status:** set all to "Pending"
   - **Section:** paper section referenced, if identifiable
3. Fill in the Status Dashboard counts
4. Generate a **Routing Summary** table grouping comments by R&R classification:
   - NEW ANALYSIS: list IDs + brief description of required analysis
   - CLARIFICATION: list IDs + target sections needing revision
   - DISAGREE: list IDs + flag for user review
   - MINOR: list IDs
5. Identify **Cross-Cutting Themes** — concerns raised by 2+ reviewers, tagged T1, T2, etc.
6. Leave Evidence Log, Patch Plan, Response Blocks, and Blockers empty (user fills during revision)

### Phase 6: Generate Review Analysis

Using the template from `templates/referee-comments/review-analysis.md`:

1. Fill in Scores & Recommendations table
2. Write a Reviewer Profile for each reviewer:
   - **Posture:** hostile / sceptical / constructive / supportive (infer from tone)
   - **What they liked:** bullet points
   - **What they want revised:** numbered list
   - **Assessment:** paragraph on how addressable their concerns are
   - **Risk:** None / Low / Medium / High with explanation
3. Identify Cross-Cutting Themes — concerns that appear across 2+ reviewers, tagged T1, T2, etc.
4. Estimate Acceptance Probability with factors for/against
5. Bucket comments into Priority 1/2/3 response categories
6. List Vulnerabilities (weaknesses in the paper that reviewers exposed)
7. Populate the Publication Strategy section:
   - **Strategy A (minimal revision):** venues that would accept the paper's strengths as-is, despite the weaknesses reviewers identified. Look for venues that value the descriptive/empirical contribution without demanding the specific improvements the current reviewers want.
   - **Strategy B (substantial revision):** venues worth targeting if the authors invest effort to address the major reviewer concerns. These should be equal or higher prestige than the current venue.
   - For conferences: check CORE rankings via `.context/resources/venue-rankings.md` (and the CSV at `.context/resources/venue-rankings/core_2026.csv`). Note upcoming deadlines.
   - For journals: check CABS AJG rankings via `.context/resources/venue-rankings.md` (and the CSV at `.context/resources/venue-rankings/abs_ajg_2024.csv`). For SJR score, query the Elsevier Serial Title API (see venue-rankings.md for snippet; requires `SCOPUS_API_KEY`). Flag journals below CABS 3 only if there's a strong fit rationale.
   - **Recommendation table:** rank 3-5 venues in priority order with rationale. First option should always be "revise for current venue" if acceptance probability is above ~30%.
   - **Key Decision:** frame the core trade-off the authors face (e.g., speed vs. impact, minimal vs. substantial revision effort).
   - Consider the paper's discipline and methodology when suggesting venues — a qualitative policy analysis fits different outlets than a computational study.
8. Leave Timeline empty (user fills)

### Phase 6.5: Strategic Coaching (Interactive)

For each **Major** or **Critical** comment, walk the user through a structured deliberation:

1. **Understanding:** "What is this reviewer's core concern — methodology, theory, or framing?"
2. **Position:** Classify as one of:
   - **Agree** — will revise as suggested
   - **Partially agree** — will address the spirit but not the exact suggestion. State which parts you accept and which you push back on.
   - **Disagree** — will rebut with evidence. Draft the core rebuttal argument.
3. **Risk assessment:** "If you push back on this, how likely is the reviewer to escalate? Is it worth the risk?"
4. **Response sketch:** One-sentence draft of the response direction (not the full response — just the strategy).

Record these in the Comment Matrix by adding two columns after `R&R Classification`:
- **Position:** Agree / Partially / Disagree
- **Strategy:** one-line response direction

**Rules:**
- Only Major and Critical comments get coaching. Minor/Editorial are auto-classified as "Agree" with no coaching.
- the user can say "skip coaching" to bypass and classify all remaining as Agree.
- Maximum 2 rounds of dialogue per comment — do not over-discuss.
- Do not write the actual response letter — that remains the user's job.

### Phase 7: Summary & Review

Present to the user:
- Total comments extracted (by reviewer)
- Breakdown by type and priority
- Key cross-cutting themes
- Position summary: N Agree / N Partially / N Disagree
- Any comments that were ambiguous or hard to classify
- Ask for corrections before finalising

## Critical Rules

1. **Verbatim means verbatim.** Never paraphrase reviewer text in the LaTeX transcription. Copy exactly.
2. **Every comment gets an ID.** No reviewer concern should be lost. If in doubt, give it its own ID.
3. **Don't write actions.** The Comment Matrix `Action` column stays blank — that's the user's job.
4. **Don't overwrite.** If files already exist at the target location, flag and version.
5. **Compile the LaTeX.** The verbatim document must build without errors before the skill completes.

## Templates

Located in `templates/referee-comments/`:
- `comment-tracker.md`
- `review-analysis.md`
- `reviewer-comments-verbatim.tex`

## Cross-References

- `/proofread` — for proofreading the response letter before submission
- `/bib-validate` — run after revision to check bibliography
- `/pre-submission-report` — full quality check before resubmission
- `paper-critic` agent — for self-review of the revised paper
- `references/rr-routing.md` — R&R classification system and routing logic for revision workflow
