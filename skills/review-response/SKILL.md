---
name: review-response
description: "Systematic reviewer response workflow: parse comments, classify by severity, develop response strategy, write structured rebuttal. Use when asked to 'write rebuttal', 'respond to reviewers', 'draft review response', or 'handle R&R'."
tags: [Research, Academic, Rebuttal, Paper Writing]
version: 1.0.0
---

# Review Response

Systematic workflow for responding to reviewer comments on academic papers. Covers the full cycle from parsing comments through to a polished rebuttal document.

## When to Use

- "Help me write a rebuttal"
- "Respond to reviewer comments"
- "Handle this R&R"
- "Develop a review response strategy"
- Paper has received referee reports and needs a structured response

## Workflow

```
1. Receive reviewer comments
2. Parse and classify each comment (Major / Minor / Typo / Misunderstanding)
3. Develop response strategy per comment (Accept / Defend / Clarify / Experiment)
4. Write structured responses
5. Tone check — every response must pass the tone checklist
6. Assemble final rebuttal document
```

## Step 1: Parse and Classify

Read all reviewer comments and classify each one:

| Type | Definition | Priority |
|------|-----------|----------|
| **Major** | Core methodology, experimental design, results interpretation — requires substantive revision or new analysis | High |
| **Minor** | Clarifications, presentation improvements, additional discussion — does not affect core contribution | Medium |
| **Typo** | Spelling, grammar, formatting, reference errors | Low |
| **Misunderstanding** | Reviewer misread or missed something already in the paper — needs polite clarification | High |

**Keyword signals for classification:**

- Major: "major concern", "fundamental issue", "missing experiments", "insufficient evidence", "not convincing"
- Minor: "minor concern", "could be improved", "please clarify", "suggestion"
- Typo: "typo", "grammar", "formatting", "inconsistent"
- Misunderstanding: "The authors did not..." (but they did), "It is unclear..." (but it is stated)

**Priority order:** Major > Misunderstanding > Minor > Typo

Present the full classification table to the user before proceeding to strategy.

## Step 2: Develop Response Strategy

For each classified comment, assign a strategy:

| Strategy | When to Use |
|----------|-------------|
| **Accept** | Comment is valid, fix is feasible and improves the paper |
| **Defend** | Current approach has sound justification; provide evidence and reasoning |
| **Clarify** | Reviewer missed or misread existing content; point to it politely |
| **Experiment** | Reviewer requests additional analysis that is feasible and would strengthen the paper |

**Decision flow:**

```
Comment → Is the reviewer correct?
  Yes → Is the fix feasible?
    Yes → Accept
    No  → Accept principle + explain constraint + offer alternative
  Partially → Accept valid part + Defend the rest with evidence
  No (misunderstanding) → Clarify with specific location references
  Requests new work → Is it feasible?
    Yes → Experiment
    No  → Explain limitation + offer alternative analysis
```

**Strategy combinations** (common in practice):
- Accept + Clarify: "We agree and have expanded Section 3. We also note this was partially addressed in Table 2."
- Defend + Experiment: "Our choice of X is justified because [reasons], but we have also added the comparison with Y as requested."

Full strategy library with templates: `references/response-strategies.md`

## Step 3: Write Responses

Each response follows this structure:

```markdown
**Comment N.M**: [Reviewer's original comment, quoted verbatim]

**Response**: [Our substantive reply]

**Changes**: [Specific modifications with section/page/table references]
```

**Non-negotiable rules:**
1. Every comment gets a response — even typos
2. Every response starts with thanks
3. Every claim in the response has evidence (data, citation, or specific manuscript reference)
4. Every change states its location (Section X, page Y, Table Z)
5. Never say "The reviewer is wrong" — use "We would like to respectfully clarify"

## Step 4: Tone Check

Before finalising, run every response through this checklist:

- [ ] Opens with genuine thanks (not perfunctory)
- [ ] Uses "We" not "I"
- [ ] No defensive or aggressive language
- [ ] No "obviously", "clearly", or "it is well-known"
- [ ] Specific location references for all changes
- [ ] No vague promises ("We will..." without specifics)
- [ ] Misunderstandings addressed with "We apologise for the confusion" not "The reviewer failed to notice"

Full tone guide with good/bad examples: `references/tone-guidelines.md`

## Step 5: Assemble Rebuttal Document

### Standard structure

