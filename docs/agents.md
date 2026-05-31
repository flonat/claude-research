# Agents

> 15 specialised review agents with separate context and persistent memory.

Agents are autonomous sub-processes that run in a separate context via Claude Code's Task tool.
Unlike skills, agents solve the "grading your own homework" problem — they review work
without access to the author's reasoning.

## Available Agents

| Agent | Description |
|-------|-------------|
| `artifact-coherence-auditor` | Audits coherence between paper prose and replication outputs — catches hallucinated results, missing scripts, mismatched numbers, and unverifiable claims |
| `blindspot` | Peripheral vision audit for empirical output |
| `claim-verify` | Verify that cited claims in a paper accurately represent what the source papers actually say |
| `code-paper-auditor` | Use this agent when you need to verify code-paper consistency — mapping every quantitative claim in a paper to its source code and output files |
| `code-review` | Multi-persona orchestrator for adversarial review of R, Python, Julia, or Stata research scripts |
| `codex-research` | Code review and research agent that delegates to OpenAI Codex CLI in headless mode |
| `domain-reviewer` | Research-focused substantive correctness agent |
| `fatal-error-check` | Fast pre-review check for fatal errors in LaTeX papers |
| `fixer` | Generic fix implementer for any critic report |
| `gemini-research` | Web research agent that delegates to Gemini CLI in headless mode |
| `paper-critic` | Adversarial auditor for LaTeX papers |
| `peer-reviewer` | Use this agent when you need to review someone else's paper — as a peer reviewer, discussant, or for reading group preparation |
| `proposal-reviewer` | Use this agent when you need to review a research proposal, extended abstract, conference submission outline, or pre-paper plan — either his own or someone else's |
| `referee2-reviewer` | Use this agent when the user wants a rigorous, adversarial academic review of their work — including papers, manuscripts, research designs, code, or arguments |
| `reproducibility-auditor` | Reviews research workflows for reproducibility gaps — hidden dependencies, absolute paths, undocumented prerequisites, environment assumptions, and output traceability |

## How Agents Work

1. The main session spawns an agent via the Task tool
2. The agent runs in a separate context with its own instructions
3. The agent produces a report (never modifies source files)
4. The report is returned to the main session for review

## The Read-Only Principle

Review agents never modify the author's files. They produce reports and recommendations.
The `fixer` agent is the only exception — it reads a critic report and applies fixes,
but only when explicitly invoked.

## Creating a New Agent

Create a `.md` file in `.claude/agents/` with YAML frontmatter:

```yaml
---
name: my-agent
description: "What this agent does"
---
```

Agents are available globally via symlink: `~/.claude/agents/` points to this repo's `.claude/agents/`.
