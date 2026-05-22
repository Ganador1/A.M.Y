"""FAIR exporter para datasets matemáticos del laboratorio matemático.

Exporta conjeturas desde la base de datos del `ConjecturePersistenceService`
como JSONL y genera un `manifest.json` reproducible con checksums.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib

from app.mathlab.persistence.conjecture_persistence import (
    ConjecturePersistenceService,
    Conjecture,
)
from app.domains.mathematics.models.conjecture_contracts import CONJECTURE_CONTRACT_VERSION


class MathFairExporter:
    """Exportador FAIR mínimo para conjeturas matemáticas."""

    def __init__(self, persistence: ConjecturePersistenceService) -> None:
        self.persistence = persistence

    def export_conjectures_dataset(
        self,
        output_dir: str,
        *,
        name: str = "math_conjectures",
        description: str = "Conjunto FAIR de conjeturas matemáticas del laboratorio matemático",
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Exporta todas las conjeturas a JSONL y genera manifest.json.

        - output_dir: carpeta destino (se crea si no existe)
        - filters: reservado para futuras opciones de filtrado
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 1) Dump de conjeturas a JSONL
        jsonl_path = os.path.join(output_dir, "conjectures.jsonl")
        count = self._dump_conjectures_jsonl(jsonl_path, filters=filters)

        # 2) Calcular checksum / tamaño
        checksum = self._sha256_of_file(jsonl_path)
        size_bytes = os.path.getsize(jsonl_path)

        # 3) Construir manifest
        manifest = {
            "type": "axiom_math_fair_dataset",
            "schema_version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "dataset": {
                "name": name,
                "description": description,
                "spec_version": CONJECTURE_CONTRACT_VERSION,
                "items": {"conjectures": count},
            },
            "files": [
                {
                    "path": "conjectures.jsonl",
                    "sha256": checksum,
                    "size_bytes": size_bytes,
                }
            ],
        }

        manifest_path = os.path.join(output_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)

        return {
            "output_dir": output_dir,
            "files": {
                "conjectures": jsonl_path,
                "manifest": manifest_path,
            },
            "counts": {"conjectures": count},
        }

    # ---------------------------- helpers ----------------------------
    def _dump_conjectures_jsonl(self, path: str, *, filters: Optional[Dict[str, Any]] = None) -> int:
        """Vuelca todas las conjeturas en JSONL. Retorna el total exportado."""
        total = 0
        with self.persistence.get_db_session() as db, open(path, "w", encoding="utf-8") as f:
            q = db.query(Conjecture)
            # Filtros simples reservados para futuro (e.g., por estado/tipo)
            for row in q.all():
                rec = {
                    "id": row.id,
                    "title": row.title,
                    "statement": row.statement,
                    "type": row.conjecture_type,
                    "status": row.status,
                    "confidence": row.confidence,
                    "importance": row.importance_score,
                    "evidence_metrics": row.evidence_metrics,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                    "verification_info": row.agent1_verification_info,
                    "tags": row.tags or [],
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                total += 1
        return total

    def _sha256_of_file(self, path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()


__all__ = ["MathFairExporter"]


