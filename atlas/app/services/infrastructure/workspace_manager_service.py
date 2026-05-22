"""Workspace Manager Service (Stub)
Gestión simple de "workspaces" efímeros en memoria para ejecuciones aisladas.
"""
from __future__ import annotations
from typing import Dict, Any, List
import uuid
import time

class WorkspaceManagerService:
    def __init__(self):
        self._workspaces: Dict[str, Dict[str, Any]] = {}
        self.version = "v0"

    def create(self, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        wid = str(uuid.uuid4())
        ws = {
            "id": wid,
            "created_at": time.time(),
            "metadata": metadata or {},
            "artifacts": {},
            "status": "active",
        }
        self._workspaces[wid] = ws
        return ws

    def list(self) -> List[Dict[str, Any]]:
        return list(self._workspaces.values())

    def add_artifact(self, wid: str, name: str, obj: Any) -> None:
        if wid not in self._workspaces:
            raise KeyError(f"Workspace no encontrado: {wid}")
        self._workspaces[wid]["artifacts"][name] = obj

    def get(self, wid: str) -> Dict[str, Any] | None:
        return self._workspaces.get(wid)

    def cleanup(self, older_than_seconds: float) -> int:
        now = time.time()
        removed = 0
        for wid, ws in list(self._workspaces.items()):
            if now - ws["created_at"] > older_than_seconds:
                ws["status"] = "expired"
                del self._workspaces[wid]
                removed += 1
        return removed

workspace_manager_service = WorkspaceManagerService()
