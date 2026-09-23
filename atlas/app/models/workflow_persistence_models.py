"""
Workflow persistence ORM models (Workflows v1.1)
Separate module to avoid coupling with legacy database_models imports.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class WorkflowRecord(Base):
    """Persisted workflow metadata."""
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, index=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    steps = relationship("WorkflowStepRecord", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowStepRecord(Base):
    """Persisted workflow step definition and execution summary."""
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False, index=True)
    step_id = Column(String(64), nullable=False)
    service_type = Column(String(64), nullable=False)
    operation = Column(String(128), nullable=False)
    parameters = Column(JSON, nullable=True)
    dependencies = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, index=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    workflow = relationship("WorkflowRecord", back_populates="steps")


class StepExecutionRecord(Base):
    """Detailed execution attempts per step (for retries/metrics)."""
    __tablename__ = "workflow_step_executions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_step_id = Column(Integer, ForeignKey("workflow_steps.id"), nullable=False, index=True)
    attempt = Column(Integer, default=1)
    status = Column(String(20), nullable=False)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_sec = Column(Float, nullable=True)
    cache_hit = Column(Boolean, default=False)
    timeout_sec = Column(Integer, nullable=True)
