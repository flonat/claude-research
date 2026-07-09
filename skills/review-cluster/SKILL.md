---
name: review-cluster
description: "Use when you need a mid-draft adversarial review of a paper — runs paper-critic + domain-reviewer + claim-verify + blindspot in parallel, then auto-synthesises into a prioritised revision plan. Distinct from /pre-submission-report (final-gate kitchen sink, 13 sub-agents) — this is the active-drafting feedback loop. Triggers: 'review my draft', 'adversarial review', 'cluster review', 'mid-draft critique', 'feedback before pre-submission'."
allowed-tools: Read, Glob, Grep, Bash(uv*), Bash(ls*), Bash(git*), Task, Skill, AskUserQuestion
argument-hint: "[paper-path or no-args (auto-detect)] [--no-synthesise]"
---

# Review Cluster — Mid-Draft Adversarial Feedback

> Parallel fan-out of 4 read-only review agents on an active-drafting paper, with auto-synthesise downstream. Lighter than `/pre-submission-report --parallel` (4 agents vs 13); designed for tight iteration, not final-gate verification. Outputs `reviews/<scope>/review-cluster/YYYY-MM-DD-cluster-report.md` (scope = paper slug from the paper path).

## Output Path

Per `rules/review-artefact-routing.md` (auto-loads in research projects (path-scoped to `paper-*/` and `paper/`)):

- **Source slug:** `review-cluster`
- **Write reports to:** `reviews/<scope>/review-cluster/YYYY-MM-DD.md` (scope = paper slug) inside the project. Path is relative to the research project root, not the Task-Management repo.
- **Never** at project root (`./CRITIC-REPORT.md`-style filenames are forbidden — pre-rule layout).
- **Idempotency:** if today's file exists, append a same-day descriptor (`{date}-revision.md`, `{date}-r2.md`, `{date}-pre-submission.md`) — never overwrite.
- **Index update:** if `reviews/INDEX.md` exists, write a one-line entry under "Latest per source" pointing at the new file. Otherwise `/review-recap` will rebuild the index next time it runs.
- **Infrastructure repos** (Task-Management, atlas-workspace, etc.): this section does not apply — the path-scoped rule won't load there.


## Hard Rules

### Existential — block output

1. **All 4 sub-agents are read-only.** No git, no latexmk, no edits. See `subagent-write-guard.md`.
2. **Auto-synthesise via `/synthesise-reviews`** (unless `--no-synthesise`). Mid-draft work needs an actionable revision plan, not 4 raw reports.
3. **Skip if paper isn't compile-ready** — run `/latex` first; review on broken builds is misleading. The skill checks compile-status before dispatching.
4. **Cluster is for the user's own papers.** For external papers, use `peer-reviewer` agent instead.

### Format — catch in review

5. Single consolidated report at `reviews/<scope>/review-cluster/YYYY-MM-DD-cluster-report.md` (scope = paper slug) — not 4 separate files.
6. Findings tiered M/m/n (Major / moderate / minor) per `severity-gradient.md`.
7. Show which sub-agent flagged each finding (audit trail for traceability).

## When to Use

- Active drafting: paper compiles, content is taking shape, want adversarial feedback before final polish
- Mid-revision: addressed first round of supervisor comments; want fresh perspective before next pass
- Pre-pre-submission: ~2 weeks before submission, want to surface major issues with time to address
- Before sharing draft with co-authors

## When NOT to Use

- Paper is in final pre-submission state — use `/pre-submission-report --parallel` (13 sub-agents, full kitchen sink)
- Paper is in early scaffold (introduction only, no method/results) — review will flag everything as missing
- Reviewing someone else's paper — use `peer-reviewer` agent
- R&R revision response — use `/strategic-revision` instead (referee-comment-driven)

## Modes

| Invocation | Behaviour |
|---|---|
| `/review-cluster` | Full 4-agent fan-out + auto-synthesise |
| `/review-cluster <paper-path>` | Same, explicit paper |
| `/review-cluster --no-synthesise` | Run agents in parallel; show 4 raw reports without merging |

