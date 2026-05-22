"""
Provenance Manager — Real provenance tracking for A.M.Y tool executions.

Every tool execution now writes a real provenance.json with:
- Full input/output
- Tool name, version, timestamp
- Environment info (Python, OS, hardware)
- SHA-256 hash of the output
- Execution duration

Papers cite these real provenance files, not synthetic IDs.
"""
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROVENANCE_DIR = Path("data/experiments")


def _sha256_hash(text: str) -> str:
    """Compute SHA-256 hash of text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _get_environment() -> dict:
    """Capture execution environment info."""
    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
    }


class ProvenanceManager:
    """Tracks real provenance for every tool execution."""

    def __init__(self, base_dir: Path | str | None = None):
        self.base_dir = Path(base_dir) if base_dir else PROVENANCE_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def record_execution(
        self,
        tool_name: str,
        tool_input: str,
        tool_output: str,
        success: bool,
        duration_seconds: float,
        domain: str = "unknown",
        experiment_id: str | None = None,
        extra: dict | None = None,
    ) -> dict:
        """
        Record a tool execution with full provenance.

        Returns the provenance record dict (also saved to disk).
        """
        # Generate experiment ID if not provided
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        if experiment_id is None:
            experiment_id = f"{domain}_{tool_name}_{timestamp}"
        experiment_id = self._unique_experiment_id(experiment_id)

        # Build provenance record
        record = {
            "experiment_id": experiment_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": {
                "name": tool_name,
                "input": tool_input,
                "output_hash": _sha256_hash(tool_output),
                "output_length": len(tool_output),
                "success": success,
                "duration_seconds": round(duration_seconds, 3),
            },
            "output_preview": tool_output[:2000] if success else f"ERROR: {tool_output[:500]}",
            "domain": domain,
            "environment": _get_environment(),
            "provenance_version": "1.0",
        }

        if extra:
            record["extra"] = extra

        # Save to disk
        exp_dir = self.base_dir / experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)
        prov_path = exp_dir / "provenance.json"
        prov_path.write_text(json.dumps(record, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

        # Also save full output separately (can be large)
        output_path = exp_dir / "output.txt"
        output_path.write_text(tool_output, encoding="utf-8")

        return record

    def _unique_experiment_id(self, experiment_id: str) -> str:
        """Avoid overwriting provenance when a tool runs multiple times per second."""
        candidate = experiment_id
        counter = 2
        while (self.base_dir / candidate).exists():
            candidate = f"{experiment_id}_{counter}"
            counter += 1
        return candidate

    def verify_experiment_id(self, experiment_id: str) -> dict:
        """
        Verify that an experiment_id has a real provenance file.

        Returns dict with 'exists', 'path', and 'record' (if exists).
        """
        prov_path = self.base_dir / experiment_id / "provenance.json"
        if prov_path.exists():
            try:
                record = json.loads(prov_path.read_text(encoding="utf-8"))
                return {"exists": True, "path": str(prov_path), "record": record}
            except (json.JSONDecodeError, OSError):
                return {"exists": False, "path": str(prov_path), "record": None}
        return {"exists": False, "path": str(prov_path), "record": None}

    def verify_all(self, experiment_ids: list[str]) -> list[dict]:
        """Verify a list of experiment IDs. Returns list of verification results."""
        return [self.verify_experiment_id(eid) for eid in experiment_ids]

    def get_provenance_path(self, experiment_id: str) -> str:
        """Return the expected provenance path for an experiment ID."""
        return str(self.base_dir / experiment_id / "provenance.json")

    def list_experiments(self) -> list[dict]:
        """List all experiments with provenance."""
        experiments = []
        if not self.base_dir.exists():
            return experiments
        for exp_dir in sorted(self.base_dir.iterdir()):
            if exp_dir.is_dir():
                prov_path = exp_dir / "provenance.json"
                if prov_path.exists():
                    try:
                        record = json.loads(prov_path.read_text(encoding="utf-8"))
                        experiments.append({
                            "experiment_id": exp_dir.name,
                            "tool": record.get("tool", {}).get("name", "unknown"),
                            "domain": record.get("domain", "unknown"),
                            "timestamp": record.get("timestamp", "unknown"),
                            "success": record.get("tool", {}).get("success", False),
                        })
                    except (json.JSONDecodeError, OSError):
                        experiments.append({
                            "experiment_id": exp_dir.name,
                            "tool": "unknown",
                            "domain": "unknown",
                            "timestamp": "unknown",
                            "success": False,
                        })
        return experiments


# Global instance
_provenance = ProvenanceManager()


def get_provenance_manager() -> ProvenanceManager:
    """Get the global provenance manager instance."""
    return _provenance
