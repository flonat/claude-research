# Rule: Mark Unverified Claims

## Principle

**Never assert a citation, statistic, venue policy, or factual claim that hasn't been verified from a primary source.** Mark anything unverified as `[UNVERIFIED]` rather than asserting it. The user reads outputs critically and catches false claims, but the cost of catching them is real — and false claims that slip through (especially in submitted papers, grant applications, or briefings to collaborators) damage credibility.

## What "unverified" means

A claim is unverified when:

- The citation key, DOI, or paper title has NOT been confirmed against Crossref / Semantic Scholar / OpenAlex / Paperpile
- The venue policy (page limit, double-blind status, formatting rule, deadline) has NOT been read from the official CFP
- The statistic has NOT been computed from a known data source or quoted from a paper just read
- The author affiliation, journal impact factor, or institutional fact has NOT been checked against a structured source
- A **self-authored mathematical result** — a comparative static (∂/∂x sign), a monotonicity or limit claim, existence of a threshold, a closed form — has NOT been actually derived or checked (solving the recurrence, taking the derivative, evaluating the limit), but only asserted from intuition

## What to do instead

| Instead of | Write |
|---|---|
| "EAAMO is double-blind" | "EAAMO is `[UNVERIFIED — check 2026 CFP]` likely double-blind" |
| "Smith (2024) showed X" | "Smith (2024) `[UNVERIFIED]` reportedly showed X" |
| "ICML 2026 page limit is 9 pages" | "ICML 2026 page limit `[UNVERIFIED — last seen 8pp main + refs in 2025]`" |
| "so `$\partial C/\partial\lambda < 0$` and a threshold `$\lambda^\star$` arises" | derive it first (solve the recurrence, sign the derivative); if not done, `[UNVERIFIED]` / state as conjecture |

The `[UNVERIFIED]` flag is preserved through edits until the user or a sub-agent runs verification (e.g., `/bib-validate --verify-doi`, reading the official CFP, or querying a structured source).

## Self-authored mathematical results

A derived claim you *write into a paper* is subject to this rule exactly as a citation is. A comparative static, monotonicity/limit claim, threshold-existence claim, or closed form counts as **unverified until you have actually derived or checked it** — solved the recurrence, taken the derivative, evaluated the limit — not merely asserted it from intuition. **Clean LaTeX compilation is not verification** (it checks syntax, not truth), and neither is user approval of the prose. Until checked, mark `[UNVERIFIED]` or state the result explicitly as a conjecture. Watch in particular the **transient-vs-stationary conflation**: a learning/adjustment *rate* governs how fast a system reaches its fixed point, not where the fixed point is — so if the rate is meant to be the operative variable, the quantity must be evaluated on a finite horizon, not at the stationary limit. This is `mark-unverified` applied to your own mathematics, and the write-time complement to `paper-code-consistency.md` (which is review-time and code-focused). Trigger incident: `2026-07-03` paper-philtech Appendix A shipped "$C(\lambda)$ decreasing in $\lambda$" when the stationary $v^\infty=\phi(e)$ is $\lambda$-independent (caught by `/review-cluster`).

## When This Applies

- Drafting paper sections, abstracts, response letters, grant applications
- Producing literature notes, syntheses, reading lists
- Writing about venue specs (page limits, formats, deadlines, review styles)
- Reporting statistics or findings from prior work
- Generating citation lists from memory

## When to Skip

- The user explicitly says "draft fast, I'll verify later"
- Internal notes / brainstorming where verification would slow ideation
- Code comments documenting what the code does (not a factual claim about the world)

## Verification chains

Where the verification should come from, by claim type:

| Claim type | Primary source |
|---|---|
| Citation existence | `paperpile search-library` or `scholarly scholarly-verify-dois` |
| DOI resolution | Crossref API |
| Venue page limit / format | Official CFP page; never WikiCFP alone |
| Venue review style (single/double-blind) | Official CFP |
| Statistic from a paper | The paper PDF, current session-readable |
| Author affiliation | Author's institutional page or ORCID |
| Journal impact factor | OpenAlex `summary_stats.2yr_mean_citedness` or JCR (when access is available) |

## Anti-Patterns

- **Don't** invent a citation key like "smith2024gaming" because it's plausible — that's a fabrication.
- **Don't** assert a venue policy from training data — venue rules change yearly. Read the CFP.
- **Don't** quote a paper from memory without re-checking the actual claim. Hallucinated quotes are a top failure mode.
- **Don't** strip `[UNVERIFIED]` flags during editing without actually verifying. The flag is the trail of unfinished work.

## Trigger incidents

This rule was promoted to a global rule on 2026-05-10 after recurring incidents:
- Phantom citation numbers in literature notes
- Fabricated "double-blind option" claim about a venue
- Hallucinated bib entries that wasted a verification cycle

## Failure modes prevented

- **F1** fabricated citation — see [`docs/reference/failure-modes.md`](../docs/reference/failure-modes.md)
- **F2** hallucinated venue policy — see [`docs/reference/failure-modes.md`](../docs/reference/failure-modes.md)
- **F3** phantom quote from memory — see [`docs/reference/failure-modes.md`](../docs/reference/failure-modes.md)
- **F4** invented bib key — see [`docs/reference/failure-modes.md`](../docs/reference/failure-modes.md)
- **F6** stripped `[UNVERIFIED]` flag — see [`docs/reference/failure-modes.md`](../docs/reference/failure-modes.md)
