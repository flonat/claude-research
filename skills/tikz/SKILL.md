---
name: tikz
description: Use when labels overlap arrows in a TikZ figure, text sits on boxes, or arrows cross each other. Audits and fixes residual TikZ visual collisions in any .tex file using mathematical gap calculations and Bézier depth formulas — no eyeballing. Downstream repair tool; the upstream defense is generating TikZ safely via /beamer-deck and tikz_rules.md.
allowed-tools: Bash(pdflatex*), Bash(latexmk*), Bash(grep*), Bash(ls*), Read, Edit, Glob
argument-hint: '[path/to/file.tex]'
---

# TikZ Collision Audit

**Purpose**: Find and fix residual visual collisions in TikZ figures in a given `.tex` file. Labels on arrows, text inside boxes, arrows crossing arrows — this skill catches them using measurement, not intuition.

**The fundamental rule**: Claude cannot reliably eyeball where TikZ elements land. All placement must be verified mathematically before declaring it safe.

---

## Critical context: this is a repair tool, not the primary defense

`/tikz` runs **after** TikZ has been generated. It audits existing code and fixes what it finds. But it cannot reliably fix diagrams that were never built with measurement in mind.

**The upstream defense** is writing TikZ safely from the start:

1. Every `\node` declares explicit `minimum width` and `minimum height`
2. Every edge label carries a directional keyword (`above`, `below`, etc.)
3. A coordinate map comment block precedes every `tikzpicture`
4. Standard diagram types use canonical safe templates
5. `scale` is never used on complex diagrams

When new decks are authored via `/beamer-deck`, prefer applying these rules during generation. `/tikz` is the downstream cleanup pass for anything that slipped through or for legacy/hand-written TikZ.

**When upstream rules were applied**: `/tikz` should find few or no issues. Run it as a check.

**When upstream rules were NOT applied** (legacy TikZ, hand-written diagrams, inherited decks): `/tikz` does its best, but expect more findings, more iteration, and lower reliability on autosized nodes and scaled diagrams.

