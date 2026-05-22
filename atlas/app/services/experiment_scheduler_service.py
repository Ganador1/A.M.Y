"""
Compatibility shim for experiment_scheduler_service.
Re-exports ExperimentSchedulerV3 as ExperimentSchedulerService for backward compatibility.

This shim provides a compatibility layer for routers and tests that still reference
the old ExperimentSchedulerService name. The actual implementation is in
app.services.orchestration.experiment_scheduler_v3.

Usage:
    from app.services.experiment_scheduler_service import ExperimentSchedulerService
    scheduler = ExperimentSchedulerService()  # Same as ExperimentSchedulerV3()
"""

from app.services.orchestration.experiment_scheduler_v3 import (
    ExperimentSchedulerV3,
    ImpactPriority,
    SchedulingStrategy,
    RetryStrategy,
)

# Alias for backward compatibility
ExperimentSchedulerService = ExperimentSchedulerV3

# Re-export all public symbols
__all__ = [
    "ExperimentSchedulerService",
    "ExperimentSchedulerV3",
    "ImpactPriority",
    "SchedulingStrategy",
    "RetryStrategy",
]
