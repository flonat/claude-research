# Stamp Directive Spec

> Canonical format for the `review-state-stamp` directive emitted by review agents at the end of their final response. Read by the orchestrator (main session for direct dispatch; `review-cluster`, `pre-submission-report`, `code-suite` for fan-out) and parsed by `skills/_shared/parse-stamp-directive.sh`.

## Why This Exists

Agents have inconsistent Bash tool grants at runtime (the 2026-05-19 harness investigation showed paper-critic and domain-reviewer self-report Bash unavailable despite YAML grants). The orchestrator always has Bash and always runs after the agent returns. The agent emits a directive describing what to stamp; the orchestrator stamps. This decouples the agent from the helper's tool surface.

## Format — strict YAML, NOT JSON

The directive is **YAML key:value lines inside a fenced markdown block**. Each line is `key: value` with a colon-space separator. **No JSON. No curly braces. No quoting of values unless they literally contain a colon.** The parser is a 30-line bash awk script — it will not tolerate JSON.

## Concrete example (template — substitute your agent's values)

````
```review-state-stamp
check: paper-critic
paper: paper-eaamo
verdict: NEEDS REVISION
score: 78/100
open_issues: 8/8
report: reviews/paper-eaamo/paper-critic/2026-05-19-1437.md
notes: M3 framing weak; 4 minors trivial
```
````

## BAD examples (parser will refuse — verify before emitting)

````
```review-state-stamp
{ "check": "paper-critic", ... }       ← NO. This is JSON, not YAML.
```
````

````
```review-state-stamp
check: paper-critic
paper: /tmp/stamp-test                 ← NO. `paper` is the BASENAME of the paper directory (e.g. `paper-eaamo`), not an absolute path.
score: 78                              ← NO. Score must include denominator: `78/100`.
report: reviews/paper-eaamo/paper-critic/X_CRITIC-REPORT.md  ← NO. Forbidden filename suffix (see review-artefact-routing.md §R2).
```
````

````
```review-state-stamp
check: paper-critic
paper: paper-eaamo
verdict: NEEDS REVISION
score: 78/100
open_issues: 8/8
report: reviews/paper-eaamo/paper-critic/2026-05-19-1437.md
notes: M3 framing weak;
       4 minors trivial                ← NO. Multi-line values forbidden. Single line only.
```
````

### BAD report-path forms (parser accepts these, the harness flags them later — fix at emission time)

````
```review-state-stamp
report: reviews/paper-eaamo/paper-critic/1437.md             ← NO. Missing date prefix. Must be YYYY-MM-DD-HHMM.md.
report: reviews/paper-eaamo/paper-critic/05-19-1437.md       ← NO. Missing year. Must be YYYY-MM-DD-HHMM.md.
report: reviews/paper-eaamo/paper-critic/2026-05-19T1437.md  ← NO. ISO T separator forbidden. Must be hyphen: YYYY-MM-DD-HHMM.md.
report: reviews/paper-eaamo/paper-critic/2026-05-19_1437.md  ← NO. Underscore separator forbidden. Must be hyphen.
report: reviews/paper-critic/paper-eaamo/2026-05-19-1437.md  ← NO. Wrong nesting: must be reviews/<scope>/<check>/, not reviews/<check>/<scope>/.
```
````

## Field rules

