"""
Audit Dashboard API Router
Provides endpoints for real-time security monitoring and analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.auth_middleware import get_current_active_user, get_db
from app.core.rbac import require_permission, Permission
from app.models.auth_models import User
from app.services.audit_service import get_audit_service, AuditService
from pydantic import BaseModel, ConfigDict


router = APIRouter(
    prefix="/api/audit",
    tags=["audit"],
    responses={404: {"description": "Not found"}}
)


# Response models
class AuditEventResponse(BaseModel):
    """Audit event response model"""
    id: str
    timestamp: str
    event_type: str
    category: str
    severity: str
    user_id: Optional[str]
    username: Optional[str]
    ip_address: Optional[str]
    endpoint: Optional[str]
    method: Optional[str]
    message: str
    success: bool
    status_code: Optional[int]
    duration_ms: Optional[float]

    model_config = ConfigDict(from_attributes=True)


class AlertResponse(BaseModel):
    """Alert response model"""
    id: str
    created_at: str
    alert_type: str
    severity: str
    status: str
    title: str
    description: str
    user_id: Optional[str]
    username: Optional[str]
    ip_address: Optional[str]
    trigger_count: int
    risk_score: int

    model_config = ConfigDict(from_attributes=True)


class MetricsResponse(BaseModel):
    """Real-time metrics response model"""
    window: dict
    authentication: dict
    authorization: dict
    tokens: dict
    rate_limiting: dict
    events: dict
    performance: dict


class EventsListResponse(BaseModel):
    """Events list with pagination"""
    events: List[AuditEventResponse]
    total: int
    limit: int
    offset: int


class AlertsListResponse(BaseModel):
    """Alerts list response"""
    alerts: List[AlertResponse]
    total: int


# Endpoints
@router.get(
    "/metrics/realtime",
    response_model=MetricsResponse,
    summary="Get real-time security metrics",
    description="Get aggregated security metrics for the current time window. Requires admin or researcher role."
)
@require_permission(Permission.READ_HYPOTHESIS)  # Using existing permission for now
async def get_realtime_metrics(
    window_size: str = Query("5min", description="Time window: 1min, 5min, 1hour"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    Get real-time security metrics.

    Returns aggregated metrics including:
    - Authentication stats (logins, failures)
    - Authorization checks
    - Token operations
    - Rate limiting events
    - Event severity distribution
    - Performance metrics
    """
    try:
        metrics = await audit_service.get_realtime_metrics(db, window_size)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get(
    "/events/recent",
    response_model=EventsListResponse,
    summary="Get recent audit events",
    description="Get recent audit events with filtering options. Requires admin or researcher role."
)
@require_permission(Permission.READ_HYPOTHESIS)  # Using existing permission for now
async def get_recent_events(
    limit: int = Query(100, ge=1, le=1000, description="Maximum events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_time: Optional[datetime] = Query(None, description="Filter events after this time"),
    end_time: Optional[datetime] = Query(None, description="Filter events before this time"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    Get recent audit events with filtering.

    Supports filtering by:
    - Event type (auth_login, auth_failed, etc.)
    - Category (authentication, authorization, etc.)
    - Severity (info, warning, error, critical)
    - User ID
    - Time range

    Returns paginated results.
    """
    try:
        events, total = await audit_service.get_recent_events(
            db=db,
            limit=limit,
            offset=offset,
            event_type=event_type,
            category=category,
            severity=severity,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time
        )

        return {
            "events": [
                AuditEventResponse(
                    id=event.id,
                    timestamp=event.timestamp.isoformat() if event.timestamp else "",
                    event_type=event.event_type,
                    category=event.category,
                    severity=event.severity,
                    user_id=event.user_id,
                    username=event.username,
                    ip_address=event.ip_address,
                    endpoint=event.endpoint,
                    method=event.method,
                    message=event.message,
                    success=event.success,
                    status_code=event.status_code,
                    duration_ms=event.duration_ms
                )
                for event in events
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")


@router.get(
    "/alerts/active",
    response_model=AlertsListResponse,
    summary="Get active security alerts",
    description="Get active security alerts. Requires admin or researcher role."
)
@require_permission(Permission.READ_HYPOTHESIS)  # Using existing permission for now
async def get_active_alerts(
    status: str = Query("open", description="Alert status: open, investigating, resolved"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=200, description="Maximum alerts to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    Get active security alerts.

    Returns alerts ordered by:
    1. Severity (critical first)
    2. Risk score (highest first)
    3. Creation time (newest first)

    Supports filtering by:
    - Status (open, investigating, resolved)
    - Severity (low, medium, high, critical)
    """
    try:
        alerts = await audit_service.get_active_alerts(
            db=db,
            status=status,
            severity=severity,
            limit=limit
        )

        return {
            "alerts": [
                AlertResponse(
                    id=alert.id,
                    created_at=alert.created_at.isoformat() if alert.created_at else "",
                    alert_type=alert.alert_type,
                    severity=alert.severity,
                    status=alert.status,
                    title=alert.title,
                    description=alert.description,
                    user_id=alert.user_id,
                    username=alert.username,
                    ip_address=alert.ip_address,
                    trigger_count=alert.trigger_count,
                    risk_score=alert.risk_score
                )
                for alert in alerts
            ],
            "total": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.post(
    "/alerts/{alert_id}/update",
    response_model=AlertResponse,
    summary="Update alert status",
    description="Update an alert's status. Requires admin role."
)
@require_permission(Permission.CREATE_HYPOTHESIS)  # Using existing permission for now
async def update_alert_status(
    alert_id: str,
    status: str = Query(..., description="New status: open, investigating, resolved, false_positive"),
    resolution_notes: Optional[str] = Query(None, description="Resolution notes"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    Update alert status.

    Allows changing alert status and adding resolution notes.
    Automatically sets resolved_at timestamp when status is 'resolved'.
    """
    try:
        updated_alert = await audit_service.update_alert_status(
            db=db,
            alert_id=alert_id,
            status=status,
            resolution_notes=resolution_notes,
            assigned_to=current_user.id
        )

        if not updated_alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return AlertResponse(
            id=updated_alert.id,
            created_at=updated_alert.created_at.isoformat() if updated_alert.created_at else "",
            alert_type=updated_alert.alert_type,
            severity=updated_alert.severity,
            status=updated_alert.status,
            title=updated_alert.title,
            description=updated_alert.description,
            user_id=updated_alert.user_id,
            username=updated_alert.username,
            ip_address=updated_alert.ip_address,
            trigger_count=updated_alert.trigger_count,
            risk_score=updated_alert.risk_score
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alert: {str(e)}")


@router.get(
    "/health",
    summary="Audit service health check",
    description="Check if audit service is operational"
)
async def audit_health():
    """Health check endpoint for audit service"""
    return {
        "status": "healthy",
        "service": "audit",
        "timestamp": datetime.utcnow().isoformat()
    }
