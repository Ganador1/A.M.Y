#!/usr/bin/env python3
"""
Script avanzado para migrar los archivos restantes con os.getenv()
"""

import re
import os
from pathlib import Path

def migrate_remaining_files():
    """Migra los archivos restantes con accesos a os.getenv()"""
    
    # Archivos restantes para migrar (segunda ronda)
    remaining_files = [
        "app/integrations/literature_clients.py",
        "app/adapters/async_tool_adapter.py", 
        "app/adapters/tool_adapter_cache.py",
        "app/services/scientific_data_lake_service.py",
        "app/services/multi_agent_orchestrator.py",
        "app/services/model_management_service.py",
        "app/services/mlflow_auto_promotion_service.py",
        "app/services/master_orchestration_service_refactored.py",
        "app/services/multi_agent_coordinator.py",
        "app/services/consistency_checker_service_improved.py",
        "app/services/advanced_cloud_lab_service.py",
        "app/services/lean4_installer.py",
        "app/services/mlflow_registry_service.py",
        "app/services/publication_system_registration.py",
        "app/services/data_versioning.py",
        "app/services/lean4_installer_improved.py",
        "app/validation/blockchain_validation.py",
        "app/validation/validation_matrix_persistence.py",
        "app/advanced_ops/advanced_torch_operations.py",
        "app/advanced_ops/advanced_redis_operations.py",
        "app/services/theorem_proving/lean4_integration.py",
        "app/domains/engineering/services/advanced_lab_automation_service.py",
        "app/domains/medicine/services/advanced_medical_imaging_service.py",
        "app/domains/mathematics/services/mathematical_brainstorming_service.py",
        "app/domains/chemistry/materials/materials_discovery_service.py",
        "app/domains/chemistry/services/materials_discovery_service.py"
    ]
    
    # Variables adicionales que necesitamos agregar a Settings
    additional_variables = {
        # Literature clients
        'LIT_HTTP_UA': 'str = Field(default="AXIOM/1.0")',
        'MATERIALS_PROJECT_API_KEY': 'Optional[str] = Field(default=None)',
        'LIT_HTTP_MAX_RETRIES': 'int = Field(default=3)',
        'OPENALEX_MAILTO': 'Optional[str] = Field(default=None)',
        'LIT_HTTP_BACKOFF': 'float = Field(default=1.0)',
        'LIT_HTTP_TIMEOUT': 'int = Field(default=30)',
        
        # Async tools
        'ASYNC_TOOL_FAIL_FAST': 'bool = Field(default=False)',
        'ASYNC_TOOL_RETRY_ATTEMPTS': 'int = Field(default=3)',
        'ASYNC_TOOL_TIMEOUT': 'int = Field(default=30)',
        'ASYNC_TOOL_MAX_CONCURRENT': 'int = Field(default=10)',
        
        # Tool adapter cache
        'TOOL_ADAPTER_CACHE_SIZE': 'int = Field(default=1000)',
        'TOOL_ADAPTER_CACHE_TTL': 'int = Field(default=300)',
        
        # Data lake
        'ENABLE_S3': 'bool = Field(default=False)',
        'DATALAKE_ROOT': 'str = Field(default="/tmp/axiom_datalake")',
        
        # Services
        'AXIOM_SKIP_AUTOINIT': 'bool = Field(default=False)',
        'AXIOM_CONFIG_DIR': 'Optional[str] = Field(default=None)',
        'MLFLOW_TRACKING_URI': 'Optional[str] = Field(default=None)',
        'ECL_BASE_URL': 'Optional[str] = Field(default=None)',
        'ECL_API_KEY': 'Optional[str] = Field(default=None)',
        'ECL_SIMULATION': 'bool = Field(default=False)',
        
        # System
        'USER': 'Optional[str] = Field(default=None)',
        'SHELL': 'Optional[str] = Field(default=None)',
        'PATH': 'Optional[str] = Field(default=None)',
        
        # Data versioning
        'ALLOWED_DATA_ROOT': 'Optional[str] = Field(default=None)',
        'STRICT_DATA_PATHS': 'bool = Field(default=True)',
        'MAX_VERSION_FILE_BYTES': 'int = Field(default=100 * 1024 * 1024)',  # 100MB
        
        # Validation
        'VALIDATION_RETENTION_DAYS': 'int = Field(default=30)',
        'VALIDATION_SNAPSHOT_INTERVAL': 'int = Field(default=3600)',  # 1 hour
        
        # Redis
        'ALLOW_REDIS_PICKLE': 'bool = Field(default=False)',
        
        # Lean4
        'LEAN_BIN': 'Optional[str] = Field(default=None)',
        'ELAN_HOME': 'Optional[str] = Field(default=None)',
        'LEAN_TIMEOUT_MS': 'int = Field(default=30000)',
        
        # Lab automation
        'LAB_ROBOT_TYPE': 'Optional[str] = Field(default=None)',
        'LAB_DECK_LAYOUT': 'Optional[str] = Field(default=None)',
        'LAB_SIMULATION': 'bool = Field(default=False)',
        
        # API Keys
        'OPENAI_API_KEY': 'Optional[str] = Field(default=None)',
        'GOOGLE_API_KEY': 'Optional[str] = Field(default=None)',
        'ANTHROPIC_API_KEY': 'Optional[str] = Field(default=None)',
        'MP_API_KEY': 'Optional[str] = Field(default=None)',
    }
    
    return remaining_files, additional_variables

