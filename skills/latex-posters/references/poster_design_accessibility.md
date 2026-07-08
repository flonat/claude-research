# Research Poster Design: Accessibility, Layout & Checklist

> Accessibility considerations, layout composition, visual elements, common mistakes, and checklists.
> See also: [poster_design_typography.md](poster_design_typography.md) for core principles & color.

## Accessibility Considerations

### Universal Design Principles

Design posters usable by the widest range of people:

**1. Visual Accessibility**:
- High contrast text (minimum 4.5:1 ratio)
- Large font sizes (24pt+ body text)
- Color-blind safe palettes
- Clear visual hierarchy
- Avoid relying solely on color to convey information

**2. Cognitive Accessibility**:
- Clear, simple language
- Logical organization
- Consistent layout
- Visual cues for navigation (arrows, numbers)
- Avoid clutter and information overload

**3. Physical Accessibility**:
- Position critical content at wheelchair-accessible height (3-5 feet)
- Include QR codes to digital versions
- Provide printed handouts for detail viewing
- Consider lighting and reflection in poster material choice

### Alternative Text and Descriptions

Make posters accessible to screen readers (for digital versions):

```latex
% Add alt text to figures
\includegraphics[width=\linewidth]{figure.pdf}
% Alternative: Include detailed caption
\caption{Bar graph showing mean±SD of treatment outcomes. 
Control group (blue): 45±5\%; Treatment group (orange): 78±6\%. 
Asterisks indicate significance: *p<0.05, **p<0.01.}
```

### Multi-Modal Information

Don't rely on single sensory channel:

**Use Redundant Encoding**:
- Color + Shape (not just color for categories)
- Color + Pattern (hatching, stippling)
- Color + Label (text labels on graph elements)
- Text + Icons (visual + verbal)

**Example**:
```latex
% Good: Color + shape + label
\begin{tikzpicture}
  \draw[fill=blue, circle] (0,0) circle (0.3) node[right] {Male: 45\%};
  \draw[fill=red, rectangle] (0,-1) rectangle (0.6,-0.4) node[right] {Female: 55\%};
\end{tikzpicture}
```

## Layout Composition

### Rule of Thirds

Divide poster into 3×3 grid; place key elements at intersections:

```
+-----+-----+-----+
|  ×  |     |  ×  |  ← Top third (title, logos)
+-----+-----+-----+
|     |  ×  |     |  ← Middle third (main content)
+-----+-----+-----+
|  ×  |     |  ×  |  ← Bottom third (conclusions)
+-----+-----+-----+
  ↑           ↑
Left        Right
```

**Power Points** (intersections):
- Top-left: Primary section start
- Top-right: Logos, QR codes
- Center: Key figure or main result
- Bottom-right: Conclusions, contact

### Balance and Symmetry

**Symmetric Layouts**:
- Formal, traditional, stable
- Easy to design
- Can appear static or boring
- Good for conservative audiences

**Asymmetric Layouts**:
- Dynamic, modern, interesting
- Harder to execute well
- More visually engaging
- Good for creative fields

**Visual Weight Balance**:
- Large elements = heavy weight
- Dark colors = heavy weight
- Dense text = heavy weight
- Distribute weight evenly across poster

### Proximity and Grouping

**Gestalt Principles**:

**Proximity**: Items close together are perceived as related
```
[Introduction]  [Methods]

[Results]       [Discussion]
```

**Similarity**: Similar items are perceived as grouped
- Use consistent colors for related sections
- Same border styles for similar content types

**Continuity**: Eyes follow lines and paths
- Use arrows to guide through methods
- Align elements to create invisible lines

**Closure**: Mind completes incomplete shapes
- Use partial borders to group without boxing in

## Visual Elements

### Icons and Graphics

Strategic use of icons enhances comprehension:

**Benefits**:
- Universal language (crosses linguistic barriers)
- Faster processing than text
- Adds visual interest
- Clarifies concepts

**Best Practices**:
- Use consistent style (all line, all filled, all flat)
- Appropriate size (1-3cm typical)
- Label ambiguous icons
- Source: Font Awesome, Noun Project, academic icon sets

