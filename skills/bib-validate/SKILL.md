---
name: bib-validate
description: "Use when you need to validate a paper's bibliography — cross-references \\cite{} keys against .bib files or embedded \\bibitem entries, finds missing/unused/typo'd keys, and checks every key against the Paperpile library via the local resolver. Deep verification mode spawns parallel agents for DOI/metadata validation at scale. Fix mode rekeys drifted keys to canonical and stages missing entries for Paperpile."
allowed-tools: Read, Glob, Grep, Task, Write, Bash(mkdir*), Bash(ls*), Bash(rm*), Bash(paperpile*), Bash(python3*), Bash(latexmk*)
argument-hint: "[project-path or tex-file] [--verify-doi] [--fix]"
---

# Bibliography Validation

**LIBRARY-FIRST RULE: ALWAYS cross-reference all `.bib` keys against Paperpile during validation** — via ONE dry-run of `scripts/bib/rekey_to_canonical.py` (Task-Management; matches the local library JSON in ~5s), NOT per-key `paperpile search-library` loops or lookup sub-agents. This catches key drift between the `.bib` file and the reference manager. See the Reference Manager Cross-Reference section.

## Output Path

Per `rules/review-artefact-routing.md` (auto-loads in research projects (path-scoped to `paper-*/` and `paper/`)):

- **Source slug:** `bib-validate`
- **Write reports to:** `reviews/<paper-slug>/bib-validate/<YYYY-MM-DD-HHMM>.md` inside the project (where `<paper-slug>` is the paper directory slug, e.g., `paper-jtp`, `paper-philtech`). Path is relative to the research project root, not the Task-Management repo.
- **Never** at project root (`./CRITIC-REPORT.md`-style filenames are forbidden — pre-rule layout).
- **Idempotency:** if today's file exists, append a same-day descriptor (`{date}-revision.md`, `{date}-r2.md`, `{date}-pre-submission.md`) — never overwrite.
- **Index update:** if `reviews/INDEX.md` exists, write a one-line entry under "Latest per source" pointing at the new file. Otherwise `/review-recap` will rebuild the index next time it runs.
- **Infrastructure repos** (Task-Management, atlas-workspace, etc.): this section does not apply — the path-scoped rule won't load there.


## Modes

| Invocation | Behaviour |
|---|---|
| `/bib-validate` | Standard: cross-reference \cite{} ↔ .bib, library check, preprint staleness |
| `/bib-validate --verify-doi` | **Adds DOI resolution**: each `@article`/`@inproceedings` entry gets its DOI checked via `scholarly scholarly-verify-dois`. Bib entries with no DOI or unresolvable DOIs are flagged. Use before submission to catch fabricated/hallucinated entries. |
| `/bib-validate --fix` | Auto-fixes resolvable issues in the project `.bib`; genuinely-missing entries are staged under `.paperpile-import/` with their draft cites marked `\CiteTodo{...}` (build-blocking) for manual Paperpile import. The Paperpile CLI is read-only — it cannot write to the library, so additions are staged, not auto-inserted. |
| Combine: `--verify-doi --fix` | Verify, then fix unverified entries by re-fetching from Crossref |

## When to Use

- Before compiling a final version of a paper
- After adding new citations to check nothing was missed
- When `biber`/`bibtex` reports undefined citations
- As part of a pre-submission checklist (pair with `/proofread`)

## When NOT to Use

- **Finding new references** — use `/literature` for discovery
- **Building a bibliography from scratch** — use `/literature` with `.bib` generation
- **General proofreading** — use `/proofread` (which also flags citation format issues)

## Phase 0: Session Log (Suggested)

Bibliography validation with preprint staleness checks can be context-heavy (OpenAlex lookups, web searches for published versions). Before starting, **suggest** running `/session-log` to capture prior work as a recovery checkpoint. If the user declines, proceed without it.

## Convention

**Default bibliography file is `references.bib`** — this is the standard across all projects (per the `/latex` skill convention). However, the skill also supports:

- Any `.bib` file found in the same directory as the `.tex` files being audited
- Embedded bibliographies using `\begin{thebibliography}` / `\bibitem{key}` blocks
- Both external and embedded simultaneously (rare but possible)

## Bibliography Detection

At the start of validation, detect which bibliography method the project uses:

### 1. External `.bib` file (standard)

