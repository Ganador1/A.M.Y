#!/usr/bin/env python3
"""
Script para mapear la conectividad entre módulos en la carpeta app/
"""
import json
import ast
from pathlib import Path
from collections import defaultdict, deque

def build_import_graph():
    """Construye el grafo de imports de todos los módulos en app/"""
    app_root = Path('app')
    
    # Encontrar todos los archivos Python recursivamente
    all_py_files = list(app_root.rglob('*.py'))
    
    # Mapeo de archivo -> módulo Python
    file_to_module = {}
    module_to_file = {}
    
    for file in all_py_files:
        # Convertir ruta a nombre de módulo
        relative = file.relative_to(Path('.'))
        module_name = str(relative.with_suffix('')).replace('/', '.')
        file_to_module[str(file)] = module_name
        module_to_file[module_name] = str(file)
    
    # Analizar imports de cada archivo
    import_graph = defaultdict(set)
    file_analysis = {}
    
    for file in all_py_files:
        module_name = file_to_module[str(file)]
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file))
            
            imports = []
            internal_imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        # También agregar imports específicos con from
                        if node.names:
                            for alias in node.names:
                                if alias.name != '*':
                                    full_import = f"{node.module}.{alias.name}"
                                    imports.append(full_import)
            
            # Filtrar imports internos (que están en nuestro proyecto)
            for imp in imports:
                # Buscar módulos que empiecen con el import
                for mod in module_to_file.keys():
                    if mod.startswith(imp) or imp.startswith(mod):
                        if mod != module_name:  # No auto-referencia
                            internal_imports.append(mod)
                            import_graph[module_name].add(mod)
            
            file_analysis[module_name] = {
                'file': str(file),
                'all_imports': imports,
                'internal_imports': list(set(internal_imports)),
                'lines': len(content.split('\n'))
            }
            
        except Exception as e:
            file_analysis[module_name] = {
                'file': str(file),
                'error': str(e),
                'all_imports': [],
                'internal_imports': [],
                'lines': 0
            }
    
    return import_graph, file_analysis, module_to_file

def find_connected_components(graph, entry_points):
    """Encuentra componentes conectados desde puntos de entrada"""
    visited = set()
    reachable = set()
    
    # BFS desde puntos de entrada
    queue = deque(entry_points)
    
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        
        visited.add(current)
        reachable.add(current)
        
        # Agregar dependencias
        for dependency in graph.get(current, set()):
            if dependency not in visited:
                queue.append(dependency)
    
    return reachable

def analyze_connectivity():
    """Análisis completo de conectividad"""
    print("🔍 Construyendo grafo de imports...")
    import_graph, file_analysis, module_to_file = build_import_graph()
    
    # Identificar puntos de entrada principales
    entry_points = []
    
    # 1. main.py (punto de entrada principal)
    if 'main' in module_to_file:
        entry_points.append('main')
    
    # 2. Routers (endpoints FastAPI)
    for module in module_to_file.keys():
        if 'routers' in module:
            entry_points.append(module)
    
    # 3. Archivos en app/ raíz que parecen ser servicios principales
    root_modules = [m for m in module_to_file.keys() if m.count('.') == 1 and m.startswith('app.')]
    for module in root_modules:
        name = module.split('.')[-1]
        if any(keyword in name for keyword in ['main', 'app', 'server', 'api']):
            if module not in entry_points:
                entry_points.append(module)
    
    print(f"📍 Puntos de entrada identificados: {len(entry_points)}")
    for ep in entry_points:
        print(f"   - {ep}")
    
    # Encontrar módulos alcanzables
    reachable = find_connected_components(import_graph, entry_points)
    
    # Identificar órfanos
    all_modules = set(module_to_file.keys())
    orphans = all_modules - reachable
    
    # Análisis de módulos raíz de app/
    app_root_modules = [m for m in all_modules if m.count('.') == 1 and m.startswith('app.')]
    app_root_orphans = [m for m in app_root_modules if m in orphans]
    
    # Estadísticas
    stats = {
        'total_modules': len(all_modules),
        'reachable_modules': len(reachable),
        'orphan_modules': len(orphans),
        'app_root_modules': len(app_root_modules),
        'app_root_orphans': len(app_root_orphans),
        'connectivity_ratio': len(reachable) / len(all_modules) if all_modules else 0
    }
    
    # Crear reporte detallado
    report = {
        'analysis_timestamp': '2025-09-21',
        'entry_points': entry_points,
        'statistics': stats,
        'reachable_modules': sorted(list(reachable)),
        'orphan_modules': sorted(list(orphans)),
        'app_root_orphans': sorted(app_root_orphans),
        'import_graph': {k: sorted(list(v)) for k, v in import_graph.items()},
        'file_analysis': file_analysis
    }
    
    # Guardar reporte
    with open('artifacts/reports/app_connectivity_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 ESTADÍSTICAS DE CONECTIVIDAD:")
    print(f"   Total módulos: {stats['total_modules']}")
    print(f"   Módulos alcanzables: {stats['reachable_modules']}")
    print(f"   Módulos órfanos: {stats['orphan_modules']}")
    print(f"   Ratio conectividad: {stats['connectivity_ratio']:.2%}")
    print(f"\n🏠 MÓDULOS EN app/ RAÍZ:")
    print(f"   Total: {stats['app_root_modules']}")
    print(f"   Órfanos: {stats['app_root_orphans']}")
    
    if app_root_orphans:
        print(f"\n⚠️  MÓDULOS ÓRFANOS EN app/ RAÍZ:")
        for orphan in app_root_orphans[:20]:  # Mostrar primeros 20
            module_name = orphan.split('.')[-1]
            lines = file_analysis.get(orphan, {}).get('lines', 0)
            print(f"   - {module_name} ({lines} líneas)")
    
    print(f"\n💾 Reporte detallado: artifacts/reports/app_connectivity_analysis.json")
    
    return report

if __name__ == '__main__':
    analyze_connectivity()
