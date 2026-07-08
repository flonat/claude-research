---
name: preprint
description: Use when you need to create a preprint / working-paper variant of a paper currently in conference or journal format. Forks the existing Overleaf project — adds a `preprint/` subfolder using the user's `your-template` Template, ports the body content from the source paper. The preprint is accessed locally via the existing `paper-{venue}/paper/preprint/` path (subfolder under the conference paper's symlink); no separate `paper-wp/` directory. Trigger on "set up a working paper", "create a preprint", "WP version", "arXiv-ready version", "ready to preprint". Never creates a new top-level Overleaf project — always nests inside the existing one. Never uses the conference's own style (.sty / .cls); always swaps to `your-template`.
---

# Preprint — fork a WP variant inside the existing Overleaf project

> Take an existing `paper-{venue}/paper/` (Overleaf-linked, conference-styled) and produce a sibling `preprint/` subfolder *inside the same Overleaf project* that compiles via the user's working-paper template (`your-template` + `your-bib-template`). Port the body content but rebuild the preamble + title block from scratch — never just toggle the conference style.

## When to Use

- Paper has been submitted (or is ready to submit) and the user wants an arXiv / SSRN / institutional-repo preprint
- Drafting an open-access version that doesn't carry venue-specific page banners, checklists, or anonymity toggles
- Sharing with collaborators who shouldn't have to install `neurips_2026.sty` / `icml.sty` / etc.

## When NOT to Use

- The paper is already on the WP template (no source to port — start fresh from `Template`)
- The user wants to retarget to a *different* journal / conference (use `/retarget-journal`)
- The user wants to archive the conference draft (use `/archive-paper-draft`)

## Critical Rules

1. **Never create a new top-level Overleaf project.** The preprint always lives as a `preprint/` subfolder inside the source paper's existing Overleaf project. Reviewers and co-authors should be able to flip the Overleaf "Main document" setting to switch variants.
2. **Always use `your-template` (Template), never the conference style.** The whole point of a preprint is to drop venue-specific scaffolding. Toggling `[main]` → `[preprint]` on `neurips_2026.sty` (or equivalent) is *forbidden* — replace the preamble entirely.
3. **Source is read-only.** Never modify `paper-{venue}/paper/main.tex` or any of its siblings. The preprint is downstream; the conference draft remains canonical.
4. **Idempotent.** If `preprint/` already exists, refresh template files but never silent-overwrite a `main.tex` containing manual edits. Diff and prompt instead.
5. **Compile must verify.** A WP fork that doesn't build is worse than no fork. The skill compiles via `latexmk` at the end and prints a per-issue manual-fix list if the build fails.
6. **Never create a vault submission entry.** A preprint post is NOT a venue submission event — see `rules/preprint-vs-submission.md`. The atlas topic's `outputs[*]` (status: Posted) and the project CLAUDE.md cover it; `~/vault/submissions/` must stay untouched. Phase 7 (CLAUDE.md update) is the only place this skill records the preprint event; do not extend to vault submissions even when prompted by adjacent helpers.
7. **Archive the as-posted PDF once the post is live.** Per `rules/submission-file-archive.md`: download the canonical server copy (for arXiv, `https://arxiv.org/pdf/<id>` — the server copy IS authoritative for preprints), file it under `paper-<venue>/submission/archive/<date>-preprint/manuscript-as-posted.pdf` with a provenance README (URL, SHA-256, page/title check), and record `submitted_files:` on the atlas `outputs[*]` preprint entry. The entry's `posted_date` + `submitted_files` double as the `preprint-posted` event in the paper's atlas timeline.

---

## Phase 1 — Resolve Source and Target

1. **Source.** If a positional arg is given, treat it as the source paper directory (`paper-{venue}/paper/` or just `paper-{venue}/`). Otherwise:
   - Auto-detect a single `paper-*/paper/` matching `paper-*` excluding `paper-wp/`.
   - If multiple, list them and prompt user to pick.
2. **Target Overleaf folder.** Resolve `<source-paper-dir>` by following its symlink:
   - `paper-{venue}/paper -> ../../../../../Apps/Overleaf/<existing-folder>`
   - Target is `<existing-folder>/preprint/` *inside that same project*.
3. **Refuse if target already populated.** If `<existing-folder>/preprint/main.tex` exists:
   - Read it, hash it, compare to a fresh template-only baseline.
   - If it has manual edits → list them, ask whether to refresh template files only (keep main.tex), refresh all (overwrite main.tex too), or abort.
