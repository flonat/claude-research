---
paths:
  - "**/*.tex"
  - "**/*.py"
  - "**/*.R"
---

# Rule: Severity Gradient

## Principle

**Calibrate critique intensity to the document's maturity.** Early drafts need encouragement and direction; pre-submission papers need adversarial scrutiny. The same issue that's a "note for later" in Discovery is a "must-fix blocker" in Pre-submission.

## Phases

| Phase | Tone | Issue Reporting | Threshold |
|-------|------|-----------------|-----------|
| **Discovery** | Encouraging, directional | Skip Minor (m-tier). Report Critical and Major only. Focus on structural and conceptual issues. | 60/100 |
| **Drafting** | Constructive, thorough | Report all tiers. Frame fixes as improvements, not failures. | 70/100 |
| **Pre-submission** | Strict, adversarial | Report all tiers. No mercy — every issue is a reviewer attack surface. | 90/100 |
| **Peer Review** | Adversarial, formal | Full Reviewer 2 mode. Score hard. Flag anything a hostile reviewer could exploit. | 90/100 |

## Phase Detection

Detect the phase from context clues. Use the **first matching** signal:

| Signal | Phase |
|--------|-------|
| User says "early draft", "just started", "rough draft", "exploring" | Discovery |
| User says "draft", "working on", "in progress" | Drafting |
| User says "ready to submit", "pre-submission", "final check", "about to submit" | Pre-submission |
| User says "R&R", "revision", "reviewer comments", "resubmission" | Peer Review |
| `reviews/` directory has existing reports | Peer Review |
| `correspondence/referee-reviews/` exists with content | Peer Review |
| Paper has no abstract or introduction is < 1 page | Discovery |
| Paper has all sections but obvious TODOs/placeholders | Drafting |
| Paper appears complete with bibliography | Pre-submission |

**When ambiguous:** Default to Drafting. If the user corrects you, adjust immediately.

## Phase Banner

Every critic or review report **must** include a Phase Banner immediately after the header:

```markdown
**Phase:** [Discovery | Drafting | Pre-submission | Peer Review]
**Detected from:** [signal that triggered phase detection]
**Threshold:** [XX/100]
```

This makes the calibration transparent and overridable.

## What Changes Per Phase

- **Scoring:** tiers and definitions are unchanged; only the **threshold** moves (see table). Score 75 = "Ship with notes" in Discovery but "Revise" in Pre-submission.
- **Issue completeness:** Discovery skips m-tier; Drafting+ reports all tiers.
- **Tone:** Discovery uses "consider restructuring"; Drafting uses "would benefit from"; Pre-submission and Peer Review drop softeners.

## When This Applies

`paper-critic`, `referee2-reviewer`, `/proofread`, `/pre-submission-report`, and any task producing a scored quality report. **Skip** for mechanical tasks (compilation, bib-validate), `/code-review` (its own scoring), or non-scored tasks.

## Override

The user can override the detected phase at any time:
- "Review this as if it's ready to submit" → Pre-submission regardless of signals
- "Go easy, this is just an early draft" → Discovery regardless of signals
- "Full Reviewer 2 mode" → Peer Review regardless of signals

## Count Calibration

**A sanity check on how many issues get reported.** Independent of phase — it catches over-compression (merging distinct issues into one) and over-reporting (ghost issues, paraphrase duplicates, listing every sentence as a flaw).

| Tier | Typical count for a **publishable** paper | Signal if out of band |
|------|-------------------------------------------|----------------------|
| Major (M-tier) | **3–7** | <3 → likely over-merged or too lenient; >7 → either the paper is genuinely weak, or moderate issues are being mis-tiered as major |
| Moderate + Minor (combined) | remainder, up to **~25** | — |
| **Total issues** | **15–30** | <15 → suspect over-merging (root-cause merges hiding distinct fixes); >30 → suspect over-reporting (paraphrase duplicates, sentence-level nits) |

### How to apply

1. Count findings by tier after producing the report.
2. If outside the expected band, **flag and reconsider the tiering** — don't silently ship an anomalous count.
3. Root-cause merge Major issues (two symptoms, one fault = one Major). Keep independent Moderate/Minor separate even within one section.
4. Earlier phases (Discovery/Drafting) skew Major-heavy — expected, not a calibration failure.

**Legitimate exceedances:** rejection-candidate papers (>7 Major is informative), long papers (>40pp may total 40+), or aggregated `synthesise-reviews` output (apply per reviewer, not to merged output).

**Source:** OpenAIReview (Chicago HAI) — bands derived from a 52-comment expert benchmark across 4 papers.

**Applies to:** final reports from `paper-critic`, `referee2-reviewer`, `peer-reviewer`, `synthesise-reviews`, and any agent consolidating multiple sub-agent findings.
