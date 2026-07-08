---
name: replication-audit
description: "Use when you need to audit which findings in a literature have been replicated or failed."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv*), Bash(python*), Task, WebSearch, WebFetch, Bash(paperpile*)
argument-hint: "[topic, .bib file, or paper directory]"
---

# Replication Audit

> Examine which findings in a literature have been replicated, failed to replicate, or never been tested. Flag papers that build on non-replicated foundations.

Don't build your dissertation on a foundation made of sand.

## Output Path

Per `rules/review-artefact-routing.md` (auto-loads in research projects (path-scoped to `paper-*/` and `paper/`)):

- **Source slug:** `replication-audit`
- **Write reports to:** `reviews/<scope>/replication-audit/<YYYY-MM-DD-HHMM>.md` inside the project, where `<scope>` is the paper slug (e.g., `paper-jtp`) for paper-level reviews or `_project` for project-level reviews. Path is relative to the research project root, not the Task-Management repo.
- **Never** at project root (`./CRITIC-REPORT.md`-style filenames are forbidden — pre-rule layout).
- **Idempotency:** if the run timestamp already exists, append a same-run descriptor (`{timestamp}-revision.md`, `{timestamp}-r2.md`) — never overwrite the same `<YYYY-MM-DD-HHMM>` path.
- **Index update:** if `reviews/INDEX.md` exists, write a one-line entry under "Latest per source" pointing at the new file. Otherwise `/review-recap` will rebuild the index next time it runs.
- **Infrastructure repos** (Task-Management, atlas-workspace, etc.): this section does not apply — the path-scoped rule won't load there.


## When to Use

- Before committing to a theoretical framework — is the evidence solid?
- Writing a literature review — need to distinguish robust from fragile findings
- Preparing a replication study — need to know what's already been tested
- Evaluating a paper for peer review — are its cited foundations sound?

## When NOT to Use

- **Your own results** — use the `referee2-reviewer` agent
- **Methodological comparison** — use `/method-audit`
- **Finding papers** — use `/literature` first

## Input

A `.bib` file, PDF directory, topic, or list of key findings to audit. Works best with a focused set of influential papers whose findings underpin a line of research.

## Workflow

### Phase 1: Findings Inventory

From the corpus (assembled as in other corpus skills), extract the **key empirical findings** — not paper summaries, but specific claims with effect sizes where available:

| Finding | Paper | Effect | N | Method |
|---------|-------|--------|---|--------|
| "X causes Y" | Author (Year) | d = 0.5 | 200 | RCT |
| "A predicts B" | Author (Year) | r = 0.3 | 1,500 | Survey |

Focus on findings that other papers **depend on** — the claims that, if wrong, would undermine subsequent work.

### Phase 2: Replication Search

For each key finding, search for replication attempts:

1. **Forward citations** — use `scholarly scholarly-citations` on the original paper's DOI
2. **Keyword search** — search for "replication" + key terms from the finding via `scholarly scholarly-search`
3. **Replication databases** — search for the paper on:
   - ReplicationWiki (via WebSearch)
   - Many Labs projects
   - Replication registries in the relevant field
4. **Author self-replication** — check if the original authors replicated in a new sample

**Dispatch rule.** If ≥5 key findings need auditing, batch findings into groups of 4–5 per sub-agent. Each sub-agent runs steps 1–4 for its batch (`scholarly-citations`, `scholarly-search`, web searches) and writes replication evidence to `/tmp/replication-audit-<n>.json`. Main context merges and proceeds to Phase 3 classification. For <5 findings, sequential searches in main context are fine. See [`_shared/cli-dispatch-policy.md`](../_shared/cli-dispatch-policy.md).

For each replication found, record:
- **Result:** Successful / Failed / Partial / Conceptual (similar but different design)
- **Sample:** How does it compare to the original (size, population)?
- **Method:** Exact replication or conceptual?
- **Effect size:** Same direction? Same magnitude?
- **Published where?** (Replication failures in top journals carry more weight)

### Phase 3: Classification

Classify each finding:

| Status | Criteria |
|--------|---------|
| **Replicated** | Successfully replicated by at least one independent team |
| **Multiply replicated** | Replicated 3+ times across different samples/contexts |
| **Failed to replicate** | At least one serious replication attempt found null or opposite results |
| **Contested** | Some replications succeed, others fail — mixed evidence |
| **Never tested** | No known replication attempts (most common and most concerning) |
| **Unreplicable** | Data/method too expensive, proprietary, or impractical to replicate |

