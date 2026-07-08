# Experiment Patterns

> Config schemas, sweep runners, aggregation, and CLI patterns. Read during Phase 3.

## Config Schema (Python Dataclass)

Pattern from IAPE's `ElicitationConfig`: validated, serializable, with sensible defaults.

```python
"""Experiment configuration as a frozen dataclass.

All experiment parameters live here — nothing hardcoded in runner scripts.
Configs are serializable to/from YAML for reproducibility.
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal

import yaml


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration for a single experiment run.

    # TODO: Replace fields with your experiment parameters.
    """

    # --- Problem ---
    problem: str = "sphere"          # Problem name / test function
    dim: int = 5                     # Problem dimensionality

    # --- Algorithm ---
    algorithm: str = "proposed"      # Algorithm name (for comparison)
    budget: int = 100                # Total evaluation budget
    n_initial: int = 10              # Initial design size

    # --- Stochastic ---
    seed: int = 0                    # Random seed for this run
    n_seeds: int = 20                # Number of seeds for aggregation

    # --- Infrastructure ---
    name: str = ""                   # Config name (auto-generated if empty)
    output_dir: Path = Path("experiments/results")

    def __post_init__(self):
        """Validation and auto-naming."""
        if not self.name:
            # Use object.__setattr__ because dataclass is frozen
            object.__setattr__(
                self, "name", f"{self.algorithm}_{self.problem}_d{self.dim}"
            )
        if self.n_initial >= self.budget:
            raise ValueError(
                f"n_initial ({self.n_initial}) must be < budget ({self.budget})"
            )

    def to_dict(self) -> dict:
        """Serialize to dict (Path → str for YAML compatibility)."""
        d = asdict(self)
        d["output_dir"] = str(d["output_dir"])
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ExperimentConfig":
        """Deserialize from dict."""
        if "output_dir" in d:
            d["output_dir"] = Path(d["output_dir"])
        return cls(**d)

    def save(self, path: Path) -> None:
        """Save config to YAML."""
        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

    @classmethod
    def load(cls, path: Path) -> "ExperimentConfig":
        """Load config from YAML."""
        with open(path) as f:
            return cls.from_dict(yaml.safe_load(f))
```

## Sweep Definitions

### Grid Sweep

```python
"""Grid sweep: all combinations of parameter lists."""

from itertools import product
from dataclasses import replace


def grid_sweep(base_config, **param_lists) -> list:
    """Generate configs for all parameter combinations.

    Usage:
        configs = grid_sweep(
            base_config,
            algorithm=["proposed", "random", "ei"],
            problem=["sphere", "ackley", "rastrigin"],
            dim=[2, 5, 10],
        )
    """
    keys = list(param_lists.keys())
    values = list(param_lists.values())
    configs = []

    for combo in product(*values):
        overrides = dict(zip(keys, combo))
        config = replace(base_config, name="", **overrides)
        configs.append(config)

    return configs
```

### Random Sweep

```python
"""Random sweep: sample configurations within bounds."""

import numpy as np
from dataclasses import replace


def random_sweep(base_config, n_configs: int, rng, **param_ranges) -> list:
    """Generate n_configs random configurations.

    param_ranges: dict of param_name -> (low, high) for continuous
                  or param_name -> [list of choices] for categorical.

    Usage:
        configs = random_sweep(
            base_config, n_configs=50, rng=rng,
            learning_rate=(1e-4, 1e-1),  # log-uniform
            n_layers=[1, 2, 3, 4],       # categorical
        )
    """
    configs = []
    for _ in range(n_configs):
        overrides = {}
        for key, spec in param_ranges.items():
            if isinstance(spec, (list, tuple)) and len(spec) == 2 and isinstance(spec[0], (int, float)):
                low, high = spec
                overrides[key] = rng.uniform(low, high)
            elif isinstance(spec, list):
                overrides[key] = rng.choice(spec)
        config = replace(base_config, name="", **overrides)
        configs.append(config)
    return configs
```

