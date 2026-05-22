"""
Tests para MLflow Registry Service

Tests comprehensivos para la gestión avanzada del registro de modelos MLflow.
"""

import pytest
from unittest.mock import patch, MagicMock
from mlflow.exceptions import RestException

from app.services.mlflow_registry_service import MLflowRegistryService, RegisteredModelInfo


@pytest.fixture
def registry_service():
    """Fixture para el servicio MLflow registry"""
    with patch('mlflow.set_tracking_uri'), \
         patch('app.services.mlflow_registry_service.MlflowClient'):
        service = MLflowRegistryService()
        return service


@pytest.fixture
def mock_model_version():
    """Mock de ModelVersion de MLflow"""
    mock_version = MagicMock()
    mock_version.name = "TestModel"
    mock_version.version = "1"
    mock_version.current_stage = "None"
    mock_version.description = "Test model description"
    mock_version.creation_timestamp = 1234567890000
    mock_version.last_updated_timestamp = 1234567891000
    mock_version.run_id = "test_run_123"
    mock_version.source = "runs:/test_run_123/model"
    mock_version.status = "READY"
    mock_version.tags = {"env": "test", "version": "v1"}
    return mock_version


@pytest.fixture
def mock_registered_model():
    """Mock de RegisteredModel de MLflow"""
    mock_model = MagicMock()
    mock_model.name = "TestModel"
    mock_model.description = "Test registered model"
    mock_model.creation_timestamp = 1234567890000
    mock_model.last_updated_timestamp = 1234567891000
    mock_model.tags = {"project": "test"}
    mock_model.latest_versions = []
    return mock_model


