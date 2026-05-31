---
name: system-audit
description: "Use when you need to run parallel audits across skills, hooks, agents, rules, and conventions."
allowed-tools: Bash(ls*), Bash(readlink*), Bash(wc*), Bash(git*), Bash(test*), Bash(stat*), Bash(find*), Read, Glob, Grep, Task
argument-hint: "[no arguments — runs full sweep]"
---

# Maintenance Sweep

> System-wide health check using agnix lint + a deterministic Python facts script + 3 parallel judgment sub-agents. Produces a consolidated report at `log/audits/system-audit-YYYY-MM-DD.md`. **Report-only — never modifies any files.**
>
> **Architecture note (2026-05-23):** Sub-agents previously handled counts, broken-link detection, ecosystem inventory, and friends-repo file checks (SA1/SA4/SA5/SA7). They were unreliable — rolling their own counters, resolving links against the wrong CWD, recursing into the wrong directories — and produced false-positive findings that wasted triage cycles. Those four are now replaced by `.scripts/system_audit_facts.py`, which uses `count_inventory.py` as ground truth and resolves links against the source file's directory. The 3 remaining sub-agents (SA2 Bibliography, SA3 Conventions, SA6 Skill Quality) handle genuinely judgment-heavy work that can't be reduced to a script.

## When to Use

- Periodic system hygiene (monthly or after major changes)
- When the user says "maintenance sweep", "system health check", "audit my setup"
- After adding/removing skills, hooks, agents, or rules
- Before presenting the system to others (ensure everything is consistent)

## Overview

1. **Lint** — run `npx agnix .` + skill-numbering lint + review-agent logger-gate lint
2. **Facts** — run `.scripts/system_audit_facts.py all --json` (deterministic: counts, docs, ecosystem, friends repo)
3. **Dispatch** — launch 3 judgment sub-agents in parallel via the Task tool (SA2/SA3/SA6)
4. **Collect** — gather facts JSON + sub-agent findings
5. **Consolidate** — merge into a single timestamped report
6. **Present** — show key findings to the user

**Python:** Always use `uv run python` or `uv pip install`. Never bare `python`, `python3`, `pip`, or `pip3`. Include this in sub-agent prompts.

## Autonomy

Per the global `--autonomous` / `-y` convention in `~/.claude/rules/phased-work.md` § "Autonomy flag convention". Invoke as `/system-audit --autonomous` (or `-y`). When set:

- **No inter-phase pauses** — Lint → Dispatch → Collect → Consolidate → Present chain end-to-end.
- **No `AskUserQuestion` mid-run** — sub-agent count defaults to 3 (SA2/SA3/SA6), all sub-agents launch in parallel without confirmation.
- **No interim "review and continue" pauses** between dispatch and consolidation.
- **Sub-agent forbid-list still applied** — all 3 sub-agents are read-only (no edits to skills/hooks/agents/rules during the audit).
- **Report-only invariant preserved** — `--autonomous` does NOT change the skill's read-only nature; it only suppresses confirmation prompts. No fixes are ever applied.
- **Single end-of-run report** at `log/audits/system-audit-YYYY-MM-DD.md` is the only mandatory user-facing output.

This is one of the safer skills to run autonomously — it's read-only by design, sub-agents have no write access to the system, and the output is a single timestamped report that you can review afterward. Recommended for scheduled monthly runs via `/scheduled-job`.

Recommended invocations:

```
/system-audit --autonomous                              # full sweep, end-to-end
/system-audit -y                                        # short form
```

---

## Phase 0: Pre-flight Lints

Two fast lint passes run in the main context before sub-agent dispatch. Both are summary-only — full findings feed into the final report.

### 0.1 agnix lint

Run `npx agnix .` and capture the summary line.

**Pass criteria:** 0 errors. Warnings are informational only.

If errors > 0, list them in the report under an **agnix Lint** section. These are structural issues in skill/hook/agent frontmatter that should be fixed.

Config lives in `.agnix.toml` at project root — known false positives are already suppressed.

### 0.2 skill-numbering lint

Run `uv run python scripts/lint-skills.py` and capture the summary line.

**Pass criteria:** 0 findings. Findings indicate phase-numbering smells, frontmatter typos, or stale cross-skill phase references. Reference: [`skills/_shared/skill-template.md`](../_shared/skill-template.md) § Anti-patterns.

If findings > 0, list them in the report under a **Skill-Numbering Lint** section. The linter explains each rule (R1–R9) inline.

### 0.3 review-agent logger-gate lint

Run:

```bash
grep -E "^After producing (DOMAIN-REVIEW|CODE-REVIEW|your verdict|your referee|the verification)" .claude/agents/*.md
```

**Pass criteria:** 0 matches. Any match means a review-agent definition is using the stale/fragile logger-gate intro pattern that was fixed by the 5-agent patch (commit `23ebcfff`, 2026-05-17). The fragile pattern conditions the `review-state-log.sh` call on producing a stale top-level filename (`DOMAIN-REVIEW.md`-style) or a soft generic phrase (`"your verdict"`, `"the verification"`); when orchestrators like `/review-cluster` send "Return findings as a structured list, NOT a file write", the gate fails and the helper never fires — leaving a logger gap detectable by `/review-recap`.

If matches > 0, list them in the report under a **Review-Agent Logger-Gate** section with the suggested replacement intro:

> Write [your <X> report] to `reviews/<source-slug>/<YYYY-MM-DD-HHMM>.md` (`mkdir -p reviews/<source-slug>/` first). Then append a row to the project's `REVIEW-STATE.md` so `/review-recap` can render the run. Use the shared helper:

