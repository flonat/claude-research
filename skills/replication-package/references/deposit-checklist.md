# Deposit Checklist for Replication Packages

> Completeness checklist for depositing replication packages on various platforms. Used by `/replication-package` Audit mode (Check 6) and as a pre-deposit reference in Assemble mode.

---

## Universal Requirements

These apply regardless of platform:

| # | Item | Details |
|---|------|---------|
| 1 | **README** | AEA-style or equivalent. Must contain: data sources, software requirements, script descriptions, replication instructions. |
| 2 | **License** | Include a `LICENSE` file. Default: CC-BY 4.0 for data/docs, MIT/BSD for code. Dual licensing is fine. |
| 3 | **Dependency manifest** | `requirements.txt`, `pyproject.toml`, `renv.lock`, `DESCRIPTION`, or equivalent. Version-pinned. |
| 4 | **No secrets** | No API keys, passwords, `.env` files, personal tokens, or credentials. |
| 5 | **No AI traces** | No `.claude/`, `CLAUDE.md`, `MEMORY.md`, Co-Authored-By AI trailers, Claude attribution markers. |
| 6 | **Reasonable file sizes** | No single file > 100 MB without justification. Total package < 5 GB (platform limits vary). |
| 7 | **No compiled outputs in source** | LaTeX build artifacts (`out/`, `.aux`, `.log`) should not be in the package unless they are the final PDF. |
| 8 | **Consistent file references** | All paths in scripts match actual file locations. No broken references. |
| 9 | **Self-contained** | Package works without access to external servers, APIs, or authenticated services (or documents these dependencies explicitly). |
| 10 | **Version pinning** | Software versions documented. Package versions pinned. Results should reproduce with stated versions. |

---

## Platform-Specific Requirements

### Zenodo

| Item | Requirement |
|------|-------------|
| **File format** | Single `.zip` or `.tar.gz` archive |
| **Size limit** | 50 GB per file, 50 GB total per record |
| **Metadata** | Title, authors, description, keywords, license, publication date |
| **DOI** | Automatically assigned on publish. Reserve a DOI before submission if you need to cite it in the paper. |
| **Versioning** | New versions create new DOIs linked to a concept DOI. Use concept DOI in the paper for always-latest. |
| **Communities** | Add to relevant communities (e.g., your institution, field) |
| **Access** | Public, embargoed, or restricted. Embargoed allows setting a release date. |
| **Linking** | Link to GitHub repo, paper DOI, or grant if available |
| **Sandbox** | Test at sandbox.zenodo.org before depositing to production |

### Dataverse (Harvard, institutional)

| Item | Requirement |
|------|-------------|
| **File format** | Individual files uploaded (not zipped), or a single archive |
| **Size limit** | Varies by installation (Harvard: 2.5 GB per file, 10 GB per dataset) |
| **Metadata** | Citation metadata block required. Geospatial, social science blocks optional. |
| **DOI** | Assigned on publish |
| **Tabular data** | `.csv`, `.tsv`, `.dta` files are auto-ingested with variable-level metadata. Prefer these over proprietary formats. |
| **Terms of Use** | Must select or create terms of use. CC0 is standard for data. |
| **Restricted files** | Individual files can be restricted while others remain open |
| **File tags** | Tag files by category (documentation, data, code) |

### ICPSR

| Item | Requirement |
|------|-------------|
| **File format** | Standard formats preferred (`.csv`, `.dta`, `.sav`, `.Rdata`) |
| **Size limit** | Contact ICPSR for large deposits (> 2 GB) |
| **Metadata** | Extensive: PI info, funding, geographic coverage, time period, methodology |
| **Codebook** | Required for survey/experimental data. Must document all variables. |
| **Confidentiality** | ICPSR reviews for disclosure risk. PII must be removed before deposit. |
| **Access levels** | Public-use, restricted-use (requires DUA), or enclave (virtual data environment) |
| **Citation** | ICPSR provides standard citation format |
| **Curation** | ICPSR curators review and may request changes before publication |

### Journal Supplementary Materials

| Item | Requirement |
|------|-------------|
| **File format** | Usually `.zip`. Check journal guidelines for accepted formats. |
| **Size limit** | Varies widely (often 10-50 MB for supplementary, more for data deposits). Large data should go to a repository. |
| **Naming** | Follow journal's naming convention (e.g., `SupplementaryMaterials.zip`) |
| **README** | Usually required inside the archive |
| **Anonymization** | If double-blind, author names must not appear anywhere in the package |
| **Cross-referencing** | Paper must cite the data deposit. Data deposit should reference the paper. |
| **Embargo** | Some journals embargo supplementary materials until publication |
| **Separate deposit** | Many journals prefer data in an external repository (Zenodo, Dataverse) with a DOI, not as supplementary files |

---

## Pre-Deposit Verification

Run these checks before uploading:

```
Pre-Deposit Checklist
======================
[ ] README is complete and follows AEA structure
[ ] LICENSE file is present
[ ] Dependency manifest is present and version-pinned
[ ] No secrets or credentials in any file
[ ] No AI traces (run Audit mode Check 9)
[ ] No identity leaks if double-blind (run Audit mode Check 10)
[ ] File sizes are within platform limits
[ ] Archive extracts correctly (test: unzip to temp dir)
[ ] Scripts reference correct relative paths (no absolute paths)
[ ] Data files are documented with provenance
[ ] All tables/figures map to scripts in README
[ ] Package compiles/runs on a clean environment (or documented exceptions)
[ ] Metadata prepared for the deposit platform
[ ] DOI reserved if needed for paper citation
```

---

## Archiving Formats

| Format | When to use |
|--------|------------|
| `.zip` | Default. Universally supported. |
| `.tar.gz` | Unix-oriented platforms, large packages. Preserves permissions better. |
| `.7z` | Better compression, but less universally supported. Avoid unless platform requires it. |

### Creating the archive

```bash
# ZIP (most common)
cd "<parent-dir>"
zip -r "<project-name>-replication.zip" "<project-name>-replication/" -x "*.DS_Store"

# TAR.GZ
cd "<parent-dir>"
tar --exclude='.DS_Store' -czf "<project-name>-replication.tar.gz" "<project-name>-replication/"
```

---

## Version Control for Deposits

- **Before submission:** Reserve a DOI (Zenodo) or note that the deposit is draft.
- **After acceptance:** Publish the deposit and update the paper with the final DOI.
- **After publication:** If corrections are needed, create a new version (new DOI) linked to the original.
- **Concept DOI:** Use the concept DOI in the paper if the platform supports it — it always resolves to the latest version.
