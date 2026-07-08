# Figure Recipes

> Publication-ready matplotlib recipes for computational papers. Read during Phase 4.
> All recipes export PDF to `paper/figures/`. Styling: serif font, appropriate size, no interactive elements.

## Global Styling

Apply this at the top of every figure script:

```python
"""Publication-quality matplotlib defaults."""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# Publication defaults
STYLE = {
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.figsize": (5.5, 3.5),  # Single-column width
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "lines.linewidth": 1.5,
    "lines.markersize": 4,
}
mpl.rcParams.update(STYLE)

# Method colors (consistent across all figures)
METHOD_COLORS = {
    "Proposed": "#1f77b4",
    "Baseline 1": "#ff7f0e",
    "Baseline 2": "#2ca02c",
    "Baseline 3": "#d62728",
    "Oracle": "#7f7f7f",
}

# Method line styles
METHOD_STYLES = {
    "Proposed": "-",
    "Baseline 1": "--",
    "Baseline 2": "-.",
    "Baseline 3": ":",
    "Oracle": "-",
}

# Double-column figure size
DOUBLE_COL = (7.0, 3.5)
```

## Convergence Plot

Metric vs iteration/budget with mean ± std across seeds.

```python
def plot_convergence(
    df,
    metric: str = "simple_regret",
    output_path: str = "paper/figures/convergence.pdf",
    log_scale: bool = True,
    xlabel: str = "Evaluation budget",
    ylabel: str | None = None,
):
    """Convergence plot: metric vs iteration for multiple methods.

    Args:
        df: Aggregated DataFrame with columns:
            config, iteration, {metric}_mean, {metric}_std
        metric: Column name prefix (looks for {metric}_mean and {metric}_std)
        output_path: Where to save PDF
        log_scale: Use log scale on y-axis
    """
    fig, ax = plt.subplots()

    for method in df["config"].unique():
        sub = df[df["config"] == method].sort_values("iteration")
        x = sub["iteration"].values
        mean = sub[f"{metric}_mean"].values
        std = sub[f"{metric}_std"].values

        color = METHOD_COLORS.get(method, None)
        ls = METHOD_STYLES.get(method, "-")

        ax.plot(x, mean, label=method, color=color, linestyle=ls)
        ax.fill_between(x, mean - std, mean + std, alpha=0.15, color=color)

    if log_scale:
        ax.set_yscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel or metric.replace("_", " ").title())
    ax.legend(frameon=False)

    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved: {output_path}")
```

## Bar Chart with Error Bars

Method comparison across problems (final performance).

```python
def plot_comparison_bars(
    df,
    metric: str = "simple_regret",
    output_path: str = "paper/figures/comparison.pdf",
    ylabel: str | None = None,
):
    """Bar chart comparing methods across problems at final iteration.

    Args:
        df: Aggregated DataFrame. Uses the last iteration per (config, problem).
    """
    # Get final iteration per config
    idx = df.groupby(["config"])["iteration"].idxmax()
    final = df.loc[idx]

    methods = final["config"].unique()
    x = np.arange(len(methods))
    means = final[f"{metric}_mean"].values
    stds = final[f"{metric}_std"].values

    fig, ax = plt.subplots()
    colors = [METHOD_COLORS.get(m, "#999999") for m in methods]
    bars = ax.bar(x, means, yerr=stds, capsize=3, color=colors, edgecolor="black",
                  linewidth=0.5, alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=15, ha="right")
    ax.set_ylabel(ylabel or metric.replace("_", " ").title())

    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved: {output_path}")
```

## Grouped Bar Chart (Methods × Problems)

```python
def plot_grouped_bars(
    df,
    metric: str = "simple_regret",
    group_col: str = "problem",
    method_col: str = "config",
    output_path: str = "paper/figures/grouped_comparison.pdf",
):
    """Grouped bar chart: methods grouped by problem (or vice versa).

    Args:
        df: Aggregated DataFrame with final-iteration rows.
    """
    problems = df[group_col].unique()
    methods = df[method_col].unique()
    n_problems = len(problems)
    n_methods = len(methods)

    x = np.arange(n_problems)
    width = 0.8 / n_methods

    fig, ax = plt.subplots(figsize=DOUBLE_COL)

    for i, method in enumerate(methods):
        sub = df[df[method_col] == method].set_index(group_col).loc[problems]
        offset = (i - n_methods / 2 + 0.5) * width
        color = METHOD_COLORS.get(method, None)

        ax.bar(x + offset, sub[f"{metric}_mean"],
               width=width, yerr=sub[f"{metric}_std"],
               label=method, color=color, edgecolor="black",
               linewidth=0.5, capsize=2)

    ax.set_xticks(x)
    ax.set_xticklabels(problems)
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.legend(frameon=False, ncol=min(n_methods, 4))

    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved: {output_path}")
```

