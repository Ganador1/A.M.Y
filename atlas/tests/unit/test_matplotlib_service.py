"""
Tests unitarios para MatplotlibService

Valida las 7 operaciones de visualización:
- create_line_plot
- create_scatter_plot
- create_histogram
- create_bar_plot
- create_heatmap
- create_contour_plot
- create_3d_surface
"""

import pytest


@pytest.mark.asyncio
async def test_matplotlib_service_import():
    """Verifica que el servicio se puede importar correctamente"""
    from app.services.matplotlib_service import MatplotlibService
    service = MatplotlibService()
    assert service is not None
    assert hasattr(service, 'process_request')


@pytest.mark.asyncio
async def test_create_line_plot():
    """Test creación de gráfico de línea"""
    from app.services.matplotlib_service import MatplotlibService
    service = MatplotlibService()
    
    request = {
        "action": "create_line_plot",
        "title": "Test Line Plot",
        "xlabel": "X Axis",
        "ylabel": "Y Axis"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "plot_base64" in result
    assert "plot_type" in result
    assert result["plot_type"] == "line_plot"
    # Verificar que es base64 válido
    assert len(result["plot_base64"]) > 100


@pytest.mark.asyncio
async def test_create_scatter_plot():
    """Test creación de gráfico de dispersión"""
    from app.services.matplotlib_service import MatplotlibService
    service = MatplotlibService()
    
    request = {
        "action": "create_scatter_plot",
        "title": "Test Scatter Plot"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "plot_base64" in result
    assert result["plot_type"] == "scatter_plot"


@pytest.mark.asyncio
async def test_create_histogram():
    """Test creación de histograma"""
    from app.services.matplotlib_service import MatplotlibService
    service = MatplotlibService()
    
    request = {
        "action": "create_histogram",
        "title": "Test Histogram",
        "bins": 20
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "plot_base64" in result
    assert result["plot_type"] == "histogram"


@pytest.mark.asyncio
async def test_create_bar_plot():
    """Test creación de gráfico de barras"""
    from app.services.matplotlib_service import MatplotlibService
    service = MatplotlibService()
    
    request = {
        "action": "create_bar_plot",
        "title": "Test Bar Plot"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "plot_base64" in result
    assert result["plot_type"] == "bar_plot"


@pytest.mark.asyncio
async def test_create_heatmap():
    """Test creación de mapa de calor"""
    from app.services.matplotlib_service import MatplotlibService
    service = MatplotlibService()
    
    request = {
        "action": "create_heatmap",
        "title": "Test Heatmap"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "plot_base64" in result
    assert result["plot_type"] == "heatmap"


@pytest.mark.asyncio
async def test_create_contour_plot():
    """Test creación de gráfico de contornos"""
    from app.services.matplotlib_service import MatplotlibService
    service = MatplotlibService()
    
    request = {
        "action": "create_contour_plot",
        "title": "Test Contour Plot"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "plot_base64" in result
    assert result["plot_type"] == "contour_plot"


@pytest.mark.asyncio
async def test_create_3d_surface():
    """Test creación de superficie 3D"""
    from app.services.matplotlib_service import MatplotlibService
    service = MatplotlibService()
    
    request = {
        "action": "create_3d_surface",
        "title": "Test 3D Surface"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "plot_base64" in result
    assert result["plot_type"] == "3d_surface"


@pytest.mark.asyncio
async def test_line_plot_with_custom_data():
    """Test gráfico de línea con datos personalizados"""
    from app.services.matplotlib_service import MatplotlibService
    service = MatplotlibService()
    
    request = {
        "action": "create_line_plot",
        "x_data": [1, 2, 3, 4, 5],
        "y_data": [2, 4, 6, 8, 10],
        "title": "Custom Line Plot",
        "xlabel": "Time",
        "ylabel": "Value"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "plot_base64" in result


@pytest.mark.asyncio
async def test_scatter_plot_with_custom_data():
    """Test scatter plot con datos personalizados"""
    from app.services.matplotlib_service import MatplotlibService
    service = MatplotlibService()
    
    request = {
        "action": "create_scatter_plot",
        "x_data": [1, 2, 3, 4, 5],
        "y_data": [1, 4, 9, 16, 25],
        "colors": [10, 20, 30, 40, 50],
        "title": "Custom Scatter"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    assert "plot_base64" in result


@pytest.mark.asyncio
async def test_invalid_operation():
    """Test operación inválida"""
    from app.services.matplotlib_service import MatplotlibService
    service = MatplotlibService()
    
    request = {
        "action": "invalid_operation"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_base64_format():
    """Verifica que el formato base64 es válido"""
    from app.services.matplotlib_service import MatplotlibService
    import base64
    
    service = MatplotlibService()
    
    request = {
        "action": "create_line_plot",
        "title": "Base64 Test"
    }
    
    result = await service.process_request(request)
    
    assert result["success"] is True
    
    # Intentar decodificar base64
    try:
        decoded = base64.b64decode(result["plot_base64"])
        # PNG debe empezar con los bytes mágicos
        assert decoded[:8] == b'\x89PNG\r\n\x1a\n'
    except Exception as e:
        pytest.fail(f"Base64 inválido: {e}")
