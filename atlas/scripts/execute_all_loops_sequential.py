#!/usr/bin/env python3
"""
Ejecuta todos los loops científicos SECUENCIALMENTE con nuevos experimentos.
Cada loop se ejecuta de forma aislada para evitar problemas de memoria.
"""

import json
import time
import sys
import traceback
from datetime import datetime
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


def execute_single_loop(loop_name: str, module_path: str, class_name: str) -> Dict[str, Any]:
    """
    Ejecuta un loop individual y retorna los resultados.
    """
    print(f"\n{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}🔬 Ejecutando: {loop_name}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
    
    start_time = time.time()
    start_timestamp = datetime.now().isoformat()
    
    try:
        # Import dinámico
        import importlib
        module = importlib.import_module(module_path)
        LoopClass = getattr(module, class_name)
        
        # Crear instancia
        print(f"{Colors.OKCYAN}📦 Instanciando {class_name}...{Colors.ENDC}")
        loop_instance = LoopClass()
        
        # Ejecutar con límite de 5 candidatos
        print(f"{Colors.OKCYAN}⚡ Ejecutando iteración...{Colors.ENDC}")
        result = loop_instance.run_iteration(iteration=1, limit=5)
        
        duration = time.time() - start_time
        
        print(f"\n{Colors.OKGREEN}✅ {loop_name} completado exitosamente en {duration:.2f}s{Colors.ENDC}")
        
        # Mostrar resumen de resultados
        if isinstance(result, dict):
            if 'candidates' in result:
                print(f"{Colors.OKGREEN}   📊 Candidatos generados: {len(result.get('candidates', []))}{Colors.ENDC}")
            if 'hypotheses' in result:
                print(f"{Colors.OKGREEN}   💡 Hipótesis generadas: {len(result.get('hypotheses', []))}{Colors.ENDC}")
            if 'molecules' in result:
                print(f"{Colors.OKGREEN}   🧪 Moléculas generadas: {len(result.get('molecules', []))}{Colors.ENDC}")
        
        return {
            "loop_name": loop_name,
            "success": True,
            "duration_seconds": duration,
            "start_time": start_timestamp,
            "end_time": datetime.now().isoformat(),
            "result": result,
            "error": None,
            "traceback": None,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        
        print(f"\n{Colors.FAIL}❌ {loop_name} falló: {error_msg}{Colors.ENDC}")
        print(f"{Colors.WARNING}⏱️  Duración antes del fallo: {duration:.2f}s{Colors.ENDC}")
        
        return {
            "loop_name": loop_name,
            "success": False,
            "duration_seconds": duration,
            "start_time": start_timestamp,
            "end_time": datetime.now().isoformat(),
            "result": None,
            "error": error_msg,
            "traceback": error_traceback,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        }


def main():
    """
    Ejecuta todos los loops en secuencia.
    """
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "🚀 AXIOM ATLAS - NUEVOS EXPERIMENTOS" + " " * 27 + "║")
    print("║" + " " * 20 + "Validación de 10 Loops Científicos" + " " * 24 + "║")
    print("╚" + "═" * 78 + "╝")
    print(f"{Colors.ENDC}\n")
    
    # Configuración de todos los loops
    loops_config = [
        {
            "name": "QuantumLoop",
            "module": "app.autonomous.pipelines.quantum_loop",
            "class": "QuantumLoop",
            "description": "Optimización de circuitos cuánticos variacionales"
        },
        {
            "name": "MathematicsLoop",
            "module": "app.autonomous.pipelines.mathematics_loop",
            "class": "MathematicsLoop",
            "description": "Generación y validación de conjeturas matemáticas"
        },
        {
            "name": "BiologyLoop",
            "module": "app.autonomous.pipelines.biology_loop",
            "class": "BiologyLoop",
            "description": "Análisis genómico con DNABERT2"
        },
        {
            "name": "ChemistryLoop",
            "module": "app.autonomous.pipelines.chemistry_loop",
            "class": "ChemistryLoop",
            "description": "Descubrimiento molecular con RDKit"
        },
        {
            "name": "MaterialsLoop",
            "module": "app.autonomous.pipelines.materials_loop",
            "class": "MaterialsLoop",
            "description": "Predicción de propiedades de materiales"
        },
        {
            "name": "NeuroscienceLoop",
            "module": "app.autonomous.pipelines.neuroscience_loop",
            "class": "NeuroscienceLoop",
            "description": "Simulación de redes neuronales con Brian2"
        },
        {
            "name": "MedicineLoop",
            "module": "app.autonomous.pipelines.medicine_loop",
            "class": "MedicineLoop",
            "description": "Diagnóstico médico con MONAI"
        },
        {
            "name": "AstronomyLoop",
            "module": "app.autonomous.pipelines.astronomy_loop",
            "class": "AstronomyLoop",
            "description": "Análisis de curvas de luz con Lightkurve"
        },
        {
            "name": "EngineeringLoop",
            "module": "app.autonomous.pipelines.engineering_loop",
            "class": "EngineeringLoop",
            "description": "Optimización topológica FEM"
        },
        {
            "name": "ClimateLoop",
            "module": "app.autonomous.pipelines.climate_loop",
            "class": "ClimateLoop",
            "description": "Modelado de anomalías climáticas"
        }
    ]
    
    all_results = []
    successful = 0
    failed = 0
    
    execution_start = time.time()
    
    # Ejecutar cada loop
    for idx, loop_config in enumerate(loops_config, 1):
        print(f"\n{Colors.BOLD}[{idx}/{len(loops_config)}] {loop_config['description']}{Colors.ENDC}")
        
        result = execute_single_loop(
            loop_name=loop_config["name"],
            module_path=loop_config["module"],
            class_name=loop_config["class"]
        )
        
        all_results.append(result)
        
        if result["success"]:
            successful += 1
        else:
            failed += 1
        
        # Pequeña pausa entre loops
        if idx < len(loops_config):
            print(f"\n{Colors.OKCYAN}⏸️  Pausa de 2 segundos antes del siguiente loop...{Colors.ENDC}")
            time.sleep(2)
    
    total_duration = time.time() - execution_start
    
    # Resumen final
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 30 + "📊 RESUMEN FINAL" + " " * 32 + "║")
    print("╚" + "═" * 78 + "╝")
    print(f"{Colors.ENDC}\n")
    
    print(f"{Colors.OKGREEN}✅ Loops exitosos: {successful}/{len(loops_config)}{Colors.ENDC}")
    if failed > 0:
        print(f"{Colors.FAIL}❌ Loops fallidos: {failed}/{len(loops_config)}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}⏱️  Tiempo total: {total_duration:.2f} segundos{Colors.ENDC}")
    
    # Guardar resultados en JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"new_experiments_results_{timestamp}.json"
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump({
            "execution_date": datetime.now().isoformat(),
            "total_duration_seconds": total_duration,
            "successful_loops": successful,
            "failed_loops": failed,
            "total_loops": len(loops_config),
            "results": all_results
        }, f, indent=2, default=str)
    
    print(f"\n{Colors.OKGREEN}📁 Resultados guardados en: {json_filename}{Colors.ENDC}")
    
    # Generar reporte Markdown
    generate_markdown_report(all_results, successful, failed, total_duration, timestamp)
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
    
    return all_results


