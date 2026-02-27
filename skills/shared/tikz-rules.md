# TikZ & Figure Anti-Collision Rules

> LLMs cannot do spatial reasoning visually. Convert every spatial question to a **computation** before placing elements. These rules are organized as a 6-pass verification workflow to run after any TikZ diagram or matplotlib figure is written or edited.

## The Core Principle

**Never eyeball positions. Calculate them.** Spatial errors (labels on arrows, boxes overlapping, annotations bleeding) are invisible in `.tex` source and Python scripts alike. The only defence is arithmetic verification before compiling or rendering. **These rules apply to both TikZ diagrams AND matplotlib/Python figures.**

---

## Pass 1: Bezier Curve Clearance (Rules 1-3)

> Most dangerous class of error. Curved arrows (`bend left`, `bend right`, `in`/`out` angles) create invisible collision zones that swallow labels.

### Rule 1: Compute Bezier Max Depth Before Placing Any Label Near a Curve

**Problem:** A `bend left=35` arrow looks like it stays close to the straight-line path, but its maximum perpendicular displacement can be large enough to overlap labels, boxes, or other arrows.

**Formula — Bezier max depth:**

```
depth = (chord / 2) * tan(bend_angle / 2)
```

Where:
- `chord` = straight-line distance between the two endpoints
- `bend_angle` = the TikZ bend angle (e.g., 35 for `bend left=35`)

**Example:**

```
% Chord = 6cm, bend left=35
% depth = (6/2) * tan(35/2) = 3 * tan(17.5°) = 3 * 0.3153 = 0.946cm
%
% WRONG: Label placed 0.5cm from the chord — the curve passes through it
\draw[->] (A) to[bend left=35] node[above, yshift=0.5cm] {label} (B);
%
% RIGHT: Label shifted beyond the depth + padding
% Required clearance: 0.946 + 0.3 (padding) = 1.25cm minimum
\draw[->] (A) to[bend left=35] node[above, yshift=1.4cm] {label} (B);
```

**Action:** For every curved arrow, compute the depth. Any element within `depth + 0.3cm` of the chord midpoint is at risk.

### Rule 2: Return Arrows Must Clear Outbound Curves

**Problem:** A diagram has a forward arrow `A -> B` curving one way and a return arrow `B -> A` curving the other. The two curves intersect if both use the same bend angle and the vertical/horizontal offset is insufficient.

**Formula — minimum separation between opposing curves:**

```
min_separation = 2 * depth + gap
                = 2 * (chord/2) * tan(bend_angle/2) + 0.4cm
```

**Example:**

```
% Chord = 5cm, bend left=30 for both directions
% depth = 2.5 * tan(15°) = 2.5 * 0.2679 = 0.67cm
% min_separation = 2 * 0.67 + 0.4 = 1.74cm
%
% WRONG: Both arrows at the same vertical level — they cross
\draw[->] (A) to[bend left=30] (B);
\draw[->] (B) to[bend left=30] (A);
%
% RIGHT: Vertically separate the nodes or increase bend angles asymmetrically
\draw[->] (A) to[bend left=25] (B);
\draw[->] (B) to[bend left=45] (A);  % deeper curve, stays below
```

**Action:** When a diagram has bidirectional curved arrows between the same pair of nodes, compute both depths and verify they don't intersect.

### Rule 3: Curved Arrows Must Not Cross Intermediate Nodes

**Problem:** A curved arrow from node A to node C passes through the vertical/horizontal space occupied by node B (which sits between them). The curve's depth places it directly on top of B.

**Formula — curve y-position at node B's x-coordinate:**

For a symmetric bend, approximate the curve height at horizontal position `x` from the start:

```
y(x) ≈ depth * sin(pi * x / chord)
```

Compare `y(x_B)` against node B's bounding box.

**Example:**

```
% A at (0,0), B at (3,0), C at (6,0). Curve A->C with bend left=30
% chord = 6, depth = 3 * tan(15°) = 0.804cm
% At x=3 (node B): y = 0.804 * sin(pi * 3/6) = 0.804 * 1.0 = 0.804cm
%
% If node B is a box extending 0.5cm above its center, the curve at 0.804cm
% is only 0.3cm above B's top edge — too close.
%
% RIGHT: Increase bend angle or route the arrow above/below the row
```

**Action:** For any curved arrow that spans multiple columns or rows, check whether the curve passes through intermediate nodes.

---

## Pass 2: Gap Calculations (Rules 4-5)

> Minimum spacing between all elements. No two elements should touch or nearly touch.

### Rule 4: Minimum Gap Between Parallel Elements

**Problem:** Adjacent boxes, labels, or arrows placed too close together merge visually or overlap when rendered.

