# Blind Mode Workflow

> Phases 8-12 for double-blind anonymization. Read when running Blind mode (after Assemble phases).

Blind mode runs **all phases from Assemble** (Phases 1-7), then continues with anonymization. The output path uses `-replication-blind/` instead of `-replication/`.

## Phase 8: Collect Identity Information

Automatically detect identifying information from multiple sources. Build a comprehensive identity profile.

### Sources to check:

| Source | What to extract |
|--------|----------------|
| `git config --global user.name` / `user.email` | Author name and email |
| `.context/profile.md` (if in Task Management) | Full name, affiliations, roles |
| `\author{}` blocks in `.tex` files | Names, affiliations, emails, ORCID |
| `\affiliation{}`, `\institute{}`, `\institution{}` | Institution names |
| `\thanks{}` in LaTeX | Grant numbers, funding acknowledgments |
| `README.md` | Author sections, contact info |
| `DESCRIPTION` file (R packages) | Author field |
| `pyproject.toml` / `setup.py` | Author metadata |

### Build the identity list:

```
Identity Items Detected
========================
Names:         <detected names>
Emails:        <detected emails>
Institutions:  <detected institutions>
ORCID:         <detected ORCID>
Other:         [any other identifying strings found]
```

**Present to the user and ask for confirmation.** They may want to add items (e.g., a nickname, an old email) or remove false positives.

---

## Phase 9: Anonymize LaTeX Files

Work in the output directory. For every `.tex` file:

- **9a — Author blocks**: Replace `\author{}`, `\affiliation{}`, `\email{}`, `\orcid{}` etc. with anonymous versions. For multi-author docs, ask user for count.
- **9b — Thanks/acknowledgments**: Remove `\thanks{}`, replace acknowledgment sections with `[Redacted for blind review.]`
- **9c — Self-citations** (**interactive**): Flag citations where author names match identity list. Present each to user with options: anonymize / keep / remove. Never auto-modify.

Full replacement tables and self-citation protocol: [`anonymization-patterns.md`](anonymization-patterns.md)

---

## Phase 10: Anonymize Other Files

- **10a — README/docs**: Replace names, emails, institutions. Replace "Author"/"Contact" sections with `[Anonymized for blind review.]`
- **10b — Code headers**: Search `.py`, `.R`, `.sh`, etc. for comment headers with identity items. Replace with `# Author: Anonymous`
- **10c — Package metadata**: `pyproject.toml`, `DESCRIPTION`, `package.json` author fields
- **10d — Personal paths**: Replace `/Users/<username>/` etc. with generic paths
- **10e — Global sweep**: Case-insensitive search-and-replace for every identity item. Be careful with common words (e.g., "Reading", "York") — flag ambiguous cases for user review.

Full patterns and replacement tables: [`anonymization-patterns.md`](anonymization-patterns.md)

---

## Phase 11: Fresh Anonymous Git Repository

1. **Remove the existing git repo** (created in Phase 6):
   ```bash
   rm -rf "<output-path>/.git"
   ```

2. **Initialize a fresh repo with anonymous identity:**
   ```bash
   cd "<output-path>" && git init
   git -C "<output-path>" config user.name "Anonymous"
   git -C "<output-path>" config user.email "anonymous@example.com"
   ```

3. **Commit everything:**
   ```bash
   cd "<output-path>" && git add -A && git commit -m "Initial commit"
   ```

4. **Verify anonymous commit:**
   ```bash
   cd "<output-path>" && git log --format=full
   ```
   Confirm author and committer are both "Anonymous <anonymous@example.com>".

---

## Phase 12: Report with Identity Leak Check

Present a comprehensive summary using the template from [`report-template.md`](report-template.md). This extends the Assemble report with identity anonymization stats, git identity verification, and an identity leak check.

Run the verification grep for **every identity item** plus AI traces. If any matches remain, list them with file and line number, and ask the user whether they are false positives or need manual fixing.
