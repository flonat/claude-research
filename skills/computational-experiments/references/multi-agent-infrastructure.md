# Multi-Agent Simulation Patterns — Infrastructure

> Infrastructure patterns for multi-agent simulations: feature toggles, config hashing, output management, simulation runner, and visualization.
>
> Core patterns (agent composition, messaging, metrics): [`multi-agent-patterns.md`](multi-agent-patterns.md)

## Feature Toggle System

Gate agent capabilities for cost control and ablation studies.

```python
"""Feature toggle pattern for agent capabilities.

Use for:
- Cost control: LLM calls with memory are more expensive
- Ablation studies: same scenario with/without a capability
- Progressive complexity: start simple, add features incrementally
"""

from dataclasses import dataclass, field


@dataclass
class FeatureConfig:
    """Which features are enabled for a simulation run.

    Use in experiment configs to define ablation conditions.
    """
    memory: bool = False
    memory_limit: int = 10          # Max memory entries per agent
    social: bool = False
    social_history_depth: int = 1   # How many past rounds of messages to show
    self_modify: bool = False
    last_reasoning: bool = False

    def to_feature_set(self) -> frozenset:
        """Convert to Feature enum set for AgentType."""
        features = set()
        if self.memory:
            features.add(Feature.MEMORY)
        if self.social:
            features.add(Feature.SOCIAL)
        if self.self_modify:
            features.add(Feature.SELF_MODIFY)
        if self.last_reasoning:
            features.add(Feature.LAST_REASONING)
        return frozenset(features)


# --- Ablation experiment generator ---

def ablation_configs(base_config, features_to_ablate: list[str]) -> list:
    """Generate configs for feature ablation study.

    Returns: list of (label, config) tuples.
    - "all_features": everything enabled
    - "no_<feature>": one feature disabled at a time
    - "baseline": all features disabled

    Usage:
        conditions = ablation_configs(base, ["memory", "social"])
        # Returns: [("all_features", ...), ("no_memory", ...), ("no_social", ...), ("baseline", ...)]
    """
    from dataclasses import replace

    conditions = []

    # Full model
    conditions.append(("all_features", base_config))

    # Ablate one at a time
    for feat in features_to_ablate:
        ablated = replace(base_config, **{feat: False})
        conditions.append((f"no_{feat}", ablated))

    # Baseline (all disabled)
    overrides = {feat: False for feat in features_to_ablate}
    conditions.append(("baseline", replace(base_config, **overrides)))

    return conditions
```

## Config Hashing for Reproducibility

Deterministic hash of experiment configuration for tracking and deduplication.

```python
"""Config hashing: SHA-256 fingerprint of experiment parameters.

Use for:
- Verifying two runs used identical parameters
- Deduplicating results across runs
- Linking results back to their config without storing the full config
"""

import hashlib
import json
from typing import Any


def compute_config_hash(params: dict) -> str:
    """Compute deterministic SHA-256 hash of a parameter dict.

    Handles nested dicts, lists, and basic types.
    Sorts keys for determinism.
    """
    def _normalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _normalize(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, (list, tuple)):
            return [_normalize(v) for v in obj]
        elif isinstance(obj, float):
            return round(obj, 10)  # Avoid float precision issues
        return obj

    normalized = _normalize(params)
    json_str = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(json_str.encode()).hexdigest()[:12]


# Usage in experiment runner:
# config_hash = compute_config_hash(config.to_dict())
# run_dir = results_dir / f"{config.name}_{config_hash}"
```

## Dual Output Paths

Save results to both a dated archive (immutable) and a "latest" symlink (overwritten each run).

