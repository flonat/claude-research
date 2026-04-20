# LaTeX Templates and Bibliography Configuration

## Working Paper Template

When creating a **new working paper**, use the template. The canonical location is the local git repo:

1. `templates/latex-wp/` (in Task Management — canonical source, git-tracked)

The template contains:

| File | Purpose |
|------|---------|
| `main.tex` | Document entry point with structure |
| `your-template.sty` | Packages, layout, formatting, math environments |
| `your-bib-template.sty` | Bibliography config (biblatex, source cleanup, Harvard style) |
| `references.bib` | Bibliography file (initially empty) |
| `out/` | Compilation output directory |

**To create a new working paper:**

1. Copy the template files to your new project folder
2. Rename as needed
3. Update `main.tex` with your title, author, abstract
4. Add references to `references.bib`
5. Compile with `latexmk main.tex`

## Citation Style Toggle

The template uses **biblatex/biber** with a toggle for Harvard vs generic authoryear style.

In `main.tex`, control the style via package option:

```latex
\usepackage[harvard]{your-bib-template}    % Harvard style (default)
\usepackage[noharvard]{your-bib-template}  % Generic authoryear style
```

## Bibliography File Naming

**Always name the bibliography file `references.bib`** — for any paper, whether using the working paper template or not. This is the standard naming convention across all projects.

## Bibliography Commands

The template uses biblatex. In `main.tex`:

```latex
\printbibliography  % (not \bibliography{references})
```

If you need natbib instead, do not load `your-bib-template` and use:
```latex
\bibliographystyle{agsm}
\bibliography{references}
```