**Minimum gaps:**

| Element pair | Minimum gap |
|-------------|-------------|
| Box edge to box edge | 0.5cm |
| Arrow to parallel arrow | 0.4cm |
| Label baseline to any element | 0.3cm |
| Annotation rectangle edge to any neighbor | 0.5cm |

**Verification:** For every pair of adjacent elements, compute the distance between their nearest edges. If below the minimum, increase spacing.

**Example:**

```
% WRONG: Two boxes with 0.2cm gap — they'll touch or nearly merge
\node[draw, minimum width=2cm] (A) at (0,0) {Box A};
\node[draw, minimum width=2cm] (B) at (2.2,0) {Box B};
% Gap = 2.2 - (0 + 1.0) - 1.0 = 0.2cm  (half-widths: 1.0cm each)
%
% RIGHT: Ensure 0.5cm gap minimum
\node[draw, minimum width=2cm] (A) at (0,0) {Box A};
\node[draw, minimum width=2cm] (B) at (2.5,0) {Box B};
% Gap = 2.5 - 1.0 - 1.0 = 0.5cm
```

### Rule 5: Annotation Rectangles Must Not Bleed Into Neighbors

**Problem:** A dashed rectangle drawn around a group of nodes (e.g., `\draw[dashed] ($(A.north west)+(-0.3,0.3)$) rectangle ...`) extends into the space of neighboring groups.

**Formula — annotation edge position:**

```
annotation_right_edge = rightmost_node_x + node_half_width + padding
annotation_left_edge  = leftmost_node_x  - node_half_width - padding
```

**Overlap test:**

```
overlap = annotation_right_edge > neighbor_left_edge - min_gap
```

If true, reduce padding or increase inter-group spacing.

**Example:**

```
% Group 1 rightmost node at x=4, half-width 1cm, padding 0.4cm
% annotation_right_edge = 4 + 1.0 + 0.4 = 5.4cm
%
% Group 2 leftmost node at x=5.5, half-width 1cm
% neighbor_left_edge = 5.5 - 1.0 = 4.5cm
%
% overlap check: 5.4 > 4.5 - 0.5 = 4.0 → 5.4 > 4.0 → YES, but...
% visual check: 5.4 vs 4.5 = only 0.9cm gap between annotation and box
%
% WRONG: annotation_right_edge (5.4) is only 0.1cm from Group 2's box edge (4.5)
% RIGHT: Move Group 2 to x=6.5 or reduce Group 1 padding to 0.2cm
```

---

## Pass 3: Label Positioning (Rules 6-7)

> Labels must fit in available space and not collide with the elements they describe.

### Rule 6: Text Width Must Fit Available Horizontal Space

**Problem:** A label or node text is wider than the space between its neighbors, causing it to overflow visually even though LaTeX compiles without error.

**Formula — available width:**

```
available_width = right_boundary - left_boundary - 2 * inner_sep
```

**Estimation — text width:** Approximate at 0.15cm per character for `\footnotesize`, 0.18cm for `\small`, 0.22cm for `\normalsize`. Multiply character count by the rate.

**Action:** Before writing any label, estimate its rendered width. If `text_width > available_width`, either:
- Shorten the text
- Use `text width=Xcm` with line breaks
- Reduce font size
- Increase the container

### Rule 7: Edge Labels Must Account for Arrow Curvature

**Problem:** `node[midway, above]` on a curved arrow places the label at the midpoint of the *chord*, not the midpoint of the *curve*. For high bend angles, this puts the label far from the actual arrow.

**Fix:** Use `node[pos=0.5, above]` (which TikZ evaluates along the curve path, not the chord) and add `sloped` if the arrow isn't horizontal. For very curved arrows, manually position with explicit coordinates computed from the depth formula (Rule 1).

**Example:**

```
% WRONG: Label floats away from a sharply curved arrow
\draw[->] (A) to[bend left=50] node[midway, above] {label} (B);
%
% RIGHT: Use pos= along the path and add sloped for angled segments
\draw[->] (A) to[bend left=50] node[pos=0.5, sloped, above] {label} (B);
%
% For extreme cases, compute the curve midpoint and place manually:
% midpoint_x = (x_A + x_B) / 2
% midpoint_y = (y_A + y_B) / 2 + depth  (depth from Rule 1)
\node at (midpoint_x, midpoint_y + 0.3) {label};
```

---

## Pass 4: Labels vs. Drawn Shapes — the Boundary Rule (Rule 8)

> Text placed at hardcoded coordinates that collide with the edge of a circle, rectangle, or filled region. The compiler gives zero warnings — these only show up visually.

