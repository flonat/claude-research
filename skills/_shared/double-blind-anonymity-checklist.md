# Double-Blind Anonymity Checklist

> **Authoritative checklist** for any double-blind submission. Skills that touch artifacts, papers, or bib files must run these checks before reporting success. Distilled from a real CCS 2026 administrative-reject incident (paper #1328, 2026-05-06) where two independent breaks slipped through: a self-citation in the bib + an `authors = ["the user"]` line in the artifact's `pyproject.toml`.

## The two CCS-class venues care about

1. **The PDF** — title page, body text, references, footnotes, acknowledgements, figure metadata.
2. **The artifact** — every file in the anonymous repo, including structured-metadata files reviewers rarely think to check (`pyproject.toml`, `package.json`, `Cargo.toml`, `CITATION.cff`, `setup.py`, `.gemspec`, `pom.xml`, `Project.toml`).

Skills that handle one MUST NOT assume the other has been checked. Both layers need their own gate.

---

## Hard checks — refuse to mark success unless ALL pass

### Paper-side (PDF / `.tex` / `.bib`)

| # | Check | How to verify | Failure example |
|---|-------|---------------|-----------------|
| P1 | Title page has no author names | `grep -E "Anonymous Author" main.tex`, no `\author{}` macro with real names | `\author{the user}` |
| P2 | No `\thanks{}`, `\acknowledgements`, `\funded by`, `\grant{}` revealing identity | `grep -E "(thanks|acknowledg|funded|grant)" *.tex` | `\acknowledgements{Funded by EPSRC EP/...}` |
| P3 | First-person self-reference uses third person | `grep -nE "\b(we|our) (previous|prior|earlier) (work|paper|study)" *.tex` | "In our prior work [3]..." |
| P4 | **Self-citations cited in the third person; real bib entry kept** | Anonymity comes from removing the author block (P1) + third-person voice (P3/P5), NOT from blinding the bibliography. Keep the real `author=` field — a `{Anonymous}` entry *advertises* the self-citation and hints at authorship. **Exception:** blind the entry only if the venue's CFP *explicitly* requires anonymizing self-citations (some security venues — see 2026-05-06 incident). | de-anonymizing form is first-person near the cite ("in *our* prior work [2]"), NOT the names in the entry |
| P5 | **Self-references use third-person voice** | Flag first-person self-reference near a self-cite ("our"/"we previously"/"in earlier work of ours"). Naming yourself in the third person ("[Author] and [Collaborator] [2] show X") is **correct**, not a violation — it's the first-person *voice*, not the names, that de-anonymizes. | "In *our* earlier work [2] we showed..." |
| P6 | No identifying URLs (personal websites, lab pages, repo URLs with handles) | `grep -nE "(github\.com/[a-z0-9-]+|sites\.google|\.cs\.[a-z]+\.edu)" *.tex` | `\url{https://example.invalid/anonymous/repo}` |
| P7 | PDF metadata sanitized | `pdfinfo paper.pdf` — `Author`, `Subject` (only ACM CCS classification OK), `Keywords` should not contain identifiers | `Author: the user` in pdfinfo |
| P8 | Figures contain no identifying watermarks/captions | Manual review of any rendered figures with text | A screenshot with a username in the corner |

The blinded-bib-entry pattern — use **only** when a venue's CFP explicitly requires anonymizing self-citations; otherwise keep the real entry and rely on third-person voice + author-block removal:
```bibtex
@misc{anonymous2026paradox,
  author = {Anonymized for double-blind review},
  title  = {Title withheld; preprint anonymized},
  year   = {2026},
  note   = {Anonymized self-citation}
}
```

### Artifact-side (anonymous repo)

| # | Check | How to verify | Failure example |
|---|-------|---------------|-----------------|
| A1 | No personal identifiers in any text file | `grep -rIE "(<author-tokens>)" --include='*.{tex,md,py,R,ipynb,sh,toml,yml,yaml,json,cff,bib,rs,go,jl}'` over repo | `# Author: the user` in a `.py` |
| A2 | **Structured-metadata author fields empty or anonymized** | Per-format check, see below. **This was the CCS 2026 #1328 trigger.** | `authors = [{ name = "the user" }]` in `pyproject.toml` |
| A3 | No personal email addresses anywhere | `grep -rIE "[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"` excluding `@example`, `@anonymous`, `@invalid` | `user@example.com` in a config file |
| A4 | No identifying file system paths | `grep -rIE "(/(Users|home)/<handle>|/Volumes/(SSD|External)|Dropbox/Research)"` | `PRISM_HOME=/Volumes/<private-volume>/tools/...` |
| A5 | No personal GitHub handles | `grep -rIE "(github\.com/<handle>|<handle>\.com)"` | `github.com/user` |
| A6 | Git commit history scrubbed (or absent) | `git log --format='%an <%ae>' \| sort -u` — must show only "Anonymous" or absent | `user <user@example.com>` |
| A7 | LICENSE file holder is anonymous | `head -5 LICENSE` — `Copyright (c) <Year> Anonymous` | `Copyright (c) 2026 the user` |
| A8 | CITATION.cff (if present) has anonymous authors | `grep -A 5 "authors:" CITATION.cff` | Real names in CFF |
| A9 | Co-author names also stripped (not just submitter's) | Skill must capture full submission author list at the start, not rely on a hardcoded single name | `[Collaborator]` slips through because pattern set only had `[Author]` |

---

## Structured-metadata field check (A2) — exact targets

Reviewers / AE chairs spot-check these because they're the easiest deanonymization vector. Each format has a specific field that must be empty or contain only "Anonymous"-style values.

| Format | File | Field(s) to check | Acceptable values |
|--------|------|-------------------|-------------------|
| Python (modern) | `pyproject.toml` | `[project] authors`, `[project] maintainers` | omitted, `[]`, `[{ name = "Anonymous" }]` |
| Python (legacy) | `setup.py`, `setup.cfg` | `author=`, `author_email=`, `maintainer=` | omitted, `"Anonymous"`, `"anon@example.invalid"` |
| Node.js | `package.json` | `author`, `contributors`, `maintainers` | omitted, `""`, `"Anonymous"` |
| Rust | `Cargo.toml` | `[package] authors` | omitted, `["Anonymous"]` |
| Ruby | `*.gemspec` | `s.authors`, `s.email` | omitted, `["Anonymous"]` |
| Java/Kotlin | `pom.xml`, `build.gradle` | `<developers>`, `<contributors>` | omitted |
| Julia | `Project.toml` | `authors` | omitted, `["Anonymous"]` |
| R | `DESCRIPTION` | `Authors@R`, `Maintainer` | `person("Anonymous", ...)` |
| Citation | `CITATION.cff` | `authors:` block | `family-names: Anonymous` |
| Container | `Dockerfile` | `LABEL maintainer=` | omitted |
| OCI | `image.json`, `*.yaml` | `org.opencontainers.image.authors` | omitted |
| Go | `go.mod` (rare) | module path containing handle | use `example.com/anonymous-submission` |
| LaTeX | `acmart.cls` calls | `\author{}`, `\affiliation{}`, `\thanks{}` | use `\anonymous{}` per acmart guidance |

**Implementation hint:** rather than per-format parsers, a robust check is:

```bash
# A2 fast scan — surface any author/maintainer field with non-empty content
grep -rInE "^\s*(authors?|maintainers?)\s*[:=]\s*[^[\"\s]" \
    --include='*.toml' --include='*.json' --include='*.yaml' \
    --include='*.yml' --include='*.cff' --include='*.gemspec' \
    --include='setup.py' --include='setup.cfg' --include='DESCRIPTION' \
    .
```

Any hit must then be inspected — false positives possible (e.g. `maintainer = ""`, `authors = []`) — but a hit on a non-empty value is a hard stop.

---

## Co-author name capture

Single-author leak patterns are insufficient when the submission has co-authors whose names are not in the skill's general pattern set. Skills MUST:

1. At run start, read project-local submission metadata and extract the full author list from `authors:` or `coauthors:`.
2. If the vault entry is missing or has no author list, prompt the user via `the available structured-question mechanism`: "Full author list for this submission (comma-separated): ".
3. Construct an *augmented* pattern set: built-in patterns + each surname + each given-name + each email handle if known.
4. Run the leak grep with the augmented pattern set, not the static set.

This is the failure mode that hid `[Collaborator]` from the CCS 2026 #1328 leak grep — the static patterns only had `[Author]`/`the user`/`user`/`user`.

---

## Verification harness for skills

When a skill claims to enforce double-blind, it should print a checklist at the end with PASS/FAIL per item. A skill whose contract is "produce an anonymous artifact" must refuse to print "deployed" / "URL minted" / "ready" if any check fails. Warn-loudly is not acceptable — fail-loudly is required.

Minimum end-of-run output:

```
Double-blind anonymity gate
─────────────────────────────
  Paper-side
   P1 title-page anonymous          .... PASS
   P2 no acknowledgements/funding   .... PASS
   P3 third-person self-reference   .... PASS
   P4 self-cite third-person, entry kept .. PASS  (blind only if CFP demands)
   P5 third-person voice (names OK)  .... FAIL  intro.tex:88 ("our prior work")
   P6 no identifying URLs           .... PASS
   P7 PDF metadata clean            .... PASS
   P8 figures/screenshots clean     .... SKIP  (manual review required)
  Artifact-side
   A1 no identifiers in text        .... PASS
   A2 structured-metadata fields    .... FAIL  pyproject.toml:5
   A3 no personal emails            .... PASS
   A4 no identifying paths          .... PASS
   A5 no personal handles           .... PASS
   A6 git history scrubbed          .... PASS
   A7 LICENSE holder anonymous      .... PASS
   A8 CITATION.cff anonymous        .... N/A
   A9 co-author names stripped      .... PASS

Result: BLOCK (3 hard-fails)
```

---

## When this checklist is overkill

- Single-blind / non-blind submissions (just verify the artifact is reproducible)
- Internal supervisory drafts that are explicitly not for review
- Camera-ready versions after notification (anonymity no longer required)

For everything else — anonymous review of any kind — every check above is mandatory.

---

## Incident log

| Date | Submission | Track | Trigger | Lesson |
|------|------------|-------|---------|--------|
| 2026-05-06 | CCS 2026 #1328 (Cycle B) | SUM | (1) `references.bib` self-citation by [Author] & [Collaborator] named in plain text; (2) `pyproject.toml` `authors = [{ name = "the user" }]` in linked anonymous artifact | Structured-metadata author fields (here `pyproject.toml` `authors`) are the easiest artifact-side leak and must **always** be blinded (Layer 2.5 — a hard refusal). On the self-citation: CCS and some security venues require anonymizing self-cites, but most venues (ICSE, ML) do **not** — third-person citation with the real bib entry kept is correct there (see `rules/double-blind-self-citation.md`); blind the entry only when the CFP explicitly demands it. *[Lesson corrected 2026-06-30: the earlier "the bib entry itself must be blinded" over-generalized this CCS-specific case.]* |

Future incidents append here so the checklist evolves with experience.
