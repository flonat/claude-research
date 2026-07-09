# Anonymization Patterns Reference

> Detailed replacement tables for `/replication-package` Blind mode (Phases 9-10). The SKILL.md provides the protocol; this file has the pattern tables.

## LaTeX Author Blocks (Phase 9a)

| Pattern | Replacement |
|---------|-------------|
| `\author{...}` (single author) | `\author{Anonymous}` |
| `\author[...]{...}` (with options) | `\author{Anonymous}` |
| Multiple `\author{}` blocks | Single `\author{Anonymous}` |
| `\affiliation{...}` | `\affiliation{Anonymous Institution}` |
| `\institute{...}` | `\institute{Anonymous Institution}` |
| `\email{...}` | Remove entirely |
| `\orcid{...}` | Remove entirely |
| `\authorrunning{...}` | `\authorrunning{Anonymous}` |
| `\titlerunning{...}` | Keep (title is not identifying) |

For multi-author documents, ask the user how many anonymous authors to list (e.g., "Anonymous Author 1", "Anonymous Author 2", etc.).

## Thanks and Acknowledgments (Phase 9b)

| Pattern | Replacement |
|---------|-------------|
| `\thanks{...}` | Remove entirely (often contains grant info) |
| `\begin{acknowledgments}...\end{acknowledgments}` | Replace body with `[Redacted for blind review.]` |
| `\begin{acknowledgements}...\end{acknowledgements}` | Replace body with `[Redacted for blind review.]` |
| `\section*{Acknowledgments}` (followed by text) | Replace section body with `[Redacted for blind review.]` |
| `\paragraph{Acknowledgments}` variant | Same treatment |

## Self-Citations (Phase 9c)

**This is interactive — never auto-modify citations.**

1. Extract all citation keys from `.tex` files
2. Read the `.bib` file(s)
3. Flag potential self-citations: entries where any author last name matches an identity item
4. Present each flagged citation:

```
Potential self-citation found:
  \citet{author2025example} — "Multi-criteria decision making with AI"
  Authors: [Author], F. and Smith, J.

  Options:
  1. Anonymize → replace with "[Anonymous, 2025]" and comment out bib entry
  2. Keep as-is (not actually a self-citation or acceptable in this venue)
  3. Remove citation entirely
```

5. Apply the user's choice for each flagged citation.

**Note:** Common surnames may cause false positives. This is expected — better to flag too many than miss one.

## Other Files (Phase 10)

### README and Documentation (10a)
- Replace author names, emails, institutions in `README.md`, `README`, `README.txt`
- Replace with "Anonymous" / "anonymous@example.com" / "Anonymous Institution"
- If a README section is titled "Author", "Contact", etc. → replace body with `[Anonymized for blind review.]`

### Code File Headers (10b)
Search `.py`, `.R`, `.r`, `.sh`, `.m`, `.jl`, `.js`, `.ts` for identity patterns:

```
# Author: the user          →  # Author: Anonymous
# Email: author@university.edu   →  (remove)
# (c) 2025 the user         →  # (c) 2025 Anonymous
```

### Package Metadata (10c)
- `pyproject.toml` / `setup.py`: replace `authors`, `maintainers`, `author_email` fields
- `DESCRIPTION` (R): replace `Author`, `Maintainer` fields
- `package.json`: replace `author`, `contributors` fields

### Personal Paths (10d)
Search all text files for paths that could identify the user:
```
/Users/<username>/     →  /path/to/project/
/home/<username>/      →  /path/to/project/
C:\Users\<username>\   →  /path/to/project/
```

### Global Identity Replacement (10e)
Final sweep — case-insensitive search-and-replace across all text files:

| Identity item | Replacement |
|--------------|-------------|
| Full name | "Anonymous" |
| First name (standalone word) | "Anonymous" |
| Last name (standalone word) | "Anonymous" |
| Email addresses | "anonymous@example.com" |
| Institution names | "Anonymous Institution" |
| ORCID | Remove |

**Be careful with common words.** If a name is also a common English word (e.g., "Reading" as in University of Reading), only replace in identity contexts. When in doubt, flag for user review.
