# Response Strategy Library

Systematic response strategies for different types of reviewer comments. Each strategy includes templates, examples, and guidance.

## Four Core Strategies

### 1. Accept

**When to use:**
- The reviewer identified a genuine problem or gap
- The fix is feasible and improves the paper
- Typos and formatting issues
- Reasonable improvement suggestions

**Template:**
```
We thank the reviewer for this valuable suggestion. We have [specific action].
[Location reference].
```

**Variations:**

Simple accept:
```
We thank the reviewer for this valuable suggestion. We have [specific change]. [Location].
```

Accept and expand:
```
We appreciate this insightful comment. We agree that [issue] is important.
We have [action 1] and [action 2]. These changes are reflected in [location 1]
and [location 2].
```

Accept typo/formatting:
```
We thank the reviewer for catching this. We have corrected [error type]
throughout the manuscript.
```

---

### 2. Defend

**When to use:**
- The current approach has sound justification
- The reviewer's suggestion doesn't apply to this setting
- Need to explain design choices with evidence

**Key principles:**
- Stay polite and respectful
- Provide specific evidence and reasoning
- Never say "The reviewer is wrong"

**Template:**
```
We appreciate the reviewer's concern. However, we respectfully note that
[our approach] is motivated by [reason]. Specifically, [detailed explanation].
We have added this clarification to Section [X].
```

**Variations:**

Comparative defence:
```
We thank the reviewer for this suggestion. While [reviewer's suggestion] has
advantages in [scenario A], we chose [our approach] because [reason 1] and
[reason 2]. Our analysis showed that [evidence]. We have added this discussion
to [location].
```

Technical limitation defence:
```
We appreciate this suggestion. However, [suggested approach] is not feasible
in our setting due to [constraint 1] and [constraint 2]. Instead, we
[alternative approach], which [advantage]. We have clarified this in [location].
```

---

### 3. Clarify

**When to use:**
- The reviewer misunderstood the paper
- The paper already contains the requested content
- Need to point to existing material politely

**Key principles:**
- Always be polite — even when the reviewer missed something obvious
- Provide specific location references (section, page, table, figure)
- Acknowledge that the writing could have been clearer
- Offer to improve the presentation

**Template:**
```
We thank the reviewer for raising this point. We would like to respectfully
clarify that [existing content]. This is discussed in [specific location].
To make this clearer, we have [improvement measure].
```

**Variations:**

Point to existing content:
```
We appreciate this comment. We would like to note that we did [work already done].
Specifically, [details]. These results are presented in [location]. To make this
more prominent, we have [improvement].
```

Acknowledge unclear writing:
```
We thank the reviewer for this comment. We apologise for the confusion. What we
meant is [clarification]. We have revised [location] to make this clearer.
```

**Important:** Even when the reviewer clearly missed something, take partial responsibility — "We apologise if this was not sufficiently clear" goes further than "As stated in Section 3..."

---

### 4. Experiment

**When to use:**
- Reviewer requests additional analysis or comparisons
- The request is feasible and would strengthen the paper
- Major Issues that require new evidence

**Key principles:**
- Only promise what you can deliver
- If already done, show results immediately
- If in progress, provide a timeline
- If not feasible, explain why and offer alternatives

**Template (completed):**
```
We thank the reviewer for this excellent suggestion. We have conducted additional
[analysis/experiments] on [content]. The results show that [key findings].
These new results have been added to [location].
```

**Template (in progress):**
```
We appreciate this valuable suggestion. We agree that [importance]. We are
currently conducting [work] and will include the results in the revised
manuscript. We expect to complete this within [timeframe].
```

**Template (not feasible):**
```
We thank the reviewer for this suggestion. While [requested work] would be
valuable, it is not feasible due to [constraint]. However, we have conducted
[alternative], which provides similar insights. The results show [findings].
These have been added to [location].
```

---

## Strategy Combinations

In practice, most responses combine strategies:

### Accept + Clarify
```
We thank the reviewer for these valuable comments. Regarding [issue A], we agree
this is an important point and have added a dedicated discussion in Section 5.3
(Accept). Regarding [issue B], we would like to respectfully clarify that we did
discuss this in Section 2.2 (page 3). To make this more prominent, we have
expanded the discussion (Clarify).
```

### Defend + Experiment
```
We appreciate the reviewer's suggestions. Regarding [approach X], we respectfully
note that [our approach] is more suitable because [reasons] (Defend). However, we
agree that [additional analysis] would strengthen our evaluation. We have conducted
[new work], and the results show [findings] (Experiment).
```

---

## Strategy Selection Flow

```
Comment → Is the reviewer correct?
│
├─ Yes → Is the fix feasible?
│   ├─ Yes, low cost       → Accept
│   ├─ Yes, needs new work → Experiment
│   └─ No, constrained     → Accept principle + explain + offer alternative
│
├─ Partially → Accept valid part + Defend the rest with evidence
│
├─ No (misunderstanding) → Clarify with location references
│
└─ Requests new work → Is it feasible?
    ├─ Yes → Experiment
    └─ No  → Explain constraint + offer alternative
```

## Strategy Priority

1. **Prefer Accept** — if the comment is valid and the fix is low-cost
2. **Use Defend sparingly** — only when you have strong justification
3. **Be gracious with Clarify** — even when the reviewer missed something obvious
4. **Be honest with Experiment** — only promise feasible work

## Tone Principles

**Always:**
- Thank the reviewer for their comment
- Use respectful, professional language
- Provide specific references and evidence
- Describe concrete improvements made

**Never:**
- "The reviewer is wrong"
- "This is obvious"
- "The reviewer failed to notice"
- Vague promises without specifics
- Defensive or aggressive language
