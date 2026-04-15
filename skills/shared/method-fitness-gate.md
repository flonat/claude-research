# Method-Fitness Gate — Shared Protocol

> Validates that the proposed research method can actually answer the research question BEFORE committing to expensive literature search or data collection. Referenced by `/literature` (pipeline mode) and `/init-project-research`.

## Principle

**A good question paired with the wrong method wastes months.** The method-fitness gate checks RQ-method alignment before committing research effort. This is distinct from concept-validation-gate (which checks concept quality) and integrity-gates (which checks post-hoc verification). This gates the transition from "planning" to "doing."

## When This Applies

- `/literature` in pipeline mode — between Phase 1.5 (search plan) and Phase 2 (search execution)
- `/init-project-research` — during the methodology interview phase
- Any project kickoff where a method has been proposed but not stress-tested

## When to Skip

- Standalone `/literature` (free-form search without project context)
- Pure exploratory searches ("what's out there on X?")
- the user explicitly says "skip method check" or "just search"

## The Five Checks

### 1. Causal-Descriptive Alignment

| RQ type | Requires | Red flags |
|---------|----------|-----------|
| "What causes X?" / "Does X increase Y?" | Experimental, quasi-experimental, or credible IV/RDD/DiD | Proposing surveys, correlations, or qualitative methods for causal claims |
| "What is X?" / "How does X work?" | Descriptive, qualitative, case study, ethnography | Proposing experiments without theory for why there'd be an effect |
| "How much X?" / "What predicts X?" | Quantitative descriptive, ML prediction, regression | Proposing causal language for correlational designs |
| "Why does X happen?" | Process tracing, qualitative, mixed methods | Proposing regression alone for mechanism questions |

**Check:** Does the verb in the RQ match what the method can deliver?

### 2. Identification Strategy Credibility

For causal/quasi-experimental designs:

| Design | Key requirement | Common failure |
|--------|----------------|----------------|
| DiD | Parallel trends assumption | No pre-treatment data, or trends clearly diverge |
| IV | Exclusion restriction + relevance | Instrument is weak (F < 10) or has direct effects |
| RDD | Clear cutoff + manipulation test | Running variable is manipulable |
| Matching/PSM | Selection on observables sufficient | Unobservables obviously matter |
| Lab experiment | Random assignment + SUTVA | Interference between subjects, demand effects |
| Survey experiment | Attention checks + ecological validity | Hypothetical scenarios without real stakes |

**Check:** Is the identification strategy named and defensible, or just assumed?

### 3. Data Feasibility

| Question | Concern |
|----------|---------|
| Does the required data exist? | Don't propose methods requiring data you can't access |
| Is the sample size sufficient? | Power analysis or precedent from similar studies |
| Is the unit of analysis correct? | Ecological fallacy, aggregation bias |
| Are there ethical constraints? | DUA restrictions, IRB requirements, GDPR |
| Is the data collection timeline realistic? | PhD Year 1 should not propose 3-year longitudinal designs |

**Check:** Can you actually get the data this method needs within your constraints?

### 4. Theoretical Mechanism

| Design type | Theory requirement |
|-------------|-------------------|
| Confirmatory (testing a hypothesis) | Named mechanism, directional prediction, falsifiable |
| Exploratory (generating theory) | Theoretical sensitizing concepts, but predictions not required |
| Mixed methods | Theory guides qualitative → quantitative (or reverse) sequencing |

**Check:** Is there a reason to expect the proposed effect, or is this a fishing expedition?

### 5. Precedent Check

| Question | How to verify |
|----------|--------------|
| Has this method been used for similar questions? | Search for "[method] + [domain]" papers |
| What's the typical sample size in these studies? | Check recent publications |
| Are there methodological objections in the literature? | Search for critique papers |
| Is the method fashionable or established? | Reviewers are skeptical of trendy methods without track record in the domain |

**Check:** Would a reviewer accept this method for this question in this field?

## Verdict

| Result | Condition | Action |
|--------|-----------|--------|
| **PASS** | All 5 checks satisfied, no red flags | Proceed to search/data collection |
| **REVISE** | 1-2 checks flagged, fixable | State what's wrong, suggest alternatives, wait for revision |
| **FAIL** | 3+ checks flagged, or fundamental mismatch (causal claim + correlational design) | Block. Suggest the user rethink the method or narrow the RQ. Offer alternatives. |

## How to Present

Keep it concise. Don't write a 500-word report — state the checks as a quick table:

```
Method-fitness check:
1. Causal-descriptive alignment: ✅ (DiD appropriate for "effect of X on Y")
2. Identification: ⚠️ (parallel trends not yet demonstrated — need pre-treatment data)
3. Data feasibility: ✅ (panel data available via OpenAlex)
4. Theoretical mechanism: ✅ (anchoring theory predicts direction)
5. Precedent: ✅ (3 published papers use DiD for similar policy questions)

Verdict: REVISE — address identification concern before committing to full search.
Suggestion: Find pre-treatment outcome data to test parallel trends, or consider synthetic control as alternative.
```

## Integration with Literature Skill

In pipeline mode, this gate runs between Phase 1.5 (search plan confirmation) and Phase 2 (parallel search). The flow:

1. Phase 1.5: Search plan presented and confirmed
2. **Method-fitness gate**: Quick 5-check validation of RQ-method fit
3. If PASS → Phase 2 (search)
4. If REVISE → feedback + wait for user response → re-check
5. If FAIL → block search, suggest alternatives

In standalone mode, skip entirely — standalone searches don't commit to a method.

## Interaction with Concept-Validation-Gate

These two gates check different things:

| Gate | What it validates | When it fires |
|------|------------------|---------------|
| Concept-validation-gate | Is the concept developed? (RQ clarity, theory, contribution, scope) | Before synthesis/drafting |
| Method-fitness-gate | Does the method match the RQ? (identification, data, precedent) | Before search/data collection |

A concept can pass validation but fail method-fitness (e.g., great question, wrong method). Both must pass for pipeline mode to proceed.
