# Research Poster Design: Core Principles, Typography & Color

> Visual hierarchy, white space, alignment, typography, and color theory.
> See also: [poster_design_accessibility.md](poster_design_accessibility.md) for accessibility & layout.


## Overview

Effective poster design balances visual appeal, readability, and scientific content. This guide covers typography, color theory, visual hierarchy, accessibility, and evidence-based design principles for research posters.

## Core Design Principles

### 1. Visual Hierarchy

Guide viewers through content in logical order using size, color, position, and contrast.

**Hierarchy Levels**:

1. **Primary (Title)**: Largest, most prominent
   - Size: 72-120pt
   - Position: Top center or top spanning
   - Weight: Bold
   - Purpose: Capture attention from 20+ feet

2. **Secondary (Section Headers)**: Organize content
   - Size: 48-72pt
   - Weight: Bold or semi-bold
   - Purpose: Section navigation, readable from 10 feet

3. **Tertiary (Body Text)**: Main content
   - Size: 24-36pt minimum
   - Weight: Regular
   - Purpose: Detailed information, readable from 4-6 feet

4. **Quaternary (Captions, References)**: Supporting info
   - Size: 18-24pt
   - Weight: Regular or light
   - Purpose: Context and attribution

**Implementation**:
```latex
% Define hierarchy in LaTeX
\setbeamerfont{title}{size=\VeryHuge,series=\bfseries}        % 90pt+
\setbeamerfont{block title}{size=\Huge,series=\bfseries}      % 60pt
\setbeamerfont{block body}{size=\LARGE}                        % 30pt
\setbeamerfont{caption}{size=\large}                           % 24pt
```

### 2. White Space (Negative Space)

Empty space is not wasted space—it enhances readability and guides attention.

**White Space Functions**:
- **Breathing room**: Prevents overwhelming viewers
- **Grouping**: Shows which elements belong together
- **Focus**: Draws attention to important elements
- **Flow**: Creates visual pathways through content

**Guidelines**:
- Minimum 5-10% margins on all sides
- Consistent spacing between blocks (1-2cm)
- Space around figures equal to or greater than border width
- Group related items closely, separate unrelated items
- Don't fill every inch—aim for 40-60% text coverage

**LaTeX Implementation**:
```latex
% beamerposter spacing
\setbeamertemplate{block begin}{
  \vskip2ex  % Space before block
  ...
}

% tikzposter spacing
\documentclass[..., blockverticalspace=15mm, colspace=15mm]{tikzposter}

% Manual spacing
\vspace{2cm}  % Vertical space
\hspace{1cm}  % Horizontal space
```

### 3. Alignment and Grid Systems

Proper alignment creates professional, organized appearance.

**Alignment Types**:
- **Left-aligned text**: Most readable for body text (Western audiences)
- **Center-aligned**: Headers, titles, symmetric layouts
- **Right-aligned**: Rarely used, special cases only
- **Justified**: Avoid (creates uneven spacing)

**Grid Systems**:
- **2-column**: Simple, traditional, good for narrative flow
- **3-column**: Most common, balanced, versatile
- **4-column**: Complex, information-dense, requires careful design
- **Asymmetric**: Creative, modern, requires expertise

**Best Practices**:
- Align block edges to invisible grid lines
- Keep consistent column widths (unless intentionally asymmetric)
- Align similar elements (all figures, all text blocks)
- Use consistent margins throughout

### 4. Visual Flow and Reading Patterns

Design for natural eye movement and logical content progression.

**Common Reading Patterns**:

**Z-Pattern (Landscape posters)**:
```
Start → → → Top Right
  ↓
Middle Left → → Middle
  ↓
Bottom Left → → → End
```

**F-Pattern (Portrait posters)**:
```
Title → → → →
↓
Section 1 → →
↓
Section 2 → →
↓
Section 3 → →
↓
Conclusion → →
```

**Gutenberg Diagram**:
```
Primary Area     Strong Fallow
(top-left)       (top-right)
        ↓              ↓
Weak Fallow      Terminal Area
(bottom-left)    (bottom-right)
```

**Implementation Strategy**:
1. Place most important content in "hot zones" (top-left, center)
2. Create visual paths with arrows, lines, or color
3. Use numbering for sequential information (Methods steps)
4. Design left-to-right, top-to-bottom flow (Western audiences)
5. Position conclusions prominently (bottom-right is natural endpoint)

## Typography

