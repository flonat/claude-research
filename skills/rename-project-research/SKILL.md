---
name: rename-project-research
description: "Use when you need to rename a research project across all systems (local directory, atlas, vault, Overleaf, git)."
allowed-tools: Bash(mv*), Bash(ln*), Bash(ls*), Bash(readlink*), Bash(git*), Bash(find*), Bash(uv*), Read, Write, Edit, Glob, Grep, AskUserQuestion
argument-hint: "[old-name new-name] or guided interview"
---

# Rename Research Project

> Full project rename across all systems: local directory, atlas topic, vault (atlas + pipeline + submissions), Overleaf symlinks, git, and documentation. Replaces the old `rename-atlas-slug` skill with a complete pipeline.

## When to Use

- Renaming a research project (directory, slug, or title)
- When the user says "rename project", "rename topic", "rename slug", "change project name"
- After deciding a project's working title should change
- When merging two projects (rename one to match the other)

## Input

| Parameter | Format | Required |
|-----------|--------|----------|
| Old name | Project name, slug, or directory name | Yes |
| New name | Project name, slug, or directory name | Yes |

If the user provides natural-language names, derive:
- **Slug** (kebab-case): `new-project-name`
- **Directory name** (Title Case): `New Project Name`
- **Display title** (natural): `New Project Name`

Confirm all three forms before proceeding.

## Processing Steps

### Phase 1: Verify and Plan

1. **Resolve old project** — find the atlas topic file:
   ```bash
   TM="$(cat ~/.config/task-mgmt/path)"
   grep -rl "project_path:.*<old-basename>" ~/vault/atlas/ 2>/dev/null
   ```
   If not found, search by slug: `find ~/vault/atlas/ -name "<old-slug>.md"`

2. **Read atlas topic** — extract: theme, title, project_path, outputs, connected_topics

3. **Locate project directory** — resolve from `project_path:` field:
   ```bash
   RESEARCH_ROOT="$(cat ~/.config/task-mgmt/research-root)"
   ls -d "$RESEARCH_ROOT/<project_path>" 2>/dev/null
   ```

4. **Inventory what needs renaming:**

   | System | What to check |
   |--------|--------------|
   | Local directory | `$RESEARCH_ROOT/<theme>/<Old Name>/` |
   | Atlas topic file | `~/vault/atlas/<theme>/<old-slug>.md` |
   | Atlas connected_topics | All topic files referencing old slug |
   | Vault theme file | `~/vault/themes/{theme-slug}.md` (verify topic_count if maintained) |
   | Atlas paperpile.md | Folder reference |
   | Project CLAUDE.md | Title, slug, any self-references |
   | Project README.md | Title |
   | Project MEMORY.md | Title in header |
   | Project .context/ | current-focus.md, project-recap.md titles |
   | vault atlas entry | Name, Atlas Slug property |
   | vault submission entries | Submission name |
   | Paper directories | Overleaf symlink targets (may need new Overleaf project names) |
   | Backup directory | backup/ subdirectory names |
   | TM _index.md | Project row in Papers in Progress table |
   | TM current-focus.md | Any references to old name |
   | Git | No rename needed (repo stays at same path after dir rename) |

5. **Present plan** — show the full rename map and wait for confirmation.

### Phase 2: Atlas Rename (Steps 1–11 from old rename-atlas-slug)

#### 2.1 Rename topic file
```bash
mv ~/vault/atlas/{theme}/{old-slug}.md ~/vault/atlas/{theme}/{new-slug}.md
```

#### 2.2 Update YAML frontmatter
In the renamed file, update:
- `title:` → new display title
- `project_path:` → `<theme>/<New Directory Name>`
- Leave other fields unchanged

#### 2.3 Update connected_topics (all files)
Grep all topic files for old slug in `connected_topics` arrays. Replace exact matches only.

#### 2.4 Verify theme directory
The topic file is already in the correct theme directory after the rename in 2.1. No separate slug list to update — themes are individual files at `~/vault/themes/`.

#### 2.5 Update paperpile.md
Rename folder entry if present.

#### 2.6 Update merge-reviewed.md
Replace old slug if present. Skip if file doesn't exist.

#### 2.7 Check prose references
Grep all topic bodies for prose mentions of old slug. Update found references.

#### 2.8 Regenerate RECAP.md
```bash
uv run python packages/atlas-vault/generate_recap.py
```

#### 2.9 Verify atlas clean
Grep entire `packages/atlas-vault/` for remaining old slug references.

### Phase 3: Local Project Rename

#### 3.1 Rename directory
```bash
mv "$RESEARCH_ROOT/<theme>/<Old Name>" "$RESEARCH_ROOT/<theme>/<New Name>"
```

#### 3.2 Update project CLAUDE.md
- Title heading
- `**Slug:**` field
- Any self-references in text

#### 3.3 Update project README.md
- Title heading

#### 3.4 Update project MEMORY.md
- Header: `# Knowledge Base — <New Name>`

#### 3.5 Update project .context/
- `current-focus.md` title
- `project-recap.md` title

#### 3.6 Update Overleaf symlinks
For each `paper*/paper` symlink, check if the target path contains the old name:
```bash
for link in paper*/paper; do
  target="$(readlink "$link")"
  if [[ "$target" == *"<Old Name>"* ]]; then
    echo "⚠ Symlink $link points to target containing old name: $target"
    echo "  Overleaf project may need manual rename in Overleaf UI"
  fi
done
```
**Do NOT** rename Overleaf folders — renaming loses Overleaf project history. The user must rename via the Overleaf UI. Flag as manual TODO and only update the symlink after the user confirms the rename is done.

