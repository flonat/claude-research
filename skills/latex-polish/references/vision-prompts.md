# Vision-Inspection Prompts (Phase 5)

> Per-page-type prompts for the vision pass. The skill `Read`s a rendered page PNG and applies the matching prompt to elicit a structured finding list.

## Prompt format

Each prompt is a fixed template the skill uses verbatim. Each ends with the same output schema so findings consolidate cleanly:

> Output as a YAML block under `findings:` with one entry per issue. Each entry has `tier` (Major / Moderate / Minor), `where` (region or element), and `issue` (one sentence). End with a one-line `verdict:` of `PASS` / `NOTES` / `REVISE`.

## Title-page prompt

```
This is page 1 of a LaTeX document — the title page. Identify visual issues:

- Line-spacing inconsistency between consecutive lines of the same logical block (title, subtitle, author block). Are inter-line gaps even within each block?
- Weight hierarchy: is the title visibly heavier than the subtitle? Is the author block clearly subordinate?
- Vertical block separation: are the gaps between blocks (title → subtitle → author → footer) consistent or arbitrary?
- Horizontal alignment: is everything centred OR everything left-aligned consistently — not a mix?
- Font-size jumps that look unintended (e.g., one line at a different size from its neighbours)
- Awkward line breaks in the title or subtitle (mid-phrase, single-word last line)
- Empty space distribution: is the title page balanced, or top-heavy / bottom-heavy by accident?

Ignore: choice of font, choice of colour palette, anything that's a design preference rather than a structural error.

Output as YAML under `findings:` with `tier` / `where` / `issue` per entry. End with `verdict:`.
```

## Body-page prompt

```
This is a body page from a LaTeX document. Identify visual issues:

- Paragraph spacing inconsistency: do paragraph breaks look like one consistent skip, or do some look notably wider/narrower?
- Hyphenation / justification artefacts: rivers of white space, three or more hyphens stacked at line ends, last line of paragraph drastically short
- Widow or orphan lines: single line of a paragraph stranded at page top or bottom
- Float placement: are figures/tables in jarring positions (e.g., immediately after their reference, or stranded at the wrong page edge)? Does any float visibly overlap text?
- Section-heading spacing: is the gap above each section consistent with others?
- Margin alignment: is anything visibly out of margin (figures, tables, equations, long-word overflow)
- Page balance: does the page feel obviously top-heavy or bottom-heavy, with large unexplained whitespace?

Ignore: typography choice, font, content. Focus on layout integrity.

Output as YAML under `findings:` with `tier` / `where` / `issue` per entry. End with `verdict:`.
```

## Table-or-figure-page prompt

```
This is a page from a LaTeX document containing a table or figure. Identify visual issues:

- Caption position: is the caption clearly attached to its table/figure (not stranded above the previous block or below the next)?
- Legibility at this rendered size: can you read all the text in the table/figure, or has scaling made it unreadable?
- Alignment: are table columns aligned consistently? Are decimals or units aligned?
- Clipping: is any element cut off at a margin, page edge, or column boundary?
- Awkward whitespace: large unexplained gaps inside the table/figure, around the caption, or between the float and surrounding text
- Float-vs-text ordering: does the float appear before its first reference in the prose? Far after it?
- Border / rule consistency: are horizontal rules consistent (booktabs vs hline mixed)?
- Caption length vs visual weight: is the caption disproportionately long for a small figure, or trivially short for a complex one?

Ignore: choice of colour, font, content. Focus on layout and legibility.

Output as YAML under `findings:` with `tier` / `where` / `issue` per entry. End with `verdict:`.
```

## Bibliography-page prompt

```
This is a bibliography or references page from a LaTeX document. Identify visual issues:

- Hanging indent: are entries formatted with a consistent hanging indent (first line flush, continuation lines indented)?
- Inter-entry spacing: is the gap between entries consistent?
- Long-URL or DOI handling: are URLs broken across lines properly (no margin overflow)? Are DOIs aligned with the entry style?
- Author-list formatting: is the author list formatting consistent across entries (initials vs full names, et al. usage)?
- Entry alignment: do all entries left-align consistently? Are line widths reasonable?
- Page balance: does the bibliography page feel sensibly filled, or does it have a tiny one-entry overflow page that should have been pulled back?

Ignore: choice of citation style (the user has committed to natbib or biblatex etc. already). Focus on layout integrity within the chosen style.

Output as YAML under `findings:` with `tier` / `where` / `issue` per entry. End with `verdict:`.
```

## General fallback prompt

```
This is a page from a LaTeX document. Identify any visual layout issues you can see:

- Awkward spacing, alignment problems, or whitespace inconsistencies
- Clipped or overlapping content
- Anything that looks like LaTeX's float algorithm failed
- Anything that looks like a manual layout fix that produced a worse result
- Typography weirdness (font-size jumps, unintended bold, missing italic correction)
- Cross-references that visibly render as `??` or `[?]`

Ignore: choice of font, colour, content. Focus on structural / layout integrity.

Output as YAML under `findings:` with `tier` / `where` / `issue` per entry. End with `verdict:`.
```

## Severity tier guidance

| Tier | Examples |
|------|----------|
| **Major** | Clipped content; overlap; unreadable shrunken text; missing/broken references rendered; large unexplained blank area; visibly broken float placement |
| **Moderate** | Inconsistent paragraph spacing; widow/orphan; modest hyphenation rivers; one-line overflow page |
| **Minor** | Small alignment imperfection; mildly inconsistent inter-block gap; aesthetic preference |
| **Skip** | Choice of font, colour, content, terminology — anything substantive rather than structural |
