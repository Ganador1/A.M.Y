#!/usr/bin/env python3
"""
AXIOM ATLAS META 4 - Ejecución de Todos los Loops en Producción
Ejecuta los 10 loops científicos autónomos y genera reporte completo
"""

import sys
import os
import json
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import traceback

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Configuración de colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message: str):
    """Imprime un encabezado formateado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(message: str):
    """Imprime un mensaje de éxito"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.OKGREEN}[{timestamp}] ✅ {message}{Colors.ENDC}")

def print_error(message: str):
    """Imprime un mensaje de error"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.FAIL}[{timestamp}] ❌ {message}{Colors.ENDC}")

def print_info(message: str):
    """Imprime un mensaje informativo"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.OKCYAN}[{timestamp}] ℹ️  {message}{Colors.ENDC}")

def print_warning(message: str):
    """Imprime un mensaje de advertencia"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.WARNING}[{timestamp}] ⚠️  {message}{Colors.ENDC}")


# Configuración de loops a ejecutar
LOOPS_CONFIG = [
    {
        "name": "QuantumLoop",
        "module": "app.autonomous.pipelines.quantum_loop",
        "class": "QuantumLoop",
        "description": "Optimización de algoritmos cuánticos",
        "priority": 1
    },
    {
        "name": "MathematicsLoop",
        "module": "app.autonomous.pipelines.mathematics_loop",
        "class": "MathematicsLoop",
        "description": "Generación de conjeturas matemáticas",
        "priority": 2
    },
    {
        "name": "EngineeringLoop",
        "module": "app.autonomous.pipelines.engineering_loop",
        "class": "EngineeringLoop",
        "description": "Optimización de manufactura aditiva",
        "priority": 3
    },
    {
        "name": "AstronomyLoop",
        "module": "app.autonomous.pipelines.astronomy_loop",
        "class": "AstronomyLoop",
        "description": "Clasificación de objetos astronómicos",
        "priority": 4
    },
    {
        "name": "ChemistryLoop",
        "module": "app.autonomous.pipelines.chemistry_loop",
        "class": "ChemistryLoop",
        "description": "Diseño molecular y optimización de fármacos",
        "priority": 5
    },
    {
        "name": "BiologyLoop",
        "module": "app.autonomous.pipelines.biology_loop",
        "class": "BiologyLoop",
        "description": "Análisis genómico funcional",
        "priority": 6
    },
    {
        "name": "MaterialsLoop",
        "module": "app.autonomous.pipelines.materials_loop",
        "class": "MaterialsLoop",
        "description": "Descubrimiento de materiales",
        "priority": 7
    },
    {
        "name": "ClimateLoop",
        "module": "app.autonomous.pipelines.climate_loop",
        "class": "ClimateLoop",
        "description": "Predicción de anomalías climáticas",
        "priority": 8
    },
    {
        "name": "MedicineLoop",
        "module": "app.autonomous.pipelines.medicine_loop",
        "class": "MedicineLoop",
        "description": "Diagnóstico médico automatizado",
        "priority": 9
    },
    {
        "name": "NeuroscienceLoop",
        "module": "app.autonomous.pipelines.neuroscience_loop",
        "class": "NeuroscienceLoop",
        "description": "Análisis de neuroimagen",
        "priority": 10
    }
]


def load_loop_module(module_path: str, class_name: str):
    """Carga un módulo de loop dinámicamente"""
    try:
        # Importar el módulo
        module = importlib.import_module(module_path)
        
        # Obtener la clase
        loop_class = getattr(module, class_name)
        
        return loop_class
    except Exception as e:
        raise ImportError(f"Error al cargar {module_path}.{class_name}: {e}")


def execute_loop(loop_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecuta un loop específico y retorna los resultados
    
    Args:
        loop_config: Configuración del loop
        
    Returns:
        Diccionario con resultados del loop
    """
    loop_name = loop_config["name"]
    start_time = datetime.now()
    
    print_info(f"Iniciando {loop_name}: {loop_config['description']}")
    
    try:
        # Cargar la clase del loop
        LoopClass = load_loop_module(loop_config["module"], loop_config["class"])
        
        # Instanciar el loop
        loop = LoopClass()
        
        # Ejecutar una iteración
        print_info(f"Ejecutando iteración de {loop_name}...")
        result = loop.run_iteration(limit=5)  # Generar 5 candidatos
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print_success(f"{loop_name} completado en {duration:.2f} segundos")
        
        return {
            "loop_name": loop_name,
            "success": True,
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "result": result,
            "error": None
        }
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        error_msg = f"{type(e).__name__}: {str(e)}"
        print_error(f"Error en {loop_name}: {error_msg}")
        
        # Imprimir traceback para debugging
        if "--verbose" in sys.argv:
            traceback.print_exc()
        
        return {
            "loop_name": loop_name,
            "success": False,
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "result": None,
            "error": error_msg,
            "traceback": traceback.format_exc()
        }


