from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from threading import RLock

from app.mathlab.core.object_models import MathematicalObject
from app.mathlab.core.hashing import semantic_hash, _normalize


@dataclass
class RegistryStats:
    total_objects: int = 0


class ObjectRegistry:
    """Registro en memoria de objetos matemáticos con hashing semántico."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._by_id: Dict[str, MathematicalObject] = {}
        self._by_hash: Dict[str, str] = {}
        self._stats = RegistryStats()

    def register(self, obj_type: str, payload_json: Dict[str, Any], spec_version: str = "v1") -> MathematicalObject:
        payload_norm = _normalize(payload_json)
        s_hash = semantic_hash(payload_norm, obj_type=obj_type, spec_version=spec_version)
        with self._lock:
            if s_hash in self._by_hash:
                # Return existing object to ensure idempotency
                existing_id = self._by_hash[s_hash]
                return self._by_id[existing_id]
            obj_id = str(uuid.uuid4())
            mobj = MathematicalObject(
                id=obj_id,
                type=obj_type,
                semantic_hash=s_hash,
                spec_version=spec_version,
                payload_json=payload_norm,
            )
            self._by_id[obj_id] = mobj
            self._by_hash[s_hash] = obj_id
            self._stats.total_objects += 1
            return mobj

    def get(self, object_id: str) -> Optional[MathematicalObject]:
        with self._lock:
            return self._by_id.get(object_id)

    def get_by_hash(self, s_hash: str) -> Optional[MathematicalObject]:
        with self._lock:
            oid = self._by_hash.get(s_hash)
            return self._by_id.get(oid) if oid else None

    def list(self, limit: int = 100) -> List[MathematicalObject]:
        with self._lock:
            return list(self._by_id.values())[:limit]

    def stats(self) -> RegistryStats:
        return self._stats


# Singleton simple para uso rápido en servicios
REGISTRY = ObjectRegistry()