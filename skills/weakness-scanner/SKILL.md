---
name: weakness-scanner
description: "Use when you need to identify the weakest arguments across a literature."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv*), Bash(python*), Task, WebSearch, WebFetch, Bash(paperpile*)
argument-hint: "[topic, .bib file, or paper directory]"
---

# Weakness Scanner

> Identify the weakest arguments made across a body of literature. Find logical flaws, data limitations, unsupported claims, and findings contradicted by other work. Your contribution section writes itself after this.

Unlike `/devils-advocate` (which stress-tests YOUR argument), this skill scans OTHER people's work for vulnerabilities. It's how you find the gap your paper fills.

## When to Use

- Before writing your contribution section — need to know what's broken in prior work
- Identifying research opportunities — weak arguments = space for new work
- Preparing a rebuttal or response — need to show where existing claims fall short
- Deciding which papers to build on vs. which to challenge

## When NOT to Use

- **Your own paper** — use `/devils-advocate` or the `paper-critic` agent
- **Full peer review** — use the `referee2-reviewer` agent
- **Methodological comparison** — use `/method-audit` (overlaps, but different focus)

## Input

Same corpus inputs: `.bib` file, PDF directory, topic, or paper list. Works best with 10-20 papers on a focused topic.

## Workflow

### Phase 1: Corpus Assembly

Same as other corpus skills. Prioritise empirical papers making causal or strong claims — these are most likely to have exploitable weaknesses.

### Phase 2: Weakness Extraction

For each paper (read via split-pdf), look for:

1. **Logical flaws**
   - Non sequiturs — conclusions that don't follow from the evidence
   - Circular reasoning — assuming what they're trying to prove
   - False dichotomies — presenting only two options when more exist
   - Hasty generalisation — drawing broad conclusions from narrow evidence

2. **Data limitations**
   - Small samples without power analysis
   - Non-representative populations with claims of generalisability
   - Measurement issues (self-report bias, proxy variables)
   - Missing data handled without sensitivity analysis

3. **Identification problems**
   - Causal claims from observational data without credible identification
   - Omitted variable bias acknowledged but not addressed
   - Reverse causality not ruled out
   - Weak instruments (if IV)

4. **Contradicted claims**
   - Findings that conflict with other papers in the corpus
   - Claims undermined by the authors' own robustness checks
   - Results that don't survive alternative specifications

5. **Rhetorical overreach**
   - Abstract claims stronger than the evidence supports
   - Policy recommendations not grounded in the findings
   - "First to study X" claims that ignore prior work

### Phase 3: Cross-Paper Validation

For each weakness identified:
1. Check if other papers in the corpus have already flagged it
2. Search for papers that contradict the weak claim (use `scholarly scholarly-search`)
3. Check if the weakness has been addressed in subsequent work by the same authors

### Phase 4: Severity Ranking

Rank all weaknesses by severity:

| Severity | Criteria |
|----------|---------|
| **Fatal** | The core finding is likely wrong — the paper's contribution doesn't hold |
| **Serious** | A major limitation that significantly qualifies the findings |
| **Moderate** | A real limitation that the authors should have discussed |
| **Minor** | A weakness that doesn't undermine the main claims |

### Phase 5: Output

Write to `WEAKNESS-SCAN.md` in the project directory.

## Output Format

```markdown
# Weakness Scan: [Topic]

**Date:** YYYY-MM-DD
**Corpus:** [N] papers
**Weaknesses identified:** [N] (Fatal: X, Serious: Y, Moderate: Z, Minor: W)

## Top 5 Weaknesses

### 1. [Paper — Author (Year)]

**Claim:**
> "[Verbatim quote of the weak claim]" (p. XX)

**Flaw:** [Type: logical / data / identification / contradiction / rhetorical]

**Why it's weak:** [Specific explanation of the logical flaw or data limitation]

**Already contradicted by:**
- [Paper A (Year)] — [How it contradicts]
- [Paper B (Year)] — [How it contradicts]

**What evidence WOULD make it strong:** [What the authors would need to show]

**Severity:** [Fatal / Serious / Moderate / Minor]

**Opportunity for your research:** [How this weakness creates space for new work]

### 2. [Paper — Author (Year)]
...

## Field-Level Vulnerabilities

Patterns that recur across multiple papers:

1. **[Vulnerability]** — seen in [N] papers
   - Papers affected: [list]
   - Why nobody has addressed it: [likely explanation]
   - How to exploit it: [what a new paper could do]

2. **[Vulnerability]**
...

## Contradiction Map

| Claim | Paper A says | Paper B says | Who has better evidence? |
|-------|-------------|-------------|------------------------|

## Implications for Your Research

- **Strongest opportunity:** [The biggest gap this scan reveals]
- **Contribution framing:** "[Your paper] addresses the [specific weakness] in [prior work] by [your approach]"
- **Caution:** [Any weakness that also applies to your planned approach]
```

## Cross-References

| Skill | When to use instead/alongside |
|-------|-------------------------------|
| `/devils-advocate` | To stress-test YOUR argument (this scans others') |
| `/method-audit` | For systematic methodological comparison (less adversarial) |
| `/theory-mapper` | To understand which theories underpin the weak arguments |
| `/replication-audit` | To check which findings have actually been replicated |
