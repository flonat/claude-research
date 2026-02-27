# System Architecture

> How the components fit together.

## Directory Structure

```
claude-code-flonat/
├── CLAUDE.md                         # Main instruction file
├── README.md                         # Setup guide
├── MEMORY.md                         # Accumulated knowledge
├── .gitignore
│
├── .claude/
│   ├── agents/                       # 6 specialised review agents
│   │   ├── referee2-reviewer.md
│   │   ├── peer-reviewer.md
│   │   ├── proposal-reviewer.md
│   │   ├── paper-critic.md
│   │   ├── domain-reviewer.md
│   │   └── fixer.md
│   ├── rules/                        # 9 auto-loaded policy rules
│   │   ├── plan-first.md
│   │   ├── scope-discipline.md
│   │   ├── learn-tags.md
│   │   ├── read-docs-first.md
│   │   ├── lean-claude-md.md
│   │   ├── overleaf-separation.md
│   │   ├── ignore-agents-md.md
│   │   ├── ignore-gemini-md.md
│   │   └── design-before-results.md
│   └── settings.json                 # Permissions, hooks, model config
│
├── skills/                           # 30 slash commands
│   ├── shared/                       # Shared utilities
│   │   ├── palettes.md
│   │   ├── quality-scoring.md
│   │   └── rhetoric-principles.md
│   ├── proofread/
│   ├── latex-autofix/
│   ├── literature/
│   └── ...
│
├── hooks/                            # 8 automated guardrails
│   ├── block-destructive-git.sh
│   ├── context-monitor.py
│   ├── postcompact-restore.py
│   ├── precompact-autosave.py
│   ├── promise-checker.sh
│   ├── protect-source-files.sh
│   ├── resume-context-loader.sh
│   └── startup-context-loader.sh
│
├── .context/                         # AI context library
│   ├── profile.md                    # Your identity and background
│   ├── current-focus.md              # What you're working on NOW
│   ├── projects/
│   │   ├── _index.md                 # All projects overview
│   │   └── papers/                   # Individual paper metadata
│   ├── preferences/
│   │   ├── priorities.md             # Priority framework
│   │   └── task-naming.md            # Task naming conventions
│   ├── workflows/                    # Process guides
│   │   ├── daily-review.md
│   │   ├── weekly-review.md
│   │   ├── meeting-actions.md
│   │   └── replication-protocol.md
│   └── resources/                    # Reference data
│       ├── journal-rankings.md
│       └── conference-rankings.md
│
├── .mcp-server-openalex/             # OpenAlex scholarly search
│   ├── server.py
│   ├── formatters.py
│   ├── pyproject.toml
│   └── uv.lock
│
├── docs/                             # Documentation
│   ├── system.md                     # This file
│   ├── skills.md
│   ├── agents.md
│   ├── hooks.md
│   └── rules.md
│
├── log/                              # Session logs
│   ├── .gitkeep
│   └── plans/                        # Saved plans
│       └── .gitkeep
│
└── scripts/
    └── setup.sh                      # Initial setup script
```

## Symlink Architecture

The `setup.sh` script creates four symlinks in `~/.claude/`:

```
~/.claude/skills/  → <repo>/skills/
~/.claude/agents/  → <repo>/.claude/agents/
~/.claude/rules/   → <repo>/.claude/rules/
~/.claude/hooks/   → <repo>/hooks/
```

This makes all components globally available from any project directory.

## How Components Interact

```
Session Start
    │
    ├── startup-context-loader.sh  →  Reads .context/ files
    │                                  Outputs to Claude as additionalContext
    │
    ├── Rules loaded                →  All 9 rules active
    │
    └── Claude ready
         │
         ├── User: "/proofread"    →  Skill invoked (same session)
         │
         ├── User: "Review paper"  →  Agent launched (separate context via Task tool)
         │
         ├── Claude: "git push -f" →  block-destructive-git.sh BLOCKS
         │
         ├── Claude uses Bash      →  context-monitor.py tracks usage
         │
         ├── Context compression   →  precompact-autosave.py saves state
         │                             postcompact-restore.py restores state
         │
         └── Session ends          →  promise-checker.sh verifies claims
```

## Configuration

All configuration lives in `~/.claude/settings.json`:

- **`permissions.allow`**: Commands Claude can run without prompting
- **`permissions.deny`**: Commands that are always blocked (bare python/pip)
- **`hooks`**: Which scripts run at which events
- **`model`**: Default model preference

## Extending the System

### Adding a new skill
1. Create `skills/my-skill/SKILL.md`
2. Available immediately as `/my-skill`

### Adding a new agent
1. Create `.claude/agents/my-agent.md`
2. Available immediately via Task tool

### Adding a new hook
1. Create script in `hooks/`
2. Make executable: `chmod +x hooks/my-hook.sh`
3. Add to `~/.claude/settings.json`

### Adding a new rule
1. Create `.claude/rules/my-rule.md`
2. Auto-loaded in every session
