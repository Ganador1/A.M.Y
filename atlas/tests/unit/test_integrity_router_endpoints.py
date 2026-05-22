"""Tests para endpoint de reportes de integridad"""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers.integrity import router


# Create test app
app = FastAPI()
app.include_router(router)  # El router ya tiene prefix="/api/integrity"

client = TestClient(app)


def test_integrity_report_endpoint():
    """Test endpoint de reporte comprehensivo"""
    response = client.get("/api/integrity/integrity-report")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura básica
    assert data["success"] is True
    assert "report" in data
    assert "generated_at" in data
    
    report = data["report"]
    
    # Verificar secciones principales
    required_sections = ["summary", "artifacts", "services", "validation", "trends", "cache", "health_indicators"]
    for section in required_sections:
        assert section in report, f"Missing section: {section}"
    
    # Verificar summary metrics
    summary = report["summary"]
    required_summary_fields = [
        "total_artifacts", "valid_artifacts", "integrity_health_percent",
        "total_services", "service_types", "validation_score", "risk_level",
        "lineage_coverage_percent"
    ]
    for field in required_summary_fields:
        assert field in summary, f"Missing summary field: {field}"
    
    # Verificar tipos de datos
    assert isinstance(summary["total_artifacts"], int)
    assert isinstance(summary["integrity_health_percent"], (int, float))
    assert summary["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    
    # Verificar health indicators
    health = report["health_indicators"]
    required_health_checks = [
        "integrity_ok", "service_diversity_ok", "validation_score_ok",
        "risk_level_ok", "lineage_coverage_ok"
    ]
    for check in required_health_checks:
        assert check in health, f"Missing health check: {check}"
        assert isinstance(health[check], bool)


def test_cache_stats_endpoint():
    """Test endpoint de estadísticas de cache"""
    response = client.get("/api/integrity/cache-stats")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "cache_stats" in data
    
    # Cache puede estar habilitado o no
    cache_stats = data["cache_stats"]
    if cache_stats.get("cache_enabled"):
        # Si está habilitado, debe tener stats básicas
        assert "size" in cache_stats
        assert "hits" in cache_stats
        assert "misses" in cache_stats


def test_validation_snapshots_endpoint():
    """Test endpoint de snapshots de validation matrix"""
    response = client.get("/api/integrity/validation-snapshots?hours_back=1&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "snapshots" in data
    assert "hours_analyzed" in data
    assert data["hours_analyzed"] == 1
    assert isinstance(data["snapshots"], list)


def test_validation_trends_endpoint():
    """Test endpoint de análisis de tendencias"""
    response = client.get("/api/integrity/validation-trends?hours_back=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "trend_analysis" in data
    
    trends = data["trend_analysis"]
    assert "trend" in trends
    assert "snapshots_count" in trends
    
    # Trend puede ser "analyzed" o "insufficient_data"
    assert trends["trend"] in ["analyzed", "insufficient_data", "no_time_difference"]


def test_record_snapshot_endpoint():
    """Test endpoint para registro manual de snapshot"""
    response = client.post("/api/integrity/validation-snapshot")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "success" in data
    assert "recorded" in data
    assert isinstance(data["success"], bool)
    assert isinstance(data["recorded"], bool)


def test_risk_policy_endpoints():
    """Test endpoints de política de riesgo"""
    # Get current policy
    response = client.get("/api/integrity/risk/policy")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "policy" in data
    
    policy = data["policy"]
    required_fields = ["block_critical", "require_signature_high", "signature_levels", "thresholds"]
    for field in required_fields:
        assert field in policy, f"Missing policy field: {field}"
    
    # Update policy (just test the endpoint, revert after)
    original_policy = policy.copy()
    update_data = {
        "block_critical": True,
        "require_signature_high": False
    }
    
    response = client.put("/api/integrity/risk/policy", json=update_data)
    assert response.status_code == 200
    
    updated_data = response.json()
    assert updated_data["success"] is True
    
    # Revert to original
    client.put("/api/integrity/risk/policy", json=original_policy)


if __name__ == "__main__":
    pytest.main([__file__])
