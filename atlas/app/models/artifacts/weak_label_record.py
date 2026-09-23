"""
Weak Label Record Model - AXIOM META 4
Pydantic v2 model for tracking weak label generation and quality metrics.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class WeakLabelSource(str, Enum):
    """Sources for weak label generation"""
    LLM_CLASSIFIER = "llm_classifier"
    HEURISTIC_RULES = "heuristic_rules"
    KEYWORD_MATCHING = "keyword_matching"
    CITATION_ANALYSIS = "citation_analysis"
    ENSEMBLE_VOTING = "ensemble_voting"
    HUMAN_ANNOTATION = "human_annotation"


class WeakLabelQuality(str, Enum):
    """Quality levels for weak labels"""
    HIGH = "high"          # >0.9 confidence
    MEDIUM = "medium"      # 0.7-0.9 confidence  
    LOW = "low"           # 0.5-0.7 confidence
    UNCERTAIN = "uncertain" # <0.5 confidence


class WeakLabelRecord(BaseModel):
    """
    Record for tracking weak label generation, sources and quality metrics.
    Used in pipeline_v4.py for reproducible weak supervision.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    # Core identification
    record_id: str = Field(..., description="Unique identifier for this weak label record")
    hypothesis_id: str = Field(..., description="ID of the hypothesis being labeled")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    # Label information
    weak_label: int = Field(..., ge=0, le=1, description="Binary weak label (0=implausible, 1=plausible)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the weak label")
    quality_level: WeakLabelQuality = Field(..., description="Assessed quality level")
    
    # Source tracking
    primary_source: WeakLabelSource = Field(..., description="Primary source of the weak label")
    contributing_sources: List[WeakLabelSource] = Field(default_factory=list, description="Additional sources used")
    source_weights: Dict[str, float] = Field(default_factory=dict, description="Weights for ensemble sources")
    
    # Content and features
    hypothesis_text: str = Field(..., min_length=10, description="Original hypothesis text")
    extracted_features: Dict[str, Any] = Field(default_factory=dict, description="Features extracted for labeling")
    
    # Quality metrics
    agreement_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Inter-source agreement")
    consistency_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Consistency with similar cases")
    
    # Metadata and lineage
    model_version: str = Field(..., description="Version of the weak labeling model/pipeline")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters used for labeling")
    git_commit: Optional[str] = Field(None, description="Git commit hash when label was generated")
    
    # Validation and review
    human_validated: bool = Field(default=False, description="Whether label was human-validated")
    validation_notes: Optional[str] = Field(None, description="Notes from human validation")
    flagged_for_review: bool = Field(default=False, description="Whether flagged for manual review")
    
    def to_training_format(self) -> Dict[str, Any]:
        """Convert to format suitable for ML training"""
        return {
            "text": self.hypothesis_text,
            "label": self.weak_label,
            "weight": self.confidence_score,
            "source": self.primary_source.value,
            "quality": self.quality_level.value
        }
    
    def get_reliability_score(self) -> float:
        """Calculate overall reliability score for this weak label"""
        base_score = self.confidence_score
        
        # Boost for high-quality sources
        if self.primary_source in [WeakLabelSource.HUMAN_ANNOTATION, WeakLabelSource.ENSEMBLE_VOTING]:
            base_score *= 1.2
        
        # Boost for agreement and consistency
        if self.agreement_score:
            base_score *= (0.8 + 0.2 * self.agreement_score)
        
        if self.consistency_score:
            base_score *= (0.9 + 0.1 * self.consistency_score)
        
        # Penalty for uncertain quality
        if self.quality_level == WeakLabelQuality.UNCERTAIN:
            base_score *= 0.7
        elif self.quality_level == WeakLabelQuality.LOW:
            base_score *= 0.85
        
        return min(base_score, 1.0)
    
    def should_include_in_training(self, min_reliability: float = 0.6) -> bool:
        """Determine if this weak label should be included in training"""
        return (
            self.get_reliability_score() >= min_reliability and
            not self.flagged_for_review and
            self.quality_level != WeakLabelQuality.UNCERTAIN
        )