4. **Verify Template source exists.** Confirm Template is at the correct Dropbox path for this machine — on Mac Mini that's `/Volumes/SSD/Dropbox/Apps/Overleaf/Template/`, on MacBook `~/Library/CloudStorage/Dropbox/Apps/Overleaf/Template/`. Resolve via `hostname` check per `multi-machine.md`. Must contain `your-template.sty`, `your-bib-template.sty`, `.latexmkrc`. If not → abort with instructions to clone Template from Overleaf first.
5. **No separate paper-wp/ directory.** The preprint lives entirely inside the existing Overleaf project as `<existing-folder>/preprint/`, accessed locally via `<source-paper-dir>/preprint/` (the existing `paper-{venue}/paper/` symlink already covers it). The tracked PDF backup goes to `<source-paper-dir-parent>/backup/preprint-vcurrent.pdf` (e.g., `paper-ieee-sp/backup/preprint-vcurrent.pdf`) — alongside the conference paper's backup PDF in the same `backup/` directory.

## Phase 2 — Stage Template into `preprint/`

Copy the following from `~/Library/CloudStorage/Dropbox/Apps/Overleaf/Template/` into `<existing-folder>/preprint/`:

| File | Action |
|------|--------|
| `your-template.sty` | Copy verbatim |
| `your-bib-template.sty` | Copy verbatim |
| `.latexmkrc` | Copy verbatim (LuaLaTeX, output to `out/`, copies PDF back) |
| `sections/` | Copy directory verbatim (skeleton section files) |
| `README.md` | **Skip** — template README does not belong in Overleaf paper folder per overleaf-separation rule |
| `paperpile.bib` | Skip — populated in Phase 4 from source's `.bib` |
| `main.tex` | Skip — rebuilt in Phase 3 |
| `out/`, `log/` | Skip — build artefacts |

These are dependencies of the WP class, not artefacts of the source paper. They must come from Template, never from the conference draft.

## Phase 3 — Port `main.tex`

Build `<existing-folder>/preprint/main.tex` by combining the WP skeleton with ported content from the source.

### What to port FROM the source `main.tex`

| Element | How |
|---------|-----|
| `\title{...}` | Lift verbatim |
| `\author{...}` | Lift verbatim if non-anonymous; otherwise prompt user for affiliations and emails |
| `\begin{abstract} ... \end{abstract}` | Lift verbatim |
| Theorem / lemma / definition declarations (`\newtheorem{...}{...}`) | Port — `your-template` declares some but not necessarily all the source's environments |
| `\input{headline_macros}` | Port if file exists; copy `headline_macros.tex` to preprint/ |
| Body content (everything between `\maketitle` and `\bibliography{...}` / `\end{document}`) | Lift verbatim |
| `\appendix` block (if present) | Lift verbatim — but strip venue-specific subsections (see below) |

### What to STRIP

| Element | Why |
|---------|-----|
| `\documentclass{article}` and original `\usepackage{...}` block | Replaced by WP preamble |
| Conference style: `\usepackage[...]{neurips_2026}`, `\usepackage{icml*}`, etc. | Forbidden by Critical Rule 2 |
| `\input{checklist}` and any `\section*{NeurIPS Paper Checklist}` | Venue-specific |
| Anonymous-mode toggles (`\anonymous`, `\if@anonymous`, blind-submission `\thanks` blocks) | Preprints are non-blind |
| `\bibliographystyle{plainnat}` + `\bibliography{references}` | Replaced by `your-bib-template` (`\printbibliography` if biblatex, or matched fallback) |
| Page-1 venue banners, footer macros, copyright lines | Venue-specific |
| `\nocite{*}` and other reviewer-only debugging | Cleanup |

### What to ADD

Build the WP `main.tex` skeleton:

```latex
\documentclass[12pt,a4paper]{article}

\usepackage{your-template}
\usepackage[harvard]{your-bib-template}

% your-template.sty pre-declares: theorem, proposition, lemma, corollary,
% definition, assumption, example, remark, hypothesis. ONLY add envs the
% source uses that are not in this list (e.g. `conjecture`). Re-declaring
% any of the above triggers `Command \theorem already defined`.
\newtheorem{conjecture}[theorem]{Conjecture}  % example — replace with what source actually needs

\input{headline_macros}  % if source has it

\title{<ported title>\thanks{<acknowledgements — leave TODO if source has none>}}
\author{<ported authors>}
\date{<GENERATION-DATE>}  % hard-coded date the preprint was generated, NOT \today.
                          % Substitute with the literal date (e.g., "19 May 2026").
                          % \today re-evaluates on every compile, which would shift
                          % the preprint's claimed publication date arbitrarily.

\begin{document}

\begin{titlepage}
    \maketitle
    \begin{abstract}
        \noindent <ported abstract body>

        \bigskip
        \noindent\textbf{Keywords:} <TODO>
    \end{abstract}
    \setcounter{page}{0}
    \thispagestyle{empty}
\end{titlepage}

\clearpage
\doublespacing

<ported body>

\printbibliography

\appendix
<ported appendix, with checklist stripped>

\end{document}
```

