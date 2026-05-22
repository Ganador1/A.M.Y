"""
AXIOM Health Check System
Comprehensive health monitoring for the Mathematics AI Engine
"""

import time
import psutil
import platform
from typing import Dict, Any
from datetime import datetime
from app.core.config import settings
from app.core.bootstrap_logging import logger


class HealthChecker:
    """Advanced health check system"""

    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.last_health_check = datetime.now()

    def increment_request(self):
        """Increment request counter"""
        self.request_count += 1

    def increment_error(self):
        """Increment error counter"""
        self.error_count += 1

    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}

    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        uptime = time.time() - self.start_time

        return {
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": (self.error_count / max(self.request_count, 1)) * 100,
            "last_health_check": self.last_health_check.isoformat()
        }

    def get_dependencies_status(self) -> Dict[str, Any]:
        """Check status of critical dependencies"""
        dependencies = {}

        # Check core mathematical libraries
        try:
            import sympy
            dependencies["sympy"] = {"status": "ok", "version": sympy.__version__}
        except ImportError:
            dependencies["sympy"] = {"status": "missing", "version": None}

        try:
            import numpy
            dependencies["numpy"] = {"status": "ok", "version": numpy.__version__}
        except ImportError:
            dependencies["numpy"] = {"status": "missing", "version": None}

        try:
            import matplotlib
            dependencies["matplotlib"] = {"status": "ok", "version": matplotlib.__version__}
        except ImportError:
            dependencies["matplotlib"] = {"status": "missing", "version": None}

        try:
            import fastapi
            dependencies["fastapi"] = {"status": "ok", "version": fastapi.__version__}
        except ImportError:
            dependencies["fastapi"] = {"status": "missing", "version": None}

        return dependencies

    def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get complete health status"""
        self.last_health_check = datetime.now()

        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "service": "AXIOM Mathematics AI",
            "system": self.get_system_info(),
            "application": self.get_application_metrics(),
            "dependencies": self.get_dependencies_status(),
            "configuration": {
                "host": settings.host,
                "port": settings.port,
                "debug": settings.debug,
                "max_computation_time": settings.max_computation_time
            }
        }

        # Determine overall health status
        if health_data["application"]["error_rate"] > 10:
            health_data["status"] = "degraded"
        elif any(dep["status"] != "ok" for dep in health_data["dependencies"].values()):
            health_data["status"] = "degraded"
        elif health_data["system"]["cpu_percent"] > 90:
            health_data["status"] = "warning"
        elif health_data["system"]["memory"]["percent"] > 90:
            health_data["status"] = "warning"

        return health_data

    def _format_uptime(self, uptime_seconds: float) -> str:
        """Format uptime in human readable format"""
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)


# Global health checker instance
health_checker = HealthChecker()
