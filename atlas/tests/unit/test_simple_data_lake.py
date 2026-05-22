#!/usr/bin/env python3
"""
Test simple para ScientificDataLakeService

Este test evita todas las dependencias complejas y se enfoca únicamente
en probar la funcionalidad básica del servicio.
"""

import os
import sys
import tempfile
import csv
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock

# Agregar el directorio app al path
sys.path.insert(0, '.')

# Mock de logging para evitar problemas de configuración
with patch('app.logging_config.logger', MagicMock()):
    with patch('app.logging_config.setup_logging', MagicMock()):
        # Mock de settings
        mock_settings = MagicMock()
        mock_settings.log_level = "INFO"
        
        with patch('app.config.settings', mock_settings):
            # Mock de base_service dependencies
            with patch('app.services.base_service.logger', MagicMock()):
                # Importar directamente el servicio
                from app.services.scientific_data_lake_service import ScientificDataLakeService


async def test_basic_functionality():
    """Test básico de funcionalidad del ScientificDataLakeService"""
    
    print("🧪 Iniciando test básico del ScientificDataLakeService...")
    
    # Usar directorio temporal para testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Configurar variables de entorno para testing
        with patch.dict('os.environ', {
            'DATALAKE_ROOT': temp_dir,
            'MAX_DATALAKE_FILE_BYTES': '10485760',  # 10MB
            'STRICT_DATALAKE_PATHS': '1',
            'ENABLE_S3': '0'
        }):
            
            # Mock del servicio de base de datos
            mock_db = MagicMock()
            mock_db.save_dataset = MagicMock()
            mock_db.get_datasets = MagicMock(return_value=[])
            
            with patch('app.services.scientific_data_lake_service.DatabaseService', return_value=mock_db):
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
                
                # Test 3: Ingesta de archivo local
                request_data = {
                    "action": "ingest",
                    "source": str(test_csv_file),
                    "namespace": "test",
                    "name": "basic_test"
                }
                
                result = await service.process_request(request_data)
                
                assert result["success"] is True
                assert "file_path" in result
                assert result["size_bytes"] > 0
                print("✅ Test de ingesta de archivo completado")
                
                # Test 4: Verificar que se copió el archivo
                ingested_path = Path(result["file_path"])
                assert ingested_path.exists()
                assert ingested_path.stat().st_size > 0
                print("✅ Test de copia de archivo completado")
                
                # Test 5: Sampling del archivo
                sample_request = {
                    "action": "sample",
                    "file_path": result["file_path"],
                    "n": 1
                }
                
                sample_result = await service.process_request(sample_request)
                
                assert sample_result["success"] is True
                assert "preview" in sample_result
                print("✅ Test de sampling completado")
                
                print("🎉 ¡Todos los tests básicos pasaron exitosamente!")
                return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_basic_functionality())
        if success:
            print("\n✨ El ScientificDataLakeService funciona correctamente!")
            sys.exit(0)
        else:
            print("\n❌ Algunos tests fallaron")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error durante la ejecución de tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)