# Algorithm Templates

> Python skeleton code for common computational research patterns. Read during Phase 2.
> Each template has `# TODO:` markers where the researcher fills in domain-specific logic.

## Base Classes

```python
"""Abstract base classes for computational experiments."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np


class Algorithm(ABC):
    """Base class for algorithms under study.

    Subclass this for each method (proposed + baselines).
    All methods share the same interface, enabling fair comparison.
    """

    def __init__(self, config: Any, rng: np.random.Generator):
        self.config = config
        self.rng = rng
        self.history: list[dict] = []

    @abstractmethod
    def initialize(self) -> None:
        """Set up initial state (e.g., initial design, prior)."""
        ...

    @abstractmethod
    def step(self, iteration: int) -> dict:
        """Execute one iteration. Returns a dict of metrics for this step."""
        ...

    def run(self, budget: int) -> list[dict]:
        """Run the algorithm for `budget` iterations."""
        self.initialize()
        for t in range(budget):
            metrics = self.step(t)
            metrics["iteration"] = t
            self.history.append(metrics)
        return self.history


class Oracle(ABC):
    """Interface for the environment / objective function.

    Wraps the true function with optional noise, cost, and query counting.
    """

    def __init__(self, rng: np.random.Generator, noise_std: float = 0.0):
        self.rng = rng
        self.noise_std = noise_std
        self.n_queries = 0

    @abstractmethod
    def _evaluate(self, x: np.ndarray) -> float | np.ndarray:
        """True (noiseless) evaluation. Implement in subclass."""
        ...

    def query(self, x: np.ndarray) -> float | np.ndarray:
        """Query the oracle. Adds noise if configured."""
        self.n_queries += 1
        value = self._evaluate(x)
        if self.noise_std > 0:
            value = value + self.rng.normal(0, self.noise_std)
        return value

    @property
    def optimum(self) -> float | None:
        """Known optimum for convergence checks. Override if known."""
        return None


class Metric(ABC):
    """Base class for evaluation metrics.

    Metrics are computed from algorithm history and/or oracle state.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short name for CSV columns and plot labels."""
        ...

    @abstractmethod
    def compute(self, history: list[dict], oracle: Oracle) -> np.ndarray:
        """Compute metric value at each iteration. Returns array of length len(history)."""
        ...
```

## Optimization Loop (Bayesian Optimization / Sequential Design)

Pattern from QUIVER-MOBO: surrogate model → acquisition function → evaluate → update.

```python
"""Surrogate-based optimization loop.

Pattern: fit surrogate → optimize acquisition → evaluate → update model.
Complexity: O(budget * model_fit_cost) per run.
"""

import numpy as np
from <pkg_name>.algorithm import Algorithm, Oracle


class SurrogateOptimizer(Algorithm):
    """Sequential surrogate-based optimizer.

    # TODO: Replace placeholder surrogate and acquisition with your model.
    """

    def __init__(self, config, rng, oracle: Oracle):
        super().__init__(config, rng)
        self.oracle = oracle
        self.X_observed = []  # TODO: adjust types
        self.Y_observed = []
        self.surrogate = None  # TODO: initialize surrogate model

    def initialize(self):
        """Generate initial design and evaluate."""
        n_init = self.config.n_initial  # TODO: add to config
        dim = self.config.dim  # TODO: add to config

        # Latin hypercube or random initial design
        X_init = self.rng.uniform(0, 1, size=(n_init, dim))
        Y_init = np.array([self.oracle.query(x) for x in X_init])

        self.X_observed = list(X_init)
        self.Y_observed = list(Y_init)
        self._fit_surrogate()

    def step(self, iteration: int) -> dict:
        """One BO iteration: acquire → evaluate → update."""
        # 1. Optimize acquisition function
        x_next = self._optimize_acquisition()

        # 2. Evaluate oracle
        y_next = self.oracle.query(x_next)

        # 3. Update observations
        self.X_observed.append(x_next)
        self.Y_observed.append(y_next)

        # 4. Re-fit surrogate
        self._fit_surrogate()

        return {
            "y_observed": float(y_next),
            "best_so_far": float(min(self.Y_observed)),  # TODO: max for maximization
            "n_queries": self.oracle.n_queries,
        }

    def _fit_surrogate(self):
        """Fit surrogate model to observed data."""
        # TODO: fit GP, random forest, neural net, etc.
        # self.surrogate.fit(np.array(self.X_observed), np.array(self.Y_observed))
        pass

    def _optimize_acquisition(self) -> np.ndarray:
        """Find the next query point by optimizing the acquisition function."""
        # TODO: implement acquisition optimization (EI, UCB, Thompson, etc.)
        # Placeholder: random point
        return self.rng.uniform(0, 1, size=self.config.dim)
```