def generate_markdown_report(results: List[Dict], successful: int, failed: int, 
                            total_duration: float, timestamp: str):
    """
    Genera un reporte detallado en Markdown con los nuevos experimentos.
    """
    md_filename = f"NEW_EXPERIMENTS_REPORT_{timestamp}.md"
    
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write("# 🚀 Nuevos Experimentos - AXIOM ATLAS META 4\n\n")
        f.write(f"**Fecha de ejecución**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 📊 Resumen Ejecutivo\n\n")
        f.write(f"- **Total de loops ejecutados**: {len(results)}\n")
        f.write(f"- **✅ Exitosos**: {successful}\n")
        f.write(f"- **❌ Fallidos**: {failed}\n")
        f.write(f"- **⏱️ Tiempo total**: {total_duration:.2f} segundos\n")
        f.write(f"- **📈 Tasa de éxito**: {(successful/len(results)*100):.1f}%\n\n")
        
        f.write("---\n\n")
        f.write("## 🔬 Resultados Detallados por Loop\n\n")
        
        for idx, result in enumerate(results, 1):
            status_emoji = "✅" if result["success"] else "❌"
            status_text = "ÉXITO" if result["success"] else "FALLO"
            
            f.write(f"### {idx}. {result['loop_name']} {status_emoji}\n\n")
            f.write(f"**Status**: {status_text}\n\n")
            f.write(f"**Duración**: {result['duration_seconds']:.2f} segundos\n\n")
            f.write(f"**Inicio**: {result['start_time']}\n\n")
            f.write(f"**Fin**: {result['end_time']}\n\n")
            
            if result["success"] and result["result"]:
                f.write("#### 📈 Resultados Generados\n\n")
                f.write("```json\n")
                f.write(json.dumps(result["result"], indent=2, default=str))
                f.write("\n```\n\n")
                
                # Análisis de resultados
                res_data = result["result"]
                if isinstance(res_data, dict):
                    f.write("#### 🔍 Análisis\n\n")
                    
                    if 'candidates' in res_data:
                        candidates = res_data['candidates']
                        f.write(f"- **Candidatos generados**: {len(candidates)}\n")
                        if len(candidates) > 0 and isinstance(candidates[0], dict):
                            if 'score' in candidates[0]:
                                scores = [c.get('score', 0) for c in candidates]
                                f.write(f"- **Score promedio**: {sum(scores)/len(scores):.3f}\n")
                                f.write(f"- **Score máximo**: {max(scores):.3f}\n")
                                f.write(f"- **Score mínimo**: {min(scores):.3f}\n")
                    
                    if 'novelty_avg' in res_data:
                        f.write(f"- **Novelty promedio**: {res_data['novelty_avg']:.3f}\n")
                    
                    if 'duration_seconds' in res_data:
                        f.write(f"- **Duración interna**: {res_data['duration_seconds']:.3f}s\n")
                    
                    f.write("\n")
            
            elif result["error"]:
                f.write("#### ❌ Error Encontrado\n\n")
                f.write(f"```\n{result['error']}\n```\n\n")
                
                if result["traceback"]:
                    f.write("<details>\n<summary>📋 Traceback completo</summary>\n\n")
                    f.write(f"```\n{result['traceback']}\n```\n\n")
                    f.write("</details>\n\n")
            
            f.write("---\n\n")
        
        # Conclusiones
        f.write("## 🎯 Conclusiones\n\n")
        
        if successful == len(results):
            f.write("🎉 **¡ÉXITO TOTAL!** Todos los loops ejecutaron correctamente.\n\n")
            f.write("El sistema AXIOM ATLAS META 4 está completamente operacional en los 10 dominios científicos.\n\n")
        elif successful > 0:
            f.write(f"✅ **{successful} loops funcionando correctamente**\n\n")
            f.write(f"⚠️ **{failed} loops requieren atención**\n\n")
        else:
            f.write("⚠️ **Todos los loops fallaron** - Se requiere debugging del sistema.\n\n")
        
        # Próximos pasos
        f.write("## 🚀 Próximos Pasos\n\n")
        
        if successful > 0:
            f.write("1. **Analizar resultados** de los loops exitosos\n")
            f.write("2. **Comparar con literatura** científica\n")
            f.write("3. **Validar hipótesis** generadas\n")
            f.write("4. **Preparar publicación** científica\n")
        
        if failed > 0:
            f.write(f"\n### Debugging requerido para {failed} loops:\n\n")
            for result in results:
                if not result["success"]:
                    f.write(f"- **{result['loop_name']}**: {result['error']}\n")
        
        f.write("\n---\n\n")
        f.write(f"*Generado automáticamente por AXIOM ATLAS META 4 - {timestamp}*\n")
    
    print(f"{Colors.OKGREEN}📄 Reporte Markdown generado: {md_filename}{Colors.ENDC}")


if __name__ == "__main__":
    try:
        results = main()
        sys.exit(0 if all(r["success"] for r in results) else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Ejecución interrumpida por el usuario{Colors.ENDC}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n{Colors.FAIL}❌ Error crítico: {e}{Colors.ENDC}\n")
        traceback.print_exc()
        sys.exit(1)