**Citation syntax port:** if source uses `\citep{}` / `\citet{}` (natbib), convert to biblatex equivalents (`\parencite{}` / `\textcite{}`) — `your-bib-template` is biblatex-based. This is a search-replace pass on the ported body.

### What to FLAG (don't auto-fix)

- Custom citation commands beyond `\citep`/`\citet` (e.g., `\citeauthoryear`, `\citealp`) → flag with line numbers
- Hyperref configuration in source preamble → flag if non-default
- `\input{}` / `\include{}` of files not in the source paper dir → flag missing dependencies
- `\graphicspath{}` overrides → flag and have user re-point to `figures/`

## Phase 4 — Port Bibliography and Figures

1. **Bibliography.** Find the source's `.bib` (`references.bib`, `paperpile.bib`, etc.). Copy its contents to `<preprint>/paperpile.bib`. If the source bib is heavily filtered for the conference draft, re-run `/bib-filter` with the new `main.tex` after Phase 5 compile.
2. **Figures.** If source has `figures/` directory, copy verbatim to `preprint/figures/`. If figures are inline (e.g., TikZ), they ride along inside `main.tex` body content — no separate copy needed.
3. **Auxiliary inputs.** Copy any `\input{}`'d files referenced from the body (typically just `headline_macros.tex` for code-generated stats).

## Phase 5 — Compile and Verify

1. `cd <preprint>/ && latexmk main.tex` (uses `.latexmkrc` → LuaLaTeX → biber → re-run pdflatex).
2. **If compile passes:** print page count, file size, "compile clean".
3. **If compile fails:** parse the log, surface the top 3 errors with file:line references, and print the most likely fix per error from this catalogue:

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Undefined control sequence \citep` | natbib → biblatex | Search-replace `\citep` → `\parencite`, `\citet` → `\textcite` |
| `Command \theorem already defined` (or any of `proposition`, `lemma`, `corollary`, `definition`, `assumption`, `example`, `remark`, `hypothesis`) | Re-declaring an env that your-template already provides | Drop the duplicate `\newtheorem{...}` from the ported preamble; keep only the envs your-template lacks (typically `conjecture`) |
| `Package biblatex Error: 'harvard' invalid` | Style mismatch | Drop `[harvard]` from `\usepackage[...]{your-bib-template}` if local TeX install lacks the harvard style |
| `Missing $ inserted` near a theorem | your-template redefines amsmath ordering | Verify theorem declarations are AFTER `\usepackage{your-template}` |
| `File 'neurips_2026.sty' not found` | Stripping didn't catch the package call | Search source for residual `\usepackage{neurips_2026}` or similar |
| `LuaLaTeX required` from a `\RequirePackage{fontspec}` | User ran `pdflatex` instead of `lualatex` | Confirm `.latexmkrc` is in place; re-run `latexmk` |
| `Citation 'X' undefined` for many keys | Bibliography file empty or biber not run | Verify `paperpile.bib` is populated; force `latexmk -gg` to regenerate |

Limit retry attempts to 2 — don't loop indefinitely on a fundamentally incompatible source.

## Phase 6 — Refresh Tracked PDF Backup

The preprint compile output (`<existing-folder>/preprint/main.pdf`) lives on the Overleaf side and syncs cross-machine via Dropbox. For faster cross-machine availability via `git pull`, also stash a copy under the source paper-dir's tracked backup:

```bash
cp <existing-folder>/preprint/main.pdf <project>/<source-paper-dir-parent>/backup/preprint-vcurrent.pdf
```

Example for an IEEE source: `paper-ieee-sp/backup/preprint-vcurrent.pdf` (sibling of the existing `paper-ieee-sp_vcurrent.pdf`).

No separate `paper-wp/` symlink is created — the preprint is accessed locally via the existing `paper-{venue}/paper/preprint/` path (subfolder under the conference paper's symlink).

## Phase 7 — Update Project CLAUDE.md

Record the preprint generation in the project's `CLAUDE.md` (project root, not the Overleaf side). Add or update a line under the "Status & Venue" or "Paper variants" section noting:

```markdown
- **Preprint variant:** generated YYYY-MM-DD at `paper-{venue}/paper/preprint/` (`your-template` template, single-column 12pt A4 double-spaced; compiles under LuaLaTeX via local `.latexmkrc`).
```

If the project doesn't have a clearly-named section for paper variants, append it under the existing "Status & Venue" block. Don't restructure CLAUDE.md beyond the minimal addition.

## Phase 8 — Final Summary

```
Preprint variant created.

