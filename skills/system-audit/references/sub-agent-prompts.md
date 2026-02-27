# System Audit Sub-Agent Prompts

> Full prompt templates for the 6 parallel sub-agents dispatched in Phase 1.
> Referenced from `SKILL.md` — do not edit prompts here without updating the parent.

## Shared Context (prepend to all prompts)

```
Task Management root: 
Global Claude config: ~/.claude/
Project index: .context/projects/_index.md
Research projects root: $HOME/Library/CloudStorage/YOUR-CLOUD/Research/
Research project categories (subdirectories of the root above):
  - Category A/
  - Category B/
  - Category C/
  - Category D/
  - Category E/
  - Category F/
  - Category G/
Each category contains individual project directories.
```

## Sub-Agent 1: Inventory Auditor

**Prompt:**
```
Audit the Task Management system inventory. Check:

1. **Skill count:** Count directories in skills/ that contain a SKILL.md (exclude .DS_Store, shared/). Compare against documented count in CLAUDE.md, README.md, docs/system.md, docs/skills.md.
2. **Hook count:** Count .sh files in hooks/ (exclude .DS_Store). Compare against documented count in CLAUDE.md, README.md, docs/system.md, docs/hooks.md.
3. **Agent count:** Count .md files in .claude/agents/. Compare against documented count.
4. **Rule count:** Count .md files in .claude/rules/. Compare against documented count.
5. **Symlink health:** Verify these symlinks resolve correctly:
   - ~/.claude/skills/ → Task Management/skills/
   - ~/.claude/agents/ → Task Management/.claude/agents/
   - ~/.claude/rules/ → Task Management/.claude/rules/
   - ~/.claude/hooks/ → Task Management/hooks/
   - ~/.claude/settings.json → Task Management/.claude/settings.json
   - ~/.claude/CLAUDE.md → Task Management/GLOBAL-CLAUDE.md
   - ~/.claude/statusline-command.sh → Task Management/.claude/statusline-command.sh
6. **MCP server tool count:** The MCP server in .mcp-server-desktop/server.py registers tools as `skill-<name>` and `agent-<name>`. Count the cached skills and agents it discovers (read the discovery functions in server.py). Compare against actual skill/agent counts.
7. **Undocumented items:** Any skills/hooks/agents/rules that exist on disk but aren't listed in their respective docs file (docs/skills.md, docs/hooks.md, docs/agents.md, docs/rules.md).
8. **MCP server alignment:** Compare MCP servers between Claude Code (.mcp.json in project root) and Claude Desktop (~/Library/Application Support/Claude/claude_desktop_config.json). Check:
   - Servers present in both configs use the same name for the same service
   - Servers that should be in both are not missing from either (biblio, context7)
   - Desktop-only servers (filesystem, skills-server) are documented
   - No stale/removed servers remain in either config
   - Report a side-by-side table: Server | Code | Desktop | Status

Return findings as markdown with sections for each check, using checkmarks for pass and warnings for mismatches.
```

## Sub-Agent 2: Bibliography & Project Hygiene

**Prompt:**
```
Quick scan of bibliography files and project health across the user's research projects. Check:

1. **Find all .bib files** under the research projects root:
   $HOME/Library/CloudStorage/YOUR-CLOUD/Research/
   Categories: Category A, Category B, Category C, Category D, Category E, Category F, Category G.
   Search each project directory and its paper/ subdirectory (2 levels deep from category).
   Skip ZZ Topic Finder and ZZ Topic Inventory (these are tooling, not research projects).

2. For each .bib file found:
   - Count entries (grep for @article, @inproceedings, @book, @misc, etc.)
   - Check naming convention (should be paperpile.bib or <project>.bib)
   - Spot-check 3 keys for Paperpile format (AuthorYYYY-xx pattern)
   - Flag any obvious issues (empty files, very large files >500 entries)

3. **MEMORY.md presence:** For each project, check if a MEMORY.md exists in the project root. Projects that have been actively worked on should have one.

4. **Summary table:** Project | Category | Bib file | Entry count | Naming OK | MEMORY.md

Do NOT do a full validation — that's what /validate-bib is for. Just flag projects that should be audited in detail.
```

## Sub-Agent 3: Convention Compliance