The companion reference `tikz_rules.md` (in this skill's directory) contains the full formulas and worked examples — read it once before running the audit passes below.

---

## Step 1: Identify the file and run the pre-check

If the user specified a file, use it. If not, ask. Then:

```bash
grep -n "tikzpicture\|begin{frame}\|node\|draw\|bend\|foreach" [file].tex | head -100
```

Get a sense of scope: how many TikZ diagrams, how many frames, how many arrows.

### Pre-check: were the generation rules followed?

Before running the six audit passes, quickly assess whether the TikZ was written safely:

```bash
# Check for autosized nodes (no minimum width/height)
grep -n "\\\\node" [file].tex | grep -v "minimum"
```

```bash
# Check for scale on tikzpicture
grep -n "scale=" [file].tex
```

```bash
# Check for coordinate map comments
grep -n "% Coordinate map\|% Node map\|% Layout" [file].tex
```

**If autosized nodes are widespread**: warn that repair reliability will be lower. The fix is upstream — add explicit dimensions to every node. Consider doing that first before running the audit passes.

**If `scale` is used on a complex diagram**: warn that coordinates are compressed but text is not. Gap calculations in Passes 2–5 must compensate for the scale factor, but this compensation is fragile. The better fix is upstream: redesign at intended size.

**If no coordinate map exists**: the audit will take longer because spatial relationships must be reverse-engineered from the code rather than read from a plan.

---

## Step 2: For each TikZ diagram, run all 6 Passes in order

Full rules and formulas are in `tikz_rules.md` alongside this SKILL. Read it if you haven't. What follows is the operational checklist — the reference file has the formulas and worked examples.

---

### Pass 0: Cross-slide consistency

```bash
grep -n "node.*{" [file].tex | grep -v "^[[:space:]]*%"
```

If the same diagram appears on multiple slides: colors, positions, and font sizes must be identical across all instances. Only the deliberate change (a new highlight, a new node) should differ.

---

### Pass 1: Bézier curves — do this FIRST

```bash
grep -n "bend" [file].tex
```

For **each** curved arrow found, compute:

```
chord_length = distance between the two endpoints
max_depth    = (chord_length / 2) × tan(bend_angle / 2)
safe_zone    = max_depth + 0.5cm
```

Quick reference:

| Bend | tan(angle/2) |
|------|-------------|
| 20°  | 0.176       |
| 25°  | 0.222       |
| 30°  | 0.268       |
| 35°  | 0.315       |
| 40°  | 0.364       |
| 45°  | 0.414       |

**Check 1**: Is any label within `safe_zone` of the baseline, in the direction the curve bends? If yes → move the label.

**Check 2**: Does the curve cross any other arrow in the same figure? Curves bending down cross vertical arrows. Fix: reverse the bend direction.

---

### Pass 2: Label-between-nodes gap calculation

For every arrow label placed between two nodes:

```
Available gap  = center-to-center distance − half-width(A) − half-width(B)
Usable space   = Available gap − 0.6cm   [0.3cm padding each side]
```

Estimate label width using character counts:

| Font         | Width/char |
|--------------|-----------|
| `\scriptsize`  | 0.10 cm   |
| `\footnotesize`| 0.12 cm   |
| `\small`       | 0.15 cm   |
| `\normalsize`  | 0.18 cm   |
| Bold           | +10%      |

**Known limitation**: these estimates break down for math mode (`$\beta$` is wider than 1 character), `\textbf` content, multi-word labels, and anything non-ASCII. When in doubt, overestimate width by 20%.

**If `scale` is in effect**: multiply the usable space by the scale factor, but leave the label width estimate at native size. This is the core of the `scale` problem — coordinates shrink, text does not.

If **estimated label width > usable space**: guaranteed collision. Fix: move above/below, or shorten text, or increase node spacing.

**The most common fix** for labels that exceed the gap: break the label out as a standalone `\node` positioned above the arrow midpoint — clear of both boxes — rather than as an inline edge label.

---

### Pass 3: Arrow label positioning keywords

```bash
grep -n "node\[" [file].tex | grep -v "above\|below\|left\|right\|anchor\|pos\|midway\|near"
```

Every arrow label must carry a directional keyword. Any `node[...]` on an arrow without `above`, `below`, `left`, `right`, `anchor=`, `pos=`, or `midway` will sit ON the arrow line. Fix: add the keyword.

---

### Pass 4: Labels vs. drawn shapes (Boundary Rule)

For every `\node`, `\fill`, `\draw` circle/rectangle: compute the boundary. Any text within 0.4cm of a shape edge is a collision.

**Circles**: center `(cx, cy)`, radius `r` → boundary from `cy − r` to `cy + r`
**Rectangles/boxes**: bottom-left `(x,y)`, width `w`, height `h` → top edge at `y + h`

If a label coordinate puts it inside or touching a shape boundary — move it 0.4cm outside.

**Note on `scale`**: `scale=0.8` shrinks coordinates but NOT text. A 2 cm gap becomes 1.6 cm, but a `\small` label stays `\small`. Recalculate all gaps accounting for scale. **If the diagram uses `scale` on a complex figure, flag this to the user as an upstream problem — the reliable fix is to redesign at intended size, not to compensate in the audit.**

---

### Pass 5: Margin check

Minimum clearances:

| Pair                          | Minimum |
|-------------------------------|---------|
| Label ↔ label                 | 0.3 cm  |
| Label ↔ axis line             | 0.3 cm  |
| Label ↔ arrow                 | 0.3 cm  |
| Arrow origin ↔ box edge       | 0.15 cm |
| Label ↔ shape boundary        | 0.4 cm  |
| Any object ↔ slide edge       | 0.5 cm  |

Also check:
- Multi-line nodes have `align=center` or `align=left`?
- No node text clipped by the slide margin?
- If `scale` is used: did text get unintentionally large relative to shrunken coordinates?

---

### Pass 6: Debug bounding-box verification

**Do NOT attempt to visually inspect the PDF by "eyeballing."** Claude cannot reliably see TikZ collisions in rendered PDFs. Instead, use a debug bounding-box approach:

1. **Temporarily add red debug outlines** around every node to make bounding boxes structurally visible:

```latex
% DEBUG — add to preamble temporarily, remove before shipping
\tikzset{every node/.append style={draw=red, very thin}}
```

2. **Compile and inspect**: with red outlines, overlapping bounding boxes are visible as overlapping red rectangles. This makes collisions structurally obvious rather than visually estimated.

3. **For each red-box overlap found**: go back to the source, fix the coordinates or dimensions, remove the debug line, and recompile.

4. **Remove the debug line** before declaring the audit complete. The debug outlines are a diagnostic tool, not a permanent addition.

This replaces the older instruction to "open the PDF and visually confirm." The debug-outline method catches the same problems but does not depend on Claude's unreliable ability to interpret rendered PDF geometry.

---

## Step 3: Fix, recompile, repeat

After making fixes, prefer `latexmk` (the user's default):

```bash
latexmk -pdf -interaction=nonstopmode [file].tex 2>&1 | grep -E "Overfull|Underfull|Error|Warning"
```

or `pdflatex` if `latexmk` isn't set up for the file:

```bash
pdflatex -interaction=nonstopmode [file].tex 2>&1 | grep -E "Overfull|Underfull|Error|Warning"
```

Must return zero lines of Error. Fix any new Overfull/Underfull warnings introduced by the repositioning. Repeat until clean.

---

## Step 4: Re-audit the ENTIRE file after any fix

One collision fix often reveals a second one nearby, or introduces a new label that now crowds a different object. After every change, re-run Passes 1–5 on **all** TikZ figures in the file — not just the one you just touched.

```bash
grep -c "tikzpicture" [file].tex
```

That count is how many diagrams need a clean bill of health.

---

## Known limitations

These are the cases where `/tikz` is least reliable. When you encounter them, the better fix is almost always upstream (rewrite the TikZ safely) rather than downstream (try to repair it).

| Limitation | Why it's hard | Upstream fix |
|---|---|---|
| **Autosized nodes** (no `minimum width`/`minimum height`) | Rendered dimensions depend on text content and font — `/tikz` can only estimate, not compute exactly | Add explicit dimensions |
| **`scale` on complex diagrams** | Coordinates shrink but text does not; gap calculations require fragile compensation | Redesign at intended size |
| **Math-mode label widths** | `$\hat{\beta}_{it}$` is wider than character-count × width/char suggests | Overestimate by 20–30% or measure with a test compile |
| **Nested `tikzpicture` environments** | Coordinate systems interact unpredictably | Flatten into a single environment |
| **`\foreach` loops generating many nodes** | Gap calculations must be done per-iteration; easy to miss one | Write explicit nodes for small counts; check loop bounds for large counts |

---

## Common collision patterns and fast fixes

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Label between wide boxes | Text bleeds into box edge | Move label above arrow as standalone `\node` |
| Step 1 / Step 2 labels on flow diagrams | Labels overlap box text | Place labels above the arrow band, not as edge labels |
| Diagonal arrow label at `below right` | Label lands inside another box | Use `pos=0.55` + compute landing position |
| Return curve crossing vertical arrow | Arrows intersect visually | Reverse bend direction (`bend left` ↔ `bend right`) |
| Scale mismatch | Text large, gaps small | **Redesign at intended size; do not use `scale` on complex diagrams** |
| Slope label on regression line | Label sits on the line | Use `node[anchor=west]` at a point 0.3cm off the line end |
| `\\` inside `\textcolor{}` | Hbox overflow | Break into two separate `\textcolor` calls on separate lines |
| Curve labels at right endpoints colliding with brace annotations | Labels horizontally adjacent at similar y | Move curve labels to different x position, or use a legend in the text column instead |

---

## Acknowledgments

Ported from Scott Cunningham's MixtapeTools skill library (`resources/academics/scott-cunningham/MixtapeTools/.claude/skills/tikz/`). The companion `tikz_rules.md` is adapted from `MixtapeTools/.claude/skills/compiledeck/tikz_rules.md`. Upstream-defense references have been rewritten to point at `/beamer-deck` and the user's unified `user-beamer` template.
