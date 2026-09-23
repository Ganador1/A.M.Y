"""
Hypothesis persistence ORM models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class HypothesisRecord(Base):
    """Persisted scientific hypothesis with metadata and counters."""
    __tablename__ = "hypotheses"

    id = Column(Integer, primary_key=True, index=True)
    # Public stable id to reference from APIs (UUID string)
    hypothesis_uuid = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(64), nullable=False, index=True)
    variables = Column(JSON, nullable=True)
    assumptions = Column(JSON, nullable=True)
    expected_outcome = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    status = Column(String(20), default="generated", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    tested_at = Column(DateTime(timezone=True), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    evidence_count = Column(Integer, default=0)
    refinement_count = Column(Integer, default=0)

    # Links (optional textual IDs to external systems)
    linked_workflow_id = Column(String(64), nullable=True, index=True)
    linked_experiment_id = Column(String(64), nullable=True, index=True)

    evidences = relationship("HypothesisEvidenceRecord", back_populates="hypothesis", cascade="all, delete-orphan")
    refinements = relationship("HypothesisRefinementRecord", back_populates="hypothesis", cascade="all, delete-orphan")


class HypothesisEvidenceRecord(Base):
    """Evidence items associated with a hypothesis (literature, experiments, analysis)."""
    __tablename__ = "hypothesis_evidences"

    id = Column(Integer, primary_key=True, index=True)
    hypothesis_id = Column(Integer, ForeignKey("hypotheses.id"), nullable=False, index=True)
    evidence_type = Column(String(64), nullable=True)  # e.g., literature, experiment, analysis
    details = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)
    support_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hypothesis = relationship("HypothesisRecord", back_populates="evidences")


class HypothesisRefinementRecord(Base):
    """Refinement history entries for a hypothesis."""
    __tablename__ = "hypothesis_refinements"

    id = Column(Integer, primary_key=True, index=True)
    hypothesis_id = Column(Integer, ForeignKey("hypotheses.id"), nullable=False, index=True)
    changes = Column(JSON, nullable=True)
    confidence_delta = Column(Float, default=0.0)
    manual = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hypothesis = relationship("HypothesisRecord", back_populates="refinements")
