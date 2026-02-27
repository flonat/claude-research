# Reveal.js Markdown Format Reference

> Format reference for `/quarto-deck`. All slides live in a single `.md` file with `---` separators.

## Basic Structure

```markdown
---
title: "Presentation Title"
theme: white
highlightTheme: github
revealOptions:
  transition: slide
  slideNumber: true
  hash: true
  center: true
  math:
    mathjax: https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
    config: TeX-AMS_HTML-full
---

# Main Title

Subtitle or key question

---

## Assertion title for slide 2

Content goes here.

Note:
Speaker notes go here. Press 's' to open speaker view.

---

## Another assertion title

- Point one
- Point two

---

<!-- .slide: data-background="#003366" -->

## White text on dark background

Use for emphasis slides.

---

## Slide with math

The treatment effect is $\tau = E[Y(1) - Y(0)]$

$$\hat{\tau}_{ATT} = \frac{1}{N_T} \sum_{i: D_i=1} \left( Y_i - \hat{Y}_i^{(0)} \right)$$

---

## Slide with code

```python
import pandas as pd
df = pd.read_csv("data.csv")
print(df.describe())
```

---

## Slide with image

![Description](figures/figure_1.png)

---

## Key takeaway

One sentence that the audience remembers.
```

## Vertical Slides (Sub-sections)

Use `----` (four dashes) for vertical slides within a section:

```markdown
## Main Topic

Overview

----

### Detail 1

First sub-point

----

### Detail 2

Second sub-point
```

## Fragments (Progressive Reveal)

```markdown
- First point <!-- .element: class="fragment" -->
- Second point <!-- .element: class="fragment" -->
- Third point <!-- .element: class="fragment" -->
```

## Custom Themes

Create a `custom.css` file alongside the Markdown:

```css
/* custom.css */
:root {
  --r-background-color: #FAFBFC;
  --r-main-color: #2C3E50;
  --r-heading-color: #003366;
  --r-link-color: #E94560;
  --r-heading-font: 'Source Sans Pro', Helvetica, sans-serif;
  --r-main-font: 'Source Sans Pro', Helvetica, sans-serif;
  --r-heading-text-transform: none;
  --r-main-font-size: 32px;
}

.reveal .slides section {
  text-align: left;
}

.reveal h2 {
  font-size: 1.4em;
  margin-bottom: 0.5em;
}

/* Emphasis slide */
.reveal section[data-background-color] h2 {
  color: white;
}
```

For colour palette starting points, see [`skills/shared/palettes.md`](../shared/palettes.md).
