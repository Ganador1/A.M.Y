"""Cross Validation Matrix (MVP)

Objetivo: combinar señales de integridad, riesgo y servicios disponibles
para producir un puntaje compuesto y banderas de alerta.

Fuentes actuales:
- integrity_core.list_artifacts()
- service_registry.list_services()
- (Opcional) estadísticas de riesgo vía recuento de niveles en artifacts si available

Score heurístico (0-100):
- Base 50
- +10 si > 5 servicios, +5 si > 10 servicios
- +10 si > 5 artifacts, +5 si > 15
- -15 si existe algún artifact con integrity_status != None y distinto de 'valid'
- -20 si artifacts > 0 y faltan lineage links (huérfanos con children vacío y parent_id None > 70%)

Flags:
- low_service_diversity
- low_artifact_count
- potential_integrity_issue
- weak_lineage
"""
from __future__ import annotations
from typing import Dict, Any

from app.security.integrity_core import integrity_core
from app.infrastructure.service_registry import list_services

# Import metrics if available
try:
    from .metrics import metrics
except ImportError:  # pragma: no cover
    metrics = None  # type: ignore

class CrossValidationMatrix:
    def build_matrix(self) -> Dict[str, Any]:
        artifacts = integrity_core.list_artifacts()
        services = list_services()
        score = 50
        flags = []

        svc_count = len(services)
        if svc_count > 5:
            score += 10
        if svc_count > 10:
            score += 5
        else:
            if svc_count < 3:
                flags.append("low_service_diversity")

        art_count = len(artifacts)
        if art_count > 5:
            score += 10
        if art_count > 15:
            score += 5
        else:
            if art_count == 0:
                flags.append("low_artifact_count")

        # Integrity anomaly
        for a in artifacts:
            st = a.get("integrity_status")
            if st and st != "valid":
                score -= 15
                flags.append("potential_integrity_issue")
                break

        # Weak lineage detection
        if art_count > 0:
            orphan_like = [a for a in artifacts if not a.get("parent_id") and not a.get("children")]
            if orphan_like and (len(orphan_like) / art_count) > 0.7:
                score -= 20
                flags.append("weak_lineage")

        # Clamp score
        score = max(0, min(100, score))
        result = {
            "score": score,
            "artifact_count": art_count,
            "service_count": svc_count,
            "flags": flags,
            "artifacts_sample": artifacts[:5],
        }
        # Record metrics if available
        if metrics:
            metrics.record_validation_matrix_check(score, flags)
        return result

# Singleton
cross_validation_matrix = CrossValidationMatrix()