| Field | Required | Format |
|---|---|---|
| `check` | yes | Your agent's slug (e.g. `paper-critic`). The parser cross-checks this against the dispatched agent name. |
| `paper` | yes | **Basename** of the paper directory (e.g. `paper-eaamo`, `paper-test`), or `—` (em-dash) for project-level reviews. Never an absolute path. If unsure, use `—`. |
| `verdict` | yes | Tool-specific vocabulary — see your agent's definition. |
| `score` | yes | `n/100` form (e.g. `78/100`, `0/100`). If your agent doesn't produce a numeric score, use `—` (em-dash). Never bare `78`. |
| `open_issues` | yes | Snapshot of open issues at this run. Format `n/n` (open = total; never updated retrospectively). |
| `report` | yes | Relative path to the markdown you just wrote, in the form `reviews/<scope>/<check>/<YYYY-MM-DD-HHMM>.md`, where `<scope>` is the paper basename (e.g. `paper-eaamo`) or `_project` for project-level reviews, and `<check>` is your agent slug. **The basename MUST match `YYYY-MM-DD-HHMM.md`** (4-digit year, dash, 2-digit month, dash, 2-digit day, dash, 4-digit HHMM, `.md` extension). Forbidden basename forms: `HHMM.md` (missing date), `MMDD-HHMM.md` (no year), `YYYY-MM-DDTHHMM.md` (ISO `T` separator), `YYYY-MM-DD_CRITIC-REPORT.md` (suffix), `YYYY-MM-DD_round[N]_report.md`. See `rules/review-artefact-routing.md` §R2 for the full canonical-form grammar. |
| `notes` | yes | Single line, ≤120 chars. No newlines. No pipe characters (would break the INDEX.md table row). No double quotes around the value. |
| `trigger` | optional | `direct` (default) or the orchestrator slug. The orchestrator overrides this anyway; agents should omit or use `direct`. |
| `source` | optional | `agent` (default) or `manual` / `recap-inferred`. Agents should omit or use `agent`. |

### Legacy compatibility note

Prior to 2026-06-29, reports were filed in the flat form `reviews/<check>/<YYYY-MM-DD-HHMM>.md` (paper not encoded in path). This form is still **read-only compatible** for backward indexing, but **never write fresh reports in the flat form**. All new reports MUST use the nested form `reviews/<scope>/<check>/<YYYY-MM-DD-HHMM>.md` to preserve paper identity in the filesystem path.

## Verdict vocabulary by agent

| Agent | Accepted verdict values |
|---|---|
| `paper-critic` | `APPROVED`, `NEEDS REVISION`, `REJECT` |
| `domain-reviewer` | `PASS`, `NEEDS REVISION`, `FAIL` |
| `claim-verify` | `PASS`, `ISSUES FOUND` |
| `referee2-reviewer` | `ACCEPT`, `MINOR REVISION`, `MAJOR REVISION`, `REJECT` |
| `peer-reviewer` | `ACCEPT`, `MINOR REVISION`, `MAJOR REVISION`, `REJECT` |
| `blindspot` | `RAN` (always — the report's CLEAR/CONDITIONAL/HOLD ruling goes in `notes`) |
| `fatal-error-check` | `PASS`, `FAIL` |
| `code-paper-auditor` | `PASS`, `FAIL` |
| `artifact-coherence-auditor` | `PASS`, `GAPS FOUND` |
| `reproducibility-auditor` | `PASS`, `GAPS FOUND` |
| `code-review` | `PASS`, `NEEDS WORK`, `FAIL` |
| `proposal-reviewer` | `GREEN`, `READY-WITH-NOTES`, `REVISE`, `REJECT` |

## Exit criterion

The directive block is the **LAST thing** in your final response. Do not omit it. Do not paraphrase it. Do not put text after the closing fence. The orchestrator's parser scans for the first `\`\`\`review-state-stamp` opening fence; anything after the matching `\`\`\`` closing fence is ignored.

## What the orchestrator does with the directive

1. Captures your full final response to a temp file.
2. Runs `bash <skills-root>/_shared/parse-stamp-directive.sh <tempfile>` → produces `--check VAL --paper VAL ...` args.
3. Runs `bash <skills-root>/_shared/review-state-log.sh $ARGS --project <resolved>` (overriding `--trigger` if the orchestrator is a fan-out skill).
4. Appends a row to `<project>/reviews/INDEX.md`.

You don't run any of those steps yourself. Just emit the directive.

## Cross-References

- `rules/stamp-after-review-dispatch.md` — directs the main session to parse + stamp after direct dispatches
- `skills/_shared/parse-stamp-directive.sh` — the parser
- `skills/_shared/review-state-log.sh` — the helper that appends to INDEX.md
- `rules/review-artefact-routing.md` — where the agent's `.md` report itself lives + forbidden filename patterns
- `docs/reference/review-state-schema.md` — schema for the row appended after stamping
