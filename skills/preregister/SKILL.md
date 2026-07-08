---
name: preregister
description: "Use when the user needs to write a preregistration for an empirical study before collecting data — OSF-Standard 'Pre-Data Collection Registration' by default, or the shorter AsPredicted 9-question form via `--aspredicted`. Triggers on phrases like 'preregister this study', 'OSF prereg', 'AsPredicted', 'register hypotheses', 'prereg the experiment', 'lock in the analysis plan before running', or whenever the user is about to launch a Prolific / lab / survey / computational-audit experiment and wants a time-stamped record of the design + analysis. Produces a single, upload-ready markdown file with every standard section filled in (hypotheses, design, sampling, variables, analysis, exclusions, stopping rule). Composes /hypothesis-generation, /experiment-design, /causal-design, /synthetic-data (power), and /ethics-review by reference."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# Preregister

Turn a study idea into a registry-ready preregistration document — one markdown file that maps section-for-section onto OSF's "Pre-Data Collection Registration" template (or AsPredicted's 9 questions) and can be pasted into the registry verbatim.

This is the *gate before data collection*. The point is to commit, in writing, to:

- What the hypotheses are (directional, falsifiable)
- What will be measured and how
- Who will be sampled, how many, and when collection stops
- Which statistical test answers which hypothesis
- What counts as an exclusion or outlier
- What is **confirmatory** vs **exploratory**

Once a study is preregistered, every deviation has to be acknowledged in the paper. Getting the prereg right is the cheapest hour you'll ever spend on a study.

## Triggers

Use this skill whenever the user says any of:

- "preregister", "prereg", "OSF prereg", "AsPredicted"
- "register hypotheses", "lock in the analysis plan", "before I collect data"
- "I'm about to launch on Prolific / Qualtrics / the lab — can you prereg this?"
- "write up the design + analysis plan for OSF"

Also trigger proactively (after surfacing the suggestion, not auto-running) when the user is clearly *about to start data collection* on an empirical study — survey experiment, behavioural lab, online experiment, computational audit — and no prereg has been written.

## Modes

| Mode | Flag | Use when |
|------|------|----------|
| **OSF-Standard** (default) | none | Most studies. The full template — what reviewers, supervisors, and replicators expect. Roughly 1,500–3,000 words. |
| **AsPredicted** | `--aspredicted` | Quick, low-overhead studies; pilots; the 9 essential questions only. Roughly 500–1,200 words. |
| **From-plan** | `--from <path>` | Pre-written design notes, a plan in `docs/plans/`, or an existing internal protocol. Skip elicitation; transcribe + sharpen. |
| **Update** | `--update <existing.md>` | The study has been registered already and the user wants a revised version (e.g. amendment after pilot). Diff-aware. |
| **Autonomous** | `--autonomous` / `-y` | No mid-run questions; use sensible defaults at every choice point and flag uncertainties as `[UNVERIFIED]` for the user to resolve in the final pass. Honours `phased-work.md`'s autonomy convention. |

Modes compose: `/preregister --aspredicted --from docs/plans/2026-06-09_pilot.md` is valid.

## Workflow

### Phase 1 — Locate context

Before asking the user anything, read what already exists. A preregistration is *much* easier to write when the surrounding design has been thought through.

Check, in order:

1. `docs/plans/` and `log/plans/` — any plan files with the study design
2. Project `CLAUDE.md` — hypotheses, methods notes, RQ statements
3. `MEMORY.md` — `[LEARN:method]` and `[LEARN:domain]` entries, Estimand Registry, Key Decisions
4. Atlas topic file (resolve via `~/.config/task-mgmt/research-root` + project name) — Key References, design notes
5. Any existing `prereg/` directory — prior versions or sibling preregs to mirror style
6. `data/` — if any pilot data exists, note it (the registry distinguishes "pre-data" vs "after pilot")

Surface what you found in 3-4 lines so the user knows you started from their existing thinking, not a blank slate.

### Phase 2 — Elicit the missing pieces

Use `AskUserQuestion` to fill gaps. Don't ask what you already know from Phase 1.

The non-negotiable inputs for any preregistration:

