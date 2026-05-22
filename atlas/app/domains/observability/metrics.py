"""
Compatibility wrapper for observability metrics.
Re-exports metrics from the observability module.
"""

from app.observability.metrics import *

__all__ = [
    "inc",
    "observe", 
    "gauge_inc",
    "gauge_set",
    "phase_timer",
    "reset_metrics",
    "set_time_provider",
    "reset_time_provider",
    "scrape",
    "update_phase_success_ratio",
]