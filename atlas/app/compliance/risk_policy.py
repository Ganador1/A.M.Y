"""Dynamic Risk Policy Store (MVP)

Permite leer/actualizar parámetros básicos de política de riesgo en runtime.
Persistencia: en memoria (podría extenderse a DB o archivo YAML).
"""
from __future__ import annotations
from typing import Dict, Any
from threading import RLock

_DEFAULT = {
    "signature_levels": ["HIGH", "CRITICAL"],
    "thresholds": {"low": 4, "medium": 8, "high": 12},
}

class RiskPolicyStore:
    def __init__(self):
        self._lock = RLock()
        self._policy: Dict[str, Any] = dict(_DEFAULT)

    def get(self) -> Dict[str, Any]:
        with self._lock:
            return self._policy.copy()

    def update(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            # Shallow merge
            if "signature_levels" in patch and isinstance(patch["signature_levels"], list):
                self._policy["signature_levels"] = patch["signature_levels"]
            if "thresholds" in patch and isinstance(patch["thresholds"], dict):
                self._policy.setdefault("thresholds", {}).update(patch["thresholds"])  # merge
            return self._policy.copy()

risk_policy_store = RiskPolicyStore()
