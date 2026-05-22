from app.services.observability_service import observability_service

def test_observability_counters_and_events():
    observability_service.incr("calls")
    observability_service.record_event("test", {"x": 1})
    snap = observability_service.snapshot()
    assert snap["counters"]["calls"] >= 1
    assert snap["event_count"] >= 1
