# Economics Visualisation Conventions

> Standards for figures in economics papers. Read during Phase 2 (EDA) and Phase 4 (Publication Output).
> For full implementation recipes, see `/econ-plots`.

## Journal-Ready Figure Conventions

| Convention | Requirement | Anti-pattern |
|-----------|-------------|-------------|
| **No embedded titles** | `labs(title = NULL)` — title goes in LaTeX `\caption{}` | `ggtitle("My Plot")` |
| **Serif fonts** | `base_family = "serif"` in theme | Default sans-serif |
| **Clean axis labels** | "Employment Rate (%)" | "emp_rate_pct" |
| **PDF output** | `ggsave(..., device = "pdf")` | PNG or JPEG for paper figures |
| **Standard width** | 6.5 inches (single column) | Arbitrary sizes |
| **No gridlines** | `panel.grid.minor = element_blank()` minimum | Heavy grid overlay |
| **Colour-blind safe** | `scale_colour_brewer(palette = "Set2")` | Rainbow or default |
| **Legend at bottom** | `legend.position = "bottom"` | Legend inside plot area |

## Base Theme

```r
theme_econ <- function(base_size = 11) {
  theme_minimal(base_size = base_size, base_family = "serif") +
    theme(
      plot.title = element_blank(),
      plot.subtitle = element_blank(),
      panel.grid.minor = element_blank(),
      legend.position = "bottom",
      legend.title = element_blank(),
      axis.title = element_text(size = rel(0.9)),
      strip.text = element_text(face = "bold")
    )
}
```

## Common Economics Figure Types

| Type | When to use | Key package |
|------|------------|-------------|
| Coefficient plot | Display regression estimates | `modelsummary::modelplot()` |
| Event study plot | DiD pre/post treatment effects | `fixest::iplot()` or custom |
| Binscatter | Conditional mean relationships | `binsreg::binsreg()` |
| RDD plot | Discontinuity visualisation | `rdrobust::rdplot()` |
| Density comparison | Treatment vs control distributions | `ggplot2::geom_density()` |
| Time series | Trends with policy event markers | `ggplot2::geom_line()` |
| Marginal effects | Interaction effect plots | `marginaleffects::plot_slopes()` |

## Table Conventions

| Convention | Requirement | Anti-pattern |
|-----------|-------------|-------------|
| **No embedded captions** | Caption in LaTeX `\caption{}` only | `stargazer(title = "...")` |
| **booktabs only** | `\toprule`, `\midrule`, `\bottomrule` | `\hline` |
| **threeparttable** | Use for table notes | Ad-hoc footnotes |
| **Stars** | `* p < 0.10, ** p < 0.05, *** p < 0.01` | Non-standard thresholds |
| **SE in parentheses** | Standard economics convention | Brackets or no SEs |
| **FE indicators** | "Yes"/"No" row at bottom | Listing FE coefficients |
| **Clustering noted** | State SE type in table footer | Unstated inference |

## Output Routing

- **EDA figures** → `output/figures/` (exploratory, not publication)
- **Publication figures** → `paper/figures/` (via code pipeline)
- **Publication tables** → `paper/tables/` as `.tex` (via code pipeline)
- **Inline statistics** → `paper/tables/inline_stats.tex` as `\newcommand` definitions
