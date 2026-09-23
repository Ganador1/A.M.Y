from app.services.manuscript_assembly_service import manuscript_assembly_service


def test_manuscript_assembly_basic():
    payload = {"title": "Test Study", "introduction": "Intro", "methods": "Methods"}
    doc = manuscript_assembly_service.assemble_manuscript(payload)
    assert "# Title" in doc
    assert "Intro" in doc
