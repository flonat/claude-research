---
name: minutes-debrief
description: Post-meeting debrief — analyzes what happened, compares outcomes to your prep intentions, tracks decision evolution. Use when the user says "debrief", "what just happened in that meeting", "what did we decide", "debrief that call", "post-meeting", "what changed", or right after stopping a recording.
user_invocable: true
---

# /minutes debrief

Post-meeting analysis that reads your latest recording, compares what happened to what you planned, and surfaces decision evolution — so nothing falls through the cracks.

## How it works

This is a multi-phase interactive flow. It connects to `/minutes prep` when a prep file exists, creating a before→after loop.

### Phase 1: Find the most recent recording

```bash
minutes list --limit 5
```

Pick the most recent recording. If there are multiple from today, ask via AskUserQuestion: "You have [N] recordings today. Which one are you debriefing?" with options listing the titles.

**If no recent recording exists:**
Say: "I don't see any recent recordings. Did you run `minutes record` and `minutes stop`? If the recording is from a specific meeting, tell me the title or date and I'll find it."

Don't proceed without a recording to debrief.

### Phase 2: Read the transcript

Use `Read` on the meeting file path. Extract from the transcript and frontmatter:

- **Decisions made** (from `decisions:` frontmatter or `## Decisions` section)
- **Action items created** (from `action_items:` frontmatter or `## Action Items` section)
- **Key discussion points** (from `## Summary` or the transcript itself)
- **Attendees** (from `attendees:` frontmatter)

### Phase 3: Check for matching prep

Look for a prep file that matches this meeting:

```bash
ls ~/.minutes/preps/ 2>/dev/null
```

Match logic:
1. Find `.prep.md` files from today or yesterday (within 48 hours)
2. Read each file's `person:` frontmatter field
3. Compare against the recording's `attendees:` list — match on first name
4. If multiple preps match → AskUserQuestion to pick which one
5. If no prep matches → standalone debrief (skip to 4.2)

### Phase 4: Debrief

Two paths depending on whether Phase 3 found a matching prep file.

#### 4.1 Prep-connected debrief (when a matching prep exists)

Read the prep file. Pull out the `goal:` field. Ask via AskUserQuestion:

"You went into this meeting wanting to: **[goal from prep]**

Did you accomplish it?"

Options:
- **A) Yes — fully resolved** → Mark as complete. Summarize what was decided.
- **B) Partially — some progress** → Ask: "What's still open?" Capture the remaining items.
- **C) No — it didn't come up or it changed** → Ask: "What happened instead?" Capture the pivot.
- **D) The goal changed during the meeting** → Ask: "What's the new direction?"

Then produce the debrief summary with the prep comparison:

```
## Debrief: [Meeting Title]

### Prep vs Reality
- **Goal:** [from prep]
- **Outcome:** [resolved / partially / pivoted]
- **What changed:** [if anything]

### Decisions
- [list each decision]

### Action Items
- [list with assignee and due date]

### Relationship Update
- [any notable changes in tone, new topics, shifted priorities]
```

#### 4.2 Standalone debrief (no matching prep)

Produce a straightforward debrief:

```
## Debrief: [Meeting Title]

### Key Decisions
- [list each decision]

### Action Items
- [list with assignee and due date]

### Notable Discussion Points
- [2-3 most significant things discussed]
```

### Phase 5: Decision evolution check

Search for prior decisions on the same topics discussed in this meeting:

```bash
minutes search "<topic>" --limit 10 --since <30-days-ago>
```

For each topic that has a decision in this meeting AND a decision in a prior meeting:
- Compare the decisions
- If they differ → surface the evolution:

"**Decision evolution — pricing:**
- Mar 3 (with Case): $599
- Mar 10 (with Alex): annual billing
- Today: monthly billing
- Status: **VOLATILE** (3 changes in 14 days)

Is this settled now, or still in flux?"

Classification:
- **STABLE** — Same decision held across 2+ meetings
- **VOLATILE** — Decision changed 2+ times in 14 days
- **CONFLICTING** — Two different active decisions exist on the same topic
- **NEW** — First decision on this topic

### Phase 6: Closing ritual

End with three beats:

1. **Signal reflection** — Quote something specific from the meeting or the debrief conversation.
   "You said '[quote]' — that sounds like the decision is locked."

2. **Assignment** — One concrete follow-up action.
   "Send Alex the pricing doc tonight while the conversation is fresh."
   "Update the roadmap doc with today's Q2 timeline change."

3. **Next skill nudge** — "At the end of the week, run `/minutes weekly` to see how all your meetings connect and what still needs attention."

### Phase 7: Update persistent relationship file

After the debrief is complete, update the persistent relationship file for each attendee (other than the user):

```bash
mkdir -p ~/.minutes/relationships
```

Write or update `~/.minutes/relationships/{first-name}.md`:

```markdown
---
person: {full name}
last_updated: {today ISO}
total_meetings: {count}
first_meeting: {date}
last_meeting: {today}
---

## Relationship Summary
{1-2 sentences: who they are, how the user knows them, their role}

## Active Topics
{bulleted list of topics currently active with this person — add new, remove stale}

## Communication Style
{direct/indirect, question-asker/proposer, tends to push back on X, etc.}

## Open Threads
{unresolved decisions, pending commitments between user and this person}

## Historical Decisions
{key decisions made with this person, most recent first, max 10}

## Notes
{any persistent context: their priorities, preferences, quirks}
```

**Update rules:**
- If the file exists, merge new information (don't overwrite — append to Active Topics, update Open Threads, add to Historical Decisions)
- Move resolved threads from "Open Threads" to "Historical Decisions"
- Remove topics from "Active Topics" if they haven't come up in 30+ days
- Keep the file under 100 lines — prune old historical decisions beyond 10 entries
- Set permissions: `chmod 600`

This file persists across sessions and is read by `/minutes prep` to build richer briefs without re-searching all meetings from scratch.

---

## Gotchas

- **Don't hallucinate if there's no recording** — If `minutes list` returns nothing, say so. Don't invent a debrief.
- **Stale preps (>48h) are ignored** — If the prep file is more than 48 hours old, treat it as no-prep mode. The prep was for a different context.
- **First-name matching for prep files** — The prep file slug uses first name only (`sarah.prep.md`). Match against attendee first names in the recording frontmatter. "Alex C." matches "sarah".
- **Multiple recordings today** — Ask which one. Don't assume the most recent is the right one.
- **Recordings without frontmatter** — Some recordings only have raw transcripts (no summary, no decisions section). Work with what you have — extract decisions and action items from the transcript text yourself.
- **Decision evolution can span weeks** — Search the last 30 days for related decisions, not just this week.
- **Don't be preachy about decision changes** — Decisions change for good reasons. Surface the evolution factually. "Here's what shifted" not "You keep changing your mind."
- **Relationship files are sensitive** — They contain accumulated intelligence about people. Always 0600 permissions.
