---
name: task-management
description: "Use when you need help with daily planning, weekly reviews, meeting actions, or vault task queries."
allowed-tools: Read, Write, Edit, AskUserQuestion
---

# the user's Task Management System

## MCP Pre-Check

Before any vault-dependent workflow, probe taskflow MCP availability with a lightweight search. If unavailable, skip vault queries and offer local-only fallbacks per [`shared/mcp-degradation.md`](../shared/mcp-degradation.md).

## System Overview

This is a hybrid vault + local context library system. Before taking action:

1. **Read context files** in `.context/` to understand current state
2. **Query vault** for dynamic task data
3. **Ask questions** before dumping lists (the user prefers this)
4. **Update context** after sessions

## Key Locations

### Context Library (`.context/`)
- `profile.md` — Who the user is, roles, research areas
- `current-focus.md` — What they're working on NOW (update this!)
- `projects/_index.md` — All active projects
- `workflows/` — How to help with specific tasks
- `preferences/` — Priority definitions, naming conventions
- `people/` — Supervisors and collaborators

### Vaults
- **Tasks Tracker**: Research Vault tasks database at `~/Research-Vault`
- **Research Pipeline**: Research Vault pipeline database at `~/Research-Vault`

## Workflows

### Daily Planning

When the user asks to plan their day:

1. **Read** `.context/current-focus.md` and `.context/workflows/daily-review.md`
2. **Query vault** for:
   - Overdue tasks (Due date < today, Status != Done)
   - Due today (Due date = today)
   - High priority items
3. **Ask orientation questions**:
   - "How's your energy today?"
   - "Any fixed commitments?"
   - "What were you working on yesterday?"
4. **Help prioritise** based on answers
5. **Update** `current-focus.md` at end of session

### Meeting Action Extraction

When the user asks to extract actions from a meeting:

1. **Read** `.context/workflows/meeting-actions.md`
2. **Find the meeting transcript** in vault (pages starting with @Date)
3. **Extract action items** looking for:
   - "I'll...", "I need to...", "I should..."
   - "Can you...", "Please..."
   - "We agreed to...", "Next step is..."
4. **Create tasks in vault** with full context:
   - Task name (action verb + object)
   - Project (infer from context)
   - Source: "Meeting"
   - Due date (if mentioned)
   - Description (meeting context)

### Weekly Review

When the user asks for weekly review:

1. **Read** `.context/workflows/weekly-review.md`
2. **Query vault** for:
   - Completed tasks this week
   - Overdue tasks
   - Upcoming deadlines
3. **Guide through reflection**:
   - What got done?
   - What didn't happen?
   - What emerged?
4. **Help plan next week's Big 3**
5. **Update** `current-focus.md` and `projects/_index.md`

### Task Creation

When creating tasks in vault:

**Required fields:**
- Task name (action verb + specific object)
- Status: "Not started"

**Recommended fields:**
- Project: Match to existing project
- Source: Meeting, Email, Supervisor request, Self-initiated, etc.
- Priority: High/Medium/Low (see `.context/preferences/priorities.md`)
- Due date: If known
- Task type: 📝 Writing, 📚 Reading, 🔬 Research, 📅 Meeting, 📋 Admin, 📧 Communication

### Research Pipeline

For paper-related queries:

1. **Query Research Pipeline database** for paper status
2. **Stages**: Idea → Literature Review → Drafting → Submitted → R&R → Published
3. **Link tasks to papers** via Project property

## the user's Preferences

- **Questions over lists** — Don't dump task lists, ask what to focus on
- **Full context for actions** — Include who, what, why, when in task descriptions
- **Flexible/reactive style** — They work on what feels right, help them navigate
- **Daily review preferred** — Short check-ins work better than big weekly sessions
- **multiple active projects** — Help manage cognitive load, don't add more

## Important Context

- PhD Year 1 at [University]
- Teaching
- 4 supervisors across institutions
- Research: [your research areas]
- Current papers: journal revision, [Project] theory, [Project]

## After Every Session

Update `.context/current-focus.md` with:
- What was worked on
- Where things were left off
- What's next
