"""
AXIOM Database Models
====================

SQLAlchemy ORM models for the AXIOM Mathematics AI Engine database.

This module defines all database tables and relationships used by the AXIOM system
for storing users, calculations, cache data, metrics, and other operational data.

Database Schema Overview:
------------------------

The AXIOM database consists of the following main entities:

1. **User Management**:
   - User: User accounts and authentication
   - UserSession: User session management

2. **Computation Storage**:
   - Calculation: Mathematical calculation history
   - CachedResult: Computation result caching

3. **System Monitoring**:
   - SystemMetric: System performance metrics
   - ErrorLog: Error tracking and debugging
   - APIRequestLog: API usage logging

4. **Data Management**:
   - ScientificDataset: Scientific data storage

Key Features:
- Comprehensive indexing for performance
- Foreign key relationships with referential integrity
- JSON storage for flexible data structures
- Automatic timestamp management
- Soft deletion support where applicable

Usage Examples:
--------------

Creating a user:
    >>> from app.models import User
    >>> user = User(username="john", email="john@example.com", hashed_password="hash")
    >>> session.add(user)
    >>> session.commit()

Storing a calculation:
    >>> calc = Calculation(
    ...     user_id=1,
    ...     operation_type="arithmetic",
    ...     operation_name="addition",
    ...     input_data={"a": 5, "b": 3},
    ...     result_data={"result": 8},
    ...     execution_time=0.001
    ... )
    >>> session.add(calc)
    >>> session.commit()

Author: AXIOM Mathematics AI Engine Team
Date: September 2025
Version: 1.0.0
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """
    User model for authentication and user management.

    This model stores user account information including authentication credentials,
    profile data, and administrative status. It serves as the central entity for
    user-related operations throughout the AXIOM system.

    Attributes:
        id (int): Primary key, auto-incrementing
        username (str): Unique username, max 50 characters
        email (str): Unique email address, max 100 characters
        hashed_password (str): Bcrypt-hashed password, max 255 characters
        full_name (str): User's full name, max 100 characters
        is_active (bool): Account activation status, defaults to True
        is_admin (bool): Administrative privileges flag, defaults to False
        created_at (datetime): Account creation timestamp (UTC)
        updated_at (datetime): Last account update timestamp (UTC)

    Relationships:
        calculations: One-to-many relationship with Calculation model
        user_sessions: One-to-many relationship with UserSession model

    Indexes:
        - Primary key on id
        - Unique index on username
        - Unique index on email

    Example:
        >>> user = User(
        ...     username="johndoe",
        ...     email="john@example.com",
        ...     hashed_password=hash_password("secure123"),
        ...     full_name="John Doe"
        ... )
        >>> session.add(user)
        >>> session.commit()
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    calculations = relationship("Calculation", back_populates="user")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class UserSession(Base):
    """
    User session model for tracking user activity and authentication.

    This model manages user sessions for web authentication, tracking login
    activity, IP addresses, and session expiration. It provides session-based
    security and audit capabilities.

    Attributes:
        id (int): Primary key, auto-incrementing
        user_id (int): Foreign key to users table
        session_token (str): Unique session token, max 255 characters
        ip_address (str): Client IP address, max 45 characters (IPv6 compatible)
        user_agent (str): Client user agent string
        created_at (datetime): Session creation timestamp (UTC)
        expires_at (datetime): Session expiration timestamp (UTC)
        is_active (bool): Session active status, defaults to True

    Relationships:
        user: Many-to-one relationship with User model

    Indexes:
        - Primary key on id
        - Unique index on session_token

    Example:
        >>> from datetime import datetime, timedelta
        >>> session = UserSession(
        ...     user_id=1,
        ...     session_token=generate_token(),
        ...     ip_address="192.168.1.100",
        ...     expires_at=datetime.utcnow() + timedelta(hours=24)
        ... )
        >>> db_session.add(session)
        >>> db_session.commit()
    """
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="user_sessions")

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"


