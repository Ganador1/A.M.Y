#!/usr/bin/env python3
"""
Generador de propuesta de reorganización para app/
"""
import json
from pathlib import Path

def load_analysis_data():
    """Cargar datos de análisis previos"""
    with open('artifacts/reports/app_root_analysis.json', 'r') as f:
        root_analysis = json.load(f)
    
    with open('artifacts/reports/app_connectivity_analysis.json', 'r') as f:
        connectivity = json.load(f)
    
    return root_analysis, connectivity

def classify_module(module_data, is_orphan=False):
    """Clasificar módulo en nueva estructura organizacional"""
    name = module_data['name']
    purpose_hints = module_data.get('purpose_hints', {})
    characteristics = module_data.get('characteristics', {})
    lines = module_data.get('lines_of_code', 0)
    
    # Reglas de clasificación específicas
    
    # 1. Core infrastructure
    if name in ['__init__', 'config', 'logging_config', 'database', 'cache']:
        return 'core'
    
    # 2. Authentication & Security
    if name in ['auth', 'security', 'security_dashboard', 'hmac_integrity', 'integrity_core', 'integrity_verification']:
        return 'security'
    
    # 3. Monitoring & Health
    if name in ['health', 'monitoring', 'metrics', 'realtime_monitoring', 'automated_alerts', 'performance_profiler']:
        return 'monitoring'
    
    # 4. Medical/Clinical Services  
    if any(keyword in name for keyword in ['medical', 'clinical', 'cardiac', 'biomechanical', 'strain']):
        return 'medical'
    
    # 5. Scientific Computing Services
    if any(keyword in name for keyword in ['plasma', 'additive', 'multiscale']) or name.endswith('_models'):
        return 'scientific'
    
    # 6. Advanced Operations (high-performance utilities)
    if name.startswith('advanced_'):
        # Sub-clasificar advanced
        if 'operations' in name:
            return 'advanced_ops'
        elif any(word in name for word in ['service', 'imaging', 'validation']):
            return 'advanced_services'
        else:
            return 'advanced_ops'
    
    # 7. Tool Adapters & Utilities
    if 'adapter' in name or 'tool' in name:
        return 'adapters'
    
    # 8. Distributed & Scaling
    if any(keyword in name for keyword in ['distributed', 'scalability', 'gpu']):
        return 'distributed'
    
    # 9. Risk & Compliance
    if any(keyword in name for keyword in ['risk', 'ethics', 'license']):
        return 'compliance'
    
    # 10. Processing & Async
    if any(keyword in name for keyword in ['processor', 'async']):
        return 'processing'
    
    # 11. Validation & Testing
    if 'validation' in name and 'clinical' not in name:
        return 'validation'
    
    # 12. Algorithms & Optimization
    if any(keyword in name for keyword in ['algorithm', 'optimizer', 'anomaly']):
        return 'algorithms'
    
    # 13. Infrastructure utilities
    if any(keyword in name for keyword in ['rate_limit', 'blockchain', 'service_registry']):
        return 'infrastructure'
    
    # 14. Uncertainty & Quality
    if 'uncertainty' in name or 'robustness' in name:
        return 'quality'
    
    # Default: utilities
    return 'utils'

def generate_reorganization_proposal():
    """Generar propuesta completa de reorganización"""
    print("📋 Generando propuesta de reorganización...")
    
    root_analysis, connectivity = load_analysis_data()
    
    # Obtener lista de módulos órfanos en app raíz
    orphans = set(connectivity['app_root_orphans'])
    
    # Clasificar todos los módulos
    classification = {}
    orphan_classification = {}
    
    for file_data in root_analysis['files']:
        name = file_data['name']
        module_path = f"app.{name}"
        is_orphan = module_path in orphans
        
        category = classify_module(file_data, is_orphan)
        classification[name] = {
            'category': category,
            'is_orphan': is_orphan,
            'lines': file_data.get('lines_of_code', 0),
            'has_docs': file_data.get('has_docstring', False),
            'current_path': f"app/{name}.py",
            'proposed_path': f"app/{category}/{name}.py"
        }
        
        if is_orphan:
            orphan_classification[name] = category
    
    # Agrupar por categoría
    by_category = {}
    for name, data in classification.items():
        category = data['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(name)
    
    # Generar estructura de directorios propuesta
    directory_structure = {
        'core': "Infraestructura básica: config, database, cache, logging",
        'security': "Autenticación, autorización, integridad, seguridad",
        'monitoring': "Salud, métricas, monitoreo, alertas, profiling",
        'medical': "Servicios médicos: imaging, validación clínica, strain",
        'scientific': "Servicios científicos: plasma, manufactura, modelos",
        'advanced_ops': "Operaciones avanzadas: numpy, scipy, torch, etc",
        'advanced_services': "Servicios avanzados especializados",
        'adapters': "Adaptadores de herramientas y APIs externas",
        'distributed': "Escalamiento, distribución, GPU, clusters",
        'compliance': "Riesgo, ética, licencias, cumplimiento",
        'processing': "Procesamiento asíncrono, colas, workers",
        'validation': "Matrices de validación, cross-validation",
        'algorithms': "Algoritmos, optimización, detección anomalías",
        'infrastructure': "Rate limiting, blockchain, service discovery",
        'quality': "Incertidumbre, robustez, métricas de calidad",
        'utils': "Utilidades generales"
    }
    
    # Crear reporte de propuesta
    proposal = {
        'reorganization_date': '2025-09-21',
        'summary': {
            'total_files': len(classification),
            'total_orphans': len(orphan_classification),
            'proposed_directories': len(directory_structure),
            'categories': list(directory_structure.keys())
        },
        'directory_structure': directory_structure,
        'classification': classification,
        'by_category': by_category,
        'orphan_focus': {
            'total_orphans': len(orphan_classification),
            'orphan_distribution': {cat: len([n for n, c in orphan_classification.items() if c == cat]) 
                                  for cat in set(orphan_classification.values())}
        },
        'migration_steps': [
            "1. Crear directorios de categorías en app/",
            "2. Mover archivos a sus categorías respectivas",
            "3. Actualizar imports en todo el proyecto",
            "4. Verificar tests y corregir paths",
            "5. Ejecutar smoke tests de conectividad",
            "6. Actualizar documentación"
        ]
    }
    
    # Guardar propuesta
    with open('artifacts/reports/app_reorganization_proposal.json', 'w') as f:
        json.dump(proposal, f, indent=2)
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN DE REORGANIZACIÓN:")
    print(f"   Total archivos: {proposal['summary']['total_files']}")
    print(f"   Archivos órfanos: {proposal['summary']['total_orphans']}")
    print(f"   Categorías propuestas: {proposal['summary']['proposed_directories']}")
    
    print(f"\n📂 ESTRUCTURA PROPUESTA:")
    for category, description in directory_structure.items():
        count = len(by_category.get(category, []))
        orphan_count = len([n for n, c in orphan_classification.items() if c == category])
        status = f"({orphan_count} órfanos)" if orphan_count > 0 else ""
        print(f"   app/{category}/ - {count} archivos {status}")
        print(f"      {description}")
    
    print(f"\n⚠️  ÓRFANOS POR CATEGORÍA:")
    for category, count in proposal['orphan_focus']['orphan_distribution'].items():
        print(f"   {category}: {count} archivos")
    
    print(f"\n💾 Propuesta detallada: artifacts/reports/app_reorganization_proposal.json")
    
    return proposal

if __name__ == '__main__':
    generate_reorganization_proposal()