def add_additional_variables_to_settings():
    """Agrega las variables adicionales a Settings"""
    settings_file = Path("./app/config/__init__.py")
    
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Encontrar donde agregar las nuevas variables (antes del field_validator)
    insertion_point = content.find("@field_validator('cors_allow_origins'")
    
    if insertion_point == -1:
        print("❌ No se encontró el punto de inserción")
        return False
    
    # Crear las nuevas variables
    new_vars_content = """
	# Additional Environment Variables (Round 2)
	# Literature & APIs
	lit_http_ua: str = Field(default="AXIOM/1.0")
	materials_project_api_key: Optional[str] = Field(default=None)
	lit_http_max_retries: int = Field(default=3)
	openalex_mailto: Optional[str] = Field(default=None)
	lit_http_backoff: float = Field(default=1.0)
	lit_http_timeout: int = Field(default=30)
	
	# Async Tools
	async_tool_fail_fast: bool = Field(default=False)
	async_tool_retry_attempts: int = Field(default=3)
	async_tool_timeout: int = Field(default=30)
	async_tool_max_concurrent: int = Field(default=10)
	
	# Tool Adapter Cache
	tool_adapter_cache_size: int = Field(default=1000)
	tool_adapter_cache_ttl: int = Field(default=300)
	
	# Data Lake
	enable_s3: bool = Field(default=False)
	datalake_root: str = Field(default="/tmp/axiom_datalake")
	
	# Services Configuration
	axiom_skip_autoinit: bool = Field(default=False)
	axiom_config_dir: Optional[str] = Field(default=None)
	mlflow_tracking_uri: Optional[str] = Field(default=None)
	ecl_base_url: Optional[str] = Field(default=None)
	ecl_api_key: Optional[str] = Field(default=None)
	ecl_simulation: bool = Field(default=False)
	
	# System Environment
	user: Optional[str] = Field(default=None)
	shell: Optional[str] = Field(default=None)
	path: Optional[str] = Field(default=None)
	
	# Data Versioning
	allowed_data_root: Optional[str] = Field(default=None)
	strict_data_paths: bool = Field(default=True)
	max_version_file_bytes: int = Field(default=100 * 1024 * 1024)  # 100MB
	
	# Validation
	validation_retention_days: int = Field(default=30)
	validation_snapshot_interval: int = Field(default=3600)  # 1 hour
	
	# Redis
	allow_redis_pickle: bool = Field(default=False)
	
	# Lean4 Integration
	lean_bin: Optional[str] = Field(default=None)
	elan_home: Optional[str] = Field(default=None)
	lean_timeout_ms: int = Field(default=30000)
	
	# Lab Automation
	lab_robot_type: Optional[str] = Field(default=None)
	lab_deck_layout: Optional[str] = Field(default=None)
	lab_simulation: bool = Field(default=False)
	
	# External API Keys
	openai_api_key: Optional[str] = Field(default=None)
	google_api_key: Optional[str] = Field(default=None)
	anthropic_api_key: Optional[str] = Field(default=None)
	mp_api_key: Optional[str] = Field(default=None)

"""
    
    # Insertar las nuevas variables
    new_content = content[:insertion_point] + new_vars_content + content[insertion_point:]
    
    with open(settings_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Variables adicionales agregadas a Settings")
    return True

def migrate_file_advanced(file_path):
    """Migra un archivo con lógica más avanzada"""
    full_path = Path(".") / file_path
    
    if not full_path.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return False
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Patrones más específicos para migración
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
    
    # Aplicar migraciones
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Agregar import de settings si no existe y se usa
    if 'settings.' in content and 'from app.config import settings' not in content:
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
    print("🚀 Iniciando migración avanzada de os.getenv()...")
    print("=" * 60)
    
    # Paso 1: Agregar variables adicionales a Settings
    print("📝 Paso 1: Agregando variables adicionales a Settings...")
    if add_additional_variables_to_settings():
        print("✅ Variables adicionales agregadas exitosamente")
    else:
        print("❌ Error agregando variables adicionales")
        exit(1)
    
    # Paso 2: Obtener archivos restantes
    remaining_files, _ = migrate_remaining_files()
    
    # Paso 3: Migrar archivos restantes
    print(f"\n📁 Paso 2: Migrando {len(remaining_files)} archivos restantes...")
    
    migrated_count = 0
    for file_path in remaining_files:
        if migrate_file_advanced(file_path):
            migrated_count += 1
    
    print(f"\n📊 Resumen:")
    print(f"   - Archivos migrados: {migrated_count}/{len(remaining_files)}")
    print(f"   - Variables adicionales agregadas: ~40")
    
    print("\n🎉 Migración avanzada completada!")
