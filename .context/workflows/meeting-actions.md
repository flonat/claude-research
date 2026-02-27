# Meeting Action Item Extraction

> How to process the user's meeting transcripts and extract action items.

## Source: Notion Meeting Transcripts

Meeting transcripts are stored in Notion as pages with titles like:
- `@14 January 2026 14:31`
- `@8 December 2025 16:02`

These are typically audio transcripts from meetings with supervisors, collaborators, and students.

## Extraction Rules

### What Counts as an Action Item

Look for:
1. **Explicit commitments:** "I'll do X", "I'm going to...", "I need to..."
2. **Requests:** "Can you...", "Could you send...", "Please..."
3. **Agreed next steps:** "The next step is...", "We agreed to..."
4. **Deadlines mentioned:** "by Friday", "before the meeting", "by end of month"

### What to Capture (Full Context)

For each action item, extract:

| Field | Description | Example |
|-------|-------------|---------|
| **Task** | What needs to be done | "Send updated literature review" |
| **Assignee** | Who should do it (the user or someone else) | the user |
| **Deadline** | When it's due (if mentioned) | "by next Tuesday" |
| **Related Project** | Which project this relates to | Journal Revision |
| **Source Meeting** | Link to the transcript | @14 January 2026 |
| **Context** | Why this matters / what was discussed | "Reviewer 2 requested more references on cognitive load" |

### Output Format for Notion

Create tasks in **Tasks Tracker** database with:

```
Task name: [Action verb] [Object] - [Brief context]
Status: Not started
Priority: [Infer from urgency/deadline]
Due date: [If mentioned]
Description:
  - Context: [Why this task exists]
  - From meeting: [Date] with [Person]
  - Related to: [Project]
```

### Example Extraction

**From transcript:**
> "the user, I know you would be operative for you, right? So when you have these events. You need to give a list of the names of people coming to the desk downstairs at the building..."

**Extracted action:**
```
Task name: Send guest list to Shard reception - event logistics
Status: Not started
Priority: Medium
Due date: [Before event date]
Description:
  - Context: For upcoming event, need to provide names to building security
  - From meeting: @11 December 2025 with [Person]
  - Related to: Event planning
```

## Processing Workflow

1. **Identify unprocessed transcripts** - Pages with `@[Date]` format
2. **Scan for action language** - Commitments, requests, agreements
3. **Extract with full context** - Don't just list tasks, explain why
4. **Create in Notion** - Add to Tasks Tracker with proper fields
5. **Mark as processed** - Add a property or note to the transcript page

## Special Cases

### Supervisor Action Items
- Flag these as higher priority by default
- Tag with the relevant university (relevant institution)

### Research-Related Actions
- Link to the relevant paper project
- Consider impact on PhD timeline

### Administrative Actions
- Often have hard deadlines (forms, claims, bookings)
- Tag with "Claim" type if it's a reimbursement/refund

## Integration

- **Auto-create:** Tasks go directly into Notion
- **Review:** the user reviews in the "Inbox" view (no due date set)
- **Triage:** During daily review, assign priorities and dates
