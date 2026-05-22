"""
Time Sensor — A.M.Y's internal clock.
Every mind needs a sense of time.
"""
import time
from datetime import datetime


class TimeSensor:
    def __init__(self):
        self._start_time = time.time()

    async def sense(self) -> dict:
        now = datetime.now()
        elapsed = time.time() - self._start_time
        return {
            "current_time": now.isoformat(),
            "hour": now.hour,
            "day_of_week": now.strftime("%A"),
            "uptime_seconds": elapsed,
            "uptime_hours": elapsed / 3600,
            "is_night": now.hour < 6 or now.hour > 22,
        }
