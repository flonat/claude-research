# Round 1 Q5 — Target Venue

> Referenced from: `init-project-research/SKILL.md` Phase 1, Round 1, Q5.

Capture the target venue and check its ranking. Three sub-cases by venue type.

## Journal

- Check CABS AJG ranking via `.context/resources/venue-rankings.md` and the CSV at `.context/resources/venue-rankings/abs_ajg_2024.csv`.
- For SJR score, query the Elsevier Serial Title API (snippet in `venue-rankings.md`; requires `SCOPUS_API_KEY`).
- Flag journals below CABS 4 with at least two higher-ranked alternatives in the same area before proceeding.

Capture for the project record: full name, ISSN, CABS rank, SJR score, typical word limit, deadline (if known).

## Conference

- Check CORE ranking via `.context/resources/venue-rankings.md` and the CSV at `.context/resources/venue-rankings/core_2026.csv`.
- Flag conferences below CORE A with alternatives.

Capture: full name, CORE rank, page limit, format (single-column / two-column / LNCS / ACM), review type (single-blind / double-blind), anonymisation requirement, abstract deadline, full-paper deadline, notification date, camera-ready date, author registration deadline.

## Preprint

Note the server (arXiv, SSRN, NBER, OSF, ResearchGate). No ranking check needed.

For arXiv, capture the primary subject category (e.g., `cs.CL`, `econ.GN`).
