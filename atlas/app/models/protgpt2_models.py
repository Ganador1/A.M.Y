"""
ProtGPT2 Database Models
SQLAlchemy models for storing protein design data
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ProteinSequence(Base):
    """Model for storing generated protein sequences"""
    __tablename__ = "protein_sequences"

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(String(50), unique=True, index=True, nullable=False)
    sequence = Column(Text, nullable=False)
    prompt_used = Column(Text, nullable=False)
    generation_method = Column(String(50), default="ProtGPT2")
    confidence_score = Column(Float)
    perplexity_score = Column(Float)

    # Sequence properties
    length = Column(Integer)
    molecular_weight = Column(Float)
    isoelectric_point = Column(Float)
    instability_index = Column(Float)
    hydrophobicity_score = Column(Float)

    # Generation parameters
    temperature = Column(Float, default=0.8)
    top_p = Column(Float, default=0.9)
    max_length = Column(Integer, default=500)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    properties = relationship("ProteinProperty", back_populates="sequence", cascade="all, delete-orphan")
    optimizations = relationship("ProteinOptimization", back_populates="sequence", cascade="all, delete-orphan")
    domains = relationship("DomainInsertion", back_populates="sequence", cascade="all, delete-orphan")


class ProteinProperty(Base):
    """Model for storing protein properties and predictions"""
    __tablename__ = "protein_properties"

    id = Column(Integer, primary_key=True, index=True)
    sequence_id = Column(Integer, ForeignKey("protein_sequences.id"), nullable=False)
    property_name = Column(String(100), nullable=False)
    property_value = Column(Float)
    property_type = Column(String(50))  # predicted, calculated, experimental
    confidence = Column(Float)
    source = Column(String(100))  # ProtGPT2, AlphaFold, experimental
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    sequence = relationship("ProteinSequence", back_populates="properties")


class ProteinOptimization(Base):
    """Model for storing protein optimization results"""
    __tablename__ = "protein_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    sequence_id = Column(Integer, ForeignKey("protein_sequences.id"), nullable=False)
    original_sequence = Column(Text, nullable=False)
    optimized_sequence = Column(Text, nullable=False)
    target_property = Column(String(100), nullable=False)
    optimization_score = Column(Float)
    rationale = Column(Text)

    # Mutations data
    mutations_json = Column(JSON)  # Store mutations as JSON array
    mutation_count = Column(Integer)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    sequence = relationship("ProteinSequence", back_populates="optimizations")


class DomainInsertion(Base):
    """Model for storing domain insertion designs"""
    __tablename__ = "domain_insertions"

    id = Column(Integer, primary_key=True, index=True)
    sequence_id = Column(Integer, ForeignKey("protein_sequences.id"), nullable=False)
    base_sequence = Column(Text, nullable=False)
    modified_sequence = Column(Text, nullable=False)
    inserted_domain = Column(Text, nullable=False)
    domain_function = Column(String(100))
    insertion_position = Column(Integer)
    structural_compatibility = Column(Float)
    functional_prediction = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    sequence = relationship("ProteinSequence", back_populates="domains")


class BatchGeneration(Base):
    """Model for storing batch generation jobs"""
    __tablename__ = "batch_generations"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(50), unique=True, index=True, nullable=False)
    base_prompt = Column(Text, nullable=False)
    num_requested = Column(Integer, nullable=False)
    num_generated = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, running, completed, failed

    # Generation parameters
    temperature = Column(Float, default=0.8)
    top_p = Column(Float, default=0.9)
    max_length = Column(Integer, default=500)

    # Results
    generated_sequences = Column(JSON)  # Array of sequence IDs
    error_message = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    sequences = relationship("ProteinSequence", secondary="batch_sequence_association")


class BatchSequenceAssociation(Base):
    """Association table for batch generations and sequences"""
    __tablename__ = "batch_sequence_association"

    batch_id = Column(Integer, ForeignKey("batch_generations.id"), primary_key=True)
    sequence_id = Column(Integer, ForeignKey("protein_sequences.id"), primary_key=True)


class ProtGPT2ModelMetrics(Base):
    """Model for storing ProtGPT2 model performance metrics"""
    __tablename__ = "protgpt2_metrics"

    id = Column(Integer, primary_key=True, index=True)
    operation_type = Column(String(50), nullable=False)  # generation, optimization, perplexity
    model_version = Column(String(50), default="nferruz/ProtGPT2")
    input_length = Column(Integer)
    output_length = Column(Integer)
    processing_time = Column(Float)  # seconds
    perplexity_score = Column(Float)
    confidence_score = Column(Float)
    success = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