class Calculation(Base):
    """
    Model for storing mathematical calculations and results.

    This model stores the history of all mathematical computations performed
    by the AXIOM system, including input parameters, results, execution times,
    and status information.

    Attributes:
        id (int): Primary key, auto-incrementing
        user_id (int): Foreign key to users table (nullable for anonymous calculations)
        operation_type (str): Type of operation (e.g., 'arithmetic', 'calculus', 'pde')
        operation_name (str): Specific operation name (e.g., 'add', 'derivative')
        input_data (dict): Input parameters as JSON
        result_data (dict): Computation result as JSON
        execution_time (float): Execution time in seconds
        status (str): Computation status ('completed', 'failed', 'running')
        error_message (str): Error message if computation failed
        created_at (datetime): Calculation start timestamp (UTC)
        completed_at (datetime): Calculation completion timestamp (UTC)

    Relationships:
        user: Many-to-one relationship with User model

    Indexes:
        - Primary key on id
        - Index on user_id, operation_type
        - Index on created_at
        - Index on status

    Example:
        >>> calc = Calculation(
        ...     user_id=1,
        ...     operation_type="arithmetic",
        ...     operation_name="addition",
        ...     input_data={"a": 5, "b": 3},
        ...     result_data={"result": 8},
        ...     execution_time=0.001,
        ...     status="completed"
        ... )
        >>> session.add(calc)
        >>> session.commit()
    """
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Allow anonymous calculations
    operation_type = Column(String(50), nullable=False, index=True)
    operation_name = Column(String(100), nullable=False)
    input_data = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=True)
    execution_time = Column(Float, nullable=True)
    status = Column(String(20), default="completed", index=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="calculations")

    # Indexes for performance
    __table_args__ = (
        Index('idx_calculation_user_type', 'user_id', 'operation_type'),
        Index('idx_calculation_created', 'created_at'),
        Index('idx_calculation_status', 'status'),
    )

    def __repr__(self):
        return f"<Calculation(id={self.id}, type='{self.operation_type}', status='{self.status}')>"


class CachedResult(Base):
    """
    Model for storing cached computation results.

    This model implements a caching system to store computation results and
    avoid redundant calculations. It includes TTL (time-to-live) functionality
    and access tracking for cache management.

    Attributes:
        id (int): Primary key, auto-incrementing
        cache_key (str): Unique cache key, max 255 characters
        operation_type (str): Type of operation that was cached
        input_data (dict): Input parameters as JSON
        result_data (dict): Cached result as JSON
        created_at (datetime): Cache entry creation timestamp (UTC)
        accessed_at (datetime): Last access timestamp (UTC)
        access_count (int): Number of times this cache entry was accessed
        ttl_seconds (int): Time-to-live in seconds

    Indexes:
        - Primary key on id
        - Unique index on cache_key
        - Index on operation_type

    Example:
        >>> cache = CachedResult(
        ...     cache_key="add_5_3",
        ...     operation_type="arithmetic",
        ...     input_data={"a": 5, "b": 3},
        ...     result_data={"result": 8},
        ...     ttl_seconds=3600
        ... )
        >>> session.add(cache)
        >>> session.commit()
    """
    __tablename__ = "cached_results"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    operation_type = Column(String(50), nullable=False, index=True)
    input_data = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accessed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    access_count = Column(Integer, default=1)
    ttl_seconds = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<CachedResult(id={self.id}, key='{self.cache_key[:20]}...')>"


class SystemMetric(Base):
    """
    Model for storing system performance metrics.

    This model stores various system performance metrics for monitoring and
    analytics purposes, including response times, resource usage, and other
    operational metrics.

    Attributes:
        id (int): Primary key, auto-incrementing
        metric_name (str): Name of the metric, max 100 characters
        metric_value (float): Numeric value of the metric
        metric_unit (str): Unit of measurement (e.g., 'ms', 'MB', 'percent')
        tags (dict): Additional metadata as JSON
        created_at (datetime): Metric timestamp (UTC)

    Indexes:
        - Primary key on id
        - Index on metric_name
        - Composite index on metric_name, created_at

    Example:
        >>> metric = SystemMetric(
        ...     metric_name="response_time",
        ...     metric_value=0.150,
        ...     metric_unit="seconds",
        ...     tags={"endpoint": "/api/calculate", "method": "POST"}
        ... )
        >>> session.add(metric)
        >>> session.commit()
    """
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_metric_name_time', 'metric_name', 'created_at'),
    )

    def __repr__(self):
        return f"<SystemMetric(name='{self.metric_name}', value={self.metric_value})>"