### Manual Configs (YAML)

```yaml
# experiments/configs/sweep_main.yaml
# Each entry is a config override on top of defaults.

- algorithm: proposed
  problem: sphere
  dim: 5
  budget: 200

- algorithm: proposed
  problem: ackley
  dim: 5
  budget: 200

- algorithm: random_search
  problem: sphere
  dim: 5
  budget: 200
```

```python
"""Load manual configs from YAML."""

import yaml
from dataclasses import replace
from pathlib import Path


def load_sweep(path: Path, base_config) -> list:
    """Load configs from a YAML sweep file."""
    with open(path) as f:
        entries = yaml.safe_load(f)
    return [replace(base_config, name="", **entry) for entry in entries]
```

## Runner Script

```python
"""Main experiment runner.

Usage:
    uv run python experiments/run_experiment.py --config experiments/configs/default.yaml
    uv run python experiments/run_experiment.py --sweep experiments/configs/sweep_main.yaml --n-seeds 20
    uv run python experiments/run_experiment.py --sweep experiments/configs/sweep_main.yaml --parallel 4
"""

import argparse
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

# TODO: adjust imports
# from <pkg_name>.config import ExperimentConfig
# from <pkg_name>.runner import run_single, save_result
# from <pkg_name>.utils.seeds import seed_sequence


def run_seed(config, seed: int):
    """Run a single (config, seed) pair. Pickleable for multiprocessing."""
    from dataclasses import replace
    config_with_seed = replace(config, seed=seed)
    result = run_single(config_with_seed, seed=seed)
    save_result(result, config_with_seed.output_dir / config_with_seed.name)
    return result


def main():
    parser = argparse.ArgumentParser(description="Run computational experiments")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--config", type=Path, help="Single config YAML file")
    group.add_argument("--sweep", type=Path, help="Sweep definition YAML file")
    parser.add_argument("--n-seeds", type=int, default=20, help="Seeds per config")
    parser.add_argument("--master-seed", type=int, default=42, help="Master seed")
    parser.add_argument("--parallel", type=int, default=1, help="Number of parallel workers")
    parser.add_argument("--output-dir", type=Path, default=None, help="Override output directory")
    args = parser.parse_args()

    # Load configs
    base = ExperimentConfig()
    if args.config:
        configs = [ExperimentConfig.load(args.config)]
    else:
        configs = load_sweep(args.sweep, base)

    if args.output_dir:
        from dataclasses import replace
        configs = [replace(c, output_dir=args.output_dir) for c in configs]

    # Generate seeds
    seeds = seed_sequence(args.master_seed, args.n_seeds)

    # Build task list: (config, seed) pairs
    tasks = [(config, seed) for config in configs for seed in seeds]
    total = len(tasks)
    print(f"Running {total} tasks ({len(configs)} configs × {args.n_seeds} seeds)")

    start = time.time()

    if args.parallel > 1:
        with ProcessPoolExecutor(max_workers=args.parallel) as executor:
            futures = {executor.submit(run_seed, c, s): (c, s) for c, s in tasks}
            for i, future in enumerate(as_completed(futures), 1):
                config, seed = futures[future]
                try:
                    result = future.result()
                    print(f"[{i}/{total}] {config.name} seed={seed} "
                          f"({result.wall_time:.1f}s)")
                except Exception as e:
                    print(f"[{i}/{total}] FAILED {config.name} seed={seed}: {e}")
    else:
        for i, (config, seed) in enumerate(tasks, 1):
            result = run_seed(config, seed)
            print(f"[{i}/{total}] {config.name} seed={seed} ({result.wall_time:.1f}s)")

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
```

## Result Aggregation

