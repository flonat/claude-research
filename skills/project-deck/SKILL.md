---
name: project-deck
description: "Use when creating a LaTeX Beamer slide deck to communicate project status, research progress, or findings to collaborators. Generates structured .tex presentations with assertion-style titles, figures, and summary frames."
allowed-tools: Bash(latexmk*), Bash(xelatex*), Bash(pdflatex*), Bash(mkdir*), Read, Write, Edit
argument-hint: [project-name-or-path]
---

# Project Deck

Create Beamer presentation decks to communicate project status to your future self and collaborators. Based on Scott Cunningham's approach: using decks not for public speaking but to efficiently communicate work status across time and to coauthors.

## When to Use

- Before a supervisor meeting
- At the end of a research sprint or when handing off to a coauthor
- When returning to a dormant project
- Weekly project status updates

## Workflow

### Phase 1: Gather Context

Read project context to understand current state:
1. Read `.context/current-focus.md` for active work
2. Read recent session logs in `log/` for progress
3. Read any existing figures/tables in `output/` or `results/`
4. If `$ARGUMENTS` specifies a project path, read its CLAUDE.md and README

### Phase 2: Design Deck Structure

Plan the slide sequence following the rhetoric principles:

1. **Title slide** — project name, date, authors
2. **Research question** — one slide, assertion-style title
3. **What's been done** — 2-3 slides with figures/tables
4. **Key findings so far** — lead with conclusions, not "Results"
5. **Current blockers** — what's slowing progress
6. **Next steps** — concrete actions with owners/dates

Present the outline to the user for approval before writing LaTeX.

### Phase 3: Create LaTeX

Write the Beamer `.tex` file in the project directory (not in `paper/`). Minimal template:

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{metropolis}
\title{Project Status: [Name]}
\author{[Author]}
\date{\today}
\begin{document}
\maketitle
\begin{frame}{Key Finding: [Assertion-style title]}
  \begin{itemize}
    \item Main result with evidence
    \item Supporting detail
  \end{itemize}
  % \includegraphics[width=0.8\textwidth]{figures/main-result.pdf}
\end{frame}
\begin{frame}{Next Steps}
  \begin{enumerate}
    \item Concrete action with owner
    \item Timeline-bound deliverable
  \end{enumerate}
\end{frame}
\end{document}
```

- One idea per slide — titles are assertions, not labels
- Include existing figures via `\includegraphics` where relevant

### Phase 4: Compile and Validate

```bash
latexmk -xelatex -output-directory=out <deck>.tex
```

1. Check exit code — fix any compilation errors
2. Review log for overfull hbox warnings and fix
3. Copy PDF from `out/` to the source directory
4. Verify slide count matches the planned structure

Present the compiled PDF path to the user.

## Deck Rhetoric Principles

1. **Titles are assertions** — "Distance increases abortion rates" not "Results"
2. **Lead with conclusions** — don't bury the lede
3. **One idea per slide** — don't overload
4. **Visual hierarchy** — most important things stand out
5. **Beautiful figures and tables** — data visualisation matters
6. **Explicit transitions** — guide the reader through the narrative

## Cross-References

| Skill | When to use instead |
|-------|---------------------|
| `/beamer-deck` | General-purpose Beamer decks (not project-status specific) |
| `/insights-deck` | For communicating research insights and findings |
| `/quarto-deck` | For Quarto/Reveal.js presentations instead of Beamer |
