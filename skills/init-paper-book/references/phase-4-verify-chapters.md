# Phase 4: Verify Chapters (MANDATORY; Hard-Gates Phase 5)

**Design rationale.** A single LLM sub-agent doing "read chapters, read paper, compare" is structurally unreliable — observed 2026-05-16: a sub-agent returned PASS while fabricating paper-line numbers and missing 4 real blocking issues including 8 fabricated citation keys. The reliable design is **deterministic extraction first, LLM judgement only on residuals where semantic alignment matters**.

Phase 4 runs in two layers:

## 4.A — Deterministic checks (Python, exhaustive)

Run `references/verify_chapters.py` (alongside this skill). It performs:

1. **Citation key check.** Regex `\{cite:[tp]\}\`([^`]+)\`` extracts each comma-separated key. Parse `references.bib` for `@type{key,` patterns. Emit `missing_cite_keys` for any key not present.
2. **Self-cite fabrication red flag.** Any key matching the paper's first-author lastname + 4-digit year (e.g. `smith2026*`) is auto-flagged as `out_of_scope_self_cite`. Books never self-cite the paper they companion.
3. **Numeric token check.** Regex `[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?(?:\s*[±]\s*\d+\.?\d*)?` extracts every numeric token in chapter files. For each, search `main.tex` for the exact string. Skip years (`19\d\d|20\d\d`), section ordinals at line start, and numbers inside `figures/` paths. Emit `numeric_drift` for unmatched tokens.
4. **Acronym expansion.** Regex `\b[A-Z]{2,}\b`. Per chapter, build the distinct acronym set. Each must appear in `<phrase> (ACRONYM)` form somewhere in the same chapter OR be in baseline allow-list (`DM, GP, BO, MOBO, ABM, EI, EHVI, MCDM, VOI, MAP, DOI, URL, PDF, JSON, CDF, MSR, ETS, DTLZ, BC, NSGA, SE, KG`). Emit `accessibility_block` for any acronym used without expansion.
5. **Equation-prose pairing.** For each `$$...$$` block, verify the next 200 chars contain ≥60 non-math characters (prose). Emit `accessibility_block` for orphaned display equations.

Script writes JSON to `/tmp/init-paper-book-verifier-<slug>.json` and exits non-zero on any blocker.

CLI:

```bash
uv run python ~/.claude/skills/init-paper-book/references/verify_chapters.py \
    --book-dir ~/vault/books/<slug>/ \
    --paper-tex <full-path-to-main.tex> \
    --bib <full-path-to-references.bib> \
    --first-author-lastname <e.g. smith> \
    --output /tmp/init-paper-book-verifier-<slug>.json
```

JSON schema:

```json
{
  "verdict": "PASS" | "BLOCK",
  "counts": {"missing_cite_keys": N, "numeric_drift": N, "out_of_scope_self_cite": N, "accessibility_block": N},
  "missing_cite_keys": [{"chapter": "...", "key": "...", "line": N}],
  "numeric_drift": [{"chapter": "...", "value": "...", "line": N, "context": "..."}],
  "out_of_scope_self_cite": [{"chapter": "...", "key": "...", "line": N}],
  "accessibility_block": [{"chapter": "...", "issue": "missing_acronym_expansion" | "equation_no_prose", "detail": "...", "line": N}]
}
```

## 4.B — Semantic claim-scope check (LLM sub-agent, narrow)

Only run if 4.A passes. Dispatch ONE read-only sub-agent with a narrow brief: "Read chapters X, Y, Z and paper sections §A, §B, §C (specific line ranges from main.tex). For each chapter, list any *claim, method variant, or empirical statement* not present in the cited paper section. Do NOT verify numbers or citations (already done). Return JSON `{chapter: [<suspect_claims>]}`. Over-flag if unsure."

This is narrower than full verification and more reliable — single dimension (semantic scope), defined comparison range, told to over-flag.

## Hard-gate rule (autonomous AND interactive)

Phase 5 runs ONLY if (a) 4.A exit code is 0 AND (b) 4.B returns empty lists across all chapters.

On any block: write merged report to `~/vault/books/<slug>/PHASE-4-VERIFIER.md` with sections `## Missing citation keys`, `## Numeric drift`, `## Out-of-scope (self-cite)`, `## Out-of-scope (semantic)`, `## Accessibility — block tier`. Print 5-line summary. EXIT. User fixes chapters and re-invokes with `--resume-phase 4`.

On pass: write clean PHASE-4-VERIFIER.md and proceed to Phase 5.
