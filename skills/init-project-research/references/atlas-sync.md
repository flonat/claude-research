# Atlas Sync — Phase 6 Details

> Referenced from: `init-project-research/SKILL.md` Phase 6

Creates the research topic in all systems: local file → vault atlas → Venues → project folder → documentation.

## 6a. Create Atlas Topic File

1. Read theme files from `~/Research-Vault/themes/` — current themes and their metadata
2. Glob `~/Research-Vault/atlas/**/*.md` — existing slugs (avoid duplicates)
3. Determine the **slug** (kebab-case, 2-5 words). Pattern: `{contribution}-{domain-object}`. Names the idea, not venue/output/method. Within clusters (e.g., carbon, elicitation), each slug needs a unique distinguishing word. Anti-patterns: acronyms (`efficient-pe`), bare fields (`smart-meters`), venue names (`facct-paper`). Good: `carbon-collusion`, `elicitation-cost-tradeoffs`.
4. Write `~/Research-Vault/atlas/{theme-dir}/{slug}.md` using the YAML frontmatter template from [`atlas-schema.md`](atlas-schema.md). Include `## Description`, `## Key References`, `## Open Questions`.
5. **Validate the topic file** before proceeding: run `uv run python packages/atlas/schema.py ~/Research-Vault/atlas/{theme-dir}/{slug}.md` from `$TM/packages/atlas/`. If validation fails, fix the file before syncing to vault.
6. If new theme needed: create the theme directory under `~/Research-Vault/atlas/` and add a theme file at `~/Research-Vault/themes/{slug}.md`. The topic file created in step 4 is sufficient — no separate slug list to maintain.

## 6b. Create vault Atlas Entry (if syncing to vault)

Atlas entries in the vault are synced from the local markdown files via `/sync-atlas`. The vault Topic Inventory is a read-only downstream copy:

1. Run `/sync-atlas push` to sync the newly created local topic file to the vault
2. The sync tool will map YAML fields to vault properties per the sync spec
3. Only use valid Methods multi-select values (see `atlas-schema.md` reference)

## 6b2. Create Vault Submission Entry (MANDATORY)

**Always create a submission entry — regardless of topic status (even Idea stage).** This makes the topic visible to taskflow MCP queries, deadline tracking, and portfolio views.

Write `~/Research-Vault/submissions/{slug}.md`:

```yaml
---
title: <full paper title from interview>
type: submission
paper: '[[{slug}]]'
venue: '[[{target venue}]]'
status: <matches atlas topic status, e.g. Idea>
year: null
deadline: <if known from interview, else null>
notification_date: null
conference_date: null
location: ''
---

## Notes

<one-line summary of the project and co-authors>
```

**Never skip this step.** A topic without a submission entry is invisible to the pipeline.

## 6c. Create Project Folder

Create the project directory under the research projects root:

```bash
RESEARCH_ROOT="$(cat ~/.config/task-mgmt/research-root)"
mkdir -p "$RESEARCH_ROOT/{ThemeAbbrev}/{slug}"
```

Theme abbreviations: ASG, BDS, EnvEcon, HAI, IO, MechDes, NLP, OR, OrgStrat, PolSci. Folder name must be the kebab-case slug (same as the atlas topic filename).

## 6d. Regenerate RECAP.md

```bash
cd "$TM/packages/atlas" && uv run python generate_recap.py
```

## 6e. Update Atlas Counts

If topic or theme count changed, update `$TM/packages/atlas/CLAUDE.md` topic/theme counts and theme directory listing.

## Atlas Defaults

| Setting | Default | Override |
|---------|---------|---------|
| Status | `Idea` | User specifies |
| Priority | `Medium` | User specifies |
| Data Availability | `None` | User specifies |
| Feasibility | `Medium` | User specifies |
| Institution | Infer from theme/co-author | User specifies |
