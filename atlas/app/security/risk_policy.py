"""
Risk Policy module
This is a compatibility stub for risk policy functionality
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class RiskLevel(str, Enum):
    """Risk levels for policy decisions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyAction(str, Enum):
    """Actions that can be taken based on risk assessment"""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    ESCALATE = "escalate"


class RiskAssessment:
    """Risk assessment result"""
    
    def __init__(self, 
                 risk_level: RiskLevel,
                 confidence: float,
                 factors: List[str],
                 metadata: Optional[Dict[str, Any]] = None):
        self.risk_level = risk_level
        self.confidence = confidence
        self.factors = factors
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "risk_level": self.risk_level.value,
            "confidence": self.confidence,
            "factors": self.factors,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class RiskPolicy:
    """Risk policy for decision making"""
    
    def __init__(self):
        self.policies = {}
        self.default_action = PolicyAction.WARN

    def assess_risk_sync(
        self,
        context: Dict[str, Any],
        operation: str = "default",
    ) -> RiskAssessment:
        """Assess actor and operation risk using app/security misuse policy."""
        risk_factors: list[str] = []
        risk_score = 0.0

        content = context.get("content")
        if content is None:
            content = {
                "prompt": context.get("prompt", ""),
                "query": context.get("query", ""),
                "hypothesis": context.get("hypothesis", ""),
                "tool_input": context.get("tool_input", ""),
                "description": context.get("description", ""),
            }

        try:
            from app.security.misuse_guard import misuse_guard

            misuse_decision = misuse_guard.evaluate(
                operation=operation,
                content=content,
                domain=str(context.get("domain", "")),
                tool_name=str(context.get("tool_name", "")),
                actor_id=str(context.get("actor_id", context.get("user_id", "anonymous"))),
                metadata={"source": "risk_policy"},
            )
        except Exception as exc:
            return RiskAssessment(
                risk_level=RiskLevel.CRITICAL,
                confidence=0.95,
                factors=["misuse_guard_unavailable"],
                metadata={"operation": operation, "error": str(exc), "score": 1.0},
            )

        if not misuse_decision.allowed:
            return RiskAssessment(
                risk_level=RiskLevel.CRITICAL,
                confidence=0.98,
                factors=misuse_decision.matched_rules,
                metadata={
                    "operation": operation,
                    "score": 1.0,
                    "misuse_decision": misuse_decision.to_dict(),
                },
            )

        if context.get("user_permissions", []):
            if "admin" in context["user_permissions"]:
                risk_score += 0.1
                risk_factors.append("admin_permissions")

        if context.get("data_sensitivity", "low") in {"high", "critical"}:
            risk_score += 0.3
            risk_factors.append("sensitive_data")

        if context.get("network_source") == "external":
            risk_score += 0.2
            risk_factors.append("external_network")

        if context.get("declared_intent") in {"dual_use", "defense"}:
            risk_score += 0.25
            risk_factors.append("dual_use_or_defense_intent")

        if context.get("domain") in {"synthetic_biology", "gain_of_function", "biosecurity_assessment"}:
            risk_score += 0.35
            risk_factors.append("high_risk_domain")

        if risk_score >= 0.7:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.5:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.3:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return RiskAssessment(
            risk_level=risk_level,
            confidence=min(0.95, 0.5 + risk_score),
            factors=risk_factors,
            metadata={"operation": operation, "score": risk_score},
        )

    async def assess_risk(
        self,
        context: Dict[str, Any],
        operation: str = "default",
    ) -> RiskAssessment:
        """Async-compatible risk assessment."""
        return self.assess_risk_sync(context, operation)
    
    def get_policy_action(self, 
                         assessment: RiskAssessment,
                         context: Optional[Dict[str, Any]] = None) -> PolicyAction:
        """Get policy action based on risk assessment"""
        if assessment.risk_level == RiskLevel.CRITICAL:
            return PolicyAction.BLOCK
        elif assessment.risk_level == RiskLevel.HIGH:
            return PolicyAction.ESCALATE
        elif assessment.risk_level == RiskLevel.MEDIUM:
            return PolicyAction.WARN
        else:
            return PolicyAction.ALLOW
    
    def evaluate_policy(self, 
                       context: Dict[str, Any],
                       operation: str = "default") -> Dict[str, Any]:
        """Evaluate policy for a given context"""
        assessment = self.assess_risk_sync(context, operation)
        action = self.get_policy_action(assessment, context)
        
        return {
            "assessment": assessment.to_dict(),
            "action": action.value,
            "timestamp": datetime.now().isoformat()
        }


# Global risk policy instance
risk_policy = RiskPolicy()

# Risk policy store for compatibility
risk_policy_store = {
    "global_policy": risk_policy,
    "cached_assessments": {},
    "policy_history": []
}


async def assess_risk(context: Dict[str, Any], operation: str = "default") -> RiskAssessment:
    """Assess risk using the global policy"""
    return await risk_policy.assess_risk(context, operation)


def evaluate_policy(context: Dict[str, Any], operation: str = "default") -> Dict[str, Any]:
    """Evaluate policy using the global policy"""
    return risk_policy.evaluate_policy(context, operation)


def get_policy_action(assessment: RiskAssessment, context: Optional[Dict[str, Any]] = None) -> PolicyAction:
    """Get policy action using the global policy"""
    return risk_policy.get_policy_action(assessment, context)


# Compatibility exports
__all__ = [
    "RiskLevel",
    "PolicyAction", 
    "RiskAssessment",
    "RiskPolicy",
    "risk_policy",
    "risk_policy_store",
    "assess_risk",
    "evaluate_policy",
    "get_policy_action"
]