```python
"""Aggregate per-seed results into summary statistics."""

from pathlib import Path

import numpy as np
import pandas as pd


def aggregate_results(results_dir: Path, output_path: Path | None = None) -> pd.DataFrame:
    """Aggregate all CSV results into mean ± std per (config, iteration).

    Expects CSV files with columns: iteration, seed, config, <metric_columns>.
    Produces: iteration, config, <metric>_mean, <metric>_std, n_seeds.
    """
    # Collect all CSVs
    csv_files = sorted(results_dir.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {results_dir}")

    df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

    # Identify metric columns (everything except iteration, seed, config, wall_time)
    meta_cols = {"iteration", "seed", "config", "wall_time"}
    metric_cols = [c for c in df.columns if c not in meta_cols]

    # Aggregate
    agg_dict = {col: ["mean", "std"] for col in metric_cols}
    agg_dict["seed"] = "nunique"

    grouped = df.groupby(["config", "iteration"]).agg(agg_dict)

    # Flatten column names
    grouped.columns = [
        f"{col}_{stat}" if col != "seed" else "n_seeds"
        for col, stat in grouped.columns
    ]
    grouped = grouped.reset_index()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        grouped.to_csv(output_path, index=False)
        print(f"Aggregated results written to {output_path}")

    return grouped
```

## Checkpointing

```python
"""Checkpoint support for long-running experiments."""

import json
from pathlib import Path


class Checkpoint:
    """Track completed (config, seed) pairs to allow resume."""

    def __init__(self, path: Path):
        self.path = path
        self.completed: set[tuple[str, int]] = set()
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            self.completed = {(d["config"], d["seed"]) for d in data}

    def is_done(self, config_name: str, seed: int) -> bool:
        return (config_name, seed) in self.completed

    def mark_done(self, config_name: str, seed: int) -> None:
        self.completed.add((config_name, seed))
        self._save()

    def _save(self) -> None:
        data = [{"config": c, "seed": s} for c, s in sorted(self.completed)]
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)


# Usage in runner:
# checkpoint = Checkpoint(args.output_dir / "checkpoint.json")
# tasks = [(c, s) for c, s in tasks if not checkpoint.is_done(c.name, s)]
# ... after each run:
# checkpoint.mark_done(config.name, seed)
```

## Config Hashing

Deterministic hash of experiment parameters for reproducibility tracking and deduplication.

```python
"""Config hash: SHA-256 fingerprint for experiment configs.

Use for:
- Verifying identical parameters across runs
- Deduplicating results
- Linking results to configs without storing the full config
"""

import hashlib
import json
from typing import Any


def compute_config_hash(params: dict) -> str:
    """Deterministic SHA-256 hash of a parameter dict (first 12 chars)."""
    def _normalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _normalize(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, (list, tuple)):
            return [_normalize(v) for v in obj]
        elif isinstance(obj, float):
            return round(obj, 10)
        return obj

    normalized = _normalize(params)
    json_str = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(json_str.encode()).hexdigest()[:12]


# Usage:
# hash_id = compute_config_hash(config.to_dict())
# run_dir = results_dir / f"{config.name}_{hash_id}"
```

## Dual Output Paths

Save to both a timestamped directory (immutable archive) and a "latest" symlink (quick access).

```python
"""Dual output: dated archive + latest symlink."""

from datetime import datetime
from pathlib import Path


def create_run_directory(base_dir: Path, name: str, config_hash: str) -> tuple[Path, Path]:
    """Create timestamped run dir and update 'latest' symlink.

    Returns: (dated_dir, latest_dir)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dated_dir = base_dir / name / f"{timestamp}_{config_hash}"
    dated_dir.mkdir(parents=True, exist_ok=True)

    latest_dir = base_dir / "latest" / name
    latest_dir.parent.mkdir(parents=True, exist_ok=True)
    if latest_dir.is_symlink():
        latest_dir.unlink()
    latest_dir.symlink_to(dated_dir)

    return dated_dir, latest_dir
```

## Baseline Implementations

Structure baselines with the same `Algorithm` interface for fair comparison:

