#!/usr/bin/env python3
"""
AXIOM - Análisis Completo de Herramientas Disponibles
Verifica el estado de importación de todos los routers y servicios
"""

import sys
import os
import importlib
from fastapi.routing import APIRoute

# Añadir el directorio raíz al path
sys.path.insert(0, '.')

def analyze_routers():
    """Analizar todos los routers disponibles"""
    routers_dir = './app/routers'
    router_files = [f for f in os.listdir(routers_dir) if f.endswith('.py') and f != '__init__.py']

    results = {
        'total_routers': len(router_files),
        'importable': [],
        'not_importable': [],
        'errors': {}
    }

    with open('./analysis_debug.log', 'a') as log_file:
        log_file.write(f"🔍 Analizando {len(router_files)} routers disponibles...\n")

    for router_file in sorted(router_files):
        router_name = router_file.replace('.py', '')
        module_path = f'app.routers.{router_name}'

        try:
            # Intentar importar el módulo
            module = importlib.import_module(module_path)
            results['importable'].append(router_name)

            # Verificar si tiene router FastAPI
            if hasattr(module, 'router'):
                with open('./analysis_debug.log', 'a') as log_file:
                    log_file.write(f"✅ {router_name}: Importable + Router FastAPI\n")
            else:
                with open('./analysis_debug.log', 'a') as log_file:
                    log_file.write(f"⚠️  {router_name}: Importable pero sin router FastAPI\n")

        except Exception as e:
            results['not_importable'].append(router_name)
            results['errors'][router_name] = str(e)
            with open('./analysis_debug.log', 'a') as log_file:
                log_file.write(f"❌ {router_name}: Error de importación - {str(e)[:50]}...\n")

    return results

def analyze_services():
    """Analizar todos los servicios disponibles"""
    services_dir = './app/services'
    service_files = [f for f in os.listdir(services_dir) if f.endswith('.py') and f != '__init__.py']

    results = {
        'total_services': len(service_files),
        'importable': [],
        'not_importable': [],
        'errors': {},
        'with_classes': []
    }

    with open('./analysis_debug.log', 'a') as log_file:
        log_file.write(f"\n🔍 Analizando {len(service_files)} servicios disponibles...\n")

    for service_file in sorted(service_files):
        service_name = service_file.replace('.py', '')
        module_path = f'app.services.{service_name}'

        try:
            # Intentar importar el módulo
            module = importlib.import_module(module_path)
            results['importable'].append(service_name)

            # Verificar si tiene clases de servicio
            service_classes = []
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    hasattr(attr, '__name__') and
                    ('Service' in attr.__name__ or 'Agent' in attr.__name__ or 'Manager' in attr.__name__)):
                    service_classes.append(attr.__name__)

            if service_classes:
                results['with_classes'].append({
                    'service': service_name,
                    'classes': service_classes
                })
                with open('./analysis_debug.log', 'a') as log_file:
                    log_file.write(f"✅ {service_name}: Importable + {len(service_classes)} clases ({', '.join(service_classes[:3])})\n")
            else:
                with open('./analysis_debug.log', 'a') as log_file:
                    log_file.write(f"⚠️  {service_name}: Importable pero sin clases identificadas\n")

        except Exception as e:
            results['not_importable'].append(service_name)
            results['errors'][service_name] = str(e)
            with open('./analysis_debug.log', 'a') as log_file:
                log_file.write(f"❌ {service_name}: Error de importación - {str(e)[:50]}...\n")

    return results

def analyze_loops():
    """Analizar los loops autónomos disponibles"""
    loops_dir = './app/autonomous/pipelines'
    loop_files = [f for f in os.listdir(loops_dir) if f.endswith('.py') and f != '__init__.py']

    results = {
        'total_loops': len(loop_files),
        'importable': [],
        'not_importable': [],
        'errors': {}
    }

    with open('./analysis_debug.log', 'a') as log_file:
        log_file.write(f"\n🔍 Analizando {len(loop_files)} loops autónomos disponibles...\n")

    for loop_file in sorted(loop_files):
        loop_name = loop_file.replace('.py', '')
        module_path = f'app.autonomous.pipelines.{loop_name}'

        try:
            # Intentar importar el módulo
            module = importlib.import_module(module_path)
            results['importable'].append(loop_name)

            # Verificar si tiene clase de loop
            loop_classes = []
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    hasattr(attr, '__name__') and
                    'Loop' in attr.__name__):
                    loop_classes.append(attr.__name__)

            if loop_classes:
                with open('./analysis_debug.log', 'a') as log_file:
                    log_file.write(f"✅ {loop_name}: Importable + {len(loop_classes)} loops ({', '.join(loop_classes)})\n")
            else:
                with open('./analysis_debug.log', 'a') as log_file:
                    log_file.write(f"⚠️  {loop_name}: Importable pero sin clases Loop identificadas\n")

        except Exception as e:
            results['not_importable'].append(loop_name)
            results['errors'][loop_name] = str(e)
            with open('./analysis_debug.log', 'a') as log_file:
                log_file.write(f"❌ {loop_name}: Error de importación - {str(e)[:50]}...\n")

    return results