### Rule 8: Every Label Near a Shape Must Clear Its Computed Boundary

**The rule:** Every label placed near a drawn geometric shape must have its coordinate verified against the shape's computed boundary. Never place text at a coordinate chosen for aesthetic alignment (e.g., "same y-height as another label") without checking whether that coordinate clears the shape it's near.

**For TikZ circles:** `\draw (cx, cy) circle (r);` → boundary extends from `cy - r` to `cy + r`. Any label must be at least **0.4cm** outside the boundary (if external) or at least **0.4cm** inside (if internal).

```
% WRONG — label at y=2.0 sits exactly on boundary of circle with center (4, 0.5) radius 1.5
\draw (4, 0.5) circle (1.5cm);  % top edge at y = 0.5 + 1.5 = 2.0
\node at (4, 2.0) {Sample};     % COLLISION: y = top edge

% RIGHT — label 0.4cm above the top edge
\node at (4, 2.4) {Sample};     % 2.0 + 0.4 = 2.4 ✓
```

**For TikZ rectangles:** bottom-left `(x, y)` with `minimum width` and `minimum height` → compute edges. Same 0.4cm clearance rule.

**For matplotlib `FancyBboxPatch` / `Circle`:** bottom-left `(x, y)` with width `w` and height `h` → top edge at `y + h`. When positioning `ax.text()` near patches, compute the patch boundary and verify clearance. Text with `va='center'` extends roughly half its font height above and below the anchor — account for this.

**Critical corollary — don't match coordinates across different shapes:** If two shapes have different sizes, a single y-coordinate that's safe for one may collide with the other. Always compute boundaries independently for each shape.

---

## Pass 5: General Structural Checks (Rules 9-10)

> Catch-all checks for common TikZ pitfalls.

### Rule 9: Node Anchors Must Be Consistent Within a Row/Column

**Problem:** Mixing `.center`, `.north`, `.south` anchors within the same visual row causes elements to appear misaligned vertically.

**Rule:** Within any visual row, use the same anchor for all nodes. Within any visual column, use the same anchor. When connecting to a node, specify the anchor explicitly (`A.east`, `B.west`) rather than relying on TikZ's automatic anchor selection.

**Example:**

```
% WRONG: Inconsistent anchors — nodes appear at different heights
\node (A) at (0,0) {Short};
\node[anchor=north] (B) at (3,0) {Tall text\\ two lines};
%
% RIGHT: Both use the same anchor
\node[anchor=center] (A) at (0,0) {Short};
\node[anchor=center] (B) at (3,0) {Tall text\\ two lines};
```

### Rule 10: Coordinate Arithmetic Must Be Verified for Every Placed Element

**Problem:** Copy-paste errors, wrong signs, or forgotten offsets silently place elements in wrong positions. Since LLMs cannot visually verify, every coordinate must be traceable to a formula.

**Rule:** For every `\node at (x,y)` or `\coordinate`, add a comment showing how `x` and `y` were derived:

```
% Column 1 at x=0, Column 2 at x=3.5 (col_width=3, gap=0.5)
% Row 1 at y=0, Row 2 at y=-2.5 (row_height=2, gap=0.5)
\node[draw] (A) at (0, 0)    {Top Left};
\node[draw] (B) at (3.5, 0)  {Top Right};
\node[draw] (C) at (0, -2.5) {Bottom Left};
```

**Action:** After writing a TikZ diagram, re-derive every coordinate from the grid/layout formula. Flag any coordinate that can't be explained by the layout logic.

---

## 6-Pass Verification Workflow

Run these passes **in order** after writing or editing any TikZ diagram or matplotlib figure:

| Pass | Rules | What to check | Stop condition |
|------|-------|---------------|----------------|
| **1. Bezier curves** | 1, 2, 3 | Compute depth for every `bend`/`in`/`out` (TikZ) or `arc3` (matplotlib). Check clearance against all nearby elements. | All curves have documented depths; no element within `depth + 0.3cm` of chord midpoint |
| **2. Gap calculations** | 4, 5 | Measure edge-to-edge distance for every adjacent pair. Check annotation rectangles. | All gaps meet minimums in Rule 4 table |
| **3. Label positioning** | 6, 7 | Estimate text width vs. available space. Verify edge labels account for curvature. | All labels fit; curved-arrow labels use `pos=` or manual placement |
| **4. Shape boundaries** | 8 | Verify every label near a circle/rectangle/patch clears its computed boundary by 0.4cm. | All labels have documented clearance from nearest shape edge |
| **5. Structural checks** | 9, 10 | Verify anchor consistency. Re-derive every coordinate from layout formula. | All anchors consistent; every coordinate has a comment |
| **6. Visual PDF review** | All | Compile and inspect rendered output (use `pdf-to-images.py` if available). | No overlaps, no misalignment, no clipped text |

