# GitHub Release Repo Convention

> Convention for maintaining a public GitHub code release alongside a Dropbox-synced research project.

## Problem

Research projects live in Dropbox-synced directories with local-only git (no remote). When a paper is submitted or accepted, the code needs to be released publicly on GitHub. But the project directory contains private files (CLAUDE.md, AI context, paper drafts, personal notes) that must never be published.

## Solution: `github-repo/` Subdirectory

A `github-repo/` directory at the project root acts as a **separate git repository** with its own `.git` pointing to a GitHub remote. It contains only public-safe code.

```
<Project>/
├── .git/                  # Main project git (local-only, Dropbox-synced)
├── github-repo/           # Separate git repo → GitHub
│   ├── .git/              # Points to user/paper-{theme}-{slug}
│   ├── capemobo/          # Python package (or src/)
│   ├── experiments/       # Experiment runners + results
│   ├── pyproject.toml     # Dependencies
│   ├── uv.lock            # Lock file
│   └── README.md          # Public-facing README
├── paper-wsc/             # Paper (NOT in github-repo)
├── CLAUDE.md              # AI context (NOT in github-repo)
└── ...
```

## Naming Convention

GitHub repo name: `paper-{theme-abbrev}-{slug}`

Examples:
- `paper-or-cost-aware-simulation`
- `paper-or-indifference-adjustments`
- `paper-bds-identity-belief-alignment`

Theme abbreviations follow the Overleaf naming convention (OR, BDS, ASG, etc.).

## What Goes In `github-repo/`

| Include | Exclude |
|---------|---------|
| Python/R package source | `CLAUDE.md`, `.claude/` |
| Experiment runners | `paper*/` directories |
| Configuration files | `.context/`, `log/` |
| `pyproject.toml`, `uv.lock` | `MEMORY.md` |
| `README.md` (public-facing) | `docs/` (internal notes) |
| Results/output (if small) | `backup/`, `to-sort/` |
| `.gitignore` | `reviews/`, `correspondence/` |
| Data (if public/synthetic) | `knowledge/` |

**Critical exclusions:**
- No `CLAUDE.md` or `.claude/` — reveals AI tooling
- No paper files — tracked in Overleaf, not GitHub
- No personal context — session logs, focus files, memory files
- No AI trace files — review reports, critic reports

## Setup (during init or at release time)

```bash
# 1. Create the directory
mkdir -p github-repo

# 2. Initialize git
cd github-repo
git init
git branch -m main

# 3. Create GitHub repo and set remote
gh repo create "user/paper-{theme}-{slug}" --private --source=. --remote=origin

# 4. Copy public-safe files (example for computational project)
# Use rsync or cp — NOT symlinks
rsync -a --exclude='__pycache__' --exclude='.venv' ../code/capemobo/ capemobo/
rsync -a --exclude='__pycache__' --exclude='.venv' ../code/experiments/ experiments/
cp ../code/pyproject.toml .
cp ../code/uv.lock .

# 5. Create public README.md
# (Write a clean README without AI references)

# 6. Create .gitignore
cat > .gitignore << 'EOF'
.DS_Store
__pycache__/
*.pyc
.venv/
*.egg-info/
dist/
build/
EOF

# 7. Initial commit + push
git add .
git commit -m "Initial release: code for [paper title]"
git push -u origin main

# 8. Tag release (if submitting)
git tag -a v1.0.0 -m "v1.0.0: Code for [venue] submission"
git push origin v1.0.0
```

## Main Project `.gitignore`

`github-repo/` must be in the main project's `.gitignore` since it's a nested git repo:

```gitignore
# GitHub release repo (separate git repo)
github-repo/
```

## Updating the Release

When code changes after initial release:

```bash
cd github-repo

# Sync updated files from project
rsync -a --delete --exclude='.git' --exclude='__pycache__' --exclude='.venv' \
  ../code/capemobo/ capemobo/
rsync -a --delete --exclude='.git' --exclude='__pycache__' --exclude='.venv' \
  ../code/experiments/ experiments/
cp ../code/pyproject.toml .
cp ../code/uv.lock .

# Review, commit, push
git add .
git diff --cached --stat
git commit -m "Update: [description]"
git push
```

## Release Workflow

| Event | Action |
|-------|--------|
| Paper submitted | Create `github-repo/`, push code, tag `v1.0.0`, create GitHub release (private repo) |
| Camera-ready | Update code if needed, tag `v1.1.0` |
| Paper published | Make GitHub repo public, update README with citation |
| Major revision | Update code, tag `v2.0.0` |

## Visibility

- **Pre-acceptance:** Private GitHub repo
- **Post-acceptance:** Make public (`gh repo edit --visibility public`)
- **Always:** README includes citation info (add DOI after publication)

## When NOT to Create

- Theoretical projects with no code
- Projects where code is trivial (< 100 lines, single script)
- Projects using shared infrastructure that's released separately
