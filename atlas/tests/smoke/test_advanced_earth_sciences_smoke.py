"""
Smoke tests for Advanced Earth Sciences endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.routers.advanced_earth_sciences import router


client = TestClient(router)


def test_advanced_earth_sciences_health():
    """Test advanced earth sciences health endpoint"""
    response = client.get("/api/advanced-earth-sciences/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["service"] == "AdvancedEarthSciences"
    assert data["status"] == "operational"
    assert data["simulation_mode"] == True
    assert "models_available" in data


def test_get_supported_models():
    """Test supported models endpoint"""
    response = client.get("/api/advanced-earth-sciences/supported-models")
    assert response.status_code == 200
    data = response.json()
    
    assert "climate_models" in data
    assert "seismic_analysis_types" in data
    assert "ocean_variables" in data
    assert "capabilities" in data
    assert "CESM2" in data["climate_models"]


def test_climate_model_analysis():
    """Test CMIP6 climate model analysis"""
    payload = {
        "model_name": "CESM2",
        "scenario": "SSP245",
        "region": {
            "lat_min": 40.0,
            "lat_max": 50.0,
            "lon_min": -10.0,
            "lon_max": 10.0
        },
        "start_year": "2020",
        "end_year": "2050"
    }
    
    response = client.post("/api/advanced-earth-sciences/climate-model/cmip6", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "analysis_id" in data
    assert data["analysis_type"] == "climate_model_cmip6"
    assert data["status"] == "completed"
    assert "results" in data
    assert "temperature_trends" in data["results"]
    assert "extreme_events" in data["results"]
    assert "tipping_points" in data["results"]


def test_seismic_analysis():
    """Test advanced seismic analysis"""
    payload = {
        "min_magnitude": 5.0,
        "max_magnitude": 8.0,
        "time_window_hours": 48,
        "analysis_types": ["magnitude_estimation", "location_refinement", "tsunami_assessment"]
    }
    
    response = client.post("/api/advanced-earth-sciences/seismic/advanced-analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "analysis_id" in data
    assert data["analysis_type"] == "seismic_advanced"
    assert data["status"] == "completed"
    assert "results" in data
    assert "total_events" in data["results"]
    assert "magnitude_distribution" in data["results"]
    assert "seismic_hazard" in data["results"]


def test_ocean_modeling():
    """Test advanced ocean modeling"""
    payload = {
        "region": {
            "lat_min": 30.0,
            "lat_max": 40.0,
            "lon_min": -80.0,
            "lon_max": -60.0
        },
        "analysis_type": "regional",
        "time_span_days": 30,
        "include_eddies": True,
        "include_fronts": True
    }
    
    response = client.post("/api/advanced-earth-sciences/ocean/advanced-modeling", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "analysis_id" in data
    assert data["analysis_type"] == "ocean_modeling_advanced"
    assert data["status"] == "completed"
    assert "results" in data
    assert "eddies" in data["results"]
    assert "ocean_fronts" in data["results"]
    assert "current_analysis" in data["results"]


def test_quick_climate_analysis():
    """Test quick climate analysis shortcut"""
    response = client.post("/api/advanced-earth-sciences/quick/climate-analysis?model=CESM2&scenario=SSP585")
    assert response.status_code == 200
    data = response.json()
    
    assert data["model_name"] == "CESM2"
    assert data["scenario"] == "SSP585"
    assert "results" in data
    assert "temperature_trends" in data["results"]


def test_quick_seismic_monitoring():
    """Test quick seismic monitoring shortcut"""
    response = client.post("/api/advanced-earth-sciences/quick/seismic-monitoring?min_magnitude=6.0&hours=12")
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_type"] == "seismic_advanced"
    assert "results" in data
    assert "total_events" in data["results"]


def test_quick_ocean_currents():
    """Test quick ocean currents analysis"""
    response = client.post("/api/advanced-earth-sciences/quick/ocean-currents?lat_min=35&lat_max=45&lon_min=-75&lon_max=-65&days=7")
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_type"] == "ocean_modeling_advanced"
    assert "results" in data
    assert "current_analysis" in data["results"]


def test_marine_heatwave_detection():
    """Test marine heatwave detection"""
    response = client.post("/api/advanced-earth-sciences/quick/marine-heatwave-detection?lat_min=20&lat_max=30&lon_min=-90&lon_max=-80&days=30")
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_type"] == "ocean_modeling_advanced"
    assert "results" in data
    assert "marine_heatwaves" in data["results"]


def test_temperature_trends():
    """Test temperature trends analysis"""
    response = client.post("/api/advanced-earth-sciences/climate/temperature-trends?model=UKESM1&scenario=SSP126&start_year=2030&end_year=2080")
    assert response.status_code == 200
    data = response.json()
    
    assert data["model_name"] == "UKESM1"
    assert data["scenario"] == "SSP126"
    assert "temperature_trends" in data["results"]


def test_tsunami_risk_assessment():
    """Test tsunami risk assessment"""
    response = client.post("/api/advanced-earth-sciences/seismic/tsunami-risk?lat_min=35&lat_max=45&lon_min=135&lon_max=145&min_magnitude=7.0")
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_type"] == "seismic_advanced"
    assert "tsunami_events" in data["results"]


def test_eddy_detection():
    """Test ocean eddy detection"""
    response = client.post("/api/advanced-earth-sciences/ocean/eddy-detection?lat_min=25&lat_max=35&lon_min=-70&lon_max=-60&days=14")
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_type"] == "ocean_modeling_advanced"
    assert "eddies" in data["results"]


def test_extreme_events_analysis():
    """Test extreme events analysis"""
    payload = {
        "lat_min": 50.0,
        "lat_max": 60.0,
        "lon_min": 10.0,
        "lon_max": 30.0
    }
    
    response = client.post("/api/advanced-earth-sciences/climate/extreme-events?model=GFDL-ESM4&scenario=SSP370", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["model_name"] == "GFDL-ESM4"
    assert data["scenario"] == "SSP370"
    assert "extreme_events" in data["results"]


def test_primary_productivity_analysis():
    """Test primary productivity analysis"""
    response = client.post("/api/advanced-earth-sciences/ocean/productivity-analysis?lat_min=0&lat_max=10&lon_min=-160&lon_max=-150&days=90")
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_type"] == "ocean_modeling_advanced"
    assert "primary_productivity" in data["results"]


def test_analysis_history():
    """Test analysis history endpoint"""
    # First run some analyses to populate history
    client.post("/api/advanced-earth-sciences/quick/climate-analysis")
    
    response = client.get("/api/advanced-earth-sciences/analysis-history?limit=5")
    assert response.status_code == 200
    data = response.json()
    
    assert "total_analyses" in data
    assert "recent_analyses" in data
    assert "analysis_types" in data


def test_invalid_model():
    """Test with invalid climate model"""
    payload = {
        "model_name": "INVALID_MODEL",
        "scenario": "SSP245"
    }
    
    response = client.post("/api/advanced-earth-sciences/climate-model/cmip6", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "error" in data
    assert "no disponible" in data["error"]


def test_invalid_scenario():
    """Test with invalid scenario"""
    payload = {
        "model_name": "CESM2",
        "scenario": "INVALID_SCENARIO"
    }
    
    response = client.post("/api/advanced-earth-sciences/climate-model/cmip6", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "error" in data
    assert "no disponible" in data["error"]


def test_invalid_region_bounds():
    """Test with invalid region bounds"""
    payload = {
        "region": {
            "lat_min": 95.0,  # Invalid latitude
            "lat_max": 100.0,
            "lon_min": -10.0,
            "lon_max": 10.0
        },
        "analysis_type": "regional",
        "time_span_days": 30
    }
    
    response = client.post("/api/advanced-earth-sciences/ocean/advanced-modeling", json=payload)
    assert response.status_code == 422  # Validation error


def test_climate_global_analysis():
    """Test climate analysis without region (global)"""
    payload = {
        "model_name": "CESM2",
        "scenario": "SSP119",
        "start_year": "2040",
        "end_year": "2060"
    }
    
    response = client.post("/api/advanced-earth-sciences/climate-model/cmip6", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["scenario"] == "SSP119"
    assert data["region"] is None  # Global analysis