Look for `.bib` files in the project directory. Priority order:
1. `references.bib` (preferred — standard naming convention across all projects)
2. Any other `.bib` file in the same directory as the `.tex` files

If **multiple `.bib` files** are found, validate all of them and produce a combined report. Note which file each issue belongs to. If a legacy-named `.bib` file (e.g., `paperpile.bib`) exists alongside `references.bib`, flag it as a potential cleanup opportunity (the project may have migrated from Paperpile).

Full validation applies: cross-reference checks **and** quality checks.

### 2. Embedded `\begin{thebibliography}` / `\bibitem{key}`

Some LaTeX documents define references inline rather than using an external `.bib` file. Detect by scanning `.tex` files for `\begin{thebibliography}`.

Extract keys from `\bibitem` entries:
- `\bibitem{key}` — standard form, key is the argument in braces
- `\bibitem[label]{key}` — optional label form (e.g., `\bibitem[Smith et al., 2020]{smith2020}`), key is in the **second** set of braces

Only **cross-reference checks** apply (missing keys, unused keys, typos). Quality checks (required fields, year, author formatting) are **skipped** because embedded bibliographies don't have structured metadata.

### 3. Both (rare)

If a project has both a `.bib` file and `\begin{thebibliography}` blocks, validate both:
- Run full validation on the `.bib` file
- Run cross-reference checks on `\bibitem` entries
- Merge both key sets when checking for missing citations

## Workflow

1. **Find files**: Locate all `.tex` files in the project
2. **Detect bibliography type**: Check for `.bib` files and/or `\begin{thebibliography}` blocks
3. **Extract citation keys from .tex**: Scan for all citation commands
4. **Extract entry keys from bibliography source(s)**:
   - External: Parse all `@type{key,` entries from `.bib` file(s)
   - Embedded: Parse all `\bibitem{key}` and `\bibitem[label]{key}` entries
5. **Cross-reference**: Compare the two sets
6. **Quality checks**: Validate `.bib` entry completeness (external only)
7. **Produce report**: Write results to stdout (or save if requested)

## Citation Commands to Scan

Scan `.tex` files for all of these patterns:

| Command | Example |
|---------|---------|
| `\cite{key}` | Basic citation |
| `\citet{key}` | Textual: Author (Year) |
| `\citep{key}` | Parenthetical: (Author, Year) |
| `\textcite{key}` | biblatex textual |
| `\autocite{key}` | biblatex auto |
| `\parencite{key}` | biblatex parenthetical |
| `\citeauthor{key}` | Author name only |
| `\citeyear{key}` | Year only |
| `\nocite{key}` | Include in bibliography without in-text citation |

Also handle **multi-key citations**: `\citep{key1, key2, key3}`

## Cross-Reference Checks

### Self-citation handling (double-blind submissions only)

When `--double-blind` is set OR when a `paper-*` directory's vault submission frontmatter shows the venue is double-blind, run a self-citation scan. **Default expectation: the author CAN and SHOULD cite their own prior work — keep the real bib entry and cite it in the third person.** Anonymity comes from removing the author block, not from blinding the bibliography; a `{Anonymous}` entry actually *advertises* the self-citation. See `rules/double-blind-self-citation.md` and `_shared/double-blind-anonymity-checklist.md` §P4–P5.

1. **Load submission author list.** Read `~/vault/submissions/<paper-slug>-<venue>-<year>.md` `authors:` / `coauthors:` field. If absent, prompt: `Submission author surnames (comma-separated):`.
2. **Identify self-citations.** For each `.bib` entry, parse `author = {...}`, tokenize by `and`, extract surnames; mark entries whose authors overlap the submission's as *self-citations* — these are expected, not violations.
3. **Scan the `.tex` body near each self-cite `\cite{<key>}` (±200 chars) for FIRST-PERSON voice** — "our"/"we previously"/"in earlier work of ours". That first-person voice is the actual de-anonymizer, not the names.
4. **Severity:**
   - **Info / no action** — self-citation cited in the third person with the real entry kept. This is the correct finished state. Naming the authors ("[Author] and [Collaborator] [2] show X") in the third person is fine.
   - **Critical** — first-person voice near a self-cite → rewrite to third person (the citation and the real entry stay).
   - **Critical (CFP-conditional)** — *only* if the venue's CFP explicitly requires anonymizing self-citations (some security venues, e.g. CCS) → then also blind the entry. Do **not** blind by default.
