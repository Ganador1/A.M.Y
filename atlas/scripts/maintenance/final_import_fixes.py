#!/usr/bin/env python3
"""
Script final para completar la corrección de imports y alcanzar >95% éxito
"""
import os
import re
from pathlib import Path


def apply_final_import_fixes(file_path: Path) -> bool:
    """Aplicar correcciones finales de imports"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Correcciones específicas para los imports que fallan
        final_fixes = [
            # El problema principal: app.database -> app.core.database
            (r'\bimport app\.database\b', 'import app.core.database'),
            (r'\bfrom app\.database\b', 'from app.core.database'),
            (r'\bapp\.database\.', 'app.core.database.'),
            
            # Otros imports que pueden estar mal
            (r'\bimport app\.config\b', 'import app.core.config'),
            (r'\bfrom app\.config\b', 'from app.core.config'),
            (r'\bapp\.config\.', 'app.core.config.'),
            
            (r'\bimport app\.cache\b', 'import app.core.cache'),
            (r'\bfrom app\.cache\b', 'from app.core.cache'),
            (r'\bapp\.cache\.', 'app.core.cache.'),
            
            # Logging fixes adicionales por si faltaron
            (r'\bfrom app\.logging_config\b', 'from app.core.bootstrap_logging'),
            (r'\bimport app\.logging_config\b', 'import app.core.bootstrap_logging'),
            (r'\bapp\.logging_config\.', 'app.core.bootstrap_logging.'),
            
            # Observability -> monitoring
            (r'\bfrom app\.observability\.', 'from app.monitoring.'),
            (r'\bimport app\.observability\.', 'import app.monitoring.'),
            
            # Específicos que pueden faltar
            (r'\bfrom app\.metrics\b', 'from app.monitoring.metrics'),
            (r'\bfrom app\.health\b', 'from app.monitoring.health'),
            
            # Tool adapters
            (r'\bfrom app\.tool_adapter\b', 'from app.adapters.tool_adapter'),
            (r'\bfrom app\.unified_tool_adapter\b', 'from app.adapters.unified_tool_adapter'),
            
            # GPU management
            (r'\bfrom app\.gpu_manager\b', 'from app.distributed.gpu_manager'),
            (r'\bfrom app\.gpu_accelerator\b', 'from app.distributed.gpu_accelerator'),
            
            # Rate limiting
            (r'\bfrom app\.rate_limit\b', 'from app.infrastructure.rate_limit'),
            
            # Security
            (r'\bfrom app\.auth\b', 'from app.security.auth'),
            
            # Processing
            (r'\bfrom app\.async_processor\b', 'from app.processing.async_processor'),
            
            # Scientific services
            (r'\bfrom app\.multiscale_models\b', 'from app.scientific.multiscale_models'),
            (r'\bfrom app\.plasma_physics_service\b', 'from app.scientific.plasma_physics_service'),
            
            # Medical services
            (r'\bfrom app\.medical_imaging_service\b', 'from app.domains.medicine.imaging.medical_imaging_service'),
(r'\bfrom app\.strain_analysis\b', 'from app.domains.medicine.imaging.strain_analysis'),
            
            # Advanced operations
            (r'\bfrom app\.advanced_algorithms\b', 'from app.advanced_ops.advanced_algorithms'),
            
            # Compliance
            (r'\bfrom app\.ethics_gate\b', 'from app.compliance.ethics_gate'),
            (r'\bfrom app\.risk_assessment\b', 'from app.compliance.risk_assessment'),
            
            # Quality
            (r'\bfrom app\.uncertainty_quantification\b', 'from app.quality.uncertainty_quantification'),
            (r'\bfrom app\.robustness_metrics\b', 'from app.quality.robustness_metrics'),
            
            # Infrastructure
            (r'\bfrom app\.service_registry\b', 'from app.infrastructure.service_registry'),
            
            # Validation
            (r'\bfrom app\.validation\b', 'from app.validation.operational_cross_validation_matrix'),
            
            # Algorithms
            (r'\bfrom app\.intelligent_optimizer\b', 'from app.algorithms.intelligent_optimizer'),
            (r'\bfrom app\.anomaly_detection\b', 'from app.algorithms.anomaly_detection'),
        ]
        
        changes_made = False
        for pattern, replacement in final_fixes:
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
    """Ejecutar correcciones finales masivas"""
    print("🚀 Aplicando correcciones finales para alcanzar 95%+ éxito...")
    
    # Directorios a procesar
    directories = ['app', 'main.py']
    
    total_files = 0
    fixed_files = 0
    
    # Procesar main.py específicamente
    if os.path.exists('main.py'):
        total_files += 1
        if apply_final_import_fixes(Path('main.py')):
            print(f"  ✅ main.py")
            fixed_files += 1
    
    # Procesar todos los archivos Python en app/
    for root, dirs, files in os.walk('app'):
        # Evitar directorios innecesarios
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', '.pytest_cache']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                total_files += 1
                
                if apply_final_import_fixes(file_path):
                    print(f"  ✅ {file_path}")
                    fixed_files += 1
    
    print(f"\n📊 Resultados Finales:")
    print(f"   • Archivos procesados: {total_files}")
    print(f"   • Archivos corregidos: {fixed_files}")
    
    print(f"\n🧪 Ejecutando smoke test final...")
    
    # Ejecutar smoke test para verificar mejoras
    try:
        import subprocess
        result = subprocess.run(['python', 'smoke_test_reorganization.py'], 
                              capture_output=True, text=True, timeout=60)
        
        # Extraer tasa de éxito del output
        output_lines = result.stdout.split('\n')
        for line in output_lines:
            if 'Tasa de éxito:' in line:
                success_rate = line.split('Tasa de éxito: ')[1].split('%')[0]
                print(f"   🎯 Tasa de éxito: {success_rate}%")
                break
        
    except Exception as e:
        print(f"   ❌ Error ejecutando smoke test: {e}")
    
    return fixed_files


if __name__ == '__main__':
    main()