def check_main_app():
    """Verificar qué routers están registrados en la aplicación principal"""
    with open('./analysis_debug.log', 'a') as log_file:
        log_file.write("\n🔍 Verificando routers registrados en main.py...\n")
    
    try:
        # Intentar importar la aplicación principal
        from main import app
        routes = []
        for route in app.routes:
            # Verificar si es una ruta API (APIRoute)
            if isinstance(route, APIRoute):
                routes.append({
                    'path': route.path,
                    'methods': list(route.methods),
                    'name': getattr(route, 'name', 'unnamed')
                })

        # Filtrar rutas de API
        api_routes = [r for r in routes if r['path'].startswith('/api/') or '/v1/' in r['path']]

        with open('./analysis_debug.log', 'a') as log_file:
            log_file.write(f"📊 Total de rutas en la app: {len(routes)}\n")
            log_file.write(f"🔗 Rutas API: {len(api_routes)}\n")

        # Mostrar algunas rutas de ejemplo
        with open('./analysis_debug.log', 'a') as log_file:
            log_file.write("\n📋 Ejemplos de rutas API disponibles:\n")
        for route in api_routes[:10]:  # Mostrar primeras 10
            methods = ', '.join(route['methods'])
            with open('./analysis_debug.log', 'a') as log_file:
                log_file.write(f"   {methods} {route['path']}\n")

        if len(api_routes) > 10:
            with open('./analysis_debug.log', 'a') as log_file:
                log_file.write(f"   ... y {len(api_routes) - 10} rutas más\n")

        return {
            'total_routes': len(routes),
            'api_routes': len(api_routes),
            'routes_sample': api_routes[:10]
        }

    except Exception as e:
        with open('./analysis_debug.log', 'a') as log_file:
            log_file.write(f"❌ Error al verificar main.py: {e}\n")
        return {'error': str(e)}

