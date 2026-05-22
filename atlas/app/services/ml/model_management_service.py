"""
Model Management Service (ligero)
Registro y consulta de modelos: registrar, listar, obtener, actualizar metadatos.
Persistencia en archivo JSON dentro de `./data/models_registry.json`.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import json
from datetime import datetime

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
import os
from app.exceptions.infrastructure.api import APIError
# Tipos genéricos para maximizar compatibilidad en runtime


REGISTRY_PATH = Path("data/models_registry.json")


@dataclass
class ModelRecord:
    name: str
    version: str
    task: str
    uri: Optional[str] = None
    created_at: str = datetime.now().isoformat()
    metadata: Dict[str, Any] = None  # type: ignore[assignment]


class ModelManagementService(BaseService):
    def __init__(self):
        super().__init__("ModelManagement")
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not REGISTRY_PATH.exists():
            REGISTRY_PATH.write_text("[]", encoding="utf-8")
        logger.info("✅ ModelManagementService initialized")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            action = request_data.get("action", "")
            if action == "register":
                return self.register_model(request_data)
            if action == "list":
                return self.list_models()
            if action == "get":
                return self.get_model(request_data)
            if action == "update":
                return self.update_model(request_data)
            return {"success": False, "error": f"Unknown action: {action}", "available_actions": ["register", "list", "get", "update"]}
        except APIError as e:
            return self.handle_error(e, "process_request")

    def _load(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except APIError:
            return []

    def _save(self, data: List[Dict[str, Any]]) -> None:
        REGISTRY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def register_model(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            name = request_data.get("name")
            version = request_data.get("version")
            task = request_data.get("task")
            uri = request_data.get("uri")
            metadata = request_data.get("metadata") or {}
            if not name or not version or not task:
                return {"success": False, "error": "name, version, and task are required"}
            rec = ModelRecord(name=name, version=version, task=task, uri=uri, metadata=metadata)
            data = self._load()
            if any(d.get("name") == name and d.get("version") == version for d in data):
                return {"success": False, "error": "model with same name+version already exists"}
            data.append(asdict(rec))
            self._save(data)
            return {"success": True, "model": asdict(rec)}
        except APIError as e:
            return self.handle_error(e, "register_model")

    def list_models(self) -> Dict[str, Any]:
        try:
            data = self._load()
            return {"success": True, "count": len(data), "models": data}
        except APIError as e:
            return self.handle_error(e, "list_models")

    def get_model(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            name = request_data.get("name")
            version = request_data.get("version")
            if not name:
                return {"success": False, "error": "name is required"}
            data = self._load()
            items = [d for d in data if d.get("name") == name and (version is None or d.get("version") == version)]
            if not items:
                return {"success": False, "error": "model not found"}
            return {"success": True, "models": items}
        except APIError as e:
            return self.handle_error(e, "get_model")

    def update_model(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            name = request_data.get("name")
            version = request_data.get("version")
            updates = request_data.get("updates") or {}
            if not name or not version:
                return {"success": False, "error": "name and version are required"}
            data = self._load()
            updated = False
            for d in data:
                if d.get("name") == name and d.get("version") == version:
                    d.update(updates)
                    updated = True
                    break
            if not updated:
                return {"success": False, "error": "model not found"}
            self._save(data)
            return {"success": True, "updated": True}
        except APIError as e:
            return self.handle_error(e, "update_model")

# --- Lazy singleton / guard al final para asegurar definición completa ---
# Respeta variable de entorno AXIOM_SKIP_AUTOINIT; por defecto no omite autoinit
_AXIOM_SKIP_AUTOINIT = os.getenv("AXIOM_SKIP_AUTOINIT", "0") == "1"
_model_management_service: Optional[ModelManagementService] = None

def get_model_management_service(force_reinit: bool = False) -> ModelManagementService:
    global _model_management_service
    if force_reinit or _model_management_service is None:
        _model_management_service = ModelManagementService()
    return _model_management_service

if not _AXIOM_SKIP_AUTOINIT:
    model_management_service = get_model_management_service()
else:
    model_management_service = None  # type: ignore

def register_model_entry(**kwargs) -> Dict[str, Any]:
    return get_model_management_service().register_model(kwargs)

def list_model_entries() -> Dict[str, Any]:
    return get_model_management_service().list_models()

def get_model_entry(name: str, version: Optional[str] = None) -> Dict[str, Any]:
    return get_model_management_service().get_model({"name": name, "version": version})

def update_model_entry(name: str, version: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    return get_model_management_service().update_model({"name": name, "version": version, "updates": updates})
