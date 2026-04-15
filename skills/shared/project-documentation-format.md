# Project Documentation — Format Conventions

> Conventions for ASCII diagrams, env vars, tone, LaTeX, Beamer, public variants, and validation.
> Split from [`project-documentation.md`](project-documentation.md) for leanness.

---

## ASCII Diagrams

### Direction Conventions

| Flow type | Direction | Example |
|-----------|-----------|---------|
| Data/request flow | Left-to-right | `User ──→ API ──→ DB` |
| Stage progression | Top-to-bottom | Stage 1 → Stage 2 → Stage 3 |
| Architecture layers | Top-to-bottom | Frontend → Backend → Database |
| Workflow chains | Left-to-right with branches | `A ──→ B ──→ C` with `└──→ D` |

### Symbol Legend

```
──→     directional flow
│       vertical connection
├──     branch (continuing)
└──     branch (terminal)
┌─┐     box corners (for containers)
▼ ▲     vertical arrows
```

### Labelling

- Label every box with its service/component name
- Label arrows only when the relationship isn't obvious (e.g., "OAuth", "REST API")
- Add parenthetical notes for data stores: `SQLite (results + cache)`
- Keep diagrams under 15 lines — split into multiple diagrams if needed

---

## Environment Variable Documentation

Use this table format everywhere env vars are documented:

```markdown
| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `OPENROUTER_API_KEY` | LLM access via OpenRouter | Yes | — |
| `OPENALEX_API_KEY` | OpenAlex bibliometric data | Yes | — |
| `SCOPUS_API_KEY` | Scopus search (optional) | No | — |
```

**Rules:**
- Required column: "Yes" or "No" — never blank
- Default column: the actual default value, or "—" if none
- Group by service (API keys together, app config together)
- In READMEs, show env vars inside bash code blocks with comments. In reference docs, use the table.
- `.env.example` must include every variable with a comment

---

## Tone by Audience

| Audience | Tone | Patterns |
|----------|------|----------|
| End users (user manual) | Approachable, instructional | "You can...", "Enter your...", "Results include..." |
| Developers (README) | Crisp, feature-focused | Active verbs: "Get", "Fetch", "Run", "Configure" |
| Maintainers (architecture) | Technical, precise | Third person: "The orchestrator wires...", "Requests flow through..." |
| Adopters (public repo) | Welcoming, honest | "Built for...", explicit audience statement |

---

## LaTeX Documentation

When a document exists in both markdown and LaTeX (e.g., user manual in `.md` and `.tex`), the markdown is the source of truth for content. The LaTeX version adds typographic polish.

### Standard Preamble (Article Style)

```latex
\documentclass[11pt,a4paper]{article}

\usepackage{geometry}       % Margins (2.5cm all sides)
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}        % Modern serif font (not Computer Modern)
\usepackage{microtype}      % Typographic refinement
\usepackage{parskip}        % Paragraph spacing, no indents
\usepackage{hyperref}       % Clickable links
\usepackage{xcolor}         % Custom colours
\usepackage{booktabs}       % Professional tables (\toprule, \midrule, \bottomrule)
\usepackage{longtable}      % Multi-page tables
\usepackage{enumitem}       % List customisation
\usepackage{listings}       % Code blocks
\usepackage[skins,breakable]{tcolorbox}  % Callout boxes
\usepackage{tikz}           % Diagrams
```

### Custom Commands

Define these reusable commands in the preamble for consistency:

```latex
\newcommand{\code}[1]{\texttt{\small #1}}           % Inline code
\newcommand{\filepath}[1]{\texttt{\small #1}}        % File paths
\newcommand{\skill}[1]{\texttt{/#1}}                 % Skill references
\newcommand{\hook}[1]{\texttt{#1}}                   % Hook references
\newcommand{\keyterm}[1]{\textbf{#1}}                % Key terminology
```

### Colour Palette for Callout Boxes

```latex
\definecolor{accentgreen}{HTML}{059669}   % Tip boxes
\definecolor{accentamber}{HTML}{D97706}   % Warning boxes
\definecolor{accentred}{HTML}{DC2626}     % Error/critical boxes
\definecolor{codebg}{HTML}{F3F4F6}        % Code background
\definecolor{codeframe}{HTML}{D1D5DB}     % Code border

\newtcolorbox{tipbox}[1][]{
    colback=accentgreen!5, colframe=accentgreen!60,
    fonttitle=\bfseries, title={#1}, sharp corners, boxrule=0.5pt}
\newtcolorbox{warnbox}[1][]{
    colback=accentamber!5, colframe=accentamber!60,
    fonttitle=\bfseries, title={#1}, sharp corners, boxrule=0.5pt}
```

### Table Formatting

- Use `booktabs` rules: `\toprule`, `\midrule`, `\bottomrule` — never vertical lines
- Column spec: `@{}lp{7cm}@{}` (remove outer padding, left column, paragraph column)
- Multi-page tables: `\begin{longtable}` with `\endhead` for repeating headers
- Always `\centering` within table environments

### md/tex Parity

When both formats exist, structural parity is required: every `##` heading in the markdown should have a corresponding `\section{}` in LaTeX. Content can differ slightly (LaTeX adds figures, better formatting), but the section structure must match. Validate with `validate_docs.py` check 2.

---

## Beamer Presentation Docs