```markdown
# Response to Reviewers

We sincerely thank all reviewers for their valuable feedback. We have carefully
addressed all comments and made substantial revisions. Below we provide detailed
responses to each reviewer's comments.

---

## Response to Reviewer 1

### Major Comments

**Comment 1.1**: [verbatim]
**Response**: [reply]
**Changes**: [locations]

### Minor Comments

**Comment 1.2**: [verbatim]
**Response**: [reply]
**Changes**: [locations]

---

## Response to Reviewer 2
[same structure]

---

## Summary of Major Changes

1. [Change 1] (addressing Reviewer X, Comment Y)
2. [Change 2] (addressing Reviewers X and Z)
3. ...

We believe these revisions have significantly strengthened the manuscript.
```

### Where multiple reviewers raise the same issue

Consolidate: "We thank Reviewers 1 and 3 for raising this important point. We have [action] which addresses both concerns."

### Where reviewers contradict each other

Acknowledge both perspectives: "After careful consideration, we have [chosen approach] because [reasons], which we believe addresses both reviewers' core concerns."

Full template library: `references/rebuttal-templates.md`

## Output

The skill produces a complete rebuttal document saved to the project's `correspondence/` directory (or paper directory if no correspondence folder exists).

**Naming convention:** `rebuttal-{venue}-{round}.md` (e.g., `rebuttal-jmp-r1.md`)

## Templates

Three templates live under `templates/referee-comments/`. Use them together
across a revision cycle:

| Template | Purpose | When |
|----------|---------|------|
| `reviewer-comments-verbatim.tex` | Internal landscape doc with reviewer text quoted verbatim, one row per comment ID (R1-C1, R2-C3, …) | First, on receipt of reports |
| `comment-tracker.md` | Triage + patch-plan table — type/priority/action/owner/status per comment ID | During planning (Steps 1–2) |
| `response-letter-ansrev.tex` | **Default LaTeX scaffold for the response letter.** Uses the `ansrev` package: auto-numbers reviewers and comments, pulls labels/citations/quotes from the main paper via `xr` | When writing the formal response (Steps 3–5) |

### When to use the LaTeX scaffold vs. the Markdown rebuttal

- **Markdown rebuttal** (the default `rebuttal-{venue}-{round}.md` above) — for venues that accept Markdown/plain-text uploads, internal review by co-authors, or quick R&Rs.
- **LaTeX `response-letter-ansrev.tex`** — when the venue requires a typeset PDF response, when the main paper has many labels/citations the response needs to reference, or when reviewers will be assigned numbers and cross-referenced ("see our reply to Reviewer 1 Comment 3"). Strongly preferred for OR / Management Science / journals with structured R&R.

### Using `response-letter-ansrev.tex`

1. Copy `templates/referee-comments/response-letter-ansrev.tex` into the project's `correspondence/` (or `paper-{venue}/paper/`) directory.
2. Copy `templates/referee-comments/ansrev/{ansrev.sty,revquote.sty}` next to it — these are vendored from GitHub (not on CTAN). See `templates/referee-comments/ansrev/README.md` for provenance.
3. Append `templates/referee-comments/ansrev/.latexmkrc-snippet` to the project's `.latexmkrc` so latexmk auto-recompiles the main paper for `xr` cross-refs.
4. Set `main={<main-file-basename>}` in the scaffold's `\usepackage{ansrev}` options.
5. Compile the main paper first, then the response file. Refer to comment-tracker IDs (`R1-C1`, `AE-C2`) as `\label{}`s inside each `\QA{}{}` — `\ref{R1-C1}` elsewhere expands to "Reviewer 1 Comment #1".

## Integration

- **Before writing:** Read the reviewer comments and the paper to understand context
- **During writing:** Cross-reference the paper for specific section/page numbers
- **After writing:** Run `/proofread` on the rebuttal document itself for tone and clarity
- **If paper changes are needed:** Track them separately — the rebuttal documents the *response*, not the *revision*

## Reference Documents

- `references/review-classification.md` — Classification criteria with keyword signals
- `references/response-strategies.md` — Strategy library with templates for each type
- `references/rebuttal-templates.md` — Full rebuttal document templates
- `references/tone-guidelines.md` — Tone guide with good/bad expression pairs
- `references/figure-interpretation.md` — Figure interpretation guide (useful when discussing figures in responses)

## Adapted from

galaxy-dawn/claude-scholar `review-response` skill, adapted for general academic research (not ML-specific).
