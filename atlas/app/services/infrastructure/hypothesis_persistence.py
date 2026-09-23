"""
Hypothesis Persistence Service
CRUD para hipótesis científicas persistidas en la base de datos y sincronización con el agente en memoria.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import uuid
import asyncio

from app.services.base_service import BaseService
from app.core.database import get_db_session
from app.models.hypothesis_models import (
    HypothesisRecord,
    HypothesisEvidenceRecord,
    HypothesisRefinementRecord,
)
from app.exceptions.domain.biology import BiologyError
from app.types.hypothesis_persistence_types import (
    ProcessRequestResult,
    CreateHypothesisResult,
    GetHypothesisResult,
    ListHypothesesResult,
    UpdateHypothesisResult,
    DeleteHypothesisResult,
    AddEvidenceResult,
    AddRefinementResult,
    ToDictResult,
)

try:
    from app.compliance.risk_assessment import risk_assessment
except BiologyError:  # pragma: no cover
    risk_assessment = None  # type: ignore


class HypothesisPersistenceService(BaseService):
    def __init__(self):
        super().__init__("HypothesisPersistence")

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        try:
            action = request_data.get("action", "")
            if action == "create":
                return await asyncio.to_thread(self.create_hypothesis, request_data)
            if action == "get":
                return await asyncio.to_thread(self.get_hypothesis, request_data)
            if action == "list":
                return await asyncio.to_thread(self.list_hypotheses, request_data)
            if action == "update":
                return await asyncio.to_thread(self.update_hypothesis, request_data)
            if action == "delete":
                return await asyncio.to_thread(self.delete_hypothesis, request_data)
            if action == "add_evidence":
                return await asyncio.to_thread(self.add_evidence, request_data)
            if action == "add_refinement":
                return await asyncio.to_thread(self.add_refinement, request_data)
            return {"success": False, "error": f"Unknown action: {action}"}
        except BiologyError as e:
            return self.handle_error(e, "process_request")

    # --- CRUD ---
    def create_hypothesis(self, data: CreateHypothesisResult) -> CreateHypothesisResult:
        db: Session = get_db_session()
        try:
            title = data.get("title")
            domain = data.get("domain")
            if not title or not domain:
                return {"success": False, "error": "title and domain are required"}

            # --- Risk gate integration (MVP) ---
            description = data.get("description") or ""
            justification = data.get("justification")
            justification_signature = data.get("justification_signature")
            risk_level: Optional[str] = None
            if risk_assessment:
                rr = risk_assessment.assess(
                    domain=domain,
                    description=description,
                    resources=data.get("resources") or {},
                    data_sensitivity=data.get("data_sensitivity", "none"),
                    declared_intent=data.get("declared_intent", "research"),
                    justification=justification,
                    justification_signature=justification_signature,
                )
                # Política: bloquear CRITICAL siempre; bloquear HIGH si falta justificación/firma
                if rr.level == "CRITICAL" or (rr.level == "HIGH" and (not justification or not justification_signature)):
                    return {
                        "success": False,
                        "error": f"Hypothesis blocked by risk gate level={rr.level}",
                        "risk_level": rr.level,
                        "reasons": rr.reasons,
                    }
                risk_level = rr.level

            hypothesis_uuid = data.get("hypothesis_uuid") or str(uuid.uuid4())
            record = HypothesisRecord(
                hypothesis_uuid=hypothesis_uuid,
                title=title,
                description=data.get("description"),
                domain=domain,
                variables=data.get("variables") or [],
                assumptions=data.get("assumptions") or [],
                expected_outcome=data.get("expected_outcome"),
                confidence_score=float(data.get("confidence_score", 0.0)),
                status=data.get("status", "generated"),
                linked_workflow_id=data.get("linked_workflow_id"),
                linked_experiment_id=data.get("linked_experiment_id"),
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return {
                "success": True,
                "hypothesis_uuid": record.hypothesis_uuid,
                "id": record.id,
                "risk_level": risk_level,
            }
        except BiologyError as e:
            db.rollback()
            return self.handle_error(e, "create_hypothesis")
        finally:
            db.close()

    def get_hypothesis(self, data: GetHypothesisResult) -> GetHypothesisResult:
        db: Session = get_db_session()
        try:
            uid = data.get("hypothesis_uuid")
            if not uid:
                return {"success": False, "error": "hypothesis_uuid is required"}
            rec: Optional[HypothesisRecord] = db.query(HypothesisRecord).filter_by(hypothesis_uuid=uid).first()
            if not rec:
                return {"success": False, "error": "Hypothesis not found"}
            return {"success": True, "hypothesis": self._to_dict(rec)}
        except BiologyError as e:
            return self.handle_error(e, "get_hypothesis")
        finally:
            db.close()

    def list_hypotheses(self, data: ListHypothesesResult) -> ListHypothesesResult:
        db: Session = get_db_session()
        try:
            q = db.query(HypothesisRecord)
            domain = data.get("domain")
            status = data.get("status")
            min_conf = data.get("min_confidence", 0.0)
            if domain:
                q = q.filter(HypothesisRecord.domain == domain)
            if status:
                q = q.filter(HypothesisRecord.status == status)
            if min_conf:
                q = q.filter(HypothesisRecord.confidence_score >= float(min_conf))
            items = q.order_by(HypothesisRecord.created_at.desc()).limit(int(data.get("limit", 100))).all()
            return {"success": True, "items": [self._to_dict(i) for i in items], "count": len(items)}
        except BiologyError as e:
            return self.handle_error(e, "list_hypotheses")
        finally:
            db.close()

    def update_hypothesis(self, data: UpdateHypothesisResult) -> UpdateHypothesisResult:
        db: Session = get_db_session()
        try:
            uid = data.get("hypothesis_uuid")
            if not uid:
                return {"success": False, "error": "hypothesis_uuid is required"}
            rec: Optional[HypothesisRecord] = db.query(HypothesisRecord).filter_by(hypothesis_uuid=uid).first()
            if not rec:
                return {"success": False, "error": "Hypothesis not found"}
            for field in [
                "title", "description", "domain", "variables", "assumptions",
                "expected_outcome", "confidence_score", "status",
                "linked_workflow_id", "linked_experiment_id",
                "tested_at", "validated_at",
            ]:
                if field in data and data[field] is not None:
                    setattr(rec, field, data[field])
            db.commit()
            db.refresh(rec)
            return {"success": True, "hypothesis": self._to_dict(rec)}
        except BiologyError as e:
            db.rollback()
            return self.handle_error(e, "update_hypothesis")
        finally:
            db.close()

    def delete_hypothesis(self, data: DeleteHypothesisResult) -> DeleteHypothesisResult:
        db: Session = get_db_session()
        try:
            uid = data.get("hypothesis_uuid")
            if not uid:
                return {"success": False, "error": "hypothesis_uuid is required"}
            rec: Optional[HypothesisRecord] = db.query(HypothesisRecord).filter_by(hypothesis_uuid=uid).first()
            if not rec:
                return {"success": False, "error": "Hypothesis not found"}
            db.delete(rec)
            db.commit()
            return {"success": True, "deleted": True}
        except BiologyError as e:
            db.rollback()
            return self.handle_error(e, "delete_hypothesis")
        finally:
            db.close()

    # --- Relations management ---
    def add_evidence(self, data: AddEvidenceResult) -> AddEvidenceResult:
        db: Session = get_db_session()
        try:
            uid = data.get("hypothesis_uuid")
            rec: Optional[HypothesisRecord] = db.query(HypothesisRecord).filter_by(hypothesis_uuid=uid).first()
            if not rec:
                return {"success": False, "error": "Hypothesis not found"}
            ev = HypothesisEvidenceRecord(
                hypothesis_id=rec.id,
                evidence_type=data.get("evidence_type"),
                details=data.get("details"),
                results=data.get("results"),
                support_score=data.get("support_score"),
            )
            db.add(ev)
            # Increment counter via SQL to avoid static type issues
            db.execute(text("UPDATE hypotheses SET evidence_count = COALESCE(evidence_count,0) + 1 WHERE id = :id"), {"id": rec.id})
            db.commit()
            # Return without reloading heavy relationships
            return {"success": True, "evidence_id": ev.id}
        except BiologyError as e:
            db.rollback()
            return self.handle_error(e, "add_evidence")
        finally:
            db.close()

    def add_refinement(self, data: AddRefinementResult) -> AddRefinementResult:
        db: Session = get_db_session()
        try:
            uid = data.get("hypothesis_uuid")
            rec: Optional[HypothesisRecord] = db.query(HypothesisRecord).filter_by(hypothesis_uuid=uid).first()
            if not rec:
                return {"success": False, "error": "Hypothesis not found"}
            delta = float(data.get("confidence_delta", 0.0) or 0.0)
            manual = bool(data.get("manual", False))
            ref = HypothesisRefinementRecord(
                hypothesis_id=rec.id,
                changes=data.get("changes"),
                confidence_delta=delta,
                manual=manual,
            )
            db.add(ref)
            # Apply updates via SQL to avoid static typing complaints
            db.execute(text("UPDATE hypotheses SET refinement_count = COALESCE(refinement_count,0) + 1 WHERE id = :id"), {"id": rec.id})
            if delta != 0.0:
                db.execute(text("UPDATE hypotheses SET confidence_score = COALESCE(confidence_score,0) + :d WHERE id = :id"), {"id": rec.id, "d": delta})
            db.commit()
            return {
                "success": True,
                "refinement_id": ref.id,
            }
        except BiologyError as e:
            db.rollback()
            return self.handle_error(e, "add_refinement")
        finally:
            db.close()

    # --- Helpers ---
    def _to_dict(self, rec: HypothesisRecord) -> ToDictResult:
        created_at = getattr(rec, "created_at", None)
        updated_at = getattr(rec, "updated_at", None)
        tested_at = getattr(rec, "tested_at", None)
        validated_at = getattr(rec, "validated_at", None)
        def _ts(v):
            return v.isoformat() if isinstance(v, datetime) else None
        def _flt(v, default=0.0):
            try:
                return float(v)
            except BiologyError:
                return float(default)
        def _int(v, default=0):
            try:
                return int(v)
            except BiologyError:
                return int(default)
        return {
            "hypothesis_uuid": getattr(rec, "hypothesis_uuid", None),
            "title": getattr(rec, "title", None),
            "description": getattr(rec, "description", None),
            "domain": getattr(rec, "domain", None),
            "variables": getattr(rec, "variables", None) or [],
            "assumptions": getattr(rec, "assumptions", None) or [],
            "expected_outcome": getattr(rec, "expected_outcome", None),
            "confidence_score": _flt(getattr(rec, "confidence_score", 0.0), 0.0),
            "status": getattr(rec, "status", None),
            "created_at": _ts(created_at),
            "updated_at": _ts(updated_at),
            "tested_at": _ts(tested_at),
            "validated_at": _ts(validated_at),
            "evidence_count": _int(getattr(rec, "evidence_count", 0), 0),
            "refinement_count": _int(getattr(rec, "refinement_count", 0), 0),
            "linked_workflow_id": getattr(rec, "linked_workflow_id", None),
            "linked_experiment_id": getattr(rec, "linked_experiment_id", None),
        }
