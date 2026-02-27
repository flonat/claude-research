# Known Error Patterns & Auto-Fixes

> Reference file for `/latex-autofix`. Each pattern maps a log signature to a fix.

## 1. Missing package

**Log pattern:**
```
! LaTeX Error: File `<package>.sty' not found.
```
or
```
! Undefined control sequence.  ...  \<command>
```
where the undefined command belongs to a well-known package.

**Fix:** Add `\usepackage{<package>}` to the preamble (before `\begin{document}`). Place it after existing `\usepackage` lines. Common mappings:

| Command | Package |
|---------|---------|
| `\includegraphics` | `graphicx` |
| `\url`, `\href` | `hyperref` |
| `\toprule`, `\midrule`, `\bottomrule` | `booktabs` |
| `\multirow` | `multirow` |
| `\lstlisting` | `listings` |
| `\tikz`, `\begin{tikzpicture}` | `tikz` |
| `\xspace` | `xspace` |
| `\adjustbox` | `adjustbox` |
| `\subcaption`, `\subfigure` | `subcaption` |
| `\sisetup`, `\SI` | `siunitx` |
| `\algorithm` | `algorithm2e` or `algorithmicx` |

If the package is unclear, report it as unresolved rather than guessing.

## 2. Font / symbol conflicts

**Log pattern:**
```
Command \<name> already defined.
```
Common case: `\Bbbk` conflict between `amssymb` and `newtxmath`.

**Fix:** Add a `\let` override **before** the conflicting package:

```latex
% Fix font conflict: \Bbbk defined by both amssymb and newtxmath
\let\Bbbk\relax
```

For the specific `amssymb` / `newtxmath` conflict, insert `\let\Bbbk\relax` between the two `\usepackage` lines. More generally:

- Read the error to identify which command is multiply defined
- Add `\let\<command>\relax` before the second package that defines it
- If multiple commands conflict, add a `\let` for each

## 3. Undefined citation

**Log pattern:**
```
LaTeX Warning: Citation `<key>' on page <n> undefined
```
or (with biblatex/biber):
```
Package biblatex Warning: ... Entry '<key>' ... not found
```

**Fix:**
1. Read the `.bib` file(s) identified in Phase 1.
2. Search for the citation key. Check for:
   - **Typo:** fuzzy-match against all keys in the `.bib` (e.g., `smith2020` vs `Smith2020`, `santanna2020` vs `santanna2020doubly`).
   - **Missing entry:** the key genuinely doesn't exist in the `.bib`.
3. If a close match is found, fix the `\cite{<key>}` in the `.tex` file.
4. If no match exists, report as unresolved — do **not** fabricate bibliography entries.

## 4. Missing image / file path

**Log pattern:**
```
! LaTeX Error: File `<path>' not found.
```
or
```
! Package pdftex.def Error: File `<path>' not found
```

**Fix:**
1. Extract the filename from the error.
2. Search the project directory recursively for a file with that name (using Glob).
3. If found, update the `\includegraphics` (or `\input`, `\include`) path in the `.tex` file.
4. If not found, report as unresolved.

## 5. Stale auxiliary / cache files

**Log pattern:** Errors that reference corrupted `.aux`, `.bbl`, `.bcf`, `.toc`, or `.idx` files, or error messages like:
```
I found no \bibstyle command
```
```
I found no \citation commands
```
```
\openout ... already open
```
or when the same error persists after a seemingly correct fix.

**Fix:**
1. Run `latexmk -C -outdir=out` in the project directory to clean all generated files.
2. Delete `out/` contents if `latexmk -C` doesn't clear them.
3. Restart the compile loop from Step 2a (this counts as one iteration).

## 6. Beamer package conflicts (enumitem)

**Log pattern:**
```
Option clash for package enumitem
```
or
```
Command \item already defined
```
when using `enumitem` with beamer.

**Fix:** Beamer redefines `\item` internally, so enumitem often clashes. First check if enumitem is actually needed — if only used for basic lists, remove it (beamer handles lists natively). If enumitem features are required (custom labels, spacing), replace:

```latex
% Before (conflicts with beamer):
\usepackage{enumitem}

% After:
\usepackage[shortlabels]{enumitem}
\setlist[itemize]{label=\textbullet}
```

If the conflict is with a non-beamer class, the `shortlabels` option alone usually resolves it.

## 7. xcolor option conflicts

**Log pattern:**
```
Option clash for package xcolor
```
or
```
Undefined control sequence. \rowcolor
```
(when `table` option is missing from xcolor).

**Fix:** xcolor must be loaded with all needed options **before** any package that loads it implicitly (e.g., `tikz`, `tcolorbox`, `beamer`). Two approaches:

```latex
% Approach 1: Load xcolor early with all options
\usepackage[table,dvipsnames,svgnames]{xcolor}
% ... then load tikz, tcolorbox, etc.

% Approach 2: If another package loads xcolor first, use PassOptionsToPackage
\PassOptionsToPackage{table,dvipsnames,svgnames}{xcolor}
\documentclass{...}
```

Common missing options: `table` (for `\rowcolor`, `\cellcolor`), `dvipsnames` (for named colours like `ForestGreen`), `svgnames` (for web colours).

## 8. TikZ reserved key conflicts

**Log pattern:**
```
I do not know the key '/tikz/<name>'
```
or
```
Package pgfkeys Error: I do not know the key '/tikz/<name>'
```

**Fix:** TikZ reserves many common English words as keys. If a custom key name conflicts, rename it:

```latex
% Before (conflicts — 'step' is a reserved TikZ key):
\tikzset{step/.style={...}}

% After:
\tikzset{mystep/.style={...}}
```

Common reserved names that cause conflicts: `step`, `at`, `node`, `draw`, `fill`, `path`, `scale`, `shift`, `rotate`, `color`, `text`, `inner sep`, `outer sep`. Rename custom keys to avoid these (e.g., `stepsize`, `mynode`, `drawstyle`).
