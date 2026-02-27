# Agents

> 6 specialised review agents with separate context and persistent memory.

Agents are autonomous sub-processes that run in a separate context via Claude Code's Task tool.
Unlike skills, agents solve the "grading your own homework" problem — they review work
without access to the author's reasoning.

## Available Agents

| Agent | Description |
|-------|-------------|
| `domain-reviewer` | Research-focused substantive correctness agent |
| `fixer` | Generic fix implementer for any critic report |
| `paper-critic` | Read-only adversarial auditor for LaTeX papers |
| `peer-reviewer` | Use this agent when you need to review someone else's paper — as a peer reviewer, discussant, or for reading group preparation |
| `proposal-reviewer` | Use this agent when you need to review a research proposal, extended abstract, conference submission outline, or pre-paper plan — either his own or someone else's |
| `referee2-reviewer` | Use this agent when the user wants a rigorous, adversarial academic review of their work — including papers, manuscripts, research designs, code, or arguments |

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
