"""Risk Assessment (MVP)

Capa simple que combina EthicsGate y un set de reglas básicas adicionales
(bio/clinical/material/chem) para producir una evaluación unificada
que otros módulos (hypothesis agent, publication) puedan consultar.
"""
from __future__ import annotations
from typing import Dict, Any
from dataclasses import dataclass
from .ethics_gate import EthicsGate, ExperimentRequest
from ..security.audit_logger import audit_logger

BIO_KEYWORDS = {"pathogen", "virus", "bacteria", "infection", "biosafety"}
CHEM_KEYWORDS = {"toxic", "hazard", "explosive", "flammable"}
CLINICAL_KEYWORDS = {"patient", "clinical", "trial", "diagnosis"}
MATERIALS_KEYWORDS = {"alloy", "microstructure", "fatigue"}

@dataclass
class RiskResult:
    level: str
    risk_score: int
    ethical_level: str
    blocked: bool
    reasons: list[str]

class RiskAssessment:
    def __init__(self):
        self._gate = EthicsGate()

    def assess(self, *, domain: str, description: str, resources: Dict[str, Any] | None = None, data_sensitivity: str = "none", declared_intent: str = "research", justification: str | None = None, justification_signature: str | None = None) -> RiskResult:
        resources = resources or {}
        req = ExperimentRequest(
            domain=domain,
            description=description,
            resources=resources,
            data_sensitivity=data_sensitivity,
            declared_intent=declared_intent,
            justification=justification,
            justification_signature=justification_signature,
        )
        decision = self._gate.evaluate(req)
        # Reglas adicionales por texto
        lowered = f"{description} {declared_intent}".lower()
        reasons: list[str] = []
        def match_any(keywords: set[str], label: str):
            if any(k in lowered for k in keywords):
                reasons.append(f"keyword:{label}")
        match_any(BIO_KEYWORDS, "bio")
        match_any(CHEM_KEYWORDS, "chem")
        match_any(CLINICAL_KEYWORDS, "clinical")
        match_any(MATERIALS_KEYWORDS, "materials")
        # Escalada simple: si CRITICAL y keywords peligrosos => mantener bloqueado
        blocked = not decision.allowed
        level = decision.level
        risk_score = decision.risk_score
        # Escalado: si HIGH + bio/chem o si MEDIUM con ambas bio+chem => elevar
        if (level == "HIGH" and ("keyword:bio" in reasons or "keyword:chem" in reasons)) or \
           (level == "MEDIUM" and "keyword:bio" in reasons and "keyword:chem" in reasons):
            level = "CRITICAL"
            risk_score = max(risk_score, 12)
            blocked = True
            reasons.append("escalated:bio_chem")
        result = RiskResult(
            level=level,
            risk_score=risk_score,
            ethical_level=decision.level,
            blocked=blocked,
            reasons=reasons if reasons else [decision.reason],
        )
        
        # Log de evaluación de riesgo
        try:
            audit_logger.log_risk_assessment(
                domain=domain,
                description=description,
                level=result.level,
                risk_score=result.risk_score,
                blocked=result.blocked,
                reasons=result.reasons,
                user_id=req.user_id,
                metadata={
                    "data_sensitivity": data_sensitivity,
                    "declared_intent": declared_intent,
                    "justification": justification,
                    "ethical_level": result.ethical_level
                }
            )
        except Exception as e:
            # No fallar la evaluación por error de logging
            pass
        
        return result

risk_assessment = RiskAssessment()
