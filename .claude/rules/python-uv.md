---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/requirements*.txt"
  - "**/*.ipynb"
  - "**/uv.lock"
---

# Rule: Always Use uv for Python

## Principle

**Never use bare `python`, `python3`, or `pip`.** All Python execution and package management goes through `uv`.

## Commands

| Instead of | Use |
|-----------|-----|
| `python script.py` | `uv run python script.py` |
| `pip install pkg` | `uv pip install pkg` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `python -m pytest` | `uv run python -m pytest` |
| `python -m venv .venv` | `uv venv` |

## When This Applies

- Every project, every session — no exceptions
- Both interactive commands and scripts
- Both Task Management and research projects

## Why This Matters

All projects use uv-managed virtual environments. Bare `python` or `pip` may resolve to the system Python or the wrong venv, causing silent dependency mismatches.
