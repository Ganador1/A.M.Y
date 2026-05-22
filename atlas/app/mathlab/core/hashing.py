from __future__ import annotations

import json
import hashlib
from typing import Any, Dict


def _normalize(obj: Any) -> Any:
    """Normaliza objetos Python a una forma canónica determinista.
    - Diccionarios: claves ordenadas recursivamente
    - Listas/tuplas: normalización elemento a elemento
    - Numéricos/básicos: se retornan directamente
    """
    if isinstance(obj, dict):
        return {k: _normalize(obj[k]) for k in sorted(obj.keys())}
    if isinstance(obj, (list, tuple)):
        return [_normalize(x) for x in obj]
    return obj


def semantic_hash(payload: Dict[str, Any], obj_type: str, spec_version: str = "v1") -> str:
    """Genera hash semántico determinista basado en tipo + forma normalizada del JSON.

    hash = SHA256( obj_type + "|" + spec_version + "|" + json_dumps_sorted )
    """
    normalized = _normalize(payload)
    serialized = json.dumps(normalized, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    material = f"{obj_type}|{spec_version}|{serialized}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()