## Architecture

```
Phase 1 (preflight) → /latex compile check; abort if broken
Phase 2 (dispatch)  → 4 read-only sub-agents in parallel via Task tool
Phase 3 (math)      → IF theory paper: /verify-math on the model section(s) [orchestrator-run skill]
Phase 4 (consolidate) → /synthesise-reviews merges (incl. math verdict) → revision plan
Phase 5 (report)    → reviews/<scope>/review-cluster/YYYY-MM-DD-cluster-report.md
```

## The 4 sub-agents

| # | Agent | Why this lens |
|---|---|---|
| 1 | **paper-critic** (specialist mode if venue known) | General adversarial — structural issues, argument quality, contribution clarity. Most-cited reviewer in the family. |
| 2 | **domain-reviewer** | Math derivations, assumption completeness, citation fidelity at the substantive level, code-theory alignment. Catches what paper-critic doesn't have the lens for. |
| 3 | **claim-verify** | Citation fidelity at the per-claim level — does what's written about Smith (2024) actually match Smith (2024)? Distinct from bib-validate (existence) and paper-critic (structure). |
| 4 | **blindspot** | Peripheral-vision audit — vices in plain sight + virtues being overlooked. Distinct from adversarial review because it surfaces *missed opportunities*, not just *things to fix*. |

Why these four (and not more):
- **referee2-reviewer** is excluded — it's the *final-stage* hostile review, used in `/pre-submission-report`. Mid-draft, hostile review pre-empts genuine improvement.
- **artifact-coherence-auditor / reproducibility-auditor** are excluded — relevant only when the paper is paired with a replication artifact, which is typically a pre-submission concern.
- **code-paper-auditor** is excluded — a separate `/code-suite` skill exists for code-side review.
- **proofread** is excluded — editorial issues are too noisy mid-draft; deferred to pre-submission.

## Phase 1: Pre-flight

```bash
# Auto-detect paper or use arg
PAPER_PATH="${1:-$(ls -d paper-*/paper 2>/dev/null | head -1)}"
[ -z "$PAPER_PATH" ] && echo "No paper-*/ directory found" && exit 1

# Check compile-readiness — exit if last latex run failed
LATEST_PDF=$(find "$PAPER_PATH/out" -name "*.pdf" -newer "$PAPER_PATH/main.tex" 2>/dev/null | head -1)
if [ -z "$LATEST_PDF" ]; then
    echo "Paper not compiled or stale. Run /latex first."
    # AskUserQuestion: run /latex now, or proceed anyway (risky)?
fi
```

## Phase 2: Dispatch

Launch all 4 in a single message with parallel Task tool calls (the standard pattern from system-audit / pre-submission-report). Each gets:

- **Read-only with respect to project files under review** — Read, Glob, Grep, Bash (read-only commands only) against the paper / code being reviewed; the agent does NOT modify any project source files
- **The standard forbid-list** from `subagent-write-guard.md`
- **Paper path** explicitly named
- **Output target — two-step, both required:**
  1. **Write the per-agent report** to `reviews/<scope>/<source-slug>/<YYYY-MM-DD-HHMM>.md` (scope = paper slug, source-slug = agent name like paper-critic; run `mkdir -p reviews/<scope>/<source-slug>/` first) per the agent's own "Log to REVIEW-STATE.md (final step)" instruction. The agent's logging step appends a row to `reviews/INDEX.md` (or legacy `REVIEW-STATE.md`) via the shared helper — this is the durable record + stamp that `/review-recap` reads.
  2. **Return a structured findings summary** to the orchestrator for the Phase 4 consolidate step.

  These two outputs are NOT mutually exclusive. The file under `reviews/<source-slug>/` is the durable artefact and triggers the row stamp; the structured return value is the orchestrator's working copy for consolidation. Earlier wording — "not a file write" — was wrong: it suppressed the per-agent logging step and resulted in 0–1 of 4 cluster dispatches stamping a row in INDEX.md. The 2026-05-17 5-agent patch (commit `23ebcfff`) made the agent-side intro unconditional; this dispatch-side fix is the orchestrator-side complement.

