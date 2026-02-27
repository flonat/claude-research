---
name: latex
description: "LaTeX document compilation and management. When Claude needs to compile LaTeX documents (.tex files) for papers, presentations, or other academic content."
allowed-tools: Bash(latexmk*), Bash(xelatex*), Bash(pdflatex*), Bash(biber*), Bash(bibtex*), Bash(mkdir*), Bash(ls*), Read, Write, Edit
argument-hint: [tex-file-path]
---

# LaTeX Document Compilation

## Critical Rules

1. **Build artifacts go to `out/`, but the PDF stays in the source directory.** Before compiling, check for `.latexmkrc` — if missing, create one with the standard config (see Output Directory section). The `.latexmkrc` uses a Perl `END {}` block to copy the PDF back to the source directory after each build.
2. **NEVER write BibTeX entries from memory.** Always verify against web sources (CrossRef, Google Scholar, DOI lookup) before writing. See the `literature` skill.
3. **Check document class before adding packages.** Some classes load packages internally (e.g., `elsarticle` loads `natbib` — adding `\usepackage{natbib}` causes errors).

## Overleaf-Synced Projects

When a project is synced to Overleaf (via Dropbox or Git):
- The `out/` directory will sync to Overleaf but Overleaf ignores it — this is fine
- Always use `.latexmkrc` to enforce `out/` — Overleaf ignores this file too
- Overleaf compiles independently on its server; local compilation is for verification only
- The `.bst` file (e.g., `elsarticle-harv.bst`) lives in the source directory, not `out/`

## When NOT to Use

- Markdown documents — use plain markdown, not LaTeX
- Quick notes or drafts — LaTeX overhead not worth it
- Documents that don't need citations, equations, or precise formatting

## Local-Only Projects (No Overleaf)

Not all projects sync to Overleaf. For local-only projects:
- The same `out/` and `.latexmkrc` conventions apply — this keeps the working directory clean regardless of sync method
- There is no `paper/` symlink — `.tex` files live directly in the project root or a subdirectory
- Use `/latex-autofix` for compilation — it handles `.latexmkrc` creation if missing

## Templates

### Working Paper Template

When creating a **new working paper**, use the template. The canonical location is the Overleaf copy, with a local fallback:

1. `~/Library/CloudStorage/YOUR-CLOUD/Apps/Overleaf/Template/` (Overleaf source)
2. `~/Library/CloudStorage/YOUR-CLOUD/Task Management/templates/latex-wp/` (local copy)

The template contains:

| File | Purpose |
|------|---------|
| `main.tex` | Document entry point with structure |
| `your-template.sty` | Packages, layout, formatting, math environments |
| `your-bib-template.sty` | Bibliography config (biblatex, Paperpile cleanup, Harvard style) |
| `paperpile.bib` | Bibliography file (initially empty) |
| `out/` | Compilation output directory |

**To create a new working paper:**

1. Copy the template files to your new project folder
2. Rename as needed
3. Update `main.tex` with your title, author, abstract
4. Add references to `paperpile.bib`
5. Compile with `latexmk main.tex`

### Citation Style Toggle

The template uses **biblatex/biber** with a toggle for Harvard vs generic authoryear style.

In `main.tex`, control the style via package option:

```latex
\usepackage[harvard]{your-bib-template}    % Harvard style (default)
\usepackage[noharvard]{your-bib-template}  % Generic authoryear style
```

**Harvard style features:**
- Author names: Family, G.
- Volume in bold, issue in parentheses
- DOI/URL shown as "Available at: ..."
- No dashes for repeated authors

### Bibliography File Naming

**Always name the bibliography file `paperpile.bib`** — for any paper, whether using the working paper template or not. This is the standard naming convention across all projects (Paperpile exports use this name).

### Bibliography Commands

The template uses biblatex. In `main.tex`:

```latex
\printbibliography  % (not \bibliography{paperpile})
```

If you need natbib instead, do not load `your-bib-template` and use:
```latex
\bibliographystyle{agsm}
\bibliography{paperpile}
```

**Note:** This template is for working papers only. Other document types (presentations, theses, etc.) may require different templates.

---

## Output Directory

All LaTeX build artifacts (`.aux`, `.log`, `.bbl`, `.fls`, etc.) go to an `out/` subfolder relative to the source file. The **PDF is copied back** to the source directory after each successful build, so it lives alongside the `.tex` file for easy access. This keeps the working directory clean while keeping the deliverable visible.

## Configuration

The PDF-copy convention is enforced in **two places** — keep them in sync when making changes:

1. **`.latexmkrc`** (per-project) — Perl `END {}` block copies PDF after terminal/Claude Code builds
2. **VS Code `.vscode/settings.json`** (per-workspace) — explicit latexmk args in LaTeX Workshop tool definition

Place a `.latexmkrc` in the project root to enforce output directory automatically.

VS Code integration, engine auto-detection (pdfLaTeX/XeLaTeX/LuaLaTeX), manual override configs, reference checking scripts, and manual compilation commands:

**[references/latex-configs.md](references/latex-configs.md)**

---

## LaTeX Skill Hierarchy

Three compilation skills exist for different scopes. Use this decision tree:

```
Need to compile LaTeX?
├── Single project, want auto error resolution?
│   └── /latex-autofix  (default — 5 iterations, citation audit, quality score)
├── Single project, need manual control or config reference?
│   └── /latex  (this skill — .latexmkrc setup, engine selection, VS Code config)
└── Multiple projects / fleet-wide health check?
    └── /latex-health-check  (project discovery, 3 iterations per project, cross-project checks)
```

| Skill | Scope | Iterations | Extra features |
|-------|-------|------------|----------------|
| `/latex` | Single project | Manual | Config reference, engine auto-detection, VS Code integration |
| `/latex-autofix` | Single project | Up to 5 | Auto error fix, citation audit, quality score |
| `/latex-health-check` | All projects | Up to 3 each | Project discovery, symlink integrity, Overleaf separation, template drift |

**Rule of thumb:** Use `/latex-autofix` by default. Use `/latex` when you need to understand or configure the build system. Use `/latex-health-check` for periodic maintenance.
