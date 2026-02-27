# Scripts & CLI Tools

Quick reference for command-line tools in your task management system.

## Overview

| Command | Purpose |
|---------|---------|
| `task "..."` | Create a task |
| `tasks` | List tasks |
| `done "..."` | Mark task done |
| `focus "..."` | Update current focus |
| `papers` | Show research pipeline |
| `inbox` | Tasks needing dates |
| `week` | Weekly summary |
| `conf` | Conference deadlines |
| `query "..."` | Search files + Notion |

## Setup (one time)

### Option A: Using .env file (recommended)

1. **Get a Notion token:** https://www.notion.so/my-integrations
2. **Add token to `.env`** (already created):
   ```bash
   export NOTION_TOKEN="your-token-here"
   ```
3. **Run scripts with uv:**
   ```bash
   cd "Task Management"
   uv run python .scripts/tasks
   ```

### Option B: Add to PATH

1. **Add to `~/.zshrc`:**
   ```bash
   export PATH="$PATH:$HOME/path/to/Task Management/.scripts"
   source "$HOME/path/to/Task Management/.env"
   ```
2. **Reload:** `source ~/.zshrc`

### For both options

**Share databases** with your integration in Notion (Tasks Tracker + Research Pipeline)

---

## task — Create Tasks

Creates tasks with **Inbox** status by default (GTD-style capture).

```bash
task "Review paper feedback"                           # basic (goes to Inbox)
task "Email supervisor" -p "Paper Revision"            # with project
task "Submit paper" --priority high                    # with priority
task "Read Smith 2024" -d friday                       # due Friday
task "Follow up" -s "Meeting"                          # from meeting
task "Exercise" -a personal                            # with area
task --list-projects                                   # show projects
```

| Flag | Description |
|------|-------------|
| `-p, --project` | Project name |
| `-a, --area` | Area: research, teaching, career, personal, health, learning |
| `--priority` | high, medium, low |
| `-d, --due` | Due date (today, tomorrow, friday, 2024-03-15) |
| `-s, --source` | Meeting, Email, Supervisor request, etc. |
| `--desc` | Additional description |

---

## tasks — Query Tasks

```bash
tasks                        # all active tasks
tasks --overdue              # overdue only
tasks --today                # due today
tasks -p "Paper Revision"    # filter by project
tasks --priority high        # filter by priority
tasks --all                  # include completed
```

| Flag | Description |
|------|-------------|
| `--overdue` | Show overdue tasks |
| `--today` | Show tasks due today |
| `-p, --project` | Filter by project |
| `--priority` | Filter by priority |
| `--status` | Filter by status |
| `--all` | Include completed tasks |

---

## done — Complete Tasks

```bash
done "paper feedback"        # mark matching task as done
done --list                  # show tasks to choose from
```

If multiple tasks match, you'll be prompted to choose.

---

## focus — Update Current Focus

```bash
focus "Working on paper section 4"         # what you're working on
focus --left-off "Finished draft"          # where you left off
focus --next "Review with supervisor"      # add next step
focus --question "Check methodology?"      # add open question
focus --show                               # show current focus
focus --clear                              # start fresh
```

Updates `.context/current-focus.md` directly.

---

## papers — Research Pipeline

```bash
papers                              # show all papers
papers --active                     # show papers in progress
papers --update "Paper A" "R&R"     # update paper stage
papers --stages                     # list available stages
```

**Stages:** Idea > Literature Review > Drafting > Internal Review > Submitted > Under Review > R&R > Revising > Accepted > Published

---

## inbox — Tasks Without Dates

```bash
inbox                   # show inbox tasks
inbox --assign          # interactively assign due dates
```

**Shortcuts in assign mode:**
- `t` = today
- `tm` = tomorrow
- `w` = +1 week
- `m` = +1 month
- `fri` = next Friday
- `s` = skip
- `q` = quit

---

## week — Weekly Summary

```bash
week              # this week's summary
week --last       # last week's summary
```

Shows: completed, due this week, overdue, in progress.

---

## conf — Conference Tracking

