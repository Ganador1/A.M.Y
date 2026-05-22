#!/usr/bin/env python3
"""
Script para auditar documentación de módulos reorganizados
"""
import json
import ast
from pathlib import Path
import os

def audit_module_documentation():
    """Auditar documentación de todos los módulos en app/"""
    print("📚 Auditando documentación de módulos reorganizados...")
    
    # Cargar datos de reorganización
    with open('artifacts/reports/app_reorganization_execution.json', 'r') as f:
        reorganization = json.load(f)
    
    app_root = Path('app')
    undocumented_modules = []
    poorly_documented_modules = []
    well_documented_modules = []
    
    # Auditar cada archivo movido
    for move_info in reorganization['moved_files']:
        target_path = Path(move_info['to'])
        
        if not target_path.exists():
            continue
        
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(target_path))
            docstring = ast.get_docstring(tree)
            
            module_info = {
                'filename': move_info['filename'],
                'category': move_info['category'],
                'path': str(target_path),
                'is_orphan': move_info['is_orphan'],
                'lines': len(content.split('\n')),
                'has_docstring': bool(docstring and docstring.strip()),
                'docstring_length': len(docstring) if docstring else 0,
                'docstring_preview': docstring[:100] + '...' if docstring and len(docstring) > 100 else docstring or ""
            }
            
            # Clasificar calidad de documentación
            if not docstring or len(docstring.strip()) < 10:
                undocumented_modules.append(module_info)
            elif len(docstring.strip()) < 50:
                poorly_documented_modules.append(module_info)
            else:
                well_documented_modules.append(module_info)
                
        except Exception as e:
            print(f"❌ Error procesando {target_path}: {e}")
    
    # Identificar módulos órfanos sin documentación (prioridad alta)
    orphan_undocumented = [m for m in undocumented_modules if m['is_orphan']]
    
    # Generar reporte de documentación
    doc_report = {
        'audit_date': '2025-09-21',
        'total_modules': len(reorganization['moved_files']),
        'well_documented': len(well_documented_modules),
        'poorly_documented': len(poorly_documented_modules),
        'undocumented': len(undocumented_modules),
        'orphan_undocumented': len(orphan_undocumented),
        'documentation_coverage': len(well_documented_modules) / len(reorganization['moved_files']) * 100 if reorganization['moved_files'] else 0,
        'modules_by_category': {
            'well_documented': well_documented_modules,
            'poorly_documented': poorly_documented_modules,
            'undocumented': undocumented_modules,
            'orphan_undocumented': orphan_undocumented
        }
    }
    
    # Guardar reporte
    with open('artifacts/reports/app_documentation_audit.json', 'w') as f:
        json.dump(doc_report, f, indent=2)
    
    print(f"\n📊 AUDITORÍA DE DOCUMENTACIÓN:")
    print(f"   Total módulos: {doc_report['total_modules']}")
    print(f"   Bien documentados: {doc_report['well_documented']}")
    print(f"   Pobremente documentados: {doc_report['poorly_documented']}")
    print(f"   Sin documentar: {doc_report['undocumented']}")
    print(f"   Órfanos sin docstring: {doc_report['orphan_undocumented']}")
    print(f"   Cobertura documentación: {doc_report['documentation_coverage']:.1f}%")
    
    if orphan_undocumented:
        print(f"\n⚠️  MÓDULOS ÓRFANOS SIN DOCUMENTACIÓN (PRIORIDAD ALTA):")
        for module in sorted(orphan_undocumented, key=lambda x: x['lines'], reverse=True):
            print(f"   - {module['filename']} ({module['lines']} líneas) en {module['category']}")
    
    print(f"\n💾 Reporte detallado: artifacts/reports/app_documentation_audit.json")
    
    return doc_report

