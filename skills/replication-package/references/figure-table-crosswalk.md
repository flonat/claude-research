# Figure/Table Crosswalk + Paper-Consistency Check

> Append this to the generated README (after the AEA-style body from `aea-readme-template.md`).
> Adapted from Yusaku Horiuchi's replication-package-guide — the AEA template documents *programs*
> but does **not** map every manuscript figure/table to its exact output/script/log/label. This
> closes that gap and adds the traceability check that catches paper↔output drift before release.

## Crosswalk — one entry per manuscript & appendix figure/table

Every figure and table cited in the paper **or** appendix appears below, in **paper order**. Use one
`####` entry per individual figure/table number — even when several are produced by the same script.
Five fields, in this fixed order (omit none; write "Not applicable" where a field is empty):

- **Output** — the generated file path(s) (e.g. `output/figures/fig2.pdf`), or "No output file" for a conceptual/hand-made item.
- **Script** — the script that produces it (e.g. `code/03_make_figures.R`), or "No code".
- **Log** — the per-script log (e.g. `logs/03_make_figures.log`), or "Not applicable".
- **LaTeX Label** — the `\label{}` used in the manuscript (e.g. `fig:main-effect`, `tab:balance`). This is the join key between paper and package.
- **Notes** — one line (e.g. "conceptual figure", "publication table hand-edited from generated CSV — see Notes").

```markdown
## Figure/Table Crosswalk

### Manuscript

#### Figure 1
- Output: No output file.
- Script: No code.
- Log: Not applicable.
- LaTeX Label: `fig:framework`
- Notes: conceptual figure (drawn in TikZ, not replicated).

#### Table 2
- Output: `output/tables/balance.tex`
- Script: `code/02_balance.R`
- Log: `logs/02_balance.log`
- LaTeX Label: `tab:balance`
- Notes: —

### Appendix

#### Table A.1
- Output: `output/tables/robustness.tex`
- Script: `code/04_robustness.py`
- Log: `logs/04_robustness.log`
- LaTeX Label: `tab:robustness`
- Notes: —
```

## Paper Source And Consistency Checks

State whether the paper source (`.tex`) was available during preparation, and — if the paper is on
Overleaf synced through Dropbox — whether the package was prepared **inside or alongside** the synced
Overleaf folder (keep the replication package a *sibling* of, not nested inside, the Overleaf folder,
so a Dropbox sync never ships build artefacts into the manuscript project).

Record the paper-source status (pick one):
- Paper source available and checked against the replication outputs.
- Paper source used during preparation but not included in the public archive.
- Paper source not available for this package.

When the `.tex` **is** available, run the consistency check and record the result:

1. **Coverage** — every figure/table `\label{}`/`\ref{}`/`\includegraphics`/`\input` in the paper + appendix has a crosswalk entry (grep the `.tex` for `\label`, `\includegraphics`, `\input{.*table}`).
2. **Path match** — every `\includegraphics`/`\input` path in the paper points at the corresponding replicated output.
3. **Hand-edited outputs** — any publication table manually edited after generation is flagged in its Notes (the generated file, script, and log still recorded).
4. **In-text numbers trace** — every in-text estimate, SE, p-value, sample size, response rate, date, and descriptive statistic traces to a script/log/generated table/figure (this is the same discipline as `paper-code-consistency.md` and the `code-paper-auditor` agent — reuse them).
5. **Non-replicated items marked** — conceptual figures, hand-made tables, and externally-sourced items are explicitly identified.

Report as PASS/FAIL per check in the release-readiness deliverable (`release-readiness-checklist.md`).
Any FAIL is a release blocker until resolved or explicitly waived.