## Ablation Plot

Performance with/without each component.

```python
def plot_ablation(
    results: dict[str, tuple[float, float]],
    output_path: str = "paper/figures/ablation.pdf",
    ylabel: str = "Performance",
    highlight: str = "Full model",
):
    """Ablation bar chart.

    Args:
        results: {variant_name: (mean, std)} dict.
            Example: {"Full model": (0.95, 0.02), "No component A": (0.82, 0.03), ...}
        highlight: Which variant to highlight (the full model).
    """
    variants = list(results.keys())
    means = [results[v][0] for v in variants]
    stds = [results[v][1] for v in variants]

    fig, ax = plt.subplots()
    colors = ["#1f77b4" if v == highlight else "#aec7e8" for v in variants]
    x = np.arange(len(variants))

    ax.barh(x, means, xerr=stds, capsize=3, color=colors,
            edgecolor="black", linewidth=0.5)
    ax.set_yticks(x)
    ax.set_yticklabels(variants)
    ax.set_xlabel(ylabel)
    ax.invert_yaxis()  # Best variant at top

    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved: {output_path}")
```

## Sensitivity Analysis

Metric vs parameter value with confidence bands.

```python
def plot_sensitivity(
    param_values,
    means,
    stds,
    param_name: str = "Parameter",
    metric_name: str = "Performance",
    output_path: str = "paper/figures/sensitivity.pdf",
    log_x: bool = False,
    reference_line: float | None = None,
):
    """Sensitivity analysis: metric vs parameter with confidence band.

    Args:
        param_values: array of parameter values tested
        means: array of metric means at each value
        stds: array of metric stds at each value
        reference_line: horizontal line for default/baseline value
    """
    fig, ax = plt.subplots()

    ax.plot(param_values, means, "o-", color="#1f77b4", markersize=5)
    ax.fill_between(param_values,
                    np.array(means) - np.array(stds),
                    np.array(means) + np.array(stds),
                    alpha=0.2, color="#1f77b4")

    if reference_line is not None:
        ax.axhline(reference_line, color="gray", linestyle="--", alpha=0.5,
                   label="Default")
        ax.legend(frameon=False)

    if log_x:
        ax.set_xscale("log")

    ax.set_xlabel(param_name)
    ax.set_ylabel(metric_name)

    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved: {output_path}")
```

## Pareto Front

2D objective space visualization.

```python
def plot_pareto(
    points: np.ndarray,
    pareto_mask: np.ndarray | None = None,
    obj_names: tuple[str, str] = ("Objective 1", "Objective 2"),
    output_path: str = "paper/figures/pareto.pdf",
    reference_point: np.ndarray | None = None,
):
    """Pareto front visualization in 2D objective space.

    Args:
        points: (n, 2) array of objective values
        pareto_mask: boolean mask of Pareto-optimal points (auto-computed if None)
        reference_point: reference point for hypervolume (shown as marker)
    """
    if pareto_mask is None:
        pareto_mask = _compute_pareto_2d(points)

    fig, ax = plt.subplots()

    # Dominated points
    ax.scatter(points[~pareto_mask, 0], points[~pareto_mask, 1],
               c="#cccccc", s=20, alpha=0.5, label="Dominated", zorder=1)

    # Pareto front
    pareto_pts = points[pareto_mask]
    order = np.argsort(pareto_pts[:, 0])
    pareto_sorted = pareto_pts[order]

    ax.scatter(pareto_sorted[:, 0], pareto_sorted[:, 1],
               c="#1f77b4", s=40, zorder=3, label="Pareto front")
    ax.step(pareto_sorted[:, 0], pareto_sorted[:, 1],
            where="post", color="#1f77b4", alpha=0.5, zorder=2)

    if reference_point is not None:
        ax.scatter(*reference_point, marker="*", c="red", s=100,
                   zorder=4, label="Reference")

    ax.set_xlabel(obj_names[0])
    ax.set_ylabel(obj_names[1])
    ax.legend(frameon=False)

    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved: {output_path}")


def _compute_pareto_2d(points: np.ndarray) -> np.ndarray:
    """Compute Pareto-optimal mask for minimization in 2D."""
    n = len(points)
    mask = np.ones(n, dtype=bool)
    for i in range(n):
        if mask[i]:
            mask[mask] = ~np.all(points[mask] >= points[i], axis=1) | np.all(
                points[mask] == points[i], axis=1
            )
            mask[i] = True
    return mask
```

