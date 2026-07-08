# Phase 4.2: Overleaf Separation Check

> Detailed check for `/audit-project-research` Phase 4.2.

Scan **all `paper*/` directories** (not just `paper/`) for files that violate the Overleaf separation rule. Detect paper directories with `ls -d paper*/ 2>/dev/null` — this catches `paper/`, `paper2/`, `paper-supplementary/`, etc. **This is a hard rule -- any violations are flagged as Missing (not Info).**

## Forbidden file types in `paper/`

| Pattern | Category |
|---------|----------|
| `*.py`, `*.R`, `*.jl`, `*.m`, `*.sh`, `*.ipynb`, `*.do` | Code |
| `*.csv`, `*.xlsx`, `*.json` (non-LaTeX), `*.dta`, `*.parquet`, `*.rds`, `*.pkl`, `*.feather`, `*.h5` | Data |
| `requirements.txt`, `pyproject.toml`, `renv.lock` | Package management |
| `.venv/`, `__pycache__/`, `node_modules/` | Runtime artifacts |

## Allowed in `paper/`

- `.tex`, `.sty`, `.cls`, `.bst`, `.bbl`, `.bib`
- `.pdf`, `.png`, `.eps`, `.jpg`, `.svg`, `.tikz` (figures)
- `.latexmkrc`, `latexmkrc`
- `out/` (build directory)
- `.gitignore`, `README.md` (if Overleaf-generated)

## Required in `paper/`

| File | Check | Severity |
|------|-------|----------|
| `.latexmkrc` | Must exist -- needed for `out/` build convention and local compilation | **Missing** if absent |

The `.latexmkrc` should contain at minimum `$out_dir = 'out';` and an `END {}` block to copy the PDF back. If it exists but is missing `$out_dir`, flag as **Degraded**.

## How to check

```bash
# Recursively find forbidden file types inside all paper*/ directories
for paperdir in "<project-path>"/paper*/; do
  [ -d "$paperdir" ] || continue
  find "$paperdir" -type f \( \
    -name "*.py" -o -name "*.R" -o -name "*.jl" -o -name "*.m" \
    -o -name "*.sh" -o -name "*.ipynb" -o -name "*.do" \
    -o -name "*.csv" -o -name "*.xlsx" -o -name "*.dta" \
    -o -name "*.parquet" -o -name "*.rds" -o -name "*.pkl" \
    -o -name "*.feather" -o -name "*.h5" \
    -o -name "requirements.txt" -o -name "pyproject.toml" \
    -o -name "renv.lock" \
  \) 2>/dev/null
done
```

Also check for directories that should never exist inside any paper directory:
```bash
for paperdir in "<project-path>"/paper*/; do
  [ -d "$paperdir" ] || continue
  find "$paperdir" -type d \( \
    -name ".venv" -o -name "__pycache__" -o -name "node_modules" \
    -o -name "renv" \
  \) 2>/dev/null
done
```

## Report format

For each violation found:

```
Overleaf separation violation: paper/<path-to-file>
  Category: Code / Data / Package management / Runtime artifact
  Remediation: Move to <suggested-project-directory>
```

Suggested destinations follow the rule in `.claude/rules/overleaf-separation.md`:
- Code files -> `code/` or `src/`
- Data files -> `data/raw/` or `data/processed/`
- Package files -> project root
- Notebooks -> `code/` or `experiments/`
