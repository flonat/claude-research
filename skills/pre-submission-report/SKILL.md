---
name: pre-submission-report
description: "Use when you need all quality checks run before submission, producing a single dated report."
allowed-tools: Bash(latexmk*, mkdir*, ls*, wc*), Read, Write, Edit, Glob, Grep, Task, Skill
argument-hint: "[path/to/main.tex or no arguments to auto-detect]"
agent-dependencies: [artifact-coherence-auditor, blindspot, claim-verify, code-paper-auditor, domain-reviewer, paper-critic, referee2-reviewer, reproducibility-auditor]
skill-dependencies: [ai-detect, bib-validate, latex, verify-math]
---

# Pre-Submission Report

> Aggregates all quality checks into one dated report. Run before submitting to a journal/conference or sharing with collaborators.

## Output Path

Per `rules/review-artefact-routing.md` (auto-loads in research projects (path-scoped to `paper-*/` and `paper/`)):

- **Source slug:** `pre-submission-report`
- **Write reports to:** `reviews/<paper-slug>/pre-submission-report/<YYYY-MM-DD-HHMM>.md` inside the project, where `<paper-slug>` is the paper directory name being reviewed (e.g., `paper-jtp` if reviewing `paper-jtp/main.tex`). Path is relative to the research project root, not the Task-Management repo.
- **Never** at project root (`./CRITIC-REPORT.md`-style filenames are forbidden — pre-rule layout).
- **Idempotency:** if the minute-based timestamp file exists, append a same-run descriptor (`{timestamp}-r2.md`, `{timestamp}-revision.md`) — never overwrite.
- **Index update:** if `reviews/INDEX.md` exists, write a one-line entry under "Latest per source" pointing at the new file. Otherwise `review-recap` will rebuild the index next time it runs.
- **Infrastructure repos** (Task-Management, atlas-workspace, etc.): this section does not apply — the path-scoped rule won't load there.


## When to Use

- Before submitting a paper to a venue
- Before sharing a draft with supervisors or co-authors
- When the user says "pre-submission check", "is this ready?", "run everything"

## Input

- A `.tex` file path, or auto-detect `paper/main.tex` in the current project

## Critical Rule

**Python:** Always use `uv run python` or `uv pip install`. Never bare `python`, `python3`, `pip`, or `pip3`. Include this in any sub-agent prompts.

## Steps

### 1. Locate the Paper

If no argument provided, search for the main `.tex` file:
1. Check `paper/main.tex`
2. Check `paper/*.tex` for a file containing `\begin{document}`
3. Ask the user if ambiguous

### 2. Integrity Gate (hard gate — must pass before quality checks)

Run these checks first. If any fail, stop and report — do not proceed to quality checks.

1. **Placeholder scan** — grep the `.tex` file(s) for `TODO`, `FIXME`, `XXX`, `TBD`, `[INSERT`, `PLACEHOLDER`, `Lorem ipsum`. Any match is a FAIL.
2. **Citation integrity** — invoke `bib-validate` in verify mode. Every `\cite{}` key must resolve to a `.bib` entry. Any missing key is a FAIL.
3. **Section completeness** — check that all standard sections exist and are non-empty (Abstract, Introduction, and at least one body section before Conclusion/References). An empty or missing section is a FAIL.
4. **Broken references** — grep for `??` in the compiled PDF output or `.log` file (undefined `\ref{}` or `\cite{}`). Any `??` in output is a FAIL.
5. **Anonymity gate (only if the venue is double-blind)** — load `_shared/double-blind-anonymity-checklist.md` and run **all** P1–P8 paper-side checks. Any FAIL is a hard stop. In particular: P4 (self-citation bib must be blinded if cited paper's author list overlaps the submission's) and P5 (body text must not name authors of self-cited works) — these are the CCS 2026 #1328 desk-reject triggers and require the submission's author list to be loaded from the vault submission frontmatter or prompted from the user. If the artifact has been minted via `anonymous-artifact`, also confirm A1–A9 ran clean for that artifact (state file at `<project>/.anonymous-artifact-state.json`). Skip this entire step only when the user explicitly says "single-blind" or "non-blind".

