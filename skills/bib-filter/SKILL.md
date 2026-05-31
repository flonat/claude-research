---
name: bib-filter
description: "Use when you need to filter a .bib file to only entries actually cited in a .tex project."
allowed-tools: Read, Glob, Grep, Write, Bash(ls*), Bash(wc*)
argument-hint: "[path-to-tex-or-project-dir]"
---

# Bibliography Filter

Produce a `filtered.bib` containing only the `.bib` entries actually cited in the LaTeX project.

## When to Use

- Before submission — strip unused references from the bibliography
- When a shared `.bib` (e.g., Paperpile/Paperpile export) contains hundreds of entries but the paper cites a subset
- To reduce `.bib` file size for Overleaf or arXiv upload
- As a cleanup step after major revision (removed sections may leave orphan citations)

## Process

### Step 1: Locate files

If given a directory, find the main `.tex` and `.bib` files:
- `.tex`: Glob for `*.tex` in the directory (and `paper/` subdirectory if it exists). The main file is the one containing `\begin{document}`.
- `.bib`: Look for `\bibliography{...}` or `\addbibresource{...}` in the main `.tex` to find the bib filename. Fall back to globbing `*.bib`.

If given a specific `.tex` file, derive the `.bib` from it.

### Step 2: Extract all citation keys from `.tex`

Scan **all** `.tex` files in the project (main + any `\input{}`/`\include{}` files) for citation commands:

```
\cite{key1,key2}
\citep{key1,key2}
\citet{key1}
\citealt{key1}
\citealp{key1}
\citeauthor{key1}
\citeyear{key1}
\citetext{key1}
\parencite{key1,key2}
\textcite{key1}
\autocite{key1}
\footcite{key1}
\fullcite{key1}
\nocite{key1}
```

Handle:
- Multiple keys in one command: `\cite{key1,key2,key3}` → extract all three
- Whitespace around commas: `\cite{key1, key2}` → trim
- Optional arguments: `\cite[p.~5]{key1}` or `\citep[see][]{key1}` → extract `key1`
- `\nocite{*}` → special case: means "include everything", so `filtered.bib` = full `.bib` (warn and stop)

Collect into a deduplicated set of cited keys.

### Step 3: Parse `.bib` and filter

Read the `.bib` file. For each entry (`@article{key,`, `@book{key,`, `@inproceedings{key,`, etc.):
- If the entry's key is in the cited set → include in output
- If not → exclude
- Preserve `@string{}`, `@preamble{}`, and `@comment{}` blocks (they may be needed by included entries)

### Step 4: Write `filtered.bib`

Write `filtered.bib` in the same directory as the original `.bib`.

Report:
```
Original: N entries
Cited: M keys found in .tex
Filtered: M entries written to filtered.bib
Removed: N-M unused entries
```

If any cited keys are **not found** in the `.bib`, list them as warnings (these are missing references — suggest running `/bib-validate`).

### Step 5: Suggest next steps

- "Replace `references.bib` with `filtered.bib`?" — ask before overwriting
- If missing keys were found: "Run `/bib-validate` to resolve M missing citation keys"

## Edge Cases

- **Multiple `.bib` files:** If the project uses multiple bib files (`\bibliography{refs1,refs2}`), read all of them and produce a single `filtered.bib` combining only cited entries
- **`\nocite{*}`:** Warn that all entries are cited and stop — filtering would be a no-op
- **Cross-references:** Some `.bib` entries use `crossref = {parent-key}`. If a cited entry cross-references another, include the parent even if it's not directly cited
- **Empty result:** If no citations found in `.tex`, warn and do not write an empty file

---

## Output Verification (Guard)

This skill writes files. Before any auto-commit, emit an outputs manifest and run the shared verifier. See [`skills/_shared/verify-outputs.md`](../_shared/verify-outputs.md) for the full protocol.

**Required tail steps** (before `git commit`):

1. Write manifest to `<project>/.claude/state/outputs-manifest-<UTC-timestamp>.json` listing every file this skill claims to have written in this invocation (paths relative to the project root).
2. Run:

   ```bash
   python3 "$HOME/.claude/skills/_shared/verify_outputs.py" \
       --manifest "$MANIFEST" \
       --project-root "$PROJECT_ROOT"
   ```

3. If the verifier exits non-zero, **do not commit** — surface the missing-files list to the user and stop. The verifier has already logged an `error` entry to `~/.claude/ecc/skill-outcomes.jsonl`, which feeds the launcher dashboard.

**Why:** closes the "hallucinated outputs" failure class (commit `b2cff75`, 2026-04-18).