Source:    paper-neurips/paper/ (Paper ASG Strategic DP Auditing (NeurIPS 26))
Target:    <Overleaf>/Paper ASG Strategic DP Auditing (NeurIPS 26)/preprint/
           (accessed locally via paper-neurips/paper/preprint/)
Template:  your-template (LuaLaTeX, Harvard biblatex)
Build:     out/main.pdf — XX pages, X.X MB
Backup:    paper-neurips/backup/preprint-vcurrent.pdf (git-tracked)
CLAUDE.md: updated with preprint generation date

Manual TODOs:
  • Set Overleaf "Main document" to preprint/main.tex (Menu → Settings)
  • Verify Overleaf project compiler is LuaLaTeX (Menu → Settings → Compiler)
  • Fill in title \thanks{} acknowledgements (current: TODO placeholder)
  • Add Keywords: line in abstract block
  • Review citation syntax port — N \citep/\citet calls converted to biblatex
  • [If figures/] verify graphicspath is correct
```

### Version bump → changelog

When this is a **refresh of an already-posted preprint** (the source paper
advanced and you're producing arXiv vN+1), generate a changelog for the version
note: run `/latex-diff` between the previously-posted `preprint/main.tex` (the
git revision or `backup/preprint-vcurrent.pdf`'s source revision) and the
refreshed one, filtered to `--semantic-only`. Surface the change list so the user
can write the "Changes in vN+1" note — do not edit the manuscript to add it.
First posting (no prior version) skips this.

## Examples

```bash
# Auto-detect single paper-{venue}/
/preprint

# Specify source explicitly (multi-paper project)
/preprint paper-neurips

# Refresh — preprint/ already exists, refresh template files only
/preprint paper-neurips --refresh-template

# Refresh — overwrite main.tex (lose manual edits)
/preprint paper-neurips --rebuild-main
```

## Failure Modes

| Failure | What the skill does |
|---------|---------------------|
| No `paper-*/` found | Print "no source paper directory found"; exit |
| Multiple `paper-*/` candidates | List them, prompt user to pick or pass arg |
| Source `paper/` is not a symlink | Print "source paper not Overleaf-linked — manual upload required for the preprint subfolder" and proceed |
| `Template` not in Overleaf folder | Abort with: "Clone Template from Overleaf to your local Overleaf folder first" |
| Existing `preprint/main.tex` has manual edits | Diff against fresh template; ask: refresh template only / rebuild main / abort |
| Existing `preprint/` directory not from this skill | Refuse — user must clear it manually (avoid silent data loss) |
| Compile fails after 2 retries | Print remaining errors and manual-fix catalogue; leave preprint/ in place for user to fix |
| Source has anonymous authors | Prompt for real author names + affiliations + emails before proceeding |

## Cross-References

- `references/venue-toggles.md` — short reference of conference-style stripping patterns (NeurIPS checklist regex, ICML camera-ready toggles, etc.)
- `/latex-diff` — on a version bump, generate the vN→vN+1 changelog for the arXiv version note (see "Version bump → changelog" above)
- `/retarget-journal` — for conference-to-conference moves (uses different style, this skill always uses `your-template`)
- `/archive-paper-draft` — for paper variants that should be archived rather than preprinted
- `/bib-filter` — run after Phase 5 if the ported `paperpile.bib` is bloated
- `/latex` — if compile fails and you want the autonomous error-resolution loop instead of the catalogue in Phase 5

## Citation Contract

<!-- paperpile-citation-contract -->
1. Paperpile is the only source of truth for committed citation keys and BibTeX metadata.
2. Before writing `\cite{key}`, verify with `paperpile get-item key` and `paperpile export-bib key`.
3. Resolve unknowns in order: DOI lookup → Paperpile substring search → `refpile` semantic search → Paperpile verify.
4. A DOI miss is **not** non-membership; continue with title/author search and refpile.
5. If unresolved, write `\CiteTodo{slug}{title/author/year/DOI hint}` — never a guessed key.
6. Drafting sub-agents must not write/edit the active `.bib`; only the orchestrator regenerates it from Paperpile exports.
7. Stage genuine new refs under `.paperpile-import/` for manual Paperpile import; don't cite until Paperpile mints the key.
8. Run `scripts/bib/citation_lint.py` before commit; zero placeholders, zero non-Paperpile keys, zero hand-authored metadata.

See `rules/paperpile-citations.md` for the full workflow.
