---
name: latex-autofix
description: "LaTeX compilation with autonomous error resolution. Build artifacts go to out/, PDF is copied back to source directory. Parses logs, auto-fixes known errors (missing packages, font conflicts, citation issues, bad paths, stale cache), and runs citation audit on success."
allowed-tools: Bash(latexmk*), Bash(xelatex*), Bash(pdflatex*), Bash(biber*), Bash(bibtex*), Bash(mkdir*), Bash(ls*), Bash(wc*), Read, Write, Edit, Grep, Glob
argument-hint: [tex-file-path]
---

# LaTeX Auto-Fix Compilation

> Compile LaTeX documents with autonomous error detection and resolution. Wraps the standard `/latex` workflow with a fix-loop that handles the most common compilation failures without manual intervention.

## When to Use

- **Default method** for all LaTeX compilation — use this instead of `/latex` unless you need manual control
- Any `.tex` file that should compile to PDF
- When compilation fails and you want automatic diagnosis and repair
- When you want a post-compilation citation audit

## When NOT to Use

- Quick one-off compilations where you already know the document is clean — `/latex` is fine
- Documents with exotic custom classes that need manual debugging

---

## Quality Scoring

Apply numeric quality scoring using the shared framework and skill-specific rubric:

- **Framework:** [`../shared/quality-scoring.md`](../shared/quality-scoring.md) — severity tiers, thresholds, verdict rules
- **Rubric:** [`references/quality-rubric.md`](references/quality-rubric.md) — issue-to-deduction mappings for this skill

Start at 100, deduct per issue found, apply verdict. Include the Score Block in the Phase 5 report.

## Critical Rules

1. **Build artifacts go to `out/`, PDF stays in the source directory.** Ensure `.latexmkrc` exists with `$out_dir = 'out'` and an `END {}` block to copy the PDF back (see pre-flight below). For VS Code builds, `.latexmkrc` in subdirectories is **not picked up** — see `/latex` skill's "VS Code LaTeX Workshop Gotchas" section for the required `.vscode/settings.json` config (`-cd`, `-outdir=out`, `forceRecipeUsage: true`).
2. **Maximum 5 fix iterations.** If the document still has errors after 5 auto-fix cycles, stop and report the unresolved errors to the user.
3. **Never silently swallow errors.** Every fix must be reported: what was wrong, what was changed, and which file was edited.
4. **Preserve user intent.** Auto-fixes should be minimal and conservative. Add packages or overrides — never remove user content.
5. **Citation audit requires clean compilation.** Only run the `\cite{}` vs `.bib` cross-check after zero errors.
6. **Run `/validate-bib` when new citations were added.** The Phase 4 citation audit only checks key cross-references. When `.bib` entries were added or modified since the last validation, also run `/validate-bib` for full metadata quality checks (preprint staleness, DOI presence, required fields, author formatting). This is mandatory — do not skip it.

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
5. **Identify the `.bib` file(s)** referenced in the document (scan for `\bibliography{}`, `\addbibresource{}`, or `\bibinput{}`). Note their paths for Phase 3.

### Phase 2: Compile–Fix Loop

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

## Integration with Other Skills

| Situation | Delegate to |
|-----------|-------------|
| Need to find or verify a bibliography entry | `/literature` |
| Full academic proofreading after clean compilation | `/proofread` |
| Detailed `.bib` validation beyond cite-key matching | `/validate-bib` |
| Beamer presentations specifically | `/beamer-deck` (which uses this skill internally for compilation) |

---

## Examples

### Basic usage

> "Compile my paper at `~/papers/mcdm-survey/main.tex`"

Runs the full protocol: pre-flight → compile–fix loop → report → citation audit.

### After fixing a known issue

> "Recompile — I added the missing package manually"

Runs from Phase 2 directly (pre-flight can be skipped if `.latexmkrc` and `out/` already exist).

### Targeted fix

> "My paper won't compile — something about Bbbk"

Identifies as Pattern 2 (font conflict), applies the `\let\Bbbk\relax` fix, recompiles.
