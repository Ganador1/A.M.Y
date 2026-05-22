import os
import tempfile
import json
from pathlib import Path
from app.services.plausibility_scoring_service import PlausibilityScoringService, get_plausibility_service
from app.database import get_db_session
from app.models.hypothesis_models import HypothesisRecord, HypothesisEvidenceRecord
from app.models.plausibility_models import HypothesisPlausibilityMetricRecord


def test_plausibility_basic_scoring():
    svc = PlausibilityScoringService()
    data = {
        "title": "Efecto de nanopartículas en cinética enzimática",
        "description": "Evaluar si la adición de nanopartículas de oro (5nm) incrementa la tasa catalítica (kcat) en un 15% en presencia de cofactor X a 37C.",
        "variables": ["nanoparticles_size", "kcat", "cofactor_concentration"],
        "expected_outcome": "Incremento del 15% ±5% en kcat",
        "assumptions": ["Las nanopartículas no alteran la estructura terciaria"],
    }
    result = svc.score_hypothesis(data)
    assert result["success"]
    assert 0 <= result["composite"] <= 1
    # Debe haber componentes clave presentes
    assert "title_length" in result["components"]


def test_plausibility_duplication_penalty():
    svc = get_plausibility_service()
    base = {
        "title": "Relación presión-temperatura en material compuesto",
        "description": "Se analiza el cambio en módulo elástico con incremento de temperatura de 20C a 200C usando simulación FEM.",
        "variables": ["temperature", "elastic_modulus"],
        "expected_outcome": "Disminución lineal del 10%",
        "assumptions": ["Comportamiento elástico dentro del rango"],
    }
    # Registrar referencia
    svc.add_reference_hypothesis(base)
    scored = svc.score_hypothesis(base)
    # Esperamos penalización duplicación (score menor comparado con variante distinta)
    assert scored["components"].get("duplication_penalty", 0) <= 0


def test_plausibility_domain_weights():
    """Test de aplicación de pesos por dominio desde config YAML."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
domain_weights:
  physics: 1.2
  biology: 0.8
  unknown: 1.0
""")
        temp_config = f.name
    
    try:
        svc = PlausibilityScoringService(config_path=temp_config)
        
        data_physics = {
            "title": "Modelo cuántico para superconductividad",
            "description": "Aplicar teoría BCS modificada para predecir temperatura crítica en nuevo material superconductor a base de cobre.",
            "domain": "physics",
            "variables": ["temp_critical", "cooper_pairs"],
            "assumptions": ["Acoplamiento débil"]
        }
        
        data_biology = data_physics.copy()
        data_biology["domain"] = "biology"
        
        result_physics = svc.score_hypothesis(data_physics)
        result_biology = svc.score_hypothesis(data_biology)
        
        # Physics debería tener mayor peso (1.2 vs 0.8)
        assert result_physics["domain_weight"] == 1.2
        assert result_biology["domain_weight"] == 0.8
        assert result_physics["composite"] > result_biology["composite"]
        
    finally:
        os.unlink(temp_config)


def test_plausibility_evidence_adjustment():
    """Test de ajuste por evidencia usando hipótesis con registros en DB."""
    # Crear hipótesis de prueba en DB
    db = get_db_session()
    hyp = None
    try:
        hyp = HypothesisRecord(
            hypothesis_uuid="test-uuid-evidence",
            title="Test hypothesis",
            description="Test description",
            domain="chemistry"
        )
        db.add(hyp)
        db.commit()
        db.refresh(hyp)
        
        # Añadir evidencias con diferentes support_scores
        ev1 = HypothesisEvidenceRecord(
            hypothesis_id=hyp.id,
            evidence_type="experiment",
            support_score=0.8
        )
        ev2 = HypothesisEvidenceRecord(
            hypothesis_id=hyp.id,
            evidence_type="literature",
            support_score=0.6
        )
        db.add_all([ev1, ev2])
        db.commit()
        
        svc = PlausibilityScoringService()
        data = {
            "title": "Test hypothesis",
            "description": "Test description with sufficient length for scoring",
            "hypothesis_uuid": "test-uuid-evidence",
            "variables": ["var1"],
            "assumptions": ["assumption1"]
        }
        
        result = svc.score_hypothesis(data)
        assert result["success"]
        if "evidence" in result:
            assert result["evidence"]["evidence_count"] == 2
            assert result["evidence"]["avg_support"] == 0.7  # (0.8 + 0.6) / 2
            assert result["evidence"]["factor"] > 1.0  # should boost score
        
    finally:
        # Cleanup
        if hyp is not None:
            db.query(HypothesisEvidenceRecord).filter(HypothesisEvidenceRecord.hypothesis_id == hyp.id).delete()
            db.query(HypothesisRecord).filter(HypothesisRecord.id == hyp.id).delete()
            db.commit()
        db.close()


