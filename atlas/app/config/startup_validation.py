"""
Integración de validación YAML en el startup de AXIOM
"""

from pathlib import Path
from .yaml_validator import YAMLConfigValidator

def validate_configuration_on_startup():
    """
    Valida todas las configuraciones YAML al inicio de la aplicación
    """
    print("🔧 Validando configuraciones YAML al inicio...")
    
    config_dir = Path("./config")
    validator = YAMLConfigValidator(config_dir)
    
    summary = validator.get_validation_summary()
    
    if summary['invalid_files'] > 0:
        print("❌ Errores de configuración encontrados:")
        for filename, (is_valid, error_msg, _) in summary['results'].items():
            if not is_valid:
                print(f"   - {filename}: {error_msg}")
        
        # En producción, podríamos lanzar una excepción
        # raise ConfigurationError(f"Configuración inválida: {summary['invalid_files']} archivos con errores")
        
        print("⚠️  Continuando con configuración por defecto...")
    else:
        print(f"✅ Todas las configuraciones YAML validadas exitosamente ({summary['valid_files']}/{summary['total_files']})")
    
    return summary

# Ejecutar validación al importar este módulo
if __name__ == "__main__":
    validate_configuration_on_startup()