### Phase 4: Dependency Mapping

Map which papers in the corpus **depend on** each finding:

```
Finding: "X causes Y" (Author, 2015) — STATUS: Failed to replicate
├── Paper A (2017) — builds entire model on this finding
├── Paper B (2019) — uses this as a control variable
└── Paper C (2021) — cites this as motivation but doesn't depend on it
```

Flag any paper whose core contribution depends on a non-replicated or failed finding.

### Phase 5: Risk Assessment

For each "never tested" finding, estimate replication risk:

| Risk factor | Increases concern |
|-------------|------------------|
| Small sample (N < 100) | High |
| P-value just below 0.05 | High |
| Surprising/counterintuitive result | Medium |
| Complex interaction effects | Medium |
| Single study, no robustness checks | High |
| Author has other failed replications | Medium |
| Published in a journal with low replication standards | Medium |

### Phase 6: Output

Write to `REPLICATION-AUDIT.md` in the project directory.

## Output Format

```markdown
# Replication Audit: [Topic]

**Date:** YYYY-MM-DD
**Corpus:** [N] papers
**Key findings audited:** [N]
**Status breakdown:** Replicated: X | Failed: Y | Never tested: Z | Contested: W

## Summary

[2-3 sentences: overall replication health of this literature]

## Finding-by-Finding Audit

### 1. "[Finding statement]" — Author (Year)

**Original:** N = [X], Effect = [Y], Method = [Z]
**Status:** [Replicated / Failed / Never tested / Contested]

**Replication evidence:**
- [Author (Year)] — [Result] — N = [X], Effect = [Y]
- [Author (Year)] — [Result] — N = [X], Effect = [Y]

**Depends on this:** [Papers in corpus that build on this finding]
**Risk level:** [Low / Medium / High / Critical]

### 2. "[Finding statement]" — Author (Year)
...

## Replication Status Matrix

| Finding | Original (Year) | Replicated? | Times tested | Risk |
|---------|----------------|-------------|-------------|------|

## Dependency Risk Map

Papers building on shaky foundations:

| Paper | Depends on | Status of dependency | Risk to paper's claims |
|-------|-----------|---------------------|----------------------|

## Recommendations

### Safe foundations (build on these)
- [Finding] — multiply replicated, robust across contexts

### Proceed with caution
- [Finding] — replicated once, small samples

### Avoid or re-test
- [Finding] — failed to replicate or never tested despite high risk factors

### Replication opportunities
- [Finding] — never tested, high-impact if confirmed, feasible to replicate with [data/method]
```

## Log to REVIEW-STATE.md (final step)

Write the replication audit to `reviews/<scope>/replication-audit/<YYYY-MM-DD-HHMM>.md` (`mkdir -p reviews/<scope>/replication-audit/` first), where `<scope>` is the paper slug or `_project`. Then append a row to the project's `REVIEW-STATE.md`:

```bash
bash ~/.claude/skills/_shared/review-state-log.sh \
  --check replication-audit \
  --paper "<paper-{venue} dir, or — for project-level audits>" \
  --verdict "<PASS|PARTIAL|FAIL>" \
  --score "<replicated-count>/<total-findings-checked>" \
  --open-issues "<failed-or-untested-count>/<total-findings-checked>" \
  --report "reviews/<scope>/replication-audit/<YYYY-MM-DD-HHMM>.md" \
  --notes "<one-line: e.g. '12/15 robust; 2 failed; 1 never tested'>" \
  [--trigger "pre-submission-report|review-cluster"]
```

- Verdict: PASS if every findings is robustly replicated; PARTIAL if some replicated, some not; FAIL if foundational findings failed to replicate.
- Score: robustly-replicated findings / total checked.
- Open issues: (failed + never-tested) / total at run time.
- Trigger: pass orchestrator name only if invoked as a sub-agent. Otherwise omit.

Schema: `~/Task-Management/docs/reference/review-state-schema.md`.

## Cross-References

| Skill | When to use instead/alongside |
|-------|-------------------------------|
| `/method-audit` | For broader methodological comparison (not replication-specific) |
| `/weakness-scanner` | For logical and argumentative weaknesses (not replication status) |
| `/literature` | To find the replication studies identified in this audit |
| `/split-pdf` | To deep-read any replication study found |