class ErrorLog(Base):
    """
    Model for storing application errors and exceptions.

    This model provides comprehensive error tracking and debugging capabilities,
    storing detailed information about application errors, stack traces, and
    contextual information.

    Attributes:
        id (int): Primary key, auto-incrementing
        error_type (str): Type of error, max 100 characters
        error_message (str): Error message text
        stack_trace (str): Full stack trace
        user_id (int): Foreign key to users table (nullable)
        endpoint (str): API endpoint where error occurred
        request_data (dict): Request data as JSON
        user_agent (str): Client user agent string
        ip_address (str): Client IP address, max 45 characters
        created_at (datetime): Error timestamp (UTC)

    Relationships:
        user: Many-to-one relationship with User model

    Indexes:
        - Primary key on id
        - Index on error_type

    Example:
        >>> error = ErrorLog(
        ...     error_type="ValidationError",
        ...     error_message="Invalid input parameters",
        ...     stack_trace=get_stack_trace(),
        ...     user_id=1,
        ...     endpoint="/api/calculate"
        ... )
        >>> session.add(error)
        >>> session.commit()
    """
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(100), nullable=False, index=True)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    endpoint = Column(String(255), nullable=True)
    request_data = Column(JSON, nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<ErrorLog(id={self.id}, type='{self.error_type}')>"


class APIRequestLog(Base):
    """
    Model for storing API request logs.

    This model tracks all API requests for analytics, debugging, and usage
    monitoring purposes. It provides comprehensive information about API usage
    patterns and performance.

    Attributes:
        id (int): Primary key, auto-incrementing
        user_id (int): Foreign key to users table (nullable for anonymous requests)
        method (str): HTTP method, max 10 characters
        endpoint (str): API endpoint, max 255 characters
        status_code (int): HTTP status code
        response_time (float): Response time in seconds
        request_size (int): Request size in bytes
        response_size (int): Response size in bytes
        user_agent (str): Client user agent string
        ip_address (str): Client IP address, max 45 characters
        created_at (datetime): Request timestamp (UTC)

    Relationships:
        user: Many-to-one relationship with User model

    Indexes:
        - Primary key on id
        - Index on endpoint
        - Composite index on endpoint, created_at
        - Composite index on user_id, created_at

    Example:
        >>> log = APIRequestLog(
        ...     user_id=1,
        ...     method="POST",
        ...     endpoint="/api/calculate",
        ...     status_code=200,
        ...     response_time=0.150,
        ...     request_size=1024,
        ...     response_size=512
        ... )
        >>> session.add(log)
        >>> session.commit()
    """
    __tablename__ = "api_request_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    method = Column(String(10), nullable=False)
    endpoint = Column(String(255), nullable=False, index=True)
    status_code = Column(Integer, nullable=False)
    response_time = Column(Float, nullable=True)
    request_size = Column(Integer, nullable=True)
    response_size = Column(Integer, nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")

    # Indexes
    __table_args__ = (
        Index('idx_request_endpoint_time', 'endpoint', 'created_at'),
        Index('idx_request_user_time', 'user_id', 'created_at'),
    )

    def __repr__(self):
        return f"<APIRequestLog(id={self.id}, endpoint='{self.endpoint}', status={self.status_code})>"


class ScientificDataset(Base):
    """
    Model for storing scientific datasets and research data.

    This model provides storage for scientific datasets, experimental data,
    and research materials used by the AXIOM system for advanced computations
    and analysis.

    Attributes:
        id (int): Primary key, auto-incrementing
        name (str): Dataset name, max 255 characters
        description (str): Dataset description
        dataset_type (str): Type of dataset (e.g., 'chemistry', 'physics', 'biology')
        data_format (str): Data format (e.g., 'json', 'csv', 'binary')
        data_content (dict): JSON data content
        file_path (str): File path for file-based datasets
        metadata_info (dict): Additional metadata as JSON
        created_by (int): Foreign key to users table
        created_at (datetime): Creation timestamp (UTC)
        updated_at (datetime): Last update timestamp (UTC)
        is_public (bool): Public visibility flag

    Relationships:
        creator: Many-to-one relationship with User model

    Example:
        >>> dataset = ScientificDataset(
        ...     name="experimental_data",
        ...     description="Experimental measurements",
        ...     dataset_type="physics",
        ...     data_format="json",
        ...     data_content={"measurements": [1.0, 2.0, 3.0]},
        ...     metadata_info={"units": "meters", "precision": 0.01},
        ...     created_by=1,
        ...     is_public=True
        ... )
        >>> session.add(dataset)
        >>> session.commit()
    """
    __tablename__ = "scientific_datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    dataset_type = Column(String(50), nullable=False, index=True)
    data_format = Column(String(20), nullable=False)
    data_content = Column(JSON, nullable=True)
    file_path = Column(String(500), nullable=True)
    metadata_info = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_public = Column(Boolean, default=False)

    # Relationships
    creator = relationship("User")

    def __repr__(self):
        return f"<ScientificDataset(id={self.id}, name='{self.name}', type='{self.dataset_type}')>"


# --- Knowledge Graph Models (AXIOM Extension v2.0) ---

class KnowledgeNode(Base):
    """
    Represents a scientific concept or entity in the knowledge graph.
    
    This model stores scientific concepts, entities, and their properties
    in a flexible schema that can represent knowledge from any domain.
    
    Attributes:
        id (int): Primary key
        name (str): Human-readable name of the concept/entity
        concept_type (str): Type classification (concept, entity, method, etc.)
        domain (str): Scientific domain (physics, biology, chemistry, etc.)
        properties (dict): Flexible JSON storage for domain-specific properties
        embeddings (dict): Pre-computed embeddings for semantic similarity
        confidence_score (float): Confidence in the knowledge accuracy (0.0-1.0)
        source_papers (list): References to source literature
        created_by (int): User who created this knowledge node
        created_at (datetime): Creation timestamp (UTC)
        updated_at (datetime): Last update timestamp (UTC)
        is_validated (bool): Whether this knowledge has been peer-validated
        validation_count (int): Number of validation confirmations

    Relationships:
        creator: Many-to-one relationship with User model
        outgoing_relations: One-to-many with KnowledgeRelation (as subject)
        incoming_relations: One-to-many with KnowledgeRelation (as object)

    Example:
        >>> node = KnowledgeNode(
        ...     name="Quantum Entanglement",
        ...     concept_type="concept",
        ...     domain="physics",
        ...     properties={"definition": "Non-local correlation phenomenon"},
        ...     confidence_score=0.95,
        ...     created_by=1,
        ...     is_validated=True
        ... )
        >>> session.add(node)
        >>> session.commit()
    """
    __tablename__ = "knowledge_nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    concept_type = Column(String(50), nullable=False, index=True)
    domain = Column(String(100), nullable=False, index=True)
    properties = Column(JSON, nullable=True)
    embeddings = Column(JSON, nullable=True)
    confidence_score = Column(Float, default=0.0, index=True)
    source_papers = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_validated = Column(Boolean, default=False, index=True)
    validation_count = Column(Integer, default=0)

    # Relationships
    creator = relationship("User")
    outgoing_relations = relationship("KnowledgeRelation", foreign_keys="KnowledgeRelation.subject_id", back_populates="subject")
    incoming_relations = relationship("KnowledgeRelation", foreign_keys="KnowledgeRelation.object_id", back_populates="object")

    def __repr__(self):
        return f"<KnowledgeNode(id={self.id}, name='{self.name}', domain='{self.domain}')>"


class KnowledgeRelation(Base):
    """
    Represents relationships between scientific concepts in the knowledge graph.
    
    This model captures semantic relationships between knowledge nodes,
    enabling complex reasoning and interdisciplinary knowledge discovery.
    
    Attributes:
        id (int): Primary key
        subject_id (int): Foreign key to source KnowledgeNode
        predicate (str): Type of relationship (causes, enables, requires, etc.)
        object_id (int): Foreign key to target KnowledgeNode
        strength (float): Relationship strength (0.0-1.0)
        context (dict): Contextual information about the relationship
        evidence_papers (list): Supporting literature references
        created_by (int): User who created this relationship
        created_at (datetime): Creation timestamp (UTC)
        updated_at (datetime): Last update timestamp (UTC)
        is_bidirectional (bool): Whether the relationship works both ways
        validation_status (str): Validation state (pending, validated, disputed)

    Relationships:
        subject: Many-to-one relationship with KnowledgeNode (source)
        object: Many-to-one relationship with KnowledgeNode (target)
        creator: Many-to-one relationship with User model

    Example:
        >>> relation = KnowledgeRelation(
        ...     subject_id=1,
        ...     predicate="enables",
        ...     object_id=2,
        ...     strength=0.85,
        ...     context={"mechanism": "quantum mechanical"},
        ...     created_by=1,
        ...     is_bidirectional=False
        ... )
        >>> session.add(relation)
        >>> session.commit()
    """
    __tablename__ = "knowledge_relations"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False, index=True)
    predicate = Column(String(100), nullable=False, index=True)
    object_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False, index=True)
    strength = Column(Float, default=0.5, index=True)
    context = Column(JSON, nullable=True)
    evidence_papers = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_bidirectional = Column(Boolean, default=False)
    validation_status = Column(String(20), default="pending", index=True)

    # Relationships
    subject = relationship("KnowledgeNode", foreign_keys=[subject_id], back_populates="outgoing_relations")
    object = relationship("KnowledgeNode", foreign_keys=[object_id], back_populates="incoming_relations")
    creator = relationship("User")

    def __repr__(self):
        return f"<KnowledgeRelation(id={self.id}, {self.subject_id}-{self.predicate}-{self.object_id})>"


