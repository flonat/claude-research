# Phase 2.9: Recognised Growth Patterns

> Detailed check for `/audit-project-research` Phase 2.9.

Projects naturally grow beyond the initial scaffold. These are documented in `/init-project-research` as expected additions:

| Pattern | Recognized as |
|---------|---------------|
| `experiments/` | Experiment configs, sweep logs, results |
| `experiments/configs/` | Parameter sweep definitions |
| `scripts/` | Utility scripts (data processing, plotting) |
| `legacy/` | Preserved old code/data (per `/project-safety`) |
| `correspondence/referee-reviews/<venue>-roundN/` | Reviewer comments, rebuttal, analysis per R&R round |
| `correspondence/referee-reviews/<venue>-roundN/analysis/` | Comment tracker, review analyses, verbatim tex |
| `docs/<venue>/internal-reviews/` | Internal review work (referee2 agent reports) |
| `docs/venues/<venue>/camera-ready/` | Final accepted version |
| `notes.md` | Quick research notes, meeting summaries |
| `SETUP.md` | Environment setup instructions |
| `pyproject.toml` | Python package management |
| `.venv/` | Virtual environment |
| `.planning/` | Project-level roadmap and state tracking (from `/init-project-orchestration`) |
| `.planning/roadmap.md` | Phased plan with checkbox subtasks and deliverables |
| `.planning/state.md` | Current phase, progress table, decisions log |
| `.claude/agents/` | Project-level role-specific agents (from `/init-project-orchestration`) |
| `.claude/commands/` | Project-level repeatable task commands (from `/init-project-orchestration`) |

When a recognized pattern is found, report it as **Info** -- present and expected.

## Unrecognized items

Any top-level directory or file that is **not** part of the common core, conditional structure, or recognized growth patterns should be flagged as **Info -- unrecognized** for user review. Do not flag hidden files/directories that are standard (`.git/`, `.DS_Store`, etc.).
