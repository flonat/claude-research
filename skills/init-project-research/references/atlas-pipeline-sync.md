# Atlas & Pipeline Sync — Phase 6 Details

> Referenced from: `init-project-research/SKILL.md` Phase 6

Creates the research topic in all systems: local file → vault atlas → vault pipeline → Venues → project folder → documentation.

## 6a. Create Atlas Topic File

1. Read `packages/atlas/themes.md` — current themes and topic lists
2. Glob `packages/atlas/topics/**/*.md` — existing slugs (avoid duplicates)
3. Determine the **slug** (kebab-case, 2-5 words). Pattern: `{contribution}-{domain-object}`. Names the idea, not venue/output/method. Within clusters (e.g., carbon, elicitation), each slug needs a unique distinguishing word. Anti-patterns: acronyms (`efficient-pe`), bare fields (`smart-meters`), venue names (`facct-paper`). Good: `carbon-collusion`, `elicitation-cost-tradeoffs`.
4. Write `packages/atlas/topics/{theme-dir}/{slug}.md` using the YAML frontmatter template from [`atlas-schema.md`](atlas-schema.md). Include `## Description`, `## Key References`, `## Open Questions`.
5. **Validate the topic file** before proceeding: run `uv run python packages/atlas/schema.py topics/{theme-dir}/{slug}.md` from the atlas directory. If validation fails, fix the file before syncing to vault.
6. Update `packages/atlas/themes.md` — add slug to the correct theme's topic list. If new theme needed: add row, create directory, create vault theme entry (`data_source_id: 2e8baef4-3e2e-4ea5-b25a-18a71ed47690`).

## 6b. Create vault Atlas Entry

1. Look up the theme's vault file ID via `mcp__taskflow__search_tasks`
2. Create Atlas entry via `mcp__taskflow__create_task` with parent `data_source_id: 0a227f82-60f4-451a-a163-bff2ce8fa9c3`
3. Map YAML fields to vault properties per [`atlas-schema.md`](atlas-schema.md)
4. Set Theme relation: `"[\"~/Research-Vault/{theme-page-id}\"]"`
5. Only use valid Methods multi-select values (see schema reference)

## 6c. Create vault Pipeline Entry

1. Create Pipeline row via `mcp__taskflow__create_task` with parent `data_source_id: YOUR-PIPELINE-DATABASE-ID-HERE`
2. Set: `Project Name` (title), Stage, Target Journal, Co-authors, Priority ("Medium")
3. Save the returned Pipeline page ID
4. **Link Pipeline→Atlas topic** via a separate `mcp__taskflow__update_task` call:
   - Property name: `Topics` (NOT "Related Topics" — that's the Atlas-side name)
   - Value format: `"Topics": "~/Research-Vault/{atlas_page_id_no_dashes}"`
   - This is a dual relation: setting `Topics` on Pipeline also sets `Papers` on the Atlas entry
   - **This step cannot be done during creation** — the relation must be set via `update_properties` after both pages exist
5. Link to Venues via "Target Venue" relation (search Venues DB `YOUR-CONFERENCES-DATABASE-ID-HERE` for venue pages)
6. **Verify the link**: fetch the Pipeline entry and confirm `Topics` contains the Atlas page URL
7. Save the Pipeline vault file URL for the confirmation report

## 6d. Create Project Folder

Create the project directory under the research projects root. Detect root location:

```bash
# Dropbox (MacBook)
if [ -d "$HOME/Library/CloudStorage/YOUR-CLOUD/Research" ]; then
  RESEARCH_ROOT="$HOME/Library/CloudStorage/YOUR-CLOUD/Research"
else
  RESEARCH_ROOT="$HOME/Projects"
fi
mkdir -p "$RESEARCH_ROOT/{Theme Name}/{Project Name}"
```

## 6e. Regenerate RECAP.md

```bash
uv run python packages/atlas/generate_recap.py
```

## 6f. Update Atlas Counts

If topic or theme count changed, update `packages/atlas/CLAUDE.md` topic/theme counts and theme directory listing.

## Atlas Defaults

| Setting | Default | Override |
|---------|---------|---------|
| Status | `Idea` | User specifies |
| Priority | `Medium` | User specifies |
| Data Availability | `None` | User specifies |
| Feasibility | `Medium` | User specifies |
| Institution | Infer from theme/co-author | User specifies |
