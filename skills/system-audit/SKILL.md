---
name: system-audit
description: "Run parallel system audits across skills, hooks, agents, rules, bibliographies, conventions, and documentation freshness. Report-only — never modifies files."
allowed-tools: Bash(ls*), Bash(readlink*), Bash(wc*), Bash(git*), Bash(test*), Bash(stat*), Bash(find*), Read, Glob, Grep, Task
argument-hint: "[no arguments — runs full sweep]"
---

# Maintenance Sweep

> System-wide health check using 6 parallel sub-agents. Produces a consolidated report at `log/system-audit-YYYY-MM-DD.md`. **Report-only — never modifies any files.**

## When to Use

- Periodic system hygiene (monthly or after major changes)
- When the user says "maintenance sweep", "system health check", "audit my setup"
- After adding/removing skills, hooks, agents, or rules
- Before presenting the system to others (ensure everything is consistent)

## Overview

1. **Dispatch** — launch 6 sub-agents in parallel via the Task tool
2. **Collect** — gather each sub-agent's findings
3. **Consolidate** — merge into a single timestamped report with summary dashboard
4. **Present** — show key findings to the user

**Python:** Always use `uv run python` or `uv pip install`. Never bare `python`, `python3`, `pip`, or `pip3`. Include this in sub-agent prompts.

---

## Phase 1: Dispatch Sub-Agents

Launch all 6 in a single message using parallel Task tool calls. Each sub-agent is `subagent_type: Explore`.

**Context overflow prevention:** Instruct each sub-agent to keep its returned output concise — summary tables and key findings only (under 500 words). If detailed findings are large, the sub-agent should write them to a temp file (e.g., `/tmp/system-audit/sa-N.md`) and return only the file path + summary.

All sub-agents receive shared context (Task Management root, research projects root, category directories). Full shared context block and all 6 sub-agent prompt templates:

**[references/sub-agent-prompts.md](references/sub-agent-prompts.md)**

Sub-agents at a glance:

| # | Name | What it checks |
|---|------|---------------|
| 1 | Inventory Auditor | Skill/hook/agent/rule counts, symlinks, MCP alignment |
| 2 | Bibliography & Project Hygiene | .bib files, naming, MEMORY.md presence |
| 3 | Convention Compliance | LaTeX out/, Overleaf separation, Python env, git health |
| 4 | Documentation Freshness | Stale counts, broken links, .context/ freshness |
| 5 | Ecosystem Health | MCP server refs, staleness, orphans, CLI tools |
| 6 | Skill Quality & Overlap | Bloat, staleness, cross-component overlap |

---

## Phase 2: Collect and Consolidate

After all 6 sub-agents return, merge their findings into a single report.

### Report Template

Write to `log/system-audit-YYYY-MM-DD.md`:

```markdown
# Maintenance Sweep — YYYY-MM-DD

## Dashboard

| Area | Status | Issues |
|------|--------|--------|
| Inventory | <OK/WARN/FAIL> | <count> |
| Bibliography & Projects | <OK/WARN/FAIL> | <count> |
| Conventions | <OK/WARN/FAIL> | <count> |
| Documentation | <OK/WARN/FAIL> | <count> |
| Ecosystem Health | <OK/WARN/FAIL> | <count> |
| Skill Quality & Overlap | <OK/WARN/FAIL> | <count> |

## Inventory Audit
<Sub-agent 1 findings>

## Bibliography & Project Hygiene
<Sub-agent 2 findings>

## Convention Compliance
<Sub-agent 3 findings>

## Documentation Freshness
<Sub-agent 4 findings>

## Ecosystem Health
<Sub-agent 5 findings>

## Skill Quality & Cross-Component Overlap
<Sub-agent 6 findings>

## Recommended Actions
<Prioritised list of things to fix, grouped by effort level>

### Quick Fixes (< 5 min each)
- ...

### Medium Effort (5–30 min)
- ...

### Larger Tasks (> 30 min)
- ...
```

---

## Phase 3: Present

Show the user:
1. The dashboard table
2. Any FAIL-status areas with specifics
3. The quick fixes list
4. Ask if he wants to address any issues now

---

## Error Handling

- **Sub-agent timeout:** If a sub-agent doesn't return, note "timed out" in the report and continue with the others.
- **Missing directories:** If a category folder is empty or doesn't exist, note "no projects found" rather than erroring.
- **Permission issues:** If files can't be read, note "access denied" and continue.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `/validate-bib` | Run on projects flagged by the Bibliography Hygiene sub-agent |
| `/audit-project-structure` | Complements Convention Compliance with deeper per-project checks |
| `/update-project-doc` | Fix documentation staleness found by Documentation Freshness |
| `/sync-permissions` | Fix symlink issues found by Inventory Auditor |
| `/audit-research-projects` | Full cross-system audit (local + Notion + Paperpile + pipeline) — deeper than this sweep |
| `/insights-deck` | Maintenance findings can feed into system insights presentations |
