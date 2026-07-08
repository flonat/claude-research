# Multi-Agent Simulation Patterns — Core

> Patterns for multi-agent simulations where heterogeneous agents interact through a shared environment. Read during Phase 2–3 when the experiment involves multiple interacting agents.
>
> Adapted from Lopez-Lira's LLM trading simulation architecture.
>
> Infrastructure patterns (feature toggles, config hashing, simulation runner, visualization): [`multi-agent-infrastructure.md`](multi-agent-infrastructure.md)

## When to Use These Patterns

- Agents interact with each other (not just with an oracle/environment independently)
- Agent populations are heterogeneous (different types, capabilities, strategies)
- Emergent behavior is the object of study (not just individual agent performance)
- The environment has persistent state that agents collectively modify (order book, resource pool, shared space)

## Agent Composition

Define agent populations declaratively. Separate agent *type* (behavior) from agent *instance* (state).

```python
"""Agent composition: define heterogeneous populations.

Pattern: AgentType (blueprint) → AgentComposition (population spec) → instantiate().
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class Feature(Enum):
    """Optional capabilities that can be toggled per agent type.

    Use for ablation studies: same scenario with/without memory, messaging, etc.
    """
    MEMORY = auto()          # Agent remembers past rounds
    SOCIAL = auto()          # Agent can send/receive messages
    SELF_MODIFY = auto()     # Agent can update its own strategy
    LAST_REASONING = auto()  # Agent sees its previous reasoning


@dataclass(frozen=True)
class AgentType:
    """Blueprint for a class of agents.

    name: human-readable label (e.g., "value_investor", "momentum_trader")
    type_id: unique identifier for registry lookup
    system_prompt: personality/role description (for LLM agents)
    enabled_features: which optional capabilities this type has
    params: type-specific parameters (e.g., risk_aversion, memory_length)
    """
    name: str
    type_id: str
    system_prompt: str = ""
    enabled_features: frozenset[Feature] = frozenset()
    params: dict = field(default_factory=dict)


@dataclass
class AgentComposition:
    """Population specification: how many of each type.

    Use named presets or custom distributions.
    """
    types: list[AgentType]
    counts: list[int]  # parallel to types

    @property
    def total(self) -> int:
        return sum(self.counts)

    def instantiate(self, base_agent_cls, rng) -> list:
        """Create agent instances from composition spec."""
        agents = []
        agent_id = 0
        for agent_type, count in zip(self.types, self.counts):
            for _ in range(count):
                agent = base_agent_cls(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    rng=rng,
                )
                agents.append(agent)
                agent_id += 1
        return agents


# --- Preset compositions ---

def uniform_composition(types: list[AgentType], total: int) -> AgentComposition:
    """Equal distribution across all types."""
    per_type = total // len(types)
    remainder = total % len(types)
    counts = [per_type + (1 if i < remainder else 0) for i in range(len(types))]
    return AgentComposition(types=types, counts=counts)


def weighted_composition(
    types: list[AgentType], weights: list[float], total: int
) -> AgentComposition:
    """Proportional distribution. weights are normalized automatically."""
    import numpy as np
    w = np.array(weights) / sum(weights)
    counts = np.round(w * total).astype(int)
    # Adjust for rounding errors
    diff = total - counts.sum()
    for i in range(abs(diff)):
        counts[i % len(counts)] += 1 if diff > 0 else -1
    return AgentComposition(types=types, counts=counts.tolist())
```

## Messaging Service

Simple broadcast channel for inter-agent communication. Opt-in via Feature.SOCIAL.

```python
"""Inter-agent messaging service.

Pattern: singleton broadcast channel, round-indexed, agents opt in via feature flag.
"""

from collections import defaultdict


class MessagingService:
    """Round-based broadcast messaging between agents.

    Messages are visible to all agents with SOCIAL enabled.
    No private channels — extend if needed for targeted communication.
    """

    def __init__(self):
        self._messages: dict[int, list[dict]] = defaultdict(list)

    def send(self, round_num: int, agent_id: int, message: str) -> None:
        """Broadcast a message from an agent."""
        self._messages[round_num].append({
            "agent_id": agent_id,
            "message": message,
        })

    def get_round_messages(self, round_num: int) -> list[dict]:
        """Get all messages from a specific round."""
        return self._messages.get(round_num, [])

    def get_history(self, up_to_round: int) -> list[dict]:
        """Get all messages up to (inclusive) a given round."""
        all_msgs = []
        for r in range(1, up_to_round + 1):
            for msg in self._messages.get(r, []):
                all_msgs.append({"round": r, **msg})
        return all_msgs

    def reset(self) -> None:
        """Clear all messages (for simulation reset)."""
        self._messages.clear()


# --- Extensions (implement as needed) ---

class TopicMessagingService(MessagingService):
    """Extension: topic-based channels (e.g., #market, #strategy).

    # TODO: implement if private/topic-scoped messaging is needed.
    """
    pass
```

## Multi-Level Evaluation Metrics

Agent-level + system-level + emergent metrics. The key insight: in multi-agent systems, individual performance alone is insufficient — you need metrics at multiple levels of analysis.

```python
"""Multi-level metrics for multi-agent simulations.

Three levels:
1. Agent-level: individual performance (wealth, accuracy, utility)
2. System-level: aggregate outcomes (efficiency, volume, inequality)
3. Emergent-level: patterns that arise from interaction (herding, bubbles, convergence)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np


class AgentMetric(ABC):
    """Metric computed per agent per round."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def compute(self, agent, round_num: int) -> float: ...


class SystemMetric(ABC):
    """Metric computed for the whole system per round."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def compute(self, agents: list, environment: Any, round_num: int) -> float: ...


class EmergentMetric(ABC):
    """Metric computed over the full history (post-hoc).

    These capture patterns that only become visible across time:
    convergence rates, regime changes, herding episodes.
    """

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def compute(self, history: list[dict]) -> dict:
        """Returns a dict of summary statistics, not per-round values."""
        ...


# --- Example metrics (adapt to domain) ---

class GiniCoefficient(SystemMetric):
    """Wealth inequality across agents."""

    @property
    def name(self) -> str:
        return "gini"

    def compute(self, agents, environment, round_num) -> float:
        values = np.array([a.wealth for a in agents])
        if values.sum() == 0:
            return 0.0
        sorted_v = np.sort(values)
        n = len(sorted_v)
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * sorted_v) / (n * np.sum(sorted_v))) - (n + 1) / n


class TypePerformanceGap(SystemMetric):
    """Performance difference between agent types.

    Useful for studying whether heterogeneity matters.
    """

    @property
    def name(self) -> str:
        return "type_performance_gap"

    def compute(self, agents, environment, round_num) -> float:
        from collections import defaultdict
        by_type = defaultdict(list)
        for a in agents:
            by_type[a.agent_type.type_id].append(a.wealth)
        means = [np.mean(v) for v in by_type.values()]
        return max(means) - min(means) if len(means) > 1 else 0.0


class HerdingIndex(EmergentMetric):
    """Measure of action correlation across agents over time.

    High herding = agents making the same decisions simultaneously.
    """

    @property
    def name(self) -> str:
        return "herding_index"

    def compute(self, history: list[dict]) -> dict:
        # TODO: implement based on action correlation
        # e.g., fraction of agents taking the same action per round
        return {"mean_herding": 0.0, "max_herding": 0.0, "herding_episodes": 0}
```
