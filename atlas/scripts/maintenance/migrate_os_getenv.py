#!/usr/bin/env python3
"""
Script automatizado para migrar accesos directos a os.getenv() a settings centralizado
"""

import re
import os
from pathlib import Path
from collections import defaultdict

def create_migration_script():
    """Crea un script para migrar archivos específicos"""
    
    # Archivos prioritarios para migrar (los más importantes)
    priority_files = [
        "app/routers/auth.py",
        "app/core/telemetry.py", 
        "app/core/bootstrap_logging.py",
        "app/distributed/distributed_scaling_manager.py",
        "app/distributed/distributed_manager.py",
        "app/config/database_config.py",
        "app/security/hmac_integrity.py",
        "app/observability/otel_init.py"
    ]
    
    # Variables que necesitamos agregar a Settings
    new_variables = {
        # Security
        'SYSTEM_ADMIN_PASSWORD': 'Optional[str] = Field(default=None)',
        'RESEARCHER_PASSWORD': 'Optional[str] = Field(default=None)', 
        'LAB_OPERATOR_PASSWORD': 'Optional[str] = Field(default=None)',
        'INTEGRITY_HMAC_KEY': 'Optional[str] = Field(default=None)',
        
        # Telemetry
        'JAEGER_PORT': 'Optional[str] = Field(default=None)',
        'CONSOLE_EXPORTER': 'bool = Field(default=False)',
        'OTLP_ENABLED': 'bool = Field(default=False)',
        'SENTRY_PROFILES_SAMPLE_RATE': 'float = Field(default=0.0)',
        'SERVICE_NAME': 'str = Field(default="axiom")',
        'SENTRY_TRACES_SAMPLE_RATE': 'float = Field(default=0.0)',
        'SERVICE_VERSION': 'str = Field(default="1.0.0")',
        'JAEGER_ENABLED': 'bool = Field(default=False)',
        'SENTRY_ENVIRONMENT': 'str = Field(default="development")',
        'JAEGER_HOST': 'str = Field(default="localhost")',
        'HOSTNAME': 'str = Field(default="localhost")',
        'OTLP_ENDPOINT': 'Optional[str] = Field(default=None)',
        
        # Logging
        'LOG_LEVEL': 'str = Field(default="INFO")',
        
        # Distributed
        'KUBERNETES_NAMESPACE': 'Optional[str] = Field(default=None)',
        'KUBERNETES_SERVICE_HOST': 'Optional[str] = Field(default=None)',
        'K8S_VERIFY_TLS': 'bool = Field(default=True)',
        'PYTORCH_MPS_HIGH_WATERMARK_RATIO': 'float = Field(default=0.0)',
        'MASTER_ADDR': 'str = Field(default="localhost")',
        'RANK': 'int = Field(default=0)',
        'MASTER_PORT': 'int = Field(default=12355)',
        'WORLD_SIZE': 'int = Field(default=1)',
        
        # Database
        'DB_USER': 'Optional[str] = Field(default=None)',
        'DB_NAME': 'Optional[str] = Field(default=None)',
        'DB_PASSWORD': 'Optional[str] = Field(default=None)',
        'DB_PORT': 'Optional[str] = Field(default=None)',
        'DB_ECHO': 'bool = Field(default=False)',
        'DB_HOST': 'Optional[str] = Field(default=None)',
        
        # Observability
        'OTEL_ENABLED': 'bool = Field(default=False)',
        'OTEL_SERVICE_NAME': 'str = Field(default="axiom")',
        'OTEL_EXPORTER_OTLP_ENDPOINT': 'Optional[str] = Field(default=None)',
        
        # Config
        'ATLAS_ENV': 'str = Field(default="development")'
    }
    
    return priority_files, new_variables

