"""
Tests para Lean4 Management Suite
=================================

Tests comprehensivos para la gestión de Lean4: instalación, validación,
diagnóstico y desinstalación.

Tests incluidos:
- Detección de sistema e instalación
- Validación de configuración
- Diagnóstico de errores
- Endpoints de gestión
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from pathlib import Path

from app.main import app
from app.services.lean4_installer import lean4_installer
from app.services.theorem_proving.lean4_integration import Lean4Service


client = TestClient(app)


class TestLean4Installer:
    """Tests para el servicio de instalación de Lean4"""
    
    @pytest.mark.asyncio
    async def test_detect_system_info(self):
        """Test detección de información del sistema"""
        system_info = await lean4_installer.detect_system_info()
        
        assert 'os' in system_info
        assert 'architecture' in system_info
        assert 'is_supported' in system_info
        assert 'install_path' in system_info
        assert 'dependencies' in system_info
    
    @pytest.mark.asyncio
    async def test_check_existing_installation_no_lean(self):
        """Test verificación cuando Lean4 no está instalado"""
        with patch('os.path.exists', return_value=False):
            result = await lean4_installer.check_existing_installation()
            
            assert result['elan_path_exists'] is False
            assert result['lean_binary_exists'] is False
            assert result['fully_installed'] is False
    
    @pytest.mark.asyncio
    async def test_check_existing_installation_with_lean(self):
        """Test verificación cuando Lean4 está instalado"""
        with patch('os.path.exists', return_value=True):
            result = await lean4_installer.check_existing_installation()
            
            assert result['elan_path_exists'] is True
            assert result['lean_binary_exists'] is True
            # Note: fully_installed requires all binaries
    
    @pytest.mark.asyncio
    async def test_install_lean4_unsupported_system(self):
        """Test instalación en sistema no soportado"""
        with patch.object(lean4_installer, '_is_system_supported', return_value=False):
            result = await lean4_installer.install_lean4()
            
            assert result['success'] is False
            assert 'no soportado' in result['error']
    
    @pytest.mark.asyncio
    async def test_install_lean4_already_installed(self):
        """Test instalación cuando ya existe"""
        mock_existing = {
            'fully_installed': True,
            'lean_version': 'Lean 4.0.0'
        }
        
        with patch.object(lean4_installer, 'check_existing_installation', 
                         return_value=mock_existing):
            result = await lean4_installer.install_lean4(force_reinstall=False)
            
            assert result['success'] is True
            assert result['action'] == 'skipped'
    
    @pytest.mark.asyncio
    async def test_uninstall_lean4_not_installed(self):
        """Test desinstalación cuando no está instalado"""
        mock_path = Mock()
        mock_path.exists.return_value = False
        
        with patch.object(lean4_installer, 'install_paths', {'darwin': mock_path}):
            result = await lean4_installer.uninstall_lean4()
            
            assert result['success'] is True
            assert result['action'] == 'none_required'


class TestLean4Service:
    """Tests para el servicio de Lean4"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.service = Lean4Service()
    
    @pytest.mark.asyncio
    async def test_validate_configuration(self):
        """Test validación de configuración"""
        result = await self.service.validate_configuration()
        
        assert 'overall_status' in result
        assert 'system_info' in result
        assert 'binary_checks' in result
        assert 'recommendations' in result
        assert isinstance(result['recommendations'], list)
    
    @pytest.mark.asyncio
    async def test_diagnose_error_syntax(self):
        """Test diagnóstico de error de sintaxis"""
        error_msg = "expected ')' got ','"
        result = await self.service.diagnose_error(error_msg)
        
        assert result['error_type'] == 'syntax_error'
        assert result['severity'] == 'low'
        assert len(result['suggestions']) > 0
        assert 'paréntesis' in result['suggestions'][0]
    
    @pytest.mark.asyncio
    async def test_diagnose_error_type_mismatch(self):
        """Test diagnóstico de error de tipos"""
        error_msg = "type mismatch: expected Nat, got String"
        result = await self.service.diagnose_error(error_msg)
        
        assert result['error_type'] == 'type_error'
        assert result['severity'] == 'low'
        assert any('tipos' in suggestion for suggestion in result['suggestions'])
    
    @pytest.mark.asyncio
    async def test_diagnose_error_unknown_identifier(self):
        """Test diagnóstico de identificador desconocido"""
        error_msg = "unknown identifier 'myFunction'"
        result = await self.service.diagnose_error(error_msg)
        
        assert result['error_type'] == 'undefined_symbol'
        assert result['severity'] == 'medium'
        assert any('imports' in suggestion for suggestion in result['suggestions'])
    
    @pytest.mark.asyncio
    async def test_system_info(self):
        """Test obtención de información del sistema"""
        result = await self.service._get_system_info()
        
        assert 'os' in result
        assert 'architecture' in result
        assert 'python_version' in result
        assert 'home_dir' in result


