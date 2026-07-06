# Research lens: "What LLMs *change*" > "Whether LLMs *work*"

> Captured 2026-07-05 from a computational-social-science commentary (source: online post).
> A framing test for any LLM-in-social-science paper. Keep as a positioning filter.

## The lens

The high-marginal-value question is **not** "do LLMs work?" (benchmarking) but **"what do LLMs change?"** (methodological/theoretical innovation). Papers that survive 5 years ask the second.

**Shrinking-returns pattern (the "benchmark" pile) — avoid framing a paper as any of:**
- GPT vs. humans on task X
- Prompt A vs. Prompt B
- Model M1 vs. model M2
- Yet another synthetic-respondent validation
- Yet another "self-critique / ensembles improve performance" demo

**High-value pattern (the "change" pile) — frame toward:**
- New **measurement problems** introduced by LLMs
- When LLMs **distort** (not merely reproduce) social phenomena
- How LLMs reshape **inference, validity, reproducibility**
- Which social-science **theories** need reconsidering under generative AI
- New **computational methods** that could not have existed pre-LLM

## Portfolio mapping (2026-07-05)

**Already on the "change" side (lean into it explicitly):**
- Multi-agent collusion (RAG collusion audit; carbon-auction collusion) — LLM agents open a *new* collusion channel (shared latent reps, RAG side-channels) with no pre-LLM analog. The contribution is the new channel, not "LLMs collude ~like humans".
- Accountability paradox / dark patterns — what generative AI *reshapes* in responsibility attribution.

**At risk of the "benchmark" pile (invert the framing):**
- LLMs as synthetic respondents / preference elicitors (touches the MCDM + indifference-elicitation line). "LLM elicits utilities ~as well as humans" is the tired pattern; the *distortion* inversion is the paper.

## Four candidate topics generated under this lens (→ Scout novelty queued 2026-07-05)

1. **LLM-induced measurement reactivity in preference elicitation.** The LLM interlocutor is not a neutral instrument — its anchoring/priors distort the *revealed* preference. A construct-validity threat unique to generative elicitation. Extends the MCDM/indifference line. *(Strongest fit — extends existing work.)*
2. **Distributional distortion, not reproduction, in synthetic samples.** Standard papers show mean fidelity; the innovative version measures **variance collapse / model monoculture** — LLM samples shrink a population toward a modal persona. Propose a formal metric for how much of the human covariance structure survives. *(Strong fit — new method.)*
3. **Measurement under non-stationary instruments (reproducibility).** LLM-based measures rest on models that drift, deprecate, silently update. Reproducibility breaks in a *new* way — the ruler changes monthly. Short sharp methods piece.
4. **Unit of observation when respondents co-author with LLMs.** Org-behaviour theory: once responses are partly LLM-generated, "individual attitude" is no longer cleanly measured on a person. The dissolving unit of observation.

Assessment: #1 and #2 strongest (extend an existing line; both framed as *distortion*, the lens's sharpest ask).