class ScientificConcept(Base):
    """
    Represents high-level scientific concepts with rich metadata.
    
    This model stores comprehensive information about scientific concepts,
    including their definitions, mathematical formulations, and relationships
    to other concepts across multiple domains.
    
    Attributes:
        id (int): Primary key
        name (str): Canonical name of the scientific concept
        alternative_names (list): List of alternative names and synonyms
        definition (str): Formal definition of the concept
        mathematical_formulation (str): Mathematical representation if applicable
        domain_primary (str): Primary scientific domain
        domains_secondary (list): Secondary domains where concept applies
        complexity_level (int): Complexity rating (1-10)
        prerequisites (list): List of prerequisite concept IDs
        applications (dict): Real-world applications and use cases
        related_methods (list): Associated computational/experimental methods
        key_papers (list): Foundational literature references
        created_by (int): User who created this concept entry
        created_at (datetime): Creation timestamp (UTC)
        updated_at (datetime): Last update timestamp (UTC)
        peer_review_status (str): Review status (draft, under_review, approved)
        citation_count (int): Number of times this concept is referenced

    Relationships:
        creator: Many-to-one relationship with User model
        concept_mappings: One-to-many with CrossDomainMapping

    Example:
        >>> concept = ScientificConcept(
        ...     name="Machine Learning",
        ...     definition="Algorithms that improve automatically through experience",
        ...     domain_primary="computer_science",
        ...     domains_secondary=["statistics", "mathematics"],
        ...     complexity_level=7,
        ...     created_by=1
        ... )
        >>> session.add(concept)
        >>> session.commit()
    """
    __tablename__ = "scientific_concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    alternative_names = Column(JSON, nullable=True)
    definition = Column(Text, nullable=True)
    mathematical_formulation = Column(Text, nullable=True)
    domain_primary = Column(String(100), nullable=False, index=True)
    domains_secondary = Column(JSON, nullable=True)
    complexity_level = Column(Integer, default=1, index=True)
    prerequisites = Column(JSON, nullable=True)
    applications = Column(JSON, nullable=True)
    related_methods = Column(JSON, nullable=True)
    key_papers = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    peer_review_status = Column(String(20), default="draft", index=True)
    citation_count = Column(Integer, default=0)

    # Relationships
    creator = relationship("User")
    concept_mappings = relationship("CrossDomainMapping", back_populates="concept")

    def __repr__(self):
        return f"<ScientificConcept(id={self.id}, name='{self.name}', domain='{self.domain_primary}')>"