5. **Output format (first-person-voice case):**
   ```
   ⚠ FIRST-PERSON SELF-REFERENCE (Critical)
     intro.tex:88  near \cite{smith2026paradox}
       "in our prior work [12] we showed..."
       fix: third person — "Prior work [12] showed..."  (citation + real entry stay)
   ```
   For the CFP-mandated-blinding exception only, additionally anonymize the entry:
   `author = {Anonymized for double-blind review}`, `title = {Title withheld}`, `note = {Anonymized self-citation}`.

This is a **venue-conditional** check, not an unconditional desk-reject gate. Run it with the standard cross-reference checks.

### Critical: Missing Entries

Citation keys used in `.tex` but not defined in the bibliography source (`.bib` file or `\bibitem` entries).

These will cause compilation errors.

### Warning: Unused Entries

Keys defined in the bibliography source but never cited in any `.tex` file.

Not errors, but may indicate:
- Forgotten citations (should they be `\nocite`?)
- Leftover entries from earlier drafts
- Entries intended for a different paper

### Warning: Possible Typos (Fuzzy Match)

For each missing key, check if a similar key exists in the bibliography using edit distance:
- Edit distance = 1: Very likely a typo
- Edit distance = 2: Possibly a typo
- Flag these with the suggested correction

Common typo patterns:
- Year off by one: `smith2020` vs `smith2021`
- Missing/extra letter: `santanna` vs `sant'anna` vs `santana`
- Underscore vs camelCase: `smith_jones` vs `smithjones`

## Reference Manager Cross-Reference

After the disk-based cross-reference, check every `.bib` key against the Paperpile library with ONE dry-run of the canonical resolver:

```bash
python3 "$(cat ~/.config/task-mgmt/path)/scripts/bib/rekey_to_canonical.py" <project.bib>
```

Produces the full status table (HEALTHY / DRIFT / SUGGESTED / AMBIGUOUS / NOT_FOUND) in ~5s with no per-key CLI calls. Fallback lookups, status semantics, and staleness caveat: [`references/ref-manager-crossref.md`](references/ref-manager-crossref.md)

## Quality Checks on .bib Entries

**These checks apply only to external `.bib` files.** Embedded bibliographies lack structured metadata, so quality checks are skipped for them.

### Required Fields by Entry Type

| Entry Type | Required Fields |
|-----------|----------------|
| `@article` | author, title, journal, year |
| `@book` | author/editor, title, publisher, year |
| `@incollection` | author, title, booktitle, publisher, year |
| `@inproceedings` | author, title, booktitle, year |
| `@techreport` | author, title, institution, year |
| `@unpublished` | author, title, note, year |
| `@phdthesis` | author, title, school, year |

### Year Reasonableness

- Flag entries with year < 1900 or year > current year + 1
- Flag entries with no year at all

### Author Formatting

- Check for inconsistent author formats within the file
- **Flag entries where author field contains "and others" or "et al."** — this is never valid in BibTeX. All authors must be listed explicitly. Severity: **Warning**.
- Flag entries with organisation names that might need `{{braces}}` to prevent splitting

### DOI Verification & Fabrication Detection

See [`references/doi-verification.md`](references/doi-verification.md) for hard rules, resolution protocol, and LLM-hallucination detection.

### Preprint Staleness Check

**For every entry that looks like a preprint**, check whether a peer-reviewed version has since been published. Full detection signals, lookup protocol, and classification: [`references/preprint-check.md`](references/preprint-check.md)

## Severity Levels

| Level | Meaning |
|-------|---------|
| **Critical** | Missing entry for a cited key — will cause compilation error |
| **Warning** | Unused entry, possible typo, missing required field |
| **Info** | Year oddity, formatting suggestion, bibliography type note |

## Bibliography Output

After validation, offer these actions if applicable:

- **Embedded bibliography → offer to create `references.bib`**: If the project uses `\begin{thebibliography}`, offer to extract the references into a proper `references.bib` file (one `@misc` entry per `\bibitem`, with the full text as a `note` field). The author can then enrich the entries with proper metadata.
- **Non-standard `.bib` name → offer to rename**: If the existing `.bib` file is not named `references.bib`, offer to rename it to `references.bib` and update the `\bibliography{}` command in the `.tex` file.

These are **offers only** — do not make changes without explicit confirmation.

## Report Format

Full report template with all sections: [`references/report-template.md`](references/report-template.md)