```python
"""Dual output: dated archive + latest symlink.

Pattern from Lopez-Lira: every run saves to a timestamped directory
AND overwrites a 'latest' directory for quick access.

Benefits:
- Dated: complete audit trail, never overwritten
- Latest: always points to most recent run for quick iteration
"""

from datetime import datetime
from pathlib import Path
import shutil


def create_run_directory(
    base_dir: Path,
    scenario_name: str,
    config_hash: str,
) -> tuple[Path, Path]:
    """Create dated run directory and update 'latest' symlink.

    Returns: (dated_dir, latest_dir)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dated_dir = base_dir / scenario_name / f"{timestamp}_{config_hash}"
    dated_dir.mkdir(parents=True, exist_ok=True)

    # Update 'latest' symlink
    latest_dir = base_dir / "latest" / scenario_name
    latest_dir.parent.mkdir(parents=True, exist_ok=True)
    if latest_dir.is_symlink() or latest_dir.exists():
        if latest_dir.is_symlink():
            latest_dir.unlink()
        else:
            shutil.rmtree(latest_dir)
    latest_dir.symlink_to(dated_dir)

    return dated_dir, latest_dir


# Usage:
# dated, latest = create_run_directory(Path("results"), "baseline_vs_memory", "a1b2c3d4")
# Save results to `dated` — they'll also be accessible via `latest`
```

## Multi-Agent Simulation Runner

Orchestrates agents, environment, messaging, and metrics across rounds.

```python
"""Multi-agent simulation runner.

Pattern: Environment mediates all agent-environment interactions.
Agents submit actions → Environment processes → Environment returns observations.
Messaging happens between action and observation phases.

Round lifecycle:
1. Environment broadcasts state to all agents
2. Agents decide actions (potentially using memory + messages)
3. Environment processes actions (matching, allocation, etc.)
4. Agents receive outcomes
5. Messaging phase (agents broadcast observations/opinions)
6. Metrics recorded
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class SimulationConfig:
    """Complete simulation specification.

    # TODO: Replace with domain-specific parameters.
    """
    # --- Core ---
    name: str = "default"
    n_rounds: int = 100
    n_agents: int = 10
    seed: int = 42

    # --- Agent composition ---
    composition: str = "uniform"  # or "weighted", custom dict

    # --- Features ---
    features: dict = field(default_factory=lambda: {
        "memory": False,
        "social": False,
    })

    # --- Environment ---
    # TODO: add domain-specific environment parameters

    # --- Output ---
    output_dir: Path = Path("results")


class MultiAgentSimulation:
    """Main simulation loop for multi-agent experiments.

    Subclass and implement:
    - _create_environment(): domain-specific environment
    - _create_agents(): agent population from composition spec
    - _get_agent_observation(): what each agent sees
    - _process_actions(): how the environment handles agent actions
    - _get_agent_outcome(): what each agent receives after processing
    """

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.messaging = MessagingService()
        self.history: list[dict] = []
        self.agents = []
        self.environment = None

    def setup(self) -> None:
        """Initialize environment and agents."""
        self.environment = self._create_environment()
        self.agents = self._create_agents()

    def run(self) -> list[dict]:
        """Execute full simulation."""
        self.setup()

        for round_num in range(1, self.config.n_rounds + 1):
            round_data = self._run_round(round_num)
            self.history.append(round_data)

            if round_num % 10 == 0:
                print(f"  Round {round_num}/{self.config.n_rounds}")

        return self.history

    def _run_round(self, round_num: int) -> dict:
        """Execute one round of the simulation."""
        round_data = {"round": round_num}

        # 1. Broadcast state
        state = self.environment.get_state()

        # 2. Collect agent actions
        actions = {}
        for agent in self.agents:
            obs = self._get_agent_observation(agent, state, round_num)
            action = agent.decide(obs, round_num)
            actions[agent.agent_id] = action

        # 3. Process actions through environment
        outcomes = self._process_actions(actions, round_num)

        # 4. Distribute outcomes to agents
        for agent in self.agents:
            outcome = outcomes.get(agent.agent_id, {})
            agent.receive_outcome(outcome, round_num)

        # 5. Messaging phase
        if self.config.features.get("social", False):
            for agent in self.agents:
                if Feature.SOCIAL in agent.agent_type.enabled_features:
                    msg = agent.compose_message(round_num)
                    if msg:
                        self.messaging.send(round_num, agent.agent_id, msg)

        # 6. Record metrics
        round_data["state"] = state
        round_data["actions"] = actions
        round_data["outcomes"] = outcomes

        return round_data

    # --- Override these in subclass ---

    def _create_environment(self):
        raise NotImplementedError

    def _create_agents(self) -> list:
        raise NotImplementedError

    def _get_agent_observation(self, agent, state, round_num) -> dict:
        raise NotImplementedError

    def _process_actions(self, actions: dict, round_num: int) -> dict:
        raise NotImplementedError
```

