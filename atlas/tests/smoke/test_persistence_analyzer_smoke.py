"""
Tests de smoke para el analizador de persistencia topológica mejorado
"""

import pytest
import asyncio
from app.mathlab.topology.persistence_analyzer import persistence_analyzer


@pytest.mark.asyncio
async def test_persistence_analyzer_basic():
    """Test básico del analizador de persistencia"""
    # Puntos simples que forman un triángulo
    points = [(0.0, 0.0), (1.0, 0.0), (0.5, 0.87)]
    
    result = await persistence_analyzer.compute_persistence_diagram(
        points=points,
        max_edge_length=2.0,
        max_dimension=1
    )
    
    # Verificar estructura básica
    assert "persistence_diagram" in result
    assert "betti_curves" in result
    assert "persistence_entropy" in result
    assert "algorithm" in result
    
    # Verificar que se detectaron algunas características
    diagram = result["persistence_diagram"]
    assert isinstance(diagram, list)
    
    # Verificar estructura de puntos en diagrama
    for point in diagram:
        assert "dimension" in point
        assert "birth" in point
        assert "death" in point
        assert "persistence" in point
        assert point["birth"] <= point["death"]


@pytest.mark.asyncio
async def test_persistence_analyzer_square():
    """Test con puntos que forman un cuadrado (debería detectar un ciclo)"""
    # Cuadrado con punto central
    points = [
        (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0),  # Esquinas
        (0.5, 0.5)  # Centro
    ]
    
    result = await persistence_analyzer.compute_persistence_diagram(
        points=points,
        max_edge_length=1.5,
        max_dimension=2
    )
    
    assert "persistence_diagram" in result
    assert "lifetime_statistics" in result
    
    # Verificar estadísticas
    stats = result["lifetime_statistics"]
    assert "mean" in stats
    assert "std" in stats
    assert "total_features" in stats
    assert stats["total_features"] >= 0


@pytest.mark.asyncio
async def test_persistence_analyzer_line():
    """Test con puntos en línea (solo componentes, sin ciclos)"""
    # Puntos en línea recta
    points = [(i * 0.5, 0.0) for i in range(5)]
    
    result = await persistence_analyzer.compute_persistence_diagram(
        points=points,
        max_edge_length=1.0,
        max_dimension=1
    )
    
    assert "persistence_diagram" in result
    assert "betti_curves" in result
    
    # Verificar que el algoritmo está identificado
    assert result["algorithm"] in ["gudhi_rips", "custom_filtration"]


@pytest.mark.asyncio
async def test_persistence_entropy_calculation():
    """Test del cálculo de entropía de persistencia"""
    # Mock de diagrama de persistencia
    mock_diagram = [
        {"dimension": 0, "birth": 0.0, "death": 1.0, "persistence": 1.0},
        {"dimension": 0, "birth": 0.1, "death": 0.5, "persistence": 0.4},
        {"dimension": 1, "birth": 0.2, "death": 0.8, "persistence": 0.6}
    ]
    
    entropy = persistence_analyzer._calculate_persistence_entropy(mock_diagram)
    
    assert isinstance(entropy, float)
    assert entropy >= 0.0  # La entropía es no negativa


@pytest.mark.asyncio
async def test_persistence_analyzer_empty():
    """Test con lista vacía de puntos"""
    with pytest.raises(Exception):  # Debería fallar con pocos puntos
        await persistence_analyzer.compute_persistence_diagram(
            points=[],
            max_edge_length=1.0,
            max_dimension=1
        )


@pytest.mark.asyncio
async def test_persistence_analyzer_single_point():
    """Test con un solo punto"""
    with pytest.raises(Exception):  # Debería fallar con un solo punto
        await persistence_analyzer.compute_persistence_diagram(
            points=[(0.0, 0.0)],
            max_edge_length=1.0,
            max_dimension=1
        )


@pytest.mark.asyncio
async def test_stability_metrics():
    """Test de métricas de estabilidad (si Gudhi está disponible)"""
    from app.mathlab.topology.persistence_analyzer import GUDHI_AVAILABLE
    
    if not GUDHI_AVAILABLE:
        pytest.skip("Gudhi not available for stability metrics")
    
    # Crear dos diagramas simples
    diagram1 = [
        {"dimension": 0, "birth": 0.0, "death": 1.0, "persistence": 1.0}
    ]
    diagram2 = [
        {"dimension": 0, "birth": 0.1, "death": 0.9, "persistence": 0.8}
    ]
    
    stability = await persistence_analyzer.compute_persistence_stability(
        diagram1, diagram2
    )
    
    assert "bottleneck_distance" in stability
    assert "wasserstein_distance" in stability


if __name__ == "__main__":
    pytest.main([__file__])
