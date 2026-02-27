# Workflows Guide

> How to use the workflow files in this folder.

## What Are Workflows?

Workflows are step-by-step process guides for recurring tasks. They tell Claude how to help you with specific activities.

**Note:** Some capabilities are now in `skills/` instead — skills are more comprehensive and include prompt templates, while workflows are simpler process guides.

## Available Workflows

| Workflow | When to Use | Trigger Phrase |
|----------|-------------|----------------|
| `daily-review.md` | Start of workday | "Plan my day" |
| `weekly-review.md` | End of week | "Weekly review" |
| `meeting-actions.md` | After meetings | "Extract actions from my meeting with [name]" |
| `replication-protocol.md` | Replicating a paper's results | "Help me replicate [paper]" |

## Related Skills

These capabilities are in `skills/` folder (more comprehensive):

| Skill | When to Use | Trigger Phrase |
|-------|-------------|----------------|
| `project-safety/` | Starting research projects | "Set up a new project safely" |
| `code-archaeology/` | Revisiting old code | "Audit this codebase" |
| `literature/` | Literature search & synthesis | "Build a literature review on [topic]" |

## How to Use

### Natural Language (Recommended)
Just ask naturally:

> "Help me plan my day"
> "Extract action items from yesterday's meeting with [Supervisor]"

### Direct Reference
Point to the specific workflow:

> "Read `.context/workflows/daily-review.md` and help me plan"

## Workflow Summaries

### Daily Review
**Purpose:** Plan your day with questions, not task dumps
**Process:** Energy check → Surface data → Prioritise → Create plan
**Output:** Must Do / Should Do / Could Do list

### Weekly Review
**Purpose:** Reflect on the week and plan the next
**Process:** Clear decks → Review completed → Plan Big 3 → Check projects
**Output:** Week summary + next week priorities

### Meeting Actions
**Purpose:** Extract tasks from meeting transcripts/notes
**Process:** Find transcript → Identify action items → Create Notion tasks
**Output:** Tasks in Notion with proper attribution

### Replication Protocol
**Purpose:** Replicate results from a published paper before extending
**Process:** Inventory targets → Line-by-line translation → Programmatic comparison → Extend
**Output:** `replication-targets.md` + `replication-report.md` in project directory

## Tips

- **Workflows = processes** — Step-by-step guides for recurring tasks
- **Skills = capabilities** — Comprehensive instructions with templates
- **Combine as needed** — E.g., use code-archaeology skill with project-safety skill
