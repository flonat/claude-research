<!-- Governed by: skills/shared/project-documentation.md -->

# Notion Integration Setup

The task management system uses **two Notion databases** to track your work:

1. **Tasks Tracker** — individual tasks with status, priority, due dates, and project links
2. **Research Pipeline** — paper-level tracking with stages (Idea → Literature Review → Drafting → Submitted → R&R → Published), target journals, and co-authors

Together with the local context library (`.context/`), these create a hybrid system: Notion handles dynamic task data, while local files handle persistent context that Claude reads every session.

## How It Works

```
You say "plan my day"
        │
        ▼
Claude reads .context/current-focus.md     ← what you're working on
Claude reads .context/workflows/daily-review.md  ← how to help you plan
Claude queries Notion Tasks Tracker        ← overdue/due today/high priority
        │
        ▼
Claude asks orientation questions           ← energy, commitments, yesterday's work
        │
        ▼
Claude helps you prioritise                 ← based on your answers + context
        │
        ▼
Claude updates .context/current-focus.md   ← so next session picks up where you left off
```

## Available Workflows

| You say | What happens |
|---------|-------------|
| "Plan my day" | Reads context, queries Notion for tasks, asks questions, creates a plan |
| "What should I work on?" | Reviews priorities and helps you decide |
| "Extract actions from my meeting" | Finds transcript, extracts tasks, creates them in Notion |
| "Weekly review" | Guides reflection: what got done, what didn't, what emerged, next week's Big 3 |
| "What's overdue?" | Queries Notion and summarises |
| "Update my research pipeline" | Shows paper status, helps update stages and target journals |
| "Sync this project" (`/sync-notion`) | Propagates project state: CLAUDE.md → context library → Notion |

## Step 1: Enable the Notion MCP

The Notion integration uses **Claude.ai's managed Notion integration** — a built-in MCP server that Claude Code can connect to. No self-hosted server needed.

1. Go to [claude.ai/settings/integrations](https://claude.ai/settings/integrations)
2. Connect your Notion workspace
3. Grant access to the pages/databases Claude should see

Once connected, Claude Code automatically has access to Notion tools (`notion-search`, `notion-fetch`, `notion-create-pages`, `notion-update-page`, etc.).

## Step 2: Create the Databases

You need two Notion databases. Create them anywhere in your workspace.

**Tasks Tracker** — for individual tasks:

| Property | Type | Purpose |
|----------|------|---------|
| Task name | Title | Action verb + specific object (e.g., "Draft methods section") |
| Status | Select | Not started, In progress, Done |
| Priority | Select | High, Medium, Low |
| Due date | Date | When it's due |
| Project | Select | Which research project this belongs to |
| Source | Select | Meeting, Email, Supervisor request, Self-initiated |
| Task type | Select | Writing, Reading, Research, Meeting, Admin, Communication |

**Research Pipeline** — for paper-level tracking:

| Property | Type | Purpose |
|----------|------|---------|
| Paper name | Title | Working title of the paper |
| Stage | Select | Idea, Literature Review, Drafting, Data Collection, Analysis, Submitted, R&R, Published |
| Target Journal | Rich text | Where you plan to submit |
| Co-authors | Rich text | Collaborators |
| Priority | Select | High, Medium, Low |
| Status | Rich text | Brief status note |

## Step 3: Add Database IDs to CLAUDE.md

1. Open each database in Notion
2. Copy the database ID from the URL (the 32-character hex string after your workspace name: `notion.so/workspace/DATABASE_ID_HERE?v=...`)
3. Add them to `CLAUDE.md`:

```markdown
## Notion Databases

| Database | ID |
|----------|-----|
| Tasks Tracker | `your-tasks-database-id-here` |
| Research Pipeline | `your-pipeline-database-id-here` |
```

Claude reads these IDs from `CLAUDE.md` and uses them to query and update your databases.

## Step 4: Start Using It

```bash
claude
> Plan my day
```

Claude will read your context, query Notion, ask you orientation questions, and help you prioritise.

## Graceful Degradation

If the Notion MCP is unavailable (not connected, network issues), skills automatically fall back to local-only mode — they still read `.context/` files and help you plan, they just can't query or update Notion. You'll see a note when this happens.
