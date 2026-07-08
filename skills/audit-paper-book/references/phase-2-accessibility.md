# Phase 2: Accessibility Check

For every chapter `.md` in `~/vault/books/<slug>/`, run the accessibility floor checks (parallel to `/init-paper-book` Phase 3.5):

- **Acronym expansion.** Regex `\b[A-Z]{2,}\b` extracts every acronym use. For each, verify it appears in expanded form (`<full phrase> (ACRONYM)`) before or at first use within the chapter. Common-acronyms baseline list (skip if expanded once): `DM, GP, BO, MOBO, ABM, EI, EHVI, MCDM, VOI, MAP, DOI, URL`.
- **Equation-prose pairing.** For every `$$...$$` display equation, check that the next paragraph (or 2 sentences) contains prose explaining what the equation says. Flag equations with no following prose.
- **Jargon-on-jargon.** Flag any sentence using ≥3 specialised terms (heuristic list: `posterior, prior, Laplace, Matérn, acquisition, surrogate, marginal, Hessian, scalarisation, kernel, MAP, MLE, Bayesian, GP, ELBO, KL divergence, Wasserstein, Pareto, hypervolume, regret`) with no inline definition of at least one.
- **Sentence length.** Flag sentences over 40 words — these are usually dense for an undergraduate reader. Severity `warn` only.

Capture: `accessibility_violations` list of `{chapter, line, type, snippet, severity}` where `type in {missing_acronym_expansion, equation_no_prose, jargon_dense, sentence_too_long}` and `severity in {block, warn}`. Block-tier: any acronym never expanded in its chapter; any display equation with zero following prose. Warn-tier: jargon-dense sentences, over-long sentences.

This phase always runs (regardless of `--apply`).
