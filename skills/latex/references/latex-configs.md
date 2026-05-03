# LaTeX Configuration Reference

> VS Code integration, the canonical `.latexmkrc`, and reference checking scripts.
> Referenced from `SKILL.md` — the parent file has a summary + pointer.

## Canonical `.latexmkrc`

**Source of truth:** `templates/latexmkrc/.latexmkrc` in Task Management.

It auto-detects the engine, builds to `out/`, and copies the PDF back to the source dir. Drop it into any directory with `.tex` files — including Overleaf-symlinked paper folders (the file goes into the symlink target so it syncs to Overleaf's web compiler too):

```bash
TM=$(cat ~/.config/task-mgmt/path)
cp "$TM/templates/latexmkrc/.latexmkrc" <target-dir>/
```

See `templates/latexmkrc/README.md` for the full spec and rationale.

## VS Code LaTeX Workshop Setup

Two gotchas to know:

1. **`.latexmkrc` in subdirectories is NOT picked up by default.** LaTeX Workshop runs latexmk from the workspace root. Fix: pass `-cd` so latexmk changes to the `.tex` file's directory before running. The canonical VS Code config below already does this.
2. **`% !TEX program` magic comments override custom recipes.** Set `latex-workshop.latex.build.forceRecipeUsage: true` (the canonical config does this).

### Canonical `.vscode/settings.json`

**Source of truth:** `templates/latexmkrc/vscode-settings.json`.

```bash
mkdir -p .vscode
cp "$TM/templates/latexmkrc/vscode-settings.json" .vscode/settings.json
```

This config delegates everything to `latexmk` with `-cd`, so the project's `.latexmkrc` is the single authority. No engine flag in the VS Code config — auto-detection happens in `.latexmkrc`.

## Manual Override (rare)

If a project needs a hard-coded engine instead of auto-detect, replace the canonical `.latexmkrc` with one of:

**pdfLaTeX** (standard fonts):
```perl
$out_dir = 'out';
$pdf_mode = 1;
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
```

**XeLaTeX** (system fonts via `fontspec`):
```perl
$out_dir = 'out';
$pdf_mode = 5;
$xelatex = 'xelatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
```

**LuaLaTeX** (`luacode`, `lua-ul`, `luamplib`):
```perl
$out_dir = 'out';
$pdf_mode = 4;
$lualatex = 'lualatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
```

All three include the `END {}` block so the PDF lands next to the `.tex` source.

---

## Reference Checking

Every compilation must verify that all references resolve correctly. After compilation, check the log and report any issues found.

### Reference Check Script

After running latexmk, check for issues and display them as warnings:

```bash
# Compile
latexmk document.tex

# Check for reference issues and report exact problems
LOGFILE="out/document.log"
ISSUES=$(grep -E "(Reference.*undefined|Citation.*undefined|multiply defined)" "$LOGFILE" 2>/dev/null)

if [ -n "$ISSUES" ]; then
    echo ""
    echo "⚠️  REFERENCE ISSUES DETECTED:"
    echo "================================"
    echo "$ISSUES" | while read -r line; do
        echo "  • $line"
    done
    echo "================================"
    echo ""
fi
```

### What to Check For

| Pattern | Meaning |
|---------|---------|
| `Reference .* undefined` | `\ref{}` or `\autoref{}` pointing to non-existent label |
| `Citation .* undefined` | `\cite{}` referencing missing BibTeX entry |
| `Label .* multiply defined` | Same `\label{}` used more than once |

### Manual Compilation (if not using latexmk)

For biblatex (default in working paper template):
```bash
mkdir -p out
xelatex -output-directory=out document.tex
biber out/document
xelatex -output-directory=out document.tex
xelatex -output-directory=out document.tex
cp out/document.pdf ./document.pdf
```

For natbib (if using that instead):
```bash
mkdir -p out
pdflatex -output-directory=out document.tex
bibtex out/document
pdflatex -output-directory=out document.tex
pdflatex -output-directory=out document.tex
cp out/document.pdf ./document.pdf
```
