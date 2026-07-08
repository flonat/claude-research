# Poster Layout: Blocks, Patterns & Testing

> White space management, block/box design, responsive layouts, research-type patterns, and testing.
> See also: [poster_layout_grids.md](poster_layout_grids.md) for grid systems & visual flow.

## White Space Management

### Margins and Padding

**Outer Margins**:
- Minimum: 2-3cm (0.75-1 inch)
- Recommended: 3-5cm (1-2 inches)
- Prevents edge trimming issues in printing
- Provides visual breathing room

**Inner Spacing**:
- Between columns: 1-2cm
- Between blocks: 1-2cm
- Inside blocks (padding): 0.5-1.5cm
- Around figures: 0.5-1cm

**LaTeX Margin Control**:
```latex
% beamerposter
\usepackage[size=a0, scale=1.4]{beamerposter}
\setbeamersize{text margin left=3cm, text margin right=3cm}

% tikzposter
\documentclass[..., margin=30mm, innermargin=15mm]{tikzposter}

% baposter
\begin{poster}{
  colspacing=1.5em,  % Horizontal spacing
  ...
}
```

### Active White Space vs. Passive White Space

**Active White Space**: Intentionally placed for specific purpose
- Around key figures (draws attention)
- Between major sections (creates clear separation)
- Above/below titles (emphasizes hierarchy)

**Passive White Space**: Natural result of layout
- Margins and borders
- Line spacing
- Gaps between elements

**Balance**: Aim for 30-40% white space overall

### Visual Breathing Room

**Avoid**:
- ❌ Elements touching edges
- ❌ Text blocks directly adjacent
- ❌ Figures without surrounding space
- ❌ Cramped, claustrophobic feel

**Implement**:
- ✅ Clear separation between sections
- ✅ Space around focal points
- ✅ Generous padding inside boxes
- ✅ Balanced distribution of content

## Block and Box Design

### Block Types and Functions

**Title Block**: Poster header
- Full width, top position
- High visual weight
- Contains identifying information

**Content Blocks**: Main sections
- Column-based or free-floating
- Hierarchical sizing (larger = more important)
- Clear headers and structure

**Callout Blocks**: Emphasized information
- Key findings or quotes
- Different color or style
- Visually distinct

**Reference Blocks**: Supporting info
- Footer position
- Smaller, less prominent
- Informational, not critical

### Block Styling Options

**Border Styles**:
```latex
% Rounded corners (friendly, modern)
\begin{block}{Title}
  % beamerposter with rounded
  \setbeamertemplate{block begin}[rounded]
  
% Sharp corners (formal, traditional)
  \setbeamertemplate{block begin}[default]

% No border (minimal, clean)
  \setbeamercolor{block title}{bg=white, fg=black}
  \setbeamercolor{block body}{bg=white, fg=black}
```

**Shadow and Depth**:
```latex
% tikzposter shadow
\tikzset{
  block/.append style={
    drop shadow={shadow xshift=2mm, shadow yshift=-2mm}
  }
}

% tcolorbox drop shadow
\usepackage{tcolorbox}
\begin{tcolorbox}[enhanced, drop shadow]
  Content with shadow
\end{tcolorbox}
```

**Background Shading**:
- **Solid**: Clean, professional
- **Gradient**: Modern, dynamic
- **Transparent**: Layered, sophisticated

### Relationship and Grouping

**Visual Grouping Techniques**:

**1. Proximity**: Place related items close
```
[Intro Text]
[Related Figure]
    ↓ grouped
[Methods Text]
[Methods Diagram]
```

**2. Color Coding**: Use color to show relationships
- All "Methods" blocks in blue
- All "Results" blocks in green
- Conclusions in orange

**3. Borders**: Enclose related elements
```latex
\begin{tcolorbox}[title=Experimental Pipeline]
  \begin{enumerate}
    \item Sample preparation
    \item Data collection
    \item Analysis
  \end{enumerate}
\end{tcolorbox}
```

**4. Alignment**: Aligned elements appear related
```
[Block A Left-aligned]
[Block B Left-aligned]
    vs.
[Block C Centered]
```

## Responsive and Adaptive Layouts

### Designing for Different Poster Sizes

