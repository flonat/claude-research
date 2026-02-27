---
name: session-log
description: "Create timestamped progress logs for research sessions. Detects multi-project sessions and creates separate logs per project. Enables continuity between Claude sessions."
allowed-tools: Read, Write, Edit, Bash(mkdir*), Bash(ls*)
argument-hint: [project-name-or-path]
---

# Session Log Skill

> Automatically create timestamped progress logs for research sessions.

## Purpose

Based on Scott Cunningham's Claude Code workflow: "Progress logs are my autosave of the workflow." When sessions end or crash, the next Claude can read logs and pick up exactly where you left off.

## When to Use

At the end of any significant work session, or when asked to "log this session" or "update progress".

## Workflow

### Step 1: Identify Projects Touched

Before writing anything, inventory which projects were affected during this session. A "project" is any directory with its own `CLAUDE.md` or `log/` directory. Common splits:

| Scope | Where the log goes |
|-------|--------------------|
| Work inside a specific project | That project's `log/` |
| Global infrastructure (skills, hooks, rules, settings) | Task Management's `log/` |
| Course/module-level changes (reorganisation, new CLAUDE.md) | That module's `log/` |

**Signs of a multi-project session:**
- Files changed under `~/.claude/` (skills, hooks, settings) → global/infrastructure log
- Files changed in the CWD project → project-specific log
- Files changed in a parent or sibling directory → check if that's a separate project

### Step 2: Create One Log Per Project

For each project identified in Step 1:

1. **Read existing context** — check that project's `.context/current-focus.md` and recent `log/` entries
2. **Create `log/` directory** if it doesn't exist
3. **Write the log** to `log/YYYY-MM-DD-HHMM.md` within that project
4. **Scope the content** — each log only covers what happened in that project, not the whole session

If there's only one project, this reduces to a single log (the common case).

### Step 3: Cross-Reference

When multiple logs are created, add a brief cross-reference at the top of each:

```markdown
> Also logged: [other project name] — `[relative or absolute path to other log]`
```

This lets a future session in one project discover that related work happened elsewhere.

### Step 4: Offer Follow-Up

- **Offer to run `/update-focus`** for a structured update (session rotation, open loops), rather than making ad-hoc edits to `current-focus.md`
- If multiple projects were touched, offer to update focus for each

## Log Template

```markdown
# Session Log: [Date] [Time]

## Project: [Project Name]

## What We Did
- [Bullet points of accomplishments]

## Key Decisions
- [Any choices made and why]

## Problems/Blockers
- [Issues encountered]

## Next Steps
- [ ] [Actionable next items]

## Files Changed
- [List of modified files — only those in THIS project]
```

## Examples

### Single-project session
"Please log this session — we worked on the research paper, fixed the simulation code, and decided to target Journal B instead of Journal A."

→ One log in the MCDM project's `log/`

### Multi-project session
"Please log this session — we did Workshop 17, reorganised the module folder, and created two new global skills."

→ Three logs:
1. **Module project** `log/` — workshop completion, reorganisation, CLAUDE.md creation
2. **Task Management** `log/` — new skills (`init-project-course`, `audit-project-course`), new hook (`ensure-latexmkrc.sh`), settings.json changes
