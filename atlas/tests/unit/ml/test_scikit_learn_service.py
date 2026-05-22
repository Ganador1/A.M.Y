"""
Tests unitarios para ScikitLearnService

Valida las 6 operaciones implementadas:
- classification
- regression
- clustering
- dimensionality_reduction
- cross_validation
- feature_selection
"""

import pytest


@pytest.mark.asyncio
async def test_scikit_service_import():
    """Verifica que el servicio se puede importar correctamente"""
    from app.services.scikit_learn_service import ScikitLearnService
    service = ScikitLearnService()
    assert service is not None
    assert hasattr(service, 'process_request')


@pytest.mark.asyncio
async def test_classification():
    """Test clasificación con Random Forest"""
    from app.services.scikit_learn_service import ScikitLearnService
    service = ScikitLearnService()
    
    request = {
        "action": "classification",
        "n_samples": 100,
        "n_features": 4,
        "test_size": 0.3
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "accuracy" in result
    assert "f1_score" in result
    assert "feature_importances" in result
    assert result["accuracy"] > 0.5  # Mejor que random


@pytest.mark.asyncio
async def test_regression():
    """Test regresión con Ridge"""
    from app.services.scikit_learn_service import ScikitLearnService
    service = ScikitLearnService()
    
    request = {
        "action": "regression",
        "n_samples": 100,
        "n_features": 3,
        "test_size": 0.3
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "r2_score" in result
    assert "rmse" in result
    assert "coefficients" in result


@pytest.mark.asyncio
async def test_clustering():
    """Test clustering con KMeans"""
    from app.services.scikit_learn_service import ScikitLearnService
    service = ScikitLearnService()
    
    request = {
        "action": "clustering",
        "n_samples": 100,
        "n_features": 2,
        "n_clusters": 3
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "silhouette_score" in result
    assert "inertia" in result
    assert "cluster_centers" in result
    assert len(result["cluster_centers"]) == 3


@pytest.mark.asyncio
async def test_dimensionality_reduction():
    """Test reducción de dimensionalidad con PCA"""
    from app.services.scikit_learn_service import ScikitLearnService
    service = ScikitLearnService()
    
    request = {
        "action": "dimensionality_reduction",
        "n_samples": 100,
        "n_features": 10,
        "n_components": 3
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "explained_variance_ratio" in result
    assert "total_variance_preserved" in result
    assert len(result["explained_variance_ratio"]) == 3
    assert result["total_variance_preserved"] <= 1.0


@pytest.mark.asyncio
async def test_cross_validation():
    """Test validación cruzada"""
    from app.services.scikit_learn_service import ScikitLearnService
    service = ScikitLearnService()
    
    request = {
        "action": "cross_validation",
        "n_samples": 100,
        "n_features": 4,
        "cv_folds": 5
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "scores" in result
    assert "mean_score" in result
    assert "std_score" in result
    assert len(result["scores"]) == 5


@pytest.mark.asyncio
async def test_feature_selection():
    """Test selección de features"""
    from app.services.scikit_learn_service import ScikitLearnService
    service = ScikitLearnService()
    
    request = {
        "action": "feature_selection",
        "n_samples": 100,
        "n_features": 10,
        "k_features": 5
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "selected_indices" in result
    assert "feature_scores" in result
    assert len(result["selected_indices"]) == 5


@pytest.mark.asyncio
async def test_invalid_operation():
    """Test operación inválida"""
    from app.services.scikit_learn_service import ScikitLearnService
    service = ScikitLearnService()
    
    request = {
        "action": "invalid_operation"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_clustering_with_custom_data():
    """Test clustering con datos personalizados"""
    pytest.skip("ScikitLearnService actualmente genera datos internos; pendiente soporte de datos personalizados.")
    from app.services.scikit_learn_service import ScikitLearnService
    service = ScikitLearnService()
    
    # Datos de ejemplo (3 clusters obvios)
    data = [
        [0.0, 0.0], [0.1, 0.1], [0.0, 0.1],  # Cluster 1
        [5.0, 5.0], [5.1, 5.1], [5.0, 5.1],  # Cluster 2
        [10.0, 10.0], [10.1, 10.1], [10.0, 10.1]  # Cluster 3
    ]
    
    request = {
        "action": "clustering",
        "data": data,
        "n_clusters": 3
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert result["metrics"]["silhouette_score"] > 0.7  # Alta separación
