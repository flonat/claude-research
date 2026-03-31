---
name: context-status
description: "Use when checking how much context window remains, whether preservation hooks are active, or what work items are pending. Displays a diagnostic summary of context usage percentage, active plans, session log freshness, and hook configuration status."
allowed-tools: Read, Glob, Bash(ls*), Bash(cat*)
---

# Context Status: Session Health Check

On-demand diagnostic showing context usage, preservation state, and open work items. Fast and lightweight — no Notion queries.

## Workflow

### Step 1: Context Usage Estimate

Read `~/.claude/sessions/{project-hash}/context-monitor-state.json` (project hash = first 12 chars of SHA-256 of `CLAUDE_PROJECT_DIR`). Calculate tool calls so far, estimated percentage (calls / 150), which thresholds have fired, and time since last warning. If the state file doesn't exist, report "No context monitor data — hook may not be active."

### Step 2: Active Plan

Find the latest file in `log/plans/`. Show filename, first 3 lines, and whether it contains "APPROVED" or "DRAFT". If none found, report "No active plan."

### Step 3: Latest Session Log

Find the latest non-compact `.md` file in `log/` (skip `-compact` files). Show filename and first 3 lines.

### Step 4: Focus Freshness

Check `.context/current-focus.md` modification date. If older than 3 days, warn "Focus file is stale — consider running `/update-focus`". Show the first 5 lines.

### Step 5: Preservation Hooks

Verify these hooks are configured in `~/.claude/settings.json`:

| Hook | Script | Expected |
|------|--------|----------|
| PreCompact | `precompact-autosave.py` | CONFIGURED |
| SessionStart compact | `postcompact-restore.py` | CONFIGURED |
| PostToolUse | `context-monitor.py` | CONFIGURED |

### Step 6: Open Loops

Count unchecked items (`- [ ]`) in `.context/current-focus.md`. If > 5, warn "Many open loops — consider triaging."

## Output Format

```
## Session Health

| Metric | Value |
|--------|-------|
| Context usage | ~XX% (N/150 tool calls) |
| Thresholds fired | none / info / warning / critical |
| Active plan | filename (DRAFT/APPROVED) / none |
| Latest log | filename / none |
| Focus freshness | N days ago / stale warning |
| Open loops | N items |

### Preservation Hooks

| Hook | Status |
|------|--------|
| PreCompact auto-save | CONFIGURED / MISSING |
| Post-compact restore | CONFIGURED / MISSING |
| Context monitor | CONFIGURED / MISSING |

### Recommendations

[Only if there are issues — e.g., stale focus, missing hooks, high context usage]
```

### Step 7: Compaction Guidance (when context > 60%)

Include these reference tables when context is high:

| Phase Transition | Compact? | Why |
|---|---|---|
| Research → Planning | Yes | Research context is bulky; plan is the distilled output |
| Planning → Implementation | Yes | Plan is in a file; free up context for code |
| Debugging → Next feature | Yes | Debug traces pollute context |
| After a failed approach | Yes | Clear dead-end reasoning |
| Mid-implementation | No | Losing file paths and partial state is costly |

| Persists After Compaction | Lost |
|---|---|
| CLAUDE.md + rules, Task list, MEMORY.md | Intermediate reasoning, file contents read |
| Git state, files on disk, precompact state | Multi-step context, tool call history |