class CrossDomainMapping(Base):
    """
    Represents mappings between scientific concepts across different domains.
    
    This model captures how concepts from one scientific domain relate to
    concepts in other domains, enabling interdisciplinary knowledge transfer
    and cross-pollination of ideas.
    
    Attributes:
        id (int): Primary key
        concept_id (int): Foreign key to source ScientificConcept
        target_domain (str): Target scientific domain
        mapping_type (str): Type of mapping (analogy, equivalence, generalization, etc.)
        target_concept_name (str): Name of concept in target domain
        similarity_score (float): Similarity strength (0.0-1.0)
        mapping_rationale (str): Explanation of why this mapping exists
        evidence_strength (str): Strength of supporting evidence (weak, moderate, strong)
        use_cases (dict): Specific use cases where this mapping is valuable
        created_by (int): User who created this mapping
        created_at (datetime): Creation timestamp (UTC)
        updated_at (datetime): Last update timestamp (UTC)
        validation_count (int): Number of expert validations
        dispute_count (int): Number of expert disputes

    Relationships:
        concept: Many-to-one relationship with ScientificConcept
        creator: Many-to-one relationship with User model

    Example:
        >>> mapping = CrossDomainMapping(
        ...     concept_id=1,
        ...     target_domain="biology",
        ...     mapping_type="analogy",
        ...     target_concept_name="Neural Networks",
        ...     similarity_score=0.8,
        ...     mapping_rationale="Both involve connected processing units",
        ...     created_by=1
        ... )
        >>> session.add(mapping)
        >>> session.commit()
    """
    __tablename__ = "cross_domain_mappings"

    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, ForeignKey("scientific_concepts.id"), nullable=False, index=True)
    target_domain = Column(String(100), nullable=False, index=True)
    mapping_type = Column(String(50), nullable=False, index=True)
    target_concept_name = Column(String(255), nullable=False)
    similarity_score = Column(Float, default=0.0, index=True)
    mapping_rationale = Column(Text, nullable=True)
    evidence_strength = Column(String(20), default="moderate", index=True)
    use_cases = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    validation_count = Column(Integer, default=0)
    dispute_count = Column(Integer, default=0)

    # Relationships
    concept = relationship("ScientificConcept", back_populates="concept_mappings")
    creator = relationship("User")

    def __repr__(self):
        return f"<CrossDomainMapping(id={self.id}, concept_id={self.concept_id}, target='{self.target_domain}')>"


