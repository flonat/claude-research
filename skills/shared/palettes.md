# Reference Colour Palettes

> Shared reference for `/beamer-deck` and `/quarto-deck`. Starting points drawn from Scott Cunningham's example decks. Always create an original palette.

## Professional (Deep Blues)

| Name | Hex | Use |
|------|-----|-----|
| Midnight | `#1A1A2E` | Headings |
| DeepBlue | `#16213E` | Body text |
| RoyalBlue | `#0F3460` | Secondary |
| Coral | `#E94560` | Accent |
| SoftGray | `#BDC3C7` | Muted elements |
| CloudWhite | `#FAFBFC` | Background |

### Beamer
```latex
\definecolor{Midnight}{HTML}{1A1A2E}
\definecolor{DeepBlue}{HTML}{16213E}
\definecolor{RoyalBlue}{HTML}{0F3460}
\definecolor{Coral}{HTML}{E94560}
\definecolor{SoftGray}{HTML}{BDC3C7}
\definecolor{CloudWhite}{HTML}{FAFBFC}
```

### CSS
```css
--r-background-color: #FAFBFC;
--r-main-color: #16213E;
--r-heading-color: #1A1A2E;
--r-link-color: #E94560;
```

## Energetic (Warm Tones)

| Name | Hex | Use |
|------|-----|-----|
| DarkSlate | `#2C3E50` | Headings, body |
| Crimson | `#C0392B` | Accent |
| Sunset | `#F39C12` | Highlights |
| Teal | `#1ABC9C` | Secondary |
| Lavender | `#9B59B6` | Tertiary |
| LightGray | `#ECF0F1` | Background |

### Beamer
```latex
\definecolor{DarkSlate}{HTML}{2C3E50}
\definecolor{Crimson}{HTML}{C0392B}
\definecolor{Sunset}{HTML}{F39C12}
\definecolor{Teal}{HTML}{1ABC9C}
\definecolor{Lavender}{HTML}{9B59B6}
\definecolor{LightGray}{HTML}{ECF0F1}
```

### CSS
```css
--r-background-color: #ECF0F1;
--r-main-color: #2C3E50;
--r-heading-color: #2C3E50;
--r-link-color: #C0392B;
```

## Academic (Muted Earth)

| Name | Hex | Use |
|------|-----|-----|
| NavyBlue | `#003366` | Headings |
| ForestGreen | `#2E7D32` | Secondary |
| BurntOrange | `#D84315` | Accent |
| WarmGray | `#757575` | Muted |
| Cream | `#FFF8E1` | Background |
| Charcoal | `#37474F` | Body text |

### Beamer
```latex
\definecolor{NavyBlue}{HTML}{003366}
\definecolor{ForestGreen}{HTML}{2E7D32}
\definecolor{BurntOrange}{HTML}{D84315}
\definecolor{WarmGray}{HTML}{757575}
\definecolor{Cream}{HTML}{FFF8E1}
\definecolor{Charcoal}{HTML}{37474F}
```

### CSS
```css
--r-background-color: #FFF8E1;
--r-main-color: #37474F;
--r-heading-color: #003366;
--r-link-color: #D84315;
```
