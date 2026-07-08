---
name: retarget-journal
description: "Use when you need to retarget a paper to a different journal (rename, swap bib, update citations)."
allowed-tools: Bash(latexmk*), Bash(pdflatex*), Bash(xelatex*), Bash(mkdir*), Bash(ls*), Bash(cp*), Bash(mv*), Bash(git*), Read, Write, Edit, Glob, Grep, Task
argument-hint: [target-journal-name]
---

# Retarget Journal Skill

> Switch a paper manuscript from one journal to another. Handles folder renaming, bibliography swaps, citation key updates, formatting changes, and compilation verification.

## When to Use

- Switching a paper's target venue (e.g., Journal A to Journal B, Journal C to Journal D)
- After a rejection when resubmitting to a different journal
- When strategic decisions change the target venue mid-drafting

## Before Starting

Ask the user for:

1. **Current project path** — where is the paper?
2. **Target journal** — full name and abbreviation
3. **What changes?** — some retargets are minor (formatting), others are major (restructuring)

Read the project's `CLAUDE.md` and `README.md` to understand current state.

---

## Workflow

### Phase 1: Assess Scope

Read the current manuscript and compare against the target journal's requirements:

| Check | What to compare |
|-------|----------------|
| **Word/page limit** | Does the draft fit? Need to cut or can expand? |
| **Required sections** | Does the target need sections the current draft lacks? (e.g., "Relevance Statement", "AI Disclosure") |
| **Citation style** | Author-year vs numbered? natbib vs biblatex? |
| **Formatting** | Template class? Column layout? Font requirements? |
| **Supplementary material** | Online appendix conventions? |

Present the assessment to the user before proceeding.

### Phase 2: Rename and Restructure

1. **Rename project folder** if it references the old journal:
   ```bash
   mv "old-journal-name/" "new-journal-name/"
   ```

2. **Update Overleaf symlink** if one exists:
   ```bash
   # Remove old symlink
   rm paper/
   # Create new symlink to the correct Overleaf directory
   ln -s "/path/to/Overleaf/new-project" paper
   ```

3. **Update folder references** in `CLAUDE.md`, `README.md`, `.gitignore`

### Phase 3: Bibliography

1. **Swap `.bib` file** if the user provides a new export from Paperpile
2. **Update citation keys** across all `.tex` files:
   - Read the new `.bib` to get the new key format
   - Find all `\cite{...}`, `\citet{...}`, `\citep{...}`, `\citeauthor{...}` commands in `.tex` files
   - Map old keys to new keys (match by author + year)
   - Replace all occurrences
3. **Validate** — run `/bib-validate` to ensure no missing or unused keys

### Phase 4: Formatting

1. **Switch document class/template** if needed
2. **Add required sections** (e.g., data availability, AI disclosure, conflict of interest)
3. **Adjust page layout** (margins, columns, font size)
4. **Update `\bibliographystyle{}`** if citation style changes
5. **Update abstract** — check word limit for target journal

### Phase 5: Update Documentation

1. **Project `CLAUDE.md`** — update target journal, formatting notes
2. **Project `README.md`** — update journal reference, submission info
3. **`MEMORY.md`** — carry forward any learnings, update journal-specific notes
4. **vault research pipeline** — update the Target Journal and Status fields. If the retarget closes a live venue event (rejection or withdrawal), append the closing `history:` row (`event: decision, outcome: reject` or `event: withdrawn`) to the OLD venue's submission entry per `rules/submission-file-archive.md` § history — the new target's entry gets its own `history:` when it is actually submitted, not at retarget time
5. **atlas topic `outputs[]`** — update the retargeted output's `venue` (slug must resolve to a `~/vault/venues/` file). **Refresh or clear `cycle`**: if the new venue is a Conference/Workshop and the output is submission-active, set `cycle: <NewVenue> <edition-year>`; if the new venue is a journal, **remove** any stale `cycle` — per `rules/atlas-status-vocabulary.md` § submission-join completeness. A stale cycle from the old venue must never survive a retarget. If the retarget also changed the paper's title, update `paper_title` here **and** the registry `canonical_title` together (keep them aligned per `paper-vault-alignment.md`).

### Phase 6: Compile and Verify

1. Compile to `out/` with `latexmk`
2. Fix all warnings (overfull/underfull)
3. Check page count against target journal limit
4. Verify all citations resolve
5. Visual check: does the formatting look right for the target venue?

### Phase 7: Confirm

Report a summary:

```
Retargeted [Paper Name]: [Old Journal] → [New Journal]

Changes made:
- Folder: [old path] → [new path]
- Symlink: updated to [new Overleaf project]
- Bibliography: [N] citation keys updated
- Sections added: [list]
- Sections removed: [list]
- Page count: [N] pages (limit: [M])
- Compilation: clean (0 warnings)

Updated: CLAUDE.md, README.md, vault
```

---

## Important Rules

- **Never delete the old `.bib` file** — rename it to `old-journal.bib.bak` as a safety copy
- **Verify citation key mappings** with the user before bulk-replacing — automated matching can misfire on common surnames
- **Don't restructure content** without approval — some retargets only need formatting changes, not rewriting
- **Preserve git history** — commit the retarget as a single, well-documented commit

---

## Venue Style Guides

When retargeting, the writing style often needs to change too — not just the formatting. Read the appropriate guide from the shared venue-guides resource:

- **Master overview:** [`skills/shared/venue-guides/venue_writing_styles.md`](../shared/venue-guides/venue_writing_styles.md) — style spectrum and adaptation tips
- **Formatting requirements:** [`skills/shared/venue-guides/journals_formatting.md`](../shared/venue-guides/journals_formatting.md) (journals) / [`conferences_formatting.md`](../shared/venue-guides/conferences_formatting.md) (conferences)
- **Venue-specific style:** `nature_science_style.md`, `ml_conference_style.md`, `cs_conference_style.md`, `cell_press_style.md`, `medical_journal_styles.md` — all in `skills/shared/venue-guides/`
- **Writing examples:** `skills/shared/venue-guides/examples/` — abstract and introduction formats by venue type

## Cross-References

| Skill | When to use alongside |
|-------|----------------------|
| `/bib-validate` | After Phase 3 to verify all citation keys |
| `/latex` | **Default compiler** — use for compilation with auto error resolution |
| `/latex` | For manual compilation config and `.latexmkrc` setup |
| `/proofread` | After retarget to check for remnants of old journal formatting |
| `vault sync (edit vault files directly)` | After Phase 5 to sync with central context library |
