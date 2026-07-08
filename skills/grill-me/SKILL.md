---
name: grill-me
description: "Use when you want to be interrogated ONE question at a time — either to (a) defend your own research (viva, job talk, seminar Q&A, hostile-referee prep) or (b) study a class / subject you're learning (exam revision, active recall). An interactive adversarial/Socratic oral drill grounded in your actual material, escalating on weak answers, then a study sheet of what you fumbled with model answers. Triggers: 'grill me', 'grill me on X', 'viva prep', 'defend my paper', 'quiz me on this class', 'test me on <topic>', 'exam revision', 'help me study X'. Distinct from /devils-advocate (stress-tests arguments in prose) and referee2-reviewer / paper-critic (produce a WRITTEN critique) — here YOU answer aloud."
allowed-tools: Read, Glob, Grep, Bash(ls*), Bash(cat*), Bash(grep*), Bash(git log*), Write, AskUserQuestion
argument-hint: "[paper-path | topic | course-notes | subject] [--reviewer2 | --coach] [--study | --defend] [--rounds N] [--focus <dimension>]"
---

# Grill Me — Interactive Oral-Exam Drill

> You answer, out loud, one grounded question at a time. This skill plays a skeptical examiner and interrogates you — escalating on weak or evasive answers — then hands you a study sheet of what you fumbled, with model answers. Two flavours: **defend** your own research, or **study** a class you're learning.

## Two Modes (auto-detected; override with `--defend` / `--study`)

| | **Defend** | **Study** |
|---|---|---|
| Target | *Your own* paper / model / proof / research idea | A class, subject, textbook chapter, lecture notes you're *learning* |
| Goal | Rehearse defending your choices under pressure | Test + deepen recall and understanding of the material |
| "Right answer"? | No single right answer — you defend a *choice*; the examiner probes whether it holds | Yes — there's an objectively correct answer; wrong answers get corrected |
| Default persona | Skeptical-but-fair examiner (viva/referee) | Examiner-Socratic (an examiner who also teaches when you miss) |
| Prep for | Viva · job talk · seminar Q&A · referee/rebuttal armour | Exams · comprehension checks · learning a new field |

**Auto-detect:** if the target is one of the user's own artifacts (a `paper-*/` dir, a proof, an atlas topic he authored) → **defend**. If it's course material / textbook / lecture notes / a subject he's revising → **study**. When ambiguous, ask once.

Everything below is shared; mode-specific differences are called out inline.

## When to Use

- **Defend:** preparing for a viva / thesis defense / job talk / seminar Q&A; building referee/rebuttal armour before submission.
- **Study:** revising for an exam; checking you actually understand a class, textbook chapter, or a new field — active-recall practice, not passive re-reading.

## When NOT to Use

- You want a **written critique** of a paper, not a live drill → `referee2-reviewer` / `paper-critic` / `/review-cluster`.
- You want to **stress-test an argument in prose** → `/devils-advocate`.
- You want to **draft a rebuttal** to reviews you already have → `/review-response` / `/strategic-revision`.
- You want a **passive summary** of the material → just ask for one; grill-me is for being *tested*.

grill-me is the only one where *you* are the one answering. If you don't want to type answers back and forth, use one of the above.

## Arguments

