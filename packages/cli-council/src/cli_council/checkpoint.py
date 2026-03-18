"""Checkpoint and file-based coordination for council runs.

Inspired by:
- Owlex (agentic-mcp-tools/owlex): session resumption across deliberation rounds
- agents-council (MrLesk/agents-council): atomic file writes, cursor-based state

Provides:
- Atomic JSON writes (tmp + fsync + rename) for crash safety
- Stage checkpointing: save after each stage, resume from last completed stage
- Pending participant tracking
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Default checkpoint directory (gitignored in projects)
DEFAULT_CHECKPOINT_DIR = ".council"


@dataclass(frozen=True)
class CheckpointMeta:
    """Metadata for a checkpoint file."""

    run_id: str
    stage: int  # 1, 2, or 3
    timestamp: str
    backends: list[str]


def _atomic_write_json(path: Path, data: dict) -> None:
    """Write JSON atomically: tmp file -> fsync -> rename.

    If the process crashes mid-write, the original file is preserved.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), suffix=".tmp", prefix=".ckpt-",
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, default=str)
            f.flush()
            os.fsync(f.fileno())
        os.rename(tmp_path, str(path))
    except BaseException:
        # Clean up temp file on any failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _read_json(path: Path) -> dict | None:
    """Read a JSON checkpoint file, returning None if missing or corrupt."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Corrupt checkpoint %s: %s", path, exc)
        return None


def _make_run_id() -> str:
    """Generate a timestamped run ID."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


@dataclass
class CouncilCheckpointer:
    """Manages checkpoint state for a council run.

    Usage:
        ckpt = CouncilCheckpointer(checkpoint_dir="/path/to/.council")
        # Saves after each stage; can resume from last completed stage.
    """

    checkpoint_dir: Path
    run_id: str = field(default_factory=_make_run_id)

    def __post_init__(self) -> None:
        self.checkpoint_dir = Path(self.checkpoint_dir)

    # ---- Save ----

    def save_stage1(self, assessments: list[dict], backends: list[str]) -> Path:
        """Save Stage 1 assessments to checkpoint."""
        path = self._stage_path(1)
        data = {
            "meta": {
                "run_id": self.run_id,
                "stage": 1,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "backends": backends,
            },
            "assessments": assessments,
        }
        _atomic_write_json(path, data)
        logger.info("Checkpoint saved: Stage 1 → %s", path)
        return path

    def save_stage2(
        self,
        peer_reviews: list[dict],
        backends: list[str],
        aggregate_rankings: list[dict] | None = None,
    ) -> Path:
        """Save Stage 2 peer reviews to checkpoint."""
        path = self._stage_path(2)
        data = {
            "meta": {
                "run_id": self.run_id,
                "stage": 2,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "backends": backends,
            },
            "peer_reviews": peer_reviews,
            "aggregate_rankings": aggregate_rankings or [],
        }
        _atomic_write_json(path, data)
        logger.info("Checkpoint saved: Stage 2 → %s", path)
        return path

    def save_stage3(self, synthesis: dict | str, chairman: str) -> Path:
        """Save Stage 3 synthesis to checkpoint."""
        path = self._stage_path(3)
        data = {
            "meta": {
                "run_id": self.run_id,
                "stage": 3,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "chairman": chairman,
            },
            "synthesis": synthesis,
        }
        _atomic_write_json(path, data)
        logger.info("Checkpoint saved: Stage 3 → %s", path)
        return path

    # ---- Load / Resume ----

    def last_completed_stage(self) -> int:
        """Return the highest completed stage (0 if none)."""
        for stage in (3, 2, 1):
            if self._stage_path(stage).exists():
                return stage
        return 0

    def load_stage1(self) -> list[dict] | None:
        """Load Stage 1 assessments from checkpoint."""
        data = _read_json(self._stage_path(1))
        if data is None:
            return None
        return data.get("assessments")

    def load_stage2(self) -> tuple[list[dict], list[dict]] | None:
        """Load Stage 2 peer reviews + aggregate rankings from checkpoint."""
        data = _read_json(self._stage_path(2))
        if data is None:
            return None
        return data.get("peer_reviews", []), data.get("aggregate_rankings", [])

    def load_stage3(self) -> dict | str | None:
        """Load Stage 3 synthesis from checkpoint."""
        data = _read_json(self._stage_path(3))
        if data is None:
            return None
        return data.get("synthesis")

    # ---- Pending participants ----

    def pending_participants(
        self, all_backends: list[str], responded: list[str],
    ) -> list[str]:
        """Return backends that haven't responded yet."""
        return [b for b in all_backends if b not in set(responded)]

    # ---- Discovery ----

    def find_latest_run(self) -> str | None:
        """Find the most recent run_id in the checkpoint directory."""
        if not self.checkpoint_dir.exists():
            return None
        # Look for stage-1 files (every run has one)
        stage1_files = sorted(self.checkpoint_dir.glob("*-stage1.json"), reverse=True)
        if not stage1_files:
            return None
        # Extract run_id from filename: {run_id}-stage1.json
        return stage1_files[0].stem.replace("-stage1", "")

    def clean(self) -> None:
        """Remove all checkpoint files for this run."""
        for stage in (1, 2, 3):
            path = self._stage_path(stage)
            if path.exists():
                path.unlink()
                logger.info("Removed checkpoint: %s", path)

    # ---- Internal ----

    def _stage_path(self, stage: int) -> Path:
        return self.checkpoint_dir / f"{self.run_id}-stage{stage}.json"
