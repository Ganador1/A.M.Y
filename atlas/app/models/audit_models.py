"""
SQLAlchemy models for audit logging and security monitoring.
Stores security events, metrics, and alerts for real-time dashboard.
"""

from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, JSON, Text, Index
from sqlalchemy.sql import func
from typing import Optional, Dict, Any
import uuid

from app.models.database_models import Base


class AuditEvent(Base):
    """
    Audit event model for tracking security and operational events.
    Stores all security-relevant events for compliance and monitoring.
    """
    __tablename__ = "audit_events"

    # Primary identification
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)

    # Event classification
    event_type = Column(String(50), nullable=False, index=True)
    """Event type: 'auth_login', 'auth_logout', 'auth_failed', 'permission_denied',
    'token_refresh', 'password_change', 'user_created', 'rate_limit_exceeded', etc."""

    category = Column(String(30), nullable=False, index=True)
    """Category: 'authentication', 'authorization', 'data_access', 'admin', 'security'"""

    severity = Column(String(20), nullable=False, index=True)
    """Severity: 'info', 'warning', 'error', 'critical'"""

    # Actor information
    user_id = Column(String, nullable=True, index=True)
    """User ID who triggered the event (null for anonymous)"""

    username = Column(String(50), nullable=True, index=True)
    """Username for quick lookup"""

    # Request context
    ip_address = Column(String(45), nullable=True, index=True)
    """IP address (supports IPv4 and IPv6)"""

    user_agent = Column(String(255), nullable=True)
    """Browser/client user agent"""

    endpoint = Column(String(255), nullable=True, index=True)
    """API endpoint accessed"""

    method = Column(String(10), nullable=True)
    """HTTP method: GET, POST, PUT, DELETE, etc."""

    # Event details
    message = Column(Text, nullable=False)
    """Human-readable event description"""

    details = Column(JSON, nullable=True)
    """Additional event data (JSON)"""

    # Result
    success = Column(Boolean, nullable=False, default=True)
    """Whether the operation succeeded"""

    status_code = Column(Integer, nullable=True)
    """HTTP status code (if applicable)"""

    # Performance
    duration_ms = Column(Float, nullable=True)
    """Request duration in milliseconds"""

    # Metadata
    tags = Column(JSON, nullable=True)
    """Tags for categorization and filtering"""

    # Indexes for common queries
    __table_args__ = (
        Index('ix_audit_timestamp_type', 'timestamp', 'event_type'),
        Index('ix_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_audit_category_severity', 'category', 'severity'),
        Index('ix_audit_ip_timestamp', 'ip_address', 'timestamp'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_type": self.event_type,
            "category": self.category,
            "severity": self.severity,
            "user_id": self.user_id,
            "username": self.username,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "endpoint": self.endpoint,
            "method": self.method,
            "message": self.message,
            "details": self.details,
            "success": self.success,
            "status_code": self.status_code,
            "duration_ms": self.duration_ms,
            "tags": self.tags
        }


class SecurityMetric(Base):
    """
    Real-time security metrics aggregated by time window.
    Used for dashboard metrics and trend analysis.
    """
    __tablename__ = "security_metrics"

    # Primary identification
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)

    # Time window
    window_start = Column(DateTime, nullable=False, index=True)
    window_end = Column(DateTime, nullable=False)
    window_size = Column(String(20), nullable=False)
    """Window size: '1min', '5min', '1hour', '1day'"""

    # Authentication metrics
    total_logins = Column(Integer, default=0)
    successful_logins = Column(Integer, default=0)
    failed_logins = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)

    # Authorization metrics
    permission_checks = Column(Integer, default=0)
    permission_denied = Column(Integer, default=0)

    # Token metrics
    tokens_created = Column(Integer, default=0)
    tokens_refreshed = Column(Integer, default=0)
    tokens_revoked = Column(Integer, default=0)

    # Rate limiting metrics
    rate_limit_hits = Column(Integer, default=0)
    rate_limit_exceeded = Column(Integer, default=0)

    # Security events
    critical_events = Column(Integer, default=0)
    error_events = Column(Integer, default=0)
    warning_events = Column(Integer, default=0)

    # Performance
    avg_response_time = Column(Float, nullable=True)
    max_response_time = Column(Float, nullable=True)

    # Additional metrics
    metrics_data = Column(JSON, nullable=True)
    """Additional custom metrics (JSON)"""

    __table_args__ = (
        Index('ix_metrics_window', 'window_start', 'window_size'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "window_start": self.window_start.isoformat() if self.window_start else None,
            "window_end": self.window_end.isoformat() if self.window_end else None,
            "window_size": self.window_size,
            "authentication": {
                "total_logins": self.total_logins,
                "successful_logins": self.successful_logins,
                "failed_logins": self.failed_logins,
                "unique_users": self.unique_users
            },
            "authorization": {
                "permission_checks": self.permission_checks,
                "permission_denied": self.permission_denied
            },
            "tokens": {
                "created": self.tokens_created,
                "refreshed": self.tokens_refreshed,
                "revoked": self.tokens_revoked
            },
            "rate_limiting": {
                "hits": self.rate_limit_hits,
                "exceeded": self.rate_limit_exceeded
            },
            "events": {
                "critical": self.critical_events,
                "error": self.error_events,
                "warning": self.warning_events
            },
            "performance": {
                "avg_response_time": self.avg_response_time,
                "max_response_time": self.max_response_time
            },
            "metrics_data": self.metrics_data
        }


class ActiveAlert(Base):
    """
    Active security alerts requiring attention.
    Used for real-time alerting and incident response.
    """
    __tablename__ = "active_alerts"

    # Primary identification
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Alert classification
    alert_type = Column(String(50), nullable=False, index=True)
    """Alert type: 'brute_force', 'rate_limit_abuse', 'suspicious_activity',
    'permission_escalation', 'multiple_failed_logins', etc."""

    severity = Column(String(20), nullable=False, index=True)
    """Severity: 'low', 'medium', 'high', 'critical'"""

    status = Column(String(20), nullable=False, default='open', index=True)
    """Status: 'open', 'investigating', 'resolved', 'false_positive'"""

    # Alert details
    title = Column(String(255), nullable=False)
    """Short alert title"""

    description = Column(Text, nullable=False)
    """Detailed alert description"""

    # Context
    user_id = Column(String, nullable=True, index=True)
    """User ID related to the alert"""

    username = Column(String(50), nullable=True)
    """Username for quick lookup"""

    ip_address = Column(String(45), nullable=True, index=True)
    """IP address related to the alert"""

    # Alert metadata
    trigger_count = Column(Integer, default=1)
    """How many times this alert was triggered"""

    first_seen = Column(DateTime, nullable=False, default=func.now())
    """When alert was first detected"""

    last_seen = Column(DateTime, nullable=False, default=func.now())
    """When alert was last triggered"""

    # Related events
    related_events = Column(JSON, nullable=True)
    """List of related audit event IDs"""

    evidence = Column(JSON, nullable=True)
    """Evidence data (JSON)"""

    # Response
    assigned_to = Column(String, nullable=True)
    """User ID assigned to investigate"""

    resolution_notes = Column(Text, nullable=True)
    """Notes about the resolution"""

    resolved_at = Column(DateTime, nullable=True)
    """When the alert was resolved"""

    # Risk score
    risk_score = Column(Integer, nullable=False, default=0)
    """Risk score: 0-100"""

    __table_args__ = (
        Index('ix_alerts_status_severity', 'status', 'severity'),
        Index('ix_alerts_type_status', 'alert_type', 'status'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "status": self.status,
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id,
            "username": self.username,
            "ip_address": self.ip_address,
            "trigger_count": self.trigger_count,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "related_events": self.related_events,
            "evidence": self.evidence,
            "assigned_to": self.assigned_to,
            "resolution_notes": self.resolution_notes,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "risk_score": self.risk_score
        }


# Helper functions for common audit operations
def create_audit_event(
    event_type: str,
    category: str,
    message: str,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    severity: str = "info",
    success: bool = True,
    **kwargs
) -> AuditEvent:
    """
    Factory function to create audit events easily.

    Args:
        event_type: Type of event (e.g., 'auth_login')
        category: Category (e.g., 'authentication')
        message: Human-readable message
        user_id: Optional user ID
        username: Optional username
        ip_address: Optional IP address
        severity: Severity level (default 'info')
        success: Whether operation succeeded (default True)
        **kwargs: Additional fields (user_agent, endpoint, details, etc.)

    Returns:
        AuditEvent instance
    """
    return AuditEvent(
        event_type=event_type,
        category=category,
        message=message,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        severity=severity,
        success=success,
        **kwargs
    )
