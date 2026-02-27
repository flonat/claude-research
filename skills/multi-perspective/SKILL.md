---
name: multi-perspective
description: "Explore a research question from multiple independent perspectives with diverse epistemic priors. Spawns parallel agents with distinct disciplinary lenses, then synthesises findings."
allowed-tools: Read, Write, Edit, Glob, Grep, Task, AskUserQuestion
argument-hint: "[research question, hypothesis, or design choice]"
---

# Multi-Perspective Exploration

Spawn 3-5 parallel agents, each with a distinct disciplinary lens and epistemic prior, to independently investigate a research question. Then synthesise their findings into a structured comparison that surfaces agreements, tensions, and blind spots.

The core insight: a single-perspective analysis inherits the biases of that perspective. Deliberately introducing cognitive diversity — grounded in real disciplinary traditions — produces more robust research designs.

## When to Use

- Early-stage research design: "Is this the right question? Is this the right method?"
- When choosing between competing identification strategies
- When a paper needs to convince reviewers from different traditions
- Before committing to a theoretical framework
- When you suspect your approach has blind spots

## When NOT to Use

- **Quick feedback** — use `/devils-advocate` (single-perspective adversarial)
- **Literature search** — use `/literature` (discovery, not deliberation)
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

### Phase 3.5: Anonymised Cross-Evaluation

Before synthesising, run a peer-review round where each perspective critiques all others — without knowing which lens produced which output. This forces content-based evaluation rather than tribal dismissal.

**Setup:** Anonymise each perspective's output by replacing the label with a neutral identifier (Perspective A, B, C, ...). Strip any self-identifying language (e.g., "as an econometrician, I...").

**Spawn one evaluator agent per perspective** using the Task tool. Each receives:

```
You are a [LABEL] ([DISCIPLINE]).

Below are [N] anonymous analyses of this research question:

[QUESTION]

---
[Perspective A output — anonymised]
---
[Perspective B output — anonymised]
---
[Perspective C output — anonymised]
---

TASK: Evaluate each perspective on these criteria (1-5 scale):
1. **Rigour** — Is the reasoning sound? Are claims supported?
2. **Relevance** — Does it address the core question?
3. **Novelty** — Does it surface something the others miss?
4. **Practicality** — Could the researcher act on this advice?

For each perspective, provide:
- Scores (4 numbers)
- One strength (1 sentence)
- One weakness (1 sentence)
- Would you change your own analysis based on this? (yes/no + why)

Then rank all perspectives from most to least valuable for the researcher.
Be honest — evaluate the content, not the style. 200-300 words total.
```

**Agent configuration:**
- Use `subagent_type: general-purpose` for each
- Run all evaluator agents in parallel
- Each agent must NOT see which label produced which output

**What this produces:**
- A cross-evaluation matrix (each perspective rated by every other)
- Self-revision signals (perspectives that update their view after seeing others)
- Consensus rankings (which perspectives were rated highest across evaluators)

Include the cross-evaluation matrix in the final report (Section "Peer Evaluation") so the user can see where perspectives found each other compelling or weak.

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

## Council Mode Enhancement

In standard mode, Phase 3 spawns Claude sub-agents with different personas — but they all share the same underlying model. Council mode upgrades this to genuine model diversity: different LLM providers (Claude, GPT, Gemini) bring genuinely different reasoning patterns, training biases, and knowledge bases.

**Trigger:** "Council multi-perspective" or "thorough multi-perspective"

**What changes in council mode:**
- Phase 3 (Parallel Investigation): Each perspective is assigned to a different LLM provider via `cli-council`, not Claude sub-agents
- Phase 3.5 (Cross-Evaluation): Each model evaluates the others' perspectives without knowing which model produced which — genuine blind review
- Phase 4 (Synthesis): Chairman model reads all perspectives and cross-evaluations, weighted by peer scores

**Invocation (CLI backend):**
```bash
cd packages/cli-council
uv run python -m cli_council \
    --prompt-file /tmp/perspective-prompt.txt \
    --context-file /tmp/research-context.txt \
    --output-md /tmp/perspectives-council.md \
    --chairman claude \
    --timeout 180
```

See `skills/shared/council-protocol.md` for the full orchestration protocol.

**Value:** High — this skill is the natural fit for council mode. The whole point of multi-perspective analysis is cognitive diversity, and using genuinely different models instead of persona-differentiated instances of the same model is a strict upgrade.

## Cross-References

| Skill | When to use instead/alongside |
|-------|-------------------------------|
| `/devils-advocate` | Quick single-perspective adversarial feedback |
| `/literature` | Find the papers that perspectives reference |
| `/interview-me` | Develop the research idea through structured conversation |
| Referee 2 agent | Formal paper audit with code verification |
