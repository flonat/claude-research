# Rule: Paper-vs-Code Consistency Check

## Principle

**Before committing edits to §experiments or §methods, grep the actual code against the prose claim.** Paper-vs-code drift surfaces at peer-review time as a "soundness" or "reproducibility" objection; by then the fix is harder than catching it at commit time. AI reviewers and careful human reviewers both catch these — the lesson is that they shouldn't be there to catch.

## When this applies

- Editing `§experiments`, `§methods`, `§setup`, `§appendix-implementation` of an empirical paper
- Editing a method paragraph that describes a hyperparameter grid, optimisation procedure, search strategy, threshold, or filter
- Adding a constraint to a displayed equation (`s.t. …`) that is supposed to mirror a runtime check
- Auto-generated tables / macros that depend on a CSV — verify the macro values match a fresh CSV recompute, not a stale one
- Cross-referencing equation labels (e.g. "the utility floor in Eq. 2") — the label and the code path must agree

## When to skip

- Bibliography, related work, discussion sections (no code claims)
- Pure proof / theory sections
- Prose the user explicitly says is aspirational ("the formulation; implementation defers to follow-on")
- Trivial polish: rewording without changing claims

## Check protocol (≈60 s per claim)

1. **For every quantitative claim in the prose** (grid size, search space values, threshold, regularisation range, optimiser choice, number of seeds), open the code location that produces it. Grep is fine. The values in code and prose must match exactly.
2. **For every constraint in formal notation** (e.g. Eq. 2 with `s.t. Acc(f) ≥ α`), find the runtime check that enforces it. If there is no runtime check, the prose must say so (e.g. "we report the post-hoc utility distribution rather than filtering at search time").
3. **For every "the auditee does X" or "we use X" claim**, confirm X actually appears in the merged code (not a planned version, not a branch, not a stale `__pycache__`).
4. **For auto-generated tables**, recompute the source CSV before committing, then regenerate the table. Stale `\input{generated/foo.tex}` files cause silent number-drift across edits.

## Failure modes prevented

- Prose claims a hyperparameter search procedure that the code does not implement
- Equation specifies a constraint (utility floor, monotonicity, normalisation) that the code never checks
- Macro file (`results-numbers.tex`, `cis.tex`, …) holds values from an earlier grid run
- Stale Q25/Q75 quartile numbers in the abstract after a regrid changed the CSV
- "We tested all five seeds" but the CSV only has four

## Trigger incidents

This rule was added 2026-05-30 after two mismatches surfaced in one external-review pass on a TMLR submission:

1. The HP-grid paragraph claimed "convex-hull search over per-group ROC operating points" for the EOPost method; the actual code grid was `constraint × C`.
2. The auditee's optimisation was written `s.t. Acc(f) ≥ α` in Eq. 2; the runtime filter was simply `audit_disp ≤ τ`, with no accuracy check anywhere. The empirical utility distribution was reported separately, but the constraint in the equation was load-bearing in the prose and the runtime ignored it.

Both survived multiple internal review cycles. The external reviewers that caught them weren't doing anything clever — they were reading the §methods paragraph alongside the equation alongside the code, in that order.

## Cross-References

| Skill / Rule | Relationship |
|---|---|
| `code-paper-auditor` agent | Does this at audit time. This rule applies the same discipline at edit time, so fewer drift bugs reach audit. |
| `mark-unverified.md` | Same family: catch claims that aren't grounded before they ship. |
| `/proofread` | Reads prose carefully but does not cross-check against code. This rule fills that gap. |
| `/pre-submission-report` | The kitchen-sink final check; this rule is the daily-edit check. |

## Anti-Patterns

- **Don't** treat "the code probably does what the paragraph says" as a check. The whole point of the rule is that "probably" lies.
- **Don't** rely on a `__pycache__` file to confirm a behaviour. Read the `.py`.
- **Don't** regenerate a table from an old CSV "to save time" — that's exactly the drift the rule catches.
- **Don't** assume that because §experiments compiled, the claims in it are still valid. LaTeX compilation tells you about syntax, not about whether the code does what you said.