## Heatmap (2D Parameter Sweep)

```python
def plot_heatmap(
    x_values,
    y_values,
    z_matrix: np.ndarray,
    xlabel: str = "Parameter A",
    ylabel: str = "Parameter B",
    zlabel: str = "Metric",
    output_path: str = "paper/figures/heatmap.pdf",
    cmap: str = "viridis",
    annotate: bool = True,
):
    """Heatmap for 2D parameter sweep results.

    Args:
        x_values: values for x-axis parameter
        y_values: values for y-axis parameter
        z_matrix: (len(y), len(x)) matrix of metric values
        annotate: show values in cells
    """
    fig, ax = plt.subplots()

    im = ax.imshow(z_matrix, cmap=cmap, aspect="auto", origin="lower")
    cbar = fig.colorbar(im, ax=ax, label=zlabel)

    ax.set_xticks(range(len(x_values)))
    ax.set_xticklabels([f"{v:.2g}" for v in x_values])
    ax.set_yticks(range(len(y_values)))
    ax.set_yticklabels([f"{v:.2g}" for v in y_values])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if annotate:
        for i in range(len(y_values)):
            for j in range(len(x_values)):
                val = z_matrix[i, j]
                color = "white" if val < (z_matrix.max() + z_matrix.min()) / 2 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=7, color=color)

    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved: {output_path}")
```

## Action / Decision Timeline

Sequential decisions over budget (from QUIVER pattern).

```python
def plot_decision_timeline(
    iterations: np.ndarray,
    decisions: list[str],
    values: np.ndarray | None = None,
    output_path: str = "paper/figures/timeline.pdf",
    ylabel: str = "Observed value",
):
    """Timeline showing sequential decisions/actions over iterations.

    Args:
        iterations: iteration indices
        decisions: categorical decision labels per iteration
        values: optional numeric values observed at each step
    """
    fig, ax = plt.subplots(figsize=DOUBLE_COL)

    unique_decisions = sorted(set(decisions))
    decision_colors = {d: plt.cm.Set2(i / max(len(unique_decisions) - 1, 1))
                       for i, d in enumerate(unique_decisions)}

    if values is not None:
        ax.plot(iterations, values, "-", color="gray", alpha=0.3, zorder=1)

    for d in unique_decisions:
        mask = np.array([dec == d for dec in decisions])
        ax.scatter(iterations[mask],
                   values[mask] if values is not None else np.zeros(mask.sum()),
                   label=d, color=decision_colors[d], s=30, zorder=2)

    ax.set_xlabel("Iteration")
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, ncol=min(len(unique_decisions), 4),
              loc="upper right", fontsize=8)

    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved: {output_path}")
```

## Table Export (LaTeX)

```python
def export_table(
    df,
    output_path: str = "paper/tables/results.tex",
    caption: str = "Experimental results",
    label: str = "tab:results",
    highlight_best: bool = True,
):
    """Export DataFrame as a LaTeX booktabs table.

    Uses \\input{} pattern — never hard-code numbers in .tex files.
    """
    # Format numeric columns to 2 decimal places
    formatters = {}
    for col in df.select_dtypes(include="number").columns:
        formatters[col] = lambda x: f"{x:.3f}"

    latex = df.to_latex(
        index=False,
        escape=True,
        column_format="l" + "c" * (len(df.columns) - 1),
        formatters=formatters,
    )

    # Add booktabs
    latex = latex.replace("\\toprule", "\\toprule")
    latex = latex.replace("\\bottomrule", "\\bottomrule")

    # Wrap in table environment
    full = (
        f"\\begin{{table}}[htbp]\n"
        f"  \\centering\n"
        f"  \\caption{{{caption}}}\n"
        f"  \\label{{{label}}}\n"
        f"  {latex}"
        f"\\end{{table}}\n"
    )

    from pathlib import Path
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(full)

    print(f"Saved: {output_path}")
```
