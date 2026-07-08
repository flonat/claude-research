# Release-Readiness Checklist (Pass/Fail Deliverable)

> Produced at **Phase 7 (Report)** as a per-item PASS/FAIL block, in addition to the summary report
> (`report-template.md`). Adapted from Yusaku Horiuchi's `release-readiness-report.md`. The point is a
> *checkable* gate: each line is PASS / FAIL / N/A, and **any FAIL is a release blocker** until fixed or
> explicitly waived (record the waiver reason). Emit this to `<output>/RELEASE-READINESS.md`.

```markdown
# Replication Package — Release Readiness

- Project:            <paper slug>
- Date checked:       <YYYY-MM-DD>
- Agent/model:        <model>
- Public package:     <output path>
- Structure:          compact | build-analyze | other
- Paper source:       available & checked | used-not-archived | unavailable
- Target archive:     <journal / OSF / Dataverse / Zenodo / anon.4open.science>

## 14-point pre-release checklist
1.  [ ] Runs from a **fresh session/interpreter** (no reliance on in-memory objects).
2.  [ ] **Relative paths only** — no absolute paths, no machine-specific/user paths (grep for `/Users/`, `/home/`, `C:\`, `setwd(`).
3.  [ ] **One log per public script** present in `logs/` (or `build/`+`analyze/` logs).
4.  [ ] **`session_info.log`** present, from a real successful full run (language version, platform, OS, packages, elapsed).
5.  [ ] **Master script** runs every script in order and regenerates all outputs cleanly (exit 0, no errors).
6.  [ ] **README section order** matches the AEA template + the figure/table crosswalk is appended.
7.  [ ] **Folder tree in the README matches** the actual package (no stale/renamed dirs).
8.  [ ] **Every manuscript figure/table** appears in the crosswalk; **every appendix** figure/table too.
9.  [ ] Every crosswalk entry has all five fields (Output · Script · Log · **LaTeX Label** · Notes); conceptual/hand-made items explicitly marked.
10. [ ] **Every in-text number traces** to a script/log/generated output (run `code-paper-auditor` if a `.tex` is present).
11. [ ] **Data sources documented**; restricted/non-redistributable sources have restriction reason + public replacement + rebuild path + reproducibility limits.
12. [ ] **Stable filenames** (no timestamps/PIDs/random suffixes in output names); outputs are deterministic (seeds set).
13. [ ] **No AI/authoring traces** (`.claude/`, `CLAUDE.md`, `.context/`, `log/`, agent trailers in git log) — Phase 3 scrub verified.
14. [ ] **Opens & runs elsewhere** — a `.gitignore` (and, if Dropbox-synced, `rules.dropboxignore`) is present; the fresh git repo has clean history.

## Verdict
- Status: **READY** | READY-WITH-CAVEATS | NOT-READY
- Blockers (FAIL items): <list, or none>
- Waived (with reason): <list, or none>
- Public entry point: `source("master.R")` / `python master.py` / `do master.do`
- Last verified: <YYYY-MM-DD> by running the master script from the package root.
```

**Blind mode:** items 2, 13, and the "no author identity" checks compound with the anonymity gate in
`blind-workflow.md` — run both; the anonymity A2 gate stays authoritative for identity leaks.