```bash
conf                    # show upcoming deadlines
conf --search           # open Google CFP search links in browser
conf --add              # interactively add a conference
conf --remind           # weekly reminder checklist
conf --deadlines        # show all deadlines
conf --all              # include past conferences
conf --topics           # list available topics
```

**Weekly routine:**
1. Run `conf --remind` on Mondays
2. Run `conf --search` to find new conferences
3. Add with `conf --add`

---

## query — Search Everything

```bash
query "game theory"              # search files + Notion
query --files "topic"            # search only context files
query --notion "keyword"         # search only Notion
query --papers "collaboration"   # search Research Pipeline
query --tasks "meeting"          # search Tasks Tracker
query --conferences "deadline"   # search Conferences
```

| Flag | Description |
|------|-------------|
| `--files` | Search only local context files |
| `--notion` | Search only Notion |
| `--papers` | Search Research Pipeline database |
| `--tasks` | Search Tasks Tracker database |
| `--conferences` | Search Conferences database |

---

## How It Works

All scripts are Python CLI tools in `.scripts/` that talk to the Notion API:

| File | Type | Purpose |
|------|------|---------|
| `task` | CLI tool | Create tasks |
| `tasks` | CLI tool | Query tasks |
| `done` | CLI tool | Complete tasks |
| `focus` | CLI tool | Update current focus |
| `papers` | CLI tool | Research pipeline |
| `inbox` | CLI tool | Inbox management |
| `week` | CLI tool | Weekly summary |
| `conf` | CLI tool | Conference tracking |
| `query` | CLI tool | Cross-system search |
| `config.py` | Helper | Database IDs, project lists, constants |
| `notion_helpers.py` | Helper | Notion API utilities, project inference |
| `daily_digest.py` | Helper | Daily digest generation |
| `extract_meeting_actions.py` | Helper | Meeting transcript action extraction |
| `openalex/` | Library | OpenAlex API client for scholarly search |

## Configuration

### `config.py`

The central configuration file contains:

- **Database IDs** — Notion database and page IDs for your workspace
- **Projects list** — Project names for task categorisation (keep in sync with `.context/projects/_index.md`)
- **Universities list** — Institutions for task tagging
- **Source types, priorities, statuses** — Dropdown values matching your Notion schema

### `notion_helpers.py`

Shared utilities including:

- **Task formatting** — Converts CLI arguments to Notion API properties
- **Deadline parsing** — Natural language dates ("friday", "end of month")
- **Project inference** — Keyword and people-based project matching
- **Priority inference** — Context-aware priority assignment
- **Action extraction** — Regex-based meeting transcript parsing

## Extending

### Adding a new CLI tool

1. Create a Python file in `.scripts/` (no `.py` extension for CLI commands)
2. Add a shebang: `#!/usr/bin/env python3`
3. Import from `config.py` and `notion_helpers.py`
4. Use `argparse` for flags
5. Make executable: `chmod +x .scripts/your-tool`

### Customising for your workspace

1. Update database IDs in `config.py` to match your Notion workspace
2. Update the `PROJECTS` list to match your project names
3. Update `project_keywords` and `people_projects` in `notion_helpers.py` for auto-categorisation
4. Update `SEARCH_KEYWORDS` and `TOPICS` in `conf` for conference tracking

## Date Formats

| Input | Result |
|-------|--------|
| `today` | Today's date |
| `tomorrow` | Tomorrow |
| `monday` | Next Monday |
| `friday` | Next Friday |
| `2024-03-15` | Specific date |
| `15/03/2024` | UK format |

## Areas of Responsibility

| Area | Description |
|------|-------------|
| Research | Papers, conferences, supervision |
| Teaching | Course prep, marking |
| Career | Applications, networking |
| Personal | Admin, finance, relationships |
| Health | Medical, fitness, wellbeing |
| Learning | Courses, certifications |

## Troubleshooting

### "NOTION_TOKEN not set"
```bash
export NOTION_TOKEN="your-token-here"
```

### "command not found"
```bash
export PATH="$PATH:$HOME/path/to/Task Management/.scripts"
```

### "Error 401/404"
Make sure your Notion integration has access to:
- Tasks Tracker database
- Research Pipeline database
- Conferences database

(In Notion: ... > Connections > Add integration)
