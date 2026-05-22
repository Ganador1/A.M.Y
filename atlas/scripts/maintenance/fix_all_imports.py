#!/usr/bin/env python3
"""
Script para corregir TODOS los imports incorrectos después de reorganización
"""
import os
import re
from pathlib import Path


def fix_all_imports_in_file(file_path: Path) -> bool:
    """Corregir todos los imports incorrectos en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones de imports incorrectos y sus correcciones
        import_fixes = [
            # Imports de database
            (r'from app\.database import', 'from app.core.database import'),
            (r'import app\.database', 'import app.core.database'),
            
            # Imports que pueden haber quedado mal después de mover
            (r'from app\.logging_config import', 'from app.core.bootstrap_logging import'),
            (r'import app\.logging_config', 'import app.core.bootstrap_logging'),
            
            # Imports de config
            (r'from app\.config import', 'from app.core.config import'),
            (r'import app\.config', 'import app.core.config'),
            
            # Imports de cache
            (r'from app\.cache import', 'from app.core.cache import'),
            (r'import app\.cache', 'import app.core.cache'),
            
            # Modelos de database
            (r'from app\.models import', 'from app.models.database_models import'),
            (r'from app\.database_models import', 'from app.models.database_models import'),
            
            # Observability
            (r'from app\.metrics import', 'from app.monitoring.metrics import'),
            (r'from app\.health import', 'from app.monitoring.health import'),
            (r'from app\.observability\.', 'from app.monitoring.'),
            
            # Middleware  
            (r'from app\.middleware\.main import', 'from app.middleware.main import'),
            
            # Servicios que fueron reorganizados
            (r'from app\.auth import', 'from app.security.auth import'),
            (r'from app\.security_service import', 'from app.security.security import'),
            
            # Rate limiting
            (r'from app\.rate_limit import', 'from app.infrastructure.rate_limit import'),
            
            # Tool adapters
            (r'from app\.adapters\.tool_adapter import', 'from app.adapters.tool_adapter import'),
            (r'from app\.adapters\.unified_tool_adapter import', 'from app.adapters.unified_tool_adapter import'),
            
            # Validation
            (r'from app\.validation import', 'from app.validation.operational_cross_validation_matrix import'),
            
            # Processing
            (r'from app\.async_processor import', 'from app.processing.async_processor import'),
            
            # GPU management
            (r'from app\.gpu_manager import', 'from app.distributed.gpu_manager import'),
            (r'from app\.gpu_accelerator import', 'from app.distributed.gpu_accelerator import'),
            
            # Scalability
            (r'from app\.scalability import', 'from app.distributed.scalability import'),
            
            # Medical services que fueron reorganizados  
            (r'from app\.medical_imaging_service import', 'from app.domains.medicine.imaging.medical_imaging_service import'),
        (r'from app\.strain_analysis import', 'from app.domains.medicine.imaging.strain_analysis import'),
            
            # Scientific services
            (r'from app\.multiscale_models import', 'from app.scientific.multiscale_models import'),
            (r'from app\.plasma_physics_service import', 'from app.scientific.plasma_physics_service import'),
            
            # Advanced operations  
            (r'from app\.advanced_algorithms import', 'from app.advanced_ops.advanced_algorithms import'),
            (r'from app\.advanced_gpu_optimizer import', 'from app.advanced_ops.advanced_gpu_optimizer import'),
            
            # Compliance
            (r'from app\.ethics_gate import', 'from app.compliance.ethics_gate import'),
            (r'from app\.risk_assessment import', 'from app.compliance.risk_assessment import'),
            
            # Quality
            (r'from app\.robustness_metrics import', 'from app.quality.robustness_metrics import'),
            (r'from app\.uncertainty_quantification import', 'from app.quality.uncertainty_quantification import'),
            
            # Infrastructure
            (r'from app\.service_registry import', 'from app.infrastructure.service_registry import'),
        ]
        
        changes_made = False
        for pattern, replacement in import_fixes:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes_made = True
        
        # Correcciones adicionales para referencias a módulos
        module_fixes = [
            (r'app\.database\.', 'app.core.database.'),
            (r'app\.logging_config\.', 'app.core.bootstrap_logging.'),  
            (r'app\.config\.', 'app.core.config.'),
            (r'app\.cache\.', 'app.core.cache.'),
        ]
        
        for pattern, replacement in module_fixes:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes_made = True
        
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False
    
    return False


def main():
    """Ejecutar corrección masiva de imports"""
    print("🔧 Corrigiendo TODOS los imports incorrectos post-reorganización...")
    
    # Directorios a procesar
    directories = ['app', 'main.py']
    
    total_files = 0
    fixed_files = 0
    
    # Procesar main.py específicamente
    if os.path.exists('main.py'):
        total_files += 1
        if fix_all_imports_in_file(Path('main.py')):
            print(f"  ✅ main.py")
            fixed_files += 1
    
    # Procesar directorios
    for directory in directories:
        if directory == 'main.py':
            continue
            
        for root, dirs, files in os.walk(directory):
            # Evitar ciertos directorios
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', '.pytest_cache']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    total_files += 1
                    
                    if fix_all_imports_in_file(file_path):
                        print(f"  ✅ {file_path}")
                        fixed_files += 1
    
    print(f"\n📊 Resultados:")
    print(f"   • Archivos procesados: {total_files}")
    print(f"   • Archivos corregidos: {fixed_files}")
    
    return fixed_files


if __name__ == '__main__':
    main()
