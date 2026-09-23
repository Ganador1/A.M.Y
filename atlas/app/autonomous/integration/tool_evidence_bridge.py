"""Bridge entre el ToolEvidenceOrchestrator y los loops autónomos.

Ofrece una API ligera para solicitar corroboraciones y normalizar las
respuestas en una estructura utilizable por los loops de materiales,
química, biología, matemáticas o computación cuántica."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.core.bootstrap_logging import logger
from app.services.tool_evidence_orchestrator import ToolEvidenceOrchestratorService
from app.exceptions.infrastructure.api import APIError


@dataclass
class EvidenceSummary:
    """Representa la salida resumida del orquestador para una hipótesis."""

    success: bool
    support_score: float = 0.0
    weighted_coverage: float = 0.0
    mean_signal: float = 0.0
    diversity: float = 0.0
    real_coverage: float = 0.0
    real_weighted_coverage: float = 0.0
    tool_realism_score: float = 0.0
    failure_count: int = 0
    evidence_items: List[Dict[str, Any]] = field(default_factory=list)
    tier_counts: Dict[str, int] = field(default_factory=dict)
    raw_result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        """Devuelve un diccionario listo para serialización o logging."""

        return {
            "success": self.success,
            "support_score": self.support_score,
            "weighted_coverage": self.weighted_coverage,
            "mean_signal": self.mean_signal,
            "diversity": self.diversity,
            "real_coverage": self.real_coverage,
            "real_weighted_coverage": self.real_weighted_coverage,
            "tool_realism_score": self.tool_realism_score,
            "failure_count": self.failure_count,
            "evidence_items": self.evidence_items,
            "tier_counts": self.tier_counts,
            "error": self.error,
        }


class ToolEvidenceBridge:
    """Fachada para consumir el ToolEvidenceOrchestrator desde los loops."""

    def __init__(
        self,
        default_domain: Optional[str] = None,
        orchestrator: Optional[ToolEvidenceOrchestratorService] = None,
    ) -> None:
        self.default_domain = default_domain
        self._orchestrator = orchestrator or ToolEvidenceOrchestratorService()

    async def corroborate(
        self,
        hypothesis: Dict[str, Any],
        *,
        domain: Optional[str] = None,
    ) -> EvidenceSummary:
        """Solicita corroboración de manera asíncrona y normaliza el resultado."""

        payload = self._prepare_payload(hypothesis, domain)
        try:
            result = await self._orchestrator.process_request(payload)
        except APIError as exc:  # noqa: BLE001
            logger.exception("ToolEvidenceBridge error calling orchestrator")
            return EvidenceSummary(success=False, error=str(exc), raw_result={"exception": str(exc)})

        if not result.get("success"):
            return EvidenceSummary(
                success=False,
                error=str(result.get("error", "unknown_error")),
                raw_result=result,
            )

        aggregate = result.get("aggregate") or {}
        return EvidenceSummary(
            success=True,
            support_score=float(aggregate.get("support_score") or 0.0),
            weighted_coverage=float(aggregate.get("weighted_coverage") or 0.0),
            mean_signal=float(aggregate.get("mean_signal") or 0.0),
            diversity=float(aggregate.get("diversity") or 0.0),
            real_coverage=float(aggregate.get("real_coverage") or 0.0),
            real_weighted_coverage=float(aggregate.get("real_weighted_coverage") or 0.0),
            tool_realism_score=float(aggregate.get("tool_realism_score") or 0.0),
            failure_count=int(aggregate.get("failure_count") or 0),
            evidence_items=result.get("evidence_items") or [],
            tier_counts=aggregate.get("tier_counts") or {},
            raw_result=result,
        )

    def corroborate_sync(
        self,
        hypothesis: Dict[str, Any],
        *,
        domain: Optional[str] = None,
    ) -> EvidenceSummary:
        """Versión bloqueante para contextos sin event loop activo."""

        coro = self.corroborate(hypothesis, domain=domain)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)

        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()

    def build_hypothesis(
        self,
        *,
        title: str,
        description: str,
        domain: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        assumptions: Optional[List[str]] = None,
        expected_outcome: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Crea un diccionario de hipótesis con valores por defecto sensatos."""

        hypothesis: Dict[str, Any] = {
            "title": title,
            "description": description,
            "domain": domain or self.default_domain,
            "variables": variables or {},
            "assumptions": assumptions or [],
        }
        if expected_outcome:
            hypothesis["expected_outcome"] = expected_outcome
        if extras:
            hypothesis.update(extras)
        return hypothesis

    def compute_priority_delta(self, summary: EvidenceSummary, weight: float = 0.2) -> float:
        """Métrica auxiliar para ajustar la prioridad de un candidato."""

        return weight * summary.support_score if summary.success else -weight * 0.1

    def _prepare_payload(self, hypothesis: Dict[str, Any], domain: Optional[str]) -> Dict[str, Any]:
        merged = dict(hypothesis)
        if "hypothesis" in merged:
            merged = dict(merged["hypothesis"])  # Permitir pasar payload completo
        if not merged.get("domain"):
            merged["domain"] = domain or self.default_domain
        if not merged.get("title"):
            merged["title"] = merged.get("description", "Unnamed hypothesis")[:120]
        return {"action": "corroborate", "hypothesis": merged}


__all__ = ["ToolEvidenceBridge", "EvidenceSummary"]
