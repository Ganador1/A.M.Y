"""
Smoke tests for Personalized Medicine endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.routers.personalized_medicine import router


client = TestClient(router)


def test_personalized_medicine_health():
    """Test personalized medicine health endpoint"""
    response = client.get("/api/personalized-medicine/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["service"] == "PersonalizedMedicine"
    assert data["status"] == "operational"
    assert "pgx_genes_supported" in data
    assert "drugs_in_database" in data


def test_pharmacogenomics_analysis():
    """Test pharmacogenomics analysis endpoint"""
    payload = {
        "variants": [
            {
                "gene": "CYP2D6",
                "variant": "*1/*10",
                "allele": "*10",
                "zygosity": "heterozygous"
            },
            {
                "gene": "CYP2C19",
                "variant": "*1/*2",
                "allele": "*2",
                "zygosity": "heterozygous"
            }
        ]
    }
    
    response = client.post("/api/personalized-medicine/pharmacogenomics", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "analyzed_genes" in data
    assert "diplotypes" in data
    assert "metabolizer_phenotypes" in data
    assert "dosing_recommendations" in data
    assert "high_risk_medications" in data
    assert "drug_interactions" in data
    assert "clinical_significance" in data


def test_cancer_analysis():
    """Test cancer mutations analysis endpoint"""
    payload = {
        "mutations": [
            {
                "gene": "EGFR",
                "variant": "L858R",
                "type": "missense",
                "position": 858,
                "id": "EGFR_L858R_001"
            },
            {
                "gene": "TP53",
                "variant": "R175H",
                "type": "missense",
                "position": 175,
                "id": "TP53_R175H_001"
            }
        ]
    }
    
    response = client.post("/api/personalized-medicine/cancer-analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "total_mutations" in data
    assert "mutation_types" in data
    assert "driver_mutations" in data
    assert "tumor_mutational_burden" in data
    assert "tmb_category" in data
    assert "actionable_mutations" in data
    assert "predicted_neoantigens" in data
    assert "immunotherapy_potential" in data


def test_drug_recommendations():
    """Test drug recommendations endpoint"""
    response = client.get("/api/personalized-medicine/drug-recommendations/warfarin")
    assert response.status_code == 200
    data = response.json()
    
    assert data["drug"] == "warfarin"
    assert "relevant_genes" in data
    assert "recommendations" in data
    assert "clinical_guidelines" in data


def test_drug_recommendations_not_found():
    """Test drug recommendations for unknown drug"""
    response = client.get("/api/personalized-medicine/drug-recommendations/unknown_drug")
    assert response.status_code == 200
    data = response.json()
    
    assert "error" in data
    assert "no encontrado" in data["error"]


def test_pgx_genes():
    """Test PGX genes endpoint"""
    response = client.get("/api/personalized-medicine/pgx-genes")
    assert response.status_code == 200
    data = response.json()
    
    assert "pgx_genes" in data
    assert "total_genes" in data
    assert "categories" in data
    assert len(data["pgx_genes"]) == data["total_genes"]
    assert "CYP2D6" in data["pgx_genes"]
    assert "TPMT" in data["pgx_genes"]


def test_drug_interaction_check():
    """Test drug interaction check endpoint"""
    payload = {
        "CYP2D6": "intermediate_metabolizer",
        "CYP2C19": "poor_metabolizer"
    }
    
    response = client.post("/api/personalized-medicine/drug-interaction-check", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "phenotypes_analyzed" in data
    assert "interactions_found" in data
    assert "interactions" in data
    assert "risk_assessment" in data
    assert data["risk_assessment"] in ["low", "medium", "high"]


def test_pharmacogenomics_empty_variants():
    """Test pharmacogenomics with empty variants list"""
    payload = {"variants": []}
    
    response = client.post("/api/personalized-medicine/pharmacogenomics", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "analyzed_genes" in data
    assert len(data["analyzed_genes"]) == 0


def test_cancer_analysis_empty_mutations():
    """Test cancer analysis with empty mutations list"""
    payload = {"mutations": []}
    
    response = client.post("/api/personalized-medicine/cancer-analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_mutations"] == 0
    assert data["tumor_mutational_burden"] == 0.0
    assert data["tmb_category"] == "low"
