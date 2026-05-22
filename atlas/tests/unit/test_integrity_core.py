import asyncio
from app.integrity_core import integrity_core

def test_register_and_verify_artifact_basic():
    rec = integrity_core.register_artifact({"values": [1,2,3]}, artifact_type="result", metadata={"model_type":"test"}, blockchain=False)
    assert rec.artifact_id
    status = asyncio.run(integrity_core.verify_artifact(rec.artifact_id))
    assert status["artifact_id"] == rec.artifact_id
    assert status["integrity_ok"] is True
    assert status["final_status"] == "valid"

from app import service_registry  # noqa

def test_service_registry_lists_services():
    services = service_registry.list_services()
    # Debe devolver al menos algunos servicios
    assert isinstance(services, list)
    assert all("name" in s for s in services)
