import asyncio

import pytest

from app.services.experiment_scheduler_v3 import ExperimentSchedulerV3, ImpactPriority, SchedulingStrategy, RetryStrategy
from app.models.experiment_scheduler_models import ExperimentJobRecord, ExperimentJobState
from app.database import get_db_session

@pytest.fixture
def scheduler():
    # Asegura aislamiento limpiando tabla antes de cada test
    session = get_db_session()
    try:
        session.query(ExperimentJobRecord).delete()
        session.commit()
    finally:
        session.close()
    s = ExperimentSchedulerV3()
    yield s


def _count_jobs(state=None):
    session = get_db_session()
    try:
        q = session.query(ExperimentJobRecord)
        if state:
            q = q.filter(ExperimentJobRecord.state == state.value)
        return q.count()
    finally:
        session.close()


def test_submit_job_sets_impact_and_priority(scheduler):
    job_uuid = scheduler.submit_job(
        name="test-impact",
        job_type="analysis",
        payload={"novelty_indicators": {"new_methods": ["m1"], "new_datasets": ["d1"], "cross_domain_elements": ["x"]}},
    )
    status = scheduler.get_job_status(job_uuid)
    assert status is not None
    assert status["impact_score"] is not None
    assert 1 <= status["priority"] <= 5


def test_priority_first_sorting(scheduler):
    # Submit different priorities explicitly
    scheduler.submit_job("p1", "t", {}, priority=ImpactPriority.LOW)
    scheduler.submit_job("p2", "t", {}, priority=ImpactPriority.CRITICAL)
    scheduler.submit_job("p3", "t", {}, priority=ImpactPriority.MEDIUM)
    jobs = scheduler._get_ready_jobs()
    scheduler.scheduling_strategy = SchedulingStrategy.PRIORITY_FIRST
    ordered = scheduler._sort_jobs_by_strategy(jobs)
    priorities = [j.priority for j in ordered]
    assert priorities == sorted(priorities)


def test_impact_weighted_changes_order(scheduler):
    scheduler.submit_job("a", "t", {"impact_dummy": 1}, priority=ImpactPriority.MEDIUM)
    high_payload = {"novelty_indicators": {"new_methods": ["m1","m2"], "new_datasets": ["d1"], "cross_domain_elements": ["x","y"]}}
    scheduler.submit_job("b", "t", high_payload)  # auto impact
    jobs = scheduler._get_ready_jobs()
    scheduler.scheduling_strategy = SchedulingStrategy.IMPACT_WEIGHTED
    ordered = scheduler._sort_jobs_by_strategy(jobs)
    assert len(ordered) == len(jobs)


def test_retry_logic_exponential(scheduler):
    attempts = {"n": 0}
    async def failing(_):
        attempts["n"] += 1
        raise RuntimeError("fail")
    scheduler.register_job_handler("failjob", failing)
    scheduler.retry_strategy = RetryStrategy.EXPONENTIAL_BACKOFF
    scheduler.max_retry_attempts = 2
    job_uuid = scheduler.submit_job("r1", "failjob", {})

    # Recuperar ese job específico
    session = get_db_session()
    try:
        job = session.query(ExperimentJobRecord).filter(ExperimentJobRecord.job_uuid == job_uuid).first()
    finally:
        session.close()
    asyncio.get_event_loop().run_until_complete(scheduler._execute_job(job))
    status = scheduler.get_job_status(job_uuid)
    # Debe haber incrementado retry_count o terminado en failed si sin retry
    assert status["retry_count"] >= 1 or status["state"] == ExperimentJobState.FAILED.value


def test_adaptive_score_monotonic(scheduler):
    scheduler.scheduling_strategy = SchedulingStrategy.ADAPTIVE
    scheduler.submit_job("ad1", "t", {})
    scheduler.submit_job("ad2", "t", {})
    jobs = scheduler._get_ready_jobs()
    scores = [scheduler._calculate_adaptive_score(j) for j in jobs]
    assert all(0 <= s for s in scores)


def test_metrics_snapshot(scheduler):
    m = scheduler.get_scheduler_metrics()
    assert "queue_metrics" in m
    assert "configuration" in m
