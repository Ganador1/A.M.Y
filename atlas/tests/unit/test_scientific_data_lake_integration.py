#!/usr/bin/env python3
"""
Integration Test for ScientificDataLakeService

Este test se ejecuta de forma aislada sin depender del conftest.py
"""

import os
import sys
import tempfile
import json
import csv
from pathlib import Path
from unittest.mock import patch, MagicMock

# Agregar el directorio app al path
sys.path.insert(0, '.')

# Mock de las dependencias problemáticas antes de importar
with patch.dict('sys.modules', {
    'app.middleware': MagicMock(),
    'app.middleware.RateLimitMiddleware': MagicMock(),
    'app.middleware.LoggingMiddleware': MagicMock(),
    'app.middleware.SecurityHeadersMiddleware': MagicMock(),
    'app.services.database_service': MagicMock(),
    'app.config': MagicMock(),
    'app.database': MagicMock(),
    'app.observability': MagicMock(),
}):
    # Mock de settings
    mock_settings = MagicMock()
    mock_settings.database_url = "sqlite:///:memory:"
    mock_settings.enable_database = True
    mock_settings.debug = True
    mock_settings.enable_redis_cache = False
    
    with patch('app.config.settings', mock_settings):
        from app.services.scientific_data_lake_service import ScientificDataLakeService


def test_scientific_data_lake_integration():
    """Test de integración completo para ScientificDataLakeService"""
    
    print("🧪 Iniciando tests de integración para ScientificDataLakeService...")
    
    # Usar directorio temporal para testing
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getenv') as mock_getenv:
            # Configurar variables de entorno para testing
            mock_getenv.side_effect = lambda key, default=None: {
                "DATALAKE_ROOT": temp_dir,
                "MAX_DATALAKE_FILE_BYTES": "10485760",  # 10MB
                "STRICT_DATALAKE_PATHS": "1",
                "ENABLE_S3": "0"
            }.get(key, default)
            
            # Mock del servicio de base de datos
            with patch('app.services.scientific_data_lake_service.DatabaseService') as mock_db:
                mock_db_instance = MagicMock()
                mock_db.return_value = mock_db_instance
                
                # Configurar métodos mock de la base de datos
                mock_db_instance.save_dataset = MagicMock()
                mock_db_instance.get_datasets = MagicMock(return_value=[])
                
                # Crear instancia del servicio
                service = ScientificDataLakeService()
                
                print("✅ ScientificDataLakeService inicializado correctamente")
                
                # Test 1: Información del servicio
                info = service.get_service_info()
                assert info["name"] == "ScientificDataLakeService"
                assert info["version"] == "1.0.0"
                print("✅ Test de información del servicio completado")
                
                # Test 2: Crear archivo CSV de prueba
                test_csv_file = Path(temp_dir) / "test_data.csv"
                with open(test_csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['id', 'name', 'value'])
                    writer.writerow([1, 'test1', 100.5])
                    writer.writerow([2, 'test2', 200.3])
                    writer.writerow([3, 'test3', 300.7])
                
                # Test 3: Ingesta de archivo local
                request_data = {
                    "action": "ingest",
                    "source": str(test_csv_file),
                    "namespace": "test",
                    "name": "integration_test",
                    "dataset_type": "tabular",
                    "description": "Integration test dataset"
                }
                
                result = service.process_request(request_data)
                
                assert result["success"] is True
                assert "dataset_id" in result
                assert "file_path" in result
                assert result["size_bytes"] > 0
                assert result["data_format"] == "csv"
                assert result["backend"] == "local"
                print("✅ Test de ingesta de archivo local completado")
                
                # Test 4: Verificar que se llamó al método de base de datos
                service.db.save_dataset.assert_called_once()
                print("✅ Test de registro en base de datos completado")
                
                # Test 5: Sampling del archivo
                sample_request = {
                    "action": "sample",
                    "file_path": result["file_path"],
                    "n": 2
                }
                
                sample_result = service.process_request(sample_request)
                
                assert sample_result["success"] is True
                assert "preview" in sample_result
                preview = sample_result["preview"]
                assert preview["kind"] == "tabular"
                assert "rows" in preview
                print("✅ Test de sampling completado")
                
                # Test 6: Estadísticas del archivo
                stat_request = {
                    "action": "stat",
                    "file_path": result["file_path"]
                }
                
                stat_result = service.process_request(stat_request)
                
                assert stat_result["success"] is True
                assert "info" in stat_result
                info = stat_result["info"]
                assert "size_bytes" in info
                assert info["size_bytes"] > 0
                print("✅ Test de estadísticas completado")
                
                # Test 7: Manejo de errores - archivo inexistente
                error_request = {
                    "action": "ingest",
                    "source": "/non/existent/file.csv",
                    "namespace": "test",
                    "name": "nonexistent"
                }
                
                error_result = service.process_request(error_request)
                
                assert error_result["success"] is False
                assert "not found" in error_result["error"].lower()
                print("✅ Test de manejo de errores completado")
                
                print("🎉 ¡Todos los tests de integración pasaron exitosamente!")
                return True


if __name__ == "__main__":
    try:
        success = test_scientific_data_lake_integration()
        if success:
            print("\n✨ Todos los tests de integración del ScientificDataLakeService funcionan correctamente!")
            sys.exit(0)
        else:
            print("\n❌ Algunos tests fallaron")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error durante la ejecución de tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)