**If any check fails:**
```
INTEGRITY GATE: FAIL

Blockers (must fix before quality checks):
  - [ ] 3 TODO placeholders found (lines 47, 112, 289)
  - [ ] 2 undefined references (\ref{fig:missing}, \cite{nonexistent2024})
  - [ ] Abstract section is empty

Fix these and re-run pre-submission-report.
```

**If all pass:** proceed to Step 3.

### 3. Run Quality Checks

Two modes:

#### 3a. Sequential (default — fast, deterministic)

Run these in order — each depends on a clean state from the previous:

1. **Compilation** — invoke `latex` on the main `.tex` file. Record pass/fail and any remaining warnings.
2. **Citation audit** — invoke `bib-validate --verify-doi` (DOI resolution mode catches fabricated entries). Record missing, unused, suspect, and unresolved-DOI keys.
3. **Adversarial review** — launch `paper-critic` agent (via fresh-context sub-agent mechanism). Capture the CRITIC-REPORT.md score and findings.

#### 3b. Parallel 7-audit fan-out (`--parallel` flag)

Use when (a) the paper is near submission and you want a comprehensive scan, or (b) the user explicitly asks for the "full pre-submission swarm". Dispatches **7 read-only sub-agents in parallel** via the fresh-context sub-agent mechanism, then consolidates findings.

