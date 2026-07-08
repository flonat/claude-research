# Venue toggles — what to strip when porting to `your-template`

> Reference for `/preprint` Phase 3. Not exhaustive — extend when porting from a venue you haven't ported before. The rule is always the same: replace the preamble entirely with `your-template` and strip venue-specific scaffolding from the body.

## NeurIPS (`neurips_*.sty`)

| Stripped | Replacement |
|----------|-------------|
| `\usepackage[main]{neurips_2026}` (and any option) | Drop entirely |
| `\input{checklist}` | Drop entirely |
| `\section*{NeurIPS Paper Checklist}` and the entire checklist content if inlined | Drop entire block |
| Anonymous-mode `\author{Anonymous}` | Replace with real authors |
| `[final]` / `[preprint]` / `[main]` package option | N/A — package is gone |

## ICML (`icml*.sty`)

| Stripped | Replacement |
|----------|-------------|
| `\usepackage[accepted]{icml*}` | Drop entirely |
| `\icmltitle{...}` | Replace with standard `\title{...}` |
| `\icmlauthor{...}` blocks | Replace with `\author{... \and ...}` |
| `\icmlaffiliation{...}` | Move to `\thanks{}` on the corresponding author |
| ICML page-1 banner | Drop (handled by class) |

## ACL / EMNLP / NAACL (`acl_*.sty`)

| Stripped | Replacement |
|----------|-------------|
| `\usepackage[review]{acl}` or `[final]` | Drop entirely |
| `\aclfinalcopy` toggle | N/A |
| `\paperID{...}` / `\confName{...}` | Drop |
| Abstract footnote with paper ID | Drop |

## IEEE (`IEEEtran.cls`)

| Stripped | Replacement |
|----------|-------------|
| `\documentclass{IEEEtran}` | Replace with WP `\documentclass[12pt,a4paper]{article}` |
| `\IEEEauthorblockN`, `\IEEEauthorblockA` | Replace with `\author{... \and ...}` |
| `\IEEEpeerreviewmaketitle` | Replace with standard `\maketitle` inside `titlepage` |
| `\bstctlcite{IEEEexample:BSTcontrol}` | Drop |

## ACM (`acmart.cls`)

| Stripped | Replacement |
|----------|-------------|
| `\documentclass[acmsmall|sigconf|...]{acmart}` | Replace with WP `\documentclass[12pt,a4paper]{article}` |
| `\setcopyright{...}` | Drop |
| `\acmConference[...]{...}` | Drop |
| `\acmBooktitle{...}` | Drop |
| `\affiliation{...}` blocks | Convert to `\thanks{}` |
| `\ccsdesc[500]{...}` | Drop (CCS concepts not in WP template) |
| `\keywords{...}` | Convert to `\noindent\textbf{Keywords:} ...` line in abstract |

## Generic — patterns to search for regardless of venue

```
% blind-mode toggles
^\\(if|new)if?@?(anonymous|blind|review|finalcopy)\b
^\\(anonymous|blindcopy)\b

% submission identifiers
^\\(paperID|submissionID|conf?(Name|Year|Track))\{

% page-1 banners and copyright lines
^\\(setcopyright|copyrightyear|conferenceinfo|CopyrightYear)\{

% footnote-style affiliations on title (move to thanks)
^\\(affiliation|institute)\{

% reviewer-mode debugging
^\\nocite\{\*\}
^\\(reviewmode|debug|todo)\{
```

## Bibliography style ports

`your-bib-template` is biblatex-based, defaults to Harvard-style author-year. Source-paper citation styles to remap:

| Source command (natbib) | Target command (biblatex) |
|-------------------------|---------------------------|
| `\citep{key}` | `\parencite{key}` |
| `\citet{key}` | `\textcite{key}` |
| `\citeyear{key}` | `\citeyear{key}` (same) |
| `\citeauthor{key}` | `\citeauthor{key}` (same) |
| `\citealp{key}` | `\cite{key}` (no parens, no comma) |
| `\citealt{key}` | `\textcite{key}` without parens — flag, use `\textcite[][]{key}` if needed |
| `\bibliographystyle{plainnat}` | Drop (handled by `your-bib-template`) |
| `\bibliography{references}` | `\printbibliography` |

If source uses a non-natbib style (e.g., raw BibTeX, `apsrev`, `chicago`), flag for manual port — don't auto-convert.

## What NEVER to port

These are reviewer-facing or venue-anchoring artefacts that don't belong in a preprint:

- Reproducibility / NeurIPS / ICML checklists (they live in the conference draft only)
- Camera-ready instructions blocks ("Authors: please update X by Y")
- Submission tracker comments (`% submitted to ICML 2026 — track A`)
- Anonymous-artifact URLs that point to `anonymous.4open.science` *if* the user has indicated they want to switch to a public GitHub URL for the preprint (otherwise keep — the anonymous link still works for everyone)
- Page-limit hacks (`\vspace{-\baselineskip}` chains, `\setlength{\textfloatsep}{0pt}`, etc.) — preprints don't have page limits
