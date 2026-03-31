# Meeting Action Item Extraction

> How to process the user's meeting transcripts and extract action items.

## Recording System: Minutes

**Tool:** [minutes](https://github.com/silverstein/minutes) — local-first meeting capture with whisper.cpp transcription, speaker diarization, and structured output.

**Output location:** `~/meetings/` (multi-speaker recordings), `~/meetings/memos/` (voice memos)

**Output format:** Markdown with YAML frontmatter containing:
- `title`, `date`, `duration`, `type` (meeting/memo)
- `attendees`, `speaker_map` (diarized speakers → real names)
- `action_items` (structured: assignee, task, due, status)
- `decisions` (structured: text, topic)

**Audio routing:** BlackHole 2ch virtual audio device for system audio (Zoom, Meet, Teams). Built-in mic for in-person.

## Meeting Lifecycle Skills

| Step | Skill | When |
|------|-------|------|
| Prepare | `/minutes prep` | Before a call — builds relationship brief from prior meetings |
| Record | `/minutes record` | During meeting — `minutes record` / `minutes stop` |
| Note | `/minutes note` | During meeting — add timestamped annotations |
| Debrief | `/minutes debrief` | After meeting — compare outcomes to prep, track decisions |
| Daily recap | `/minutes recap` | End of day — digest all meetings |
| Weekly | `/minutes weekly` | End of week — themes, decision arcs, stale commitments |
| Search | `/minutes search` | Anytime — find past discussions by topic, person, decision |

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
| **Source Meeting** | Path to the transcript file | `~/meetings/2026-03-29-weekly-standup.md` |
| **Context** | Why this matters / what was discussed | "Reviewer 2 requested more references on cognitive load" |

### Output Format

Create tasks in the vault's `tasks/` directory as markdown files with YAML frontmatter:

```yaml
---
title: "[Action verb] [Object] - [Brief context]"
status: not-started
priority: [Infer from urgency/deadline]
due: YYYY-MM-DD
project: [project-slug]
tags: [meeting-action]
---

- **Context:** [Why this task exists]
- **From meeting:** [Date] with [Person]
- **Related to:** [Project]
```

## Processing Workflow

1. **Check for new transcripts** — `minutes list` or browse `~/meetings/`
2. **Run debrief** — `/minutes debrief` for structured analysis
3. **Extract action items** — from YAML frontmatter `action_items:` or transcript scan
4. **Create in vault** — add to `tasks/` directory with proper frontmatter
5. **Check for conflicts** — `/minutes debrief` flags decision conflicts with prior meetings

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

- **Auto-extraction:** Minutes extracts `action_items` into YAML frontmatter (when LLM summarization is configured)
- **Manual extraction:** Run `/minutes debrief` or use `meeting-analyst` agent for cross-meeting synthesis
- **Vault sync:** Tasks are written directly to vault `tasks/` files
- **Triage:** During daily review, assign priorities and dates

## Cross-Meeting Intelligence

The `meeting-analyst` agent handles questions spanning multiple meetings:
- Person profiles: "What does X usually bring up?"
- Decision tracking: "What have we decided about pricing?"
- Stale commitments: "What's still outstanding?"
- Preparation: "Prepare me for my call with the Acme team"