1. **Research question** — one sentence
2. **Hypotheses** — directional, numbered (H1, H2, …), tied to specific tests
3. **Population & sampling frame** — Prolific? UK undergrads? Synthetic agents? A specific Reddit subset?
4. **Sample size + power justification** — N, target power, expected effect size, source of the effect-size guess
5. **Stopping rule** — fixed N? sequential? time-bounded?
6. **Design** — between/within/mixed; conditions; assignment mechanism
7. **Manipulated variables** — the IVs, with operationalisation
8. **Measured variables** — the DVs and any moderators/mediators, with operationalisation
9. **Confirmatory analysis plan** — for each hypothesis, the *exact* test (model, estimator, inference threshold)
10. **Exclusion rules** — attention checks, completion time, duplicates, IP filters; pre-specified
11. **Outlier handling** — how defined, how handled, before or after model fit
12. **Missing data** — listwise, multiple imputation, FIML, conditional on what?
13. **Exploratory analysis** — anything *not* confirmatory must be labelled as such here

For computational audits and agent-based studies, also:

14. **Model / system under test** — exact API version, sampling parameters, date locked
15. **Prompt protocol** — fixed wording, randomisation, attestation that prompts won't change after registration
16. **Re-run policy** — if the model is updated mid-collection, what happens?

For AsPredicted mode, condense (1–13) into the registry's 9 questions — see `references/aspredicted-template.md`.

### Phase 3 — Sharpen

This is where the skill earns its keep. Before writing the document:

- **Hypotheses must be falsifiable.** "We expect a positive effect" is not a hypothesis. "H1: the AI-assisted condition will produce significantly higher (p < .05, two-sided) decision quality scores than the unassisted condition, with a Cohen's d ≥ 0.3" is.
- **Each hypothesis must name its test.** No floating predictions without a matching line in the analysis plan.
- **Power calculations must be honest.** If the user has no pilot data and no published effect size to anchor on, *say so* and pick a smallest-effect-size-of-interest (SESOI) instead of inventing a plausible-looking `d`. Use `/synthetic-data` for power simulation when the design is non-standard.
- **Identification.** For causal claims, call `/causal-design` semantics: what's the estimand, what's the assignment mechanism, what threats are being addressed by design vs by assumption?
- **Exclusion rules can't be open-ended.** "We will exclude inattentive participants" is not enough — name the attention check, the threshold, and the expected exclusion rate.
- **Exploratory ≠ confirmatory.** Anything the user "might also look at" goes in the exploratory section, not the confirmatory plan. Mixing them is the single biggest source of registration credibility loss.

If anything material is missing or vague, flag it explicitly (`[UNVERIFIED — power calc assumes d=0.4 from Smith 2022, confirm]`) per the global `mark-unverified.md` rule, rather than inventing.

### Phase 4 — Write

Default output path:

```
prereg/YYYY-MM-DD-{study-slug}.md
```

Where `{study-slug}` is a short hyphenated label for the study (e.g. `ai-assistance-decision-quality-pilot`). If the project has no `prereg/` directory, create it. If running outside a project (rare), put the file in the current working directory and tell the user.

Use `references/osf-standard-template.md` for OSF mode and `references/aspredicted-template.md` for AsPredicted mode. Both templates are designed to be pasted *verbatim* into the corresponding registry — the section headings match what OSF and AsPredicted expect.

After writing:

- Run a self-check via `references/elicitation-checklist.md` — every item ticked or explicitly waived
- Word-count the file (rough budget: 1500–3000 for OSF, 500–1200 for AsPredicted)
- Output the path + word count + any `[UNVERIFIED]` flags still in the document

### Phase 5 — Hand-off

Print the next steps:

1. **Upload.** Either:
   - OSF: `https://osf.io/registries/osf/new` → "Pre-Data Collection Registration" → paste section by section
   - AsPredicted: `https://aspredicted.org/` → create new prereg → paste answer by answer
2. **Time-stamp.** OSF and AsPredicted both stamp the submission server-side; the file in `prereg/` is the local record, not the registration itself.
3. **Get the URL.** After submission, OSF returns a DOI; AsPredicted returns a short URL. Save it into the markdown file's frontmatter and into the project's atlas topic `outputs[*]` entry as a `Preregistration` artifact (consistent with `preprint-vs-submission.md` — a prereg is also *not* a submission).
4. **Lock the file.** No further edits to the markdown after submission. Subsequent changes go in a dated amendment file (`prereg/YYYY-MM-DD-{slug}-amendment.md`) so the trail is honest.