| Arg | Effect |
|---|---|
| `[target]` | Paper dir / `.tex` / `.pdf`, a proof, an atlas topic, **course notes / slides / textbook chapter**, or a plain subject name. Default: auto-detect `paper-*/paper` in CWD. |
| `--defend` / `--study` | Force the mode when auto-detect would guess wrong. |
| `--reviewer2` | Persona = **hostile Reviewer 2** (defend mode). |
| `--coach` | Persona = **supportive coach** — challenges but scaffolds a hint toward the answer (great for early study). |
| `--rounds N` | Number of primary questions (default 10; follow-ups don't count). |
| `--focus <dim>` | Concentrate on one dimension (see the tables in Phase 1). Default: spread. |

Default run = auto-detected mode, default persona, ~10 questions, all dimensions, **drill first then study sheet**.

## Procedure

### Phase 0 — Ground the material (read-only, silent)

Read the target so questions are *specific*, not quiz-show generic.

- **Defend:** read the paper `.tex`/PDF (or proof/idea). Identify the headline claim, contribution list, load-bearing assumptions, identification/proof spine, positioning vs the nearest rival. **Reuse existing review state — don't re-derive it:** read `reviews/INDEX.md` + latest `reviews/<scope>/*` reports, the project `CLAUDE.md` risks, and the venue's referee-bait (`docs/reference/venue-profiles/<field>.md`). A logged referee objection is your sharpest question.
- **Study:** read the course notes / slides / textbook chapter / syllabus provided (or, for a named subject with no file, work from the established canonical content of that subject — and say so). Identify the key definitions, mechanisms, results, derivations, and the *common misconceptions / exam traps* for that topic.

If nothing resolves, ask once (`AskUserQuestion`) what to grill on and at what level (e.g. "undergrad final? qualifying exam? seminar?").

### Phase 1 — Build the question bank (internal, not shown)

Rank a bank across the dimensions for the mode. Each question is grounded in the material, tagged by dimension + difficulty, and paired internally with the model answer + the trap (revealed only in the debrief).

**Defend dimensions:**

| Dimension | Probing… |
|---|---|
| Motivation / "so what" | Why care? What breaks if you're wrong? |
| Contribution / novelty | What's new vs the nearest rival? One contribution or three? |
| Model / assumptions | Which assumption is load-bearing? What happens when you weaken it? Is it stated? |
| Identification / proofs | Does the design identify the claim? Does each step hold? Counterexample to the general case? |
| Positioning / venue | Why isn't this subsumed by \[rival\]? Why this venue? |
| Robustness / limits | The most damaging check you *didn't* run? What would change your mind? |

**Study dimensions:**

| Dimension | Probing… |
|---|---|
| Recall / definitions | State the definition/result precisely — no hand-waving. |
| Mechanism / "why" | *Why* is it true? Explain the intuition, not just the statement. |
| Derivation / working | Work the step / solve the problem — show the reasoning. |
| Application / transfer | Apply it to a case you haven't seen; when does it fail? |
| Connections / compare | How does it relate to \[other concept\]? What's the difference? |
| Misconceptions / traps | The exam trap — the plausible-but-wrong answer, and why it's wrong. |

Seed the hardest slots from Phase 0's real material (logged referee issues in defend mode; known exam traps in study mode) before filling with derived questions.

### Phase 2 — The drill (interactive, ONE question per turn)

The drill is turn-by-turn — **ask exactly one primary question, then STOP and wait for the answer.** Never dump the bank; never answer your own question.

Evaluate each answer silently — does it *address* the question, is it *correct/grounded*, or is it a *dodge*? Then:

- **Weak / wrong / evasive →** grill it. Name the gap precisely. In **defend** mode: press whether the choice holds ("your Assumption 2 lets \(g\) be bimodal — so why does the peak stay at \(\bar\theta\)?"). In **study** mode: the answer is objectively wrong, so probe toward the correct one *without handing it over* ("not quite — what does the second-order condition require here?"). Push **1–2 follow-ups**, then log and move on.
- **Solid →** one-line acknowledgement, then next dimension or **raise the stakes**.
- **Adapt** — spend the budget where the defender struggles; skip what they've nailed.
- **Persona = tone, not substance:** examiner (rigorous, no free passes), reviewer2 (maximally adversarial), coach (drops a hint toward the answer — best for early study).

Keep a running tally: dimension · verdict (`solid` / `shaky` / `fumbled` / `wrong` / `dodged`) · the gap. The defender can say **"stop"**, **"skip"**, **"hint"**, or **"move on"** anytime.

**Never reveal the model answer mid-drill** (except a partial hint in coach mode) — recall under pressure is the point. End after `--rounds N` primaries (default 10) or on "stop".

### Phase 3 — Debrief + study sheet

When the drill ends:

1. **Readiness read (qualitative, no gimmick score):** e.g. defend — "6 solid / 3 shaky / 1 fumbled — the *mechanism* is airtight, but *contribution-count* and *identification* would draw blood in a viva"; study — "you know the definitions cold but the *derivations* and *application* transfer is where you'd lose marks".
2. **Per-dimension summary** — armoured vs exposed.
3. **The questions you fumbled / got wrong**, each as: the question · why your answer was weak/wrong · **the model answer (defend: a strong defense; study: the correct explanation)** · the trap · how costly it is (viva-fail / desk-reject / lost-exam-marks).
4. **Prep actions** — concrete and specific. Defend: what to add to the paper/talk, the one line to rehearse, the robustness check that kills the question. Study: exactly which sections/concepts to re-review, and the misconceptions to unlearn.
5. **Offer to persist it:** write the study sheet to `reviews/<scope>/grill-me/<YYYY-MM-DD>.md` (defend, scope = paper slug or `_project`) or `notes/grill-me/<subject>-<YYYY-MM-DD>.md` (study). Read-only w.r.t. the material — grill-me never edits your paper or notes.

## Key Rules

1. **One question per turn — the drill is the product.** Batch-dumping is a study sheet, not a grilling.
2. **Ground every question in the material.** No generic "what's your contribution?" / "define entropy" — tie it to *their* paper or *their* course notes.
3. **Reuse real material first** — a logged referee open-issue (defend) or a known exam trap (study) outranks an invented question.
4. **No model answers mid-drill** (partial hints only in coach mode). Answers land in Phase 3.
5. **Escalate then release** — 1–2 follow-ups, then log and move on; don't grind one point forever.
6. **Honest verdicts, calibrated tone.** Don't flatter a thin answer; the persona sets how hard you say it. In study mode, wrong is wrong — correct it kindly but clearly.
7. **Read-only on the material.** The only write is the optional study-sheet file.

## Anti-Patterns

- **Don't** print all 10 questions at once and wait — ask one, stop.
- **Don't** reveal the answer while the defender is still trying (recall under pressure is the point).
- **Don't** ask ungrounded quiz-show questions they can't map to their paper/class.
- **Don't** accept a dodge — name it and re-ask.
- **Don't** grill without a debrief — the study sheet is where the value is banked.
- **Don't** invent a referee objection when `reviews/INDEX.md` already records a real one, or a fake exam trap when the notes state the real one.

## Cross-References

| Skill / Agent | Relationship |
|---|---|
| `/devils-advocate` | Stress-tests arguments in prose; grill-me makes *you* defend them live |
| `referee2-reviewer` / `paper-critic` | Written adversarial critique; grill-me seeds its hardest defend-mode questions from their reports |
| `weakness-scanner` | Finds weak points; grill-me turns them into live questions |
| `/review-cluster` / `/pre-submission-report` | Run first — their logged open-issues are grill-me's sharpest defend material |
| `course-reading-list` / `init-project-course` | Course scaffolding; grill-me is the study-mode drill over that material |
| `docs/reference/venue-profiles/<field>.md` | Venue referee-bait to seed positioning/venue questions (defend mode) |
