#!/usr/bin/env python3
"""
Ejecución Simplificada de Loops en Producción
==============================================

Ejecuta loops individuales sin generador de hipótesis complejo.
Usa configuración directa para validar servicios científicos reales.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleLoopRunner:
    """Ejecutor simplificado de loops"""
    
    AVAILABLE_LOOPS = {
        'quantum': {
            'name': 'QuantumLoop',
            'module': 'app.autonomous.pipelines.quantum_loop',
            'description': 'Quantum computing research'
        },
        'biology': {
            'name': 'BiologyLoop',
            'module': 'app.autonomous.pipelines.biology_loop',
            'description': 'Biological systems research'
        },
        'chemistry': {
            'name': 'ChemistryLoop',
            'module': 'app.autonomous.pipelines.chemistry_loop',
            'description': 'Chemical research'
        },
        'materials': {
            'name': 'MaterialsLoop',
            'module': 'app.autonomous.pipelines.materials_loop',
            'description': 'Materials discovery'
        },
        'mathematics': {
            'name': 'MathematicsLoop',
            'module': 'app.autonomous.pipelines.mathematics_loop',
            'description': 'Mathematical research'
        },
        # === NUEVOS: 5 Loops Restantes (Tarea 3) ===
        'neuroscience': {
            'name': 'NeuroscienceLoop',
            'module': 'app.autonomous.pipelines.neuroscience_loop',
            'description': 'Brain and neural systems research'
        },
        'climate': {
            'name': 'ClimateLoop',
            'module': 'app.autonomous.pipelines.climate_loop',
            'description': 'Climate science and modeling'
        },
        'engineering': {
            'name': 'EngineeringLoop',
            'module': 'app.autonomous.pipelines.engineering_loop',
            'description': 'Engineering design and optimization'
        },
        'medicine': {
            'name': 'MedicineLoop',
            'module': 'app.autonomous.pipelines.medicine_loop',
            'description': 'Medical research and drug discovery'
        },
        'astronomy': {
            'name': 'AstronomyLoop',
            'module': 'app.autonomous.pipelines.astronomy_loop',
            'description': 'Astronomy and astrophysics research'
        }
    }
    
    def __init__(self, output_dir: str = "production_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def run_loop(self, loop_key: str) -> Dict:
        """Ejecuta un loop específico"""
        if loop_key not in self.AVAILABLE_LOOPS:
            raise ValueError(f"Loop '{loop_key}' no disponible")
        
        loop_info = self.AVAILABLE_LOOPS[loop_key]
        loop_name = loop_info['name']
        
        print(f"\n{'='*80}")
        print(f"🚀 EJECUTANDO: {loop_name}")
        print(f"📝 {loop_info['description']}")
        print(f"{'='*80}\n")
        
        start_time = datetime.now()
        
        try:
            # Importar módulo
            import importlib
            module = importlib.import_module(loop_info['module'])
            loop_class = getattr(module, loop_name)
            
            # Crear instancia
            loop_instance = loop_class()
            
            print("✅ Loop inicializado")
            print("🔬 Ejecutando iteración...\n")
            
            # Ejecutar de forma SÍNCRONA (los loops ya manejan su propia async internamente)
            # Cada loop tiene su propia firma de run_iteration
            if loop_name == 'QuantumLoop':
                # Patrón A: run_iteration(iteration: int, limit: Optional[int])
                result = loop_instance.run_iteration(iteration=1, limit=10)
            elif loop_name == 'MaterialsLoop':
                # Patrón B: run_iteration(iteration: int, iteration_data: Optional[Dict])
                result = loop_instance.run_iteration(iteration=1)
            elif loop_name == 'MathematicsLoop':
                # Patrón C: run_iteration(iteration: int, limit: int, domain: Optional[str])
                result = loop_instance.run_iteration(iteration=1, limit=10)
            else:
                # Patrón D: run_iteration(top_n: int, iteration_data: Optional[Dict])
                # BiologyLoop, ChemistryLoop, NeuroscienceLoop, ClimateLoop, EngineeringLoop, MedicineLoop, AstronomyLoop
                result = loop_instance.run_iteration(top_n=10)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # Compilar output
            output = {
                'loop_name': loop_name,
                'loop_key': loop_key,
                'description': loop_info['description'],
                'timestamp': datetime.now().isoformat(),
                'elapsed_seconds': elapsed,
                'success': True,
                'result': result
            }
            
            # Extraer métricas
            if isinstance(result, dict):
                output['metrics'] = {
                    'selected': result.get('selected', 0),
                    'mutations': result.get('mutations', 0),
                    'avg_support_score': result.get('avg_support_score', 0.0),
                    'avg_novelty': result.get('avg_novelty', 0.0)
                }
            
            print(f"\n✅ COMPLETADO en {elapsed:.1f}s")
            if 'metrics' in output:
                print(f"   📊 Support Score: {output['metrics']['avg_support_score']:.3f}")
                print(f"   🆕 Novedad: {output['metrics']['avg_novelty']:.3f}")
                print(f"   🎯 Seleccionados: {output['metrics']['selected']}")
                print(f"   🔄 Mutaciones: {output['metrics']['mutations']}")
            
            return output
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error en {loop_name}: {e}", exc_info=True)
            
            return {
                'loop_name': loop_name,
                'loop_key': loop_key,
                'timestamp': datetime.now().isoformat(),
                'elapsed_seconds': elapsed,
                'success': False,
                'error': str(e)
            }
    
    def run_all_loops(self) -> Dict:
        """Ejecuta todos los loops disponibles"""
        print(f"\n{'='*80}")
        print("🌟 EJECUCIÓN DE TODOS LOS LOOPS")
        print(f"{'='*80}")
        print(f"\nLoops disponibles: {len(self.AVAILABLE_LOOPS)}")
        print(f"Timestamp: {self.timestamp}\n")
        
        results = []
        successful = 0
        failed = 0
        
        for loop_key in self.AVAILABLE_LOOPS.keys():
            result = self.run_loop(loop_key)
            results.append(result)
            
            if result.get('success'):
                successful += 1
            else:
                failed += 1
            
            # Guardar resultado individual
            filename = f"{result['loop_name']}_{self.timestamp}.json"
            self._save_result(result, filename)
            
            # Pausa entre loops
            import time
            time.sleep(2)
        
        # Compilar resumen
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_loops': len(self.AVAILABLE_LOOPS),
            'successful': successful,
            'failed': failed,
            'success_rate': successful / len(self.AVAILABLE_LOOPS),
            'results': results
        }
        
        # Guardar resumen
        summary_file = f"production_summary_{self.timestamp}.json"
        self._save_result(summary, summary_file)
        
        # Imprimir resumen
        self._print_summary(summary)
        
        return summary
    
    def _save_result(self, result: Dict, filename: str):
        """Guarda resultado en JSON"""
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"💾 Guardado: {filepath}")
    
    def _print_summary(self, summary: Dict):
        """Imprime resumen ejecutivo"""
        print(f"\n{'='*80}")
        print("📊 RESUMEN EJECUTIVO")
        print(f"{'='*80}")
        print(f"\nTotal: {summary['total_loops']}")
        print(f"✅ Exitosos: {summary['successful']}")
        print(f"❌ Fallidos: {summary['failed']}")
        print(f"📈 Tasa: {summary['success_rate']*100:.1f}%\n")
        
        # Top loops por score
        successful = [r for r in summary['results'] if r.get('success') and 'metrics' in r]
        if successful:
            sorted_by_score = sorted(
                successful,
                key=lambda x: x['metrics'].get('avg_support_score', 0),
                reverse=True
            )
            
            print("🏆 Top por Support Score:")
            for i, r in enumerate(sorted_by_score[:5], 1):
                print(f"   {i}. {r['loop_name']}: {r['metrics']['avg_support_score']:.3f}")
            
            sorted_by_novelty = sorted(
                successful,
                key=lambda x: x['metrics'].get('avg_novelty', 0),
                reverse=True
            )
            
            print("\n🆕 Top por Novedad:")
            for i, r in enumerate(sorted_by_novelty[:5], 1):
                print(f"   {i}. {r['loop_name']}: {r['metrics']['avg_novelty']:.3f}")
        
        print(f"\n{'='*80}\n")


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ejecutar loops en producción')
    parser.add_argument('--loop', type=str, help='Loop a ejecutar (quantum, biology, chemistry, materials, mathematics)')
    parser.add_argument('--all', action='store_true', help='Ejecutar todos los loops')
    parser.add_argument('--list', action='store_true', help='Listar loops disponibles')
    
    args = parser.parse_args()
    
    runner = SimpleLoopRunner()
    
    if args.list:
        print("\n📋 Loops disponibles:\n")
        for key, info in runner.AVAILABLE_LOOPS.items():
            print(f"  {key:15} → {info['name']:20} - {info['description']}")
        print()
        return
    
    if args.all:
        runner.run_all_loops()
    elif args.loop:
        result = runner.run_loop(args.loop)
        filename = f"{result['loop_name']}_{runner.timestamp}.json"
        runner._save_result(result, filename)
    else:
        print("❌ Usa --loop NOMBRE, --all, o --list")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
