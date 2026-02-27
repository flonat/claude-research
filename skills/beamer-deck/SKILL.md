---
name: beamer-deck
description: "Generate academic Beamer presentations with multi-agent review. Builds original themes, applies rhetoric principles, iterates until zero warnings."
allowed-tools: Bash(latexmk*), Bash(xelatex*), Bash(pdflatex*), Bash(biber*), Bash(bibtex*), Bash(mkdir*), Bash(ls*), Bash(R*), Bash(Rscript*), Bash(python*), Read, Write, Edit, Task
argument-hint: [topic, content-path, or project-name]
---

# Beamer Deck Skill

> Generate academic Beamer presentations with original themes, rhetoric-driven structure, and multi-agent review. Internalises Scott Cunningham's rhetoric framework and implements an adversarial review workflow.

## Purpose

Create polished, zero-warning Beamer decks for academic contexts: seminars, conference talks, teaching lectures, and working decks for coauthors. Every deck gets a custom theme, assertion-driven titles, and parallel review by rhetoric and graphics sub-agents.

**NOT for project status updates** — use `/project-deck` for those.

## When to Use

- Academic seminar presentations
- Conference talks (15–45 min)
- Teaching lectures (undergraduate or PhD)
- Working decks for coauthors or supervisors
- Any presentation that needs rhetoric discipline and visual quality

---

## Critical Rules

1. **Build artifacts go to `out/`, PDF stays in the source directory.** Create `.latexmkrc` with `$out_dir = 'out'` and an `END {}` block to copy the PDF back if missing. Use `/latex-autofix` for compilation — it handles error resolution automatically. See `/latex` for manual config details.
2. **Python:** Always use `uv run python`. Never bare `python`, `python3`, `pip`, or `pip3`.
2. **Fix ALL warnings.** Overfull hbox, underfull hbox, overfull vbox, underfull vbox — no matter how small. Parse the `.log` file. Recompile until clean.
3. **Titles are assertions, not labels.** "Distance increases abortion rates" — not "Results". Every frame title states a claim.
4. **One idea per slide.** Not a guideline. A law. If a slide has two ideas, split it.
5. **Original themes only.** Never use default Beamer themes (Warsaw, Madrid, etc.) as-is. Define colours and templates inline in the `.tex` file — no separate `.sty` files.
6. **Code-first figures.** Generate figures via R or Python scripts before inserting. Never use placeholder images. **Always save the script alongside the figures** — never generate a figure without preserving the code that created it.
7. **If a `.bib` file is used, validate it.** Cross-reference all `\cite{}` keys against the bibliography file. See `/validate-bib` for the full protocol.

---

## Rhetoric Principles

