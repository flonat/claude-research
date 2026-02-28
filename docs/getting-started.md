<!-- Governed by: skills/shared/project-documentation.md -->

# Getting Started

## Claude Code vs Claude Desktop

- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** — the terminal-based agentic coding tool. This is the engine that reads CLAUDE.md, runs skills, and executes hooks. It's what this entire system is built around.
- **[Claude Desktop](https://claude.ai/download)** — the GUI chat app. Optional but useful. With the included MCP server, it can access the same context library and skills.

Both require an Anthropic account with a Claude subscription.

## Prerequisites

Install a **package manager** first — it makes installing everything else easy:

- **macOS/Linux:** [Homebrew](https://brew.sh/) — run `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- **Windows:** [WinGet](https://learn.microsoft.com/en-us/windows/package-manager/winget/) (built into Windows 11) or [Scoop](https://scoop.sh/)

Then install these tools:

| Tool | What it's for | macOS (brew) | Windows | Linux |
|------|--------------|-------------|---------|-------|
| [Claude Code](https://code.claude.com/docs/en/setup) | The CLI that powers everything | `curl -fsSL https://claude.ai/install.sh \| bash` | `winget install Anthropic.ClaudeCode` | `curl -fsSL https://claude.ai/install.sh \| bash` |
| [Git](https://git-scm.com/) | Version control | Included on macOS | `winget install Git.Git` | `sudo apt install git` |
| [uv](https://docs.astral.sh/uv/) | Python package management | `brew install uv` | `winget install astral-sh.uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| [TeX Live](https://tug.org/texlive/) | LaTeX distribution for paper compilation | `brew install --cask mactex` | [install guide](https://tug.org/texlive/windows.html) | `sudo apt install texlive-full` |
| [VS Code](https://code.visualstudio.com/) | Recommended editor (lightweight, cross-platform) | `brew install --cask visual-studio-code` | `winget install Microsoft.VisualStudioCode` | [install guide](https://code.visualstudio.com/docs/setup/linux) |

**VS Code extensions:**
- [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop) — syntax highlighting, compilation, and PDF preview. VS Code is recommended over heavier LaTeX editors (TeXstudio, Overleaf desktop) because it's low-resource and handles both code and LaTeX in one window.
- **Markdown editing** — VS Code handles `.md` files natively with preview (`Cmd+Shift+V` / `Ctrl+Shift+V`). For a dedicated writing experience, consider [Typora](https://typora.io/) or [Obsidian](https://obsidian.md/).

**[Notion](https://www.notion.so/)** — used for task management and research pipeline tracking. Enable the Claude.ai managed Notion integration in the web UI (no self-hosted server needed). See [`docs/notion-setup.md`](notion-setup.md) for the full setup guide.

## Installation

```bash
git clone https://github.com/flonat/claude-code-flonat.git
cd claude-code-flonat
./scripts/setup.sh
```

The setup script creates symlinks so Claude Code can find your skills, agents, hooks, and rules from any project directory.

## Customise Your Context

Edit these files with your own details:

- `.context/profile.md` — Your name, institution, research areas, supervisors
- `.context/current-focus.md` — What you're working on right now
- `.context/projects/_index.md` — Your active research projects
- `CLAUDE.md` — Conventions and tool preferences

## Configure Settings

Edit `.claude/settings.json` to adjust:
- Allowed/denied commands
- Hook configuration
- Model preferences

## Start Using It

```bash
cd ~/your-research-project
claude
```

Claude will automatically load your context, skills, and rules. Try:

- "Plan my day" — Daily planning with Notion task queries
- "Extract actions from my meeting" — Turn transcripts into Notion tasks
- `/proofread` — Academic proofreading for a LaTeX paper
- `/latex-autofix` — Compile LaTeX with automatic error fixing
- `/validate-bib` — Check citation keys against your `.bib` file
- `/literature` — Search for academic papers and manage bibliography
- `/session-recap` — End-of-session checklist (update focus, log, sync)
- `/code-review` — 11-category quality review for R/Python scripts

## Adding a New Research Project

1. Create a directory for your project
2. Add a `CLAUDE.md` in the project with project-specific instructions
3. Symlink `paper/` to your Overleaf directory (if applicable)
4. Add the project to `.context/projects/_index.md`
5. Create a paper file in `.context/projects/papers/`

## Adding Your Own Skills

Create a new directory in `skills/` with a `SKILL.md` file:

```
skills/my-custom-skill/
└── SKILL.md
```

The `SKILL.md` needs YAML frontmatter with `name`, `description`, and optionally `allowed-tools`. See any existing skill for the format.
