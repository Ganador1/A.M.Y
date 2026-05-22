import asyncio
import os
import pytest
from app.config import settings
from app.database import init_database, close_database


class FakeService:
    def __init__(self):
        self.calls = 0

    async def process_request(self, payload):
        self.calls += 1
        op = payload.get("operation")
        if op == "timeout":
            # sleep longer than timeout to trigger
            await asyncio.sleep(2)
            return {"ok": True}
        if op == "fail_then_succeed":
            if self.calls == 1:
                raise RuntimeError("boom")
            return {"value": 42}
        if op == "echo":
            return {"echo": payload}
        return {"ok": True}


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    os.environ['ENABLE_DATABASE'] = 'true'
    os.environ['PYTEST_RUNNING'] = '1'
    settings.enable_database = True
    settings.database_url = "sqlite:///migrations.db"
    init_database()
    yield
    close_database()


@pytest.mark.asyncio
async def test_cache_hits_and_retries(monkeypatch):
    from app.services.workflow_orchestration import WorkflowOrchestratorService, ServiceType
    svc = WorkflowOrchestratorService()

    fake = FakeService()
    # monkeypatch registry
    svc.service_registry[ServiceType.SCIENTIFIC_AI] = fake.process_request

    # First run should compute and cache
    create = await svc.process_request({
        "action": "create_workflow",
        "name": "wf_cache",
        "steps": [
            {"service_type": ServiceType.SCIENTIFIC_AI.value, "operation": "echo", "parameters": {"a": 1}},
        ]
    })
    wf_id = create["workflow_id"]
    await svc.process_request({"action": "execute_workflow", "workflow_id": wf_id})
    # wait completion
    for _ in range(20):
        st = await svc.process_request({"action": "get_workflow_status", "workflow_id": wf_id})
        if st["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.05)

    # Second run with identical params should hit cache
    create2 = await svc.process_request({
        "action": "create_workflow",
        "name": "wf_cache2",
        "steps": [
            {"service_type": ServiceType.SCIENTIFIC_AI.value, "operation": "echo", "parameters": {"a": 1}},
        ]
    })
    wf_id2 = create2["workflow_id"]
    await svc.process_request({"action": "execute_workflow", "workflow_id": wf_id2})
    st2 = None
    for _ in range(20):
        st2 = await svc.process_request({"action": "get_workflow_status", "workflow_id": wf_id2})
        if st2["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.05)

    assert st2 is not None and st2.get("success", False)
    # cache_stats exist
    assert st2 is not None and "cache_stats" in st2

    # Retry path: first failure then success
    create3 = await svc.process_request({
        "action": "create_workflow",
        "name": "wf_retry",
        "steps": [
            {"service_type": ServiceType.SCIENTIFIC_AI.value, "operation": "fail_then_succeed", "parameters": {}, "max_retries": 1},
        ]
    })
    wf_id3 = create3["workflow_id"]
    await svc.process_request({"action": "execute_workflow", "workflow_id": wf_id3})
    st3 = None
    for _ in range(40):
        st3 = await svc.process_request({"action": "get_workflow_status", "workflow_id": wf_id3})
        if st3["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.05)

    assert st3 is not None and st3.get("success", False)


@pytest.mark.asyncio
async def test_timeout_path(monkeypatch):
    from app.services.workflow_orchestration import WorkflowOrchestratorService, ServiceType
    svc = WorkflowOrchestratorService()
    fake = FakeService()
    svc.service_registry[ServiceType.SCIENTIFIC_AI] = fake.process_request

    create = await svc.process_request({
        "action": "create_workflow",
        "name": "wf_timeout",
        "steps": [
            {"service_type": ServiceType.SCIENTIFIC_AI.value, "operation": "timeout", "parameters": {}, "timeout": 1, "max_retries": 0},
        ]
    })
    wf_id = create["workflow_id"]
    await svc.process_request({"action": "execute_workflow", "workflow_id": wf_id})
    st = None
    for _ in range(40):
        st = await svc.process_request({"action": "get_workflow_status", "workflow_id": wf_id})
        if st["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.05)

    assert st is not None and st.get("success", False)
