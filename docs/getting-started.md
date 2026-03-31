<!-- Governed by: skills/shared/project-documentation.md -->

# Getting Started

## How to Use Claude Code

Claude Code is the AI engine that reads your CLAUDE.md, runs skills, and executes hooks. You can access it in several ways:

| Interface | Best for | Install |
|-----------|----------|---------|
| **[Terminal CLI](https://docs.anthropic.com/en/docs/claude-code)** | Power users, full control, scripting | See install table below |
| **[VS Code extension](https://marketplace.visualstudio.com/items?itemName=anthropics.claude-code)** | Integrated coding + chat in one window | Install from VS Code marketplace |
| **[JetBrains extension](https://plugins.jetbrains.com/plugin/27189-claude-code)** | IntelliJ, PyCharm, WebStorm users | Install from JetBrains marketplace |
| **[Web app](https://claude.ai/code)** | Quick access from any browser, no install | Visit claude.ai/code |
| **[Desktop app](https://claude.ai/download)** | GUI chat (Mac/Windows) | Download from claude.ai |

All interfaces share the same skills, agents, hooks, and rules once you run the setup script. The terminal CLI is the most full-featured and what this guide focuses on, but you can use whichever interface suits your workflow.

**You need an Anthropic account with a Claude subscription** (Max plan recommended for heavy research use).

## Prerequisites

### 1. Package Manager

Install a package manager first — it makes installing everything else easy:

| Platform | Package manager | Install command |
|----------|----------------|-----------------|
| **macOS** | [Homebrew](https://brew.sh/) | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| **Ubuntu / Debian** | apt | Already included |
| **Fedora / RHEL** | dnf | Already included |
| **Arch** | pacman | Already included |
| **Windows** | [WinGet](https://learn.microsoft.com/en-us/windows/package-manager/winget/) | Built into Windows 11. On Windows 10, install [App Installer](https://apps.microsoft.com/detail/9nblggh4nns1) from the Microsoft Store. |

### 2. Python (3.11 or later)

Python is required for several hooks (context monitor, compact save/restore) and the bibliography MCP server.

| Platform | Install command | Verify |
|----------|----------------|--------|
| **macOS** | `brew install python@3.12` | `python3 --version` |
| **Ubuntu 24.04+** | `sudo apt install python3.12 python3.12-venv` | `python3 --version` |
| **Ubuntu 22.04 / Debian 11** | See note below | `python3 --version` |
| **Fedora 39+** | `sudo dnf install python3.12` | `python3 --version` |
| **Arch** | `sudo pacman -S python` (ships 3.12+) | `python3 --version` |
| **Windows** | `winget install Python.Python.3.12` | `python --version` |

> **Why Python 3.11+?** The hooks and MCP servers use modern Python features (`tomllib`, `match` statements, type hints) that require 3.11 or later. Python 3.12 is recommended as the current stable release.

> **Ubuntu 22.04 / Debian 11:** These ship Python 3.10, which is too old. Add the [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) first:
> ```bash
> sudo add-apt-repository ppa:deadsnakes/ppa
> sudo apt update
> sudo apt install python3.12 python3.12-venv
> ```

> **Windows note:** The Windows Python installer adds `python` (not `python3`) to your PATH. The hooks in `settings.json` reference `python3` — you may need to adjust these to `python` on Windows, or create an alias. See the [Windows Setup](#windows-setup) section below.

### 3. uv (Python package manager)

| Platform | Install command | Verify |
|----------|----------------|--------|
| **macOS** | `brew install uv` | `uv --version` |
| **Linux** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `uv --version` |
| **Windows** | `winget install astral-sh.uv` | `uv --version` |

> **Why uv instead of pip?** [uv](https://docs.astral.sh/uv/) is a fast Python package manager that handles virtual environments automatically. When Claude runs Python code or installs dependencies, it uses `uv run python` and `uv pip install` instead of bare `python` or `pip`. This prevents conflicts between projects (each gets its own isolated environment) and avoids polluting your system Python. The `settings.json` included with this repo enforces this by blocking bare `python` and `pip` commands.

### 4. Other tools

| Tool | What it's for | macOS | Ubuntu/Debian | Fedora | Arch | Windows |
|------|--------------|-------|---------------|--------|------|---------|
| [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) | The engine | `curl -fsSL https://claude.ai/install.sh \| bash` | same | same | same | `winget install Anthropic.ClaudeCode` |
| [Git](https://git-scm.com/) | Version control | Included | `sudo apt install git` | `sudo dnf install git` | `sudo pacman -S git` | `winget install Git.Git` |
| [TeX Live](https://tug.org/texlive/) | LaTeX compilation | `brew install --cask mactex` | `sudo apt install texlive-full` | `sudo dnf install texlive-scheme-full` | `sudo pacman -S texlive` | [install guide](https://tug.org/texlive/windows.html) |

**Optional but recommended:**
- [VS Code](https://code.visualstudio.com/) with the [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop) extension — handles both code and LaTeX in one window
- [Obsidian](https://obsidian.md/) — for browsing and editing the Research Vault

> **TeX Live on Windows:** The [TeX Live install guide](https://tug.org/texlive/windows.html) walks you through the installer. Alternatively, install [MiKTeX](https://miktex.org/download) which auto-installs missing packages on first use. Either works — just make sure `latexmk` is available in your terminal after installation.

> **TeX Live on Arch:** The `texlive` group installs a minimal set. For full coverage (recommended), use `sudo pacman -S texlive-most texlive-lang`.

## Installation

### macOS / Linux

```bash
git clone https://github.com/flonat/claude-research.git
cd claude-research
./scripts/setup.sh
```

### Windows

Open **PowerShell** (not Command Prompt) and run:

```powershell
git clone https://github.com/flonat/claude-research.git
cd claude-research
.\scripts\setup.ps1
```

> **If you get an execution policy error:** Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` first, then retry. This allows PowerShell to run local scripts.

The setup script creates links in `~/.claude/` so Claude Code can find your skills, agents, hooks, and rules from any project directory.

### What the setup script does

1. Creates `~/.claude/` if it doesn't exist
2. Links `skills/`, `agents/`, `rules/`, and `hooks/` into `~/.claude/`
3. Copies `settings.json` (first install only — preserved on updates)
4. Checks that Python, uv, Git, and LaTeX are installed
5. Creates `log/` directories for session continuity

## Linux Notes

Linux is the most straightforward platform — hooks run natively and paths work out of the box. A few things to check:

### Hook permissions

After cloning, make sure hook scripts are executable:

```bash
chmod +x hooks/*.sh hooks/*.py
```

The setup script handles this, but if you copy files manually or reset permissions, hooks will silently fail without `+x`.

### Python version

Many distros ship an older Python as the system default. Check with `python3 --version`. If it's below 3.11, install a newer version alongside it (the deadsnakes PPA on Ubuntu, or your distro's package for Python 3.12). The system Python is untouched — uv manages its own environments.

### `~/.claude/` location

On Linux, `~` resolves to `/home/youruser/`. Claude Code looks for `~/.claude/` there. If you use a non-standard `$HOME`, verify the symlinks point correctly after setup.

## Windows Setup

Windows works well with Claude Code but needs a few adjustments:

### Shell hooks

The `.sh` hook scripts require a Unix-like shell. Two options:

1. **Git Bash (recommended):** Installed automatically with Git for Windows. Claude Code can use Git Bash to run `.sh` scripts. Make sure Git Bash is in your PATH (the Git installer does this by default).

2. **WSL (Windows Subsystem for Linux):** If you prefer a full Linux environment, [install WSL](https://learn.microsoft.com/en-us/windows/wsl/install) with `wsl --install`. You can then run the Linux setup inside WSL.

### Python command name

Windows installs Python as `python` (not `python3`). The hook configuration in `settings.json` uses `python3`. You have two options:

**Option A — Create a `python3` alias** (recommended):
```powershell
# Find where python.exe is
where python
# Create a copy named python3.exe in the same directory
Copy-Item (Get-Command python).Source ((Get-Command python).Source -replace 'python\.exe','python3.exe')
```

**Option B — Edit `settings.json`** to replace `python3` with `python`:
Open `~/.claude/settings.json` and replace every occurrence of `"python3 "` with `"python "` in the hooks section.

### Path separators

Claude Code handles path separators automatically. You don't need to change `/` to `\` in any configuration files.

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

- "Plan my day" — Daily planning with task queries
- "Extract actions from my meeting" — Turn transcripts into tasks
- `/proofread` — Academic proofreading for a LaTeX paper
- `/latex-autofix` — Compile LaTeX with automatic error fixing
- `/bib-validate` — Check citation keys against your `.bib` file
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

## Troubleshooting

### "uv: command not found"

uv isn't installed or isn't in your PATH. Install it using the commands in the [uv section](#3-uv-python-package-manager) above, then restart your terminal.

### "python3: command not found" (Windows)

Windows uses `python` instead of `python3`. See the [Python command name](#python-command-name) section above.

### Hooks not running

1. Check that `~/.claude/settings.json` exists and contains the `"hooks"` section
2. Verify the hook files are executable: `ls -la ~/.claude/hooks/` (macOS/Linux) or check they exist in `%USERPROFILE%\.claude\hooks\` (Windows)
3. On Windows, ensure Git Bash is in your PATH for `.sh` hooks

### LaTeX skills fail with "latexmk not found"

Install a TeX distribution — see the [Other tools](#4-other-tools) section. After installing, restart your terminal so `latexmk` is in your PATH.

### "Execution policy" error on Windows

Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` in PowerShell, then retry the setup script.