**Hard rules for parallel mode:**
1. **All sub-agents are read-only with respect to project files under review** — see `subagent-write-guard.md` rule. They do NOT modify the paper, bib, code, or any other artefact under review; the orchestrator (this skill) decides what to fix. **They DO write their own per-agent reports** to `reviews/<paper-slug>/<check>/<YYYY-MM-DD-HHMM>.md` per each agent's "Log to REVIEW-STATE.md (final step)" instruction (where `<paper-slug>` is the paper being reviewed and `<check>` is the agent name, e.g., `paper-critic`, `referee2-reviewer`) — this is the durable record + the INDEX.md stamp that `review-recap` reads. The "read-only" scope is the artefact under review, NOT a prohibition on writing the review report itself.
2. **Each sub-agent gets the standard forbid-list** — no git, no latexmk, no edits to files outside their scope. The forbid-list explicitly carves out the `reviews/<paper-slug>/<check>/` path as a permitted write target (the agent's logging step needs it), where `<paper-slug>` is the paper being reviewed (passed in the dispatch) and `<check>` is the agent name.
3. **Findings consolidate into a P0/P1/P2 fix list** before any edits — single triage point, not 13 streams. Sub-agents return structured findings to the orchestrator in addition to writing their report file; the consolidate step uses the structured returns.
4. **No edit phase auto-runs** — the user reviews the consolidated report and approves which fixes to apply.
5. **Evidence contract + spot-verify** (per [`_shared/audit-integrity.md`](../_shared/audit-integrity.md) Rule 2). Each sub-agent's dispatch prompt MUST require **every finding to cite `path:line` (or `§`) AND quote the exact text/code verbatim** — unanchored findings are inadmissible. Before consolidating (rule 3), the orchestrator **spot-verifies a random sample** of returned findings (≥3, or 20%, weighted to P0/P1): open the cited location, confirm the quote is there and the claim follows. Any miss ⇒ widen to that agent's full set and **drop** what can't be grounded. Record `Integrity: N sampled, M dropped` in the consolidated report.

**The 7 sub-agents:**

**Always dispatched (13 sub-agents):**

| # | Agent | Scope | Output |
|---|---|---|---|
| 1 | **bib-verifier** | DOI resolution + Crossref/S2 verification of every bib entry via `bib-validate --verify-doi` mode; flag fabricated/unresolvable | List of unverified keys + suggested fixes |
| 2 | **claim-verifier** | Launch `claim-verify` agent — checks every cited claim against the source paper (citation fidelity, not just key existence) | Per-claim verdicts |
| 3 | **novelty-reviewer** | Run `scholarly scholarly-search "<paper title>" --source openalex`; report score + threats not yet cited | Novelty score + missing-related-work list |
| 4 | **paper-critic** | Launch `paper-critic` agent — general adversarial CRITIC-REPORT (specialist mode for venue-calibrated review) | Scored CRITIC-REPORT.md |
| 5 | **domain-reviewer** | Launch `domain-reviewer` agent — math/derivations/assumptions/code-theory alignment | DOMAIN-REVIEW.md |
| 6 | **referee2-reviewer** | Launch `referee2-reviewer` agent — Reviewer 2 hostile read; top reviewer-attack-surface concerns | Adversarial concerns |
| 7 | **blindspot** | Launch `blindspot` agent — peripheral-vision audit (vices in plain sight + virtues being overlooked) | Blindspot report |
| 8 | **code-paper-auditor** | Launch `code-paper-auditor` agent — cross-check quantitative claims against source code outputs | Mismatch table |
| 9 | **artifact-coherence-auditor** | Launch `artifact-coherence-auditor` agent — paper prose vs replication outputs (catches hallucinated results) | Coherence report |
| 10 | **reproducibility-auditor** | Launch `reproducibility-auditor` agent — workflow rerunnability (hidden deps, absolute paths, env assumptions) | Reproducibility report |
| 11 | **anonymity / double-blind checker** | Apply paper-side checks P1-P8 from `_shared/double-blind-anonymity-checklist.md`; verify `[review]` mode if double-blind venue | Pass/fail + leak list |
| 12 | **page-limit + LaTeX validator** | Verify page count under venue limit; check for compile warnings; check `out/` is current | Page count + warning summary |

**Conditional — math verification (theory papers):**

If the paper contains formal environments (`grep -lE '\\begin\{(theorem|proposition|lemma|corollary)\}'` matches), run `verify-math` (via the skill-routing mechanism) on the model section(s) **in addition to** the domain-reviewer agent (#5). The two are complementary, not redundant: domain-reviewer (#5) reads the conceptual layer (rung R0), while `verify-math` machine-checks the algebra/analytics across the rest of the spectrum (R1 numerical falsification · R2 symbolic/CAS · R3 Lean). This runs as an **orchestrator skill, not a sub-agent** — the computational rungs need Bash + sympy/lean, which sub-agents can't reliably get at runtime (same Bash-grant fragility that motivates orchestrator-side stamping below); the orchestrator always has Bash. It is read-only with respect to project files (writes only its own report) and self-stamps its INDEX.md row. Fold its aggregate verdict into consolidation: **any `FALSIFIED` obligation is a P0 blocker** (a machine-falsified theorem outranks any reviewer concern); an `INCONCLUSIVE` obligation is P1. When both run, tell domain-reviewer (#5) in its prompt that the algebra is being verified separately so it focuses on assumption completeness / citation fidelity / backward logic — see the domain-reviewer "Math R0 Mode" preset.

**Conditional follow-ups (run after parallel fan-out, opt-in):**

| Trigger | Skill |
|---|---|
| Paper has code (detect: non-tex/non-bib files in project) AND venue is double-blind | `anonymous-artifact` — assemble + sanitize + push to anonymous repo, mint URL |
| Strategic-revision context (paper has referee comments) | `strategic-revision` — revision plan after the swarm flags issues |

The conditional follow-ups are NOT in the parallel batch — they're sequential because they may modify files (and so violate the read-only invariant of the parallel sub-agents).

**Dispatch protocol:**

```python
# Pseudocode for orchestration — see fresh-context sub-agent mechanism docs for actual API
parallel_tasks = [
    Agent("bib-verifier", subagent_type="general-purpose",
          prompt=f"Read {paper_path}/references.bib. Run scholarly scholarly-verify-dois on all DOI-bearing entries (batch ≤50). Report unresolvable DOIs, missing DOIs, suspected fabricated entries. READ-ONLY. {forbid_list}"),
    Agent("novelty-reviewer", ...),
    # ... 5 more
]
# Wait all → consolidate
findings = consolidate_p0_p1_p2(parallel_tasks)
```

Sub-agents run concurrently — total wall-clock is bounded by the slowest (typically novelty-reviewer at ~2-3 min via OpenAlex).

**Consolidation:** the orchestrator merges findings from all 13 sub-agents into a single P0/P1/P2 fix list:
- **P0 (block submission):** anonymity leaks (#11), fabricated citations (#1, #2), compilation errors (#12), over-page-limit (#12), code-paper mismatches (#8), prose-replication divergence (#9), **any `FALSIFIED` math obligation (`verify-math`, theory papers)**
- **P1 (must fix):** unresolved DOIs (#1), claim-verify failures (#2), novelty threats (#3), critic-report Major issues (#4), domain-review math errors (#5), reproducibility issues (#10), referee2-reviewer concerns (#6), **`INCONCLUSIVE` math obligations (`verify-math`)**
- **P2 (should consider):** blindspot virtues + minor vices (#7), AI-detect hot zones (#13), critic-report Moderate/Minor issues (#4), novelty positioning (#3)

**Code-bearing detection:** if the project has non-tex / non-bib files outside `paper-*/` and `notes/` (typical signal: `code/`, `data/`, `scripts/`, `analysis/`, `src/` directories), enable code-side sub-agents (#8 code-paper-auditor, #9 artifact-coherence-auditor, #10 reproducibility-auditor) and queue `anonymous-artifact` as a conditional follow-up.

**Edit phase (separate, opt-in):** if the user approves any P0/P1 fixes, dispatch a *second* round of edit-agents with **explicit scoped permissions per file** — see `subagent-write-guard.md` for the forbid-list pattern. The orchestrator confirms each edit-agent's scope before dispatch.

**Why parallel:** the 13 audits are independent — sequential is ~10x slower for the same coverage. Reviewer-pool collision risk is zero (read-only sub-agents).

**Skip parallel mode if:** paper is in early drafting (use the sequential 3-audit instead — faster feedback for incomplete drafts), or sub-agents fail repeatedly (fall back to sequential).

### 4. Aggregate Report

Save to `log/audits/quality-reports/YYYY-MM-DD_<project-name>.md`:

```markdown
# Pre-Submission Quality Report

**Project:** <project name>
**Date:** YYYY-MM-DD
**File:** <path to main.tex>
**Target:** <venue from project CLAUDE.md, or "not specified">

---

## Integrity Gate: PASS / FAIL

- **Placeholders:** 0 found
- **Citation integrity:** all keys resolved
- **Section completeness:** all sections present
- **Broken references:** none

---

## Overall Score: XX/100 — [Verdict]

Verdict uses the quality scoring framework:
- 90-100: Publication-ready
- 80-89: Minor revisions needed
- 70-79: Significant revisions needed
- Below 70: Not ready

---

## Compilation

- **Status:** PASS / FAIL
- **Warnings:** <count>
- **Details:** <brief summary of any issues>

## Citations

- **Missing keys:** <count> — <list>
- **Unused keys:** <count> — <list>
- **Suspect entries:** <count> — <list>

## Adversarial Review

- **Score:** XX/100
- **Key findings:**
  - <finding 1>
  - <finding 2>
  - ...

## Research Quality Score

Load `skills/shared/research-quality-rubric.md` and report the weighted aggregate (X.X / 5.0) with verdict.

## Remaining Issues

| # | Severity | Category | Issue |
|---|----------|----------|-------|
| 1 | High/Medium/Low | Compilation/Citation/Content | <description> |

## Recommendation

**[Submit / Revise / Not ready]**

<1-2 sentence summary of what needs to happen before submission>
```

### 5. Present Summary

Display the report path and the summary table to the user. If the recommendation is "Submit", congratulate. If "Revise", list the top 3 issues to fix first.

## Error Handling

- If compilation fails after `latex`, still run the remaining checks. Mark compilation as FAIL in the report.
- If `paper-critic` agent fails, note it in the report and base the overall score on compilation + citations only.
- Always produce the report file, even if some checks failed.

## Integration

| Skill/Agent | Role in this workflow |
|-------------|---------------------|
| `latex` | Compilation + auto-fix |
| `bib-validate` | Citation cross-reference + self-citation deanonymization scan |
| `paper-critic` agent | Adversarial content review |
| `quality-scoring.md` | Verdict thresholds |
| `_shared/double-blind-anonymity-checklist.md` | P1–P8 / A1–A9 anonymity gate (double-blind venues only) |
| `_shared/audit-integrity.md` | Fan-out integrity contract — each of the 13 review agents must cite `path:line` + verbatim evidence (Rule 2); the orchestrator spot-verifies before including a finding in the report |

## REVIEW-STATE.md propagation (orchestrator-side stamping)

This skill is an **orchestrator** in the REVIEW-STATE.md schema. As of the 2026-05-19 architecture change, the orchestrator handles all stamping; sub-agents emit directives but do not call the helper themselves.

### Required orchestrator behaviour

When constructing prompts for any sub-agent that is a logging tool (paper-critic, referee2-reviewer, peer-reviewer, domain-reviewer, claim-verify, blindspot, fatal-error-check, code-paper-auditor, artifact-coherence-auditor, reproducibility-auditor, code-review), include this line in the sub-agent prompt:

> Emit a `review-state-stamp` directive at the end of your final response per the installed shared resource `_shared/stamp-directive-spec.md`. Set `trigger: pre-submission-report` (or omit — this orchestrator overrides). Do not call the stamping helper yourself.


### After each sub-agent returns

For each agent's return:

1. Write the agent's final response to a temp file (`/tmp/pre-submission-<agent>.md`).
2. Parse the directive:
   ```bash
   ARGS=$(bash <skills-root>/_shared/parse-stamp-directive.sh /tmp/pre-submission-<agent>.md)
   ```
   If `parse-stamp-directive.sh` exits non-zero, log a warning ("Agent X return did not contain a review-state-stamp directive — INDEX.md not updated for this run") and continue.
3. **Verify the `.md` report file exists; reconstruct from return content if missing:**
   ```bash
   VERIFY=$(bash <skills-root>/_shared/post-dispatch-verify.sh \
       --return-file /tmp/pre-submission-<agent>.md \
       --project "$PROJECT_ROOT" \
       --agent <agent>)
   ```
   If `VERIFY` starts with `RECONSTRUCTED`, append `(report reconstructed by orchestrator — agent skipped Write)` to the `--notes` value before stamping. Guards against the blindspot-class failure mode. See `log/2026-05-21-blindspot-write-fix.md`.
4. Stamp with the orchestrator's `--trigger` override:
   ```bash
   eval bash <skills-root>/_shared/review-state-log.sh "$ARGS" \
       --trigger pre-submission-report \
       --source agent \
       --project "$PROJECT_ROOT"
   ```
5. Clean up the temp file.

All sub-agent stamps land in `<project>/reviews/INDEX.md` with `Trigger=pre-submission-report` and roughly the same `Last Run` timestamp.

### Why the orchestrator stamps (not the sub-agent)

Agents have inconsistent Bash tool grants at runtime (the 2026-05-19 harness investigation). The orchestrator always has Bash and always runs after the agents return. Moving stamping here decouples it from agent tool-surface uncertainty and fixes the burying problem (referee2-reviewer's stamping section used to live at line ~475 of a 518-line agent definition; agents reliably forgot to reach it).

Schema: the installed shared resource `shared/review-state-schema.md`.
Stamp directive format: the installed shared resource `_shared/stamp-directive-spec.md`.
