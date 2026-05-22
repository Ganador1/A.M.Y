"""Experiment Scheduler ORM models."""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum


class ExperimentJobState(str, Enum):
    """Estados posibles de jobs experimentales."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExperimentJobRecord(Base):
    """Tabla de jobs experimentales persistentes para scheduler.

    Permite programar experimentos con delay, retry, intervalos y prioridades.
    Se integra con AdvancedAsyncProcessor para ejecución efectiva.
    """
    __tablename__ = "experiment_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_uuid = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    payload_json = Column(JSON, nullable=False)  # parámetros del experimento
    state = Column(String(20), nullable=False, default=ExperimentJobState.PENDING, index=True)
    
    # Scheduling
    run_at = Column(DateTime(timezone=True), nullable=True)  # cuándo ejecutar (None = inmediato)
    next_run_at = Column(DateTime(timezone=True), nullable=True, index=True)  # próxima ejecución (intervals)
    interval_seconds = Column(Integer, nullable=True)  # repetir cada N segundos (opcional)
    
    # Retries
    max_retries = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)  
    error_message = Column(String(1000), nullable=True)  # cambiado nombre
    
    # Prioridad y metadatos
    priority = Column(Integer, default=0)  # mayor valor = mayor prioridad
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Opcional: referencia a resultado si se guarda aparte
    result_reference = Column(String(255), nullable=True)

    __table_args__ = (
        Index("ix_exp_jobs_state_priority", "state", "priority"),
        Index("ix_exp_jobs_next_run", "next_run_at"),
    )
