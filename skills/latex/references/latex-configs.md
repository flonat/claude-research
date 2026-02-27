# LaTeX Configuration Reference

> VS Code integration, engine auto-detection, manual overrides, and reference checking scripts.
> Referenced from `SKILL.md` — the parent file has a summary + pointer.

## VS Code LaTeX Workshop Gotchas

1. **`.latexmkrc` in subdirectories is NOT picked up.** LaTeX Workshop runs latexmk from the workspace root, not the `.tex` file's directory. Subdirectory `.latexmkrc` files are ignored. Fix: pass `-cd -lualatex -outdir=out` (or `-cd -pdf -outdir=out` for pdfLaTeX) explicitly in the VS Code tool args. The `-cd` flag makes latexmk change to the `.tex` file's directory before running.
2. **`% !TEX program` magic comments override custom recipes.** LaTeX Workshop looks for a tool whose name matches the program (e.g., `lualatex`). If no match, it falls back to a default recipe that ignores `-outdir`. Fix: set `"latex-workshop.latex.build.forceRecipeUsage": true` in `.vscode/settings.json`.

### Recommended `.vscode/settings.json` for LuaLaTeX projects

```json
{
  "latex-workshop.latex.tools": [
    {
      "name": "latexmk",
      "command": "latexmk",
      "args": [
        "-cd",
        "-lualatex",
        "-outdir=out",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-synctex=1",
        "%DOC%"
      ],
      "env": {}
    }
  ],
  "latex-workshop.latex.recipes": [
    {
      "name": "latexmk (LuaLaTeX → out/)",
      "tools": ["latexmk"]
    }
  ],
  "latex-workshop.latex.outDir": "%DIR%/out",
  "latex-workshop.latex.build.forceRecipeUsage": true
}
```

Swap `-lualatex` for `-pdf` (pdfLaTeX) or `-xelatex` as needed. The `.latexmkrc` remains the authority for terminal builds.

---

## Auto-detecting Engine

This config automatically uses XeLaTeX if the document or any `\input{}`/`\include{}` file contains `\usepackage{fontspec}`, otherwise falls back to pdfLaTeX:

```perl
# .latexmkrc
$out_dir = 'out';

# Copy PDF back to source directory after build
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }

# Recursively check for fontspec in main file and all \input{}/\include{} files
sub needs_xelatex {
    my ($file, $seen) = @_;
    $seen //= {};

    # Normalize and check if already visited
    return 0 if $seen->{$file};
    $seen->{$file} = 1;

    # Try with and without .tex extension
    my $filepath = -e $file ? $file : -e "$file.tex" ? "$file.tex" : undef;
    return 0 unless $filepath;

    open(my $fh, '<', $filepath) or return 0;
    my $dir = $filepath =~ s|/[^/]*$||r;  # Directory of current file
    $dir = '.' if $dir eq $filepath;

    while (<$fh>) {
        return 1 if /\\usepackage.*\{fontspec\}/;

        # Recurse into \input{} and \include{} files
        if (/\\(?:input|include)\{([^}]+)\}/) {
            my $subfile = $1;
            $subfile = "$dir/$subfile" unless $subfile =~ m|^/|;
            return 1 if needs_xelatex($subfile, $seen);
        }
    }
    close($fh);
    return 0;
}

# Auto-detect engine
$pdf_mode = 1;  # Default to pdflatex
foreach my $file (@ARGV) {
    if (needs_xelatex($file)) {
        $pdf_mode = 5;  # Switch to xelatex
        last;
    }
}

$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error %O %S';
$xelatex = 'xelatex -interaction=nonstopmode -halt-on-error %O %S';
```

---

## Manual Override Configs

If auto-detection doesn't suit a project, use one of these explicit configs:

**pdfLaTeX** (standard LaTeX fonts):
```perl
# .latexmkrc
$out_dir = 'out';
$pdf_mode = 1;
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error %O %S';
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
```

**XeLaTeX** (system fonts, Unicode, OpenType features):
```perl
# .latexmkrc
$out_dir = 'out';
$pdf_mode = 5;
$xelatex = 'xelatex -interaction=nonstopmode -halt-on-error %O %S';
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
```

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
