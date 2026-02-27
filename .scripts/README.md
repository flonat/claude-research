# Automation Scripts

> Python utilities for task management automation, designed to work with Claude/Cowork.

## Overview

### CLI Tools

| Script | Purpose |
|--------|---------|
| `task` | Create a new task in Notion |
| `tasks` | Query and list tasks |
| `done` | Mark tasks as completed |
| `focus` | Update current focus file |
| `papers` | Research pipeline management |
| `inbox` | Process tasks without dates |
| `week` | Weekly summary |
| `conf` | Conference tracking |
| `query` | Search context files and Notion |

### Helper Modules

| Script | Purpose |
|--------|---------|
| `config.py` | Configuration (auto-loads `.env` for Notion token) |
| `notion_helpers.py` | Utility functions for Notion operations |
| `extract_meeting_actions.py` | Extract action items from meeting transcripts |
| `daily_digest.py` | Generate daily planning briefings |

### Shared Libraries

| Directory | Purpose |
|-----------|---------|
| `openalex/` | OpenAlex scholarly API client — shared across `/literature`, `/validate-bib`, `/split-pdf`, and the OpenAlex MCP server |

## How They Work with Claude

These scripts are designed for **Claude-assisted automation**, not fully autonomous execution. When you ask Claude to help with tasks like:

- "Help me plan my day"
- "Extract action items from yesterday's meeting"
- "What tasks are overdue?"

Claude uses these scripts as reference for:
1. **What to query** from Notion
2. **How to format** results
3. **What questions** to ask you
4. **How to create** new tasks

## Configuration

### 1. Notion Integration

The scripts auto-load the `.env` file from the project root.

**Option A: Use .env (recommended)**
```bash
# .env file already exists with your token
cd "Task Management"
uv run python .scripts/tasks
```

**Option B: Environment variable**
```bash
export NOTION_TOKEN="your-token-here"
```

**Option C: Source .env manually**
```bash
source .env
python .scripts/tasks
```

Make sure to share your databases with the integration in Notion.

### 2. Database IDs

The `config.py` file contains your database IDs:

```python
DATABASES = {
    "tasks_tracker": "YOUR-TASKS-DATABASE-ID-HERE",
    "research_pipeline": "YOUR-PIPELINE-DATABASE-ID-HERE",
}
```

## Usage

### With Claude/Cowork (Recommended)

Just ask Claude naturally:

```
"Help me plan my day"
→ Claude reads context, queries Notion, asks you questions, creates a plan

"Extract actions from my meeting with [Supervisor] yesterday"
→ Claude finds the transcript, extracts actions, creates tasks

"What's overdue?"
→ Claude queries Tasks Tracker and summarises
```

### Standalone (Advanced)

```bash
# Daily digest
python daily_digest.py --date "2026-01-29"

# Meeting actions (dry run)
python extract_meeting_actions.py --dry-run

# Show Claude instructions
python daily_digest.py --instructions
```

## Extending

### Adding a New Workflow

1. Create a new script in `.scripts/`
2. Add a corresponding workflow file in `.context/workflows/`
3. Document how Claude should use it

### Adding New Task Types

Edit `config.py`:
```python
TASK_TYPES = [
    # ... existing types
    "🆕 New Type",
]
```

Then update the Notion database to include the new option.

## Troubleshooting

### "NOTION_TOKEN not set"
The scripts work best with Claude's built-in Notion integration. For standalone use, you need to set up a Notion integration token.

### Tasks not appearing
Make sure:
1. The database is shared with your Notion integration
2. The database IDs in `config.py` match your actual databases

### Claude doesn't follow the workflow
Point Claude to the specific workflow file:
```
"Read .context/workflows/daily-review.md and help me plan my day"
```

## Files Changed

When running these scripts or using the workflows, the following may be updated:

- `.context/current-focus.md` - Updated after planning sessions
- Notion Tasks Tracker - New tasks created
- Notion Research Pipeline - Paper status updates