Reference pattern: see `paper-critic.md` line ~432 (already patched).

---

## Phase 1: Deterministic Facts

Run the deterministic facts script in the main context. This replaces the four count/link/inventory sub-agents that were unreliable.

```bash
uv run python .scripts/system_audit_facts.py all --json > /tmp/system-audit/facts.json
```

What this covers (all deterministic — no LLM judgment needed):

| Section | Replaces | What it checks |
|---------|----------|---------------|
| `inventory` | SA1 Inventory Auditor | Skill/hook/agent/rule counts vs `count_inventory.py` ground truth, symlinks, file-extension sanity |
| `docs` | SA4 Documentation Freshness | Stale counts in CLAUDE.md/README/docs, broken markdown links (resolved against source-file dir, not CWD), `.context/` mtime freshness |
| `ecosystem` | SA5 Ecosystem Health | MCP server registry alignment, orphan tool references, CLI tool presence |
| `friends` | SA7 Friends Repo Health | Friends-repo skill/rule freshness vs upstream, anonymisation hygiene, install script presence |

**Why this is deterministic-only, not a sub-agent:**

- Counts have a single source of truth (`count_inventory.py`) — re-rolling them in an LLM produces drift.
- Broken-link detection requires resolving relative paths against the source file's directory; sub-agents have variable CWD and produce false positives.
- Friends-repo file checks are presence/diff operations, not judgment.

If the script fails (exit code != 0), capture stderr in the report under a **Facts Script Failure** section and continue with sub-agent dispatch — the audit degrades gracefully but is no longer authoritative on the deterministic sections.

---

## Phase 2: Dispatch Judgment Sub-Agents

Launch 3 in a single message using parallel Task tool calls. Each sub-agent is `subagent_type: Explore`.

**Context overflow prevention:** Instruct each sub-agent to keep its returned output concise — summary tables and key findings only (under 500 words). If detailed findings are large, the sub-agent should write them to a temp file (e.g., `/tmp/system-audit/sa-N.md`) and return only the file path + summary.

All sub-agents receive shared context (Task Management root, research projects root, category directories). Full shared context block and the 3 sub-agent prompt templates:

**[references/sub-agent-prompts.md](references/sub-agent-prompts.md)**

Sub-agents at a glance:

| # | Name | What it checks |
|---|------|---------------|
| 2 | Bibliography & Project Hygiene | .bib files, naming, MEMORY.md presence |
| 3 | Convention Compliance | LaTeX out/, Overleaf separation, Python env, git health |
| 6 | Skill Quality & Overlap | Bloat, staleness, cross-component overlap |

Sub-agent numbering retained from the old 7-agent fan-out so prompts and reports stay cross-referenceable. SA1/SA4/SA5/SA7 are now handled by `.scripts/system_audit_facts.py` in Phase 1.

---

## Phase 3: Collect and Consolidate

After the 3 sub-agents return, merge their findings + the Phase 1 facts JSON into a single report.

### Report Template

Write to `log/audits/system-audit-YYYY-MM-DD.md`:

```markdown
# Maintenance Sweep — YYYY-MM-DD

## Dashboard

| Area | Source | Status | Issues |
|------|--------|--------|--------|
| agnix Lint | Phase 0 | <OK/WARN/FAIL> | <count> |
| Skill-Numbering Lint | Phase 0 | <OK/WARN/FAIL> | <count> |
| Review-Agent Logger-Gate | Phase 0 | <OK/WARN/FAIL> | <count> |
| Inventory | Phase 1 (facts) | <OK/WARN/FAIL> | <count> |
| Documentation Freshness | Phase 1 (facts) | <OK/WARN/FAIL> | <count> |
| Ecosystem Health | Phase 1 (facts) | <OK/WARN/FAIL> | <count> |
| Friends Repo Health | Phase 1 (facts) | <OK/WARN/FAIL> | <count> |
| Bibliography & Projects | SA2 | <OK/WARN/FAIL> | <count> |
| Conventions | SA3 | <OK/WARN/FAIL> | <count> |
| Skill Quality & Overlap | SA6 | <OK/WARN/FAIL> | <count> |

## agnix Lint
<Phase 0 results: error count, warning count, any specific errors>

## Inventory Audit
<Phase 1 facts.json `inventory` section>

## Documentation Freshness
<Phase 1 facts.json `docs` section>

## Ecosystem Health
<Phase 1 facts.json `ecosystem` section>

## Friends Repo Health
<Phase 1 facts.json `friends` section>

## Bibliography & Project Hygiene
<SA2 findings>

## Convention Compliance
<SA3 findings>

## Skill Quality & Cross-Component Overlap
<SA6 findings>

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

## Phase 4: Present

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
| `/bib-validate` | Run on projects flagged by the Bibliography Hygiene sub-agent |
| `/audit-project-research` | Complements Convention Compliance with deeper per-project checks |
| `/update-project-doc` | Fix documentation staleness found by Documentation Freshness |
| `/sync-permissions` | Fix symlink issues found by Inventory Auditor |
| `/atlas-audit` | Full cross-system audit (local + vault + Paperpile + pipeline) — deeper than this sweep |
| `/insights-deck` | Maintenance findings can feed into system insights presentations |
| `/repo-doc-audit friends` | Dedicated deep audit for friends-repo — Sub-agent 7 is a quick health check; the audit skill is the full version |
| `/sync-friends-repo` | Fix freshness issues found by Sub-agent 7 |