## Composed skills

| Skill | When to invoke | Why |
|-------|----------------|-----|
| `/hypothesis-generation` | Phase 2 if hypotheses are vague or single-direction | Forces directional, falsifiable phrasing |
| `/experiment-design` | Phase 2 if assignment, blocking, or counterbalancing is unclear | Ensures the design supports the test |
| `/causal-design` | Phase 3 if a causal claim is being made | Identification before analysis plan |
| `/synthetic-data` | Phase 3 if power requires simulation (multilevel, ordinal, non-standard) | Honest power, not invented `d` |
| `/ethics-review` | Phase 3 for online / participant studies | Catch consent, debrief, PII issues before they delay collection |

These are pointers, not auto-invocations. Suggest them when the gap is visible; don't burn turns running every composed skill on every study.

## Output format

```markdown
---
title: <Study title>
study_slug: <study-slug>
template: osf-standard | aspredicted
created: YYYY-MM-DD
project: <project name>
authors: [<list>]
status: draft | submitted
osf_url: <fill after submission>
aspredicted_url: <fill after submission>
data_collection_status: not_yet_started | pilot_only | started
---

# Preregistration — <Study title>

## 1. Study information
…
## 2. Hypotheses
…
## 3. Design plan
…
## 4. Sampling plan
…
## 5. Variables
…
## 6. Analysis plan
…
## 7. Exclusion criteria
…
## 8. Stopping rule
…
## 9. Exploratory analysis
…
## 10. Other
…
```

(Section numbers and headings exactly match OSF-Standard. AsPredicted mode uses the 9-question structure instead — see `references/aspredicted-template.md`.)

## Gotchas

- **"We'll collect data and then decide"** is not a preregistration. If the user is still negotiating with themselves about which test to run, push back — the point of the file is to *commit*.
- **Power calculation without an effect size** is not power — it's a placeholder. If the user has no defensible `d`/`f²`/odds-ratio to anchor on, write a SESOI ("smallest effect we'd care about is d=0.2") and say so.
- **Confirmatory bloat.** Listing 14 confirmatory tests is a soft form of HARKing. Three to five preregistered confirmatory tests is the realistic ceiling for one study; everything else is exploratory.
- **Exclusion rules that "might" apply** aren't exclusion rules. Name them now, with thresholds, or drop them.
- **Computational audits drift fast.** If the LLM under test is `gpt-4o-2024-11-20`, lock that string into the prereg. A prereg that says "GPT-4" is meaningless six months later.
- **The file is the local record, not the registration.** The OSF / AsPredicted server timestamp is what matters legally; the markdown is for the project's records. Don't claim "preregistered" until the URL is back.
- **Amendments are normal but must be explicit.** If anything changes after submission, write `YYYY-MM-DD-{slug}-amendment.md` next to the original. Editing the original in-place destroys the trail.
- **Don't conflate this with a vault submission.** A prereg post is not a venue submission — it lives in `outputs[*]` on the atlas topic, not in `~/vault/submissions/` (same logic as `preprint-vs-submission.md`).
- **Don't run `/proofread` over the prereg.** The voice is intentionally terse and template-driven; copy-editing it the way you would a paper is wasted effort.

## When to skip

- The user just wants to *think out loud* about a study; offer `/experiment-design` or `/hypothesis-generation` instead and circle back when they're ready to commit
- The study is already collected — preregistration after data collection is not preregistration; that's a "registered report" or, if disclosed, a "post-hoc registration" and should be labelled as such in the paper, not slipped through this skill
- The study is pure theory or simulation with no empirical data — there's nothing to preregister in the OSF/AsPredicted sense

## Failure modes guarded

- `mark-unverified.md` — flag every uncertain number (effect size, expected N, exclusion rate) rather than inventing
- `phased-work.md` — Phase 2 elicitation can be long; pause for user confirmation before Phase 3 sharpening if the elicitation took >10 turns
- `preprint-vs-submission.md` — preregistration is an `outputs[*]` event on the atlas topic, not a vault submission
- `multi-system-completeness.md` — after submission, update both the markdown frontmatter AND the atlas topic `outputs[*]` with the prereg URL
