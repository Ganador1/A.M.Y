"""
Audit service for managing security events, metrics, and alerts.
Provides real-time monitoring and analytics for security dashboard.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging

from app.models.audit_models import AuditEvent, ActiveAlert, create_audit_event
from app.core.websocket_manager import get_connection_manager


logger = logging.getLogger(__name__)


class AuditService:
    """
    Service for managing audit events, security metrics, and alerts.
    Provides comprehensive security monitoring and analytics.
    """

    # Event types
    EVENT_AUTH_LOGIN = "auth_login"
    EVENT_AUTH_LOGOUT = "auth_logout"
    EVENT_AUTH_FAILED = "auth_failed"
    EVENT_TOKEN_REFRESH = "token_refresh"
    EVENT_TOKEN_REVOKE = "token_revoke"
    EVENT_PASSWORD_CHANGE = "password_change"
    EVENT_PERMISSION_DENIED = "permission_denied"
    EVENT_RATE_LIMIT = "rate_limit_exceeded"
    EVENT_USER_CREATED = "user_created"
    EVENT_USER_UPDATED = "user_updated"

    # Categories
    CAT_AUTH = "authentication"
    CAT_AUTHZ = "authorization"
    CAT_DATA = "data_access"
    CAT_ADMIN = "admin"
    CAT_SECURITY = "security"

    # Severities
    SEV_INFO = "info"
    SEV_WARNING = "warning"
    SEV_ERROR = "error"
    SEV_CRITICAL = "critical"

    # Alert types
    ALERT_BRUTE_FORCE = "brute_force"
    ALERT_RATE_ABUSE = "rate_limit_abuse"
    ALERT_SUSPICIOUS = "suspicious_activity"
    ALERT_PERMISSION_ESC = "permission_escalation"

    async def log_event(
        self,
        db: Session,
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
        Log an audit event and broadcast via WebSocket.

        Args:
            db: Database session
            event_type: Event type
            category: Event category
            message: Human-readable message
            user_id: Optional user ID
            username: Optional username
            ip_address: Optional IP address
            severity: Severity level
            success: Whether operation succeeded
            **kwargs: Additional event data

        Returns:
            Created AuditEvent
        """
        try:
            event = create_audit_event(
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

            db.add(event)
            db.commit()
            db.refresh(event)

            logger.info(f"Audit event logged: {event_type} - {message}")

            # Broadcast event via WebSocket
            try:
                manager = get_connection_manager()
                await manager.broadcast_event({
                    "id": str(event.id),
                    "event_type": event.event_type,
                    "category": event.category,
                    "message": event.message,
                    "user_id": event.user_id,
                    "username": event.username,
                    "ip_address": event.ip_address,
                    "severity": event.severity,
                    "success": event.success,
                    "timestamp": event.timestamp.isoformat() if event.timestamp else None,
                    "details": event.details
                })
            except Exception as ws_error:
                logger.warning(f"Failed to broadcast event via WebSocket: {ws_error}")

            # Check for alert conditions
            await self._check_alert_conditions(db, event)

            return event

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to log audit event: {e}")
            raise

    async def get_recent_events(
        self,
        db: Session,
        limit: int = 100,
        offset: int = 0,
        event_type: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Tuple[List[AuditEvent], int]:
        """
        Get recent audit events with filtering.

        Args:
            db: Database session
            limit: Maximum number of events to return
            offset: Number of events to skip
            event_type: Filter by event type
            category: Filter by category
            severity: Filter by severity
            user_id: Filter by user ID
            start_time: Filter events after this time
            end_time: Filter events before this time

        Returns:
            Tuple of (events list, total count)
        """
        try:
            # Build query
            query = select(AuditEvent)

            # Apply filters
            filters = []
            if event_type:
                filters.append(AuditEvent.event_type == event_type)
            if category:
                filters.append(AuditEvent.category == category)
            if severity:
                filters.append(AuditEvent.severity == severity)
            if user_id:
                filters.append(AuditEvent.user_id == user_id)
            if start_time:
                filters.append(AuditEvent.timestamp >= start_time)
            if end_time:
                filters.append(AuditEvent.timestamp <= end_time)

            if filters:
                query = query.where(and_(*filters))

            # Count total
            count_query = select(func.count()).select_from(query.subquery())
            total = db.execute(count_query).scalar()

            # Get events
            query = query.order_by(desc(AuditEvent.timestamp)).limit(limit).offset(offset)
            result = db.execute(query)
            events = result.scalars().all()

            return events, total

        except Exception as e:
            logger.error(f"Failed to get recent events: {e}")
            raise

    async def get_realtime_metrics(
        self,
        db: Session,
        window_size: str = "5min"
    ) -> Dict[str, Any]:
        """
        Get real-time security metrics for the current time window.

        Args:
            db: Database session
            window_size: Time window ('1min', '5min', '1hour')

        Returns:
            Dictionary with current metrics
        """
        try:
            # Calculate window
            now = datetime.utcnow()
            if window_size == "1min":
                window_start = now - timedelta(minutes=1)
            elif window_size == "5min":
                window_start = now - timedelta(minutes=5)
            elif window_size == "1hour":
                window_start = now - timedelta(hours=1)
            else:
                window_start = now - timedelta(minutes=5)

            # Query events in window
            query = select(AuditEvent).where(
                AuditEvent.timestamp >= window_start
            )
            result = db.execute(query)
            events = result.scalars().all()

            # Aggregate metrics
            metrics = {
                "window": {
                    "start": window_start.isoformat(),
                    "end": now.isoformat(),
                    "size": window_size
                },
                "authentication": {
                    "total_logins": 0,
                    "successful_logins": 0,
                    "failed_logins": 0,
                    "unique_users": set()
                },
                "authorization": {
                    "permission_checks": 0,
                    "permission_denied": 0
                },
                "tokens": {
                    "created": 0,
                    "refreshed": 0,
                    "revoked": 0
                },
                "rate_limiting": {
                    "hits": 0,
                    "exceeded": 0
                },
                "events": {
                    "total": len(events),
                    "critical": 0,
                    "error": 0,
                    "warning": 0,
                    "info": 0
                },
                "performance": {
                    "avg_response_time": 0.0,
                    "max_response_time": 0.0
                }
            }

            # Process events
            response_times = []
            for event in events:
                # Authentication
                if event.event_type == self.EVENT_AUTH_LOGIN:
                    metrics["authentication"]["total_logins"] += 1
                    if event.success:
                        metrics["authentication"]["successful_logins"] += 1
                        if event.user_id:
                            metrics["authentication"]["unique_users"].add(event.user_id)
                elif event.event_type == self.EVENT_AUTH_FAILED:
                    metrics["authentication"]["failed_logins"] += 1

                # Tokens
                if "token" in event.event_type:
                    if "refresh" in event.event_type:
                        metrics["tokens"]["refreshed"] += 1
                    elif "revoke" in event.event_type:
                        metrics["tokens"]["revoked"] += 1
                    else:
                        metrics["tokens"]["created"] += 1

                # Authorization
                if event.event_type == self.EVENT_PERMISSION_DENIED:
                    metrics["authorization"]["permission_denied"] += 1
                if event.category == self.CAT_AUTHZ:
                    metrics["authorization"]["permission_checks"] += 1

                # Rate limiting
                if event.event_type == self.EVENT_RATE_LIMIT:
                    metrics["rate_limiting"]["exceeded"] += 1

                # Severity
                if event.severity == self.SEV_CRITICAL:
                    metrics["events"]["critical"] += 1
                elif event.severity == self.SEV_ERROR:
                    metrics["events"]["error"] += 1
                elif event.severity == self.SEV_WARNING:
                    metrics["events"]["warning"] += 1
                else:
                    metrics["events"]["info"] += 1

                # Performance
                if event.duration_ms:
                    response_times.append(event.duration_ms)

            # Finalize metrics
            metrics["authentication"]["unique_users"] = len(metrics["authentication"]["unique_users"])

            if response_times:
                metrics["performance"]["avg_response_time"] = sum(response_times) / len(response_times)
                metrics["performance"]["max_response_time"] = max(response_times)

            return metrics

        except Exception as e:
            logger.error(f"Failed to get realtime metrics: {e}")
            raise

    async def get_active_alerts(
        self,
        db: Session,
        status: str = "open",
        severity: Optional[str] = None,
        limit: int = 50
    ) -> List[ActiveAlert]:
        """
        Get active security alerts.

        Args:
            db: Database session
            status: Alert status ('open', 'investigating', 'resolved')
            severity: Filter by severity
            limit: Maximum alerts to return

        Returns:
            List of active alerts
        """
        try:
            query = select(ActiveAlert).where(ActiveAlert.status == status)

            if severity:
                query = query.where(ActiveAlert.severity == severity)

            query = query.order_by(
                desc(ActiveAlert.severity),
                desc(ActiveAlert.risk_score),
                desc(ActiveAlert.created_at)
            ).limit(limit)

            result = db.execute(query)
            alerts = result.scalars().all()

            return alerts

        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            raise

    async def create_alert(
        self,
        db: Session,
        alert_type: str,
        title: str,
        description: str,
        severity: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        risk_score: int = 0,
        evidence: Optional[Dict[str, Any]] = None,
        related_events: Optional[List[str]] = None
    ) -> ActiveAlert:
        """
        Create a new security alert and broadcast via WebSocket.

        Args:
            db: Database session
            alert_type: Type of alert
            title: Short title
            description: Detailed description
            severity: Severity level
            user_id: Related user ID
            username: Related username
            ip_address: Related IP address
            risk_score: Risk score (0-100)
            evidence: Evidence data
            related_events: Related event IDs

        Returns:
            Created alert
        """
        try:
            alert = ActiveAlert(
                alert_type=alert_type,
                title=title,
                description=description,
                severity=severity,
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                risk_score=risk_score,
                evidence=evidence,
                related_events=related_events
            )

            db.add(alert)
            db.commit()
            db.refresh(alert)

            logger.warning(f"Alert created: {alert_type} - {title}")

            # Broadcast alert via WebSocket
            try:
                manager = get_connection_manager()
                await manager.broadcast_alert(alert.to_dict())
            except Exception as ws_error:
                logger.warning(f"Failed to broadcast alert via WebSocket: {ws_error}")

            return alert

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create alert: {e}")
            raise

    async def update_alert_status(
        self,
        db: Session,
        alert_id: str,
        status: str,
        resolution_notes: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> Optional[ActiveAlert]:
        """
        Update alert status.

        Args:
            db: Database session
            alert_id: Alert ID
            status: New status
            resolution_notes: Optional resolution notes
            assigned_to: Optional user assigned

        Returns:
            Updated alert or None
        """
        try:
            query = select(ActiveAlert).where(ActiveAlert.id == alert_id)
            result = db.execute(query)
            alert = result.scalar_one_or_none()

            if not alert:
                return None

            alert.status = status
            if resolution_notes:
                alert.resolution_notes = resolution_notes
            if assigned_to:
                alert.assigned_to = assigned_to
            if status == "resolved":
                alert.resolved_at = datetime.utcnow()

            db.commit()
            db.refresh(alert)

            return alert

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update alert status: {e}")
            raise

    async def _check_alert_conditions(
        self,
        db: Session,
        event: AuditEvent
    ) -> None:
        """
        Check if event should trigger an alert.

        Args:
            db: Database session
            event: Audit event to check
        """
        try:
            # Check for brute force (5+ failed logins in 5 minutes)
            if event.event_type == self.EVENT_AUTH_FAILED and event.ip_address:
                five_min_ago = datetime.utcnow() - timedelta(minutes=5)
                query = select(func.count()).select_from(AuditEvent).where(
                    and_(
                        AuditEvent.event_type == self.EVENT_AUTH_FAILED,
                        AuditEvent.ip_address == event.ip_address,
                        AuditEvent.timestamp >= five_min_ago
                    )
                )
                failed_count = db.execute(query).scalar()

                if failed_count >= 5:
                    # Check if alert already exists
                    alert_query = select(ActiveAlert).where(
                        and_(
                            ActiveAlert.alert_type == self.ALERT_BRUTE_FORCE,
                            ActiveAlert.ip_address == event.ip_address,
                            ActiveAlert.status == "open"
                        )
                    )
                    existing = db.execute(alert_query).scalar_one_or_none()

                    if not existing:
                        await self.create_alert(
                            db=db,
                            alert_type=self.ALERT_BRUTE_FORCE,
                            title=f"Brute force attack from {event.ip_address}",
                            description=f"{failed_count} failed login attempts in 5 minutes",
                            severity="high",
                            ip_address=event.ip_address,
                            risk_score=75,
                            evidence={"failed_count": failed_count}
                        )

            # Check for rate limit abuse (10+ rate limit hits in 10 minutes)
            if event.event_type == self.EVENT_RATE_LIMIT and event.ip_address:
                ten_min_ago = datetime.utcnow() - timedelta(minutes=10)
                query = select(func.count()).select_from(AuditEvent).where(
                    and_(
                        AuditEvent.event_type == self.EVENT_RATE_LIMIT,
                        AuditEvent.ip_address == event.ip_address,
                        AuditEvent.timestamp >= ten_min_ago
                    )
                )
                rate_limit_count = db.execute(query).scalar()

                if rate_limit_count >= 10:
                    alert_query = select(ActiveAlert).where(
                        and_(
                            ActiveAlert.alert_type == self.ALERT_RATE_ABUSE,
                            ActiveAlert.ip_address == event.ip_address,
                            ActiveAlert.status == "open"
                        )
                    )
                    existing = db.execute(alert_query).scalar_one_or_none()

                    if not existing:
                        await self.create_alert(
                            db=db,
                            alert_type=self.ALERT_RATE_ABUSE,
                            title=f"Rate limit abuse from {event.ip_address}",
                            description=f"{rate_limit_count} rate limit violations in 10 minutes",
                            severity="medium",
                            ip_address=event.ip_address,
                            risk_score=50,
                            evidence={"rate_limit_count": rate_limit_count}
                        )

        except Exception as e:
            logger.error(f"Failed to check alert conditions: {e}")
            # Don't raise - this is background processing


# Singleton instance
_audit_service = AuditService()


def get_audit_service() -> AuditService:
    """Get the singleton audit service instance"""
    return _audit_service
