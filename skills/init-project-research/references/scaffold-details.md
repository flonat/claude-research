# Scaffold Details

> Templates, directory structures, and reference material used by `/init-project-research`. The SKILL.md has pointers here — read this when executing the relevant phase.

---

## Venues & Correspondence Structure

When a target venue is known from the interview, seed the venue folder and correspondence directory:

```
docs/venues/<venue-slug>/      # e.g., docs/venues/ejor/, docs/venues/mcdm-2026/
└── submission/                # .gitkeep — for initial submission materials

correspondence/
└── referee-reviews/            # .gitkeep — for review rounds (seeded by /process-reviews)
```

As the project progresses through submission and revision cycles, material splits across two locations:

**`docs/venues/`** — submission and venue material only:
```
docs/venues/<venue-slug>/
├── submission/                # Original submission
│   ├── <Paper Title>.pdf      # Compiled PDF as submitted
│   └── source/                # LaTeX source snapshot (optional)
└── camera-ready/              # Final accepted version
```

**`correspondence/referee-reviews/`** — reviewer exchanges per round:
```
correspondence/referee-reviews/<venue>-round<N>/
├── reviews-original.pdf       # What reviewers sent
├── rebuttal.md                # What we send back
└── analysis/                  # Our work on their feedback
    ├── comment-tracker.md
    ├── review-analysis.md
    └── reviewer-comments-verbatim.tex
```

**`docs/<venue>/internal-reviews/`** — internal review work (not round-specific):
```
docs/<venue>/internal-reviews/
├── referee2-report.md         # Referee2 agent analysis
└── referee2-deck.tex          # Summary deck
```

---

## Conference Submission Checklist Template

For **conference venues**, seed a `submission-checklist.md` inside the venue folder:

```markdown
# <Conference Name> Submission Checklist

## Venue Details
- **Conference:** <name> (<acronym>)
- **CORE ranking:** <ranking>
- **Page limit:** <N pages + refs>
- **Format:** <template>
- **Review type:** <type>
- **Anonymisation:** <yes/no>

## Key Dates
- [ ] Submission deadline: <date>
- [ ] Notification: <date>
- [ ] Camera-ready: <date>
- [ ] Conference: <dates>

## Pre-Submission
- [ ] Page count within limit
- [ ] Correct LaTeX template used
- [ ] Anonymisation applied (if required) — use `/export-project-anon`
- [ ] All figures render correctly
- [ ] Bibliography complete — run `/validate-bib`
- [ ] Proofread — run `/proofread`
- [ ] AI traces removed — run `/export-project-clean`

## Submission
- [ ] Paper uploaded to submission system
- [ ] Supplementary materials attached (if any)
- [ ] Author information entered correctly
- [ ] Conflicts of interest declared
```

---

## Papers Context File Template

Used in Phase 6 when creating `.context/projects/papers/<short-name>.md`:

```markdown
# <Working Title>

## Overview
<Abstract/elevator pitch>

## Status
<Stage> — project just initialised

## Key Details
- **Authors:** <names>
- **Affiliation:** <institution>
- **Target:** <venue> (<deadline>)
- **Design:** <methodology>

## Links
- **Overleaf:** <external link>
- **GitHub:** <URL or "local-only">
- **Notion:** <URL — added after Notion entry created>
- **Project folder:** <relative path>

## Research Questions
1. <RQ1>
2. <RQ2>
3. <RQ3>

## Key Decisions
<empty — to be populated>

## Completed
- [x] Project folder structure + Overleaf symlink
- [x] Git initialised
- [x] Context library entries created
- [x] Notion Research Pipeline entry

## Action Items
- [ ] Literature review
- [ ] <First concrete next step based on project type>
```

---

## Expected Post-Init Growth

Projects naturally grow beyond the initial scaffold. These items are **not** created by `/init-project-research` but are recognized as valid by `/audit-project-structure`:

| Growth item | When it appears | Purpose |
|-------------|----------------|---------|
| `experiments/` | Computational projects with parameter sweeps | Experiment configs, sweep logs, results |
| `experiments/configs/` | Sub-directory for sweep YAML/JSON files | Parameter sweep definitions |
| `scripts/` | When utility scripts accumulate | One-off data processing, plotting scripts |
| `legacy/` | After refactoring or restructuring | Preserves old code/data safely (per `/project-safety`) |
| `correspondence/referee-reviews/<venue>-roundN/` | After receiving R&R | Reviewer comments, rebuttal, analysis |
| `docs/<venue>/internal-reviews/` | After running referee2 agent | Internal review reports (not round-specific) |
| `docs/venues/<venue>/camera-ready/` | After acceptance | Final camera-ready version |
| `notes.md` | Early research phase | Quick research notes, meeting summaries |
| `SETUP.md` | Computational projects with dependencies | Environment setup for collaborators |
| `pyproject.toml` / `.venv/` | Python-heavy projects | Package management |

---

## Overleaf Symlink Commands (Phase 4)

### 4a. Create symlink

```bash
OVERLEAF_PATH="$HOME/Library/CloudStorage/YOUR-CLOUD/Apps/Overleaf/<overleaf-name>"
PROJECT_PATH="<project-path>"

# Verify Overleaf directory exists
ls "$OVERLEAF_PATH"

# Create symlink
ln -s "$OVERLEAF_PATH" "$PROJECT_PATH/paper"

# Verify it resolves
ls "$PROJECT_PATH/paper/"
```

If the Overleaf directory doesn't exist, warn the user but still create the symlink (it will resolve once Overleaf creates the folder).

### 4b. Seed template files

If a template was selected in Round 2 (not "None"):

1. Check whether the Overleaf folder already has `.tex` files
2. If existing content, ask: "The Overleaf folder already has files. Overwrite with template, or skip?"
3. If empty or overwrite confirmed:

```bash
TEMPLATE_PATH="<Task Management>/templates/<template-slug>"
rsync -av --exclude='.git' --exclude='.gitignore' --exclude='out/' "$TEMPLATE_PATH/" "$PROJECT_PATH/paper/"
```

### 4c. Ensure `.latexmkrc` exists

Check whether `paper/.latexmkrc` exists. If not, create it:

```perl
$out_dir = 'out';
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
```
