# Daily Review Workflow

> How AI should help the user plan their day.

## Approach: Questions First, Then Plan

Don't just generate a task list. Instead, follow this process:

### Step 1: Orientation Questions

Ask the user these questions (adapt based on context):

1. **Energy check:** "How are you feeling today - high energy for deep work, or better suited for lighter tasks?"

2. **Constraints:** "Any meetings or hard commitments today that I should plan around?"

3. **Continuity:** "What were you working on yesterday? Want to continue, or switch focus?"

4. **Pressure points:** "Anything weighing on your mind or feeling overdue?"

### Step 2: Surface Relevant Information

After understanding context, present:

1. **Overdue tasks** from Notion (Tasks Tracker)
2. **Due today** items
3. **Upcoming deadlines** (next 7 days)
4. **Recent meeting action items** not yet addressed
5. **Current focus** from `current-focus.md`

### Step 3: Help Prioritise

Based on the user's answers and the data:

1. Suggest a **realistic** number of tasks (usually 3-5)
2. Flag any **blocking** items (where others are waiting)
3. Consider the **project mix** - avoid all tasks from one project
4. Account for **transition costs** between different types of work

### Step 4: Create the Plan

Format the daily plan as:

```markdown
## Today's Focus: [Date]

### Must Do (non-negotiable)
1. [Task] - [Why it's a must]

### Should Do (important but flexible)
2. [Task]
3. [Task]

### Could Do (if time permits)
4. [Task]

### Parking Lot
- [Tasks explicitly deferred to another day]
```

## Example Interaction

**AI:** Good morning! Before we plan your day, a few quick questions:
- How's your energy today?
- Any meetings or fixed commitments?
- Where did you leave off yesterday?

**the user:** Tired. Meeting with [Supervisor] at 2pm. Was working on the journal revision.

**AI:** Got it. Given you're tired and have a meeting at 2pm, I'd suggest:

**Must Do:**
1. Prepare talking points for [Supervisor] meeting (30 min before)

**Should Do:**
2. Continue journal revision - Section 4 where you left off
3. Reply to [Supervisor]'s email about the project timeline

**Could Do:**
4. Review Notion inbox for captured tasks

That leaves your morning for focused writing and gives you buffer before the meeting. Does this feel right?

---

## Integration Points

- **Notion:** Query Tasks Tracker for overdue/due items
- **Calendar:** Check for meetings (if connected)
- **Current Focus:** Read `.context/current-focus.md`
- **Meeting Notes:** Check recent `@[Date]` pages for unprocessed action items
