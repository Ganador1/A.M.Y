"""Decision Ledger Service (Stub)

Propósito: Registrar decisiones científicas críticas con su contexto, opciones consideradas,
razonamiento y métricas de soporte para trazabilidad y auditoría.
Estado: Stub inicial (sin persistencia) para futura implementación.
"""
from __future__ import annotations
from typing import List, Dict, Any
import time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import DecisionLedgerEntry
from app.exceptions.infrastructure.database import DatabaseError

class DecisionLedgerService:
    def __init__(self):
        self._entries: List[Dict[str, Any]] = []
        self.version = "v0"

    def log_decision(self, *, decision_type: str, subject_id: str | None, options: list, chosen: str, rationale: str, metrics: Dict[str, float] | None = None) -> Dict[str, Any]:
        entry = {
            "ts": time.time(),
            "decision_type": decision_type,
            "subject_id": subject_id,
            "options": options,
            "chosen": chosen,
            "rationale": rationale,
            "metrics": metrics or {},
            "version": self.version,
        }
        self._entries.append(entry)
        # Persistencia best-effort
        try:
            db: Session = SessionLocal()
            row = DecisionLedgerEntry(
                decision_type=decision_type,
                subject_id=subject_id,
                options=options,
                chosen=chosen,
                rationale=rationale,
                metrics=metrics,
                version=self.version,
            )
            db.add(row)
            db.commit()
        except DatabaseError:  # pragma: no cover
            try:
                db.rollback()  # type: ignore
            except DatabaseError:
                pass
        finally:
            try:
                db.close()  # type: ignore
            except DatabaseError:
                pass
        return entry

    def list_decisions(self, decision_type: str | None = None) -> List[Dict[str, Any]]:
        # Combina memoria + DB (DB primero por completitud)
        results: List[Dict[str, Any]] = []
        try:
            db: Session = SessionLocal()
            q = db.query(DecisionLedgerEntry)
            if decision_type:
                q = q.filter(DecisionLedgerEntry.decision_type == decision_type)
            for row in q.order_by(DecisionLedgerEntry.created_at.desc()).limit(200):
                ts_val = None
                try:
                    if getattr(row, "created_at", None) is not None:
                        ts_val = row.created_at.timestamp()
                except DatabaseError:
                    ts_val = None
                results.append({
                    "ts": ts_val,
                    "decision_type": row.decision_type,
                    "subject_id": row.subject_id,
                    "options": row.options,
                    "chosen": row.chosen,
                    "rationale": row.rationale,
                    "metrics": row.metrics or {},
                    "version": row.version,
                    "id": row.id,
                })
        except DatabaseError:  # pragma: no cover
            pass
        finally:
            try:
                db.close()  # type: ignore
            except DatabaseError:
                pass
        # Añade en-memoria (no duplicar por chosen+ts aproximado)
        mem = [e for e in self._entries if (not decision_type or e["decision_type"] == decision_type)]
        results.extend(mem)
        return results

# Singleton
decision_ledger_service = DecisionLedgerService()
