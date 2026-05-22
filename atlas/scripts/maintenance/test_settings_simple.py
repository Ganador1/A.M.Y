#!/usr/bin/env python3
"""
Test simple para verificar la migración de Settings a BaseSettings
"""

import os
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_settings_direct():
    """Prueba directa de Settings sin importar otros módulos"""
    print("🧪 Probando migración de Settings a BaseSettings...")
    
    try:
        # Importar solo el módulo de configuración
        sys.path.insert(0, str(project_root / "app"))
        from config import Settings, settings
        
        print("✅ Importación exitosa de Settings")
        
        # Verificar que es una instancia de BaseSettings
        from pydantic_settings import BaseSettings
        assert isinstance(settings, BaseSettings), "Settings debe heredar de BaseSettings"
        print("✅ Settings hereda de BaseSettings")
        
        # Verificar configuración básica
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
        os.environ['SECRET_KEY'] = 'test-secret-key-12345'
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test_db'
        os.environ['OLLAMA_MODEL'] = 'test-model:latest'
        
        # Crear nueva instancia para probar
        test_settings = Settings()
        
        print(f"   - SECRET_KEY: {test_settings.secret_key}")
        print(f"   - DATABASE_URL: {test_settings.database_url}")
        print(f"   - OLLAMA_MODEL: {test_settings.ollama_model}")
        
        print("✅ Migración a BaseSettings completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en la migración: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de migración de configuración...")
    print("=" * 60)
    
    success = test_settings_direct()
    
    if success:
        print("\n🎉 ¡La migración a BaseSettings es exitosa!")
    else:
        print("\n💥 La migración falló. Revisar la implementación.")
        sys.exit(1)
