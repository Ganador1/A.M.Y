import pytest

from app.services.infrastructure.matplotlib_service import MatplotlibService


@pytest.mark.asyncio
async def test_matplotlib_service_uses_real_library_for_scatter_plot():
    service = MatplotlibService()

    result = await service.process_request({"action": "create_scatter_plot"})

    assert result["success"] is True
    assert result["operation"] == "scatter_plot"
    assert isinstance(result["image_base64"], str)
    assert len(result["image_base64"]) > 100
