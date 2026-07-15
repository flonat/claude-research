# Canonical `.latexmkrc`

Single source of truth for LaTeX build config across all projects.

## Files

| File | Purpose |
|------|---------|
| `.latexmkrc` | Robust auto-detecting build config (drop into any dir with `.tex` files) |
| `vscode-settings.json` | VS Code LaTeX Workshop config (drop into `.vscode/settings.json`) |

## What `.latexmkrc` does

- Builds to `out/` so source dir stays clean
- Auto-detects engine: pdflatex (default), xelatex (if `fontspec`), lualatex (if `luacode`/`lua-ul`/`luamplib`)
- Recurses into `\input{}`/`\include{}` files to detect engine requirements
- Copies compiled PDF back to source dir on success
- Works with terminal `latexmk`, VS Code LaTeX Workshop (with `-cd`), and Overleaf-synced folders

## Usage

```bash
# Drop into any directory with .tex files
cp <task-mgmt>/templates/latexmkrc/.latexmkrc <target-dir>/

# For Overleaf-symlinked paper dirs, drop into the symlink TARGET (the Overleaf folder)
cp <task-mgmt>/templates/latexmkrc/.latexmkrc <overleaf-folder>/

# For VS Code support
mkdir -p <target-dir>/.vscode
cp <task-mgmt>/templates/latexmkrc/vscode-settings.json <target-dir>/.vscode/settings.json
```

## Overleaf interaction

When dropped into an Overleaf-synced folder, `.latexmkrc` is git-tracked by Overleaf and synced to the web compiler. The web compiler picks the engine from *Settings → Compiler*, not from `.latexmkrc` — the auto-detect Perl runs locally only. This is fine: web Overleaf ignores the engine logic but doesn't break.

## Override

If a project needs a fixed engine (rare), set `$pdf_mode` explicitly *after* the detect block, or replace the file with a hard-coded variant. See `skills/latex/references/latex-configs.md` for explicit per-engine variants.