### Font Selection

**Recommended Fonts**:

**Sans-Serif (Recommended for posters)**:
- **Helvetica**: Clean, professional, widely available
- **Arial**: Similar to Helvetica, universal compatibility
- **Calibri**: Modern, friendly, good readability
- **Open Sans**: Contemporary, excellent web and print
- **Roboto**: Modern, Google design, highly readable
- **Lato**: Warm, professional, works at all sizes

**Serif (Use sparingly)**:
- **Times New Roman**: Traditional, formal
- **Garamond**: Elegant, good for humanities
- **Georgia**: Designed for screens, readable

**Avoid**:
- ❌ Comic Sans (unprofessional)
- ❌ Decorative or script fonts (illegible from distance)
- ❌ Mixing more than 2-3 font families

**LaTeX Implementation**:
```latex
% Helvetica (sans-serif)
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

% Arial-like
\usepackage{avant}
\renewcommand{\familydefault}{\sfdefault}

% Modern fonts with fontspec (requires LuaLaTeX/XeLaTeX)
\usepackage{fontspec}
\setmainfont{Helvetica Neue}
\setsansfont{Open Sans}
```

### Font Sizing

**Absolute Minimum Sizes** (readable from 4-6 feet):
- Title: 72pt+ (85-120pt recommended)
- Section headers: 48-72pt
- Body text: 24-36pt (30pt+ recommended)
- Captions/small text: 18-24pt
- References: 16-20pt minimum

**Testing Readability**:
- Print at 25% scale
- Read from 2-3 feet distance
- If legible, full-scale poster will be readable from 8-12 feet

**Size Conversion**:
| LaTeX Command | Approximate Size | Use Case |
|---------------|------------------|----------|
| `\tiny` | 10pt | Avoid on posters |
| `\small` | 16pt | Minimal use only |
| `\normalsize` | 20pt | References (scaled up) |
| `\large` | 24pt | Captions, small text |
| `\Large` | 28pt | Body text (minimum) |
| `\LARGE` | 32pt | Body text (recommended) |
| `\huge` | 36pt | Subheadings |
| `\Huge` | 48pt | Section headers |
| `\VeryHuge` | 72pt+ | Title |

### Text Formatting Best Practices

**Use**:
- ✅ **Bold** for emphasis and headers
- ✅ Short paragraphs (3-5 lines maximum)
- ✅ Bullet points for lists
- ✅ Adequate line spacing (1.2-1.5)
- ✅ High contrast (dark text on light background)

**Avoid**:
- ❌ Italics from distance (hard to read)
- ❌ ALL CAPS FOR LONG TEXT (SLOW TO READ)
- ❌ Underlines (old-fashioned, interferes with descenders)
- ❌ Long paragraphs (> 6 lines)
- ❌ Light text on light backgrounds

**Line Spacing**:
```latex
% Increase line spacing for readability
\usepackage{setspace}
\setstretch{1.3}  % 1.3x normal spacing

% Or in specific blocks
\begin{spacing}{1.5}
  Your text here with extra spacing
\end{spacing}
```

## Color Theory for Posters

### Color Psychology and Meaning

Colors convey meaning and affect viewer perception:

| Color | Associations | Use Cases |
|-------|--------------|-----------|
| **Blue** | Trust, professionalism, science | Academic, medical, technology |
| **Green** | Nature, health, growth | Environmental, biology, health |
| **Red** | Energy, urgency, passion | Attention, warnings, bold statements |
| **Orange** | Creativity, enthusiasm | Innovative research, friendly approach |
| **Purple** | Wisdom, creativity, luxury | Humanities, arts, premium research |
| **Gray** | Neutral, professional, modern | Technology, minimal designs |
| **Yellow** | Optimism, attention, caution | Highlights, energy, caution areas |

### Color Scheme Types

**1. Monochromatic**: Variations of single hue
- **Pros**: Harmonious, professional, easy to execute
- **Cons**: Can be boring, less visual interest
- **Use**: Conservative conferences, institutional branding

```latex
% Monochromatic blue scheme
\definecolor{darkblue}{RGB}{0,51,102}
\definecolor{medblue}{RGB}{51,102,153}
\definecolor{lightblue}{RGB}{204,229,255}
```

**2. Analogous**: Adjacent colors on color wheel
- **Pros**: Harmonious, visually comfortable
- **Cons**: Low contrast, may lack excitement
- **Use**: Nature/biology topics, smooth gradients

