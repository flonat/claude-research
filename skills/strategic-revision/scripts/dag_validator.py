#!/usr/bin/env python3
"""
Generic DAG Validator for Revision Master Plans

Validates task dependencies, computes execution schedules, identifies
critical paths and bottlenecks using NetworkX graph algorithms.

Usage:
    python dag_validator.py <tasks_json_file> [--output <output_json>]
    python dag_validator.py revision_tasks.json
    python dag_validator.py revision_tasks.json --validate-only
    python dag_validator.py revision_tasks.json --quiet
    python dag_validator.py revision_tasks.json --task A1_size_control

Input format: See task-schema.md in the skill references.
"""

import sys
import json
import argparse
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

try:
    import networkx as nx
except ImportError:
    logging.error("networkx is not installed. Install with: pip install networkx")
    sys.exit(1)

logger = logging.getLogger(__name__)


# ======================================================================
# Data structures
# ======================================================================

@dataclass
class ValidationResult:
    is_acyclic: bool
    cycles: List[List[Dict[str, str]]]
    warnings: List[str]


@dataclass
class BottleneckInfo:
    task_id: str
    direct_dependents: int
    total_downstream: int
    in_degree: int
    description: str


@dataclass
class TaskAnalysis:
    task_id: str
    info: Dict
    direct_prerequisites: List[str]
    direct_dependents: List[str]
    all_prerequisites: List[str]
    all_dependents: List[str]
    in_degree: int
    out_degree: int


# ======================================================================
# I/O
# ======================================================================

