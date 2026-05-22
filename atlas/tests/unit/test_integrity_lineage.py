import asyncio
from app.integrity_core import integrity_core

def test_lineage_link_and_query():
    parent = integrity_core.register_artifact({"data": 1}, artifact_type="dataset", metadata={"model_type":"x"})
    child = integrity_core.register_artifact({"data": 2}, artifact_type="result", metadata={"parent_id": parent.artifact_id})
    # link explicito (si metadata ya lo puso, asegura idempotencia)
    integrity_core.link_child(parent.artifact_id, child.artifact_id)
    lineage_parent = integrity_core.get_lineage(parent.artifact_id)
    lineage_child = integrity_core.get_lineage(child.artifact_id)
    assert lineage_parent["artifact_id"] == parent.artifact_id
    assert child.artifact_id in lineage_parent["children"]
    assert lineage_child["parent_id"] == parent.artifact_id
    # verificacion integridad funciona igual
    status = asyncio.run(integrity_core.verify_artifact(child.artifact_id))
    assert status["final_status"] == "valid"