```latex
% Analogous blue-green scheme
\definecolor{blue}{RGB}{0,102,204}
\definecolor{teal}{RGB}{0,153,153}
\definecolor{green}{RGB}{51,153,102}
```

**3. Complementary**: Opposite colors on wheel
- **Pros**: High contrast, vibrant, energetic
- **Cons**: Can be overwhelming if intense
- **Use**: Drawing attention, modern designs

```latex
% Complementary blue-orange scheme
\definecolor{primary}{RGB}{0,71,171}     % Blue
\definecolor{accent}{RGB}{255,127,0}     % Orange
```

**4. Triadic**: Three evenly spaced colors
- **Pros**: Balanced, vibrant, visually rich
- **Cons**: Can appear busy if not balanced
- **Use**: Multi-topic posters, creative fields

```latex
% Triadic scheme
\definecolor{blue}{RGB}{0,102,204}
\definecolor{red}{RGB}{204,0,51}
\definecolor{yellow}{RGB}{255,204,0}
```

**5. Split-Complementary**: Base + two adjacent to complement
- **Pros**: High contrast but less tense than complementary
- **Cons**: Complex to balance
- **Use**: Sophisticated designs, experienced designers

### High-Contrast Combinations

Ensure readability with sufficient contrast:

**Excellent Contrast (Use these)**:
- Dark blue on white
- Black on white
- White on dark blue/green/purple
- Dark gray on light yellow
- Black on light cyan

**Poor Contrast (Avoid)**:
- ❌ Red on green (color-blind issue)
- ❌ Yellow on white
- ❌ Light gray on white
- ❌ Blue on black (hard to read)
- ❌ Any pure colors on each other

**Contrast Ratio Standards**:
- Minimum: 4.5:1 (WCAG AA)
- Recommended: 7:1 (WCAG AAA)
- Test at: https://webaim.org/resources/contrastchecker/

**LaTeX Color Contrast**:
```latex
% High contrast header
\setbeamercolor{block title}{bg=black, fg=white}

% Medium contrast body
\setbeamercolor{block body}{bg=gray!10, fg=black}

% Check contrast manually or use online tools
```

### Color-Blind Friendly Palettes

~8% of males and ~0.5% of females have color vision deficiency.

**Safe Color Combinations**:
- Blue + Orange (most universally distinguishable)
- Blue + Yellow
- Blue + Red
- Purple + Green (use with caution)

**Avoid**:
- ❌ Red + Green (indistinguishable to most common color blindness)
- ❌ Green + Brown
- ❌ Blue + Purple (can be problematic)
- ❌ Light green + Yellow

**Recommended Palettes**:

**IBM Color Blind Safe** (excellent accessibility):
```latex
\definecolor{ibmblue}{RGB}{100,143,255}
\definecolor{ibmmagenta}{RGB}{254,97,0}
\definecolor{ibmpurple}{RGB}{220,38,127}
\definecolor{ibmcyan}{RGB}{33,191,115}
```

**Okabe-Ito Palette** (scientifically tested):
```latex
\definecolor{okorange}{RGB}{230,159,0}
\definecolor{okskyblue}{RGB}{86,180,233}
\definecolor{okgreen}{RGB}{0,158,115}
\definecolor{okyellow}{RGB}{240,228,66}
\definecolor{okblue}{RGB}{0,114,178}
\definecolor{okvermillion}{RGB}{213,94,0}
\definecolor{okpurple}{RGB}{204,121,167}
```

**Paul Tol's Bright Palette**:
```latex
\definecolor{tolblue}{RGB}{68,119,170}
\definecolor{tolred}{RGB}{204,102,119}
\definecolor{tolgreen}{RGB}{34,136,51}
\definecolor{tolyellow}{RGB}{238,221,136}
\definecolor{tolcyan}{RGB}{102,204,238}
```

### Institutional Branding

Match university or department colors:

```latex
% Example: Stanford colors
\definecolor{stanford-red}{RGB}{140,21,21}
\definecolor{stanford-gray}{RGB}{83,86,90}

% Example: MIT colors
\definecolor{mit-red}{RGB}{163,31,52}
\definecolor{mit-gray}{RGB}{138,139,140}

% Example: Cambridge colors
\definecolor{cambridge-blue}{RGB}{163,193,173}
\definecolor{cambridge-lblue}{RGB}{212,239,223}
```