def load_tasks(filepath: str) -> Dict[str, Dict]:
    """Load tasks from a JSON file.

    Accepts two formats:
      - Flat dict:  {"task_id": {...}, ...}
      - Wrapped:    {"tasks": {"task_id": {...}, ...}}
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "tasks" in data and isinstance(data["tasks"], dict):
        return data["tasks"]
    return data


# ======================================================================
# Console formatting utilities
# ======================================================================

def _divider(title: str, width: int = 72) -> str:
    return f"\n{'=' * width}\n  {title}\n{'=' * width}"


def _section(title: str, width: int = 72) -> str:
    return f"\n--- {title} {'-' * max(0, width - len(title) - 5)}"


# ======================================================================
# Validator
# ======================================================================

class RevisionDAGValidator:
    """Validate and analyze a revision master plan DAG."""

    def __init__(self, tasks: Dict[str, Dict]):
        self.tasks = tasks
        self.G = nx.DiGraph()
        self._warnings: List[str] = []
        self._build_graph()

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def _build_graph(self):
        """Build the directed graph from task definitions."""
        # Add all nodes with attributes in one pass
        self.G.add_nodes_from(
            (tid, {
                "category": info.get("category", "UNKNOWN"),
                "block": info.get("block", "?"),
                "description": info.get("description", ""),
            })
            for tid, info in self.tasks.items()
        )

        # Add edges and collateral risks
        for task_id, info in self.tasks.items():
            for prereq in info.get("depends_on", []):
                if prereq in self.tasks:
                    self.G.add_edge(prereq, task_id)
                else:
                    msg = (
                        f"Task '{task_id}' depends on '{prereq}', "
                        f"which is not defined in the task set"
                    )
                    logger.warning(msg)
                    self._warnings.append(msg)

            # Collateral risks stored as node attributes — not structural
            # edges — so they do not affect cycle detection or sorting.
            for risk in info.get("collateral_risks", []):
                self.G.nodes[task_id].setdefault("risk_affects", []).append(risk)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> ValidationResult:
        """Check for circular dependencies."""
        cycles: List[List[Dict[str, str]]] = []
        is_acyclic = nx.is_directed_acyclic_graph(self.G)
        if not is_acyclic:
            try:
                raw = nx.find_cycle(self.G)
                cycles.append([{"from": e[0], "to": e[1]} for e in raw])
            except nx.NetworkXNoCycle:
                pass
        return ValidationResult(
            is_acyclic=is_acyclic,
            cycles=cycles,
            warnings=list(self._warnings),
        )

    # ------------------------------------------------------------------
    # Execution scheduling
    # ------------------------------------------------------------------

    def get_execution_order(self) -> List[str]:
        """Topologically sorted task sequence (sequential fallback)."""
        return list(nx.topological_sort(self.G))

    def get_parallel_batches(self) -> List[List[str]]:
        """Groups of tasks that can execute simultaneously."""
        return [sorted(batch) for batch in nx.topological_generations(self.G)]

    # ------------------------------------------------------------------
    # Critical path and bottlenecks
    # ------------------------------------------------------------------

    def get_critical_path(self) -> List[str]:
        """Longest dependency chain (determines minimum revision time)."""
        return nx.dag_longest_path(self.G)

    def get_bottlenecks(self, min_out_degree: int = 2) -> List[BottleneckInfo]:
        """Tasks with high downstream impact, sorted by total descendants."""
        results = []
        for t in self.G.nodes():
            out_deg = self.G.out_degree(t)
            if out_deg >= min_out_degree:
                results.append(BottleneckInfo(
                    task_id=t,
                    direct_dependents=out_deg,
                    total_downstream=len(nx.descendants(self.G, t)),
                    in_degree=self.G.in_degree(t),
                    description=self.tasks[t].get("description", ""),
                ))
        results.sort(key=lambda b: b.total_downstream, reverse=True)
        return results

    # ------------------------------------------------------------------
    # Block-level analysis
    # ------------------------------------------------------------------

    def get_block_analysis(self) -> Dict[str, Dict]:
        """Analyze each execution block."""
        blocks: Dict[str, List[str]] = {}
        for task_id, info in self.tasks.items():
            blocks.setdefault(info.get("block", "?"), []).append(task_id)

        result = {}
        for block_id, tasks in sorted(blocks.items()):
            block_set = set(tasks)
            external_deps = {
                t: [p for p in self.G.predecessors(t) if p not in block_set]
                for t in tasks
                if any(p not in block_set for p in self.G.predecessors(t))
            }
            result[block_id] = {
                "task_count": len(tasks),
                "tasks": sorted(tasks),
                "internal_edges": list(self.G.subgraph(tasks).edges()),
                "external_dependencies": external_deps,
            }
        return result

    # ------------------------------------------------------------------
    # Single-task analysis
    # ------------------------------------------------------------------

    def analyze_task(self, task_id: str) -> Optional[TaskAnalysis]:
        """Deep-dive analysis of a single task."""
        if task_id not in self.tasks:
            return None
        return TaskAnalysis(
            task_id=task_id,
            info=self.tasks[task_id],
            direct_prerequisites=sorted(self.G.predecessors(task_id)),
            direct_dependents=sorted(self.G.successors(task_id)),
            all_prerequisites=sorted(nx.ancestors(self.G, task_id)),
            all_dependents=sorted(nx.descendants(self.G, task_id)),
            in_degree=self.G.in_degree(task_id),
            out_degree=self.G.out_degree(task_id),
        )

    # ------------------------------------------------------------------
    # Full export
    # ------------------------------------------------------------------

    def export_full_analysis(self) -> Dict:
        """Produce complete analysis summary."""
        validation = self.validate()
        if not validation.is_acyclic:
            return {"validation": asdict(validation)}

        critical_path = self.get_critical_path()
        bottlenecks = self.get_bottlenecks()

        # Impact details for critical-path and bottleneck tasks
        impact_ids = set(critical_path) | {b.task_id for b in bottlenecks}
        impact_details = {
            tid: asdict(self.analyze_task(tid))
            for tid in sorted(impact_ids)
            if self.analyze_task(tid) is not None
        }

        return {
            "validation": asdict(validation),
            "metadata": {
                "total_tasks": len(self.tasks),
                "total_dependencies": self.G.number_of_edges(),
            },
            "execution_order": self.get_execution_order(),
            "parallel_batches": self.get_parallel_batches(),
            "critical_path": critical_path,
            "bottlenecks": [asdict(b) for b in bottlenecks],
            "block_analysis": self.get_block_analysis(),
            "impact_details": impact_details,
        }

    # ------------------------------------------------------------------
    # Console report
    # ------------------------------------------------------------------

    def _fmt_task(self, task_id: str) -> str:
        """Format a single task line: ID [block] CATEGORY."""
        info = self.tasks.get(task_id, {})
        return f"{task_id:45s} [{info.get('block', '?')}] {info.get('category', '?')}"

    def print_report(self, result: Dict):
        """Print a human-readable summary to stdout."""
        v = result["validation"]

        print(_divider("DAG Validation Report"))

        if v["warnings"]:
            print(_section("Warnings"))
            for w in v["warnings"]:
                print(f"  WARNING: {w}")

        print(_section("Cycle Detection"))
        if not v["is_acyclic"]:
            print("  FAILED: Circular dependency detected")
            for cycle in v["cycles"]:
                path = " -> ".join([e["from"] for e in cycle] + [cycle[-1]["to"]])
                print(f"  Cycle: {path}")
            print("\n  Fix the dependency tables and re-run.")
            return

        print("  PASSED: No circular dependencies")

        meta = result["metadata"]
        print(_section("Summary"))
        print(f"  Tasks:        {meta['total_tasks']}")
        print(f"  Dependencies: {meta['total_dependencies']}")
        print(f"  Batches:      {len(result['parallel_batches'])}")
        print(f"  Critical path length: {len(result['critical_path'])}")

        print(_section("Parallel Execution Batches"))
        for i, batch in enumerate(result["parallel_batches"], 1):
            print(f"\n  Batch {i} ({len(batch)} tasks):")
            for t in batch:
                print(f"    {self._fmt_task(t)}")

        print(_section("Critical Path"))
        for i, t in enumerate(result["critical_path"], 1):
            desc = self.tasks.get(t, {}).get("description", "")
            print(f"  {i}. {t:45s} {desc[:55]}")

        if result["bottlenecks"]:
            print(_section("Bottleneck Tasks"))
            for b in result["bottlenecks"][:10]:
                print(
                    f"  {b['task_id']:45s} "
                    f"blocks {b['direct_dependents']} direct, "
                    f"{b['total_downstream']} total downstream"
                )

        print(_section("Block Analysis"))
        for block_id, ba in result["block_analysis"].items():
            n_ext = len(ba["external_dependencies"])
            print(
                f"  Block {block_id}: {ba['task_count']} tasks, "
                f"{len(ba['internal_edges'])} internal edges, "
                f"{n_ext} tasks with external dependencies"
            )

        print(f"\n{'=' * 72}")

    def print_task_report(self, analysis: TaskAnalysis):
        """Print a single-task analysis to stdout."""
        print(_divider(f"Task Analysis: {analysis.task_id}"))
        print(f"  Description:  {analysis.info.get('description', '')}")
        print(f"  Category:     {analysis.info.get('category', '?')}")
        print(f"  Block:        {analysis.info.get('block', '?')}")
        print(f"  In-degree:    {analysis.in_degree}")
        print(f"  Out-degree:   {analysis.out_degree}")

        print(_section("Direct Prerequisites"))
        if analysis.direct_prerequisites:
            for t in analysis.direct_prerequisites:
                print(f"    {self._fmt_task(t)}")
        else:
            print("    (none — this task can begin immediately)")

        print(_section("Direct Dependents"))
        if analysis.direct_dependents:
            for t in analysis.direct_dependents:
                print(f"    {self._fmt_task(t)}")
        else:
            print("    (none — no tasks are blocked by this)")

        print(_section("All Prerequisites (transitive)"))
        print(f"    {len(analysis.all_prerequisites)} tasks")
        if analysis.all_prerequisites:
            for t in analysis.all_prerequisites:
                print(f"      {t}")

        print(_section("All Dependents (transitive)"))
        print(f"    {len(analysis.all_dependents)} tasks")
        if analysis.all_dependents:
            for t in analysis.all_dependents:
                print(f"      {t}")

        print(f"\n{'=' * 72}")


# ======================================================================
# Main
# ======================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Validate a revision master plan DAG using NetworkX"
    )
    parser.add_argument(
        "tasks_file",
        help="Path to the tasks JSON file (see task-schema.md)",
    )
    parser.add_argument(
        "--output", "-o",
        default="revision_dag_analysis.json",
        help="Output JSON path (default: revision_dag_analysis.json)",
    )
    parser.add_argument(
        "--task", "-t",
        default=None,
        help="Analyze a single task by ID (skip full report)",
    )
    parser.add_argument(
        "--validate-only", "-v",
        action="store_true",
        help="Check acyclicity and warnings only (Phase 3b gate check)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress console output (still writes JSON)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    # Load tasks
    try:
        tasks = load_tasks(args.tasks_file)
    except FileNotFoundError:
        logger.error("File not found: %s", args.tasks_file)
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in %s: %s", args.tasks_file, e)
        sys.exit(1)

    if not args.quiet:
        print(f"Loaded {len(tasks)} tasks from {args.tasks_file}")

    validator = RevisionDAGValidator(tasks)

    # Validate-only mode (Phase 3b gate check)
    if args.validate_only:
        validation = validator.validate()
        if not args.quiet:
            print(_divider("Phase 3b: Structural Validation"))
            if validation.warnings:
                print(_section("Warnings"))
                for w in validation.warnings:
                    print(f"  WARNING: {w}")
            print(_section("Cycle Detection"))
            if validation.is_acyclic:
                print("  PASSED: No circular dependencies")
                print(f"\n  {len(tasks)} tasks, "
                      f"{validator.G.number_of_edges()} dependencies — "
                      f"graph is a valid DAG.")
                print("  Proceed to Phase 4 (Sequencing).")
            else:
                print("  FAILED: Circular dependency detected")
                for cycle in validation.cycles:
                    path = " -> ".join(
                        [e["from"] for e in cycle] + [cycle[-1]["to"]]
                    )
                    print(f"  Cycle: {path}")
                print("\n  Fix Phase 3 dependency tables and re-run.")
            print(f"\n{'=' * 72}")
        output = {"validation": asdict(validation)}
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        if not args.quiet:
            print(f"\nValidation result written to {args.output}")
        if not validation.is_acyclic:
            sys.exit(1)
        return

    # Single-task mode
    if args.task:
        analysis = validator.analyze_task(args.task)
        if analysis is None:
            logger.error("Task '%s' not found in %s", args.task, args.tasks_file)
            sys.exit(1)
        if not args.quiet:
            validator.print_task_report(analysis)
        output = {"analyzed_task": asdict(analysis)}
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        if not args.quiet:
            print(f"\nTask analysis written to {args.output}")
        return

    # Full analysis mode
    result = validator.export_full_analysis()

    if not args.quiet:
        validator.print_report(result)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    if not args.quiet:
        print(f"\nFull analysis written to {args.output}")

    if not result["validation"]["is_acyclic"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
