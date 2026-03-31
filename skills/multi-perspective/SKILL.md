---
name: multi-perspective
description: "Use when exploring a research question from multiple independent disciplinary perspectives. Spawns 3-5 parallel agents with distinct epistemic priors, runs anonymised cross-evaluation, and synthesises a structured comparison of agreements, tensions, and blind spots."
allowed-tools: Read, Write, Edit, Glob, Grep, Task, AskUserQuestion
argument-hint: "[research question, hypothesis, or design choice]"
---

# Multi-Perspective Exploration

Spawn 3-5 parallel agents, each with a distinct disciplinary lens and epistemic prior, to independently investigate a research question. Synthesise their findings into a structured comparison that surfaces agreements, tensions, and blind spots.

## When to Use

- Early-stage research design: "Is this the right question/method?"
- Choosing between competing identification strategies
- Before committing to a theoretical framework
- When a paper needs to convince reviewers from different traditions

## When NOT to Use

- **Quick feedback** — use `/devils-advocate` (single-perspective adversarial)
- **Literature search** — use `/literature`
- **Paper proofreading** — use `/proofread` or `paper-critic` agent

## Workflow

### Phase 1: Frame the Question

Read `$ARGUMENTS` and any referenced files. Formulate a clear, debatable research question or design choice. Good inputs:

- "Should I use DiD or synthetic control for this policy evaluation?"
- "Is bounded rationality or information asymmetry the better theoretical lens for this phenomenon?"
- "What are the threats to my identification strategy for [paper X]?"
- "How would different disciplines approach [phenomenon Y]?"

If the input is vague, ask one clarifying question before proceeding.

### Phase 2: Generate Perspectives

Generate 3-5 distinct perspectives. Each perspective is defined by:

| Field | Description |
|-------|-------------|
| **Label** | Short name (e.g., "Behavioural Economist", "Organisational Theorist") |
| **Discipline** | Academic field and tradition |
| **Epistemic prior** | What this perspective takes as given, and what it questions |
| **Methodological preference** | Preferred empirical approach and evidence standards |
| **Likely concern** | What this perspective would worry about most |

**Rules for perspective generation:**
- At least one perspective must be **methodologically sceptical** (e.g., econometrician focused on identification)
- At least one must come from a **different discipline** than the paper's primary field
- At least one must prioritise **practical/policy relevance** over internal validity
- Perspectives must **genuinely disagree** on at least one substantive point — no hollow diversity
- Ground perspectives in real traditions, not caricatures

**Perspective templates by domain:**

| If the research is about... | Consider these lenses |
|----------------------------|----------------------|
| Human-AI collaboration | Cognitive psychologist, HCI researcher, organisational economist, ethicist, systems engineer |
| MCDM / preference elicitation | Decision theorist, behavioural economist, operations researcher, UX researcher, philosopher of rationality |
| Multi-agent systems | Game theorist, mechanism designer, complexity scientist, political economist, social choice theorist |
| Organisational behaviour | Sociologist, micro-economist, evolutionary psychologist, management scientist, institutional theorist |
| Environmental/carbon policy | Environmental economist, political scientist, energy engineer, regulatory lawyer, behavioural scientist |

Present the generated perspectives to the user and get approval before proceeding. The user may want to add, remove, or adjust perspectives.

### Phase 3: Parallel Investigation

Spawn one sub-agent per perspective using the Task tool. Each agent receives:

```
You are a [LABEL] investigating this research question:

[QUESTION]

Your disciplinary background: [DISCIPLINE]
Your epistemic prior: [EPISTEMIC PRIOR]
Your methodological preference: [METHODOLOGICAL PREFERENCE]
Your primary concern: [LIKELY CONCERN]

Context about the project:
[Relevant project context — CLAUDE.md summary, paper abstract if available]

TASK: Analyse this question from your perspective. Address:
1. How would you frame this question in your discipline?
2. What theoretical framework would you apply?
3. What empirical strategy would you recommend, and why?
4. What are the main threats to validity from your perspective?
5. What would you find most/least convincing in the current approach?
6. What is the one thing the researcher is probably overlooking?

Be specific and grounded. Cite real methodological traditions and papers where relevant.
Write 300-500 words. Do not hedge — commit to your perspective's position.
```

**Agent configuration:**
- Use `subagent_type: general-purpose` for each
- Run all agents in parallel (up to 5 concurrent, per orchestration convention)
- Each agent writes to a temp file; collect results after all complete

### Phase 3.25: User Check-In (Interactive Mode)

Present each perspective's key position (2-3 sentences) and main disagreements. Ask via AskUserQuestion:

1. **Reveal constraints:** Anything these perspectives don't know? (data limitations, institutional constraints, supervisor preferences)
2. **Redirect:** Any perspective off-base or irrelevant?
3. **Challenge:** Push back on any specific claim?

