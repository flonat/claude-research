# Template Compliance — Report Format

> Phase 5 report template for `/latex-template`. Adapt to actual audit findings.

## Severity Levels

| Severity | Deduction | Marker |
|----------|-----------|--------|
| Major | -5 | `!!` |
| Moderate | -2 | `!` |
| Minor | -1 | `~` |

## Classification Labels

| Label | Marker | Meaning |
|-------|--------|---------|
| Adopt | `+` | Template feature missing from project — should add |
| Keep | `=` | Project-specific addition — informational only |
| Conflict | `?` | Same functionality, different implementation — needs user decision |
| Drop | `-` | Redundant or superseded — safe to remove |

## Example Report

```
Template Compliance Report
===========================
Project:  Costly Voice
Path:     ~/papers/costly-voice/paper/
Template: templates/latex-wp/your-template.sty + your-bib-template.sty
Date:     2026-02-15
Score:    78/100 (Good)

Summary:
  + Adopt:     6
  = Keep:      3
  ? Conflict:  1
  - Drop:      2
  Total:      12

────────────────────────────────────────

PACKAGES
--------

  + [Moderate] Missing: csquotes
    Template provides csquotes for proper quote handling with biblatex.
    Add: \usepackage{csquotes}

  + [Moderate] Missing: dvipsnames option on xcolor
    Project has: \usepackage{xcolor}
    Template has: \usepackage[dvipsnames]{xcolor}
    Add dvipsnames option for named colours (NavyBlue used in hyperref).

  + [Minor] Missing: comment
    Template provides comment for block-commenting sections.
    Add: \usepackage{comment}

  = [Info] Extra: tikz-cd
    Project loads tikz-cd (not in template). Likely project-specific.

  - [Moderate] Duplicate: amsmath
    Loaded twice — once standalone, once via mathtools (which loads it).
    Remove the standalone \usepackage{amsmath}.

────────────────────────────────────────

HYPERREF
--------

  + [Minor] Missing key: anchorcolor=NavyBlue
    Project's \hypersetup is missing anchorcolor.

  = [Info] Different value: linkcolor
    Project: linkcolor=NavyBlue
    Template: linkcolor=black
    Keeping project's preference.

────────────────────────────────────────

BIBLIOGRAPHY
------------

  + [Moderate] Missing: bibliography source mappings
    Template includes DeclareSourcemap blocks for month cleanup,
    author cleanup, and journal cleanup. Project has none.

  + [Moderate] Missing: field clearing (\AtEveryBibitem)
    Template clears language, note, issn, isbn fields.
    Project does not clear these — bibliography may show noisy metadata.

  ? [Major] Conflict: biblatex options
    Project: style=authoryear, backend=biber, maxcitenames=3
    Template: style=authoryear, backend=biber, maxcitenames=2
    Different maxcitenames — user should decide.

  = [Info] Extra: \addbibresource{extra-refs.bib}
    Project loads an additional bib file. Keeping.

────────────────────────────────────────

CUSTOM COMMANDS
---------------

  + [Moderate] Missing: \todo command
    Template defines: \newcommand{\todo}[1]{{\color{red}\textbf{TODO:} #1}}

  = [Info] Extra: \highlight command
    Project defines \highlight (not in template). Keeping.

────────────────────────────────────────

THEOREM ENVIRONMENTS
--------------------

  + [Minor] Missing: hypothesis environment
    Template defines: \newtheorem{hypothesis}[theorem]{Hypothesis}
    (remark style)

────────────────────────────────────────

BUILD CONFIG
------------

  - [Major] Missing: .latexmkrc
    No .latexmkrc found in project root or paper directory.
    Template provides: lualatex engine, out/ directory, PDF copy-back.
    Create .latexmkrc from template.

────────────────────────────────────────

AUXILIARIES
-----------

  main.tex:
    ✓ Preamble loading: \usepackage{your-template} + \usepackage{your-bib-template} (or legacy \input{settings})
    ✓ \documentclass[12pt,a4paper]{article}
    ✓ \printbibliography present
    ✓ No stale \bibliography{} or \bibliographystyle{}

  .latexmkrc:
    ✗ File missing (flagged above)

────────────────────────────────────────

SCORING BREAKDOWN
-----------------

  Starting score:                   100
  !! Missing .latexmkrc             -5
  !! biblatex maxcitenames conflict  -5
  !  Missing csquotes               -2
  !  Missing dvipsnames             -2
  !  Duplicate amsmath              -2
  !  Missing source mappings        -2
  !  Missing field clearing         -2
  !  Missing \todo command          -2
  ~  Missing comment                -1
  ~  Missing anchorcolor            -1
  ~  Missing hypothesis env         -1
                                   ----
  Final score:                      75

  Label: Good (75-89)
    Minor gaps — mostly missing template utilities and bibliography cleanup.

────────────────────────────────────────

RECOMMENDATIONS (prioritised)
-----------------------------

  1. Create .latexmkrc from template (enables proper build pipeline)
  2. Resolve biblatex maxcitenames: choose 2 (template) or 3 (current)
  3. Add dvipsnames option to xcolor (required for NavyBlue in hyperref)
  4. Add bibliography source mappings (cleans up month/author/journal noise)
  5. Add \AtEveryBibitem field clearing (removes issn/isbn/language clutter)
  6. Add csquotes (recommended companion for biblatex)
  7. Remove duplicate amsmath load
  8. Add \todo command for draft annotations
  9. Add missing hyperref keys (anchorcolor)
  10. Add hypothesis theorem environment

Run `/latex-template ~/papers/costly-voice --apply` to interactively apply changes.
```

## Score Interpretation

| Score | Label | Meaning |
|-------|-------|---------|
| 90-100 | Excellent | Fully aligned with template |
| 75-89 | Good | Minor gaps only |
| 50-74 | Needs attention | Several missing features |
| < 50 | Significant drift | Consider full resync |
