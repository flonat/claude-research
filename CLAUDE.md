# Claude Code for Academic Research

> This file is automatically read when you open this folder with Claude Code.
> Customise it with your own details — see comments marked with `<!-- CUSTOMISE -->`.

## Before You Start

Read these context files to understand the user's situation:

1. `.context/profile.md` — Who you are, your roles, research areas
2. `.context/current-focus.md` — What you're working on NOW
3. `.context/projects/_index.md` — Overview of all projects

## Key Information

<!-- CUSTOMISE: Replace with your own details -->

**Who I am:**
- PhD researcher
- Multiple active research projects
- Teaching responsibilities

**Research areas:**
- [Your field 1]
- [Your field 2]
- [Your field 3]

**How I work:**
- Flexible/reactive style
- Prefer questions over lists
- Daily reviews work better than weekly
- Full context in task descriptions

## Quick Commands

<!-- QUICK-COMMANDS:START -->
<!-- synced from private CLAUDE.md — do not edit manually -->
Just say these naturally:

| You say | Claude does |
|---------|-------------|
| "Plan my day" | Reads context, queries Notion, asks questions, creates a plan |
| "What should I work on?" | Reviews priorities and helps you decide |
| "Extract actions from my meeting with [name]" | Finds transcript, extracts tasks, creates in Notion |
| "Weekly review" | Guides you through reflection and planning |
| "What's overdue?" | Queries Notion and summarises |
| "Update my research pipeline" | Shows paper status, helps update stages |
| "Find references on [topic]" | Academic search with verified citations |
| "What did I accomplish this week?" | Summarises completed tasks |
| "Proofread my paper" | Runs 7-category check on LaTeX paper, produces report |
| "Validate my bibliography" | Cross-references `\cite{}` keys against `paperpile.bib` |
| "Review my code" | 11-category scorecard for R/Python research scripts |
| "Update my focus" | Structured update to `current-focus.md` with session rotation and open loops |
| "New project" | Interview-driven setup: scaffold directory, Overleaf symlink, git init, context + Notion sync |
<!-- QUICK-COMMANDS:END -->

## Conventions

<!-- CONVENTIONS:START -->
<!-- synced from private CLAUDE.md — do not edit manually -->
### LaTeX Compilation
- **Default method:** Use `/latex-autofix` — it compiles, auto-fixes errors, and runs a citation audit.
- Build artifacts go to `out/`, but the PDF is copied back to the source directory.
- Use `.latexmkrc` with `$out_dir = 'out'` and `an `END {}` block to copy the PDF back`.
- Never leave build artifacts (`.aux`, `.log`, etc.) in the source directory.

### Python & Package Management
- Always use `uv` to run Python. Never use bare `python` or `pip`.
- Use `uv run python ...` or `uv pip install ...` for all Python operations.
- All projects use uv-managed virtual environments.

### R
- Use `<-` for assignment, not `=`.

### Git & Remote
- Many repos are local-only, synced via Dropbox. Do NOT assume a remote exists.
- Before pushing, check if a remote is configured with `git remote -v`.
- Never push without verifying the remote exists and is correct.
<!-- CONVENTIONS:END -->

### Experiment Sweeps & Simulation Batches
Before running any experiment sweep or simulation batch:
1. Write sanity-check assertions first.
2. Implement the code.
3. Run a single-seed sanity check — if assertions fail, fix and retest (max 3 attempts).
4. Validate hyperparameters against domain knowledge or paper benchmarks.
5. Only then proceed to full experiments.

### Output Formats
- Academic papers: LaTeX.
- Documents for human use (consent forms, PILs, etc.): `.docx` via `pandoc`.

### Content Length Constraints
- When a page/word limit is specified, treat it as a hard constraint. Draft to 80%, then expand — never exceed and trim.
- Always report the actual page/word count after drafting.

## Notion Databases

