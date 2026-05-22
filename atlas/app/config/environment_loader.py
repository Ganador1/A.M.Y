#!/usr/bin/env python3
"""
Environment-specific configuration loader for AXIOM
Carga configuración dinámica basada en el ambiente (dev/test/stage/prod)
"""

import os
from pathlib import Path
from typing import Optional

def get_environment_config_path() -> Optional[Path]:
    """
    Determina el archivo de configuración basado en la variable de entorno ENV
    """
    # Obtener el ambiente desde la variable de entorno
    env = os.getenv("ENV", "development")
    
    # Mapear ambientes a archivos
    env_files = {
        "development": "env.development",
        "dev": "env.development", 
        "testing": "env.testing",
        "test": "env.testing",
        "staging": "env.staging",
        "stage": "env.staging",
        "production": "env.production",
        "prod": "env.production"
    }
    
    env_file = env_files.get(env.lower(), "env.development")
    
    # Buscar el archivo en config/environments/
    config_dir = Path(__file__).parent.parent / "config" / "environments"
    env_path = config_dir / env_file
    
    if env_path.exists():
        print(f"🔧 Cargando configuración para ambiente: {env} desde {env_path}")
        return env_path
    else:
        print(f"⚠️  Archivo de configuración no encontrado: {env_path}")
        print(f"📁 Usando configuración por defecto para ambiente: {env}")
        return None

def load_environment_variables():
    """
    Carga variables de entorno desde el archivo de configuración específico del ambiente
    """
    env_path = get_environment_config_path()
    
    if env_path is None:
        return
    
    # Leer el archivo de configuración
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Procesar cada línea
    for line in lines:
        line = line.strip()
        
        # Saltar comentarios y líneas vacías
        if not line or line.startswith('#'):
            continue
            
        # Procesar variables KEY=VALUE
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Solo establecer si no está ya definida en el entorno
            if key not in os.environ:
                os.environ[key] = value
                print(f"   ✓ {key} = {value}")

def setup_environment():
    """
    Configura el ambiente completo para AXIOM
    """
    print("🚀 Configurando ambiente AXIOM...")
    print("=" * 50)
    
    # Cargar variables de entorno específicas del ambiente
    load_environment_variables()
    
    # Mostrar información del ambiente
    env = os.getenv("ENV", "development")
    atlas_env = os.getenv("ATLAS_ENV", "development")
    service_name = os.getenv("SERVICE_NAME", "axiom")
    service_version = os.getenv("SERVICE_VERSION", "1.0.0")
    
    print(f"\n📊 Información del ambiente:")
    print(f"   - ENV: {env}")
    print(f"   - ATLAS_ENV: {atlas_env}")
    print(f"   - SERVICE_NAME: {service_name}")
    print(f"   - SERVICE_VERSION: {service_version}")
    
    # Mostrar configuración crítica
    debug = os.getenv("DEBUG", "false")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    enable_database = os.getenv("ENABLE_DATABASE", "true")
    enable_otel = os.getenv("ENABLE_OTEL", "false")
    
    print(f"\n⚙️  Configuración crítica:")
    print(f"   - DEBUG: {debug}")
    print(f"   - LOG_LEVEL: {log_level}")
    print(f"   - ENABLE_DATABASE: {enable_database}")
    print(f"   - ENABLE_OTEL: {enable_otel}")
    
    print(f"\n✅ Ambiente configurado exitosamente!")

if __name__ == "__main__":
    setup_environment()
