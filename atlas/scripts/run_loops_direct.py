#!/usr/bin/env python3
"""
Ejecución directa de loops científicos sin pasar por app/__init__.py
para evitar imports pesados innecesarios.
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message: str):
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")


def print_success(message: str):
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message: str):
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_info(message: str):
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")


def print_warning(message: str):
    print(f"{Colors.WARNING}⚠️ {message}{Colors.ENDC}")


def execute_loop_direct(loop_name: str, module_path: str, class_name: str, limit: int = 5) -> Dict[str, Any]:
    """
    Ejecuta un loop directamente importando solo el módulo necesario.
    """
    start_time = time.time()
    start_timestamp = datetime.now().isoformat()
    
    print_info(f"Iniciando {loop_name}: {module_path}.{class_name}")
    
    try:
        # Import dinámico solo del módulo específico
        import importlib
        module = importlib.import_module(module_path)
        LoopClass = getattr(module, class_name)
        
        # Instanciar y ejecutar
        loop_instance = LoopClass()
        result = loop_instance.run_iteration(limit=limit)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print_success(f"{loop_name} completado en {duration:.2f}s")
        
        return {
            "loop_name": loop_name,
            "success": True,
            "duration_seconds": duration,
            "start_time": start_timestamp,
            "end_time": datetime.now().isoformat(),
            "result": result,
            "error": None,
            "traceback": None
        }
        
    except Exception as e:
        import traceback as tb
        
        end_time = time.time()
        duration = end_time - start_time
        error_traceback = tb.format_exc()
        
        print_error(f"{loop_name}: {type(e).__name__}: {str(e)}")
        
        return {
            "loop_name": loop_name,
            "success": False,
            "duration_seconds": duration,
            "start_time": start_timestamp,
            "end_time": datetime.now().isoformat(),
            "result": None,
            "error": f"{type(e).__name__}: {str(e)}",
            "traceback": error_traceback
        }


def main():
    """
    Ejecuta todos los loops científicos autónomos.
    """
    print_header("\n" + "=" * 80)
    print_header("🚀 AXIOM ATLAS META 4 - Ejecución Directa de Loops Científicos")
    print_header("=" * 80 + "\n")
    
    # Configuración de loops (en orden de prioridad)
    loops_config = [
        {
            "name": "QuantumLoop",
            "module": "app.autonomous.pipelines.quantum_loop",
            "class": "QuantumLoop",
            "description": "Optimización de algoritmos cuánticos"
        },
        {
            "name": "MathematicsLoop",
            "module": "app.autonomous.pipelines.mathematics_loop",
            "class": "MathematicsLoop",
            "description": "Generación de conjeturas matemáticas"
        },
        {
            "name": "EngineeringLoop",
            "module": "app.autonomous.pipelines.engineering_loop",
            "class": "EngineeringLoop",
            "description": "Optimización de diseños de ingeniería"
        },
        {
            "name": "AstronomyLoop",
            "module": "app.autonomous.pipelines.astronomy_loop",
            "class": "AstronomyLoop",
            "description": "Análisis de datos astronómicos"
        },
        {
            "name": "ChemistryLoop",
            "module": "app.autonomous.pipelines.chemistry_loop",
            "class": "ChemistryLoop",
            "description": "Descubrimiento de moléculas"
        },
        {
            "name": "BiologyLoop",
            "module": "app.autonomous.pipelines.biology_loop",
            "class": "BiologyLoop",
            "description": "Análisis genómico y proteómico"
        },
        {
            "name": "MaterialsLoop",
            "module": "app.autonomous.pipelines.materials_loop",
            "class": "MaterialsLoop",
            "description": "Descubrimiento de materiales"
        },
        {
            "name": "ClimateLoop",
            "module": "app.autonomous.pipelines.climate_loop",
            "class": "ClimateLoop",
            "description": "Modelado climático"
        },
        {
            "name": "MedicineLoop",
            "module": "app.autonomous.pipelines.medicine_loop",
            "class": "MedicineLoop",
            "description": "Diagnóstico médico automatizado"
        },
        {
            "name": "NeuroscienceLoop",
            "module": "app.autonomous.pipelines.neuroscience_loop",
            "class": "NeuroscienceLoop",
            "description": "Simulación de redes neuronales"
        }
    ]
    
    results = []
    successful = 0
    failed = 0
    
    total_start_time = time.time()
    
    # Ejecutar cada loop
    for loop_config in loops_config:
        print(f"\n{Colors.BOLD}[{datetime.now().strftime('%H:%M:%S')}]{Colors.ENDC} ", end="")
        print_info(f"Iniciando {loop_config['name']}: {loop_config['description']}")
        
        result = execute_loop_direct(
            loop_name=loop_config["name"],
            module_path=loop_config["module"],
            class_name=loop_config["class"],
            limit=5
        )
        
        results.append(result)
        
        if result["success"]:
            successful += 1
        else:
            failed += 1
    
    total_duration = time.time() - total_start_time
    
    # Resumen final
    print_header("\n" + "=" * 80)
    print_header("📊 RESUMEN DE EJECUCIÓN")
    print_header("=" * 80 + "\n")
    
    print_success(f"Experimentos exitosos: {successful}/{len(loops_config)}")
    if failed > 0:
        print_error(f"Experimentos fallidos: {failed}/{len(loops_config)}")
    print_info(f"⏱️  Tiempo total: {total_duration:.2f}s")
    
    # Guardar resultados en JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"all_loops_direct_results_{timestamp}.json"
    
    with open(json_filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print_info(f"📁 Resultados guardados en: {json_filename}")
    
    # Generar reporte markdown
    md_filename = f"PRODUCTION_REPORT_ALL_LOOPS_DIRECT_{timestamp}.md"
    generate_markdown_report(results, md_filename, total_duration)
    
    print_info(f"📄 Reporte generado en: {md_filename}")
    print_header("\n" + "=" * 80 + "\n")
    
    return results


def generate_markdown_report(results: List[Dict[str, Any]], filename: str, total_duration: float):
    """
    Genera un reporte detallado en formato Markdown.
    """
    successful = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])
    
    with open(filename, 'w') as f:
        f.write(f"# 🚀 Reporte de Ejecución Directa - AXIOM ATLAS META 4\n\n")
        f.write(f"**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 📊 Resumen\n\n")
        f.write(f"- **Total de loops**: {len(results)}\n")
        f.write(f"- **Exitosos**: {successful} ✅\n")
        f.write(f"- **Fallidos**: {failed} ❌\n")
        f.write(f"- **Tiempo total**: {total_duration:.2f} segundos\n\n")
        
        f.write(f"## 📋 Resultados Detallados\n\n")
        
        for result in results:
            status = "✅ ÉXITO" if result["success"] else "❌ FALLO"
            f.write(f"### {result['loop_name']} - {status}\n\n")
            f.write(f"- **Duración**: {result['duration_seconds']:.2f}s\n")
            f.write(f"- **Inicio**: {result['start_time']}\n")
            f.write(f"- **Fin**: {result['end_time']}\n")
            
            if result["success"] and result["result"]:
                f.write(f"\n**Resultado**:\n```json\n")
                f.write(json.dumps(result["result"], indent=2, default=str))
                f.write(f"\n```\n\n")
            elif result["error"]:
                f.write(f"\n**Error**: `{result['error']}`\n\n")
            
            f.write("---\n\n")


if __name__ == "__main__":
    main()
