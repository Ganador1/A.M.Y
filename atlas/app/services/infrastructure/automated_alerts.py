"""
Automated Alerts module
This is a compatibility stub for automated alerts functionality
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class AlertLevel(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    ERROR = "error"
    THRESHOLD = "threshold"
    SYSTEM = "system"


class Alert:
    """Alert class for automated alerts"""
    
    def __init__(self, 
                 message: str, 
                 level: AlertLevel = AlertLevel.MEDIUM,
                 alert_type: AlertType = AlertType.SYSTEM,
                 metadata: Optional[Dict[str, Any]] = None):
        self.id = f"alert_{int(datetime.now().timestamp())}"
        self.message = message
        self.level = level
        self.alert_type = alert_type
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.acknowledged = False
    
    def acknowledge(self):
        """Acknowledge the alert"""
        self.acknowledged = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            "id": self.id,
            "message": self.message,
            "level": self.level.value,
            "type": self.alert_type.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged
        }


class AlertManager:
    """Manager for automated alerts"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_handlers = {}
    
    def create_alert(self, 
                    message: str, 
                    level: AlertLevel = AlertLevel.MEDIUM,
                    alert_type: AlertType = AlertType.SYSTEM,
                    metadata: Optional[Dict[str, Any]] = None) -> Alert:
        """Create a new alert"""
        alert = Alert(message, level, alert_type, metadata)
        self.alerts.append(alert)
        
        # Trigger handlers if configured
        if alert_type in self.alert_handlers:
            self.alert_handlers[alert_type](alert)
        
        return alert
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unacknowledged) alerts"""
        return [alert for alert in self.alerts if not alert.acknowledged]
    
    def get_all_alerts(self) -> List[Alert]:
        """Get all alerts"""
        return self.alerts
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert by ID"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledge()
                return True
        return False
    
    def clear_acknowledged_alerts(self):
        """Remove acknowledged alerts"""
        self.alerts = [alert for alert in self.alerts if not alert.acknowledged]
    
    def register_handler(self, alert_type: AlertType, handler):
        """Register a handler for specific alert types"""
        self.alert_handlers[alert_type] = handler


# Global alert manager
alert_manager = AlertManager()


def create_alert(message: str, 
                level: AlertLevel = AlertLevel.MEDIUM,
                alert_type: AlertType = AlertType.SYSTEM,
                metadata: Optional[Dict[str, Any]] = None) -> Alert:
    """Create a new alert using the global manager"""
    return alert_manager.create_alert(message, level, alert_type, metadata)


def get_active_alerts() -> List[Alert]:
    """Get active alerts using the global manager"""
    return alert_manager.get_active_alerts()


def acknowledge_alert(alert_id: str) -> bool:
    """Acknowledge alert using the global manager"""
    return alert_manager.acknowledge_alert(alert_id)


# Compatibility exports
__all__ = [
    "Alert",
    "AlertLevel", 
    "AlertType",
    "AlertManager",
    "alert_manager",
    "create_alert",
    "get_active_alerts", 
    "acknowledge_alert"
]