## Visualization Orchestrator

Modular plot generation with category-based organization.

```python
"""Modular visualization for multi-agent simulations.

Pattern: PlotOrchestrator delegates to category-specific plot generators.
Each category produces a set of related plots.

Categories (adapt to domain):
1. Agent plots: per-agent performance over time
2. System plots: aggregate outcomes
3. Interaction plots: communication patterns, action correlations
4. Decision plots: reasoning analysis (for LLM agents)
"""

from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np


class PlotOrchestrator:
    """Generate all plots for a simulation run.

    Register plot functions by category. Each function takes
    (history, agents, output_dir) and saves its own files.
    """

    def __init__(self, history: list[dict], agents: list, output_dir: Path):
        self.history = history
        self.agents = agents
        self.output_dir = output_dir
        self._categories: dict[str, list[Callable]] = {}

    def register(self, category: str, plot_fn: Callable) -> None:
        """Register a plot function under a category."""
        self._categories.setdefault(category, []).append(plot_fn)

    def generate_all(self) -> dict[str, list[Path]]:
        """Generate all registered plots. Returns {category: [paths]}."""
        results = {}
        for category, fns in self._categories.items():
            cat_dir = self.output_dir / category
            cat_dir.mkdir(parents=True, exist_ok=True)
            paths = []
            for fn in fns:
                try:
                    path = fn(self.history, self.agents, cat_dir)
                    if path:
                        paths.append(path)
                except Exception as e:
                    print(f"  Warning: {fn.__name__} failed: {e}")
            results[category] = paths
            print(f"  {category}: {len(paths)} plots")
        return results


# --- Example plot functions ---

def plot_agent_wealth(history, agents, output_dir) -> Path:
    """Wealth over time, colored by agent type."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for agent in agents:
        wealth = [h["outcomes"].get(agent.agent_id, {}).get("wealth", 0)
                  for h in history]
        ax.plot(wealth, alpha=0.5, label=agent.agent_type.name)

    ax.set_xlabel("Round")
    ax.set_ylabel("Wealth")
    ax.set_title("Agent Wealth Over Time")
    # Deduplicate legend entries
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())

    path = output_dir / "wealth_over_time.pdf"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_type_comparison(history, agents, output_dir) -> Path:
    """Box plot of final wealth by agent type."""
    from collections import defaultdict

    by_type = defaultdict(list)
    final = history[-1]
    for agent in agents:
        wealth = final["outcomes"].get(agent.agent_id, {}).get("wealth", 0)
        by_type[agent.agent_type.name].append(wealth)

    fig, ax = plt.subplots(figsize=(8, 5))
    labels = sorted(by_type.keys())
    data = [by_type[l] for l in labels]
    ax.boxplot(data, labels=labels)
    ax.set_ylabel("Final Wealth")
    ax.set_title("Performance by Agent Type")

    path = output_dir / "type_comparison.pdf"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path
```

## Cross-References

| Pattern | Source in Lopez-Lira | Adaptation target |
|---------|---------------------|-------------------|
| Agent composition | `src/agents/agent_types.py` | Multi-agent scaffold (Phase 2) |
| Feature toggles | `src/agents/base_agent.py` | Ablation config (Phase 3) |
| Messaging | `src/services/messaging_service.py` | Inter-agent communication |
| Config hashing | `src/scenarios/base.py` | Reproducibility tracking |
| Dual output | `src/run_base_sim.py` | Result management |
| Plot orchestrator | `src/visualization/plot_generator.py` | Publication output (Phase 4) |
| Multi-level metrics | Agent/trading/price/decision plots | Evaluation framework |
