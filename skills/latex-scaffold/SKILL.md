---
name: latex-scaffold
description: "Use when you need to convert a Markdown draft into a buildable LaTeX project."
argument-hint: "[path/to/draft.md]"
allowed-tools: Read, Write, Edit, Bash(latexmk*), Bash(mkdir*), Bash(ls*), Glob, Grep
---

# LaTeX Scaffold

Convert an approved Markdown draft into a minimal, compilable LaTeX project. This is a **deterministic format conversion** — prose quality should already be addressed in the source draft.

## When to Use

- Converting a literature review, survey, or report from Markdown to LaTeX for PDF output
- Turning meeting notes or drafts into a formatted document
- Bootstrapping a LaTeX project from an existing outline
- Any time you need md→tex without rewriting content

## Inputs

- A Markdown file (`.md`) — the draft to convert
- A `.bib` file (optional) — if the draft contains citations

## Outputs

- A `.tex` file ready to compile with `/latex`
- A `.latexmkrc` if one doesn't already exist (see `/latex` for config details — must include `$out_dir = 'out'` and the `END {}` block to copy the PDF back)

---

## Workflow

### Step 1: Analyse the Draft

Read the Markdown file and inventory:
- Heading structure (determine `\section` / `\subsection` depth)
- Citations (`[@Key]` or `[@Key1; @Key2]` patterns)
- Tables (Markdown pipe tables)
- Math blocks (`$...$` inline, `$$...$$` display)
- Figures (`![caption](path)`)
- Code blocks (fenced with language)
- Whether an abstract section exists

### Step 2: Create the LaTeX File

Apply these conversion rules:

| Markdown | LaTeX |
|----------|-------|
| `# Title` (first H1) | `\title{...}` |
| `## Section` | `\section{...}` |
| `### Subsection` | `\subsection{...}` |
| `#### Subsubsection` | `\subsubsection{...}` |
| `## Abstract` | `\begin{abstract}...\end{abstract}` |
| Headings starting with `Appendix` | `\appendix` once, then `\section{...}` |
| `**bold**` | `\textbf{...}` |
| `*italic*` | `\emph{...}` |
| `` `code` `` | `\texttt{...}` |
| `[@Key]` | `\citep{Key}` |
| `[@Key1; @Key2]` | `\citep{Key1,Key2}` |
| `@Key` (inline) | `\citet{Key}` |
| `$...$` / `$$...$$` | Pass through unchanged |
| `- item` | `\begin{itemize}\item ...\end{itemize}` |
| `1. item` | `\begin{enumerate}\item ...\end{enumerate}` |
| `> quote` | `\begin{quote}...\end{quote}` |
| `![caption](path)` | `\begin{figure}[htbp]\includegraphics{path}\caption{caption}\end{figure}` |
| Pipe tables | `\begin{table}[htbp]\begin{tabular}{...}...\end{tabular}\end{table}` |
| Fenced code blocks | `\begin{verbatim}...\end{verbatim}` |
| `---` (horizontal rule) | `\bigskip\hrule\bigskip` or omit |

### Preamble Template

```latex
\documentclass[a4paper,11pt]{article}

\usepackage[a4paper,margin=1in]{geometry}
\usepackage{hyperref}
\hypersetup{colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{enumitem}
\usepackage[backend=biber,style=authoryear,natbib=true]{biblatex}
\addbibresource{references.bib}

\title{...}
\author{...}
\date{\today}

\begin{document}
\maketitle
% content here
\printbibliography
\end{document}
```

Adjust the preamble based on what the draft actually uses (e.g., skip `graphicx` if no figures). The `natbib=true` option provides `\citet`/`\citep` compatibility. If the project already uses natbib (e.g., with a journal `.bst` file), keep natbib — but for new scaffolds, biblatex is the default.

### Step 3: Strip Markdown Residue

After conversion, scan the `.tex` file for any remaining Markdown syntax:
- `##` heading markers
- `**` bold markers
- `[@` citation markers
- Pipe `|` table syntax
- `![` image markers

These indicate incomplete conversion — fix them.

### Step 4: Wire Bibliography

- If a `.bib` file exists in the project, point `\addbibresource{}` to it
- If the project has a `references.bib`, use that
- If no `.bib` exists but citations are present, create placeholder comments: `% TODO: create .bib with keys: Key1, Key2, ...`
- Ensure `\printbibliography` is at the end of the document (not `\bibliography{}`)

### Step 5: Compile and Verify

Run `/latex` to compile. Verify:
- [ ] Document compiles without errors
- [ ] All citations resolve (or are marked as TODO)
- [ ] Tables render correctly
- [ ] Math renders correctly
- [ ] Page count is reasonable

---

## Rules

- **No content rewriting** — this is format conversion only. Do not improve prose, fix grammar, or reorganise sections.
- **Preserve all content** — every paragraph, figure reference, and citation in the draft must appear in the `.tex` output.
- **Strip heading numbering** — if the draft has numbered headings like `1.2 Methods`, let LaTeX handle the numbering (just use `\subsection{Methods}`).
- **Use `/latex`** for compilation — never bare `pdflatex` or `latexmk` without `out/` directory.
- **Bold caption lines** like `**Table 1. Description**` immediately before a pipe table should become `\caption{Description}` inside a `table` float.

---

## Cross-References

| Skill | When to use alongside |
|-------|----------------------|
| `/latex` | Compile the scaffolded `.tex` file |
| `/latex` | For manual compilation config and `.latexmkrc` setup |
| `/bib-validate` | After scaffolding to verify all citation keys resolve |
| `/proofread` | After scaffolding for grammar and consistency check |
| `/latex-template` | After scaffolding to verify preamble aligns with the working paper template |
