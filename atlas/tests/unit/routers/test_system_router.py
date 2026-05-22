"""
Tests para System Router - Router de monitoreo y gestión del sistema
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime
import psutil

from app.routers.system import router, LineageNode, SystemLineage, SLOMetric, SystemSLO, SystemHealth


class TestSystemRouter:
    """Tests para System Router"""

    def setup_method(self):
        """Setup para cada test"""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)

    @patch('app.routers.system.require_scopes')
    @patch('app.routers.system.scrape')
    def test_get_lineage_success(self, mock_scrape, mock_require_scopes):
        """Test: Obtención exitosa del linaje del sistema"""
        # Mock de autenticación
        mock_require_scopes.return_value = Mock()
        
        # Mock de datos de linaje
        mock_lineage_data = {
            "nodes": [
                {
                    "id": "node_1",
                    "type": "service",
                    "name": "API Gateway",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "metadata": {"version": "1.0"},
                    "parent_ids": [],
                    "children_ids": ["node_2"]
                }
            ],
            "total_nodes": 1,
            "lineage_depth": 1,
            "generated_at": "2024-01-01T00:00:00Z"
        }
        
        with patch('app.routers.system._get_system_lineage', return_value=mock_lineage_data):
            response = self.client.get("/api/system/lineage")
            
            assert response.status_code == 200
            data = response.json()
            assert "nodes" in data
            assert "total_nodes" in data
            assert "lineage_depth" in data
            assert "generated_at" in data

    @patch('app.routers.system.require_scopes')
    def test_get_lineage_unauthorized(self, mock_require_scopes):
        """Test: Acceso no autorizado al linaje"""
        mock_require_scopes.side_effect = Exception("Unauthorized")
        
        response = self.client.get("/api/system/lineage")
        assert response.status_code == 500

    @patch('app.routers.system.require_scopes')
    @patch('app.routers.system.scrape')
    def test_get_slo_metrics_success(self, mock_scrape, mock_require_scopes):
        """Test: Obtención exitosa de métricas SLO"""
        # Mock de autenticación
        mock_require_scopes.return_value = Mock()
        
        # Mock de métricas SLO
        mock_slo_data = {
            "overall_health": "healthy",
            "slo_metrics": [
                {
                    "name": "response_time",
                    "current_value": 150.0,
                    "target_value": 200.0,
                    "threshold_warning": 180.0,
                    "threshold_critical": 250.0,
                    "status": "healthy",
                    "last_updated": "2024-01-01T00:00:00Z"
                }
            ],
            "uptime_seconds": 86400.0,
            "total_requests": 1000,
            "error_rate_5m": 0.01,
            "avg_response_time_ms": 150.0,
            "active_workflows": 5,
            "generated_at": "2024-01-01T00:00:00Z"
        }
        
        with patch('app.routers.system._get_slo_metrics', return_value=mock_slo_data):
            response = self.client.get("/api/system/slo")
            
            assert response.status_code == 200
            data = response.json()
            assert "overall_health" in data
            assert "slo_metrics" in data
            assert "uptime_seconds" in data
            assert "total_requests" in data
            assert "error_rate_5m" in data
            assert "avg_response_time_ms" in data
            assert "active_workflows" in data
            assert "generated_at" in data

    @patch('app.routers.system.require_scopes')
    def test_get_slo_metrics_unauthorized(self, mock_require_scopes):
        """Test: Acceso no autorizado a métricas SLO"""
        mock_require_scopes.side_effect = Exception("Unauthorized")
        
        response = self.client.get("/api/system/slo")
        assert response.status_code == 500

    @patch('app.routers.system.require_scopes')
    @patch('app.routers.system.psutil')
    def test_get_health_success(self, mock_psutil, mock_require_scopes):
        """Test: Obtención exitosa del estado de salud del sistema"""
        # Mock de autenticación
        mock_require_scopes.return_value = Mock()
        
        # Mock de psutil
        mock_cpu = Mock()
        mock_cpu.percent = 25.0
        mock_cpu.count = 8
        
        mock_memory = Mock()
        mock_memory.percent = 60.0
        mock_memory.total = 8589934592  # 8GB
        mock_memory.available = 3435973836  # 4GB
        
        mock_disk = Mock()
        mock_disk.percent = 45.0
        mock_disk.total = 107374182400  # 100GB
        mock_disk.free = 59055800320  # 55GB
        
        mock_psutil.cpu_percent.return_value = 25.0
        mock_psutil.cpu_count.return_value = 8
        mock_psutil.virtual_memory.return_value = mock_memory
        mock_psutil.disk_usage.return_value = mock_disk
        mock_psutil.boot_time.return_value = 1640995200  # 2022-01-01
        
        response = self.client.get("/api/system/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "overall_health" in data
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
        assert "uptime_seconds" in data
        assert "timestamp" in data

    @patch('app.routers.system.require_scopes')
    def test_get_health_unauthorized(self, mock_require_scopes):
        """Test: Acceso no autorizado al estado de salud"""
        mock_require_scopes.side_effect = Exception("Unauthorized")
        
        response = self.client.get("/api/system/health")
        assert response.status_code == 500

    @patch('app.routers.system.require_system_admin')
    def test_track_lineage_success(self, mock_require_admin):
        """Test: Registro exitoso de nodo en linaje"""
        # Mock de autenticación
        mock_require_admin.return_value = Mock()
        
        # Mock de datos de entrada
        lineage_data = {
            "id": "new_node",
            "type": "service",
            "name": "New Service",
            "metadata": {"version": "1.0"},
            "parent_ids": ["parent_node"]
        }
        
        with patch('app.routers.system._add_lineage_node', return_value=True):
            response = self.client.post("/api/system/lineage/track", json=lineage_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert "message" in data

    @patch('app.routers.system.require_system_admin')
    def test_track_lineage_invalid_data(self, mock_require_admin):
        """Test: Registro de nodo con datos inválidos"""
        # Mock de autenticación
        mock_require_admin.return_value = Mock()
        
        # Datos inválidos (falta id)
        invalid_data = {
            "type": "service",
            "name": "New Service"
        }
        
        response = self.client.post("/api/system/lineage/track", json=invalid_data)
        assert response.status_code == 422  # Validation error

    @patch('app.routers.system.require_system_admin')
    def test_delete_lineage_node_success(self, mock_require_admin):
        """Test: Eliminación exitosa de nodo del linaje"""
        # Mock de autenticación
        mock_require_admin.return_value = Mock()
        
        with patch('app.routers.system._remove_lineage_node', return_value=True):
            response = self.client.delete("/api/system/lineage/test_node")
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert "message" in data

    @patch('app.routers.system.require_system_admin')
    def test_delete_lineage_node_not_found(self, mock_require_admin):
        """Test: Eliminación de nodo inexistente"""
        # Mock de autenticación
        mock_require_admin.return_value = Mock()
        
        with patch('app.routers.system._remove_lineage_node', return_value=False):
            response = self.client.delete("/api/system/lineage/nonexistent_node")
            
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data

    def test_lineage_node_model(self):
        """Test: Modelo LineageNode"""
        node = LineageNode(
            id="test_node",
            type="service",
            name="Test Service",
            timestamp="2024-01-01T00:00:00Z",
            metadata={"version": "1.0"},
            parent_ids=["parent_1"],
            children_ids=["child_1"]
        )
        
        assert node.id == "test_node"
        assert node.type == "service"
        assert node.name == "Test Service"
        assert node.timestamp == "2024-01-01T00:00:00Z"
        assert node.metadata == {"version": "1.0"}
        assert node.parent_ids == ["parent_1"]
        assert node.children_ids == ["child_1"]

    def test_system_lineage_model(self):
        """Test: Modelo SystemLineage"""
        lineage = SystemLineage(
            nodes=[],
            total_nodes=0,
            lineage_depth=0,
            generated_at="2024-01-01T00:00:00Z"
        )
        
        assert lineage.nodes == []
        assert lineage.total_nodes == 0
        assert lineage.lineage_depth == 0
        assert lineage.generated_at == "2024-01-01T00:00:00Z"

    def test_slo_metric_model(self):
        """Test: Modelo SLOMetric"""
        metric = SLOMetric(
            name="response_time",
            current_value=150.0,
            target_value=200.0,
            threshold_warning=180.0,
            threshold_critical=250.0,
            status="healthy",
            last_updated="2024-01-01T00:00:00Z"
        )
        
        assert metric.name == "response_time"
        assert metric.current_value == 150.0
        assert metric.target_value == 200.0
        assert metric.threshold_warning == 180.0
        assert metric.threshold_critical == 250.0
        assert metric.status == "healthy"
        assert metric.last_updated == "2024-01-01T00:00:00Z"

    def test_system_slo_model(self):
        """Test: Modelo SystemSLO"""
        slo = SystemSLO(
            overall_health="healthy",
            slo_metrics=[],
            uptime_seconds=86400.0,
            total_requests=1000,
            error_rate_5m=0.01,
            avg_response_time_ms=150.0,
            active_workflows=5,
            generated_at="2024-01-01T00:00:00Z"
        )
        
        assert slo.overall_health == "healthy"
        assert slo.slo_metrics == []
        assert slo.uptime_seconds == 86400.0
        assert slo.total_requests == 1000
        assert slo.error_rate_5m == 0.01
        assert slo.avg_response_time_ms == 150.0
        assert slo.active_workflows == 5
        assert slo.generated_at == "2024-01-01T00:00:00Z"

    def test_system_health_model(self):
        """Test: Modelo SystemHealth"""
        health = SystemHealth(
            overall_health="healthy",
            cpu={"usage_percent": 25.0, "core_count": 8},
            memory={"usage_percent": 60.0, "total_gb": 8.0, "available_gb": 4.0},
            disk={"usage_percent": 45.0, "total_gb": 100.0, "free_gb": 55.0},
            uptime_seconds=86400.0,
            timestamp="2024-01-01T00:00:00Z"
        )
        
        assert health.overall_health == "healthy"
        assert health.cpu["usage_percent"] == 25.0
        assert health.memory["usage_percent"] == 60.0
        assert health.disk["usage_percent"] == 45.0
        assert health.uptime_seconds == 86400.0
        assert health.timestamp == "2024-01-01T00:00:00Z"

    @patch('app.routers.system.require_scopes')
    def test_get_lineage_with_filters(self, mock_require_scopes):
        """Test: Obtención de linaje con filtros"""
        # Mock de autenticación
        mock_require_scopes.return_value = Mock()
        
        # Mock de datos filtrados
        mock_filtered_data = {
            "nodes": [],
            "total_nodes": 0,
            "lineage_depth": 0,
            "generated_at": "2024-01-01T00:00:00Z"
        }
        
        with patch('app.routers.system._get_system_lineage', return_value=mock_filtered_data):
            response = self.client.get("/api/system/lineage?node_type=service&max_depth=2")
            
            assert response.status_code == 200
            data = response.json()
            assert "nodes" in data
            assert "total_nodes" in data

    @patch('app.routers.system.require_scopes')
    def test_get_slo_with_time_range(self, mock_require_scopes):
        """Test: Obtención de SLO con rango de tiempo"""
        # Mock de autenticación
        mock_require_scopes.return_value = Mock()
        
        # Mock de datos con rango de tiempo
        mock_slo_data = {
            "overall_health": "healthy",
            "slo_metrics": [],
            "uptime_seconds": 86400.0,
            "total_requests": 1000,
            "error_rate_5m": 0.01,
            "avg_response_time_ms": 150.0,
            "active_workflows": 5,
            "generated_at": "2024-01-01T00:00:00Z"
        }
        
        with patch('app.routers.system._get_slo_metrics', return_value=mock_slo_data):
            response = self.client.get("/api/system/slo?time_range=1h")
            
            assert response.status_code == 200
            data = response.json()
            assert "overall_health" in data
            assert "slo_metrics" in data

    def test_error_handling_in_health_check(self):
        """Test: Manejo de errores en health check"""
        with patch('app.routers.system.require_scopes') as mock_require_scopes:
            mock_require_scopes.side_effect = Exception("System error")
            
            response = self.client.get("/api/system/health")
            assert response.status_code == 500

    def test_error_handling_in_slo_metrics(self):
        """Test: Manejo de errores en métricas SLO"""
        with patch('app.routers.system.require_scopes') as mock_require_scopes:
            mock_require_scopes.side_effect = Exception("SLO error")
            
            response = self.client.get("/api/system/slo")
            assert response.status_code == 500

    def test_error_handling_in_lineage(self):
        """Test: Manejo de errores en linaje"""
        with patch('app.routers.system.require_scopes') as mock_require_scopes:
            mock_require_scopes.side_effect = Exception("Lineage error")
            
            response = self.client.get("/api/system/lineage")
            assert response.status_code == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
