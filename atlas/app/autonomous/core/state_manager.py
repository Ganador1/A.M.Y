"""State management for Agent 3 autonomous loops.

Provides a lightweight persistence of loop iteration states, decisions, and outcomes.
Backed by an in-memory dict with optional JSON snapshot export (lazy on demand) to keep
initial implementation simple.
"""
from __future__ import annotations
import asyncio

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import time
from app.core.bootstrap_logging import logger

STATE_SNAPSHOT_PATH = Path("data/autonomous_state.json")
STATE_SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class IterationRecord:
    iteration: int
    domain: str
    selected_ids: List[str]
    actions: List[str]
    outcomes: Dict[str, Any]
    timestamp: float = time.time()


class StateManager:
    """Holds transient state for autonomous exploration cycles."""

    def __init__(self) -> None:
        self._iterations: List[IterationRecord] = []
        self._meta: Dict[str, Any] = {"version": 1}
        logger.debug("StateManager initialized")

    def add_iteration(self, record: IterationRecord) -> None:
        self._iterations.append(record)
        logger.debug(
            "Iteration appended (iter=%d domain=%s selected=%d)",
            record.iteration,
            record.domain,
            len(record.selected_ids),
        )

    def latest(self) -> Optional[IterationRecord]:
        return self._iterations[-1] if self._iterations else None

    def stats(self) -> Dict[str, Any]:
        return {
            "iterations": len(self._iterations),
            "domains": list({r.domain for r in self._iterations}),
        }

    def snapshot(self, path: Path | None = None) -> Path:
        """Persist the current state (lossy: only iteration records) to JSON."""
        target = path or STATE_SNAPSHOT_PATH
        serializable = [asdict(r) for r in self._iterations]
        target.write_text(json.dumps({"iterations": serializable, "meta": self._meta}, indent=2), encoding="utf-8")
        logger.info("State snapshot written to %s", target)
        return target

    # Backwards-compatible alias
    def save_snapshot(self, path: Path | None = None) -> Path:  # pragma: no cover - thin wrapper
        """Alias descriptivo de snapshot para claridad externa."""
        return self.snapshot(path)

    def load_snapshot(self, path: Path | None = None) -> int:
        target = path or STATE_SNAPSHOT_PATH
        if not target.exists():
            logger.warning("Snapshot path %s does not exist", target)
            return 0
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            self._apply_snapshot_data(data)
            logger.info("Loaded %d iteration records from snapshot", len(self._iterations))
            return len(self._iterations)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to load snapshot %s: %s", target, exc)
            return 0

    def load_snapshot_file(self, path: Path) -> int:
        """Explicit method para cargar snapshot desde ruta obligatoria.

        Diferencia: 'load_snapshot' usa ruta por defecto si no se pasa nada; aquí se exige path.
        """
        return self.load_snapshot(path)

    def _apply_snapshot_data(self, data: Dict[str, Any]) -> None:
        """Internal helper to populate internal state from parsed snapshot JSON."""
        self._iterations.clear()
        for rec in data.get("iterations", []):
            self._iterations.append(
                IterationRecord(
                    iteration=rec.get("iteration", 0),
                    domain=rec.get("domain", "unknown"),
                    selected_ids=list(rec.get("selected_ids", [])),
                    actions=list(rec.get("actions", [])),
                    outcomes=rec.get("outcomes", {}),
                    timestamp=rec.get("timestamp", time.time()),
                )
            )
        self._meta = data.get("meta", {})

__all__ = ["StateManager", "IterationRecord", "STATE_SNAPSHOT_PATH"]