---

## Quick Reference: Bezier Depth Table

Pre-computed depths for common bend angles (per 1cm of chord):

| Bend angle | `tan(angle/2)` | Depth per cm of chord |
|-----------|----------------|----------------------|
| 15 | 0.1317 | 0.066 cm |
| 20 | 0.1763 | 0.088 cm |
| 25 | 0.2217 | 0.111 cm |
| 30 | 0.2679 | 0.134 cm |
| 35 | 0.3153 | 0.158 cm |
| 40 | 0.3640 | 0.182 cm |
| 45 | 0.4142 | 0.207 cm |
| 50 | 0.4663 | 0.233 cm |
| 60 | 0.5774 | 0.289 cm |

**Usage:** `depth = (chord / 2) * value_from_table`

Example: 8cm chord, bend=40 -> depth = 4 * 0.364 = 1.456cm

---

## Matplotlib Extension: arc3 Bézier & Anchor-Based Centering

> These rules extend the TikZ principles to Python/matplotlib figures generated in Phase 3. The same "never eyeball, always compute" principle applies.

### Bézier-First for matplotlib Arrows

When labelling curved arrows using `connectionstyle='arc3,rad=R'`, compute the actual curve position before placing labels. The same "Claude cannot eyeball where a curve passes" rule from Pass 1 applies to Python figures.

**Control point formula:**

```python
# For ax.annotate with connectionstyle='arc3,rad=R':
# Start: (x1, y1), End: (x2, y2)
dx, dy = x2 - x1, y2 - y1
cx = (x1 + x2) / 2 + R * dy     # control point x
cy = (y1 + y2) / 2 - R * dx     # control point y
```

**To find where the curve passes at any point**, use the quadratic Bézier formula:

```
B(t) = (1-t)²·P0 + 2(1-t)t·P1 + t²·P2,  t ∈ [0,1]
```

**Label placement workflow:**
1. Compute the control point using the formula above
2. Find t at the desired x-coordinate (numerical sampling)
3. Compute y(t) — this is where the curve actually passes
4. Offset the label perpendicular to the curve with a white-background bbox

**Label offset direction:**
- Arrow curves upward → label above (`va='bottom'`)
- Arrow curves downward → label below (`va='top'`)
- Arrow is straight → label above (`va='bottom'`)

### Anchor-Based Centering of Text Pairs

When multiple text elements (title + math, header + body) are placed inside a single container, do NOT use `va='center'` for both at symmetric y-offsets. Multi-line text extends further from its anchor than single-line text, creating visual asymmetry even when coordinates are symmetric.

**Instead, anchor both elements outward from the container's center:**
- Upper element: `va='bottom'` at `center_y + small_gap` (text grows upward)
- Lower element: `va='top'` at `center_y - small_gap` (text grows downward)

```python
# WRONG — symmetric coordinates but visually asymmetric
ax.text(x, box_mid_y + 0.7, 'Title\nLine 2', va='center', ...)  # top-heavy
ax.text(x, box_mid_y - 0.7, r'$math$',       va='center', ...)  # too low

# RIGHT — anchor-based, text grows outward from center
ax.text(x, box_mid_y + 0.15, 'Title\nLine 2', va='bottom', ...)  # grows UP
ax.text(x, box_mid_y - 0.15, r'$math$',       va='top', ...)     # grows DOWN
```

### Helper Functions (Copy-Paste Template)

Include these at the top of any matplotlib script with curved arrows:

```python
import numpy as np

def arc3_control_point(x1, y1, x2, y2, rad):
    """Compute the quadratic Bézier control point for matplotlib's arc3."""
    dx, dy = x2 - x1, y2 - y1
    cx = (x1 + x2) / 2 + rad * dy
    cy = (y1 + y2) / 2 - rad * dx
    return cx, cy

def find_t_for_x(target_x, x1, cx, x2, num_samples=1000):
    """Find the Bézier parameter t where x(t) ≈ target_x."""
    ts = np.linspace(0, 1, num_samples)
    xs = (1 - ts)**2 * x1 + 2 * (1 - ts) * ts * cx + ts**2 * x2
    return ts[np.argmin(np.abs(xs - target_x))]

def bezier_y_at_t(t, y1, cy, y2):
    """Y-coordinate of quadratic Bézier at parameter t."""
    return (1 - t)**2 * y1 + 2 * (1 - t) * t * cy + t**2 * y2
```

**When to use:** Every time a matplotlib figure has `connectionstyle='arc3'` AND labels near those arrows.
