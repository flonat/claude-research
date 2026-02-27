# MCP Degradation Pattern

> Shared reference for skills that depend on MCP servers. Gracefully degrade when a server is unreachable instead of failing silently or blocking the workflow.

## The 5-Step Pattern

### Step 1: Probe at Start

Before any MCP-dependent work, test connectivity:

```
Try a lightweight read operation (e.g., notion-search with a known term,
openalex_search_works with a trivial query). If it times out or errors,
mark that server as unavailable for the session.
```

Do this **once**, at the beginning of the skill — not before every call.

### Step 2: Report Availability

After probing, state clearly:

```
MCP status:
- Notion: ✓ available
- OpenAlex: ✗ unavailable (timeout)
```

This sets expectations before the user sees skipped steps.

### Step 3: Skip Dependent Phases

When a server is unavailable, skip phases that depend on it entirely — do not attempt them, do not retry. Mark skipped phases clearly in the output:

```
Step 5: Update Notion Research Pipeline — SKIPPED (Notion unavailable)
```

### Step 4: Offer Fallbacks

For each skipped phase, suggest what the user can do manually:

| Unavailable | Fallback |
|-------------|----------|
| Notion MCP | "Run `/sync-notion` later when Notion is accessible" |
| OpenAlex MCP | "Use `/literature` with web search mode instead" |
| Scholarly MCP | "Use `/literature` with web search mode instead" |

### Step 5: Summarize at End

Close with a clean summary of what completed vs. what was skipped:

```
Completed: Steps 1-4 (local context updates)
Skipped: Step 5 (Notion sync — server unavailable)
Action needed: Run `/sync-notion` when Notion is back
```

## MCP-Consuming Skills

These skills should reference this pattern:

| Skill | MCP Server | What depends on it |
|-------|------------|-------------------|
| `sync-notion` | Notion | Steps 3, 5 (search + update) |
| `task-management` | Notion | Daily planning, task creation, pipeline queries |
| `init-project-research` | Notion | Pipeline entry creation |
| `literature` | OpenAlex, Scholarly | Citation search, DOI verification |
| `audit-research-projects` | Notion | Pipeline cross-reference |

## When to Apply

- Always when a skill's workflow includes MCP tool calls
- Especially in background agents (where MCP tools may auto-deny due to permission constraints)
- When network issues are suspected (slow responses, recent timeouts)

## When to Skip

- Skills that don't use MCP tools
- When the user explicitly says "skip Notion" or "offline mode"
- Interactive sessions where the user can retry immediately