def add_basic_docstrings():
    """Agregar docstrings básicos a módulos órfanos críticos"""
    print("\n📝 Agregando docstrings a módulos órfanos críticos...")
    
    # Cargar auditoría de documentación
    with open('artifacts/reports/app_documentation_audit.json', 'r') as f:
        audit = json.load(f)
    
    orphan_undocumented = audit['modules_by_category']['orphan_undocumented']
    
    # Priorizar módulos grandes (más de 200 líneas)
    priority_modules = [m for m in orphan_undocumented if m['lines'] > 200]
    priority_modules.sort(key=lambda x: x['lines'], reverse=True)
    
    # Agregar docstrings a los primeros 5 módulos prioritarios
    added_docs = []
    
    for module in priority_modules[:5]:
        filepath = Path(module['path'])
        
        if not filepath.exists():
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Buscar dónde insertar el docstring
            insert_line = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('#!') or line.strip().startswith('# -*-'):
                    continue
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    # Ya tiene docstring, skip
                    break
                if line.strip() and not line.strip().startswith('#'):
                    # Primera línea de código
                    insert_line = i
                    break
            
            # Generar docstring básico basado en el nombre y categoría
            module_name = module['filename']
            category = module['category']
            
            docstring_content = generate_basic_docstring(module_name, category)
            
            # Insertar docstring
            lines.insert(insert_line, docstring_content)
            
            # Escribir archivo modificado
            new_content = '\n'.join(lines)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            added_docs.append({
                'filename': module_name,
                'path': str(filepath),
                'category': category,
                'lines': module['lines']
            })
            
            print(f"✓ Agregado docstring a {module_name}")
            
        except Exception as e:
            print(f"❌ Error procesando {module['filename']}: {e}")
    
    print(f"\n📊 DOCSTRINGS AGREGADOS:")
    print(f"   Total módulos procesados: {len(added_docs)}")
    
    for doc in added_docs:
        print(f"   - {doc['filename']} ({doc['lines']} líneas) en {doc['category']}")
    
    return added_docs

def generate_basic_docstring(module_name, category):
    """Generar docstring básico basado en nombre y categoría del módulo"""
    
    category_descriptions = {
        'core': 'Core infrastructure component',
        'security': 'Security and authentication module',
        'monitoring': 'Monitoring and metrics module',
        'medical': 'Medical imaging and analysis service',
        'scientific': 'Scientific computing service',
        'advanced_ops': 'Advanced operations utility',
        'advanced_services': 'Advanced service implementation',
        'adapters': 'Tool adapter and integration',
        'distributed': 'Distributed computing and scaling',
        'compliance': 'Risk management and compliance',
        'processing': 'Asynchronous processing module',
        'validation': 'Validation and testing utilities',
        'algorithms': 'Algorithm implementation',
        'infrastructure': 'Infrastructure utilities',
        'quality': 'Quality assurance and metrics',
        'utils': 'General utilities'
    }
    
    base_description = category_descriptions.get(category, 'Application module')
    
    # Crear descripción más específica basada en el nombre
    if 'imaging' in module_name.lower():
        specific = 'for medical imaging processing and analysis'
    elif 'strain' in module_name.lower():
        specific = 'for cardiac strain analysis and biomechanical modeling'
    elif 'clinical' in module_name.lower():
        specific = 'for clinical validation and healthcare applications'
    elif 'multiscale' in module_name.lower():
        specific = 'for multi-scale modeling and simulation'
    elif 'optimizer' in module_name.lower():
        specific = 'for optimization algorithms and performance enhancement'
    elif 'network' in module_name.lower():
        specific = 'for network analysis and graph operations'
    elif 'redis' in module_name.lower():
        specific = 'for Redis operations and caching'
    else:
        specific = 'providing specialized functionality'
    
    docstring = f'''"""
{module_name.replace('_', ' ').title()}

{base_description} {specific}.

This module is part of the AXIOM scientific computing platform
and provides core functionality for the application.

Note: This module requires integration review to ensure proper
connectivity within the application workflow.
"""'''
    
    return docstring

if __name__ == '__main__':
    audit_result = audit_module_documentation()
    added_docs = add_basic_docstrings()