**Prompt:**
```
Check convention compliance across the user's research projects. Scan each project directory under:
$HOME/Library/CloudStorage/YOUR-CLOUD/Research/
Categories: Category A, Category B, Category C, Category D, Category E, Category F, Category G.
Skip ZZ Topic Finder and ZZ Topic Inventory.

For each project, check:

1. **LaTeX output directory:** If .tex files exist (in project root or paper/), does an out/ directory exist? Is there a .latexmkrc file?
2. **Overleaf separation:** If a paper/ directory exists, is it a symlink? Check that paper/ contains ONLY LaTeX source files (.tex, .sty, .cls, .bst, .bbl, .bib, .latexmkrc, out/) and figures (.pdf, .png, .eps, .jpg, .svg, .tikz). Flag any code files (.py, .R, .jl, .sh, .ipynb), data files (.csv, .xlsx, .json, .dta, .parquet), or other non-LaTeX artifacts found inside paper/.
3. **Hook executability:** All .sh files in hooks/ should be executable (chmod +x).
4. **Python environment:** If .py files exist in the project, is there a pyproject.toml? Any sign of bare pip usage (requirements.txt without pyproject.toml, pip in scripts)?
5. **CLAUDE.md presence:** Does each project have a CLAUDE.md?
6. **Git health:** Is the project a git repo? Any uncommitted changes? Any untracked files that should probably be tracked?

Report per-project compliance as a table:
Project | Category | LaTeX/out | Overleaf sep. | Python env | CLAUDE.md | Git

Only scan top-level project directories — don't recurse deeply into subdirectories.
```

## Sub-Agent 4: Documentation Freshness

**Prompt:**
```
Check documentation freshness in the Task Management system at:


Audit:

1. **Stale counts in docs:** Check these files for numeric claims about skills, hooks, agents, rules, and compare against actual counts on disk:
   - CLAUDE.md: skill count, hook count, agent count, rule count
   - README.md: same counts
   - docs/system.md: same counts, file tree accuracy
   - docs/skills.md: total skill count, category counts, skill catalogue completeness

2. **Broken internal links:** Check markdown links in CLAUDE.md, README.md, docs/system.md, docs/skills.md, docs/hooks.md, docs/agents.md, docs/rules.md — do the referenced files actually exist?

3. **Outdated statuses in .context/:**
   - current-focus.md: when was it last modified? (check file stat or git log)
   - projects/_index.md: compare project list against actual directories in the research projects root. Any projects on disk but missing from the index? Any entries in the index for projects that don't exist?

4. **Old session logs:** What's the most recent file in log/? How many logs exist? Any very old logs (>90 days) that could be archived?

5. **Plan staleness:** Any plans in log/plans/ more than 30 days old that reference incomplete work?

6. **GLOBAL-CLAUDE.md vs CLAUDE.md consistency:** Check that GLOBAL-CLAUDE.md (the slim pointer file) doesn't duplicate detailed content from CLAUDE.md. It should contain only identity, pointers, and global policies.

Return as markdown with severity levels: OK, STALE, BROKEN.
```

## Sub-Agent 5: Ecosystem Health