## Inference Engine (Particle-Based)

Pattern from IAPE: particle posterior → importance sampling → resampling.

```python
"""Particle-based inference engine.

Pattern: initialize particles → compute weights → resample → iterate.
Complexity: O(n_particles * n_iterations) per run.
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class InferenceResult:
    """Structured output from inference run."""
    posterior_mean: np.ndarray
    posterior_std: np.ndarray
    particles: np.ndarray
    weights: np.ndarray
    ess_history: list[float]  # Effective sample size over iterations
    # TODO: add domain-specific fields


class ParticleInference:
    """Sequential Monte Carlo / importance sampling inference.

    # TODO: Replace likelihood and prior with your model.
    """

    def __init__(self, config, rng: np.random.Generator):
        self.config = config
        self.rng = rng
        self.n_particles = config.n_particles  # TODO: add to config
        self.particles = None
        self.weights = None

    def initialize(self):
        """Draw particles from prior."""
        # TODO: sample from your prior distribution
        # self.particles = self.rng.normal(0, 1, size=(self.n_particles, self.config.dim))
        self.weights = np.ones(self.n_particles) / self.n_particles

    def update(self, observation) -> None:
        """Update posterior given new observation."""
        # 1. Compute likelihood weights
        log_likelihoods = self._log_likelihood(self.particles, observation)

        # 2. Update weights (log-space for stability)
        log_weights = np.log(self.weights) + log_likelihoods
        log_weights -= np.max(log_weights)  # shift for numerical stability
        self.weights = np.exp(log_weights)
        self.weights /= self.weights.sum()

        # 3. Resample if ESS too low
        ess = 1.0 / np.sum(self.weights ** 2)
        if ess < self.n_particles / 2:
            self._resample()

    def _log_likelihood(self, particles: np.ndarray, observation) -> np.ndarray:
        """Compute log-likelihood of observation for each particle.

        # TODO: implement your likelihood model.
        """
        # Placeholder: uniform likelihood
        return np.zeros(len(particles))

    def _resample(self):
        """Systematic resampling."""
        cumsum = np.cumsum(self.weights)
        u = (self.rng.uniform() + np.arange(self.n_particles)) / self.n_particles
        indices = np.searchsorted(cumsum, u)
        self.particles = self.particles[indices]
        self.weights = np.ones(self.n_particles) / self.n_particles

    @property
    def posterior_mean(self) -> np.ndarray:
        return np.average(self.particles, weights=self.weights, axis=0)

    @property
    def posterior_std(self) -> np.ndarray:
        mean = self.posterior_mean
        var = np.average((self.particles - mean) ** 2, weights=self.weights, axis=0)
        return np.sqrt(var)

    def result(self) -> InferenceResult:
        return InferenceResult(
            posterior_mean=self.posterior_mean,
            posterior_std=self.posterior_std,
            particles=self.particles.copy(),
            weights=self.weights.copy(),
            ess_history=[],  # TODO: collect during run
        )
```

## Simulation Runner

