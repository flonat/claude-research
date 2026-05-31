# Grounded Mode — Tool-Grounded Audit

> Mode for referee2-reviewer where every Major+ finding must be preceded by
> a tool-call attempt to verify the underlying claim. Composes with deep
> mode (4 rounds × verification discipline) and council mode (each LLM has
> its own verification budget).
>
> **Origin**: validated by `packages/peer-reviewer-bench` v2 (commit
> ab33e626). Tool-augmented `peer-reviewer` agent improved correctness
> +5.4pp and evidence sufficiency +15.7pp under cross-family GPT-5 judge
> on the prometheus-eval/peerreview-bench dataset. The persona-naive v2
> loop on this same agent regressed referee2 because the adversarial
> persona overrode tool restraint; this mode is the disciplined version
> that fixes that interaction.

---

## When to Use

| Trigger | Recommended mode |
|---|---|
| `"grounded review"`, `"grounded review"`, `mode: grounded` | Single-pass grounded |
| Pre-submission of a paper with many citations or numeric claims | Single-pass grounded |
| `"thorough grounded"`, `mode: deep mode: grounded` | Deep + grounded (4 rounds × discipline) |
| `"council grounded"`, multi-LLM citation verification | Council + grounded |
| Internal R&R prep where reviewers will check every reference | Grounded or deep+grounded |

**Don't use grounded mode for:**
- Early-draft feedback where structure matters more than claim-by-claim verification
- Section-level reviews on incomplete prose
- Reviews where the paper is intentionally abstract (no claims with external referents yet)

---

## The Verification Mandate

Before raising any **Major** or **Critical** finding, you MUST attempt verification via a tool call. **Minor** findings are exempt — verification overhead doesn't justify their severity.

| Claim type | Verification tool | Required |
|---|---|---|
| Citation existence (`Smith 2024 showed X`) | `WebSearch` with paper title + first-author surname + year | Yes |
| Cited methodological norm (`the field standard is X`) | `WebSearch` for the norm + likely originating paper | Yes |
| Numeric / table / equation claim (`MAE is 10.70 pm`, `error <1%`) | `Bash` with `python3 -c 'import sympy/numpy/scipy; …'` | Yes |
| Convergence rate / sample-size claim (`P=16 beads suffice`) | `Bash` with `python3 -c '…'` re-derivation | Yes |
| Author-code claim (`their script does X`) | `Bash` to actually run / grep the script | Yes |
| Style, structure, narrative, framing | No tool grounding required | No |
| LaTeX hygiene, formatting | No tool grounding required | No |

**A claim is "verified"** when the tool call returns results consistent with the claim. **A claim is "failed-verification"** when the tool call returns results that contradict, contradict-by-absence (zero hits for a cited paper title), or are inconclusive. **Failed verifications are themselves findings** (typically Major), not omissions.

Example failed-verification findings:
- *"M5: Paper cites Smith et al. 2024 'Robust Benchmark Adaptation' (ref [23]). WebSearch returns 0 results for this title + authors. The citation may be fabricated or the title/year is wrong; verify provenance."*
- *"M8: Paper states integral $\\int_0^\\infty e^{-x^2} dx = \\sqrt{\\pi}$. SymPy re-derivation gives $\\sqrt{\\pi}/2$. The paper's stated value is off by a factor of 2; check the derivation."*

---

## Tool Budget

| Mode composition | Budget |
|---|---|
| `mode: grounded` (single-pass) | 12 tool calls |
| `mode: deep mode: grounded` (4-round) | 30 tool calls (≈7 per round) |
| `mode: council mode: grounded` | 12 per LLM (each council member has its own budget) |

When the budget is exhausted, the agent forces final report compilation. Any remaining Major+ findings without verification get flagged in the Verification Ledger as `budget-exhausted: not verified` and downgraded one tier (Major → Minor, Critical → Major) — un-verified-because-budget should not block the paper.

Per-call hygiene:
- WebSearch queries should be specific (paper title + first-author surname + year), not generic (`Goodhart law machine learning`)
- Bash python snippets should be short (≤20 lines), self-contained (imports + computation + print), and use sympy / numpy / scipy which are available in the bench's `peer-reviewer-bench/.venv` AND in the user's project virtualenv
- If a snippet errors, fix it and retry once; if it errors a second time, treat the verification as inconclusive and flag in the ledger

