---
name: latex
description: "Use when you need to compile a LaTeX document — includes autonomous error resolution, citation audit, and quality scoring."
allowed-tools: Bash(latexmk*), Bash(xelatex*), Bash(pdflatex*), Bash(biber*), Bash(bibtex*), Bash(mkdir*), Bash(ls*), Bash(wc*), Bash(cp*), Read, Write, Edit, Grep, Glob
argument-hint: [tex-file-path]
---

# LaTeX Document Compilation

> Default compilation skill for all LaTeX documents. Compiles with autonomous error detection and resolution (up to 5 iterations), runs a citation audit on clean builds, and produces a quality score.

## When to Use

- **Default method** for all LaTeX compilation
- Any `.tex` file that should compile to PDF
- When compilation fails and you want automatic diagnosis and repair
- When you want a post-compilation citation audit

## When NOT to Use

- Markdown documents — use plain markdown, not LaTeX
- Quick notes or drafts — LaTeX overhead not worth it
- Documents that don't need citations, equations, or precise formatting
- Documents with exotic custom classes that need manual debugging

---

## Quality Scoring

Apply numeric quality scoring using the shared framework and skill-specific rubric:

- **Framework:** [`../shared/quality-scoring.md`](../shared/quality-scoring.md) — severity tiers, thresholds, verdict rules
- **Rubric:** [`references/quality-rubric.md`](references/quality-rubric.md) — issue-to-deduction mappings for this skill

Start at 100, deduct per issue found, apply verdict. Include the Score Block in the final report.

## Critical Rules

1. **Build artifacts go to `out/`, PDF stays in the source directory.** Ensure `.latexmkrc` exists with `$out_dir = 'out'` and an `END {}` block to copy the PDF back (see pre-flight below). For VS Code builds, `.latexmkrc` in subdirectories is **not picked up** — see "VS Code Integration" section for the required `.vscode/settings.json` config.
2. **NEVER write BibTeX entries from memory.** Always verify against web sources (CrossRef, Google Scholar, DOI lookup) before writing. See the `/literature` skill.
3. **Check document class before adding packages.** Some classes load packages internally (e.g., `elsarticle` loads `natbib` — adding `\usepackage{natbib}` causes errors).
4. **Maximum 5 fix iterations.** If the document still has errors after 5 auto-fix cycles, stop and report the unresolved errors to the user.
5. **Never silently swallow errors.** Every fix must be reported: what was wrong, what was changed, and which file was edited.
6. **Preserve user intent.** Auto-fixes should be minimal and conservative. Add packages or overrides — never remove user content.
7. **Citation audit requires clean compilation.** Only run the `\cite{}` vs `.bib` cross-check after zero errors.
8. **Run `/bib-validate` when new citations were added.** The citation audit only checks key cross-references. When `.bib` entries were added or modified since the last validation, also run `/bib-validate` for full metadata quality checks (preprint staleness, DOI presence, required fields, author formatting). This is mandatory.

---

## Protocol

### Phase 1: Pre-flight

1. **Locate the `.tex` file.** Resolve the path (absolute or relative to CWD).
2. **Identify the project directory** — the folder containing the `.tex` file.
3. **Ensure `.latexmkrc` exists** in the project directory with at minimum:
   ```perl
   $out_dir = 'out';
   # Copy PDF back to source directory after build
   END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
   ```
   If a `.latexmkrc` already exists, verify it sets `$out_dir = 'out'` and has the `END {}` block. If either is missing, add it. Do not overwrite other settings.
4. **Create `out/` directory** if it doesn't exist: `mkdir -p <project-dir>/out`.
5. **Identify the `.bib` file(s)** referenced in the document (scan for `\bibliography{}`, `\addbibresource{}`, or `\bibinput{}`). Note their paths for Phase 4.

### Phase 2: Compile-Fix Loop

Run up to **5 iterations**. Each iteration:

#### Step 2a — Compile

```bash
cd <project-dir> && latexmk -interaction=nonstopmode <filename>.tex 2>&1
```

Capture the full output. The log file will be at `out/<filename>.log`.

#### Step 2b — Read the log

Read `out/<filename>.log` in full. Parse for errors and warnings.

#### Step 2c — Classify errors

Check the log against the known error patterns below. If an error matches, apply the fix and go to Step 2a. If no known pattern matches, record the error as **unresolved** and stop the loop.

---

### Known Error Patterns & Auto-Fixes

