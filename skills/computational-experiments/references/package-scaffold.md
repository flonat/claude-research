# Package Scaffold Reference

> Templates for computational research project structure. Read during Phase 2.

## Directory Layout

```
project-root/
├── src/<pkg_name>/
│   ├── __init__.py          # Version, top-level imports
│   ├── algorithm.py         # Core algorithm implementation
│   ├── config.py            # Config dataclasses
│   ├── metrics.py           # Evaluation metrics
│   ├── oracle.py            # Environment / objective interface
│   └── utils/
│       ├── __init__.py
│       ├── seeds.py         # Seed management
│       └── io.py            # Save/load results
├── tests/
│   ├── __init__.py
│   ├── test_algorithm.py    # Unit tests for core logic
│   ├── test_convergence.py  # Convergence / correctness tests
│   └── test_smoke.py        # End-to-end smoke test (single seed, tiny problem)
├── experiments/
│   ├── configs/             # YAML or Python config files
│   │   ├── default.yaml
│   │   └── sweep_main.yaml
│   ├── run_experiment.py    # Main runner script
│   └── results/             # Output directory (gitignored)
├── scripts/
│   ├── make_all_figures.py  # Regenerate all publication figures
│   └── aggregate_results.py # Aggregate per-seed results
├── paper/                   # Overleaf symlink (LaTeX only)
│   ├── figures/             # PDF figures for paper
│   └── tables/              # .tex tables for paper
├── pyproject.toml
├── .gitignore
├── CLAUDE.md
└── README.md
```

## pyproject.toml Template

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "<pkg-name>"
version = "0.1.0"
description = "<one-line description>"
requires-python = ">=3.11"
dependencies = [
    "numpy>=1.26",
    "scipy>=1.12",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "matplotlib>=3.8",
    "pandas>=2.2",
    "pyyaml>=6.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/<pkg_name>"]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "convergence: convergence correctness tests",
]
```

## __init__.py Template

```python
"""<Package description>."""

__version__ = "0.1.0"
```

## .gitignore Additions

```gitignore
# Experiment outputs
experiments/results/
results/

# Serialized objects
*.pkl
*.pickle
*.npy
*.npz

# Tracking
wandb/
mlruns/

# Build
__pycache__/
*.egg-info/
dist/
build/

# Environment
.venv/

# LaTeX build artifacts
out/
```

## Test Skeleton: Unit Test

```python
"""Unit tests for core algorithm components."""

import numpy as np
import pytest

from <pkg_name>.algorithm import Algorithm  # TODO: adjust import
from <pkg_name>.config import ExperimentConfig  # TODO: adjust import


class TestAlgorithm:
    """Tests for the main algorithm class."""

    def test_initialization(self):
        """Algorithm initializes with valid config."""
        config = ExperimentConfig()  # TODO: fill defaults
        algo = Algorithm(config)
        assert algo is not None

    def test_single_step(self):
        """Algorithm completes one iteration without error."""
        config = ExperimentConfig()
        algo = Algorithm(config)
        # TODO: call algo.step() or equivalent
        pass

    def test_deterministic_with_seed(self):
        """Same seed produces identical results."""
        config = ExperimentConfig(seed=42)
        algo1 = Algorithm(config)
        result1 = algo1.run()  # TODO: adjust

        algo2 = Algorithm(config)
        result2 = algo2.run()

        # TODO: compare result1 and result2
        # np.testing.assert_array_equal(result1, result2)
        pass
```

## Test Skeleton: Convergence Test

```python
"""Convergence and correctness tests.

These tests verify mathematical properties that should hold
regardless of implementation details.
"""

import numpy as np
import pytest

from <pkg_name>.algorithm import Algorithm
from <pkg_name>.config import ExperimentConfig


@pytest.mark.convergence
class TestConvergence:
    """Tests for convergence properties."""

    @pytest.mark.slow
    def test_converges_on_known_problem(self):
        """Algorithm converges to known optimum on a simple test problem."""
        # TODO: define a problem with known solution
        # config = ExperimentConfig(problem="sphere", budget=1000, seed=0)
        # algo = Algorithm(config)
        # result = algo.run()
        # assert result.best_value < 1e-3, f"Did not converge: {result.best_value}"
        pass

    def test_monotonic_improvement(self):
        """Best-so-far metric is non-decreasing (for maximization) or non-increasing."""
        # TODO: run algorithm, check that best_values is monotonic
        pass

    def test_metric_non_negative(self):
        """Key metrics are non-negative where expected."""
        # TODO: verify metric bounds
        pass
```

## Test Skeleton: Smoke Test

```python
"""Smoke tests — end-to-end with minimal budget.

These should run in < 10 seconds and catch import errors,
shape mismatches, and obvious crashes.
"""

import pytest

from <pkg_name>.config import ExperimentConfig


class TestSmoke:
    """Quick end-to-end tests."""

    def test_full_pipeline_runs(self, tmp_path):
        """Complete experiment pipeline runs without error."""
        config = ExperimentConfig(
            # TODO: minimal config
            # budget=10,
            # n_seeds=1,
            # seed=0,
            # output_dir=str(tmp_path),
        )
        # TODO: run the full pipeline
        # from experiments.run_experiment import run_single
        # result = run_single(config)
        # assert (tmp_path / "results.csv").exists()
        pass

    def test_config_serialization(self, tmp_path):
        """Config round-trips through YAML."""
        import yaml

        config = ExperimentConfig()
        path = tmp_path / "config.yaml"

        # TODO: adjust serialization
        # with open(path, "w") as f:
        #     yaml.dump(config.to_dict(), f)
        # with open(path) as f:
        #     loaded = ExperimentConfig.from_dict(yaml.safe_load(f))
        # assert config == loaded
        pass
```

## scripts/make_all_figures.py Template

```python
"""Regenerate all publication figures from saved results.

Usage:
    uv run python scripts/make_all_figures.py [--results-dir experiments/results]

Outputs:
    paper/figures/*.pdf
    paper/tables/*.tex
"""

import argparse
from pathlib import Path

# TODO: import project-specific figure functions
# from scripts.plot_convergence import plot_convergence
# from scripts.plot_comparison import plot_comparison


def main():
    parser = argparse.ArgumentParser(description="Generate all publication figures")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("experiments/results"),
        help="Directory containing experiment results",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=Path("paper/figures"),
        help="Output directory for figures",
    )
    parser.add_argument(
        "--tables-dir",
        type=Path,
        default=Path("paper/tables"),
        help="Output directory for tables",
    )
    args = parser.parse_args()

    args.figures_dir.mkdir(parents=True, exist_ok=True)
    args.tables_dir.mkdir(parents=True, exist_ok=True)

    # TODO: call figure generation functions
    # plot_convergence(args.results_dir, args.figures_dir / "convergence.pdf")
    # plot_comparison(args.results_dir, args.figures_dir / "comparison.pdf")

    print(f"Figures written to {args.figures_dir}")
    print(f"Tables written to {args.tables_dir}")


if __name__ == "__main__":
    main()
```
