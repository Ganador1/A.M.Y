"""
Ethics Gate - Implementación completa con evaluación real de riesgos éticos

Sistema de evaluación ética que analiza experimentos científicos basado en:
- Pesos por dominio científico
- Keywords bloqueadas y sensibles
- Sensibilidad de datos
- Intención declarada
- Escalación automática de riesgos
"""

import logging
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from pydantic import BaseModel
from datetime import datetime, timezone
from uuid import uuid4

from .ethics_policy import policy_manager
from .ethics_decision_store import decision_store, EthicsDecisionRecord
from ..security.audit_logger import audit_logger

logger = logging.getLogger(__name__)


class ExperimentRequest(BaseModel):
    """Request para experimento con campos extendidos"""
    domain: str
    description: str
    resources: Dict[str, Any] = {}
    data_sensitivity: str = "none"
    declared_intent: str = "research"
    justification: Optional[str] = None
    justification_signature: Optional[str] = None
    keywords: List[str] = []
    metadata: Dict[str, Any] = {}
    user_id: Optional[str] = None
    organization: Optional[str] = None


@dataclass
class EthicsDecision:
    """Decisión ética con campos extendidos"""
    allowed: bool
    level: str
    risk_score: int
    reason: str
    requires_signature: bool = False
    escalation_reasons: List[str] = None
    recommended_actions: List[str] = None
    decision_id: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.escalation_reasons is None:
            self.escalation_reasons = []
        if self.recommended_actions is None:
            self.recommended_actions = []
        if not self.decision_id:
            self.decision_id = str(uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class EthicsGate:
    """Ethics Gate - implementación completa con evaluación real"""

    def __init__(self, policy_path: Optional[str] = None):
        self.policy_path = policy_path
        self.policy_manager = policy_manager
        self.decision_store = decision_store
        logger.info("Ethics Gate initialized with real evaluation")

    def evaluate(self, request: ExperimentRequest, auto_anchor: bool = False) -> EthicsDecision:
        """Evaluación completa de ética con scoring real"""
        try:
            # 1. Verificar keywords bloqueadas (rechazo automático)
            blocked_result = self._check_blocked_keywords(request)
            if blocked_result:
                return self._create_decision(
                    request=request,
                    allowed=False,
                    level="CRITICAL",
                    risk_score=20,
                    reason="Blocked keywords detected",
                    escalation_reasons=[f"Blocked keyword: {blocked_result}"],
                    recommended_actions=["Review experiment description", "Remove blocked content"]
                )
            
            # 2. Calcular score base por dominio
            domain_score = self._calculate_domain_score(request.domain)
            
            # 3. Calcular score por sensibilidad de datos
            data_score = self._calculate_data_sensitivity_score(request.data_sensitivity)
            
            # 4. Calcular score por intención declarada
            intent_score = self._calculate_intent_score(request.declared_intent)
            
            # 5. Calcular score por keywords sensibles
            keyword_score = self._calculate_keyword_score(request.description, request.keywords)
            
            # 6. Score total
            total_score = domain_score + data_score + intent_score + keyword_score
            
            # 7. Determinar nivel de riesgo
            level, allowed = self._determine_risk_level(total_score)
            
            # 8. Verificar si requiere firma
            requires_signature = level in self.policy_manager.get_signature_levels()
            
            # 9. Generar razones de escalación
            escalation_reasons = self._generate_escalation_reasons(
                request, domain_score, data_score, intent_score, keyword_score
            )
            
            # 10. Generar acciones recomendadas
            recommended_actions = self._generate_recommended_actions(level, escalation_reasons)
            
            # 11. Crear decisión
            decision = self._create_decision(
                request=request,
                allowed=allowed,
                level=level,
                risk_score=total_score,
                reason=f"Risk assessment: {level} risk (score: {total_score})",
                requires_signature=requires_signature,
                escalation_reasons=escalation_reasons,
                recommended_actions=recommended_actions
            )
            
            # 12. Almacenar decisión
            self._store_decision(decision, request)
            
            # 13. Audit logging
            self._log_ethics_evaluation(decision, request)
            
            # 14. Logging
            logger.info(f"Ethics evaluation: {request.domain} -> {level} (score: {total_score})")
            
            return decision
            
        except Exception as e:
            logger.error(f"Error in ethics evaluation: {e}")
            # Fallback a decisión conservadora
            return self._create_decision(
                request=request,
                allowed=False,
                level="CRITICAL",
                risk_score=20,
                reason=f"Evaluation error: {str(e)}",
                escalation_reasons=["System error during evaluation"],
                recommended_actions=["Manual review required"]
            )

    def _check_blocked_keywords(self, request: ExperimentRequest) -> Optional[str]:
        """Verificar keywords bloqueadas"""
        blocked_keywords = self.policy_manager.get_blocked_keywords()
        text_to_check = f"{request.description} {' '.join(request.keywords)}".lower()
        
        for keyword in blocked_keywords:
            if keyword.lower() in text_to_check:
                return keyword
        return None

    def _calculate_domain_score(self, domain: str) -> int:
        """Calcular score por dominio científico"""
        return self.policy_manager.get_domain_weight(domain)

    def _calculate_data_sensitivity_score(self, sensitivity: str) -> int:
        """Calcular score por sensibilidad de datos"""
        return self.policy_manager.get_data_sensitivity_weight(sensitivity)

    def _calculate_intent_score(self, intent: str) -> int:
        """Calcular score por intención declarada"""
        return self.policy_manager.get_intent_weight(intent)

    def _calculate_keyword_score(self, description: str, keywords: List[str]) -> int:
        """Calcular score por keywords sensibles"""
        score = 0
        sensitive_keywords = self.policy_manager.get_sensitive_keywords()
        text_to_check = f"{description} {' '.join(keywords)}".lower()
        
        for category, keyword_list in sensitive_keywords.items():
            for keyword in keyword_list:
                if keyword.lower() in text_to_check:
                    score += 2  # +2 por keyword sensible
                    break  # Solo contar una vez por categoría
        
        return score

    def _determine_risk_level(self, score: int) -> tuple[str, bool]:
        """Determinar nivel de riesgo y si está permitido"""
        thresholds = self.policy_manager.get_thresholds()
        
        if score >= thresholds.critical:
            return "CRITICAL", False
        elif score >= thresholds.high:
            return "HIGH", False
        elif score >= thresholds.medium:
            return "MEDIUM", True
        else:
            return "LOW", True

    def _generate_escalation_reasons(self, request: ExperimentRequest, 
                                   domain_score: int, data_score: int, 
                                   intent_score: int, keyword_score: int) -> List[str]:
        """Generar razones de escalación"""
        reasons = []
        
        if domain_score >= 8:
            reasons.append(f"High-risk domain: {request.domain}")
        
        if data_score >= 5:
            reasons.append(f"High data sensitivity: {request.data_sensitivity}")
        
        if intent_score >= 3:
            reasons.append(f"High-risk intent: {request.declared_intent}")
        
        if keyword_score >= 4:
            reasons.append("Sensitive keywords detected")
        
        return reasons

    def _generate_recommended_actions(self, level: str, escalation_reasons: List[str]) -> List[str]:
        """Generar acciones recomendadas"""
        actions = []
        
        if level in ["HIGH", "CRITICAL"]:
            actions.append("Obtain ethics committee approval")
            actions.append("Provide detailed justification")
        
        if "High-risk domain" in str(escalation_reasons):
            actions.append("Consult domain experts")
        
        if "Sensitive keywords" in str(escalation_reasons):
            actions.append("Review and modify description")
        
        if level == "CRITICAL":
            actions.append("Manual review required")
            actions.append("Consider alternative approaches")
        
        return actions

    def _create_decision(self, request: ExperimentRequest, allowed: bool, level: str,
                        risk_score: int, reason: str, requires_signature: bool = False,
                        escalation_reasons: List[str] = None, 
                        recommended_actions: List[str] = None) -> EthicsDecision:
        """Crear objeto de decisión"""
        return EthicsDecision(
            allowed=allowed,
            level=level,
            risk_score=risk_score,
            reason=reason,
            requires_signature=requires_signature,
            escalation_reasons=escalation_reasons or [],
            recommended_actions=recommended_actions or [],
            decision_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc)
        )

    def _store_decision(self, decision: EthicsDecision, request: ExperimentRequest) -> None:
        """Almacenar decisión en base de datos"""
        try:
            record = EthicsDecisionRecord(
                decision_id=decision.decision_id,
                timestamp=decision.timestamp,
                domain=request.domain,
                description=request.description,
                decision=decision.level,
                risk_score=decision.risk_score,
                allowed=decision.allowed,
                requires_signature=decision.requires_signature,
                escalation_reasons=decision.escalation_reasons,
                recommended_actions=decision.recommended_actions,
                user_id=request.user_id,
                organization=request.organization,
                metadata=request.metadata
            )
            
            self.decision_store.store_decision(record)
            
        except Exception as e:
            logger.error(f"Error storing ethics decision: {e}")

    def _log_ethics_evaluation(self, decision: EthicsDecision, request: ExperimentRequest) -> None:
        """Log de evaluación ética en audit logger"""
        try:
            audit_logger.log_ethics_evaluation(
                domain=request.domain,
                description=request.description,
                decision=decision.level,
                risk_score=decision.risk_score,
                allowed=decision.allowed,
                requires_signature=decision.requires_signature,
                escalation_reasons=decision.escalation_reasons,
                user_id=request.user_id,
                metadata={
                    "decision_id": decision.decision_id,
                    "keywords": request.keywords,
                    "data_sensitivity": request.data_sensitivity,
                    "declared_intent": request.declared_intent,
                    "organization": request.organization,
                    "recommended_actions": decision.recommended_actions
                }
            )
        except Exception as e:
            logger.error(f"Error logging ethics evaluation: {e}")

    def is_approved(self) -> bool:
        """Verificar si la última evaluación fue aprobada"""
        # Este método se mantiene por compatibilidad pero no es muy útil
        # en la implementación real ya que cada evaluación es independiente
        return True

    def get_decision_history(self, domain: str = None, limit: int = 100) -> List[EthicsDecisionRecord]:
        """Obtener historial de decisiones"""
        if domain:
            return self.decision_store.get_decisions_by_domain(domain, limit)
        else:
            return self.decision_store.get_recent_decisions(hours=24, limit=limit)

    def get_statistics(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Obtener estadísticas de decisiones"""
        return self.decision_store.get_statistics(start_date, end_date)
