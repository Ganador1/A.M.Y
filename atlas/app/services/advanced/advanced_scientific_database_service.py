"""Advanced Scientific Database Service
=====================================

Fachada unificada para operaciones científicas de alto nivel (MVP):

Incluye:
  - CRUD de hipótesis (delegado al HypothesisPersistenceService existente)
  - Gestión de evidencias y refinamientos (delegado)
  - Registro y consulta de modelos (delegado al ModelManagementService)
  - Búsqueda semántica (stub): filtrado simple por coincidencia parcial + puntuación heurística
  - Hook de embeddings (stub) para futura integración (vector store / proveedor externo)
  - Paginación consistente en listados

NOTA: Este servicio no reemplaza servicios especializados; ofrece una capa agregada
para clientes que deseen reducir número de llamadas o construir queries compuestas.

Acciones soportadas (action):
  * create_hypothesis
  * get_hypothesis
  * list_hypotheses
  * add_evidence
  * add_refinement
  * register_model
  * list_models
  * search (target: hypothesis|model)
  * embed_text
  * health

Estructura de respuesta estándar:
  { "success": bool, <payload>, "meta": {"service": str, "action": str} }

Futuras extensiones previstas:
  - Integración real de embeddings (vector store central)
  - Unificación de transacciones multi-entidad
  - Query planner sobre Knowledge Graph + hipótesis
  - Seguridad / control de acceso granular
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import or_
import math
import time

from app.services.base_service import BaseService
from app.core.database import get_db_session
from app.models.hypothesis_models import (
	HypothesisRecord,
)
from app.exceptions.infrastructure.database import DatabaseError

from app.services.hypothesis_persistence import HypothesisPersistenceService
from app.services.model_management_service import ModelManagementService
from app.core.bootstrap_logging import logger
from app.types.advanced_scientific_database_service_types import (
    HypothesisDtoResult,
    ToDictResult,
    ProcessRequestResult,
    CreateHypothesisResult,
    GetHypothesisResult,
    ListHypothesesResult,
    AddEvidenceResult,
    AddRefinementResult,
    RegisterModelResult,
    ListModelsResult,
    SearchResult,
    EmbedTextResult,
    HealthResult,
    WrapResult,
)


# ----------------------------- Embeddings Stub ---------------------------------

def _compute_embedding_stub(text: str, dim: int = 32) -> List[float]:
	"""Devuelve un embedding determinista simple (hash -> pseudo vector) para stub.

	NO usar en producción; únicamente para mantener interfaz estable hasta disponer
	de un proveedor real (p.ej. local model, OpenAI, HuggingFace, etc.).
	"""
	if not text:
		return [0.0] * dim
	h = abs(hash(text))
	vec = []
	for i in range(dim):
		# Mezcla simple bit-shift + mod para generar flotantes reproducibles
		v = ((h >> (i % 16)) & 0xFFFF) / 65535.0
		vec.append(round(v, 6))
	return vec


# ------------------------------ DTOs -------------------------------------------

def _safe_float(v: Any, default: float = 0.0) -> float:
	try:
		return float(v)  # type: ignore
	except DatabaseError:
		return default


def _hypothesis_dto(rec: HypothesisRecord) -> HypothesisDtoResult:
	def _ts(v):
		try:
			return v.isoformat() if v else None
		except DatabaseError:
			return None
	return {
		"hypothesis_uuid": getattr(rec, "hypothesis_uuid", None),
		"title": getattr(rec, "title", None),
		"description": getattr(rec, "description", None),
		"domain": getattr(rec, "domain", None),
		"confidence_score": _safe_float(getattr(rec, "confidence_score", 0.0), 0.0),
		"status": getattr(rec, "status", None),
		"evidence_count": int(getattr(rec, "evidence_count", 0) or 0),
		"refinement_count": int(getattr(rec, "refinement_count", 0) or 0),
		"created_at": _ts(getattr(rec, "created_at", None)),
		"updated_at": _ts(getattr(rec, "updated_at", None)),
	}


@dataclass
class SearchResult:
	kind: str  # hypothesis | model
	id: str
	score: float
	payload: Dict[str, Any]

	def to_dict(self) -> ToDictResult:
		return {"kind": self.kind, "id": self.id, "score": round(self.score, 4), **self.payload}


class AdvancedScientificDatabaseService(BaseService):
	"""Servicio fachada avanzado para entidades científicas principales.

	Se apoya en servicios existentes para evitar duplicación de lógica y expone
	un punto único de acceso para clientes avanzados o UI agregada.
	"""

	def __init__(self):
		super().__init__("AdvancedScientificDatabase")
		self.hypothesis_service = HypothesisPersistenceService()
		self.model_service = ModelManagementService()
		logger.info("✅ AdvancedScientificDatabaseService inicializado")

	# ------------------------------------------------------------------
	async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
		action = request_data.get("action")
		try:
			handler_map = {
				"create_hypothesis": self._create_hypothesis,
				"get_hypothesis": self._get_hypothesis,
				"list_hypotheses": self._list_hypotheses,
				"add_evidence": self._add_evidence,
				"add_refinement": self._add_refinement,
				"register_model": self._register_model,
				"list_models": self._list_models,
				"search": self._search,
				"embed_text": self._embed_text,
				"health": self._health,
			}
			if action not in handler_map:
				return self._wrap(False, {"error": f"Unknown action: {action}"}, action)
			result = handler_map[action](request_data)
			return self._wrap(True, result, action)
		except DatabaseError as e:
			return self._wrap(False, self.handle_error(e, "process_request"), action)

	# ---------------- Hypothesis Delegations ---------------------------------
	def _create_hypothesis(self, data: CreateHypothesisResult) -> CreateHypothesisResult:
		return self.hypothesis_service.create_hypothesis(data)  # type: ignore

	def _get_hypothesis(self, data: GetHypothesisResult) -> GetHypothesisResult:
		return self.hypothesis_service.get_hypothesis(data)  # type: ignore

	def _list_hypotheses(self, data: ListHypothesesResult) -> ListHypothesesResult:
		# Reaprovechamos consulta directa para añadir paginación avanzada
		db: Session = get_db_session()
		try:
			q = db.query(HypothesisRecord)
			if domain := data.get("domain"):
				q = q.filter(HypothesisRecord.domain == domain)
			if status := data.get("status"):
				q = q.filter(HypothesisRecord.status == status)
			if mc := data.get("min_confidence"):
				try:
					q = q.filter(HypothesisRecord.confidence_score >= float(mc))
				except DatabaseError:
					pass
			total = q.count()
			limit = min(int(data.get("limit", 50)), 200)
			offset = max(int(data.get("offset", 0)), 0)
			items = (
				q.order_by(HypothesisRecord.created_at.desc())
				.offset(offset)
				.limit(limit)
				.all()
			)
			return {
				"items": [_hypothesis_dto(i) for i in items],
				"pagination": {
					"total": total,
					"limit": limit,
					"offset": offset,
					"pages": math.ceil(total / limit) if limit else 1,
				},
			}
		finally:
			db.close()

	def _add_evidence(self, data: AddEvidenceResult) -> AddEvidenceResult:
		return self.hypothesis_service.add_evidence(data)  # type: ignore

	def _add_refinement(self, data: AddRefinementResult) -> AddRefinementResult:
		return self.hypothesis_service.add_refinement(data)  # type: ignore

	# ---------------- Model Registry Delegations -----------------------------
	def _register_model(self, data: RegisterModelResult) -> RegisterModelResult:
		return self.model_service.register_model(data)  # type: ignore

	def _list_models(self, data: ListModelsResult) -> ListModelsResult:
		return self.model_service.list_models()  # type: ignore

	# ---------------- Semantic Search (Stub) ---------------------------------
	def _search(self, data: SearchResult) -> SearchResult:
		target = data.get("target", "hypothesis")
		query = (data.get("query") or "").strip()
		if not query:
			return {"results": [], "count": 0}
		results: List[SearchResult] = []
		if target in ("hypothesis", "all"):
			results.extend(self._search_hypotheses(query, limit=int(data.get("limit", 20))))
		if target in ("model", "all"):
			results.extend(self._search_models(query, limit=int(data.get("limit", 20))))
		# Ordenar por score descendente
		results.sort(key=lambda r: r.score, reverse=True)
		return {"results": [r.to_dict() for r in results], "count": len(results)}

	def _search_hypotheses(self, query: str, limit: int = 20) -> List[SearchResult]:
		db: Session = get_db_session()
		try:
			pattern = f"%{query}%"
			q = (
				db.query(HypothesisRecord)
				.filter(or_(HypothesisRecord.title.ilike(pattern), HypothesisRecord.description.ilike(pattern)))
				.order_by(HypothesisRecord.created_at.desc())
				.limit(limit)
			)
			out: List[SearchResult] = []
			for rec in q.all():
				title_val = getattr(rec, "title", "") or ""
				base_score = 1.0 if query.lower() in title_val.lower() else 0.7
				# Ajuste pequeño por confianza
				conf_val = _safe_float(getattr(rec, "confidence_score", 0.0), 0.0)
				score = base_score * (0.85 + 0.15 * conf_val)
				out.append(
					SearchResult(
						kind="hypothesis",
						id=str(getattr(rec, "hypothesis_uuid", "")),
						score=score,
						payload={"hypothesis": _hypothesis_dto(rec)},
					)
				)
			return out
		finally:
			db.close()

	def _search_models(self, query: str, limit: int = 20) -> List[SearchResult]:
		res = self.model_service.list_models()
		items = res.get("models", []) if res.get("success") else []
		out: List[SearchResult] = []
		for m in items:
			name = (m.get("name") or "").lower()
			if query.lower() in name:
				score = 1.0
			else:
				continue  # Simplificamos: coincidencia exacta parcial únicamente
			out.append(
				SearchResult(
					kind="model",
					id=f"{m.get('name')}:{m.get('version')}",
					score=score,
					payload={"model": m},
				)
			)
			if len(out) >= limit:
				break
		return out

	# ---------------- Embedding Stub ----------------------------------------
	def _embed_text(self, data: EmbedTextResult) -> EmbedTextResult:
		text_value = data.get("text") or ""
		dim = int(data.get("dim", 32))
		dim = max(4, min(dim, 256))
		embedding = _compute_embedding_stub(text_value, dim=dim)
		return {"text_length": len(text_value), "dimension": dim, "embedding": embedding}

	# ---------------- Health -------------------------------------------------
	def _health(self, _: HealthResult) -> HealthResult:
		return {"status": "ok", "timestamp": time.time(), "delegates": ["hypothesis", "model_registry"], "semantic_search": "stub"}

	# ---------------- Helpers ------------------------------------------------
	def _wrap(self, success: bool, payload: WrapResult, action: Optional[str]) -> WrapResult:
		meta = {"service": self.name, "action": action}
		return {"success": success, **payload, "meta": meta}


# Instancia opcional reutilizable
advanced_scientific_database_service = AdvancedScientificDatabaseService()