Pattern shared by both QUIVER and IAPE: config → initialize → loop → collect → aggregate.

```python
"""Simulation runner: config-driven experiment execution.

Pattern: load config → for each seed: initialize → run → save → aggregate.
"""

import time
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class RunResult:
    """Structured output from a single run.

    # TODO: add domain-specific fields.
    """
    seed: int
    config_name: str
    wall_time: float
    metrics: dict  # metric_name -> array over iterations


def run_single(config, seed: int) -> RunResult:
    """Execute a single experiment run.

    # TODO: replace with your algorithm + oracle setup.
    """
    rng = np.random.default_rng(seed)
    start = time.time()

    # 1. Initialize
    # oracle = YourOracle(config, rng)
    # algo = YourAlgorithm(config, rng, oracle)

    # 2. Run
    # history = algo.run(config.budget)

    # 3. Compute metrics
    # metrics = {}
    # for metric in [SimpleRegret(), LogRegret()]:
    #     metrics[metric.name] = metric.compute(history, oracle)

    wall_time = time.time() - start

    return RunResult(
        seed=seed,
        config_name=config.name,
        wall_time=wall_time,
        metrics={},  # TODO: fill from computed metrics
    )


def save_result(result: RunResult, output_dir: Path) -> Path:
    """Save a single run result to CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{result.config_name}_seed{result.seed}.csv"

    # Build DataFrame from metrics
    data = {"iteration": range(len(next(iter(result.metrics.values()))))}
    data.update(result.metrics)
    df = pd.DataFrame(data)
    df["seed"] = result.seed
    df["config"] = result.config_name
    df["wall_time"] = result.wall_time

    df.to_csv(path, index=False)
    return path
```

## Metrics Module

```python
"""Standard metrics for computational experiments.

Each metric takes algorithm history and returns a value per iteration.
"""

import numpy as np
from <pkg_name>.algorithm import Metric, Oracle


class SimpleRegret(Metric):
    """Gap between best found and true optimum."""

    @property
    def name(self) -> str:
        return "simple_regret"

    def compute(self, history: list[dict], oracle: Oracle) -> np.ndarray:
        if oracle.optimum is None:
            raise ValueError("Oracle must define optimum for regret computation")
        best_so_far = np.minimum.accumulate([h["y_observed"] for h in history])
        return best_so_far - oracle.optimum  # TODO: adjust sign for maximization


class CumulativeRegret(Metric):
    """Sum of instantaneous regrets."""

    @property
    def name(self) -> str:
        return "cumulative_regret"

    def compute(self, history: list[dict], oracle: Oracle) -> np.ndarray:
        if oracle.optimum is None:
            raise ValueError("Oracle must define optimum for regret computation")
        instant = np.array([h["y_observed"] for h in history]) - oracle.optimum
        return np.cumsum(instant)


class LogRegret(Metric):
    """Log10 of simple regret (for convergence plots)."""

    @property
    def name(self) -> str:
        return "log_regret"

    def compute(self, history: list[dict], oracle: Oracle) -> np.ndarray:
        sr = SimpleRegret().compute(history, oracle)
        return np.log10(np.maximum(sr, 1e-16))


class RankCorrelation(Metric):
    """Spearman rank correlation between predicted and true rankings.

    Useful for surrogate model quality evaluation.
    """

    @property
    def name(self) -> str:
        return "rank_correlation"

    def compute(self, history: list[dict], oracle: Oracle) -> np.ndarray:
        from scipy.stats import spearmanr

        # TODO: requires predicted values in history
        # correlations = []
        # for h in history:
        #     if "predicted" in h and "true" in h:
        #         corr, _ = spearmanr(h["predicted"], h["true"])
        #         correlations.append(corr)
        # return np.array(correlations)
        raise NotImplementedError("Add 'predicted' and 'true' fields to history")


class TopKAccuracy(Metric):
    """Fraction of true top-k items found in predicted top-k.

    # TODO: set k via config or constructor.
    """

    def __init__(self, k: int = 5):
        self.k = k

    @property
    def name(self) -> str:
        return f"top{self.k}_accuracy"

    def compute(self, history: list[dict], oracle: Oracle) -> np.ndarray:
        # TODO: implement based on your ranking/selection task
        raise NotImplementedError
```

