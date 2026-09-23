"""Persistencia ligera para resultados del Mathematical Discovery Engine.

Almacena cada `InvestigationResult` como una línea JSON (JSONL) para:
  - Simplicidad sin añadir dependencias.
  - Lectura incremental / streaming futuro.
  - Fácil migración posterior a una base de datos.

Formato de línea:
{
  "id": <conjecture.id>,
  "statement": <conjecture.statement>,
  "domain": <conjecture.domain>,
  "status": "proven|refuted|open|error",
  "importance": float,
  "timestamp": ISO8601,
  "proof": str|None,
  "counterexample": object|None,
  "time_seconds": float
}
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.domains.mathematics.services.mathematical_discovery_engine import InvestigationResult


class DiscoveryPersistence:
    """Persistencia basada en archivo JSONL.

    Thread-safe usando un lock simple. No realiza truncado automático.
    """

    def __init__(self, storage_path: str = "data/mathematical_discoveries.jsonl"):
        self.path = Path(storage_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def append(self, result: InvestigationResult) -> None:
        record = {
            "id": result.conjecture.id,
            "statement": result.conjecture.statement,
            "domain": result.conjecture.domain,
            "goal": result.conjecture.goal,
            "metadata": result.conjecture.metadata,
            "status": result.status,
            "importance": result.importance,
            "timestamp": datetime.utcnow().isoformat(),
            "proof": result.proof,
            "counterexample": result.counterexample,
            "time_seconds": result.time_seconds,
        }
        line = json.dumps(record, ensure_ascii=False)
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

    def read_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        results: List[Dict[str, Any]] = []
        with self._lock:
            with self.path.open("r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if limit is not None and i >= limit:
                        break
                    try:
                        results.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return results

    def query(
        self,
        domain: Optional[str] = None,
        status: Optional[str] = None,
        since: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Consulta filtrada con paginación básica.

        Args:
            domain: filtra por dominio exacto.
            status: filtra por estado exacto.
            since: ISO8601 mínima (timestamp registro > since).
            offset: desplazamiento.
            limit: máximo resultados devueltos.
        """
        all_data = self.read_all()

        def _matches_filters(record: Dict[str, Any]) -> bool:
            if domain and record.get("domain") != domain:
                return False
            if status and record.get("status") != status:
                return False
            if since:
                ts = record.get("timestamp")
                if isinstance(ts, str) and ts <= since:
                    return False
            return True

        filtered = [record for record in all_data if _matches_filters(record)]
        total = len(filtered)
        page = filtered[offset : offset + limit]
        return {
            "total_filtered": total,
            "offset": offset,
            "limit": limit,
            "returned": len(page),
            "results": page,
        }

    def tail(self, n: int = 20) -> List[Dict[str, Any]]:
        data = self.read_all()
        return data[-n:]

    def stats(self) -> Dict[str, Any]:
        data = self.read_all()
        total = len(data)
        status_counts = {}
        for r in data:
            status_counts[r.get("status", "unknown")] = status_counts.get(r.get("status", "unknown"), 0) + 1
        return {
            "total": total,
            "status_counts": status_counts,
        }


MathematicalDiscoveryPersistence = DiscoveryPersistence