def generate_summary_report(results: List[Dict[str, Any]]) -> str:
    """Genera un reporte resumen de los resultados"""
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    total_duration = sum(r["duration_seconds"] for r in results)
    
    report_lines = []
    report_lines.append("\n" + "="*70)
    report_lines.append("REPORTE DE EJECUCIÓN - AXIOM ATLAS META 4".center(70))
    report_lines.append("="*70 + "\n")
    
    report_lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    report_lines.append(f"✅ Experimentos exitosos: {len(successful)}/{len(results)}")
    report_lines.append(f"❌ Experimentos fallidos: {len(failed)}/{len(results)}")
    report_lines.append(f"⏱️  Tiempo total de ejecución: {total_duration:.2f}s\n")
    
    if successful:
        report_lines.append("\n📊 EXPERIMENTOS EXITOSOS:\n")
        for result in successful:
            report_lines.append(f"  ✅ {result['loop_name']}: {result['duration_seconds']:.2f}s")
    
    if failed:
        report_lines.append("\n❌ EXPERIMENTOS FALLIDOS:\n")
        for result in failed:
            report_lines.append(f"  ❌ {result['loop_name']}: {result['error']}")
    
    report_lines.append("\n" + "="*70)
    
    return "\n".join(report_lines)


def main():
    """Función principal"""
    
    print_header("AXIOM ATLAS META 4 - EJECUCIÓN DE PRODUCCIÓN")
    print_info("Ejecutando todos los loops científicos autónomos...\n")
    
    # Resultados de todos los loops
    all_results = []
    
    # Ejecutar cada loop
    for loop_config in sorted(LOOPS_CONFIG, key=lambda x: x["priority"]):
        result = execute_loop(loop_config)
        all_results.append(result)
        print()  # Línea en blanco entre loops
    
    # Generar reporte resumen
    summary = generate_summary_report(all_results)
    print(summary)
    
    # Guardar resultados en JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"all_loops_production_results_{timestamp}.json"
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    print_success(f"Resultados guardados en: {json_filename}")
    
    # Generar reporte markdown
    md_filename = f"PRODUCTION_REPORT_ALL_LOOPS_{timestamp}.md"
    generate_markdown_report(all_results, md_filename)
    print_success(f"Reporte Markdown generado: {md_filename}")
    
    # Retornar código de salida
    failed_count = len([r for r in all_results if not r["success"]])
    return 0 if failed_count == 0 else 1


def generate_markdown_report(results: List[Dict[str, Any]], filename: str):
    """Genera un reporte en formato Markdown"""
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    total_duration = sum(r["duration_seconds"] for r in results)
    
    lines = []
    lines.append("# 🚀 Reporte de Ejecución de Producción - AXIOM ATLAS META 4\n")
    lines.append(f"**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"**Modo**: PRODUCCIÓN  ")
    lines.append(f"**Loops ejecutados**: {len(results)}\n")
    lines.append("---\n")
    
    lines.append("## 📊 Resumen Ejecutivo\n")
    lines.append(f"- ✅ **Experimentos exitosos**: {len(successful)}/{len(results)}")
    lines.append(f"- ❌ **Experimentos fallidos**: {len(failed)}/{len(results)}")
    lines.append(f"- ⏱️ **Tiempo total**: {total_duration:.2f} segundos")
    lines.append(f"- 📈 **Tasa de éxito**: {len(successful)/len(results)*100:.1f}%\n")
    
    if successful:
        lines.append("## ✅ Experimentos Exitosos\n")
        for result in successful:
            lines.append(f"### {result['loop_name']}\n")
            lines.append(f"- **Duración**: {result['duration_seconds']:.2f}s")
            lines.append(f"- **Inicio**: {result['start_time']}")
            lines.append(f"- **Estado**: ✅ EXITOSO\n")
            
            # Intentar extraer métricas si existen
            if result.get('result'):
                try:
                    res_data = result['result']
                    if isinstance(res_data, dict):
                        if 'candidates' in res_data:
                            lines.append(f"- **Candidatos generados**: {len(res_data['candidates'])}")
                        if 'novelty' in res_data:
                            lines.append(f"- **Novelty promedio**: {res_data['novelty']:.3f}")
                except:
                    pass
            
            lines.append("")
    
    if failed:
        lines.append("## ❌ Experimentos Fallidos\n")
        for result in failed:
            lines.append(f"### {result['loop_name']}\n")
            lines.append(f"- **Duración**: {result['duration_seconds']:.2f}s")
            lines.append(f"- **Error**: `{result['error']}`")
            lines.append(f"- **Estado**: ❌ FALLIDO\n")
    
    lines.append("---\n")
    lines.append("**Generado por**: AXIOM ATLAS META 4  ")
    lines.append("**Sistema**: Ejecución automatizada de loops científicos  ")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
