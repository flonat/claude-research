# Comparison Checklist & Classification Rules

> Reference file for `/latex-template`. Detailed check tables for Phase 2, classification rules for Phase 3, and auxiliary checks for Phase 4.

## Phase 2: Comparison — Detailed Checks

### Packages

| Check | Detail |
|-------|--------|
| Missing packages | In template but not in project |
| Extra packages | In project but not in template |
| Option differences | Same package loaded with different options |
| Load order | Flag if `hyperref` or `cleveref` are loaded out of order (hyperref must come before cleveref) |
| Duplicate loads | Same package loaded twice in the project |

**Package groups to check explicitly:**

- Core math: `mathtools`, `amssymb`, `amsmath`, `amsfonts`, `amsthm`
- Tables: `booktabs`, `longtable`, `multirow`, `tabularx`, `threeparttable`, `threeparttablex`
- Typography: `microtype`, `setspace`, `fontspec`, `unicode-math`
- Figures: `graphicx`, `subcaption`, `tikz`, `pgfplots`
- Utilities: `etoolbox`, `comment`, `enumitem`, `csquotes`
- Layout: `geometry`, `fancyhdr`, `titlesec`, `pdflscape`, `pdfpages`
- xcolor with `dvipsnames` option

### Hyperref

| Check | Detail |
|-------|--------|
| Missing keys | Template keys not in project's `\hypersetup` |
| Different values | Same key, different value (e.g., `linkcolor=blue` vs `linkcolor=black`) |
| Missing `\urlstyle{same}` | Template uses it; project should too |
| `cleveref` loaded after `hyperref` | Required ordering |

### Bibliography

| Check | Detail |
|-------|--------|
| System mismatch | biblatex vs natbib — this is a **Conflict**, never auto-resolved |
| Option differences | Missing or different biblatex options |
| Missing source mappings | Template's bibliography cleanup maps not in project |
| Missing field clearing | Template's `\AtEveryBibitem` rules not in project |
| Missing possessive citations | `\posscite`, `\Posscite`, `\posscites` commands |
| `\addbibresource` present | Must exist if using biblatex |

### Custom Commands

| Check | Detail |
|-------|--------|
| Missing commands | Template commands not defined in project |
| Different definitions | Same command name, different body |
| Missing column types | `L`, `C`, `R` column types |
| Missing math commands | `\R`, `\N`, `\E`, `\Prob`, `\indicator` |
| Missing operators | `\argmin`, `\argmax` |

### Theorem Environments

| Check | Detail |
|-------|--------|
| Missing environments | Template theorems not in project |
| Different styles | Same environment, different `\theoremstyle` |
| Different counters | Same environment, different counter relationship |
| Missing `\numberwithin` | Template uses `\numberwithin{equation}{section}` |

### Build Config

| Check | Detail |
|-------|--------|
| `.latexmkrc` exists | In project root or paper directory |
| Engine match | Template uses `lualatex` via `$pdf_mode = 4` |
| Output directory | Template uses `$out_dir = 'out'` |
| PDF copy-back | Template has `END { system("cp ...") }` |

---

## Phase 3: Classification Rules

Label every difference from Phase 2 with one of four categories:

| Label | Meaning | Action in `--apply` mode |
|-------|---------|--------------------------|
| **Adopt** | Template feature missing from project. Safe to add. | Apply automatically (with confirmation summary) |
| **Keep** | Project-specific addition not in template. Legitimate. | No action — informational only |
| **Conflict** | Same functionality loaded differently. Needs human judgement. | Always ask user via `AskUserQuestion` |
| **Drop** | Redundant or superseded by a template equivalent. | Apply automatically (with confirmation summary) |

### When to use each label

**Adopt** when:
- Package is in template but entirely absent from project
- Template command/environment is missing from project
- Template hyperref key is missing from project
- `.latexmkrc` is missing
- `dvipsnames` option is missing from xcolor

**Keep** when:
- Project loads a package not in the template (project-specific need)
- Project defines commands not in the template
- Project defines extra theorem environments
- Project has extra hyperref settings

**Conflict** when:
- biblatex vs natbib (different bibliography systems)
- Same package with incompatible options
- Same command name with different definitions
- Different `\theoremstyle` for the same environment name
- Different geometry margins

**Drop** when:
- Project loads a package that the template supersedes (e.g., `palatino` when template uses `fontspec`)
- Project defines a command identically to the template (true duplicate)
- Project loads a package twice

---

## Phase 4: Auxiliary Checks

Beyond the preamble files, check consistency of related files:

### main.tex

| Check | Detail |
|-------|--------|
| Preamble loading present | `\usepackage{your-template}` + `\usepackage{your-bib-template}` (new format) or `\input{settings}` (legacy) |
| `\documentclass` matches | Template uses `[12pt,a4paper]{article}` |
| `\printbibliography` present | Required if using biblatex |
| No `\bibliography{}` | Should not appear if using biblatex |
| No `\bibliographystyle{}` | Should not appear if using biblatex |

### .latexmkrc

| Check | Detail |
|-------|--------|
| Exists | In project root or paper directory |
| Engine | Template: `lualatex` via `$pdf_mode = 4` |
| Output dir | Template: `$out_dir = 'out'` |
| PDF copy-back | `END { system("cp $out_dir/*.pdf . 2>/dev/null") }` |

### Economics Paper Conventions (if `docs/domain-profile.md` exists or JEL codes present)

These checks apply when the project appears to be an economics paper (JEL codes in `main.tex`, domain profile referencing economics, or field journals in target list). Report as informational — these are field conventions, not strict template requirements.

| Check | Detail |
|-------|--------|
| Abstract singlespacing | `\singlespacing` or `\begin{singlespace}` inside abstract |
| JEL codes present | `\textbf{JEL Codes:}` outside the abstract environment |
| Keywords present | `\textbf{Keywords:}` outside the abstract environment |
| `\tablenote` command | Template defines `\tablenote{}` for `threeparttable` notes |
| `\fignote` command | Template defines `\fignote{}` for figure notes |
| `\figsource` command | Template defines `\figsource{}` for figure source attribution |
| No `\hline` in tables | Only `booktabs` rules (`\toprule`, `\midrule`, `\bottomrule`) |
| `\doublespacing` after title page | Body text double-spaced (economics convention) |
| `\singlespacing` before bibliography | References single-spaced |
