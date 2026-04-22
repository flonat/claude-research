---
name: python-env
description: "Use when you need Python environment management with uv (install, create venv, manage deps)."
allowed-tools: Bash(uv*), Bash(python*), Bash(mkdir*), Bash(ls*)
---

# Python Environment Management

**CRITICAL RULE: Never use `pip` directly. Always use `uv`.** This applies to all Python package management.

## Golden Rule

**ALWAYS use `uv` for Python package and environment management. Never use `pip` directly.**

## Commands

| Task | Command |
|------|---------|
| Create venv | `uv venv` |
| Install package | `uv pip install <package>` |
| Install from requirements | `uv pip install -r requirements.txt` |
| Run script in project | `uv run python script.py` |
| Run with dependencies | `uv run --with pandas python script.py` |
| Install CLI tool globally | `uv tool install <tool>` |
| Sync project deps | `uv sync` |
| Add dependency | `uv add <package>` |

## Project Setup

For new projects:
```bash
uv init
uv add <dependencies>
uv sync
```

For existing projects with `pyproject.toml`:
```bash
uv sync
uv run python main.py
```

## Rules

1. **Never use `pip install`** — always `uv pip install` or `uv add`
2. **Never install globally** — use `uv tool install` for CLI tools
3. **Always work in a venv** — created by `uv venv` or `uv sync`
4. **Use `uv run`** — to execute scripts within the project environment

## This Project

The Task Management system uses uv:
```bash
cd "Task Management"
uv sync                           # Install dependencies
uv run python .scripts/tasks      # Run CLI tools
```

## On your HPC cluster HPC

Avon uses **Miniconda3 + Lmod** (not uv) because cluster users need to compose with `module load CUDA/12.6.0` and other pre-built modules. The project-specific pattern is `hpc/env-setup.sh` (conda create + pip install) — see [`docs/guides/hpc.md`](../../docs/guides/hpc.md) and reference implementations under `Projects/[your-project]/hpc/env-setup.sh`. The local dev env still uses uv; HPC gets its own conda env with identical pins. Don't try to port uv to Avon — the module system assumes conda.
