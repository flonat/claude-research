# Worker-Critic Protocol

> Lightweight inline review embedded within creator skills. The worker produces artifacts; a paired critic sub-agent reviews them in a separate context before the skill reports "done". This catches issues earlier than post-hoc review agents (`paper-critic`, `referee2-reviewer`), which are expensive and run after significant work is already committed.

## Principle

**Every major creator skill should have a built-in critic pass.** The critic is a read-only sub-agent spawned via the Agent tool. It sees the output artifact but NOT the reasoning that produced it — this independence is the source of its value.

## When to Use

Activate the critic pass when ALL of these hold:

1. The skill produces a substantial artifact (report, code, table, draft section — not just file edits)
2. The artifact will be consumed downstream (by the user, another skill, or a reviewer)
3. The skill is not itself a review skill (don't review the review)

## When to Skip

- Quick single-file edits
- Intermediate artifacts that will be immediately revised
- The user says "skip review" or "quick mode"
- The skill is already a review/audit skill (`paper-critic`, `code-review`, `referee2-reviewer`, etc.)

## Protocol

### 1. Worker Phase (normal skill execution)

The skill runs its standard workflow and produces the output artifact(s).

### 2. Critic Spawn

Spawn a sub-agent with:

```
Agent({
  description: "Inline critic for [skill-name]",
  prompt: "[CRITIC PROMPT — see templates below]",
  model: "haiku"  // fast and cheap — this is a lightweight check
})
```

**Key constraints for the critic prompt:**
- Pass the artifact content or file path (sub-agents can Read files)
- State what the artifact IS and what it's FOR (the critic has no conversation context)
- Ask for specific checks, not open-ended review
- Request structured output: a short verdict + itemised issues

### 3. Triage

The worker (main skill) receives the critic's report and:

| Critic verdict | Action |
|---------------|--------|
| **No issues** | Proceed — report success to user |
| **Minor issues** (formatting, style, clarity) | Fix inline, no need to re-run critic |
| **Major issues** (incorrect claims, missing sections, logical errors) | Fix, then re-run critic (max 1 retry) |
| **Structural issues** (wrong approach, missing data, flawed design) | Report to user with critic's findings — don't silently fix |

### 4. Report

Include a one-line critic summary in the skill's output:

```
**Inline review:** Passed (no issues) / Passed after 1 fix / Flagged N issues for user review
```

## Critic Prompt Templates

### For Literature Outputs

```
You are reviewing a literature synthesis produced by the /literature skill.
The output is at: [file_path]

Check for:
1. Are all claims attributed to specific papers (not vague "the literature suggests")?
2. Are there logical gaps between paragraphs (assertions that don't follow from cited evidence)?
3. Is the synthesis balanced (not just listing papers, but identifying tensions/agreements)?
4. Are there any claims that seem too specific to be real (potential hallucinated findings)?

Return: PASS/FAIL verdict + max 5 bullet points of issues found.
```

### For Code Outputs

```
You are reviewing code produced by the /computational-experiments skill.
The script is at: [file_path]

Check for:
1. Are random seeds set before any stochastic operation?
2. Are results written to files (not just printed)?
3. Are there hardcoded paths that should be relative?
4. Is the output format consistent with what downstream scripts expect?
5. Are there any obvious bugs (off-by-one, wrong variable name, missing imports)?

Return: PASS/FAIL verdict + max 5 bullet points of issues found.
```

### For Hypothesis Reports

```
You are reviewing a hypothesis report produced by the /hypothesis-generation skill.
The report is at: [file_path]

Check for:
1. Does each hypothesis have a distinct mechanism (not just variations of the same idea)?
2. Are the experimental designs actually testable with available methods?
3. Are there predictions that discriminate between competing hypotheses?
4. Are quality ratings justified (not all "Strong" across the board)?

Return: PASS/FAIL verdict + max 5 bullet points of issues found.
```

### For Data Analysis Outputs

```
You are reviewing an analysis report/script produced by the /data-analysis skill.
The output is at: [file_path]

Check for:
1. Does the specification match the stated estimand?
2. Are standard errors appropriate for the data structure (clustered, robust, etc.)?
3. Are sample restrictions documented and justified?
4. Are results presented with appropriate hedging for the identification strategy?

Return: PASS/FAIL verdict + max 5 bullet points of issues found.
```

## Which Skills Should Use This

| Skill | Artifact | Critic focus |
|-------|----------|-------------|
| `/literature` | Synthesis report | Attribution, balance, hallucination risk |
| `/hypothesis-generation` | Hypothesis report | Mechanism distinctness, testability |
| `/computational-experiments` | Code + results | Seeds, output routing, bugs |
| `/data-analysis` | Analysis script + tables | Specification-estimand alignment, SE choice |
| `/causal-design` | Design document | Assumption completeness, threat assessment |
| `/synthetic-data` | DGP code + validation | DGP-theory alignment, edge case coverage |

## Relationship to Existing Review Infrastructure

```
Skill execution ──→ [Worker-Critic] ──→ Skill output ──→ [paper-critic / referee2 / code-review]
                    (inline, fast,       (cleaned)        (post-hoc, thorough, expensive)
                     haiku-level)
```

The worker-critic catches low-hanging issues before the heavy review agents run. This reduces the noise in `paper-critic` reports and focuses expensive review time on substantive problems.

## Cost Model

Using `haiku` for critic sub-agents keeps costs minimal:
- ~2-5 seconds per critic pass
- ~$0.001-0.005 per invocation
- Net positive ROI: catching one issue early saves a full paper-critic re-run (~$0.10-0.50)
