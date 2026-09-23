import asyncio
import os
import pytest
from app.config import settings
from app.database import init_database, close_database


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Configure SQLite file for migrations env and mark pytest running to avoid auto-init
    os.environ['ENABLE_DATABASE'] = 'true'
    os.environ['PYTEST_RUNNING'] = '1'
    settings.enable_database = True
    settings.database_url = "sqlite:///migrations.db"
    init_database()
    yield
    close_database()


@pytest.mark.asyncio
async def test_create_execute_workflow_and_graph():
    # Import after env+DB setup
    from app.services.workflow_orchestration import WorkflowOrchestratorService, ServiceType
    svc = WorkflowOrchestratorService()

    # Create two-step workflow with trivial operations (use existing services; expect graceful handling if missing)
    create = await svc.process_request({
        "action": "create_workflow",
        "name": "wf_test",
        "steps": [
            {"service_type": ServiceType.SCIENTIFIC_AI.value, "operation": "noop", "parameters": {"x": 1}},
            {"service_type": ServiceType.SCIENTIFIC_AI.value, "operation": "noop", "parameters": {"y": "{{step_0.result}}"}, "dependencies": ["step_0"], "timeout": 1, "max_retries": 1},
        ]
    })
    assert create["success"]
    wf_id = create["workflow_id"]

    # Start execution (it may fail if service not available; we still validate status path and graph endpoint existence)
    await svc.process_request({"action": "execute_workflow", "workflow_id": wf_id})

    # Poll a bit
    for _ in range(10):
        status = await svc.process_request({"action": "get_workflow_status", "workflow_id": wf_id})
        assert status["success"]
        if status["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.1)

    graph = await svc.process_request({"action": "get_workflow_graph", "workflow_id": wf_id})
    assert graph["success"]
    assert len(graph["nodes"]) == 2
    # edge from step_0 -> step_1
    assert any(e["source"] == "step_0" and e["target"] == "step_1" for e in graph["edges"])