## Multi-Agent Simulation

Pattern from Lopez-Lira's LLM Trading Simulation: heterogeneous agents interacting through a shared environment with optional memory and messaging.

```python
"""Multi-agent simulation base classes.

Pattern: BaseAgent (state + decide) + Environment (state + process) + Simulation (orchestrate).
Unlike Algorithm+Oracle (single agent), this handles N interacting agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np


class BaseAgent(ABC):
    """Agent with persistent state across rounds.

    Tracks: positions, action history, payments, optional memory.
    """

    def __init__(self, agent_id: int, agent_type: Any, rng: np.random.Generator):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.rng = rng
        self.action_history: list[dict] = []
        self.outcome_history: list[dict] = []
        self.memory_notes: list[tuple[int, str]] = []  # (round, note)
        # TODO: add domain-specific state (wealth, positions, etc.)

    @abstractmethod
    def decide(self, observation: dict, round_num: int) -> dict:
        """Choose an action given current observation.

        observation: what the agent sees (environment state, messages, etc.)
        Returns: action dict (domain-specific: orders, bids, choices, etc.)
        """
        ...

    def receive_outcome(self, outcome: dict, round_num: int) -> None:
        """Process the result of the agent's action."""
        self.outcome_history.append({"round": round_num, **outcome})

    def add_memory(self, round_num: int, note: str, limit: int = 10) -> None:
        """Store a memory note (if memory feature is enabled)."""
        self.memory_notes.append((round_num, note))
        if len(self.memory_notes) > limit:
            self.memory_notes = self.memory_notes[-limit:]

    def compose_message(self, round_num: int) -> str | None:
        """Compose a broadcast message (if social feature is enabled).

        Override in subclass. Return None to skip.
        """
        return None

    @property
    def wealth(self) -> float:
        """Current total wealth. Override with domain-specific calculation."""
        return 0.0


class Environment(ABC):
    """Shared environment that agents interact with.

    Maintains persistent state (order book, resource pool, etc.).
    Processes agent actions and produces outcomes.
    """

    @abstractmethod
    def get_state(self) -> dict:
        """Return current environment state visible to agents."""
        ...

    @abstractmethod
    def process_actions(self, actions: dict[int, dict], round_num: int) -> dict[int, dict]:
        """Process all agent actions and return per-agent outcomes.

        actions: {agent_id: action_dict}
        Returns: {agent_id: outcome_dict}
        """
        ...

    @abstractmethod
    def update(self, round_num: int) -> None:
        """Update environment state between rounds (dividends, decay, etc.)."""
        ...
```

For the full multi-agent patterns (composition, messaging, metrics, visualization), see [`multi-agent-patterns.md`](multi-agent-patterns.md).

## Seed Management

```python
"""Deterministic seed management.

All stochastic operations use np.random.default_rng(seed).
Never use np.random.seed() or global random state.
"""

import numpy as np


def make_rng(seed: int) -> np.random.Generator:
    """Create a new RNG from a seed. Use this everywhere."""
    return np.random.default_rng(seed)


def seed_sequence(master_seed: int, n: int) -> list[int]:
    """Generate n independent seeds from a master seed.

    Uses SeedSequence for proper statistical independence.
    """
    ss = np.random.SeedSequence(master_seed)
    child_seeds = ss.spawn(n)
    return [cs.generate_state(1)[0] for cs in child_seeds]


# Usage:
# seeds = seed_sequence(master_seed=42, n=config.n_seeds)
# results = [run_single(config, seed=s) for s in seeds]
```