#### 3.7 Git re-init (if needed)
If git repo was at old path, it moves with the directory. No action needed unless there's a remote with the old name.

### Phase 4: Vault Rename

#### 4.1 Find and update topic entry
```bash
# Search for topic
# Use `taskflow-cli search-tasks --query "<old-name>" --json` to find, then edit the vault markdown file directly
curl -s -X PATCH "https://vault file edit (~/vault/)/<topic-id>" \
  # vault files are local — no auth needed \
  -H "Content-Type: text/markdown" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Name": {"title": [{"text": {"content": "<New Name>"}}]}, "Atlas Slug": {"rich_text": [{"text": {"content": "<new-slug>"}}]}}}'
```

#### 4.2 Update submission entries
For each submission entry, update the `Submission` name if it contains the old name.

### Phase 5: Task Management Updates

#### 5.1 Update _index.md
Find and update the project row in `.context/projects/_index.md`.

#### 5.2 Update current-focus.md
Replace old project name references in `.context/current-focus.md`.

#### 5.3 Update papers context file
Rename `.context/projects/papers/<old-name>.md` → `<new-name>.md` if it exists. Update title inside.

#### 5.4 GitHub artifact repo rename (with anonymous-URL safety check)

If `<project>/github-repo/` exists with a GitHub remote whose name embeds the old slug:

1. **Check for live anonymous URLs** — read the matching vault submission frontmatter at `~/vault/submissions/<old-slug>-<venue>-<year>.md` (and any other submissions for this paper). Look for `anonymous_repo:`.

2. **If `anonymous_repo:` is set:**
   - The 4open.science URL is **immutable** and embeds the GitHub repo's old name. Renaming the GitHub repo would break the anonymous mirror — reviewers may currently be reading it.
   - **Default behaviour: skip the GH rename.** Print a warning explaining the trade-off and leave the existing GH repo + 4open.science mirror untouched.
   - Prompt the user with three options: (a) skip GH rename (default), (b) rename anyway and accept that the 4open.science URL will break — useful only if reviewing is over and the mirror is no longer needed, (c) defer the rename until after a future re-submission cycle creates a new artifact under the new name.

3. **If no `anonymous_repo:` is set** (no double-blind submission active):
   - Rename via `gh repo rename user/<old-repo-name> <new-repo-name>` from inside `github-repo/`.
   - Update `github-repo/.git/config` remote URL (gh handles this automatically when `gh repo rename` runs locally).
   - Naming follows whichever mode applies: Mode A (`<venue>-<year>-<new-slug>-artifact`) or Mode B (`paper-<theme>-<new-slug>`). See `init-project-research/references/github-release-repo.md`.

4. **Update vault submission `artifact_repo:` field** to the new GitHub URL. Atlas `outputs[].artifact_repo:` likewise. Same atomicity rule as `/anonymous-artifact` Phase 6 — apply all writebacks together or none.

### Phase 6: Verification

1. **Grep for old name** across all systems:
   ```bash
   grep -r "<old-slug>" "$TM/packages/atlas-vault/" 2>/dev/null
   grep -r "<Old Name>" "$RESEARCH_ROOT/<theme>/<New Name>/" 2>/dev/null
   grep -r "<old-slug>\|<Old Name>" "$TM/.context/" 2>/dev/null
   ```

2. **Report remaining references** that couldn't be auto-fixed.

3. **List manual TODOs:**
   - Overleaf project rename (if symlink targets contain old name)
   - Paperpile/Paperpile folder rename on Google Drive
   - Any external references (email threads, shared docs)

## Anti-Patterns

- Do NOT rename Overleaf folders — this destroys project history. User must rename via Overleaf UI
- Do NOT rename Paperpile folders automatically — flag as manual TODO
- Do NOT edit RECAP.md directly — always regenerate via script
- Do NOT use Edit without first reading the file
- Do NOT do partial slug matches — `"old-slug"` must match exactly
- Do NOT proceed without confirmation after presenting the plan
- **Do NOT strip references to the renamed project from other atlas topics, vault submissions, or context files.** Rename the *symlink and target* to the new name; inbound references must be *updated to the new name*, never removed. Deleting references breaks the reference graph and loses history. If a reference seems redundant, flag it for manual review — do not delete.

## Output

After completion, report:

```
Project renamed: <Old Name> → <New Name>

Systems updated:
  Atlas topic file:    ✓ renamed + frontmatter updated
  Atlas cross-refs:    ✓ N files updated
  Theme directory:     ✓ verified
  Local directory:     ✓ renamed
  Project CLAUDE.md:   ✓ title + slug updated
  Project README.md:   ✓ title updated
  Vault atlas:        ✓ Name + Atlas Slug updated
  Vault submissions:  ✓ N entries updated
  TM _index.md:        ✓ row updated
  TM current-focus.md: ✓ references updated
  RECAP.md:            ✓ regenerated

Manual TODOs:
  - [ ] Rename Overleaf project(s) in Overleaf UI
  - [ ] Rename Paperpile folder on Google Drive

Remaining references: [list or "none"]
```

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/audit-project-research` | Run after rename to verify structure |
| `/session-close` | Atlas cross-ref check will validate the rename |
| `vault sync (edit vault files directly)` | Can be used for follow-up vault sync if needed |
| `/sync-atlas` | Can be used for follow-up atlas-vault sync |