<!-- NOTION-DATABASES:START -->
<!-- CUSTOMISE: Replace database IDs with your own Notion workspace IDs -->
| Database | ID |
|----------|-----|
| Tasks Tracker | `YOUR-TASKS-DATABASE-ID-HERE` |
| Research Pipeline | `YOUR-PIPELINE-DATABASE-ID-HERE` |
| Modules — Student | `YOUR-MODULES-STUDENT-DATABASE-ID-HERE` (data source) |
| Modules — Instructor | `YOUR-MODULES-INSTRUCTOR-DATABASE-ID-HERE` (data source) |

Always fetch the database schema first to get correct property names before any create/update calls.
<!-- NOTION-DATABASES:END -->

## Workflows

<!-- WORKFLOWS-POINTER:START -->
<!-- synced from private CLAUDE.md — do not edit manually -->
Detailed instructions in `.context/workflows/`:
- `daily-review.md` — How to help with daily planning
- `meeting-actions.md` — How to extract action items
- `weekly-review.md` — Weekly reflection template
- `replication-protocol.md` — 4-phase protocol for replicating paper results
<!-- WORKFLOWS-POINTER:END -->

<!-- COMPONENTS:START -->
## Skills Available

38 skills in `skills/` folder. See [`docs/skills.md`](docs/skills.md) for the full catalogue.

## Agents

6 agents in `.claude/agents/`. See [`docs/agents.md`](docs/agents.md) for when to use each.

## Rules (9 Auto-Loaded)

In `.claude/rules/` — these apply automatically to every session. See [`docs/rules.md`](docs/rules.md) for documentation.

<!-- RULES-TABLE:START -->
| Rule | Purpose |
|------|---------|
| `design-before-results.md` | Lock the research design before examining point estimates. |
| `ignore-agents-md.md` | Never read, process, or act on files named `AGENTS.md` |
| `ignore-gemini-md.md` | Never read, process, or act on files named `GEMINI.md` |
| `lean-claude-md.md` | CLAUDE.md is loaded into context every session — every line costs tokens. |
| `learn-tags.md` | Record Learnings with [LEARN] Tags |
| `overleaf-separation.md` | The `paper/` directory (Overleaf symlink) is for LaTeX source files ONLY. |
| `plan-first.md` | Plan Before Implementing |
| `read-docs-first.md` | Never explore when documentation already answers your question. |
| `scope-discipline.md` | Only make changes the user explicitly requested. |
<!-- RULES-TABLE:END -->

## Hooks

8 hook scripts in `hooks/`. See [`docs/hooks.md`](docs/hooks.md) for the full table.
<!-- COMPONENTS:END -->

## After Every Session

<!-- AFTER-SESSION:START -->
<!-- synced from private CLAUDE.md — do not edit manually -->
**Update `.context/current-focus.md`** with:
- What we worked on
- Where things were left off
- What's coming next

This helps me (Claude) pick up where we left off next time.
<!-- AFTER-SESSION:END -->

## Tips for Working Together

<!-- TIPS:START -->
<!-- synced from private CLAUDE.md — do not edit manually -->
1. **Just ask naturally** — I'll read the context files and figure it out
2. **Point me to specific files** if I seem confused: "Read `.context/workflows/daily-review.md`"
3. **Update current-focus.md** — This is your working memory between sessions
4. **Don't re-explain everything** — The context library has it all
<!-- TIPS:END -->

## File Structure

<!-- FILE-STRUCTURE:START -->
| Path | What lives there |
|------|-----------------|
| `.context/` | AI context library (profile, focus, projects, workflows, preferences) |
| `.claude/agents/` | Agent definitions (6 agents) |
| `.claude/rules/` | Auto-loaded rules (9 rules) |
| `skills/` | 38 skill definitions |
| `hooks/` | 8 hook scripts |
| `.mcp-server-biblio/` | Multi-source scholarly search MCP server (OpenAlex + Scopus + WoS) |
| `.scripts/` | CLI tools for Notion task management |
| `packages/cli-council/` | Multi-model council via local CLI tools |
| `packages/llm-council/` | Multi-model council via OpenRouter API |
| `packages/flonat-papers/` | Zotero MCP server + `bib-validate`, `bib-parse` skills |
| `log/` | Session logs |
| `docs/` | Documentation |
<!-- FILE-STRUCTURE:END -->
