# Phase 2.8 — GitHub release repo

> If `github-repo/` exists at project root, validate its structure and hygiene. If the project is Computational or Experimental and has no `github-repo/`, this is informational only.

| Check | What to look for | Severity |
|-------|-----------------|----------|
| Has own `.git` | `test -d github-repo/.git` | Missing — "github-repo/ exists but has no .git" |
| In `.gitignore` | `grep -q 'github-repo' .gitignore` | Missing — "nested repo will cause issues" |
| Has GitHub remote | `git -C github-repo remote -v \| grep github` | Degraded — "No GitHub remote configured" |
| No forbidden files | No `CLAUDE.md`, `.claude/`, `MEMORY.md`, `paper*/`, `reviews/`, `.context/`, `log/` inside | Missing — "contains private files that must not be published" |
| Has README.md | `test -f github-repo/README.md` | Degraded — "Public release needs a README" |

Convention details: `init-project-research/references/round-2-github.md` (after init's recent rewrite).
