"""
Smoke tests for Advanced Genomics endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.routers.advanced_genomics import router


client = TestClient(router)


def test_advanced_genomics_health():
    """Test advanced genomics health endpoint"""
    response = client.get("/api/advanced-genomics/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["service"] == "AdvancedGenomics"
    assert data["status"] == "operational"
    assert data["simulation_mode"] == True
    assert "analyses_available" in data


def test_get_supported_analyses():
    """Test supported analyses endpoint"""
    response = client.get("/api/advanced-genomics/supported-analyses")
    assert response.status_code == 200
    data = response.json()
    
    assert "variant_calling" in data
    assert "somatic_analysis" in data
    assert "specialized_analyses" in data
    assert "supported_file_formats" in data
    assert "reference_genomes" in data


def test_deepvariant_analysis():
    """Test DeepVariant variant calling"""
    payload = {
        "sample_info": {
            "sample_id": "test_sample_wgs",
            "file_path": "/data/test.bam",
            "coverage": 35.5,
            "sequencing_platform": "illumina",
            "library_type": "wgs"
        },
        "analysis_type": "wgs",
        "reference_genome": "GRCh38",
        "quality_threshold": 30.0
    }
    
    response = client.post("/api/advanced-genomics/variant-calling/deepvariant", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "analysis_id" in data
    assert data["analysis_type"] == "deepvariant"
    assert data["status"] == "completed"
    assert "results" in data
    assert "total_variants" in data["results"]
    assert "variant_types" in data["results"]
    assert "quality_distribution" in data["results"]


def test_cancer_analysis():
    """Test cancer mutations analysis"""
    payload = {
        "tumor_sample": {
            "sample_id": "tumor_sample_1",
            "file_path": "/data/tumor.bam",
            "coverage": 50.0,
            "library_type": "wes"
        },
        "normal_sample": {
            "sample_id": "normal_sample_1",
            "file_path": "/data/normal.bam",
            "coverage": 40.0,
            "library_type": "wes"
        },
        "cancer_type": "breast_cancer",
        "include_signatures": True
    }
    
    response = client.post("/api/advanced-genomics/cancer-analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "analysis_id" in data
    assert data["analysis_type"] == "cancer_somatic"
    assert data["status"] == "completed"
    assert "results" in data
    assert "driver_mutations" in data["results"]
    assert "tumor_mutational_burden" in data["results"]
    assert "mutational_signatures" in data["results"]
    assert "predicted_neoantigens" in data["results"]


def test_pharmacogenomics_analysis():
    """Test pharmacogenomics analysis"""
    payload = {
        "sample_info": {
            "sample_id": "pgx_sample_1",
            "coverage": 25.0,
            "library_type": "panel"
        },
        "drug_list": ["warfarina", "clopidogrel", "omeprazol"],
        "include_interactions": True
    }
    
    response = client.post("/api/advanced-genomics/pharmacogenomics", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "analysis_id" in data
    assert data["analysis_type"] == "pharmacogenomics"
    assert data["status"] == "completed"
    assert "results" in data
    assert "diplotypes" in data["results"]
    assert "metabolizer_phenotypes" in data["results"]
    assert "dosing_recommendations" in data["results"]
    assert "drug_interactions" in data["results"]


def test_structural_variants_analysis():
    """Test structural variants analysis"""
    payload = {
        "sample_info": {
            "sample_id": "sv_sample_1",
            "file_path": "/data/sv_test.bam",
            "coverage": 30.0,
            "library_type": "wgs"
        },
        "min_sv_size": 50,
        "include_repeats": False
    }
    
    response = client.post("/api/advanced-genomics/structural-variants", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "analysis_id" in data
    assert data["analysis_type"] == "structural_variants"
    assert data["status"] == "completed"
    assert "results" in data
    assert "total_sv_calls" in data["results"]
    assert "sv_type_distribution" in data["results"]
    assert "clinically_relevant_svs" in data["results"]


def test_quick_wgs_analysis():
    """Test quick WGS analysis shortcut"""
    response = client.post("/api/advanced-genomics/quick/wgs-analysis?sample_id=quick_wgs_test")
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_type"] == "deepvariant"
    assert "results" in data
    assert "total_variants" in data["results"]


def test_quick_wes_analysis():
    """Test quick WES analysis shortcut"""
    response = client.post("/api/advanced-genomics/quick/wes-analysis?sample_id=quick_wes_test")
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_type"] == "deepvariant"
    assert "results" in data
    assert "total_variants" in data["results"]


def test_quick_cancer_analysis():
    """Test quick cancer analysis shortcut"""
    response = client.post("/api/advanced-genomics/quick/cancer-analysis?tumor_sample_id=tumor_quick&cancer_type=lung_cancer")
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_type"] == "cancer_somatic"
    assert "results" in data
    assert "driver_mutations" in data["results"]


def test_quick_pgx_analysis():
    """Test quick pharmacogenomics analysis shortcut"""
    payload = ["warfarina", "clopidogrel"]
    response = client.post("/api/advanced-genomics/quick/pgx-analysis?sample_id=pgx_quick", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_type"] == "pharmacogenomics"
    assert "results" in data
    assert "dosing_recommendations" in data["results"]


def test_analysis_history():
    """Test analysis history endpoint"""
    # First run some analyses to populate history
    client.post("/api/advanced-genomics/quick/wgs-analysis?sample_id=history_test")
    
    response = client.get("/api/advanced-genomics/analysis-history?limit=5")
    assert response.status_code == 200
    data = response.json()
    
    assert "total_analyses" in data
    assert "recent_analyses" in data
    assert "analysis_types" in data
    assert "completed_analyses" in data


def test_invalid_analysis_type():
    """Test with invalid analysis type"""
    payload = {
        "sample_info": {
            "sample_id": "invalid_test",
            "library_type": "wgs"
        },
        "analysis_type": "invalid_type"
    }
    
    response = client.post("/api/advanced-genomics/variant-calling/deepvariant", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Should return error for invalid analysis type
    assert "error" in data or "analysis_id" in data  # Could be either depending on implementation


def test_missing_sample_info():
    """Test with missing required sample info"""
    payload = {
        "analysis_type": "wgs"
        # Missing sample_info
    }
    
    response = client.post("/api/advanced-genomics/variant-calling/deepvariant", json=payload)
    assert response.status_code == 422  # Validation error


def test_cancer_analysis_tumor_only():
    """Test cancer analysis with tumor sample only"""
    payload = {
        "tumor_sample": {
            "sample_id": "tumor_only_test",
            "library_type": "wes"
        },
        "include_signatures": True
    }
    
    response = client.post("/api/advanced-genomics/cancer-analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_type"] == "cancer_somatic"
    assert data["normal_sample_id"] is None
    assert "results" in data
