from app.services.mathematical_discovery_engine import MathematicalDiscoveryEngine
from app.services.mathematical_discovery_persistence import DiscoveryPersistence
from app.services.mathematical_exporter import results_to_markdown

def test_autonomous_with_mutations_and_export(tmp_path):
    persistence = DiscoveryPersistence(storage_path=str(tmp_path / "disc_test.jsonl"))
    engine = MathematicalDiscoveryEngine(persistence=persistence)
    results = engine.autonomous_exploration(domain="algebra", cycles=2, per_cycle=2, enable_mutations=True, max_mutations_per_cycle=3)
    assert results, "Debe producir resultados"
    # Debe haber al menos un resultado con origin=mutation en metadata si mutaciones aplican
    has_mutation = any(r.conjecture.metadata.get("origin") == "mutation" for r in results)
    assert has_mutation, "Se esperaba al menos una mutación"
    md = results_to_markdown(results)
    assert "Informe de Descubrimientos" in md
    assert md.count("Conjetura:") >= len(results) // 2  # heurístico
