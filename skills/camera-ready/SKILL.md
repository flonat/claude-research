---
name: camera-ready
description: "Convert an accepted anonymous-submission LaTeX paper (AAAI/AIES/ACM-style) to camera-ready and implement the accepted reviews. Use when a paper is accepted with no rebuttal and you need to de-anonymize, add copyright, turn on section numbering, implement each reviewer's minor revisions, optionally move proofs to a non-counted appendix, and QA. Not for R&R/revise-and-resubmit (use /strategic-revision) or for preprints (use /preprint)."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(mkdir*)
  - Bash(cp*)
  - Bash(ls*)
  - Bash(grep*)
  - Bash(stat*)
  - Bash(latexmk*)
  - Bash(pdftotext*)
  - Bash(pdftoppm*)
  - Bash(mdls*)
  - Bash(uv run python*)
  - AskUserQuestion
  - Task
---

# camera-ready: Accepted Paper → Camera-Ready + Review Implementation

For a paper that has been **accepted** (no rebuttal stage): produce the camera-ready version and implement the reviewers' (typically minor) revisions. Distinct from `/strategic-revision`, which handles **R&R** (rebuttal, DAG, resubmission strategy).

## When to Use

- Acceptance notification arrived; reviews are final; you implement rather than argue.
- Triggers: "prepare the camera-ready", "implement the reviews for the accepted paper", "de-anonymize and finalize".

## Operating Rules (read first)

- **Overleaf-canonical**: edit the Overleaf/`paper/` symlink target, not any git mirror (`overleaf-canonical-source.md`). The `.tex` is a **live edit surface** — obey `reconcile-before-rewriting.md` (fresh-read, narrow edits, no `replace_all`/full-`Write`, mtime check).
- **Phased-work**: stop after each phase, summarize, await `continue` (`phased-work.md`) unless `--autonomous`.
- **mark-unverified**: never assert a reviewer-suggested citation/venue fact you haven't verified.
- **Status logging**: acceptance means the vault/atlas status *should* move to Accepted/camera-ready per `multi-system-completeness.md` — **but** if the formal decision letter hasn't landed yet (early prep), hold status changes until the user confirms.

## Phase 0 — Setup & verify
1. **Save the reviews** to `paper-{venue}/correspondence/referee-reviews/<YYYY-MM-DD>-<venue>-reviews.md` (score table + verbatim text).
2. **Back up** the submitted `main.tex`/`.bib`/`.pdf` → `paper-{venue}/backup/submitted-<YYYY-MM-DD>/`.
3. **Verify reviewer-suggested citations** before adding any (DOI/title via `scholarly`/`paperpile`); reviewers often mis-spell/mis-date (e.g. "Edelmann 1996" → Suchman & Edelman 1996). Stash verified new entries.
4. **Build a reviewer-point → action table** so nothing is dropped; confirm scope with the user.
5. **Confirm the page-limit rule** (see Phase 3) — `[UNVERIFIED]` until checked against the CfP/acceptance email.

## Phase 1 — Camera-ready mechanics (low-risk)
- **De-anonymize**: replace `\author{Anonymous Submission}` with the real author/affiliation block.
- **Copyright**: AAAI auto-renders the slug from the style; set `\copyrightyear{<proceedings year>}`. ACM: set `\setcopyright`/`\acmConference`/DOI per the rights email. Never use `\nocopyright` for AAAI.
- **Section numbering**: AAAI submissions ship with `\setcounter{secnumdepth}{0}` → set to `2`. This also **fixes blank `Section~\ref{}`** references (a common reviewer complaint).
- Compile; confirm 0 undefined refs and the copyright slug renders on p1.

## Phase 2 — Bibliography
- If adopting canonical (e.g. Paperpile) keys, invoke **`/bib-rekey`** (DOI-safe remap + diff-verified `\cite` rewrite).
- Add the verified reviewer-suggested citations and any self-citations (camera-ready is de-anonymized, so self-cites are normal — use the **published** entry, not the arXiv preprint, when one exists).
- Compile; **0 undefined citations**.

## Phase 3 — Structure (appendix offload) — GATED on the page rule
- **First verify** whether the venue's page limit **excludes the technical appendix** (AAAI/AIES typically count body + figures; references and a post-references appendix are often exempt — confirm). This determines how aggressively to offload.
- If excluded: move full proofs / long derivations / worked-example arithmetic to `\appendix` after references; leave each result's **statement + a 3–5 sentence proof sketch + appendix pointer** in the body.
- **Equation-label coupling**: if a proof you are moving *defines* equations the body references, **lift those equations into the body** first (else body text points at appendix equation numbers). Verify 0 undefined after.

## Phase 4 — Reviewer revisions + intuition aids
- Implement each row of the Phase-0 action table.
- Common high-value additions for broad-audience venues: a **plain-language mechanics paragraph**, a **notation table**, a **results-at-a-glance table**, one-line **Reading** glosses, and a **mechanism figure/boxed causal chain** (covers "more visualization" and "more plain-language" asks at once).
- Apply any consistency fixes surfaced in Phase 0 (e.g. clamped first-best, index-vs-probability clarifications) — flag any that touch a theorem's math for author sign-off before editing.

## Phase 5 — QA
- `latexmk` clean (exit 0); **0 undefined** refs/citations; no large overfull boxes; no placeholders/TODOs.
- **Page-budget check**: locate where references/appendix begin (`pdftotext` + form-feed page count, or per-label pages from `.aux`); confirm **body ≤ limit** (appendix/refs exempt per Phase 3).
- **Visual render** key pages (`pdftoppm`) — de-anon header + copyright slug, new tables/figures, appendix.
- Run `/proofread` scoped to the **new prose** only.

## Phase 6 — Author-side handoff
Report what remains for the human: **acknowledgments** (now un-anonymized — offer a funding stub), signed copyright/rights form, reproducibility checklist, and the vault/atlas **status update to Accepted** (per the Operating Rules caveat).

When the user confirms the camera-ready was uploaded: append the `history:` rows to the vault submission entry (`event: decision, outcome: accept` if not already recorded, then `event: camera-ready` with the archive `files:` pointer) and archive the as-submitted files per `rules/submission-file-archive.md` (human-supplied only).

## Anti-Patterns

- **Don't move proofs to an appendix before confirming the appendix is page-exempt.** If it counts, you've just relocated, not saved, space.
- **Don't `replace_all` or full-`Write` the live `.tex`.** Narrow edits; for bulk citekey work defer to `/bib-rekey`'s diff-verified flow.
- **Don't add a reviewer-suggested citation from memory.** Verify it — reviewers mis-cite.
- **Don't chain all phases in one response.** Checkpoint per `phased-work.md`.
- **Don't log acceptance to vault/atlas if the formal decision letter hasn't arrived** — confirm with the user.

## Verification

- All reviewer points map to a concrete edit (action table fully checked off).
- Build clean, 0 undefined, body within page limit, copyright slug present, author block de-anonymized.
- Submitted version preserved in `backup/`.

## Cross-References

| Skill | Relationship |
|---|---|
| `/bib-rekey` | Phase 2 bibliography rekey + `\cite` remap |
| `/strategic-revision` | The R&R counterpart (rebuttal + DAG) — use that, not this, for revise-and-resubmit |
| `/proofread`, `/latex`, `/bib-validate` | QA components composed in Phases 2 & 5 |
| `/preprint` | For an arXiv/working-paper variant instead of a venue camera-ready |
