# Phase 4.5: LaTeX Build Config Consistency

> Detailed check for `/audit-project-research` Phase 4.5.

Every directory that contains `.tex` files must have the canonical `.latexmkrc` (`templates/latexmkrc/.latexmkrc`) so build artifacts stay in `out/` and the PDF is copied back to the source directory. This applies to **standalone paper dirs and Overleaf-symlinked paper dirs alike** — the file lives in the Overleaf target so it syncs to the web compiler too.

## Step 1: Find directories with `.tex` files

```bash
# Find all directories containing .tex files, deduplicated
# -L follows symlinks so Overleaf-symlinked paper/ dirs are included
find -L "<project>" -name "*.tex" -not -path "*/out/*" -not -path "*/.git/*" \
  -exec dirname {} \; | sort -u
```

## Step 2: Exclude directories

Skip these — they have their own conventions:

| Directory | Reason |
|-----------|--------|
| Any `out/` directory | Build output, not source |
| Any `legacy/` or `archive/` directory | Preserved old files, not actively compiled |

**Note:** Overleaf-symlinked `paper*/` directories are **not** excluded. They need `.latexmkrc` in the symlink target (the Overleaf folder) for both local and Overleaf web compilation.

## Step 3: Check each directory

### 3a: `.latexmkrc` existence

| Condition | Severity |
|-----------|----------|
| `.latexmkrc` exists | Check contents (Step 3b) |
| `.latexmkrc` missing | **Missing** — ".latexmkrc missing in {dir}/ — drop canonical from `templates/latexmkrc/.latexmkrc`" |

### 3b: `.latexmkrc` content validation

Read the `.latexmkrc` and check for required directives:

| Directive | Required | Severity if absent |
|-----------|----------|-------------------|
| `$out_dir = 'out'` (or equivalent) | Yes | **Degraded** — ".latexmkrc in {dir}/ missing `$out_dir = 'out'`" |
| `END { ... cp $out_dir/*.pdf ... }` block | Yes | **Degraded** — ".latexmkrc in {dir}/ missing PDF copy-back `END {}` block — PDF will only land in out/" |
| Engine auto-detect or explicit `$pdf_mode` | No | Not flagged — defaults are acceptable |

Match `$out_dir` flexibly: accept `$out_dir = 'out'`, `$out_dir = "out"`, `$out_dir='out'` (with or without spaces).

Match the `END {}` block by grepping for `END\s*\{.*cp.*\$out_dir.*\.pdf` (allowing whitespace/quote variations).

### 3c: Stale build artifacts

If `.latexmkrc` is correct but build artifacts exist in the source directory (not in `out/`), flag:

```bash
# Check for build artifacts alongside .tex files (not inside out/)
find "<dir>" -maxdepth 1 \( \
  -name "*.aux" -o -name "*.bbl" -o -name "*.blg" \
  -o -name "*.fdb_latexmk" -o -name "*.fls" -o -name "*.log" \
  -o -name "*.synctex.gz" -o -name "*.toc" -o -name "*.nav" \
  -o -name "*.snm" -o -name "*.vrb" -o -name "*.dvi" \
  -o -name "*.bcf" -o -name "*.run.xml" \
\) 2>/dev/null
```

| Condition | Severity |
|-----------|----------|
| Build artifacts in source directory | **Degraded** — "build artifacts in {dir}/ — run `latexmk -C` or move to out/" |
| No artifacts outside `out/` | OK |

## Report format

```
LaTeX Build Config:
  presentations/                          .latexmkrc OK (out/ + copy-back)
  paper-eaamo/paper/ (→ Overleaf)         .latexmkrc OK (out/ + copy-back)
  docs/venues/ejor/revision-1/response/   .latexmkrc OK (out/ + copy-back)
  correspondence/referee-reviews/.../analysis/  .latexmkrc missing
  paper-rand/paper/ (→ Overleaf)          .latexmkrc missing copy-back END block
```

## Remediation

When flagging a missing or degraded `.latexmkrc`, the fix is always the same — drop the canonical file:

```bash
TM=$(cat ~/.config/task-mgmt/path)
cp "$TM/templates/latexmkrc/.latexmkrc" <target-dir>/
```

For Overleaf-symlinked paper dirs, `<target-dir>` is the symlink path (which resolves through to the Overleaf folder).

Canonical source and rationale: `templates/latexmkrc/README.md`.

## When to skip

- If no `.tex` files exist anywhere in the project