```python
"""Baseline algorithms.

Each baseline implements the same Algorithm interface as the proposed method.
Register in config via algorithm="random_search" etc.
"""

import numpy as np
from <pkg_name>.algorithm import Algorithm, Oracle


class RandomSearch(Algorithm):
    """Uniform random search baseline."""

    def __init__(self, config, rng, oracle: Oracle):
        super().__init__(config, rng)
        self.oracle = oracle

    def initialize(self):
        pass  # No initialization needed

    def step(self, iteration: int) -> dict:
        x = self.rng.uniform(0, 1, size=self.config.dim)
        y = self.oracle.query(x)
        return {"y_observed": float(y)}


class LatinHypercube(Algorithm):
    """Latin hypercube sampling baseline (non-adaptive)."""

    def __init__(self, config, rng, oracle: Oracle):
        super().__init__(config, rng)
        self.oracle = oracle
        self.design = None
        self._idx = 0

    def initialize(self):
        from scipy.stats.qmc import LatinHypercube as LHS
        sampler = LHS(d=self.config.dim, seed=self.rng)
        self.design = sampler.random(n=self.config.budget)
        self._idx = 0

    def step(self, iteration: int) -> dict:
        x = self.design[self._idx]
        self._idx += 1
        y = self.oracle.query(x)
        return {"y_observed": float(y)}


# Algorithm registry for config-driven selection
ALGORITHM_REGISTRY = {
    # "proposed": ProposedAlgorithm,  # TODO: register your algorithm
    "random_search": RandomSearch,
    "latin_hypercube": LatinHypercube,
}


def make_algorithm(config, rng, oracle: Oracle) -> Algorithm:
    """Factory: create algorithm from config name."""
    cls = ALGORITHM_REGISTRY.get(config.algorithm)
    if cls is None:
        raise ValueError(
            f"Unknown algorithm '{config.algorithm}'. "
            f"Available: {list(ALGORITHM_REGISTRY.keys())}"
        )
    return cls(config, rng, oracle)
```

## CLI Entry Point

```python
"""CLI entry point with argparse (lightweight) or typer (rich).

For most computational projects, argparse is sufficient.
Use typer only if you need subcommands or rich output.
"""

# === argparse version (recommended for simplicity) ===

import argparse
from pathlib import Path


def cli():
    parser = argparse.ArgumentParser(
        description="Computational experiment runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python -m <pkg_name> run --config configs/default.yaml
  uv run python -m <pkg_name> run --sweep configs/sweep.yaml --parallel 4
  uv run python -m <pkg_name> aggregate --results-dir experiments/results
  uv run python -m <pkg_name> figures --results-dir experiments/results
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # run
    run_p = sub.add_parser("run", help="Run experiments")
    group = run_p.add_mutually_exclusive_group(required=True)
    group.add_argument("--config", type=Path)
    group.add_argument("--sweep", type=Path)
    run_p.add_argument("--n-seeds", type=int, default=20)
    run_p.add_argument("--master-seed", type=int, default=42)
    run_p.add_argument("--parallel", type=int, default=1)

    # aggregate
    agg_p = sub.add_parser("aggregate", help="Aggregate results")
    agg_p.add_argument("--results-dir", type=Path, required=True)
    agg_p.add_argument("--output", type=Path, default=None)

    # figures
    fig_p = sub.add_parser("figures", help="Generate publication figures")
    fig_p.add_argument("--results-dir", type=Path, required=True)
    fig_p.add_argument("--figures-dir", type=Path, default=Path("paper/figures"))

    args = parser.parse_args()

    if args.command == "run":
        from experiments.run_experiment import main as run_main
        run_main()  # TODO: pass args
    elif args.command == "aggregate":
        from scripts.aggregate_results import aggregate_results
        aggregate_results(args.results_dir, args.output)
    elif args.command == "figures":
        from scripts.make_all_figures import main as fig_main
        fig_main()  # TODO: pass args
```
