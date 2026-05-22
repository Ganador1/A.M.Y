"""
Risk Policy module for compatibility
This is a compatibility stub that redirects to the correct module
"""

# Import specific items from the correct location
from app.security.risk_policy import (
    RiskLevel,
    PolicyAction, 
    RiskAssessment,
    RiskPolicy,
    risk_policy,
    risk_policy_store,
    assess_risk,
    evaluate_policy,
    get_policy_action
)

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