Check the log against these patterns. Full fix instructions: [`references/known-errors.md`](references/known-errors.md)

| # | Pattern | Key log signature |
|---|---------|-------------------|
| 1 | Missing package | `File '<pkg>.sty' not found` or undefined command from known package |
| 2 | Font/symbol conflicts | `Command \<name> already defined` |
| 3 | Undefined citation | `Citation '<key>' ... undefined` or biblatex entry not found |
| 4 | Missing image/file | `File '<path>' not found` (pdftex.def or LaTeX) |
| 5 | Stale auxiliary files | Corrupted `.aux`/`.bbl`/`.bcf`, or `no \bibstyle command` |
| 6 | Beamer/enumitem clash | `Option clash for package enumitem` or `\item already defined` |
| 7 | xcolor option conflicts | `Option clash for package xcolor` or undefined `\rowcolor` |
| 8 | TikZ reserved keys | `I do not know the key '/tikz/<name>'` or pgfkeys error |

If an error matches, read the full fix from the reference and apply it. If no pattern matches, record as **unresolved** and stop the loop.

---

### Phase 2.5: PDF Backup (paper directories only)

**Only run if Phase 2 ended with a successful compilation (PDF exists).**

If the `.tex` file is inside a `paper-{venue}/paper/` structure (where `paper/` is a symlink to Overleaf):

1. **Identify the paper wrapper** — the parent of the `paper/` symlink (e.g., `paper-jbdm/`).
2. **Create the backup directory:** `mkdir -p <paper-wrapper>/backup`
3. **Copy the PDF:**
   ```bash
   cp <paper-wrapper>/paper/<filename>.pdf <paper-wrapper>/backup/<wrapper-name>_vcurrent.pdf
   ```

**Detection logic:**
- The project directory containing the `.tex` file is a symlink named `paper`
- Its parent directory name starts with `paper-`
- If either condition is false, skip this phase silently

---

### Phase 3: Final Report

After the loop ends (either clean compilation or max iterations reached), report:

#### Compilation Status

| Field | Value |
|-------|-------|
| **Status** | Clean / Errors remaining |
| **Iterations** | N of 5 |
| **Pages** | (from log: `Output written on ... (N pages)`) |
| **Warnings** | Count of remaining warnings (overfull/underfull hbox, etc.) |
| **Fixes applied** | List each fix: what error, what was changed, which file |
| **Unresolved errors** | List any errors that couldn't be auto-fixed |

#### How to extract page count

```bash
grep -o "Output written on .* ([0-9]* page" out/<filename>.log | grep -o "[0-9]* page"
```

#### How to count warnings

```bash
grep -c "Warning" out/<filename>.log
```

**Breadcrumb:** Append to `.planning/state.md` (if exists) or `.context/current-focus.md`:
```
### [/latex] Compilation complete [YYYY-MM-DD HH:MM]
- **Done:** [Clean/Errors remaining, N iterations, N pages, N fixes applied]
- **Outputs:** [PDF at <path>]
- **Next:** [Citation audit (if clean) or manual error resolution]
```

---

### Phase 4: Citation Audit (clean builds only)

**Only run this phase if Phase 2 ended with zero errors.**

1. **Extract all `\cite` keys** from the `.tex` file (and any `\input`/`\include` files):
   - Match `\cite{...}`, `\citep{...}`, `\citet{...}`, `\textcite{...}`, `\parencite{...}`, `\autocite{...}`, and multi-key variants like `\cite{key1,key2}`.
2. **Extract all bib entry keys** from the `.bib` file(s): match `@<type>{<key>,`.
3. **Cross-reference:**

| Check | What it finds |
|-------|--------------|
| **Missing in .bib** | Keys cited in `.tex` but absent from `.bib` |
| **Unused in .tex** | Keys defined in `.bib` but never cited |
| **Possible typos** | Near-matches between missing cite keys and existing bib keys |

4. **Report** the results as a table. Do not modify any files during the audit — report only.

---

### Phase 5: Quality Score

After all phases complete, compute the quality score:

1. Read [`references/quality-rubric.md`](references/quality-rubric.md) for deduction mappings.
2. Log every issue from Phases 2-4 (unresolved errors, remaining warnings, citation mismatches).
3. Compute score (100 - total deductions), apply verdict per [`../shared/quality-scoring.md`](../shared/quality-scoring.md).
4. Append the Score Block to the compilation report:

