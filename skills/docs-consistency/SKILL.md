---
name: docs-consistency
description: "Review user-facing documentation for accuracy, consistency, and completeness across private, public, nested repos, and the user manual. Use when docs feel stale, after major changes, or before sharing. (Replaces `/repo-doc-audit`)"
allowed-tools: Read, Glob, Grep, Bash(ls*), Bash(wc*), Bash(find*), Bash(git log*), Bash(diff*), Bash(cat*), Write
argument-hint: "[scope] — all (default), private, public, cross-check, user-manual"
---

# Docs Review

> Cross-cutting documentation review that checks **consistency, accuracy, and completeness** across the entire documentation ecosystem. Unlike `/repo-doc-audit` (per-repo quality) or `/sync-repo` (mechanical freshness), this skill verifies that docs **agree with each other** and with reality.

## When to Use

- After adding, removing, or renaming skills, hooks, agents, or rules
- After major infrastructure changes (consolidation, new repos, renamed components)
- Before publishing or sharing the public repo
- Periodic health check (monthly)
- When the user says "review docs", "check my docs", "are my docs consistent"

## When NOT to Use

- For per-repo doc quality audit — use `/repo-doc-audit <target>`
- For mechanical count/freshness sync — use `/sync-repo <target>`
- For code architecture audit — use `/external-audit <target>`

## Argument Parsing

Parse `$ARGUMENTS` for scope (optional, default `all`):

| Scope | What it covers |
|-------|---------------|
| `all` | All 5 checks below |
| `private` | Checks 1-3 on private docs only |
| `public` | Checks 1-3 on public docs only |
| `cross-check` | Check 4 only (public-private consistency) |
| `user-manual` | Check 5 only (user manual alignment) |

## Checks

### Check 1: Count Consistency

Count actual components on disk, then verify every document that states counts matches reality.

**Disk counts** (source of truth):

```
Skills:  find skills -name SKILL.md -type f | wc -l   # recurse — skills/{engineering,research}/ are nested; ls -d skills/*/SKILL.md MISSES them (undercounts by ~5)
Hooks:   ls hooks/*.sh hooks/*.py hooks/*.mjs 2>/dev/null | wc -l   # hooks are .sh + .py + .mjs, NOT just .sh (counting .sh-only undercounts by ~15)
Agents:  ls .claude/agents/*.md | wc -l
Rules:   ls rules/*.md | wc -l
```

> Counting gotchas (these caused false-positive drift reports on 2026-06-06):
> skills live in nested category dirs too (`skills/engineering/`, `skills/research/`) so you MUST `find -name SKILL.md`, not glob `skills/*/`; and hooks are written in shell, Python, and Node, so count all three extensions.

**Documents to verify** (private scope):

| File | What to check |
|------|--------------|
| `README.md` | Skill category table totals, hook count in heading, agent count, rule count |
| `CLAUDE.md` | Skill count, hook count, agent count, rule count, file structure table |
| `docs/components/skills.md` | Total count in header, per-category counts, overview table row count |
| `docs/components/hooks.md` | Total count in header, hook table row count |
| `docs/components/agents.md` | Total count in header, agent table row count |
| `docs/components/rules.md` | Total count in header, rule table row count |
| `docs/system.md` | Component counts in overview section |

**Documents to verify** (public scope):

| File | What to check |
|------|--------------|
| `public/public-repo/README.md` | Counts in auto-generated marker sections |
| `public/public-repo/CLAUDE.md` | Skill/hook/agent/rule counts |

**Report format** per file:

```
| File | Component | Stated | Actual | Status |
|------|-----------|--------|--------|--------|
| README.md | Skills | 129 | 130 | MISMATCH |
| README.md | Hooks | 21 | 21 | OK |
```

### Check 2: Component Coverage

Every component on disk must appear in its catalogue file. Every entry in the catalogue must exist on disk.

| Component | Catalogue file | Disk location |
|-----------|---------------|--------------|
| Skills | `docs/components/skills.md` | `find skills -name SKILL.md` (incl. nested categories) |
| Hooks | `docs/components/hooks.md` | `hooks/*.{sh,py,mjs}` |
| Agents | `docs/components/agents.md` | `.claude/agents/*.md` |
| Rules | `docs/components/rules.md` | `rules/*.md` |

For each: list items on disk not in catalogue (**undocumented**) and items in catalogue not on disk (**orphan entries**).

Also check `README.md` skill category table — every skill on disk should appear in exactly one category row.

### Check 3: Stale References

Grep documentation files for references to components that no longer exist on disk.

**Scan these files:**
- `README.md`, `CLAUDE.md`
- `docs/*.md` (all)
- the user-manual .tex source (in docs/reference/user-manual)
- `skills/shared/*.md`
- `rules/*.md`