Sections: Summary table → Critical (missing entries) → Warning (typos, unused, missing fields, DOI mismatches, stale preprints) → Info (year issues) → Limitations (for embedded bibliographies).

## Optional: Metadata Verification

See [`references/metadata-verification.md`](references/metadata-verification.md) for Paperpile and scholarly CLI lookup workflows.

## Deep Verification Mode (Parallel, Disk-Based)

See [`references/deep-verify-protocol.md`](references/deep-verify-protocol.md) for auto-trigger thresholds (≥40 entries) and sub-agent architecture.

## Council Mode (Optional)

For high-stakes submissions. Trigger: "council bib-validate", "thorough bib check". Full details: [`references/council-mode.md`](references/council-mode.md)

## Fix Mode

After producing the validation report, automatically fix resolvable issues. **DRIFT (paper in library under a different key) → the verified rekey chain:** `rekey_to_canonical.py --apply` (remaps `\cite` keys in `.tex`; `--extra-map` for confirmed SUGGESTED/AMBIGUOUS cases) → `rebuild_paperpile_bib.py <bib>` (regenerates the `.bib` from canonical Paperpile exports) → `citation_lint.py` → `latexmk` compile check. NOT_FOUND → search, then stage the entry as a `.bib` under `.paperpile-import/` and replace its draft cite with `\CiteTodo{slug}{title; authors; year; DOI}` (build-blocking until imported); metadata → correct BibTeX. Library additions are *staged* under `.paperpile-import/` for manual import — the Paperpile CLI is read-only (no import command; `paperpile write-bib --citekeys` only exports entries already in the library).

Full auto-fix actions, post-fix maintenance, and skip conditions: [`references/fix-mode.md`](references/fix-mode.md)

## Quality Scoring

When producing a full validation report, apply numeric quality scoring using the shared framework:

- **Framework:** [`../shared/quality-scoring.md`](../shared/quality-scoring.md) — severity tiers, thresholds, verdict rules

Map validation findings to the framework tiers:
- **Critical** (-15 to -25): Missing entry for a cited key (compilation error)
- **Major** (-5 to -14): DOI mismatch, **likely fabricated reference** (LLM-drafted hallucination), stale preprint with published version available, "et al." in author field
- **Minor** (-1 to -4): Missing optional fields, year oddities, unused entries

Compute the score and include the Score Block in the report after the summary table.

## Log to REVIEW-STATE.md (final step)

Write the bib-validate report to `reviews/<paper-slug>/bib-validate/<YYYY-MM-DD-HHMM>.md` (where `<paper-slug>` is the paper directory slug, e.g., `paper-jtp`, `paper-philtech`; create `mkdir -p reviews/<paper-slug>/bib-validate/` first). Then append a row to the project's `REVIEW-STATE.md`:

```bash
bash ~/.claude/skills/_shared/review-state-log.sh \
  --check bib-validate \
  --paper "<paper-{venue} dir>" \
  --verdict "<PASS|ISSUES FOUND>" \
  --score "<numeric score from quality-scoring framework, or —>" \
  --open-issues "<missing-plus-unused-plus-typo-count>/<missing-plus-unused-plus-typo-count>" \
  --report "reviews/<paper-slug>/bib-validate/<YYYY-MM-DD-HHMM>.md" \
  --notes "<one-line: e.g. '2 missing keys, 5 unused; 1 likely fabricated'>" \
  [--trigger "pre-submission-report|review-cluster"]
```

- Verdict: PASS if no missing/unused/typo'd citations; ISSUES FOUND otherwise.
- Score: the numeric quality score if computed; `—` otherwise.
- Open issues: total of (missing + unused + typo'd) at run time.
- Trigger: pass orchestrator name only if invoked via `/pre-submission-report` or `/review-cluster`. Otherwise omit.

Schema: `~/Task-Management/docs/reference/review-state-schema.md`.

## Cross-References

- **`/proofread`** — For overall paper quality including citation format
- **`/literature`** — For finding and adding new references (includes full OpenAlex workflows)
- **`/bib-coverage`** — Compare project `.bib` vs Paperpile label — find uncited papers and unfiled references
- **`/latex`** — For compilation with reference checking
- **`/latex`** — For compilation and error resolution. Run after fixing bibliography issues to verify citations compile cleanly.
- **`shared/reference-resolution.md`** — Canonical lookup + filing sequence used by Ref Manager Cross-Reference and Fix Mode
