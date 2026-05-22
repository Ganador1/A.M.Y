"""Plausibility related ORM models."""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base


class HypothesisPlausibilityMetricRecord(Base):
    """Almacena componentes y resultado de un cálculo de plausibilidad para una hipótesis.

    Se guarda cada evaluación para histórico y potencial entrenamiento ML.
    """
    __tablename__ = "hypothesis_plausibility_metrics"

    id = Column(Integer, primary_key=True, index=True)
    hypothesis_uuid = Column(String(64), index=True, nullable=False)
    raw_score = Column(Float, nullable=False)
    composite = Column(Float, nullable=False)
    duplication_penalty = Column(Float, nullable=False)
    domain_weight = Column(Float, nullable=True)
    evidence_adjustment = Column(Float, nullable=True)
    model_score = Column(Float, nullable=True)  # salida de modelo ML calibrado si existe
    components = Column(JSON, nullable=False)  # dict con breakdown
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_pl_metric_hyp_created", "hypothesis_uuid", "created_at"),
    )