**LaTeX Implementation**:
```latex
% Font Awesome icons
\usepackage{fontawesome5}
\faFlask{} Methods \quad \faChartBar{} Results

% Custom icons with TikZ
\begin{tikzpicture}
  \node[circle, draw, thick, minimum size=1cm] {\Huge \faAtom};
\end{tikzpicture}
```

### Borders and Dividers

**Use Borders To**:
- Define sections
- Group related content
- Add visual interest
- Match institutional branding

**Border Styles**:
- Solid lines: Traditional, formal
- Dashed lines: Informal, secondary info
- Rounded corners: Friendly, modern
- Drop shadows: Depth, modern (use sparingly)

**Guidelines**:
- Keep consistent width (2-5pt typical)
- Use sparingly (not every element needs a border)
- Match border color to content or theme
- Ensure sufficient padding inside borders

```latex
% tikzposter borders
\usecolorstyle{Denmark}
\tikzposterlatexaffectionproofoff  % Remove bottom-right logo

% Custom border style
\defineblockstyle{CustomBlock}{
  titlewidthscale=1, bodywidthscale=1, titleleft,
  titleoffsetx=0pt, titleoffsety=0pt, bodyoffsetx=0pt, bodyoffsety=0pt,
  bodyverticalshift=0pt, roundedcorners=10, linewidth=2pt,
  titleinnersep=8mm, bodyinnersep=8mm
}{
  \draw[draw=blocktitlebgcolor, fill=blockbodybgcolor, 
        rounded corners=\blockroundedcorners, line width=\blocklinewidth]
       (blockbody.south west) rectangle (blocktitle.north east);
}
```

### Background and Texture

**Background Options**:

**Plain (Recommended)**:
- White or very light color
- Maximum readability
- Professional
- Print-friendly

**Gradient**:
- Subtle gradients acceptable
- Top-to-bottom or radial
- Avoid strong contrasts that interfere with text

**Textured**:
- Very subtle textures only
- Watermarks of logos/molecules (5-10% opacity)
- Avoid patterns that create visual noise

**Avoid**:
- ❌ Busy backgrounds
- ❌ Images behind text
- ❌ High contrast backgrounds
- ❌ Repeating patterns that cause visual artifacts

```latex
% Gradient background in tikzposter
\documentclass{tikzposter}
\definecolorstyle{GradientStyle}{
  % ...color definitions...
}{
  \colorlet{backgroundcolor}{white!90!blue}
  \colorlet{framecolor}{white!70!blue}
}

% Watermark
\usepackage{tikz}
\AddToShipoutPictureBG{
  \AtPageCenter{
    \includegraphics[width=0.5\paperwidth,opacity=0.05]{university-seal.pdf}
  }
}
```

## Common Design Mistakes

### Critical Errors

**1. Too Much Text** (Most common mistake)
- ❌ More than 1000 words
- ❌ Long paragraphs (>5 lines)
- ❌ Small font sizes to fit more content
- ✅ Solution: Cut ruthlessly, use bullet points, focus on key messages

**2. Poor Contrast**
- ❌ Light text on light background
- ❌ Colored text on colored background
- ✅ Solution: Dark on light or light on dark, test contrast ratio

**3. Font Size Too Small**
- ❌ Body text under 24pt
- ❌ Trying to fit full paper content
- ✅ Solution: 30pt+ body text, prioritize key findings

**4. Cluttered Layout**
- ❌ No white space
- ❌ Elements touching edges
- ❌ Random placement
- ✅ Solution: Generous margins, grid alignment, intentional white space

**5. Inconsistent Styling**
- ❌ Multiple font families
- ❌ Varying header styles
- ❌ Misaligned elements
- ✅ Solution: Define style guide, use templates, align to grid

### Moderate Issues

**6. Poor Figure Quality**
- ❌ Pixelated images (<300 DPI)
- ❌ Tiny axis labels
- ❌ Unreadable legends
- ✅ Solution: Vector graphics (PDF/SVG), large labels, clear legends

