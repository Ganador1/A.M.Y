#!/usr/bin/env python3
"""
Script para auditar el uso de pickle en el código
Identifica archivos que usan pickle y evalúa el riesgo de seguridad
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Tuple

def check_pickle_usage(filepath: str) -> List[Tuple[int, str]]:
    """Analiza un archivo Python para encontrar usos de pickle"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        pickle_calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Verificar si es una llamada a pickle
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['loads', 'load', 'dumps', 'dump']:
                        # Verificar si el objeto es pickle
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == 'pickle':
                            line = node.lineno
                            call_type = node.func.attr
                            pickle_calls.append((line, call_type))
                
                # Verificar imports de pickle
                elif isinstance(node.func, ast.Name):
                    if node.func.id in ['pickle.loads', 'pickle.load', 'pickle.dumps', 'pickle.dump']:
                        line = node.lineno
                        call_type = node.func.id.split('.')[1]
                        pickle_calls.append((line, call_type))
        
        return pickle_calls
    except Exception as e:
        print(f"Error analizando {filepath}: {e}")
        return []

def check_pickle_imports(filepath: str) -> List[str]:
    """Verifica si el archivo importa pickle"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == 'pickle':
                        imports.append(f"import pickle (línea {node.lineno})")
            elif isinstance(node, ast.ImportFrom):
                if node.module == 'pickle':
                    for alias in node.names:
                        imports.append(f"from pickle import {alias.name} (línea {node.lineno})")
        
        return imports
    except Exception as e:
        print(f"Error verificando imports en {filepath}: {e}")
        return []

def classify_risk(filepath: str, pickle_calls: List[Tuple[int, str]]) -> str:
    """Clasifica el riesgo basado en el uso de pickle"""
    if not pickle_calls:
        return "NONE"
    
    # Verificar si hay loads/load (más peligroso)
    dangerous_calls = [call for call in pickle_calls if call[1] in ['loads', 'load']]
    
    if dangerous_calls:
        return "HIGH"  # Carga de datos deserializados
    else:
        return "MEDIUM"  # Solo serialización

def main():
    """Función principal para auditar pickle"""
    
    # Archivos identificados en el roadmap
    files_to_check = [
        "app/models/artifacts/manifest_models.py",
        "app/services/literature_offline_cache.py", 
        "app/services/reproducibility_service.py",
        "app/services/dynamic_priority_queue_service.py",
        "app/services/scientific_automl_service.py",
        "app/services/data_versioning_service.py",
        "app/services/massive_automl_service.py",
        "app/advanced_ops/advanced_redis_operations.py"
    ]
    
    print("🔍 AUDITORÍA DE USO DE PICKLE")
    print("=" * 50)
    
    total_files = 0
    files_with_pickle = 0
    high_risk_files = 0
    
    results = []
    
    for file_path in files_to_check:
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"❌ Archivo no encontrado: {file_path}")
            continue
            
        total_files += 1
        
        # Verificar imports
        imports = check_pickle_imports(str(full_path))
        
        # Verificar uso
        pickle_calls = check_pickle_usage(str(full_path))
        
        if imports or pickle_calls:
            files_with_pickle += 1
            risk_level = classify_risk(str(full_path), pickle_calls)
            
            if risk_level == "HIGH":
                high_risk_files += 1
            
            result = {
                'file': file_path,
                'imports': imports,
                'calls': pickle_calls,
                'risk': risk_level
            }
            results.append(result)
            
            print(f"\n📁 {file_path}")
            print(f"   Riesgo: {risk_level}")
            if imports:
                print(f"   Imports: {', '.join(imports)}")
            if pickle_calls:
                print(f"   Llamadas pickle: {len(pickle_calls)}")
                for line, call_type in pickle_calls:
                    print(f"     - Línea {line}: {call_type}")
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE AUDITORÍA")
    print(f"Archivos analizados: {total_files}")
    print(f"Archivos con pickle: {files_with_pickle}")
    print(f"Archivos de alto riesgo: {high_risk_files}")
    
    # Generar reporte JSON
    import json
    report = {
        'timestamp': str(Path().cwd()),
        'total_files': total_files,
        'files_with_pickle': files_with_pickle,
        'high_risk_files': high_risk_files,
        'results': results
    }
    
    with open('pickle_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Reporte guardado en: pickle_audit_report.json")
    
    return results

if __name__ == "__main__":
    main()