# --- Orchestrator Persistence Models (Workflows v1.1) ---

"""
NOTE: Workflow persistence models were moved to app/models/workflow_persistence_models.py
to avoid circular imports and duplicate mapper registrations. Do not redefine them here.
"""

# --- Scientific Evaluation & Decision Ledger Extensions (v0) ---

class EvaluationRecord(Base):
    """Persistencia de evaluaciones científicas.

    Almacena snapshot reproducible de métricas, pesos y score compuesto.
    """
    __tablename__ = "evaluation_records"

    id = Column(Integer, primary_key=True, index=True)
    hypothesis_id = Column(String(64), nullable=True, index=True)
    inputs = Column(JSON, nullable=True)
    normalized = Column(JSON, nullable=True)
    components = Column(JSON, nullable=True)
    weights = Column(JSON, nullable=True)
    composite_score = Column(Float, nullable=False, index=True)
    formula_version = Column(String(10), nullable=False, default="v0", index=True)
    formula_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<EvaluationRecord(id={self.id}, score={self.composite_score:.3f}, version={self.formula_version})>"


class DecisionLedgerEntry(Base):
    """Persistencia de entradas del decision ledger."""
    __tablename__ = "decision_ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    decision_type = Column(String(100), nullable=False, index=True)
    subject_id = Column(String(64), nullable=True, index=True)
    options = Column(JSON, nullable=True)
    chosen = Column(String(255), nullable=False)
    rationale = Column(Text, nullable=True)
    metrics = Column(JSON, nullable=True)
    version = Column(String(10), nullable=False, default="v0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<DecisionLedgerEntry(id={self.id}, type='{self.decision_type}', chosen='{self.chosen}')>"


# --- Paper Analysis & Peer Review Persistence (v0) ---

class ClaimRecord(Base):
    """Claim científico extraído de un paper.

    Permite auditoría de extracción y posteriores relaciones con hipótesis.
    """
    __tablename__ = "claim_records"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(String(64), nullable=True, index=True)
    paper_title = Column(String(500), nullable=True)
    claim_text = Column(Text, nullable=False)
    claim_hash = Column(String(64), nullable=True, index=True)
    claim_type = Column(String(50), nullable=True, index=True)  # finding, method, limitation, other
    confidence_score = Column(Float, default=0.0, index=True)
    extraction_method = Column(String(50), default="heuristic", index=True)
    source_section = Column(String(100), nullable=True)
    position = Column(Integer, nullable=True)
    claim_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    relations = relationship("ClaimRelation", back_populates="claim", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ClaimRecord(id={self.id}, paper_id='{self.paper_id}', type='{self.claim_type}')>"


class PaperQualityMetrics(Base):
    """Snapshot de métricas de calidad calculadas para un paper.

    Almacena directamente la estructura JSON devuelta por paper_analysis_service
    para reproducibilidad y trazabilidad de ranking.
    """
    __tablename__ = "paper_quality_metrics"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(String(64), nullable=True, index=True)
    paper_title = Column(String(500), nullable=True)
    metrics = Column(JSON, nullable=True)  # transparencia, método, citaciones, etc.
    claims_summary = Column(JSON, nullable=True)  # agregados: total_claims, tipos, etc.
    coverage_ratio = Column(Float, nullable=True, index=True)
    ranking_score = Column(Float, nullable=True, index=True)
    red_flags = Column(JSON, nullable=True)
    embeddings = Column(JSON, nullable=True)  # opcional (vector serializado / reducción)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<PaperQualityMetrics(id={self.id}, paper_id='{self.paper_id}', score={self.ranking_score})>"


class PeerReviewRecord(Base):
    """Registro persistente de peer review automático multi-rol.

    Guarda revisiones por rol y el consenso para trazabilidad y evolución de versión.
    """
    __tablename__ = "peer_review_records"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(String(64), nullable=True, index=True)
    paper_title = Column(String(500), nullable=True)
    role_reviews = Column(JSON, nullable=True)  # dict role -> {scores, comments}
    consensus_score = Column(Float, nullable=True, index=True)
    methodology_score = Column(Float, nullable=True)
    statistical_score = Column(Float, nullable=True)
    robustness_score = Column(Float, nullable=True)
    domain_score = Column(Float, nullable=True)
    version = Column(String(10), default="v0", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<PeerReviewRecord(id={self.id}, paper_id='{self.paper_id}', consensus={self.consensus_score})>"


class ClaimRelation(Base):
    """Relación claim ↔ hipótesis para grafo de evidencia.

    relation_type: supports | contradicts | extends (extensible)
    strength: heurística 0-1
    """
    __tablename__ = "claim_relations"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claim_records.id"), nullable=False, index=True)
    hypothesis_id = Column(String(64), nullable=True, index=True)
    relation_type = Column(String(20), nullable=False, default="supports", index=True)
    strength = Column(Float, default=0.5, index=True)
    evidence = Column(JSON, nullable=True)  # contexto, frases, métricas
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    claim = relationship("ClaimRecord", back_populates="relations")

    def __repr__(self):
        return f"<ClaimRelation(id={self.id}, claim={self.claim_id}, hyp='{self.hypothesis_id}', type='{self.relation_type}')>"