Full framework (Three Laws, MB/MC, Aristotelian Triad, Narrative Arc, Pyramid Principle, Devil's Advocate): [`../shared/rhetoric-principles.md`](../shared/rhetoric-principles.md)

Scott's original essay: `resources/academics/scott-cunningham/MixtapeTools/presentations/rhetoric_of_decks.md`

---

## Quality Scoring

Apply numeric quality scoring using the shared framework and skill-specific rubric:

- **Framework:** [`../shared/quality-scoring.md`](../shared/quality-scoring.md) — severity tiers, thresholds, verdict rules
- **Rubric:** [`references/quality-rubric.md`](references/quality-rubric.md) — issue-to-deduction mappings for this skill

Start at 100, deduct per issue found, apply verdict. Compute the score in Phase 7 and report it in the final output.

## Context-Specific Guidance

See [`../shared/rhetoric-principles.md`](../shared/rhetoric-principles.md) for the full Aristotelian Triad framework. Context-specific Ethos/Pathos/Logos balance and adjustments are applied in Phase 2 based on audience type (academic seminar, conference talk, teaching lecture, working deck).

---

## Workflow: 7 Phases

```
You (orchestrator)
├── Phase 1: Gather context        (direct)
├── Phase 2: Design structure       (direct)
├── Phase 3: Build deck             (direct)
├── Phase 4: Fix all warnings       (direct)
├── Phase 5: Rhetoric review        (sub-agent — Explore)
├── Phase 6: Graphics review        (sub-agent — Explore)  ← parallel with Phase 5
└── Phase 7: Apply & finalise       (direct)
```

### Phase 1: Gather Context (Direct)

Read project files, content sources, and audience brief. Ask the user clarifying questions:

- **Audience**: Who is this for? (seminar, conference, teaching, coauthors)
- **Duration**: How long is the talk?
- **Content source**: Paper draft? Notes? Existing slides? Code output?
- **Special requirements**: Specific figures, institutional branding, language?

Check for existing `.bib` files in the project. If citations are needed, note this for Phase 3.

### Phase 2: Design Structure (Direct)

1. **Choose rhetoric balance** based on audience (see table above)
2. **Outline slide sequence** with assertion titles — write each title as a claim
3. **Plan narrative arc** — identify Act I/II/III transitions
4. **Choose colour palette** — original, appropriate to audience tone (see Reference Palettes below for starting points)
5. **Identify figures needed** — which need to be generated via code?

Present the outline to the user for approval before building.

### Phase 3: Build Deck (Direct)

1. **Generate figures first** — run R/Python scripts, save to `figures/`
2. **Write `.tex` file** with inline theme (colours, templates, fonts — all in one file, no `.sty`)
3. **Use 16:9 aspect ratio** (`\documentclass[aspectratio=169,11pt]{beamer}`)
4. **Create `.latexmkrc`** if not present (`$out_dir = 'out'` + `END {}` block to copy PDF back)
5. **Compile using `/latex-autofix`** — this handles missing packages, font conflicts, citation key mismatches, and stale cache automatically
6. **If using citations**: add `\addbibresource{paperpile.bib}` or `\bibliography{}` as appropriate

### Phase 4: Fix All Warnings (Direct)

After `/latex-autofix` resolves errors, address remaining **warnings** (which autofix does not fix):

1. Parse `out/*.log` for overfull/underfull hbox/vbox warnings
2. Fix every single one — adjust text, resize figures, tweak `\parbox`, etc.
3. Recompile
4. Repeat until the log is clean

**"Compilation success does not mean visual success."** Also check for silent visual errors:
- TikZ: shape constraints forcing label misplacement, coordinate misalignment. **If the deck contains TikZ diagrams**, run the 6-pass verification from [`../shared/tikz-rules.md`](../shared/tikz-rules.md) — compute Bezier depths, check gaps, verify label fit, check shape boundary clearance.
- matplotlib/ggplot: axis labels cut off, legend obscuring data, text sizing. **If figures use curved arrows (`arc3`)**, compute Bézier positions using the helper functions in `../shared/tikz-rules.md` § Matplotlib Extension — never guess where curves pass. Check label-to-shape clearance (Boundary Rule) and use anchor-based centering for text pairs.
- **PDF visual inspection**: Run `uv run python scripts/pdf-to-images.py <deck>.pdf` to convert pages to images, then inspect each image for text overflow, element overlap, font readability, and alignment issues that are invisible in the log

### Phase 5: Rhetoric Review (Sub-Agent — Explore)

Launch a sub-agent to review the `.tex` file against 7 criteria: narrative arc, MB/MC balance, title quality, one-idea-per-slide, transitions, Aristotelian balance, and pyramid principle.

Full prompt template: [`references/review-prompts.md`](references/review-prompts.md) § Rhetoric Review

### Phase 6: Graphics Review (Sub-Agent — Explore)

Launch **in parallel with Phase 5**. Reviews TikZ diagrams, figure sizing, table formatting, colour consistency, typography, and numerical accuracy.

Full prompt template: [`references/review-prompts.md`](references/review-prompts.md) § Graphics Review

### Phase 7: Apply and Finalise (Direct)

1. Read both reviewer reports
2. Incorporate feedback — prioritise Critical and Needs Work items
3. Recompile
4. Verify zero warnings in the log
5. **If using a `.bib` file**: validate all `\cite{}` keys resolve correctly (check log for `Citation .* undefined`). See `/validate-bib` for the full cross-referencing protocol.
6. If significant changes were made, loop back to Phase 5 for another review round
7. **Compute quality score** — read `references/quality-rubric.md`, log all issues from Phases 4-6, compute score and verdict
8. Confirm final PDF is in the source directory (copied from `out/` by `.latexmkrc`)

---

## Reference Palettes

Three starting palettes (Professional, Energetic, Academic) in both LaTeX and CSS formats: [`../shared/palettes.md`](../shared/palettes.md)

Use as inspiration — always create an original palette for each deck.

---

## Output Checklist

A completed deck directory should contain:

```
project/
├── deck.tex              # Main Beamer file (inline theme)
├── deck.pdf              # Compiled PDF (copied from out/ by .latexmkrc)
├── .latexmkrc            # Output directory config
├── out/                  # Build artifacts only
├── figures/              # Generated figures (if any)
│   ├── figure_1.png
│   └── ...
├── scripts/              # R/Python scripts that generated figures (if any)
│   ├── figure_1.R
│   └── ...
└── paperpile.bib         # Bibliography (if citations used)
```

- [ ] PDF compiles with zero warnings
- [ ] All frame titles are assertions
- [ ] One idea per slide
- [ ] Narrative arc: Problem → Investigation → Resolution
- [ ] Rhetoric review completed (Phase 5)
- [ ] Graphics review completed (Phase 6)
- [ ] If `.bib` used: all `\cite{}` keys validated (see `/validate-bib`)
- [ ] Quality score computed and reported

---

## Cross-References

| Skill | When to use instead/alongside |
|-------|-------------------------------|
| `/project-deck` | For project status updates (supervisor meetings, coauthor handoffs) |
| `/latex-autofix` | **Default compiler** — used in Phase 3 for error resolution and citation audit |
| `/latex` | For manual compilation config details, `.latexmkrc` setup, engine selection |
| `/proofread` | For post-hoc review of text quality in the deck |
| `/validate-bib` | For thorough bibliography cross-referencing when citations are used |
| `/literature` | For finding and verifying citations to include |
| `/quarto-deck` | For HTML presentations (teaching, informal talks) instead of PDF |
| `/quarto-course` | For full course websites with multiple lectures, exercises, and navigation |

**Scott's full rhetoric essay:** `resources/academics/scott-cunningham/MixtapeTools/presentations/rhetoric_of_decks.md`
**Scott's deck generation prompt:** `resources/academics/scott-cunningham/MixtapeTools/presentations/create_deck_prompt.md`
**Scott's example decks:** `resources/academics/scott-cunningham/MixtapeTools/presentations/examples/`
