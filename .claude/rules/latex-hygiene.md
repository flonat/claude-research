---
paths:
  - "**/*.tex"
---

# Rule: LaTeX Hygiene

## Principles

1. **Never leave build artifacts in the source directory.** All compilation output goes to `out/`. Only the final PDF is copied back after a successful build.
2. **When a package is missing, install via `tlmgr` — never download `.sty` files.** Downloaded files pollute the source directory, don't update with TeX Live, and sync to Overleaf as junk.

## Build Output

- **Always invoke `latexmk` directly.** Never substitute bare `pdflatex`/`xelatex`/`lualatex`/`bibtex`/`biber` — even with `-output-directory=out`. Bypassing `latexmk` silently ignores `.latexmkrc` (engine, build sequence, post-build hooks).
- Standard invocation: `latexmk <file>.tex`. The `.latexmkrc` controls everything else.
- If `latexmk` is unavailable, state this and ask the user to `tlmgr install latexmk`.

### `.latexmkrc` policy

- Opening an existing project: check the main `.tex` directory; if missing, create before compiling. If present, verify `$out_dir = 'out'` + END block — flag, don't modify without permission.
- New projects: always create `.latexmkrc` alongside the main `.tex`; add `out/` to `.gitignore` if git-tracked.

### Standard `.latexmkrc`

```perl
$out_dir = 'out';
$pdf_mode = 1;        # 1=pdflatex, 4=lualatex, 5=xelatex
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error %O %S';
$lualatex = 'lualatex -interaction=nonstopmode -halt-on-error %O %S';
$xelatex  = 'xelatex -interaction=nonstopmode -halt-on-error %O %S';

# Copy PDFs from $out_dir back to source dir after a successful build
END {
    if (-d $out_dir) {
        my @pdfs = glob("$out_dir/*.pdf");
        foreach my $pdf (@pdfs) {
            my $base = $pdf;
            $base =~ s|.*/||;
            system("cp '$pdf' '$base'");
        }
    }
}
```

To switch engines: change `$pdf_mode` only (1/4/5). The relevant engine command (`$pdflatex`/`$lualatex`/`$xelatex`) is already there.

### VS Code Integration

LaTeX-Workshop config lives in **User settings** (`~/Library/Application Support/Code/User/settings.json`), not per-project. Invoke `latexmk` with `-cd` and no engine/output flags — `.latexmkrc` controls those. Don't duplicate in per-project `.vscode/settings.json` unless genuinely needed.

### Build artifacts (never in source directory)

`.aux`, `.bbl`, `.blg`, `.fdb_latexmk`, `.fls`, `.log`, `.out`, `.toc`, `.lof`, `.lot`, `.nav`, `.snm`, `.vrb`, `.synctex.gz`, `.bcf`, `.run.xml`

### What stays in the source directory

- `.tex`, `.sty`, `.cls`, `.bst` — source files
- `.bib` — bibliography
- `.latexmkrc` — build config
- `.pdf` — final output (copied from `out/` after successful build)
- Figures: `.pdf`, `.png`, `.eps`, `.jpg`, `.svg`, `.tikz`

### If you find artifacts in a source directory

1. Flag: "I found build artifacts in the source directory — these should be in `out/`."
2. Offer to clean up and create `.latexmkrc` if missing.
3. Wait for confirmation before deleting anything.

## Missing Packages

```bash
sudo tlmgr install <package-name>
```

If `sudo` requires an interactive password prompt (which it does inside Claude Code), ask the user to run the command themselves:

> "Missing package `<name>`. Please run: `! sudo tlmgr install <name>`"

### What NOT to do

- `curl` or `wget` a `.sty` file from CTAN
- Copy `.sty` files into the paper directory
- Generate `.sty` from `.dtx`/`.ins` in `/tmp` and copy it over
- Use any workaround that places package files in the project tree

## Applies To

All LaTeX compilations on all machines: papers, proposals, presentations, teaching materials, standalone docs. Both Overleaf-linked `paper/` dirs and standalone projects. Both `/latex` and manual `latexmk`.

## Why This Matters

Build artifacts clutter source dirs, pollute git history, and break Overleaf sync. Downloaded `.sty` files are version-pinned, unmanaged, and invisible to TeX Live updates. Same root cause: putting generated or external files where only human-authored source belongs.

## Failure modes prevented

- **L4** build artifacts in source dir — see [`docs/reference/failure-modes.md`](../docs/reference/failure-modes.md)
