"""Service Registry

Auto-discovery de servicios *_service.py para unificar metadatos básicos.
MVP: escanea app/ y app/services/, carga introspectivamente clases que contengan
'Service' en el nombre y expone list_services() con información mínima.

Futuro: health, dominios, capacidades declaradas, riesgo, timeouts, circuit breakers.
"""
from __future__ import annotations
import pkgutil
import inspect
import importlib
from pathlib import Path
from typing import Dict, Any, List

BASE_PATH = Path(__file__).resolve().parent

_cached: List[Dict[str, Any]] | None = None

DOMAIN_KEYWORDS = {
    "plasma": "plasma_physics",
    "medical": "medical_imaging",
    "clinical": "clinical_validation",
    "protein": "computational_biology",
    "material": "materials_science",
    "manufactur": "additive_manufacturing",
    "chem": "computational_chemistry",
}

def _infer_domain(name: str, doc: str | None) -> str:
    source = f"{name} {(doc or '').lower()}".lower()
    for kw, dom in DOMAIN_KEYWORDS.items():
        if kw in source:
            return dom
    return "general"

def _discover() -> List[Dict[str, Any]]:
    services: List[Dict[str, Any]] = []
    search_paths = [BASE_PATH, BASE_PATH / "services"]
    for sp in search_paths:
        if not sp.exists():
            continue
        for module_info in pkgutil.iter_modules([str(sp)]):
            if not module_info.name.endswith("_service"):
                continue
            full_name = f"{__package__}.{module_info.name}" if sp == BASE_PATH else f"{__package__}.services.{module_info.name}"
            try:
                module = importlib.import_module(full_name)
            except Exception:  # pragma: no cover
                continue
            for attr_name, attr in inspect.getmembers(module, inspect.isclass):
                if attr.__module__ != module.__name__:
                    continue
                if "Service" not in attr_name:
                    continue
                doc = inspect.getdoc(attr) or ""
                domain = _infer_domain(attr_name, doc)
                services.append({
                    "name": attr_name,
                    "module": module.__name__,
                    "domain": domain,
                    "doc_first_line": doc.splitlines()[0] if doc else "",
                })
    return services

def refresh_cache() -> int:
    global _cached
    _cached = _discover()
    return len(_cached)

def list_services(force_refresh: bool = False) -> List[Dict[str, Any]]:
    global _cached
    if force_refresh or _cached is None:
        refresh_cache()
    return list(_cached or [])

# Pre-cargar al importar
refresh_cache()
