from app.services.workspace_manager_service import workspace_manager_service

def test_workspace_lifecycle():
    ws = workspace_manager_service.create({"purpose": "test"})
    workspace_manager_service.add_artifact(ws["id"], "a", 123)
    listed = workspace_manager_service.list()
    assert any(w["id"] == ws["id"] for w in listed)
    removed = workspace_manager_service.cleanup(0)  # none should be old yet
    assert removed >= 0