User input feeds forward: constraints become "Additional context from the researcher" in cross-evaluation prompts; off-base perspectives are flagged but still included; challenges become extra evaluation criteria.

**Skip when:** User says "skip check-in", "just run it", or "non-interactive".

### Phase 3.5: Anonymised Cross-Evaluation

Run a peer-review round where each perspective critiques all others without knowing which lens produced which output.

**Setup:** Replace labels with neutral identifiers (Perspective A, B, C...). Strip self-identifying language.

**Spawn one evaluator agent per perspective** (parallel, `subagent_type: general-purpose`). Each evaluates all anonymous perspectives on: Rigour (1-5), Relevance (1-5), Novelty (1-5), Practicality (1-5). Each provides one strength, one weakness, and whether they'd change their own analysis. Include user constraints from Phase 3.25 if available — perspectives ignoring known constraints score lower on Practicality.

**Output:** Cross-evaluation matrix, self-revision signals, and consensus rankings for the final report.

### Phase 4: Synthesise

Read all agent outputs **and their peer evaluations** and produce a structured synthesis. Weight the synthesis by peer evaluation scores — perspectives rated highly across evaluators get more influence than those rated poorly:

#### 4.1 Agreement Map

What do all (or most) perspectives agree on? These are robust findings — if sceptics from different traditions converge, the point is likely sound.

#### 4.2 Tension Map

Where do perspectives disagree? For each tension:
- What is the disagreement about? (framing, method, assumption, evidence standard)
- Is it resolvable? (empirically testable vs. fundamentally different values)
- What would it take to resolve it?

#### 4.3 Blind Spot Detection

What did one perspective flag that no others mentioned? These are the most valuable findings — they reveal assumptions that are invisible within the primary discipline.

#### 4.4 Recommendations

Based on the synthesis:
1. **Strengthen:** What should the researcher do to address the most serious concerns?
2. **Acknowledge:** What limitations should be explicitly discussed in the paper?
3. **Test:** What additional analyses could resolve the key tensions?
4. **Reframe:** Should the question or approach be reconsidered?

### Phase 5: Output

Write the report to the project directory as `PERSPECTIVES-REPORT.md` (or print to console for quick use).

## Output Format

```markdown
# Multi-Perspective Analysis

**Question:** [The research question or design choice]
**Date:** YYYY-MM-DD
**Perspectives:** [N] ([list of labels])

## Perspectives

### 1. [Label]: [Discipline]
**Prior:** [One sentence]
**Analysis:** [Agent's full response]

### 2. [Label]: [Discipline]
...

## Peer Evaluation

| Perspective | Avg Rigour | Avg Relevance | Avg Novelty | Avg Practicality | Overall Rank |
|-------------|-----------|--------------|------------|-----------------|--------------|
| [Label] | X.X | X.X | X.X | X.X | #N |

**Key cross-evaluation findings:**
- [Which perspectives updated their view after seeing others]
- [Where evaluators converged on a strength/weakness]

## Synthesis

### Agreements
- [Point 1 — which perspectives agree, and why this is robust]
- [Point 2]

### Tensions

| Tension | Perspectives | Nature | Resolvable? |
|---------|-------------|--------|-------------|
| [Description] | A vs. B | Methodological | Yes — via [test] |
| [Description] | C vs. D, E | Conceptual | No — different values |

### Blind Spots
- [Finding] — flagged by [perspective], missed by all others
- [Finding]

### Recommendations
1. **Strengthen:** [Most important action]
2. **Acknowledge:** [Limitation to discuss]
3. **Test:** [Additional analysis]
4. **Reframe:** [If applicable]

## Next Steps
- [ ] [Actionable item 1]
- [ ] [Actionable item 2]
```

## Council Mode

**Trigger:** "Council multi-perspective" or "thorough multi-perspective"

Upgrades Phase 3 to use genuinely different LLM providers (Claude, GPT, Gemini) via `cli-council` instead of Claude sub-agents with personas. Cross-evaluation becomes genuine blind review across models.

```bash
uv run python -m cli_council \
    --prompt-file /tmp/perspective-prompt.txt \
    --context-file /tmp/research-context.txt \
    --output-md /tmp/perspectives-council.md \
    --chairman claude --timeout 180
```

See `skills/shared/council-protocol.md` for the full orchestration protocol.

## Cross-References

| Skill | When to use instead/alongside |
|-------|-------------------------------|
| `/devils-advocate` | Quick single-perspective adversarial feedback |
| `/literature` | Find the papers that perspectives reference |
| `/interview-me` | Develop the research idea through structured conversation |
| Referee 2 agent | Formal paper audit with code verification |
| `references/computational-many-analysts.md` | When combining qualitative perspectives with quantitative many-analysts |