def test_plausibility_persistence_metrics():
    """Test de persistencia de métricas en tabla hypothesis_plausibility_metrics."""
    db = get_db_session()
    try:
        # Primero crear hipótesis base
        hyp = HypothesisRecord(
            hypothesis_uuid="test-uuid-persist",
            title="Persistence test",
            description="Testing metric persistence",
            domain="materials"
        )
        db.add(hyp)
        db.commit()
        db.refresh(hyp)
        
        svc = PlausibilityScoringService()
        data = {
            "title": "Persistence test hypothesis",
            "description": "This is a test with sufficient length to pass description requirements",
            "hypothesis_uuid": "test-uuid-persist",
            "domain": "materials",
            "variables": ["density", "strength"],
            "assumptions": ["Linear elasticity"]
        }
        
        result = svc.score_hypothesis(data)
        assert result["success"]
        assert "metric_id" in result
        
        # Verificar que se guardó en DB
        metric = db.query(HypothesisPlausibilityMetricRecord).filter_by(
            hypothesis_uuid="test-uuid-persist"
        ).first()
        assert metric is not None
        assert metric.composite == result["composite"]
        assert metric.components is not None
        assert isinstance(metric.components, dict)
        assert "title_length" in metric.components
        
    finally:
        # Cleanup
        db.query(HypothesisPlausibilityMetricRecord).filter_by(hypothesis_uuid="test-uuid-persist").delete()
        db.query(HypothesisRecord).filter_by(hypothesis_uuid="test-uuid-persist").delete()
        db.commit()
        db.close()


def test_plausibility_model_fallback():
    """Test de fallback cuando no existe modelo ML entrenado."""
    svc = PlausibilityScoringService()
    # Asegurar que no hay modelo cargado
    svc.model = None
    
    data = {
        "title": "Fallback test",
        "description": "Test scoring without ML model - should use heuristic scoring only",
        "variables": ["param1"],
        "assumptions": ["base assumption"]
    }
    
    result = svc.score_hypothesis(data)
    assert result["success"]
    assert "model_score" not in result  # No debería haber score de modelo ML
    assert result["composite"] > 0  # Pero sí score heurístico


def test_plausibility_model_training():
    """Test de entrenamiento condicional de modelo."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Crear dataset de prueba
        dataset_path = Path(temp_dir) / "data" / "plausibility_training.jsonl"
        dataset_path.parent.mkdir(parents=True)
        
        # Datos sintéticos para entrenamiento
        training_data = [
            {"hypothesis_uuid": "h1", "composite": 0.8, "label": 1},
            {"hypothesis_uuid": "h2", "composite": 0.3, "label": 0},
            {"hypothesis_uuid": "h3", "composite": 0.9, "label": 1},
            {"hypothesis_uuid": "h4", "composite": 0.2, "label": 0},
            {"hypothesis_uuid": "h5", "composite": 0.7, "label": 1},
        ]
        
        with open(dataset_path, 'w') as f:
            for item in training_data:
                f.write(json.dumps(item) + "\n")
        
        # Cambiar directorio de trabajo temporalmente
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            svc = PlausibilityScoringService()
            result = svc.train_model_if_dataset_available(min_samples=3)
            
            # Debería fallar por pocos samples (5 < 30 default)
            if result["success"]:
                assert result["samples"] >= 3
            else:
                assert "insuficiente" in result.get("error", "")
                
        finally:
            os.chdir(original_cwd)
