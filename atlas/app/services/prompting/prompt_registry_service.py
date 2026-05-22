"""Prompt Registry Service
Registra y gestiona plantillas de prompts versionadas para agentes.
MVP Features:
- Registrar plantilla (name, version, template, metadata, variables esperadas)
- Renderizar con contexto validando variables requeridas
- Listar / Obtener
- Persistencia JSON en `data/prompt_registry.json`
- Auditoría de renders en `data/prompt_renders.jsonl`

Extensiones futuras (no implementadas aquí):
- A/B testing, expiración, tags semánticos, embedding de propósito
- Cache de renders, métricas de uso
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import datetime
from jinja2 import Environment, StrictUndefined, TemplateSyntaxError
import aiofiles
import asyncio

from app.core.bootstrap_logging import logger
from app.types.prompt_registry_service_types import (
    RegisterResult,
    ListResult,
    GetResult,
    RenderResult,
)

REGISTRY_PATH = Path("data/prompt_registry.json")
RENDERS_LOG = Path("data/prompt_renders.jsonl")

@dataclass
class PromptRecord:
    name: str
    version: str
    template: str
    variables: List[str]
    metadata: Dict[str, Any]
    created_at: str = datetime.datetime.utcnow().isoformat()

class PromptRegistryService:
    def __init__(self) -> None:
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not REGISTRY_PATH.exists():
            REGISTRY_PATH.write_text("[]", encoding="utf-8")
        self.env = Environment(undefined=StrictUndefined, autoescape=False, trim_blocks=True, lstrip_blocks=True)
        # Simple in-memory caches (por instancia)
        self._cache_list: Optional[List[Dict[str, Any]]] = None
        self._cache_get: Dict[str, Any] = {}
        self._cache_render: Dict[str, str] = {}
        logger.info("✅ PromptRegistryService inicializado")

    # --- Persistencia interna ---
    def _load(self) -> List[Dict[str, Any]]:
        if self._cache_list is not None:
            return self._cache_list
        try:
            self._cache_list = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            self._cache_list = []
        # Garantizar list no None
        return self._cache_list or []

    def _save(self, data: List[Dict[str, Any]]) -> None:
        REGISTRY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        # invalidate caches
        self._cache_list = data
        self._cache_get.clear()
        self._cache_render.clear()

    # --- API Pública ---
    def register(self, *, name: str, version: str, template: str, variables: Optional[List[str]] = None, metadata: Optional[RegisterResult] = None) -> RegisterResult:
        if not name or not version or not template:
            return {"success": False, "error": "name, version y template requeridos"}
        data = self._load()
        if any(d["name"] == name and d["version"] == version for d in data):
            return {"success": False, "error": "Ya existe name+version"}
        variables = variables or []
        metadata = metadata or {}
        # Validar compilación
        try:
            self.env.from_string(template)
        except TemplateSyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        rec = PromptRecord(name=name, version=version, template=template, variables=variables, metadata=metadata)
        data.append(asdict(rec))
        self._save(data)
        return {"success": True, "prompt": asdict(rec)}

    def list(self) -> ListResult:
        data = self._load()
        return {"success": True, "count": len(data), "prompts": data}

    def get(self, *, name: str, version: Optional[str] = None) -> GetResult:
        cache_key = f"{name}:{version or '*'}"
        if cache_key in self._cache_get:
            items = self._cache_get[cache_key]
        else:
            data = self._load()
            items = [d for d in data if d["name"] == name and (version is None or d["version"] == version)]
            self._cache_get[cache_key] = items
        if not items:
            return {"success": False, "error": "No encontrado"}
        # Si no se especifica version y hay varias, devolver todas
        return {"success": True, "prompts": items}

    def render(self, *, name: str, version: str, context: RenderResult) -> RenderResult:
        cache_key = f"render:{name}:{version}:{','.join(sorted(context.keys()))}"
        if cache_key in self._cache_render:
            return {"success": True, "rendered": self._cache_render[cache_key], "cached": True}
        data = self._load()
        match = next((d for d in data if d["name"] == name and d["version"] == version), None)
        if not match:
            return {"success": False, "error": "Prompt no registrado"}
        required = match.get("variables", [])
        missing = [v for v in required if v not in context]
        if missing:
            return {"success": False, "error": f"Faltan variables: {missing}"}
        try:
            template = self.env.from_string(match["template"])
            rendered = template.render(**context)
        except Exception as e:
            return {"success": False, "error": f"Render error: {e}"}
        self._cache_render[cache_key] = rendered
        render_record = {
            "ts": datetime.datetime.utcnow().isoformat(),
            "name": name,
            "version": version,
            "hash_key": f"{name}:{version}:{hash(rendered)}",
            "context_keys": sorted(list(context.keys())),
        }
        with RENDERS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(render_record) + "\n")
        return {"success": True, "rendered": rendered, "audit": render_record}

prompt_registry_service = PromptRegistryService()
