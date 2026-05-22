from app.services.mathematical_discovery_engine import MathematicalDiscoveryEngine
from app.services.mathematical_discovery_persistence import DiscoveryPersistence


def test_investigation_persistence_tmp(tmp_path):
    storage = tmp_path / "discoveries.jsonl"
    persistence = DiscoveryPersistence(storage_path=str(storage))
    engine = MathematicalDiscoveryEngine(persistence=persistence)
    # Tomar primera seed y ejecutar
    seed = engine.generate_seed_conjectures(limit=1)[0]
    result = engine.investigate_conjecture(seed)
    assert result.status in {"proven", "refuted", "open"}
    # Verificar archivo
    assert storage.exists()
    lines = storage.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    # Leer vía API de persistencia
    data = persistence.read_all()
    assert len(data) == 1
    assert data[0]["statement"] == seed.statement
