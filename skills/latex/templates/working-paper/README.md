# LaTeX working-paper template

A clean LuaLaTeX template for academic working papers. The template is client-neutral: it can be used directly, through Claude Code, through Codex, or through other research automation without changing its source format. Client-specific hooks and deployment logic belong outside this repository.

## Included files

| File | Purpose |
|------|---------|
| `main.tex` | Document structure and section inputs |
| `your-template.sty` | Page layout, typography, mathematics, tables, figures, and theorem environments |
| `your-bib-template.sty` | BibLaTeX configuration and Harvard-style option |
| `paperpile.bib` | Project bibliography populated with verified citekeys |
| `citation-placeholders.tex` | Fail-closed placeholders for citations that have not yet been resolved |
| `biblatex-preamble.tex` | Standalone bibliography configuration example |
| `.latexmkrc` | LuaLaTeX build configuration; writes intermediates to `out/` |
| `sections/` | Introduction, literature, data, results, discussion, and conclusion stubs |

## Requirements and compilation

The style uses `fontspec` and `unicode-math`, so LuaLaTeX is required. A TeX Live installation with `latexmk` and Biber is recommended.

```bash
latexmk
```

Build intermediates remain in `out/`. After a successful build, `.latexmkrc` copies the final PDF to the project root.

## Starting a paper

Copy the repository contents into a new LaTeX or Overleaf project, excluding `.git/` and any existing `out/` directory. Then replace the title, author, abstract, keywords, and section stubs in `main.tex` and `sections/`.

Optional Theory and Model section inputs are already present as comments in `main.tex`. New sections should use a dedicated file under `sections/` and an explicit `\label{}`.

## Citations

Use verified citekeys exported into `paperpile.bib`; never guess a citekey. When the intended source is known but its canonical key has not yet been resolved, use:

```latex
\CiteTodo{short-slug}{title; authors; year; DOI or lookup hint}
```

`\CiteTodo` fails the build by default. For an explicitly temporary draft, add `\draftcitationstodotrue` after `citation-placeholders.tex` is loaded; unresolved citations then render as visible warnings instead of silently appearing valid.

## Framework integration

Research frameworks may copy this template into a project, but the template itself has no dependency on a particular AI client, startup hook, home-directory layout, or machine. Keep project code and data outside an Overleaf paper directory; only LaTeX sources, bibliography files, and rendered figures or tables belong in the paper project.
