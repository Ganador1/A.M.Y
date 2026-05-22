"""
Tests unitarios para SciPyService

Valida las 7 operaciones implementadas:
- numerical_integration
- optimize_function
- interpolate_data
- compute_fft
- statistical_analysis
- linear_algebra_ops
- solve_ode
"""

import pytest
import asyncio


@pytest.mark.asyncio
async def test_scipy_service_import():
    """Verifica que el servicio se puede importar correctamente"""
    from app.services.scipy_service import SciPyService
    service = SciPyService()
    assert service is not None
    assert hasattr(service, 'process_request')


@pytest.mark.asyncio
async def test_numerical_integration_quad():
    """Test integración numérica con método quad"""
    from app.services.scipy_service import SciPyService
    service = SciPyService()
    
    request = {
        "action": "integrate",
        "function": "sin(x)",
        "limits": [0, 3.14159],
        "method": "quad"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "result" in result
    assert "error_estimate" in result
    assert abs(result["result"] - 2.0) < 0.01  # sin integrado de 0 a π ≈ 2


@pytest.mark.asyncio
async def test_numerical_integration_trapz():
    """Test integración numérica con método trapz"""
    from app.services.scipy_service import SciPyService
    service = SciPyService()
    
    request = {
        "action": "integrate",
        "function": "x**2",
        "limits": [0, 1],
        "method": "trapz"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "result" in result
    # x^2 de 0 a 1 = 1/3 ≈ 0.333
    assert abs(result["result"] - 0.333) < 0.01


@pytest.mark.asyncio
async def test_optimize_function():
    """Test optimización de función Rosenbrock"""
    from app.services.scipy_service import SciPyService
    service = SciPyService()
    
    request = {
        "action": "optimize",
        "function": "rosenbrock",
        "initial_guess": [0.0, 0.0]
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "optimal_point" in result
    assert "optimal_value" in result
    assert "iterations" in result
    # Mínimo de Rosenbrock está en (1, 1)
    assert abs(result["optimal_point"][0] - 1.0) < 0.1
    assert abs(result["optimal_point"][1] - 1.0) < 0.1


@pytest.mark.asyncio
async def test_interpolate_data_cubic():
    """Test interpolación cúbica"""
    from app.services.scipy_service import SciPyService
    service = SciPyService()
    
    request = {
        "action": "interpolate",
        "x_data": [0.0, 1.0, 2.0, 3.0],
        "y_data": [0.0, 1.0, 4.0, 9.0],
        "method": "cubic",
        "x_new": [0.5, 1.5, 2.5]
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "interpolated_values" in result
    assert len(result["interpolated_values"]) == 3


@pytest.mark.asyncio
async def test_compute_fft():
    """Test transformada rápida de Fourier"""
    from app.services.scipy_service import SciPyService
    service = SciPyService()
    
    request = {
        "action": "fft",
        "signal": [1.0, 2.0, 1.0, 2.0, 1.0, 2.0],
        "sampling_rate": 100.0
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "fft_magnitude" in result
    assert "frequencies" in result
    assert "dominant_frequency" in result


@pytest.mark.asyncio
async def test_statistical_analysis():
    """Test análisis estadístico"""
    from app.services.scipy_service import SciPyService
    service = SciPyService()
    
    request = {
        "action": "stats",
        "data": [1.5, 2.3, 1.8, 2.7, 1.9, 2.4, 1.7, 2.5],
        "test_type": "ttest"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "mean" in result
    assert "std" in result
    assert result["mean"] > 0


@pytest.mark.asyncio
async def test_linear_algebra_ops():
    """Test operaciones de álgebra lineal"""
    from app.services.scipy_service import SciPyService
    service = SciPyService()
    
    request = {
        "action": "linear_algebra",
        "matrix": [[1, 2], [3, 4]],
        "operation": "det"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "eigenvalues" in result
    assert "eigenvectors" in result
    assert "determinant" in result


@pytest.mark.asyncio
async def test_solve_ode():
    """Test resolución de ecuaciones diferenciales ordinarias"""
    from app.services.scipy_service import SciPyService
    service = SciPyService()
    
    request = {
        "action": "ode_solve",
        "equation_type": "simple",
        "initial_conditions": [1.0],
        "time_span": [0.0, 10.0]
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "solution" in result
    assert len(result["solution"]) > 0


@pytest.mark.asyncio
async def test_invalid_operation():
    """Test operación inválida"""
    from app.services.scipy_service import SciPyService
    service = SciPyService()
    
    request = {
        "action": "invalid_operation"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_missing_parameters():
    """Test parámetros faltantes"""
    from app.services.scipy_service import SciPyService
    service = SciPyService()
    
    request = {
        "action": "integrate"
        # Faltan function y limits
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is False
    assert "error" in result