---

## Composition Rules

### `mode: grounded` (single-pass)

Run all six audits with the verification mandate. Total tool budget = 12. Verification ledger spans the whole report.

### `mode: deep mode: grounded` (4-round)

Verification mandate applies within each round, but the budget is shared (30 across 4 rounds, ~7 per round). The self-challenge round (Round 4) uses its remaining budget to re-verify findings that survived the cut.

The deep-mode self-challenge check is *strengthened* under grounded mode: any Major finding without a corresponding successful verification in the ledger gets cut OR downgraded. This is the discipline mechanism — grounded mode trusts tools more than the persona's adversarial instinct.

### `mode: council mode: grounded`

Each council member runs grounded mode independently with its own 12-call budget. The chairman synthesis includes a "consensus verification" check — findings that multiple council members verified independently get a `verified-by-N-members` tag.

---

## Verification Ledger (Report Section)

Every grounded-mode report ends with a Verification Ledger section. See `report-template.md` for the full format; the structure is:

```markdown
## Verification Ledger

| Finding | Tier | Claim | Tool | Query / Snippet | Result |
|---|---|---|---|---|---|
| M3 | Major | Paper cites Smith 2024 (ref [23]) | WebSearch | "Smith 2024 robust benchmark adaptation" | 0 results — citation may be fabricated; flagged as new finding M3 |
| M8 | Major | Paper claims integral = √π | code_exec (sympy) | `sympy.integrate(sp.exp(-x**2), (x, 0, sp.oo))` | √π/2 — paper's value off by factor 2; flagged as new finding M8 |
| C1 | Critical | Author code reports MAE = 10.70 pm | Bash | `python code/analysis/eval.py | grep MAE` | 10.70 pm — confirmed |
| M11 | Major | Llama Guard 3 cited Inan 2023 | WebSearch | "Llama Guard 3 Meta 2024" | Llama Guard 3 released 2024 with Llama 3.1; Inan 2023 was original Llama Guard; year mismatch |
| M14 | Major | Stackelberg setup from Tirole 1988 | budget-exhausted | — | not verified — downgraded to Minor |

**Verification summary**: 18 / 22 Major+ findings verified; 2 failed (now flagged as M3 and M8); 1 budget-exhausted (M14 → m14); 1 inconclusive (M16, tool errored twice).
```

The ledger is mandatory. Without it, the report is not a grounded-mode report.

---

## Stamp Directive Convention

When stamping the run via the orchestrator (per `rules/stamp-after-review-dispatch.md`), the grounded-mode-specific token goes in the `notes:` field:

```review-state-stamp
check: referee2-reviewer
paper: paper-emnlp
verdict: NEEDS REVISION
score: 72/100
open_issues: 8/22
report: reviews/referee2-reviewer/2026-05-25-1830.md
notes: mode: grounded; 18/22 grounded; 2 failed-verification findings
```

The `notes:` field carries `mode: grounded` (or `mode: deep+grounded`, etc.) as the first segment so `/review-recap` can parse it and render mode-aware rows.

---

## Anti-patterns

- **Don't** use WebSearch for things you already know. The discipline is "before asserting an external claim, verify"; it is not "search the web before every paragraph."
- **Don't** treat WebSearch returning *something* as automatic confirmation. Read the snippet; if it doesn't actually verify the claim, the verification is inconclusive.
- **Don't** let a failed verification stop the review. Failed verifications are findings, not blockers. Continue.
- **Don't** spend budget on Minor findings. Reserve budget for Major+ where verification changes the report.
- **Don't** skip the ledger because findings are "obvious". The ledger is the audit trail; even confirmed findings get a row.

---

## Why This Mode Exists

The bench-validated finding from `peer-reviewer-bench` v2: tool access improves reviewer correctness +5–17pp on aggregate, but only when the persona is calibrated to USE the tools. Vanilla referee2 (adversarial-first) slightly regressed with naive tool access because the persona made sharper claims faster than the tools could verify them.

Grounded mode flips the order: **verify first, claim second**. The adversarial persona still drives WHICH claims get tested, but only verified claims survive to the final report. Failed verifications become explicit findings, making the bench's bias-correction visible in production output.
