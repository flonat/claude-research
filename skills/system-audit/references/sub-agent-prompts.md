# System Audit Sub-Agent Prompts

> Full prompt templates for the 3 parallel judgment sub-agents (SA2, SA3, SA6) dispatched in Phase 2.
> Referenced from `SKILL.md` — do not edit prompts here without updating the parent.
> SA1 (Inventory), SA4 (Documentation Freshness), SA5 (Ecosystem Health), and SA7 (Friends Repo Health) were retired 2026-05-23 — their checks are now deterministic and live in `.scripts/system_audit_facts.py`.

## Shared Context (prepend to all prompts)

```
Task Management root: $TM/
Global Claude config: ~/.claude/
Project index: .context/projects/_index.md
Research projects root: $RESEARCH_ROOT/
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

## (Removed) Sub-Agent 1: Inventory Auditor

Inventory checks (counts, symlinks, MCP alignment) are now handled deterministically by `.scripts/system_audit_facts.py inventory`. See SKILL.md Phase 1 and the rationale in the architecture note.

## Sub-Agent 2: Bibliography & Project Hygiene

**Prompt:**
```
Quick scan of bibliography files and project health across the user's research projects. Check:

1. **Find all .bib files** under the research projects root:
   $RESEARCH_ROOT/
   Categories: Category A, Category B, Category C, Category D, Category E, Category F, Category G.
   Search each project directory and its paper/ subdirectory (2 levels deep from category).
   Skip packages/scout/ (tooling, not a research project — now lives in Task Management).

2. For each .bib file found:
   - Count entries (grep for @article, @inproceedings, @book, @misc, etc.)
   - Check naming convention (should be references.bib or <project>.bib)
   - Spot-check 3 keys for BBT format (AuthorYYYY-xx pattern)
   - Flag any obvious issues (empty files, very large files >500 entries)

3. **MEMORY.md presence:** For each project, check if a MEMORY.md exists in the project root. Projects that have been actively worked on should have one.

4. **Summary table:** Project | Category | Bib file | Entry count | Naming OK | MEMORY.md

Do NOT do a full validation — that's what /bib-validate is for. Just flag projects that should be audited in detail.
```

## Sub-Agent 3: Convention Compliance

**Prompt:**
```
Check convention compliance across the user's research projects. Scan each project directory under:
$RESEARCH_ROOT/
Categories: Category A, Category B, Category C, Category D, Category E, Category F, Category G.
Skip packages/scout/ (tooling, not a research project).

For each project, check:

1. **LaTeX output directory:** For each directory containing standalone `.tex` files (root, `paper*/`, `reviews/`, `presentations/`, etc. — NOT `backup/`, `archive/`, `output/`, `code/`, or other generated/archived locations), check for a colocated `out/` directory and `.latexmkrc`. Convention is per-tex-directory, not project-root. Skip directories where `.tex` files are clearly generated outputs (e.g., `output/LaTeX/M1_*.tex`, `code/results/table_*.tex`) — those are `\input{}` fragments, not standalone documents.
2. **Overleaf separation:** If a paper/ directory exists, is it a symlink? Check that paper/ contains ONLY LaTeX source files (.tex, .sty, .cls, .bst, .bbl, .bib, .latexmkrc, out/) and figures (.pdf, .png, .eps, .jpg, .svg, .tikz). Flag any code files (.py, .R, .jl, .sh, .ipynb), data files (.csv, .xlsx, .json, .dta, .parquet), or other non-LaTeX artifacts found inside paper/.
3. **Hook executability:** All .sh files in $TM/hooks/ should be executable (chmod +x).
4. **Python environment:** If .py files exist in the project, is there a pyproject.toml? Any sign of bare pip usage (requirements.txt without pyproject.toml, pip in scripts)?
5. **CLAUDE.md presence:** Does each project have a CLAUDE.md?
6. **Git health:** Is the project a git repo? Any uncommitted changes? Any untracked files that should probably be tracked?

Report per-project compliance as a table:
Project | Category | LaTeX/out | Overleaf sep. | Python env | CLAUDE.md | Git

Only scan top-level project directories — don't recurse deeply into subdirectories.
```

## (Removed) Sub-Agent 4: Documentation Freshness

Documentation checks (stale counts, broken markdown links, `.context/` mtime freshness, log/plan staleness) are now handled deterministically by `.scripts/system_audit_facts.py docs`. The script resolves links against each source file's directory (fixing the false-positive class where the previous sub-agent used the wrong CWD). See SKILL.md Phase 1.

## (Removed) Sub-Agent 5: Ecosystem Health

Ecosystem checks (MCP server alignment between Code/Desktop configs, orphan tool refs, CLI tool presence) are now handled deterministically by `.scripts/system_audit_facts.py ecosystem`. The deterministic version reads the canonical `.mcp.json` + Claude Desktop config and emits aligned tables rather than re-parsing them per-run in a sub-agent. See SKILL.md Phase 1.

Staleness/orphan detection (90-day mtime sweep across skills/hooks/agents/rules/scripts) is a known-judgment domain — currently absorbed into SA6 Skill Quality. If a separate orphan-detection script becomes worthwhile, add it as another section in the facts script rather than reviving this sub-agent.

## Sub-Agent 6: Skill Quality & Cross-Component Overlap

**Prompt:**
```
Evaluate skill quality and cross-component overlap for the Task Management system at:
$TM/

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

## (Removed) Sub-Agent 7: Friends Repo Health

Friends-repo checks (skill/rule counts vs README, sampled freshness diff, anonymisation grep, install script presence) are now handled deterministically by `.scripts/system_audit_facts.py friends`. Anonymisation grep is exact-string matching; freshness is a file-diff sample — both are mechanical and don't benefit from LLM judgment. See SKILL.md Phase 1.
