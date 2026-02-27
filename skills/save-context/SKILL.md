---
name: save-context
description: "Save information from conversations to the user's task management context library. Use when the user says: 'save this to my context', 'remember this', 'add to my profile', 'update my current focus', 'add this person to my contacts', 'save this project info', or any variation of wanting to persist information for future AI sessions."
---

# Save to Context Library

Save information from the current conversation to the user's task management context files for future reference.

## Context Library Location

```
.context/
```

## Available Context Files

### 1. Profile (`profile.md`)
**Save here:** Personal details, roles, research areas, working style, preferences

**Triggers:**
- "Add this to my profile"
- "Remember that I prefer..."
- "Save my research interests"

**Format:** Update the relevant section, preserving existing content

### 2. Current Focus (`current-focus.md`)
**Save here:** What the user is actively working on, recent progress, next steps

**Triggers:**
- "Update my current focus"
- "I'm now working on..."
- "Save where I left off"

> **Preferred:** For structured end-of-session updates, use `/update-focus` instead. It preserves the full document structure and handles session rotation, open loops, and mental state. Use `/save-context` only for quick, targeted saves (e.g., adding a single note or updating one field). If `/update-focus` is not available, read the file first and merge carefully — never overwrite with a blank template.

**Format:** Read the existing file and update the relevant section. Do not use a template — the file has a rich structure that must be preserved.

### 3. Projects Index (`projects/_index.md`)
**Save here:** Project overviews, paper status, collaborations

**Triggers:**
- "Add this project"
- "Update my journal paper status"
- "Save this research idea"

**Format:** Update the appropriate table or section

### 4. Individual Project Files (`projects/papers/[name].md`)
**Save here:** Detailed notes on specific papers/projects

**Triggers:**
- "Save these notes to my [project] file"
- "Create a project file for [name]"

**Format:** Create new file if doesn't exist:
```markdown
# [Project Name]

## Overview
[Brief description]

## Status
[Current stage]

## Key Decisions
- [Important choices made]

## Notes
[Detailed notes]

## Action Items
- [ ] [Tasks]
```

### 5. People (`people/supervisors.md` or `people/collaborators.md`)
**Save here:** Information about supervisors, collaborators, contacts

**Triggers:**
- "Add [name] to my contacts"
- "Remember that [person] works on..."
- "Save [person]'s details"

**Format:**
```markdown
### [Name]
- **Institution:** [Where they work]
- **Role:** [Their position]
- **Collaboration:** [What you work on together]
- **Contact:** [Email/preferred method]
- **Notes:** [Relevant context]
```

### 6. Preferences (`preferences/`)
**Save here:** Task naming conventions, priority definitions, workflow preferences

**Triggers:**
- "Remember I prefer tasks named like..."
- "Save my priority rules"

### 7. Workflows (`workflows/`)
**Save here:** How the user wants certain processes to work

**Triggers:**
- "Update my daily review workflow"
- "Change how I want meetings processed"

## How to Save

### Step 1: Identify the target file
Based on the information type, determine which context file to update.

### Step 2: Read the existing file
Always read the current content first to preserve existing information.

### Step 3: Merge intelligently
- Don't overwrite existing content unless explicitly asked
- Add new information in the appropriate section
- Update timestamps where relevant

### Step 4: Write the updated file
Save the merged content back to the file.

### Step 5: Confirm
Tell the user what was saved and where:
> "Saved to `.context/[file]`: [brief summary of what was added]"

## Examples

**User:** "Remember that my supervisor is [Supervisor] [Supervisor], he specialises in multi-objective optimisation"

**Action:**
1. Read `.context/people/supervisors.md`
2. Find or create the Supervisor section
3. Update with: Name: [Supervisor] [Supervisor], Focus: Multi-objective optimisation
4. Save file
5. Respond: "Saved to `.context/people/supervisors.md`: Added [Supervisor] [Supervisor] as your supervisor (multi-objective optimisation)"

---

**User:** "Update my current focus - I'm now deep in the journal revision, specifically rewriting section 4"

**Action:**
1. Read `.context/current-focus.md`
2. Update "What I'm Working On" section
3. Add timestamp
4. Save file
5. Respond: "Updated `.context/current-focus.md`: Now working on journal revision, section 4 rewrite"

---

**User:** "Save this meeting summary to my context"

**Action:**
1. Determine if it's project-specific or general
2. If project-specific: save to `projects/papers/[project].md`
3. If general: save key points to `current-focus.md`
4. Extract any action items and offer to create Notion tasks

## Integration with Notion

After saving to context files, offer to:
- Create related tasks in Notion Tasks Tracker
- Update Research Pipeline if paper-related
- Link context to specific Notion pages

## Tips

- Always preserve existing content unless asked to replace
- Use timestamps for time-sensitive information
- Keep entries concise but complete
- Cross-reference between files when relevant
