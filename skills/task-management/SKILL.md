---
name: task-management
description: "Use for daily planning, weekly reviews, meeting actions, or read/write queries over the Research Vault and research portfolio: tasks, topics, papers, outputs, submissions, venues, people, institutions, and deadlines. Triggers include 'do I have any topics for this venue?', 'which institution-X projects target venue Y?', and 'what is recorded for this paper?'. For venue suitability or recommendations rather than recorded state, query the portfolio first, then use the installed venue-recommendation workflow."
allowed-tools: Read, Write, Edit, AskUserQuestion, Bash(taskflow-cli *)
---

# the user's Task Management System

## Portable vault pre-check

Before any vault-dependent workflow, probe the portable CLI once:

```bash
taskflow-cli list-topics --limit 1 --json
```

`taskflow-cli` is the default route in both clients. A Taskflow MCP registration is an optional Claude adapter; its absence never means that the vault is unavailable. If the CLI probe fails, report the failure and follow [`shared/mcp-degradation.md`](../shared/mcp-degradation.md).

For the boundary between stored portfolio facts, venue recommendations, venue policy, and interface audits, follow [`shared/research-query-routing.md`](../shared/research-query-routing.md).

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
- **Tasks Tracker**: Research Vault tasks database at `~/vault`
- **Research Pipeline**: Research Vault pipeline database at `~/vault`

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

### Research portfolio lookup

For questions such as “Do I have any topics associated with institution X that record venue Y?”:

1. Treat “do I have,” “which of my,” and “what is recorded” as stored-state queries, not venue recommendations.
2. Query the complete relevant inventories with `--json` and a sufficient `--limit`:
   - `taskflow-cli list-topics` for topic status, theme, and institution;
   - `taskflow-cli list-papers` for output venue and output status;
   - `taskflow-cli list-submissions` for active and historical venue events;
   - `taskflow-cli list-venues` for the canonical venue identity;
   - `taskflow-cli list-people` when collaborator or supervisor metadata defines the requested association.
3. Filter on structured metadata such as `institution`, not words appearing in titles.
4. Join topics to outputs by topic slug and submissions by their paper/topic wikilink. Resolve venue aliases through the venue inventory.
5. Report three categories separately:
   - **explicit potential venue** — recorded as an Idea/planned output;
   - **active or previous output** — a concrete Drafting/Submitted/Accepted/Rejected/Published-style output or submission event;
   - **inferred suitability** — plausible from the topic, but not recorded in the vault.
6. Invoke the installed venue-recommendation workflow only when the user asks for suitability, recommendations, or acceptance assessment. Never present recommendation inference as stored portfolio state.


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