def add_variables_to_settings():
    """Agrega las nuevas variables a Settings"""
    settings_file = Path("./app/config/__init__.py")
    
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Encontrar donde agregar las nuevas variables (antes del último field_validator)
    insertion_point = content.find("@field_validator('cors_allow_origins'")
    
    if insertion_point == -1:
        print("❌ No se encontró el punto de inserción")
        return False
    
    # Crear las nuevas variables
    new_vars_content = """
	# Additional Environment Variables (migrated from os.getenv)
	# Security
	system_admin_password: Optional[str] = Field(default=None)
	researcher_password: Optional[str] = Field(default=None)
	lab_operator_password: Optional[str] = Field(default=None)
	integrity_hmac_key: Optional[str] = Field(default=None)
	
	# Telemetry & Observability
	jaeger_port: Optional[str] = Field(default=None)
	console_exporter: bool = Field(default=False)
	otlp_enabled: bool = Field(default=False)
	sentry_profiles_sample_rate: float = Field(default=0.0)
	service_name: str = Field(default="axiom")
	sentry_traces_sample_rate: float = Field(default=0.0)
	service_version: str = Field(default="1.0.0")
	jaeger_enabled: bool = Field(default=False)
	sentry_environment: str = Field(default="development")
	jaeger_host: str = Field(default="localhost")
	hostname: str = Field(default="localhost")
	otlp_endpoint: Optional[str] = Field(default=None)
	otel_enabled: bool = Field(default=False)
	otel_service_name: str = Field(default="axiom")
	otel_exporter_otlp_endpoint: Optional[str] = Field(default=None)
	
	# Logging
	log_level: str = Field(default="INFO")
	
	# Distributed Computing
	kubernetes_namespace: Optional[str] = Field(default=None)
	kubernetes_service_host: Optional[str] = Field(default=None)
	k8s_verify_tls: bool = Field(default=True)
	pytorch_mps_high_watermark_ratio: float = Field(default=0.0)
	master_addr: str = Field(default="localhost")
	rank: int = Field(default=0)
	master_port: int = Field(default=12355)
	world_size: int = Field(default=1)
	
	# Database Additional
	db_user: Optional[str] = Field(default=None)
	db_name: Optional[str] = Field(default=None)
	db_password: Optional[str] = Field(default=None)
	db_port: Optional[str] = Field(default=None)
	db_echo: bool = Field(default=False)
	db_host: Optional[str] = Field(default=None)
	
	# Environment
	atlas_env: str = Field(default="development")

"""
    
    # Insertar las nuevas variables
    new_content = content[:insertion_point] + new_vars_content + content[insertion_point:]
    
    with open(settings_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Variables agregadas a Settings")
    return True

def migrate_file(file_path):
    """Migra un archivo específico de os.getenv() a settings"""
    full_path = Path(".") / file_path
    
    if not full_path.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return False
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    # Patrones de migración
    patterns = [
        # os.getenv('VAR', default) -> settings.var
        (r'os\.getenv\(["\']([^"\']+)["\']', r'settings.\1'),
        # os.getenv("VAR", default) -> settings.var  
        (r'os\.getenv\([""]([^""]+)[""]', r'settings.\1'),
        # os.environ.get('VAR') -> settings.var
        (r'os\.environ\.get\(["\']([^"\']+)["\']', r'settings.\1'),
        # os.environ['VAR'] -> settings.var
        (r'os\.environ\[["\']([^"\']+)["\']\]', r'settings.\1'),
    ]
    
    original_content = content
    
    # Aplicar migraciones
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Agregar import de settings si no existe
    if 'from app.config import settings' not in content and 'settings.' in content:
        # Encontrar la primera línea de import
        lines = content.split('\n')
        import_line = -1
        
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_line = i
        
        if import_line != -1:
            lines.insert(import_line + 1, 'from app.config import settings')
            content = '\n'.join(lines)
    
    # Solo escribir si hubo cambios
    if content != original_content:
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✅ Migrado: {file_path}")
        return True
    else:
        print(f"ℹ️  Sin cambios: {file_path}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando migración automatizada de os.getenv()...")
    print("=" * 60)
    
    # Paso 1: Agregar variables a Settings
    print("📝 Paso 1: Agregando variables a Settings...")
    if add_variables_to_settings():
        print("✅ Variables agregadas exitosamente")
    else:
        print("❌ Error agregando variables")
        exit(1)
    
    # Paso 2: Obtener archivos prioritarios
    priority_files, _ = create_migration_script()
    
    # Paso 3: Migrar archivos prioritarios
    print(f"\n📁 Paso 2: Migrando {len(priority_files)} archivos prioritarios...")
    
    migrated_count = 0
    for file_path in priority_files:
        if migrate_file(file_path):
            migrated_count += 1
    
    print(f"\n📊 Resumen:")
    print(f"   - Archivos migrados: {migrated_count}/{len(priority_files)}")
    print(f"   - Variables agregadas a Settings: ~50")
    
    print("\n🎉 Migración automatizada completada!")