Wait for all 4. Do not start Phase 4 (consolidate) until all return.

## Phase 3: Math verification (theory papers only)

The 4-agent fan-out covers the **conceptual** math layer (via `domain-reviewer`, rung R0) but does **not** run the computational verification rungs. For a theory paper, add a `/verify-math` pass so the algebra/analytic claims are machine-checked, not just read.

**Detect a theory paper** (any of):
```bash
grep -lE '\\begin\{(theorem|proposition|lemma|corollary)\}' "$PAPER_PATH"/**/*.tex 2>/dev/null
```
If there are no formal environments, skip this phase entirely.

If it IS a theory paper, invoke `/verify-math` (via the Skill tool) scoped to the section(s) holding the model — it decomposes each proposition into atomic obligations and routes them across the spectrum (R0 conceptual · R1 numerical falsification · R2 symbolic/CAS · R3 Lean). `/verify-math` is a **skill**, run by this orchestrator in the main session — this is deliberate: the computational rungs (`/numerical-check`, `/symbolic-check`, `/lean-check`) need Bash + sympy/lean, which sub-agents cannot reliably obtain at runtime (the same Bash-grant fragility documented below). The orchestrator always has Bash, so the rungs run here, not inside an agent.

`/verify-math` writes its own aggregate report to `reviews/<scope>/verify-math/<YYYY-MM-DD-HHMM>.md` and stamps its own INDEX.md row (it is a self-stamping skill, like `/proofread`). Fold its aggregate verdict — and any `FALSIFIED` obligation — into the Phase 4 synthesis as a high-confidence finding (a machine-falsified claim outranks any single reviewer's concern).

**Avoid double-work:** `domain-reviewer` (agent #2) and `/verify-math`'s R0 rung both cover the conceptual layer. When this phase runs, tell `domain-reviewer` in its dispatch prompt that the algebraic identities and comparative-static signs are being machine-verified separately, so it should focus on the conceptual obligations (assumption completeness, citation fidelity, backward logic) rather than re-deriving algebra — see the domain-reviewer "Math R0 Mode" preset.

## Phase 4: Consolidate

If `--no-synthesise`: stop here, show 4 raw reports.

Otherwise, invoke `/synthesise-reviews` with the 4 reports as input. Output is a prioritised revision plan with:
- Cross-reviewer agreement (claims raised by ≥2 reviewers — high confidence)
- Single-reviewer claims (medium confidence)
- Blindspot virtues (opportunities, not problems — sometimes the most valuable finding)
- Recommended action queue with priority + estimated effort

## Phase 5: Report

Save to `reviews/<scope>/review-cluster/YYYY-MM-DD-cluster-report.md` (scope = paper slug):

```markdown
# Review Cluster Report — YYYY-MM-DD

**Paper:** <path>
**Compile status:** <PASS / WARN / FAIL>
**Reviewers:** paper-critic, domain-reviewer, claim-verify, blindspot

## Summary
- Major issues (M-tier): N
- Moderate (m-tier): N
- Minor (n-tier): N
- Blindspot virtues (opportunities): N

## Cross-reviewer agreement (high confidence)
| Issue | Severity | Flagged by |
|---|---|---|
| ... | M | paper-critic, domain-reviewer |

## Single-reviewer claims (medium confidence)
[Table by severity]

## Blindspot — virtues + missed opportunities
[Items from #4 sub-agent]

## Recommended action queue
1. [Highest-priority]
2. ...
```

## Cross-References

| Skill / Agent / Rule | Relationship |
|---|---|
| `/pre-submission-report --parallel` | Final-gate kitchen sink (13 agents) — this skill is the mid-draft analogue (4 agents) |
| `/synthesise-reviews` | The merge step this skill invokes |
| `/strategic-revision` | After this skill produces a revision plan, optionally hand off to /strategic-revision for DAG-validated execution |
| `paper-critic`, `domain-reviewer`, `claim-verify`, `blindspot` agents | The 4 sub-agents this skill orchestrates |
| `/verify-math` | Phase 3 node for theory papers — machine-verifies the math (R1/R2/R3 rungs the agents can't run); self-stamps its own report |
| `/code-suite` | Code-side counterpart for projects with code |
| `subagent-write-guard.md` | Sub-agents follow this rule (read-only forbid-list) |
| `/proofread` | Editorial polish — run AFTER cluster review, before pre-submission-report |

## REVIEW-STATE.md propagation (orchestrator-side stamping)

This skill is an **orchestrator** in the REVIEW-STATE.md schema. As of the 2026-05-19 architecture change, the orchestrator (this skill) handles all stamping; sub-agents emit directives but do not call the helper themselves. Each of the 4 sub-agents (paper-critic, domain-reviewer, claim-verify, blindspot) ends its final response with a `review-state-stamp` fenced block (see `skills/_shared/stamp-directive-spec.md`).

### Required orchestrator behaviour

When constructing the prompts for the 4 parallel sub-agents, include this line in each:

> Emit a `review-state-stamp` directive at the end of your final response per `skills/_shared/stamp-directive-spec.md`. Set `trigger: review-cluster` (or omit — this orchestrator overrides). Do not call the stamping helper yourself.

### After all 4 sub-agents return

For each sub-agent's return:

1. Write the agent's final response to a temp file (`/tmp/review-cluster-<agent>.md`).
2. Parse the directive:
   ```bash
   ARGS=$(bash ~/.claude/skills/_shared/parse-stamp-directive.sh /tmp/review-cluster-<agent>.md)
   ```
   If `parse-stamp-directive.sh` exits non-zero, log a warning ("Agent X return did not contain a review-state-stamp directive") and continue with the next agent — best-effort.
3. **Verify the `.md` report file exists; reconstruct from return content if missing:**
   ```bash
   VERIFY=$(bash ~/.claude/skills/_shared/post-dispatch-verify.sh \
       --return-file /tmp/review-cluster-<agent>.md \
       --project "$PROJECT_ROOT" \
       --agent <agent>)
   # $VERIFY is 'OK <path>' or 'RECONSTRUCTED <path>'.
   # Exit code 10 means reconstruction happened — append a marker to the notes
   # so /review-recap shows this row was a recovery, not a real run.
   ```
   If `VERIFY` starts with `RECONSTRUCTED`, append `(report reconstructed by orchestrator — agent skipped Write)` to the `--notes` value before stamping. This guards against the blindspot-class failure mode (agent claims to write but skips the call). See `log/2026-05-21-blindspot-write-fix.md`.
4. Stamp with the orchestrator's `--trigger` override (overriding whatever the agent emitted):
   ```bash
   eval bash ~/.claude/skills/_shared/review-state-log.sh "$ARGS" \
       --trigger review-cluster \
       --source agent \
       --project "$PROJECT_ROOT"
   ```
5. Clean up the temp file.

All 4 stamps land in `<project>/reviews/INDEX.md` with the same orchestrator name and roughly the same `Last Run` timestamp, making the cluster visible at a glance.

### Why the orchestrator stamps (not the sub-agent)

Agents have inconsistent Bash tool grants at runtime (the 2026-05-19 harness investigation showed paper-critic and domain-reviewer self-report Bash unavailable despite YAML grants). The orchestrator always has Bash and always runs after the agents return. Moving stamping here decouples it from agent tool-surface uncertainty.

Schema: `~/Task-Management/docs/reference/review-state-schema.md`.
Stamp directive format: `~/Task-Management/skills/_shared/stamp-directive-spec.md`.

## Anti-Patterns

- **Don't** include `referee2-reviewer` in the cluster — that's the final-stage hostile review, not mid-draft.
- **Don't** run cluster review on a broken build — phase-1 check should abort.
- **Don't** auto-apply fixes from the synthesised report — the report is read-only output. User reviews and dispatches edit-agents (per `subagent-write-guard.md`) separately.
- **Don't** run cluster review on every save — designed for milestone-driven iteration, not continuous integration.
