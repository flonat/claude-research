# Phase 7 — Task Management Integration

> Audits init's Phase 8 outputs. Verifies the project has Task Management context library entries with the right shape.

Resolve `TM_ROOT="$(cat ~/.config/task-mgmt/path)"` first.

## 7.1 Index row

Check `$TM_ROOT/.context/projects/_index.md` has a row for the project's slug.

| Check | What to look for | Severity |
|-------|-----------------|----------|
| Row exists | `grep -F "$slug" .context/projects/_index.md` returns a hit | Missing |
| Row not stale | Row's stage column matches CLAUDE.md status (Idea / Drafting / Submitted / R&R / Published) | Info if drifted |

## 7.2 Paper context file

Check `$TM_ROOT/.context/projects/papers/<short-name>.md` exists.

| Check | What to look for | Severity |
|-------|-----------------|----------|
| File exists | `test -f .context/projects/papers/<short>.md` | Missing |
| Has frontmatter | First line is `---` and frontmatter parses as YAML | Degraded |
| Frontmatter keys present | `title`, `slug`, `theme`, `venue`, `stage` exist | Degraded if any missing |

## 7.3 Current-focus mention

Check `$TM_ROOT/.context/current-focus.md` mentions the project's slug somewhere (Top 3 Active Projects or Open Loops).

| Check | What to look for | Severity |
|-------|-----------------|----------|
| Slug appears | `grep -F "$slug" .context/current-focus.md` returns a hit | Missing |

If the project is `status: Idea` and < 7 days old, demote Missing to Info — current-focus mention may not have happened yet.
