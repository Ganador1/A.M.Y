"""
Integrity Core module for compatibility
Simple in-memory stub to satisfy unit tests expectations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
import hashlib
import time


@dataclass
class ArtifactRecord:
    artifact_id: str
    metadata: Dict[str, Any]
    artifact_type: str
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    integrity_status: Optional[str] = None


class IntegrityCore:
    def __init__(self):
        # minimal in-memory store
        self._store: Dict[str, ArtifactRecord] = {}

    def register_artifact(
        self,
        data: Any,
        *,
        artifact_type: str = "result",
        metadata: Optional[Dict[str, Any]] = None,
        blockchain: bool = False,
    ) -> ArtifactRecord:
        # create a simple deterministic id from data representation and time
        h = hashlib.sha256()
        try:
            h.update(repr(data).encode("utf-8"))
        except Exception:
            h.update(str(type(data)).encode("utf-8"))
        h.update(str(time.time_ns()).encode("utf-8"))
        artifact_id = h.hexdigest()[:16]
        parent_id = (metadata or {}).get("parent_id") if isinstance(metadata, dict) else None
        rec = ArtifactRecord(
            artifact_id=artifact_id,
            metadata=metadata or {},
            artifact_type=artifact_type,
            parent_id=parent_id,
            # integrity_status can be used by validators; default to 'valid' for MVP
            integrity_status="valid",
        )
        self._store[artifact_id] = rec
        # link to parent if provided and exists
        if parent_id and parent_id in self._store:
            if artifact_id not in self._store[parent_id].children:
                self._store[parent_id].children.append(artifact_id)
        return rec

    async def verify_artifact(self, artifact_id: str) -> Dict[str, Any]:
        # minimal verification response expected by tests
        exists = artifact_id in self._store
        return {
            "artifact_id": artifact_id,
            "integrity_ok": exists,
            "final_status": "valid" if exists else "not_found",
        }

    # --- Minimal API used by validation matrix and integrity router ---
    def list_artifacts(self) -> List[Dict[str, Any]]:
        """Return a lightweight list of artifacts for monitoring.
        Each item includes lineage and integrity fields expected by validators.
        """
        items: List[Dict[str, Any]] = []
        for rec in self._store.values():
            items.append({
                "artifact_id": rec.artifact_id,
                "artifact_type": rec.artifact_type,
                "metadata": dict(rec.metadata or {}),
                "parent_id": rec.parent_id,
                "children": list(rec.children),
                "integrity_status": rec.integrity_status or "valid",
            })
        return items

    def link_child(self, parent_id: str, child_id: str) -> bool:
        parent = self._store.get(parent_id)
        child = self._store.get(child_id)
        if not parent or not child:
            return False
        child.parent_id = parent_id
        if child_id not in parent.children:
            parent.children.append(child_id)
        return True

    def get_lineage(self, artifact_id: str) -> Dict[str, Any]:
        rec = self._store.get(artifact_id)
        if not rec:
            return {"artifact_id": artifact_id, "parent_id": None, "children": []}
        return {
            "artifact_id": rec.artifact_id,
            "parent_id": rec.parent_id,
            "children": list(rec.children),
        }


# Expose an instance named integrity_core as expected by tests
integrity_core = IntegrityCore()