**Scaling Strategy**:
- Design for target size (e.g., A0)
- Test at other common sizes (A1, 36×48")
- Use relative sizing (percentages, not absolute)

**Font Scaling**:
```latex
% Scale fonts proportionally
\usepackage[size=a0, scale=1.4]{beamerposter}  % A0 at 140%
\usepackage[size=a1, scale=1.0]{beamerposter}  % A1 at 100%

% Or define sizes relatively
\newcommand{\titlesize}{\fontsize{96}{110}\selectfont}
\newcommand{\headersize}{\fontsize{60}{72}\selectfont}
```

**Content Adaptation**:
- **A0 (full)**: All content, 5-6 figures
- **A1 (reduced)**: Condense to 3-4 main figures
- **A2 (compact)**: Key finding only, 1-2 figures

### Portrait vs. Landscape Orientation

**Portrait (Vertical)**:
- **Pros**: Traditional, more common stands, natural reading flow
- **Cons**: Less width for figures, can feel cramped
- **Best for**: Text-heavy posters, multi-section flow, conferences

**Landscape (Horizontal)**:
- **Pros**: Wide figures, natural for timelines, modern feel
- **Cons**: Harder to read from distance, less common
- **Best for**: Timelines, wide data visualizations, non-traditional venues

**LaTeX Orientation**:
```latex
% Portrait
\usepackage[size=a0, orientation=portrait]{beamerposter}
\documentclass[..., portrait]{tikzposter}

% Landscape
\usepackage[size=a0, orientation=landscape]{beamerposter}
\documentclass[..., landscape]{tikzposter}
```

## Layout Patterns by Research Type

### Experimental Research

**Typical Flow**:
```
[Title and Authors]
+---------------------------+
| Background | Methods      |
| Problem    | (Diagram)    |
+---------------------------+
| Results (Figure 1)        |
| Results (Figure 2)        |
+---------------------------+
| Discussion | Conclusions  |
| Limitations| Future Work  |
+---------------------------+
[References and Contact]
```

**Emphasis**: Visual results, clear methodology

### Computational/Modeling

**Typical Flow**:
```
[Title and Authors]
+---------------------------+
| Motivation | Algorithm    |
|            | (Flowchart)  |
+---------------------------+
| Implementation Details    |
+---------------------------+
| Results    | Results      |
| (Benchmark)| (Comparison) |
+---------------------------+
| Conclusions| Code QR      |
+---------------------------+
[GitHub, Docker, Documentation]
```

**Emphasis**: Algorithm clarity, reproducibility

### Clinical/Medical

**Typical Flow**:
```
[Title and Authors]
+---------------------------+
| Background | Methods      |
| Clinical   | - Design     |
| Need       | - Population |
|            | - Outcomes   |
+---------------------------+
| Results               |    |
| (Primary Outcome)     | Key|
|                       | Fig|
+---------------------------+
| Discussion | Clinical     |
|            | Implications |
+---------------------------+
[Trial Registration, Ethics, Funding]
```

**Emphasis**: Patient outcomes, clinical relevance

### Review/Meta-Analysis

**Typical Flow**:
```
[Title and Authors]
+---------------------------+
| Research  | Search        |
| Question  | Strategy      |
|           | (PRISMA Flow) |
+---------------------------+
| Included Studies Overview |
+---------------------------+
| Findings  | Findings      |
| (Theme 1) | (Theme 2)     |
+---------------------------+
| Synthesis | Gaps &        |
|           | Future Needs  |
+---------------------------+
[Systematic Review Registration]
```

**Emphasis**: Comprehensive coverage, synthesis

## Layout Testing and Iteration

### Design Iteration Process

**1. Sketch Phase**:
- Hand-draw rough layout
- Experiment with different arrangements
- Mark primary, secondary, tertiary content

**2. Digital Mockup**:
- Create low-fidelity version in LaTeX
- Use placeholder text/figures
- Test different grid systems

**3. Content Integration**:
- Replace placeholders with actual content
- Adjust spacing and sizing
- Refine visual hierarchy

**4. Refinement**:
- Fine-tune alignment
- Balance visual weight
- Optimize white space

**5. Testing**:
- Print at reduced scale (25%)
- View from distance
- Get colleague feedback

### Feedback Checklist

**Visual Balance**:
- [ ] No single area feels too heavy or too light
- [ ] Color distributed evenly across poster
- [ ] Text and figures balanced
- [ ] White space well-distributed

**Hierarchy and Flow**:
- [ ] Clear entry point (title visible)
- [ ] Logical reading path
- [ ] Section relationships clear
- [ ] Conclusions easy to find

**Technical Execution**:
- [ ] Consistent alignment
- [ ] Uniform spacing
- [ ] Professional appearance
- [ ] No awkward breaks or orphans

## Common Layout Mistakes

**1. Unbalanced Visual Weight**
- ❌ All content on left, empty right side
- ❌ Large figure dominating, tiny text elsewhere
- ✅ Distribute content evenly across poster

**2. Inconsistent Spacing**
- ❌ Random gaps between blocks
- ❌ Elements touching in some places, spaced in others
- ✅ Use consistent spacing values throughout

**3. Poor Column Width**
- ❌ Extremely narrow columns (hard to read)
- ❌ Very wide columns (eye tracking difficult)
- ✅ Optimal: 40-80 characters per line

**4. Ignoring Grid**
- ❌ Random placement of elements
- ❌ Misaligned blocks
- ✅ Align to invisible grid, consistent positioning

**5. Overcrowding**
- ❌ No white space, cramped feel
- ❌ Trying to fit too much content
- ✅ Generous margins, clear separation

## Conclusion

Effective layout design:
- Uses appropriate grid systems (2, 3, or 4 columns)
- Follows natural eye movement patterns
- Maintains visual balance and hierarchy
- Provides adequate white space
- Groups related content clearly
- Adapts to different poster sizes and orientations

Remember: Layout should support content, not compete with it. When viewers focus on your research rather than your design, you've succeeded.

