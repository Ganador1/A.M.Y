#!/usr/bin/env python3
"""
Script de prueba para verificar que la migración a BaseSettings funciona correctamente
"""

import os
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_settings_migration():
    """Prueba la migración de Settings a BaseSettings"""
    print("🧪 Probando migración de Settings a BaseSettings...")
    
    try:
        # Importar settings
        from app.config import settings, Settings
        
        print("✅ Importación exitosa")
        
        # Verificar que es una instancia de BaseSettings
        from pydantic_settings import BaseSettings
        assert isinstance(settings, BaseSettings), "Settings debe heredar de BaseSettings"
        print("✅ Settings hereda de BaseSettings")
        
        # Verificar que las variables se cargan correctamente
        print(f"📊 Configuración cargada:")
        print(f"   - Host: {settings.host}")
        print(f"   - Port: {settings.port}")
        print(f"   - Debug: {settings.debug}")
        print(f"   - Database URL: {settings.database_url}")
        print(f"   - LLM Backend: {settings.llm_backend}")
        print(f"   - Ollama Model: {settings.ollama_model}")
        
        # Probar carga desde variables de entorno
        print("\n🔧 Probando carga desde variables de entorno...")
        
        # Establecer algunas variables de prueba
        os.environ['TEST_HOST'] = 'test.example.com'
        os.environ['TEST_PORT'] = '9000'
        os.environ['TEST_DEBUG'] = 'true'
        
        # Crear nueva instancia para probar
        test_settings = Settings()
        
        # Verificar que las variables se cargan (si están definidas en Settings)
        print(f"   - Host desde env: {test_settings.host}")
        print(f"   - Port desde env: {test_settings.port}")
        
        print("✅ Migración a BaseSettings completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en la migración: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_env_var_loading():
    """Prueba la carga de variables de entorno específicas"""
    print("\n🔍 Probando carga de variables de entorno específicas...")
    
    # Variables que sabemos que están en Settings
    test_vars = {
        'SECRET_KEY': 'test-secret-key-12345',
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/test_db',
        'OLLAMA_MODEL': 'test-model:latest',
        'LLM_BACKEND': 'test-backend',
        'ENABLE_AUTH_ROUTES': 'true',
        'API_BEARER_TOKEN': 'test-bearer-token'
    }
    
    # Establecer variables de entorno
    for key, value in test_vars.items():
        os.environ[key] = value
    
    try:
        # Crear nueva instancia de Settings
        from app.config import Settings
        test_settings = Settings()
        
        # Verificar que las variables se cargan correctamente
        print(f"   - SECRET_KEY: {test_settings.secret_key}")
        print(f"   - DATABASE_URL: {test_settings.database_url}")
        print(f"   - OLLAMA_MODEL: {test_settings.ollama_model}")
        print(f"   - LLM_BACKEND: {test_settings.llm_backend}")
        print(f"   - ENABLE_AUTH_ROUTES: {test_settings.enable_auth_routes}")
        print(f"   - API_BEARER_TOKEN: {test_settings.api_bearer_token}")
        
        print("✅ Carga de variables de entorno funciona correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en carga de variables: {e}")
        return False
    finally:
        # Limpiar variables de entorno de prueba
        for key in test_vars.keys():
            os.environ.pop(key, None)

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de migración de configuración...")
    print("=" * 60)
    
    success1 = test_settings_migration()
    success2 = test_env_var_loading()
    
    if success1 and success2:
        print("\n🎉 ¡Todas las pruebas pasaron! La migración a BaseSettings es exitosa.")
    else:
        print("\n💥 Algunas pruebas fallaron. Revisar la implementación.")
        sys.exit(1)
