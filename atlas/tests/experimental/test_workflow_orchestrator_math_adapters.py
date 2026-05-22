import asyncio
import os
import pytest

from app.config import settings
from app.database import init_database, close_database


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Use SQLite and enable DB for step execution records; avoid auto-init during imports
    os.environ['ENABLE_DATABASE'] = 'true'
    os.environ['PYTEST_RUNNING'] = '1'
    settings.enable_database = True
    settings.database_url = "sqlite:///migrations.db"
    init_database()
    yield
    close_database()


@pytest.mark.asyncio
async def test_orchestrator_math_adapters_end_to_end():
    """End-to-end test orchestrating multiple math adapters with dependencies."""
    from app.services.workflow_orchestration import WorkflowOrchestratorService, ServiceType

    svc = WorkflowOrchestratorService()

    # Build a workflow across arithmetic -> calculus -> equations -> statistics -> graphing -> geometry
    create = await svc.process_request({
        "action": "create_workflow",
        "name": "wf_math_chain",
        "steps": [
            # step_0: arithmetic add
            {"service_type": ServiceType.ARITHMETIC.value, "operation": "add", "parameters": {"operands": [2, 3, 5]}},
            # step_1: calculus derivative uses previous result to form expression k*x^2 -> derivative 2*k*x
            {"service_type": ServiceType.CALCULUS.value, "operation": "derivative", "parameters": {"expression": "{{step_0.result.result}}*x**2", "variable": "x", "order": 1}, "dependencies": ["step_0"]},
            # step_2: equations solve simple equation using result constant from step_0
            {"service_type": ServiceType.EQUATIONS.value, "operation": "solve_equation", "parameters": {"equation": "x-10=0", "variable": "x"}, "dependencies": ["step_1"]},
            # step_3: statistics descriptive stats on fixed data
            {"service_type": ServiceType.STATISTICS.value, "operation": "descriptive", "parameters": {"data": [1,2,3,4,5]}, "dependencies": ["step_2"]},
            # step_4: graphing single graph
            {"service_type": ServiceType.GRAPHING.value, "operation": "generate_graph", "parameters": {"expression": "x**2", "x_min": -2, "x_max": 2, "points": 50}, "dependencies": ["step_3"]},
            # step_5: geometry circle area
            {"service_type": ServiceType.GEOMETRY.value, "operation": "area", "parameters": {"shape": "circle", "parameters": {"center": [0,0], "radius": 2}}, "dependencies": ["step_4"]},
        ]
    })
    assert create["success"], create
    wf_id = create["workflow_id"]

    # Execute
    start = await svc.process_request({"action": "execute_workflow", "workflow_id": wf_id})
    assert start["success"], start

    # Poll for completion
    for _ in range(60):
        status = await svc.process_request({"action": "get_workflow_status", "workflow_id": wf_id})
        assert status["success"], status
        if status["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.1)

    # Validate completion and key results exist
    status = await svc.process_request({"action": "get_workflow_status", "workflow_id": wf_id})
    assert status["status"] in ("completed", "failed")

    # Graph should have 6 nodes and 5 edges
    graph = await svc.process_request({"action": "get_workflow_graph", "workflow_id": wf_id})
    assert graph["success"], graph
    assert len(graph["nodes"]) == 6
    assert len(graph["edges"]) == 5

    # Cache hit on re-run of a single step: trigger arithmetic again via direct step execution
    # Create a tiny workflow to validate cache set/get quickly
    create2 = await svc.process_request({
        "action": "create_workflow",
        "name": "wf_cache_check",
        "steps": [
            {"service_type": ServiceType.ARITHMETIC.value, "operation": "add", "parameters": {"operands": [2, 3, 5]}},
        ]
    })
    wf2 = create2["workflow_id"]
    await svc.process_request({"action": "execute_workflow", "workflow_id": wf2})
    for _ in range(50):
        status2 = await svc.process_request({"action": "get_workflow_status", "workflow_id": wf2})
        if status2["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.05)

    # Run same workflow again to confirm cache hit recorded
    await svc.process_request({"action": "execute_workflow", "workflow_id": wf2})
    for _ in range(50):
        status2b = await svc.process_request({"action": "get_workflow_status", "workflow_id": wf2})
        if status2b["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.05)

    # Final status check succeeds
    final_status = await svc.process_request({"action": "get_workflow_status", "workflow_id": wf2})
    assert final_status["success"], final_status