```markdown
## Quality Score

| Metric | Value |
|--------|-------|
| **Score** | XX / 100 |
| **Verdict** | Ship / Ship with notes / Revise / Revise (major) / Blocked |

### Deductions

| # | Issue | Tier | Deduction | Category |
|---|-------|------|-----------|----------|
| 1 | [description] | [tier] | -X | [category] |
| | **Total deductions** | | **-XX** | |
```

---

## Configuration Reference

### Output Directory

All LaTeX build artifacts (`.aux`, `.log`, `.bbl`, `.fls`, etc.) go to an `out/` subfolder relative to the source file. The **PDF is copied back** to the source directory after each successful build, so it lives alongside the `.tex` file for easy access.

The PDF-copy convention is enforced in **two places** — keep them in sync when making changes:

1. **`.latexmkrc`** (per-project) — Perl `END {}` block copies PDF after terminal/Claude Code builds
2. **VS Code `.vscode/settings.json`** (per-workspace) — explicit latexmk args in LaTeX Workshop tool definition

VS Code integration, engine auto-detection (pdfLaTeX/XeLaTeX/LuaLaTeX), manual override configs, reference checking scripts, and manual compilation commands:

**[references/latex-configs.md](references/latex-configs.md)**

### Overleaf-Synced Projects

When a project is synced to Overleaf (via Dropbox or Git):
- The `out/` directory will sync to Overleaf but Overleaf ignores it — this is fine
- Always use `.latexmkrc` to enforce `out/` — Overleaf ignores this file too
- Overleaf compiles independently on its server; local compilation is for verification only
- The `.bst` file (e.g., `elsarticle-harv.bst`) lives in the source directory, not `out/`

### Local-Only Projects (No Overleaf)

Not all projects sync to Overleaf. For local-only projects:
- The same `out/` and `.latexmkrc` conventions apply — this keeps the working directory clean regardless of sync method
- There is no `paper/` symlink — `.tex` files live directly in the project root or a subdirectory

---

## Templates

### Working Paper Template

When creating a **new working paper**, use the template. The canonical location is the local git repo:

1. `templates/latex-wp/` (in Task Management — canonical source, git-tracked)

The template contains:

| File | Purpose |
|------|---------|
| `main.tex` | Document entry point with structure |
| `your-template.sty` | Packages, layout, formatting, math environments |
| `your-bib-template.sty` | Bibliography config (biblatex, source cleanup, Harvard style) |
| `references.bib` | Bibliography file (initially empty) |
| `out/` | Compilation output directory |

**To create a new working paper:**

1. Copy the template files to your new project folder
2. Rename as needed
3. Update `main.tex` with your title, author, abstract
4. Add references to `references.bib`
5. Compile with `latexmk main.tex`

### Citation Style Toggle

The template uses **biblatex/biber** with a toggle for Harvard vs generic authoryear style.

In `main.tex`, control the style via package option:

```latex
\usepackage[harvard]{your-bib-template}    % Harvard style (default)
\usepackage[noharvard]{your-bib-template}  % Generic authoryear style
```

### Bibliography File Naming

**Always name the bibliography file `references.bib`** — for any paper, whether using the working paper template or not. This is the standard naming convention across all projects.

### Bibliography Commands

The template uses biblatex. In `main.tex`:

```latex
\printbibliography  % (not \bibliography{references})
```

If you need natbib instead, do not load `your-bib-template` and use:
```latex
\bibliographystyle{agsm}
\bibliography{references}
```

---

## Related Skills

| Situation | Delegate to |
|-----------|-------------|
| Need to find or verify a bibliography entry | `/literature` |
| Full academic proofreading after clean compilation | `/proofread` |
| Detailed `.bib` validation beyond cite-key matching | `/bib-validate` |
| Beamer presentations specifically | `/beamer-deck` (which uses this skill internally for compilation) |
| Fleet-wide compilation health check | `/latex-health-check` (project discovery, 3 iterations per project, cross-project checks) |

---

## Examples

### Basic usage

> "Compile my paper at `~/papers/mcdm-survey/main.tex`"

Runs the full protocol: pre-flight → compile-fix loop → report → citation audit → quality score.

### After fixing a known issue

> "Recompile — I added the missing package manually"

Runs from Phase 2 directly (pre-flight can be skipped if `.latexmkrc` and `out/` already exist).

### Targeted fix

> "My paper won't compile — something about Bbbk"

Identifies as Pattern 2 (font conflict), applies the `\let\Bbbk\relax` fix, recompiles.