def generate_comprehensive_report(routers, services, loops, app_status):
    """Generar reporte comprehensivo"""
    report = {
        'timestamp': '2025-09-21T21:45:00Z',
        'analysis_type': 'AXIOM Tools Availability Analysis',
        'summary': {
            'total_routers': routers['total_routers'],
            'routers_importable': len(routers['importable']),
            'routers_not_importable': len(routers['not_importable']),
            'total_services': services['total_services'],
            'services_importable': len(services['importable']),
            'services_not_importable': len(services['not_importable']),
            'services_with_classes': len(services['with_classes']),
            'total_loops': loops['total_loops'],
            'loops_importable': len(loops['importable']),
            'loops_not_importable': len(loops['not_importable']),
            'api_routes_registered': app_status.get('api_routes', 0) if isinstance(app_status, dict) else 0
        },
        'details': {
            'routers': routers,
            'services': services,
            'loops': loops,
            'app_status': app_status
        }
    }

    # Guardar reporte
    import json
    with open('./axiom_tools_availability_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    return report

def display_summary_report(report):
    """Mostrar reporte resumen"""
    print("\n" + "="*80)
    print("🎯 AXIOM - ANÁLISIS DE HERRAMIENTAS DISPONIBLES")
    print("="*80)

    summary = report['summary']

    print("\n📊 RESUMEN GENERAL:")
    print(f"   🔗 Routers totales: {summary['total_routers']}")
    print(f"   ✅ Routers importables: {summary['routers_importable']}")
    print(f"   ❌ Routers no importables: {summary['routers_not_importable']}")
    print(f"   🔧 Servicios totales: {summary['total_services']}")
    print(f"   ✅ Servicios importables: {summary['services_importable']}")
    print(f"   ❌ Servicios no importables: {summary['services_not_importable']}")
    print(f"   🏗️ Servicios con clases: {summary['services_with_classes']}")
    print(f"   🔄 Loops autónomos totales: {summary['total_loops']}")
    print(f"   ✅ Loops importables: {summary['loops_importable']}")
    print(f"   ❌ Loops no importables: {summary['loops_not_importable']}")
    print(f"   🌐 Rutas API registradas: {summary['api_routes_registered']}")

    # Calcular porcentajes
    router_success_rate = (summary['routers_importable'] / summary['total_routers'] * 100) if summary['total_routers'] > 0 else 0
    service_success_rate = (summary['services_importable'] / summary['total_services'] * 100) if summary['total_services'] > 0 else 0
    loop_success_rate = (summary['loops_importable'] / summary['total_loops'] * 100) if summary['total_loops'] > 0 else 0

    print("\n📈 TASAS DE ÉXITO:")
    print(f"   🔗 Routers: {router_success_rate:.1f}% importables")
    print(f"   🔧 Servicios: {service_success_rate:.1f}% importables")
    print(f"   🔄 Loops: {loop_success_rate:.1f}% importables")

    # Mostrar servicios más importantes disponibles
    print("\n🛠️ SERVICIOS CLAVE DISPONIBLES:")
    key_services = ['computational_chemistry', 'dnabert2', 'gnome_materials',
                   'advanced_medical_imaging', 'quantum_physics', 'literature_search',
                   'scientific_hypothesis', 'peer_review', 'publication_generator']

    available_key_services = []
    for service_info in report['details']['services']['with_classes']:
        if service_info['service'] in key_services:
            available_key_services.append(service_info)

    for service in available_key_services:
        classes = ', '.join(service['classes'][:2])  # Mostrar máximo 2 clases
        print(f"   ✅ {service['service']}: {classes}")

    # Mostrar problemas principales
    print("\n⚠️ PROBLEMAS PRINCIPALES:")
    if summary['routers_not_importable'] > 0:
        print(f"   🔗 {summary['routers_not_importable']} routers con errores de importación")
    if summary['services_not_importable'] > 0:
        print(f"   🔧 {summary['services_not_importable']} servicios con errores de importación")
    if summary['loops_not_importable'] > 0:
        print(f"   🔄 {summary['loops_not_importable']} loops con errores de importación")

    print("\n💾 Reporte guardado: axiom_tools_availability_analysis.json")
    print("="*80)

def main():
    """Función principal"""
    try:
        with open('./analysis_debug.log', 'w') as log_file:
            log_file.write("🚀 AXIOM - ANÁLISIS COMPLETO DE HERRAMIENTAS DISPONIBLES\n")
            log_file.write("Verificando estado de importación de todos los componentes...\n")
            log_file.write(f"Directorio actual: {os.getcwd()}\n")
            log_file.write(f"Python path incluye: {[p for p in sys.path if 'atlas' in p]}\n")

            # Analizar componentes
            log_file.write("\n--- ANALIZANDO ROUTERS ---\n")
            routers = analyze_routers()
            log_file.write(f"Routers analizados: {len(routers['importable'])} importables, {len(routers['not_importable'])} no importables\n")

            log_file.write("\n--- ANALIZANDO SERVICIOS ---\n")
            services = analyze_services()
            log_file.write(f"Servicios analizados: {len(services['importable'])} importables, {len(services['not_importable'])} no importables\n")

            log_file.write("\n--- ANALIZANDO LOOPS ---\n")
            loops = analyze_loops()
            log_file.write(f"Loops analizados: {len(loops['importable'])} importables, {len(loops['not_importable'])} no importables\n")

            log_file.write("\n--- VERIFICANDO APP PRINCIPAL ---\n")
            app_status = check_main_app()
            log_file.write(f"App status: {app_status}\n")

            # Generar reporte
            log_file.write("\n--- GENERANDO REPORTE ---\n")
            report = generate_comprehensive_report(routers, services, loops, app_status)

            # Mostrar resumen
            log_file.write("\n--- MOSTRANDO RESUMEN ---\n")
            display_summary_report(report)

            log_file.write("\n✅ ANÁLISIS COMPLETADO EXITOSAMENTE\n")

    except Exception as e:
        with open('./analysis_error.log', 'w') as error_file:
            error_file.write(f"❌ ERROR CRÍTICO en main(): {e}\n")
            import traceback
            error_file.write(traceback.format_exc())
        print(f"❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    print("Script starting...")
    main()
    print("Script finished successfully!")
