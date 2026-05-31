---
name: docx
description: "Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing images in documents, performing find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a 'report', 'memo', 'letter', 'template', or similar deliverable as a Word or .docx file, use this skill. Do NOT use for PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document generation."
license: Proprietary. LICENSE.txt has complete terms
allowed-tools: Bash(uv*, pandoc*, node*, npx*, mkdir*, ls*), Read, Write, Edit
---

# DOCX creation, editing, and analysis

## Overview

A .docx file is a ZIP archive containing XML files.

## Quick Reference

| Task | Approach |
|------|----------|
| Read/analyze content | `pandoc` or unpack for raw XML |
| Create new document | Use `docx-js` — see [`references/docx-js-patterns.md`](references/docx-js-patterns.md) |
| Edit existing document | Unpack → edit XML → repack — see Editing below |

### Converting .doc to .docx

```bash
python scripts/office/soffice.py --headless --convert-to docx document.doc
```

### Reading Content

```bash
# Text extraction with tracked changes
pandoc --track-changes=all document.docx -o output.md

# Raw XML access
python scripts/office/unpack.py document.docx unpacked/
```

### Converting to Images

```bash
python scripts/office/soffice.py --headless --convert-to pdf document.docx
pdftoppm -jpeg -r 150 document.pdf page
```

### Accepting Tracked Changes

```bash
python scripts/accept_changes.py input.docx output.docx
```

---

## Creating New Documents

Generate .docx files with JavaScript using `docx-js`. Install: `npm install -g docx`

Full code patterns (setup, page size, styles, lists, tables, images, hyperlinks, footnotes, tab stops, multi-column layouts, TOC, headers/footers): [`references/docx-js-patterns.md`](references/docx-js-patterns.md)

### Critical Rules for docx-js

- **Set page size explicitly** — defaults to A4; use US Letter (12240 x 15840 DXA) for US documents
- **Landscape: pass portrait dimensions** — docx-js swaps width/height internally
- **Never use `\n`** — use separate Paragraph elements
- **Never use unicode bullets** — use `LevelFormat.BULLET` with numbering config
- **PageBreak must be in Paragraph** — standalone creates invalid XML
- **ImageRun requires `type`** — always specify png/jpg/etc
- **Always set table `width` with DXA** — never use `WidthType.PERCENTAGE` (breaks in Google Docs)
- **Tables need dual widths** — `columnWidths` array AND cell `width`, both must match
- **Use `ShadingType.CLEAR`** — never SO[Project] for table shading
- **Never use tables as dividers** — use border on Paragraph instead; for two-column footers, use tab stops
- **TOC requires HeadingLevel only** — no custom styles on heading paragraphs
- **Override built-in styles** — use exact IDs: "Heading1", "Heading2", etc.
- **Include `outlineLevel`** — required for TOC (0 for H1, 1 for H2, etc.)

### Validation

```bash
python scripts/office/validate.py doc.docx
```

---

## Editing Existing Documents

**Follow all 3 steps in order.**

### Step 1: Unpack
```bash
python scripts/office/unpack.py document.docx unpacked/
```
Extracts XML, pretty-prints, merges adjacent runs, and converts smart quotes to XML entities. Use `--merge-runs false` to skip run merging.

### Step 2: Edit XML

Edit files in `unpacked/word/`. **Use "Claude" as the author** for tracked changes and comments.

**Use the Edit tool directly for string replacement. Do not write Python scripts.**

**Use smart quotes for new content:**
| Entity | Character |
|--------|-----------|
| `&#x2018;` | ' (left single) |
| `&#x2019;` | ' (right single / apostrophe) |
| `&#x201C;` | " (left double) |
| `&#x201D;` | " (right double) |

**Adding comments:**
```bash
python scripts/comment.py unpacked/ 0 "Comment text with &amp; and &#x2019;"
python scripts/comment.py unpacked/ 1 "Reply text" --parent 0
```
Then add markers to document.xml.

Full XML patterns (tracked changes, comments, images): [`references/xml-reference.md`](references/xml-reference.md)

### Step 3: Pack
```bash
python scripts/office/pack.py unpacked/ output.docx --original document.docx
```
Validates with auto-repair, condenses XML, and creates DOCX. Use `--validate false` to skip.

### Common Pitfalls

- **Replace entire `<w:r>` elements**: When adding tracked changes, replace the whole `<w:r>...</w:r>` block with `<w:del>...<w:ins>...` as siblings.
- **Preserve `<w:rPr>` formatting**: Copy the original run's `<w:rPr>` block into your tracked change runs.

---

## Dependencies

- **pandoc**: Text extraction
- **docx**: `npm install -g docx` (new documents)
- **LibreOffice**: PDF conversion (auto-configured via `scripts/office/soffice.py`)
- **Poppler**: `pdftoppm` for images
