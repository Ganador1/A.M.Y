"""
Enhanced Plausibility Scoring Service
Integrates advanced ML-based scoring with existing infrastructure
"""

import sys
from pathlib import Path

# Add improvements to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'improvements'))

from improvements.advanced_plausibility_scorer import AdvancedPlausibilityScorerV2
from typing import Dict, Any, Optional

# Singleton instance
_advanced_scorer = None

def get_plausibility_service(config: Optional[Dict[str, Any]] = None):
    """Get enhanced plausibility scoring service"""
    global _advanced_scorer
    if _advanced_scorer is None:
        _advanced_scorer = AdvancedPlausibilityScorerV2(config)
    return _advanced_scorer

# Compatibility wrapper
class PlausibilityScoringService:
    """Wrapper for backward compatibility"""
    
    def __init__(self):
        self.scorer = get_plausibility_service()
    
    async def score_hypothesis(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Score hypothesis using advanced ML"""
        result = await self.scorer.score_hypothesis(hypothesis)
        
        # Convert to expected format
        return {
            "success": result.get("success", True),
            "composite": result.get("final_score", 0.5),
            "components": result.get("confidence_breakdown", {}),
            "model_score": result.get("final_score", 0.5),
            "warnings": result.get("recommendations", [])
        }
