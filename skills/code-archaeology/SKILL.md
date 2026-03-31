---
name: code-archaeology
description: "Use when returning to old or inherited code to systematically audit, document, and safely organise legacy projects. Maps data pipelines, creates safety backups, generates documentation, and produces an audit report with reproducibility assessment."
allowed-tools: Bash(ls*), Bash(cp*), Bash(mkdir*), Bash(git*), Read, Write, Edit, Glob, Grep
argument-hint: [project-path]
---

# Code Archaeology

Systematically review and understand old code, data, and analysis files. For formal audits with cross-language replication and referee reports, use the Referee 2 agent (`.claude/agents/referee2-reviewer.md`).

## Safety Rules

**CRITICAL: Never delete data or code files.** Based on Scott Cunningham's workflow:

1. Never delete data — under no circumstances
2. Never delete programs — no do-files, no R scripts, nothing
3. Stay in this folder — can go down, not up
4. Create a `legacy/` folder — copy originals there for safekeeping
5. Copy, don't move — when reorganising, always copy from `legacy/`

## When to Use

- Returning to an old project after months/years
- Taking over code from a coauthor
- Before extending existing analysis
- R&R requiring you to revisit old work

## When NOT to Use

- **Brand new projects** — use `/init-project` or `/init-project-research`
- **Formal code verification** — use Referee 2 agent
- **Quick code questions** — just ask directly

## Workflow

### Phase 1: Explore and Inventory

1. List all files with modification dates: `ls -laR $ARGUMENTS`
2. Identify main scripts (.do, .R, .py, .m), data files, and outputs
3. Map the directory structure

### Phase 2: Trace the Pipeline

For each script, determine inputs, transformations, outputs, and dependencies. Build a pipeline map:

```
raw/survey_data.csv
  → 01_clean.R        → data/cleaned.rds
  → 02_merge.R        → data/merged.rds
  → 03_analysis.R     → output/regression_table.tex
  → 04_figures.R      → paper/figures/main_result.pdf
```

Use `grep -rn "read\|load\|source\|import" *.R *.py *.do` to trace data dependencies.

### Phase 3: Establish Safety

1. Create `legacy/` folder: `mkdir -p legacy/`
2. Copy all originals into `legacy/`
3. Set up version control if not present: `git init && git add -A && git commit -m "Initial commit: legacy snapshot"`

### Phase 4: Document Findings

Create/update these files:
- `README.md` — project overview, file descriptions, pipeline order
- `AUDIT.md` — findings, issues, reproducibility assessment
- `docs/data_dictionary.md` — variables, sources, formats

### Phase 5: Produce Audit Report

Answer these key questions in `AUDIT.md`:

| Question | Status |
|----------|--------|
| What is the research question? | |
| What data is used? | |
| What is the identification strategy? | |
| Are results reproducible from the code? | |
| What assumptions are made? | |
| What would need to change to extend this? | |

Present the report to the user with concrete recommendations for cleanup.

## Cross-References

| Skill | When to use instead |
|-------|---------------------|
| `/project-safety` | Setting up safety rules for new projects |
| `/init-project-research` | Scaffolding a brand-new research project |
| Referee 2 agent | Formal verification with cross-language replication |
