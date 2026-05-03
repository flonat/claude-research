# Round 2 Q5 — GitHub Release Repo

> Referenced from: `init-project-research/SKILL.md` Phase 1, Round 2, Q5.

Only ask this question for **Experimental, Computational, or Mixed** projects. Theoretical projects skip it.

## Question

"GitHub release repo? — Yes / No / Later."

## Behaviour by answer

| Answer | What to do |
|--------|-----------|
| **Yes** | Create a `github-repo/` subdirectory at project root with its own git repo for public code releases. Initialise empty (no first commit yet). The user will populate it manually when ready to release. |
| **Later** | Add `github-repo/` to the project's `.gitignore` so it's reserved as a placeholder. The user can run `git init github-repo` when ready. |
| **No** | Do nothing. Project root git tracks code in place. |

## Convention

- The release repo is a **separate repo** from the project's main git history. This keeps the public artefact clean (no draft commits, no internal correspondence in history).
- Naming: `user/<project-slug>-replication` for replication packages, `user/<project-slug>` for general code.
- License: MIT for code, CC-BY-4.0 for data, unless the user specifies otherwise.
- Replication packages should follow `/replication-package` conventions.

Full release-repo conventions: [`github-release-repo.md`](github-release-repo.md).
