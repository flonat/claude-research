---
name: sync-notion
description: "Sync the current project's state to the central context library and Notion. Updates projects/_index.md, current-focus.md, and the Research Pipeline database entry."
allowed-tools: Read, Edit, Write, Glob, Grep, Bash(ls*), mcp__claude_ai_Notion__notion-search, mcp__claude_ai_Notion__notion-update-page, mcp__claude_ai_Notion__notion-fetch
argument-hint: [optional: summary of what changed]
---

# Update Notion Skill

> Sync the current project's state to the central task management context library and Notion Research Pipeline.

## Purpose

After working on a research project, this skill propagates the current state outward:
- **Project CLAUDE.md** (source of truth) → **`.context/projects/_index.md`** (central registry)
- **Recent session logs** → **`.context/current-focus.md`** (working memory)
- **Project metadata** → **Notion Research Pipeline** (tracking database)

This keeps all systems in sync without manual updates.

## When to Use

- At the end of a work session (often paired with `/session-log`)
- After changing a project's target journal, status, or stage
- When the user says "update project doc", "sync project", "update my project index"

## MCP Pre-Check

Before starting, probe Notion MCP availability with a lightweight search. If unavailable, skip Steps 3 and 5 and offer fallbacks per [`shared/mcp-degradation.md`](../shared/mcp-degradation.md).

## Workflow

### Step 1: Read the current project's CLAUDE.md

Extract key metadata:
- **Project name** (from header)
- **Target journal** (from `Target:` field)
- **Stage** (infer from content: Idea / Literature Review / Drafting / Data Collection / Analysis / Submitted / R&R / Published)
- **Co-authors** (if listed)
- **Working title**
- **Key next steps** (from Research Design or recent session log)

### Step 2: Read the most recent session log

Look in the project's `log/` directory for the latest `YYYY-MM-DD-HHMM.md` file. Extract:
- What was accomplished
- Current blockers
- Next steps

### Step 3: Update `.context/projects/_index.md`

Location: `.context/projects/_index.md`

Find the project's row in the "Papers in Progress" table. If it exists, update the Stage, Target Journal, and Status columns. If it doesn't exist, add a new row.

**Table format:**
```
| Project | Stage | Co-authors | Target Journal | Status |
```

### Step 4: Update `.context/current-focus.md`

Location: `.context/current-focus.md`

Update the "Recent Context" section with a brief summary of the latest session. Add any new open loops.

> **Note:** For full session-level updates (session rotation, open loop management, mental state), defer to `/update-focus`. This skill adds a brief summary only.

### Step 5: Update Notion Research Pipeline

Search the Research Pipeline database (`collection://YOUR-PIPELINE-DATABASE-ID-HERE`) for the project name. If found, update:
- **Status** (match to: Idea, Literature Review, Drafting, Submitted, R&R, Published)
- **Target Journal**
- **Priority** (if changed)

If not found, inform the user (don't auto-create — they may want to set properties manually).

### Step 6: Confirm

Report what was updated:
```
Updated project docs for [Project Name]:
- .context/projects/_index.md: [what changed]
- .context/current-focus.md: [what changed]
- Notion Research Pipeline: [what changed, or "no entry found"]
```

## Important Notes

- This skill **reads** the project CLAUDE.md and session logs — it never modifies them.
- It **writes** to the central context files and Notion only.
- Always read before writing to preserve existing content.
- If the user provides a summary argument, use that instead of inferring from logs.
