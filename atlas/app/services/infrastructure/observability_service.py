"""Observability Service (Stub)
Contadores y eventos en memoria para instrumentar servicios.
"""
from __future__ import annotations
from typing import Dict, Any, List
import time
from app.services.base_service import BaseService

class ObservabilityService(BaseService):
    def __init__(self):
        super().__init__("ObservabilityService")
        self.counters: Dict[str, int] = {}
        self.events: List[Dict[str, Any]] = []
        self.version = "v0"

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a service request"""
        try:
            action = request_data.get("action")
            if action == "snapshot":
                return {"success": True, "data": self.snapshot()}
            elif action == "record_event":
                self.record_event(request_data.get("event_type"), request_data.get("payload"))
                return {"success": True}
            elif action == "incr":
                self.incr(request_data.get("name"), request_data.get("value", 1))
                return {"success": True}
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return self.handle_error(e, "process_request")

    def incr(self, name: str, value: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + value

    def record_event(self, event_type: str, payload: Dict[str, Any] | None = None) -> None:
        self.events.append({
            "ts": time.time(),
            "type": event_type,
            "payload": payload or {},
        })

    def snapshot(self) -> Dict[str, Any]:
        return {
            "counters": dict(self.counters),
            "event_count": len(self.events),
            "last_event": self.events[-1] if self.events else None,
        }

observability_service = ObservabilityService()