**What to look for:**
- Skill names (`/skill-name` or backtick-quoted) that don't match any skill on disk — resolve via `find skills -name SKILL.md` (a name like `skill-latex` is the MCP-tool form of the `latex` skill, NOT a separate/orphan skill — strip the `skill-` prefix before checking)
- Hook script names that don't match any `hooks/*.{sh,py,mjs}` file
- Agent names that don't match any `.claude/agents/*.md` file
- Broken relative links (markdown `[text](path)` where path doesn't exist)

Exclude `log/` and `MEMORY.md` — these are historical records, not active documentation.

### Check 4: Public-Private Cross-Consistency

Verify that public and private docs agree on the same facts.

1. **Count alignment:** Compare counts in `public/public-repo/README.md` vs `README.md`. They should match (sync-to-public.sh propagates counts).

2. **Section currency:** For each synced section (Architecture, Workflows, Session Continuity, Design Principles, Credits), check that the public version matches what `extract_section()` would produce from the private README. Flag sections where content has diverged.

3. **Marker freshness:** Check auto-generated markers in public README (COMPONENT-TABLE, SKILLS-SUMMARY, AGENTS-TABLE, HOOKS-TABLE, RULES-TABLE, FILE-TREE, FILE-STRUCTURE). Run `uv run python scripts/generate-public-docs.py --dry-run` if available, or manually compare marker content against disk reality.

4. **Leaked details:** Grep public repo for personal details that should have been anonymised:
   - Institutional names (your affiliations) outside of credits/attribution
   - Personal names (other than in credits)
   - vault file paths
   - GitHub usernames (other than `user` in attribution)

### Check 5: User Manual Alignment

Check the user-manual .tex source (in docs/reference/user-manual) against current system state.

1. **Skill tables:** Extract skill names from LaTeX tabular environments. Compare against actual skills on disk.
2. **Hook tables:** Same for hooks.
3. **Agent/rule counts:** Check any stated counts.
4. **Category structure:** Verify skill categories in the manual match the categories in `docs/components/skills.md`.
5. **Architecture diagram:** If the manual contains a system diagram, check that component names match current naming.

### Check 6: Package Coverage

Every `packages/<name>/` directory (each is a package — nested git repo or local) must appear in `docs/components/packages.md`, and the stated package count must match disk.

This check is **automated** — the canonical counter already does both the count scan and the coverage scan:

```bash
uv run python .scripts/count_inventory.py --check
```

- **Count drift:** the `packages` count in `CLAUDE.md`, `docs/system.md`, and `docs/components/packages.md` must equal `ls -d packages/*/ | wc -l`. Reported in the script's stale-count section.
- **Coverage drift:** any `packages/<name>/` subdir not mentioned in `docs/components/packages.md` is listed under "package(s) … missing from docs/components/packages.md". This catches the common drift: a new package added to disk that nobody added to the catalogue.

Exit 1 from the script ⇒ either stale count or uncovered package ⇒ this check is **FAIL** (or WARN for 1–3 items). The same script runs in `daily-maintenance.sh`, so this drift is also caught nightly without an explicit `/docs-consistency` run.

## Output

Write report to `log/audits/docs-consistency-YYYY-MM-DD.md`:

```markdown
# Documentation Review — YYYY-MM-DD

## Scope: [all / private / public / cross-check / user-manual]

## Dashboard

| Check | Status | Issues |
|-------|--------|--------|
| Count Consistency | OK/WARN/FAIL | N |
| Component Coverage | OK/WARN/FAIL | N |
| Stale References | OK/WARN/FAIL | N |
| Public-Private Sync | OK/WARN/FAIL | N |
| User Manual | OK/WARN/FAIL | N |
| Package Coverage | OK/WARN/FAIL | N |

## Count Consistency
[Per-file table from Check 1]

## Component Coverage
### Undocumented (on disk, not in catalogue)
### Orphan Entries (in catalogue, not on disk)

## Stale References
[File, line, stale reference, suggested fix]

## Public-Private Cross-Consistency
[Divergences, leaked details]

## User Manual
[Mismatches]

## Recommended Fixes
### Quick (< 2 min each)
### Medium (2-10 min)
### Requires sync script run
```

**Status thresholds:**
- **OK:** 0 issues
- **WARN:** 1-3 issues
- **FAIL:** 4+ issues

## After the Report

Present the dashboard + top-5 issues. Ask:
- **Fix now** — apply fixes (count updates, catalogue additions, stale reference removal)
- **Run sync** — run `/sync-repo private` + `bash scripts/sync-to-public.sh` to fix mechanical issues
- **Done** — report saved

## Anti-Patterns

- Do NOT modify any files during the review — report only until explicitly asked to fix
- Do NOT check `log/`, `MEMORY.md`, or `.context/current-focus.md` — these are session artifacts, not documentation
- Do NOT duplicate what `/repo-doc-audit` does — skip prose quality, readability, audience-appropriateness
- Do NOT check code or configuration — this is documentation-only

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/repo-doc-audit <target>` | Per-repo doc quality (prose, structure, audience). Run for deeper single-repo review. |
| `/sync-repo private` | Mechanical sync (counts, file trees). Fixes what this skill reports. |
| `/sync-public-repo` | Syncs private → public. Fixes cross-consistency issues. |
| `/system-audit` | Broader infrastructure health. Sub-agent 4 overlaps on count checks. |
| `/update-project-doc` | Updates project-level docs (CLAUDE.md, README). Different scope. |