class TestLean4Endpoints:
    """Tests para los endpoints de Lean4"""
    
    def test_detect_endpoint(self):
        """Test endpoint de detección"""
        response = client.get("/api/lean4/detect")
        
        assert response.status_code == 200
        data = response.json()
        assert 'system_info' in data
        assert 'installation_status' in data
        assert 'is_supported_system' in data
    
    def test_validate_endpoint(self):
        """Test endpoint de validación"""
        response = client.post("/api/lean4/validate")
        
        assert response.status_code == 200
        data = response.json()
        assert 'overall_status' in data
        assert 'binary_checks' in data
        assert 'recommendations' in data
    
    def test_diagnose_endpoint(self):
        """Test endpoint de diagnóstico"""
        payload = {
            "error_message": "expected 'end' got 'lemma'",
            "context": "proving a theorem",
            "include_system_info": True
        }
        
        response = client.post("/api/lean4/diagnose", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert 'error_analysis' in data
        assert 'troubleshooting_steps' in data
        assert data['error_analysis']['error_type'] == 'syntax_error'
    
    def test_diagnose_endpoint_invalid_request(self):
        """Test endpoint de diagnóstico con request inválido"""
        payload = {}  # Missing error_message
        
        response = client.post("/api/lean4/diagnose", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_system_info_endpoint(self):
        """Test endpoint de información del sistema"""
        response = client.get("/api/lean4/system-info")
        
        assert response.status_code == 200
        data = response.json()
        assert 'system_details' in data
        assert 'dependencies' in data
        assert 'compatibility' in data
        assert 'useful_commands' in data
    
    def test_install_endpoint_simulation(self):
        """Test endpoint de instalación (simulado)"""
        # Note: Este test simula la instalación para evitar cambios reales
        payload = {
            "force_reinstall": False,
            "include_mathlib": True
        }
        
        with patch('app.services.lean4_installer.lean4_installer.install_lean4') as mock_install:
            mock_install.return_value = {
                'success': True,
                'message': 'Instalación simulada',
                'steps_completed': {}
            }
            
            response = client.post("/api/lean4/install", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
    
    def test_uninstall_endpoint_simulation(self):
        """Test endpoint de desinstalación (simulado)"""
        with patch('app.services.lean4_installer.lean4_installer.uninstall_lean4') as mock_uninstall:
            mock_uninstall.return_value = {
                'success': True,
                'message': 'Desinstalación simulada'
            }
            
            response = client.delete("/api/lean4/uninstall")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True


class TestLean4Integration:
    """Tests de integración para Lean4"""
    
    @pytest.mark.asyncio
    async def test_full_detection_validation_flow(self):
        """Test flujo completo: detección → validación"""
        # Detección
        detection = await lean4_installer.detect_system_info()
        assert 'is_supported' in detection
        
        # Validación si está soportado
        if detection.get('is_supported', False):
            service = Lean4Service()
            validation = await service.validate_configuration()
            assert 'overall_status' in validation
    
    @pytest.mark.asyncio
    async def test_error_diagnosis_flow(self):
        """Test flujo de diagnóstico de errores"""
        service = Lean4Service()
        
        # Test múltiples tipos de errores
        error_cases = [
            ("expected 'end' got 'lemma'", "syntax_error"),
            ("type mismatch", "type_error"),
            ("unknown identifier", "undefined_symbol"),
            ("could not resolve import", "import_error"),
            ("timeout", "timeout_error"),
            ("out of memory", "memory_error")
        ]
        
        for error_msg, expected_type in error_cases:
            result = await service.diagnose_error(error_msg)
            assert result['error_type'] == expected_type
            assert len(result['suggestions']) > 0


@pytest.mark.integration
class TestLean4EndToEnd:
    """Tests end-to-end para Lean4 Management"""
    
    def test_complete_management_workflow(self):
        """Test workflow completo de gestión"""
        # 1. Detectar estado actual
        response = client.get("/api/lean4/detect")
        assert response.status_code == 200
        
        # 2. Validar configuración
        response = client.post("/api/lean4/validate")
        assert response.status_code == 200
        validation = response.json()
        
        # 3. Si hay problemas, diagnosticar
        if validation.get('overall_status') != 'healthy':
            diagnose_payload = {
                "error_message": "configuration issue",
                "include_system_info": True
            }
            response = client.post("/api/lean4/diagnose", json=diagnose_payload)
            assert response.status_code == 200
        
        # 4. Obtener información del sistema
        response = client.get("/api/lean4/system-info")
        assert response.status_code == 200
    
    def test_error_handling_resilience(self):
        """Test manejo de errores y resilencia"""
        # Test diagnóstico con mensaje vacío
        response = client.post("/api/lean4/diagnose", json={"error_message": ""})
        assert response.status_code == 422
        
        # Test diagnóstico con mensaje muy largo
        long_message = "error " * 1000
        response = client.post("/api/lean4/diagnose", json={"error_message": long_message})
        assert response.status_code == 200  # Debe manejar gracefully


# Configuración de pytest
@pytest.fixture(scope="session")
def event_loop():
    """Fixture para asyncio event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