**Prompt:**
```
Check ecosystem health for the Task Management system at:


Run these 4 checks:

1. **MCP server health:** Find all mcp__*__ tool references in skills and agents:
   grep -rohn "mcp__[A-Za-z0-9_-]*__[A-Za-z0-9_]*" skills/ .claude/agents/ --include="*.md" | sort -u

   Extract server names (the part between mcp__ and the second __).

   Then get configured MCP servers from both configs using jq:
   cat .mcp.json | jq -r '.mcpServers // {} | keys[]' 2>/dev/null | sort -u
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq -r '.mcpServers // {} | keys[]' 2>/dev/null | sort -u

   Also check for disabled servers:
   cat .mcp.json | jq -r '.disabledMcpServers // [] | .[]' 2>/dev/null

   Flag: CRITICAL if a referenced server is not configured anywhere (phantom tool).
   Flag: WARNING if a server is configured but also in disabledMcpServers.
   Known aliases: "claude_ai_Notion" is a Claude.ai managed integration (not in local config — OK).
   Known servers: biblio, context7, claude_ai_Notion, claude_ai_Gamma.

2. **Staleness detection:** Find components not modified in 90+ days across ALL types:
   find skills/ -name "SKILL.md" -not -path "*/shared/*" -mtime +90 -type f
   find .claude/agents/ -name "*.md" -mtime +90 -type f
   find hooks/ \( -name "*.sh" -o -name "*.py" \) -mtime +90 -type f
   find .claude/rules/ -name "*.md" -mtime +90 -type f
   find .scripts/ \( -name "*.py" -o -name "*.sh" \) -mtime +90 -type f

   For each stale file, check if it's still referenced by other active components.
   Flag: WARNING if stale AND referenced (may be outdated).
   Flag: INFO if stale AND not referenced (candidate for archive).
   Flag: OK if still within 90 days.

3. **Orphan detection:** Find components with zero external references across ALL types.
   For each skill directory in skills/:
   - Read first 10 lines to check for "user-invocable: true" — if present, skip (exempt)
   - Search for the skill name across all other skills, agents, hooks, rules, CLAUDE.md, and docs/
   - If zero references found: flag as INFO (dead code, candidate for archive)
   For each hook in hooks/:
   - Check if registered in .claude/settings.json (unregistered hook = orphan)
   - Search for the hook filename across skills, agents, docs/hooks.md
   - If not registered AND not documented: flag as INFO
   For each agent in .claude/agents/:
   - Search for the agent name across skills, CLAUDE.md, docs/
   - If zero references found: flag as INFO
   For each rule in .claude/rules/:
   - Search for the rule filename across CLAUDE.md, docs/, skills/
   - Rules are auto-loaded so they're never truly orphaned, but flag if undocumented in docs/rules.md
   For each script in .scripts/:
   - Search for the script name across skills, hooks, CLAUDE.md, docs/
   - If zero references found: flag as INFO

4. **CLI tool availability:** Verify these tools are installed and accessible:
   - gh (GitHub CLI)
   - latexmk (LaTeX compilation)
   - uv (Python package manager)
   - jq (JSON processor)
   - gemini (Gemini CLI for council mode)
   - codex (Codex CLI for council mode)
   - node (Node.js for MCP servers)
   For each: run "which [tool]" and "[tool] --version" (or equivalent).
   Flag: CRITICAL if a tool referenced in CLAUDE.md as required is not installed.
   Flag: WARNING if installed but fails to respond.
   Flag: OK if installed and responds.

Return findings as markdown with a summary table:
| Check | OK | Warning | Critical |
Then list each finding with severity, file path, and brief description.
Keep output under 500 words — write details to /tmp/system-audit/sa-5.md if needed.
```

## Sub-Agent 6: Skill Quality & Cross-Component Overlap

**Prompt:**
```
Evaluate skill quality and cross-component overlap for the Task Management system at:


## Part A: Skill Quality

For each skill directory in skills/ (excluding shared/):

1. Read the SKILL.md frontmatter (name, description)
2. Check file size (flag >300 lines as potentially bloated)
3. Check modification date (flag >90 days as potentially stale)
4. Spot-check for content overlap with other skills (read first 20 lines of each, look for similar descriptions or duplicate trigger phrases)
5. Check for broken references (references to files in references/ or shared/ that don't exist)

For each skill, assign a verdict:
- **OK** — healthy, no issues
- **BLOATED** — >300 lines, may need extraction to references/
- **STALE** — not modified in 90+ days AND not referenced by other components
- **OVERLAP** — significant description/trigger overlap with another skill (name it)
- **BROKEN** — references missing files

Return a summary table:
| Skill | Lines | Last Modified | Verdict | Notes |

## Part B: Cross-Component Overlap

Check for functional overlap ACROSS component types (skills, hooks, agents, rules, .scripts/). Read the description/purpose of each component:
- skills/*/SKILL.md (frontmatter description)
- hooks/*.sh and hooks/*.py (header comment block)
- .claude/agents/*.md (first 10 lines for purpose)
- .claude/rules/*.md (first 10 lines for principle)
- .scripts/*.py and .scripts/*.sh (header comment block)

Flag cases where two different component types appear to do the same thing or enforce the same constraint. Common overlap patterns to check:
- A hook gating something a rule also describes (e.g., both blocking bare python)
- A skill doing what a .scripts/ CLI tool also does
- An agent's workflow duplicating a skill's workflow
- A rule describing a convention that a hook already enforces automatically

For each overlap found, assess:
- **Complementary** — both are needed (e.g., hook enforces at runtime, rule instructs at planning time)
- **Redundant** — one could be removed without loss
- **Conflicting** — they give contradictory instructions

Return a cross-component table:
| Component A | Component B | Type | Assessment | Notes |

Only flag genuine overlaps — a rule mentioning "use uv" and a hook enforcing "use uv" is complementary (expected), not redundant. Focus on cases where work is truly duplicated or instructions conflict.

Keep total output under 500 words. Write details to /tmp/system-audit/sa-6.md if needed.
```