Projects may include Beamer decks in `docs/` (e.g., `docs/scout-overview/`, `docs/setup/setup-overview/`). These are outward-facing documentation, not just slides.

### Standard Setup

```latex
\documentclass[aspectratio=169,11pt]{beamer}
\setbeamertemplate{navigation symbols}{}     % No nav clutter
\setbeamertemplate{footline}[frame number]   % Frame numbers only
```

- **Aspect ratio:** Always 16:9 (`aspectratio=169`)
- **Navigation symbols:** Disabled
- **Footline:** Frame number only (or custom three-part: author | title | X/Y)

### Colour Palette

Define a cohesive palette of 5-8 colours in the preamble. Established palette:

| Colour | Hex | Use |
|--------|-----|-----|
| `Midnight` | `1A1A2E` | Dark backgrounds, body text |
| `DeepBlue` | `16213E` | Frame title backgrounds |
| `RoyalBlue` | `0F3460` | Structure, bullet markers |
| `Coral` | `E94560` | Alerts, emphasis |
| `CloudWhite` | `FAFBFC` | Main background |
| `SoftGray` | `BDC3C7` | Subtitles, subdued text |
| `LightBlue` | `D6EAF8` | TikZ box fills |
| `SlateGray` | `5D6D7E` | Arrows, secondary elements |

### Frame Title Conventions

- Use **substantive claims**, not labels: "62 skills cover the full research lifecycle" not "Skills Overview"
- Optional subtitle for framing questions: "Every new AI session starts from zero"
- Keep titles to one line

### TikZ Diagram Styling

```latex
\begin{tikzpicture}[
    node distance=0.6cm and 0.8cm,
    box/.style={draw=SlateGray, rounded corners=3pt,
                minimum width=2.0cm, minimum height=0.75cm,
                align=center, fill=#1, text=Midnight},
    box/.default={LightBlue},
    arr/.style={-{Stealth[length=2mm]}, thick, color=SlateGray},
]
```

- Rounded corners (3pt), minimum dimensions, centred text
- Colour-code by component type (e.g., `Coral!20` for interfaces, `CloudWhite` for core, `SoftGray!30` for external)
- Stealth arrowheads, thick strokes

### Code Blocks in Beamer

Use small monospace fonts — slides need compact code:

```latex
\begin{lstlisting}[language={}, basicstyle=\ttfamily\fontsize{6.5}{8}\selectfont]
```

### Bullet Styles

- Level 1: `\tiny$\blacksquare$` in primary colour (filled square)
- Level 2: `\scriptsize$\blacktriangleright$` in secondary colour (right triangle)
- Enumerate: `\insertenumlabel.` in primary colour

---

## Public/Anonymized Variants

When a document has both private and public versions (e.g., `setup-overview.tex` and `setup-overview-public.tex`), follow these conventions.

### What to Anonymize

| Private | Public replacement |
|---------|-------------------|
| Author name | Generic descriptor ("PhD researcher") or GitHub handle |
| Institution names | Remove entirely |
| Exact component counts | Remove or genericize ("30+", "Skills" without number) |
| Specific project names | "Multiple active research projects" |
| vault references | "Task manager" (generic) |
| Date in `\date{}` | GitHub URL or "Open-source" descriptor |

### Sync Markers

For auto-generated or synced content in public markdown files, use HTML comment markers:

```markdown
<!-- MARKER-NAME:START -->
<!-- auto-generated by script-name.py — do not edit manually -->
[content here]
<!-- MARKER-NAME:END -->
```

- Marker names: UPPERCASE-HYPHENATED (`COMPONENT-TABLE`, `SKILLS-SUMMARY`, `FILE-TREE`)
- Attribution line after START: `auto-generated by ...` or `synced from private ...`
- Warning: `do not edit manually`

### Private LaTeX Headers

```latex
% ============================================================
% Document Title — Description
% Author · Month Year
% ============================================================
```

### Public LaTeX Headers

```latex
% ============================================================
% Document Title — Public Version (Format)
% Generated during sync — DO NOT EDIT MANUALLY
% Edit source-file.tex and re-run sync-script.sh
% ============================================================
```

---

## Automated Validation

Projects with documentation in multiple formats or locations should include a validation script that catches drift automatically.

### The `validate_docs.py` Pattern

- **Stdlib-only** — no venv needed, runs anywhere Python is installed
- **Location:** `scripts/validate_docs.py` in the project root
- **Severity levels:** FAIL (blocks CI) and WARN (informational, `--strict` promotes to FAIL)
- **Flags:** `--strict` (treat warnings as failures), `--check N` (run only check N)
- **Paths:** All resolved relative to script location — no hardcoded absolute paths
- **CI integration:** Run before tests in the CI pipeline

### Common Checks

| Check | Severity | What it catches |
|-------|----------|----------------|
| Help slug integrity | FAIL | WORKFLOW_TIPS slugs that don't match user-manual headings |
| md/tex section parity | WARN | Structural divergence between markdown and LaTeX versions |
| File path references | FAIL | Backtick-quoted paths in docs that don't exist on disk |
| Class/method references | FAIL | Code references in architecture docs that don't match source |
| Count accuracy | WARN | Claimed counts vs actual (data sources, templates, etc.) |
| Env var completeness | WARN | Settings fields missing from documentation |