class TestMLflowRegistryService:
    """Test suite para MLflowRegistryService"""
    
    def test_service_initialization(self, registry_service):
        """Test inicialización del servicio"""
        assert registry_service.name == "MLflowRegistry"
        assert registry_service.tracking_uri == "file:./mlruns"
        assert registry_service.valid_stages == ["None", "Staging", "Production", "Archived"]
        assert hasattr(registry_service, 'client')

    @pytest.mark.asyncio
    async def test_process_request_unknown_action(self, registry_service):
        """Test process_request con acción desconocida"""
        request_data = {"action": "unknown_action"}
        
        result = await registry_service.process_request(request_data)
        
        assert result["success"] is False
        assert "desconocida" in result["error"].lower()
        assert "available_actions" in result

    @pytest.mark.asyncio
    @patch('mlflow.register_model')
    async def test_register_model_success(self, mock_register, registry_service, mock_model_version):
        """Test registro exitoso de modelo"""
        mock_register.return_value = mock_model_version
        
        request_data = {
            "action": "register_model",
            "model_uri": "runs:/test_run_123/model",
            "name": "TestModel",
            "description": "Test description",
            "tags": {"env": "test"}
        }
        
        result = await registry_service.register_model(request_data)
        
        assert result["success"] is True
        assert result["model_name"] == "TestModel"
        assert result["model_version"] == "1"
        assert result["model_uri"] == "runs:/test_run_123/model"
        mock_register.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_model_missing_params(self, registry_service):
        """Test registro de modelo con parámetros faltantes"""
        request_data = {
            "action": "register_model",
            "name": "TestModel"
            # Falta model_uri
        }
        
        result = await registry_service.register_model(request_data)
        
        assert result["success"] is False
        assert "requeridos" in result["error"]

    @pytest.mark.asyncio
    @patch('mlflow.register_model')
    async def test_register_model_mlflow_error(self, mock_register, registry_service):
        """Test error de MLflow al registrar modelo"""
        mock_register.side_effect = RestException({"error_code": "INTERNAL_ERROR", "message": "MLflow error"})
        
        request_data = {
            "action": "register_model",
            "model_uri": "runs:/test_run_123/model",
            "name": "TestModel"
        }
        
        result = await registry_service.register_model(request_data)
        
        assert result["success"] is False
        assert "MLflow" in result["error"]

    @pytest.mark.asyncio
    async def test_list_registered_models(self, registry_service, mock_registered_model):
        """Test listado de modelos registrados"""
        registry_service.client.search_registered_models.return_value = [mock_registered_model]
        
        request_data = {
            "action": "list_registered_models",
            "max_results": 10
        }
        
        result = await registry_service.list_registered_models(request_data)
        
        assert result["success"] is True
        assert "registered_models" in result
        assert result["count"] >= 0

    @pytest.mark.asyncio
    async def test_get_model_version(self, registry_service, mock_model_version):
        """Test obtener versión específica de modelo"""
        registry_service.client.get_model_version.return_value = mock_model_version
        
        request_data = {
            "action": "get_model_version",
            "name": "TestModel",
            "version": "1"
        }
        
        result = await registry_service.get_model_version(request_data)
        
        assert result["success"] is True
        assert result["model_version"]["name"] == "TestModel"
        assert result["model_version"]["version"] == "1"

    @pytest.mark.asyncio
    async def test_get_model_version_missing_params(self, registry_service):
        """Test obtener versión con parámetros faltantes"""
        request_data = {
            "action": "get_model_version",
            "name": "TestModel"
            # Falta version
        }
        
        result = await registry_service.get_model_version(request_data)
        
        assert result["success"] is False
        assert "requeridos" in result["error"]

    @pytest.mark.asyncio
    async def test_get_latest_versions(self, registry_service, mock_model_version):
        """Test obtener últimas versiones por stage"""
        registry_service.client.get_latest_versions.return_value = [mock_model_version]
        
        request_data = {
            "action": "get_latest_versions",
            "name": "TestModel",
            "stages": ["Production"]
        }
        
        result = await registry_service.get_latest_versions(request_data)
        
        assert result["success"] is True
        assert "latest_versions" in result
        assert result["model_name"] == "TestModel"

    @pytest.mark.asyncio
    async def test_transition_model_version_stage(self, registry_service, mock_model_version):
        """Test promoción de modelo entre stages"""
        registry_service.client.transition_model_version_stage.return_value = mock_model_version
        
        request_data = {
            "action": "transition_model_version_stage",
            "name": "TestModel",
            "version": "1",
            "stage": "Staging"
        }
        
        result = await registry_service.transition_model_version_stage(request_data)
        
        assert result["success"] is True
        assert result["model_name"] == "TestModel"
        assert result["version"] == "1"
        assert result["new_stage"] == "Staging"

    @pytest.mark.asyncio
    async def test_transition_invalid_stage(self, registry_service):
        """Test promoción con stage inválido"""
        request_data = {
            "action": "transition_model_version_stage",
            "name": "TestModel",
            "version": "1",
            "stage": "InvalidStage"
        }
        
        result = await registry_service.transition_model_version_stage(request_data)
        
        assert result["success"] is False
        assert "inválido" in result["error"]

    @pytest.mark.asyncio
    async def test_update_model_version(self, registry_service, mock_model_version):
        """Test actualización de descripción de modelo"""
        registry_service.client.update_model_version.return_value = mock_model_version
        
        request_data = {
            "action": "update_model_version",
            "name": "TestModel",
            "version": "1",
            "description": "Updated description"
        }
        
        result = await registry_service.update_model_version(request_data)
        
        assert result["success"] is True
        assert result["model_name"] == "TestModel"
        assert result["updated_description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_search_model_versions(self, registry_service, mock_model_version):
        """Test búsqueda de versiones de modelos"""
        registry_service.client.search_model_versions.return_value = [mock_model_version]
        
        request_data = {
            "action": "search_model_versions",
            "filter": "name='TestModel'",
            "max_results": 50
        }
        
        result = await registry_service.search_model_versions(request_data)
        
        assert result["success"] is True
        assert "model_versions" in result
        assert result["count"] >= 0

    @pytest.mark.asyncio
    async def test_get_model_version_download_uri(self, registry_service):
        """Test obtener URI de descarga"""
        registry_service.client.get_model_version_download_uri.return_value = "s3://bucket/model"
        
        request_data = {
            "action": "get_model_version_download_uri",
            "name": "TestModel",
            "version": "1"
        }
        
        result = await registry_service.get_model_version_download_uri(request_data)
        
        assert result["success"] is True
        assert result["download_uri"] == "s3://bucket/model"

    @pytest.mark.asyncio
    async def test_set_model_version_tag(self, registry_service):
        """Test establecer tag en modelo"""
        request_data = {
            "action": "set_model_version_tag",
            "name": "TestModel",
            "version": "1",
            "key": "env",
            "value": "production"
        }
        
        result = await registry_service.set_model_version_tag(request_data)
        
        assert result["success"] is True
        assert result["tag_key"] == "env"
        assert result["tag_value"] == "production"

    @pytest.mark.asyncio
    async def test_delete_model_version_tag(self, registry_service):
        """Test eliminar tag de modelo"""
        request_data = {
            "action": "delete_model_version_tag",
            "name": "TestModel",
            "version": "1",
            "key": "env"
        }
        
        result = await registry_service.delete_model_version_tag(request_data)
        
        assert result["success"] is True
        assert result["deleted_tag_key"] == "env"

    def test_get_registry_stats(self, registry_service, mock_registered_model, mock_model_version):
        """Test obtener estadísticas del registry"""
        mock_registered_model.latest_versions = [mock_model_version]
        registry_service.client.search_registered_models.return_value = [mock_registered_model]
        
        result = registry_service.get_registry_stats()
        
        assert result["success"] is True
        assert "registry_stats" in result
        assert "total_models" in result["registry_stats"]
        assert "models_by_stage" in result["registry_stats"]

    def test_registered_model_info_dataclass(self):
        """Test dataclass RegisteredModelInfo"""
        model_info = RegisteredModelInfo(
            name="TestModel",
            version="1",
            stage="Production"
        )
        
        assert model_info.name == "TestModel"
        assert model_info.version == "1"
        assert model_info.stage == "Production"
        assert model_info.status == "READY"
        assert isinstance(model_info.tags, dict)

    @pytest.mark.asyncio
    async def test_process_request_register_model(self, registry_service):
        """Test process_request para register_model"""
        with patch.object(registry_service, 'register_model', return_value={"success": True}) as mock_register:
            request_data = {"action": "register_model", "name": "TestModel"}
            
            result = await registry_service.process_request(request_data)
            
            assert result["success"] is True
            mock_register.assert_called_once_with(request_data)

    @pytest.mark.asyncio
    async def test_process_request_get_registry_stats(self, registry_service):
        """Test process_request para get_registry_stats"""
        with patch.object(registry_service, 'get_registry_stats', return_value={"success": True}) as mock_stats:
            request_data = {"action": "get_registry_stats"}
            
            result = await registry_service.process_request(request_data)
            
            assert result["success"] is True
            mock_stats.assert_called_once()


# Test de integración simple (sin MLflow real)
@pytest.mark.asyncio 
async def test_integration_model_lifecycle():
    """Test de integración para ciclo de vida de modelo"""
    with patch('mlflow.set_tracking_uri'), \
         patch('app.services.mlflow_registry_service.MlflowClient') as mock_client:
        
        service = MLflowRegistryService()
        
        # Mock de respuestas de MLflow
        mock_version = MagicMock()
        mock_version.version = "1"
        mock_version.current_stage = "None"
        
        # 1. Registrar modelo
        with patch('mlflow.register_model', return_value=mock_version):
            register_result = await service.register_model({
                "model_uri": "runs:/123/model",
                "name": "TestModel",
                "description": "Integration test model"
            })
            
            assert register_result["success"] is True
        
        # 2. Promover a staging
        mock_client.return_value.transition_model_version_stage.return_value = mock_version
        transition_result = await service.transition_model_version_stage({
            "name": "TestModel",
            "version": "1",
            "stage": "Staging"
        })
        
        assert transition_result["success"] is True