**7. Color Overload**
- ❌ Too many colors (>5 distinct hues)
- ❌ Neon or overly saturated colors
- ✅ Solution: Limit to 2-3 main colors, use tints/shades for variation

**8. Ignoring Visual Hierarchy**
- ❌ All text same size
- ❌ No clear entry point
- ✅ Solution: Vary sizes significantly, clear title, visual flow

**9. Information Overload**
- ❌ Trying to show everything
- ❌ Too many figures
- ✅ Solution: Show 3-5 key results, link to full paper via QR code

**10. Poor Typography**
- ❌ Justified text (uneven spacing)
- ❌ All caps body text
- ❌ Mixing serif and sans-serif randomly
- ✅ Solution: Left-align body, sentence case, consistent fonts

## Design Checklist

### Before Printing

- [ ] Title visible and readable from 20+ feet
- [ ] Body text minimum 24pt, ideally 30pt+
- [ ] High contrast (4.5:1 minimum) throughout
- [ ] Color-blind friendly palette
- [ ] Less than 800 words total
- [ ] White space around all elements
- [ ] Consistent alignment and spacing
- [ ] All figures high resolution (300+ DPI)
- [ ] Figure labels readable (18pt+ minimum)
- [ ] No orphaned text or awkward breaks
- [ ] Contact information included
- [ ] QR codes tested and functional
- [ ] Consistent font usage (2-3 families max)
- [ ] All acronyms defined
- [ ] Proper institutional branding/logos
- [ ] Print test at 25% scale for readability check

### Content Review

- [ ] Clear narrative arc (problem → approach → findings → impact)
- [ ] 1-3 main messages clearly communicated
- [ ] Methods concise but reproducible
- [ ] Results visually presented (not just text)
- [ ] Conclusions actionable and clear
- [ ] References cited appropriately
- [ ] No typos or grammatical errors
- [ ] Figures have descriptive captions
- [ ] Data visualizations are clear and honest
- [ ] Statistical significance properly indicated

## Evidence-Based Design Recommendations

Research on poster effectiveness shows:

**Findings from Studies**:
1. **Viewers spend 3-5 minutes average** on posters
   - Design for scanning, not deep reading
   - Most important info must be visible immediately

2. **Visual content processed 60,000× faster** than text
   - Use figures, not paragraphs, to convey key findings
   - Images attract attention first

3. **High contrast improves recall** by 40%
   - Dark on light > light on dark for comprehension
   - Color contrast aids memory retention

4. **White space increases comprehension** by 20%
   - Don't fear empty space
   - Margins and padding are essential

5. **Three-column layouts most effective** for portrait posters
   - Balanced visual weight
   - Natural reading flow

6. **QR codes increase engagement** by 30%
   - Provide digital access to full paper
   - Link to videos, code repositories, data

## Resources and Tools

### Color Tools
- **Coolors.co**: Generate color palettes
- **Adobe Color**: Color wheel and accessibility checker
- **ColorBrewer**: Scientific visualization palettes
- **WebAIM Contrast Checker**: Test contrast ratios

### Design Resources
- **Canva**: Poster mockups and inspiration
- **Figma**: Design prototypes before LaTeX
- **Noun Project**: Icons and graphics
- **Font Awesome**: Icon fonts for LaTeX

### Testing Tools
- **Coblis**: Color blindness simulator
- **Vischeck**: Another color blindness checker
- **Accessibility Checker**: WCAG compliance

### LaTeX Packages
- `xcolor`: Extended color support
- `tcolorbox`: Colored boxes and frames
- `fontawesome5`: Icon fonts
- `qrcode`: QR code generation
- `tikz`: Custom graphics

## Conclusion

Effective poster design requires balancing aesthetics, readability, and scientific content. Follow these core principles:

1. **Less is more**: Prioritize key messages over comprehensive detail
2. **Size matters**: Make text large enough to read from distance
3. **Contrast is critical**: Ensure all text is highly readable
4. **Accessibility first**: Design for diverse audiences
5. **Visual hierarchy**: Guide viewers through content logically
6. **Test early**: Print at reduced scale and gather feedback

Remember: A poster is an advertisement for your research and a conversation starter—not a substitute for reading the full paper.

