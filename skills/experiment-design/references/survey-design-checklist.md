# Survey Design Checklist

> Quality checks for survey instruments. Read during Survey mode of `/experiment-design`.

## Survey Flow Order

Standard experimental survey flow:

1. **Consent** — informed consent with study description, duration, compensation
2. **Screening** (if needed) — eligibility checks with graceful exclusion
3. **Demographics** (short) — age, gender, education (if needed for stratification; otherwise move to end)
4. **Pre-treatment measures** — baseline attitudes, traits (before any manipulation)
5. **Manipulation** — treatment/control condition exposure
6. **Manipulation check** — verify treatment was noticed/understood
7. **Dependent variables** — primary outcome, then secondary outcomes
8. **Attention check** — placed after key DVs, not before (to avoid priming)
9. **Mediators/Moderators** — process measures
10. **Demographics** (full) — remaining demographics, open-ended feedback
11. **Debrief** — purpose disclosure, contact info

## Attention Checks

### Placement Rules
- At least 1 attention check per 5 minutes of expected survey duration
- Never place immediately before the primary DV (priming risk)
- Never place at the very start (participants are still calibrating)
- Ideal positions: after the manipulation check, within a scale battery

### Types

| Type | Example | Pass rate target |
|------|---------|-----------------|
| Instructed response | "Please select 'Strongly Agree' for this item" | 90-95% |
| Content trap | "I have been to every country in the world" (embedded in a scale) | 85-90% |
| Comprehension check | "Based on what you just read, what was the person's job?" | 80-90% |
| Visual attention | "What colour was the background of the image?" | 85-95% |
| Open-ended quality | "In a few words, describe what the scenario was about" | Manual coding |

### Calibration (Krosnick 1991; Meade & Craig 2012)
- **MTurk/Prolific:** Expect 5-15% failure on instructed response items
- **Student samples:** Expect 3-8% failure
- **Panel samples:** Expect 2-5% failure
- If failure rate is <2% or >20%, the check may be too easy or too hard

### Exclusion Policy
Document in PAP:
- Which checks are used for exclusion vs. flagging
- Whether exclusion is applied before or after looking at results
- How you handle partial failures (e.g., fail 1 of 3 checks)

## Scale Quality Checks

### Acquiescence Bias
- **Flag:** Scales with 4+ items all worded in the same direction
- **Fix:** Add reverse-coded items (at least 1 per 4 same-direction items)
- **Report:** Warn if no reverse-coded items exist in a 5+ item scale

### Response Style Mitigation
- Vary response scale formats within a survey (Likert, slider, ranking)
- Use balanced scales (equal positive and negative anchors)
- Avoid agree/disagree format when possible — use construct-specific anchors

### Scale Diagnostics to Plan For
| Metric | Threshold | When to check |
|--------|-----------|---------------|
| Cronbach's alpha | > 0.70 | Post-data collection |
| Inter-item correlation | 0.15 - 0.85 | Post-data collection |
| Corrected item-total | > 0.30 | Post-data collection |
| Factor loadings | > 0.40 | If multiple subscales |

## Manipulation Checks

### When Required
- **Always** for between-subjects designs with novel manipulations
- **Optional** for well-established manipulations with published validation
- **Skip** if the manipulation IS the measure (e.g., real economic decisions)

### Types
| Type | Use when |
|------|----------|
| Direct MC | "Did you read about a human or AI?" — for awareness |
| Inference MC | "How competent did the advisor seem?" — for psychological state |
| Behavioural MC | Response time, engagement metrics — for effort |

### Placement
- After the manipulation and before DVs (standard)
- Exception: if the MC could contaminate the DV (demand effect), place after DVs

## Common Design Errors

| Error | Why it's a problem | Fix |
|-------|--------------------|-----|
| Leading question stems | Biases responses toward expected answer | Use neutral wording |
| Double-barrelled questions | Two concepts in one item → ambiguous responses | Split into two items |
| Anchoring with specific numbers | "How many hours (e.g., 10)?" biases toward 10 | Use open-ended or unanchored scale |
| Scale mismatch | 5-point for some items, 7-point for others in same construct | Standardize within constructs |
| Missing "prefer not to say" | Sensitive items without opt-out → non-response or lies | Add for demographics, sensitive topics |
| Too many matrix items | Survey fatigue → straightlining | Max 8-10 items per matrix block |
| No randomization | Order effects confound results | Randomize within blocks |

## Question Wording Rules

1. **One concept per question** — never double-barrelled
2. **Simple language** — 8th grade reading level for general population
3. **Neutral framing** — no leading questions
4. **Specific time frames** — "in the past 7 days" not "recently"
5. **Consistent anchors** — same direction within a scale
6. **No jargon** — unless the sample is expert (then define on first use)
