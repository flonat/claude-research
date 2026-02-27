# Seed File Templates

> Templates for Phase 3 of `/init-project-research`. Replace `<placeholders>` with interview answers.

## CLAUDE.md

```markdown
# Claude Context for <Working Title>

## Project Overview
- **Working title:** <title>
- **Authors:** <names>
- **Venue type:** <journal/conference/preprint>
- **Target venue:** <name>
- **Deadline:** <date or "No fixed deadline">
- **Type:** <experimental/computational/theoretical/mixed>

### Venue Details
<!-- Use ONE of the blocks below based on venue type -->

<!-- IF JOURNAL -->
- **CABS AJG:** <ranking>
- **WBS 60:** <yes/no>
- **FT 50:** <yes/no>
<!-- END JOURNAL -->

<!-- IF CONFERENCE -->
- **CORE ranking:** <A*/A/B/C>
- **Page limit:** <N pages + refs>
- **Format:** <template name>
- **Review type:** <double-blind/single-blind/open>
- **Anonymisation:** <yes/no>
- **Submission deadline:** <date>
- **Notification:** <date>
- **Camera-ready:** <date>
- **CfP link:** <URL>
<!-- END CONFERENCE -->

## Research Questions
1. <RQ1>
2. <RQ2>
3. <RQ3>

## Methodology
<One-line methodology overview>

## Setup

### Overleaf
- **Symlink:** `paper/` → `~/...Dropbox.../Apps/Overleaf/<overleaf-name>/`
- **External link:** <URL>
- **To recreate symlink:** `ln -s "<overleaf-path>" "<project-path>/paper"`

### GitHub
<URL or "Local-only (synced via Dropbox)">

### Collaborators
<Names, affiliations, contact if provided>

## Folder Structure
```
<tree of the created structure>
```

## Conventions
- Compile LaTeX: build artifacts to `out/`, PDF copied back to source directory via `.latexmkrc`
- Use `uv` for Python, never bare `pip` or `python`
- Canonical bibliography: `paper/paperpile.bib`
- Citation keys: Paperpile format (e.g., `AuthorYYYY-xx`)
- **Overleaf separation:** `paper/` is LaTeX source ONLY — no code, data, or scripts. All code goes in `code/` or `src/`, all data in `data/`. Only exported figures/tables go into `paper/`.

## Session Continuity
- Update `.context/current-focus.md` at end of each session
- Use `.context/project-recap.md` for research design notes
- Session logs go in `log/`
```

## README.md

```markdown
# <Working Title>

**Authors:** <names>
**Affiliation:** <institution>
**Target:** <venue> (<deadline or "ongoing">)

## Abstract
<elevator pitch>

## Links
- **Overleaf:** <external link>
- **GitHub:** <URL or "local-only">

## Status
- [ ] Literature review
- [ ] Research design
- [ ] Data collection
- [ ] Analysis
- [ ] Drafting
- [ ] Submission
```

## .gitignore

```gitignore
# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp

# Data (regenerable or too large for git)
data/
output/
results/

# Paper (tracked in Overleaf)
paper/

# Logs
log/

# Unsorted inbox
to-sort/

# Python
__pycache__/
*.pyc
.venv/
*.egg-info/
dist/
build/

# R
.Rhistory
.RData
.Rproj.user/

# LaTeX build artifacts
*.aux
*.bbl
*.blg
*.fdb_latexmk
*.fls
*.log
*.out
*.synctex.gz
*.toc
out/
```

## MEMORY.md

Seed MEMORY.md at project root based on project type. Use the **research** template by default; use the **teaching** template for teaching or workshop projects.

### Research Template

```markdown
# Memory — <Working Title>

## Notation Registry

| Variable | Convention | Anti-pattern |
|----------|-----------|--------------|
| | | |

## Citations

<!-- One-liner [LEARN:citation] corrections go here -->

## Estimand Registry

| What we estimate | Identification | Key assumptions |
|-----------------|---------------|-----------------|
| | | |

## Key Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| | | |

## Anti-Patterns

| What went wrong | Correction |
|----------------|------------|
| | |

## Code Pitfalls

| Bug | Impact | Fix |
|-----|--------|-----|
| | | |
```

### Teaching Template

```markdown
# Memory — <Course/Workshop Name>

## Lecture Progression

| Topic | Core question | Key method |
|-------|--------------|------------|
| | | |

## Student Misconceptions

| Misconception | Correction | How to address |
|--------------|------------|----------------|
| | | |

## Empirical Applications

| Paper | Dataset | Purpose |
|-------|---------|---------|
| | | |

## Code Pitfalls

| Bug | Impact | Fix |
|-----|--------|-----|
| | | |
```

## .context/current-focus.md

```markdown
# Current Focus

> Project just initialised. Update this file at the end of each session.

## Next Steps
1. <First logical step based on project type>
2. Set up bibliography in Overleaf
3. Begin literature review
```

## .context/project-recap.md

```markdown
# Project Recap: <Working Title>

## Abstract
<elevator pitch>

## Research Questions
1. <RQ1>
2. <RQ2>
3. <RQ3>

## Methodology
<overview>

## Key Decisions
<empty — to be populated as the project evolves>

## References
<empty — add key papers as literature review progresses>
```

## .claude/hooks/copy-paper-pdf.sh

PostToolUse hook that copies compiled paper PDFs to project root after LaTeX compilation. Multi-paper-safe: scans for all `paper*` directories/symlinks and copies each `main.pdf` to `<dirname>_vcurrent.pdf`.

```bash
#!/usr/bin/env bash
# PostToolUse hook: copy compiled paper PDFs to project root after LaTeX compilation
# Scans for all paper* directories and copies each main.pdf → <dirname>_vcurrent.pdf
# Only copies when source is newer; silently skips missing PDFs

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

for paper_dir in "$PROJECT_ROOT"/paper*; do
    [ -d "$paper_dir" ] || [ -L "$paper_dir" ] || continue
    dirname="$(basename "$paper_dir")"
    src="$paper_dir/main.pdf"
    dest="$PROJECT_ROOT/${dirname}_vcurrent.pdf"
    if [ -f "$src" ]; then
        if [ ! -f "$dest" ] || [ "$src" -nt "$dest" ]; then
            cp "$src" "$dest"
        fi
    fi
done
```

After creating the hook script, the PostToolUse hook must also be registered in `.claude/settings.local.json`. Add the following to the `hooks` key:

```json
"hooks": {
    "PostToolUse": [
        {
            "matcher": "Bash",
            "hooks": [
                {
                    "type": "command",
                    "command": ".claude/hooks/copy-paper-pdf.sh"
                }
            ]
        }
    ]
}
```
