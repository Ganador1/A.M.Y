#!/usr/bin/env python3
"""
Análisis Estadístico de Varianza - Loops Autónomos
===================================================

Ejecuta múltiples iteraciones de run_loops_isolated.py y calcula:
- Media ± desviación estándar de support_scores
- Intervalos de confianza (95%)
- Coeficiente de variación
- Comparación con línea base

Uso:
    python analyze_loop_variance.py --runs 5 --baseline isolated_loops_results_20251029_221143.json
"""

import asyncio
import json
import subprocess
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys


class LoopVarianceAnalyzer:
    """Analiza varianza estadística de loops autónomos"""
    
    def __init__(self, num_runs: int = 5, baseline_file: str = None):
        self.num_runs = num_runs
        self.baseline_file = baseline_file
        self.results = []
        self.baseline_data = None
        
    def load_baseline(self):
        """Carga datos de línea base"""
        if self.baseline_file and Path(self.baseline_file).exists():
            with open(self.baseline_file, 'r') as f:
                self.baseline_data = json.load(f)
                print(f"📊 Línea base cargada: {self.baseline_file}")
        else:
            print("⚠️  Sin línea base - solo análisis de varianza")
    
    async def run_single_iteration(self, iteration: int) -> Dict:
        """Ejecuta una iteración de run_loops_isolated.py"""
        print(f"\n{'='*70}")
        print(f"🔬 Ejecución {iteration}/{self.num_runs}")
        print(f"{'='*70}")
        
        start_time = datetime.now()
        
        # Ejecutar script
        try:
            result = subprocess.run(
                ['python3', 'run_loops_isolated.py'],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos max
            )
            
            if result.returncode != 0:
                print(f"❌ Error en ejecución {iteration}")
                print(f"STDERR: {result.stderr[:500]}")
                return None
            
            # Buscar archivo de resultados más reciente
            result_files = sorted(Path('.').glob('isolated_loops_results_*.json'))
            if not result_files:
                print(f"❌ No se encontró archivo de resultados")
                return None
            
            latest_file = result_files[-1]
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ Ejecución {iteration} completada en {elapsed:.1f}s")
            print(f"   Archivo: {latest_file}")
            
            return {
                'iteration': iteration,
                'file': str(latest_file),
                'data': data,
                'elapsed_seconds': elapsed
            }
            
        except subprocess.TimeoutExpired:
            print(f"⏱️  Timeout en ejecución {iteration}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    async def run_all_iterations(self):
        """Ejecuta todas las iteraciones"""
        print(f"\n🚀 Iniciando {self.num_runs} ejecuciones de run_loops_isolated.py")
        print(f"⏱️  Tiempo estimado: {self.num_runs * 9} minutos\n")
        
        for i in range(1, self.num_runs + 1):
            result = await self.run_single_iteration(i)
            if result:
                self.results.append(result)
            
            # Pausa entre ejecuciones
            if i < self.num_runs:
                await asyncio.sleep(2)
        
        print(f"\n✅ Completadas {len(self.results)}/{self.num_runs} ejecuciones exitosas")
    
    def extract_scores(self) -> Dict[str, List[float]]:
        """Extrae support_scores de todas las ejecuciones"""
        scores_by_loop = {}
        
        for result in self.results:
            data = result['data']
            for loop_name, loop_data in data.get('results', {}).items():
                if loop_name not in scores_by_loop:
                    scores_by_loop[loop_name] = []
                
                score = loop_data.get('evidence_support_score', 0.0)
                scores_by_loop[loop_name].append(score)
        
        return scores_by_loop
    
    def calculate_statistics(self, values: List[float]) -> Dict:
        """Calcula estadísticas para una lista de valores"""
        if len(values) < 2:
            return {
                'mean': values[0] if values else 0.0,
                'std': 0.0,
                'cv': 0.0,
                'min': values[0] if values else 0.0,
                'max': values[0] if values else 0.0,
                'ci_95': (0.0, 0.0)
            }
        
        mean = statistics.mean(values)
        std = statistics.stdev(values)
        cv = (std / mean * 100) if mean > 0 else 0.0
        
        # Intervalo de confianza 95% (aproximación t-student)
        margin = 1.96 * (std / (len(values) ** 0.5))
        ci_95 = (mean - margin, mean + margin)
        
        return {
            'mean': mean,
            'std': std,
            'cv': cv,
            'min': min(values),
            'max': max(values),
            'ci_95': ci_95,
            'n': len(values)
        }
    
    def generate_report(self):
        """Genera reporte estadístico completo"""
        scores_by_loop = self.extract_scores()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'num_iterations': len(self.results),
            'baseline_file': self.baseline_file,
            'loops': {},
            'summary': {
                'total_loops': len(scores_by_loop),
                'avg_execution_time': statistics.mean([r['elapsed_seconds'] for r in self.results]),
                'total_time': sum([r['elapsed_seconds'] for r in self.results])
            }
        }
        
        print(f"\n{'='*70}")
        print(f"📊 ANÁLISIS ESTADÍSTICO DE VARIANZA")
        print(f"{'='*70}\n")
        print(f"Iteraciones: {len(self.results)}/{self.num_runs}")
        print(f"Tiempo total: {report['summary']['total_time']:.1f}s ({report['summary']['total_time']/60:.1f} min)")
        print(f"Tiempo promedio: {report['summary']['avg_execution_time']:.1f}s\n")
        
        print(f"{'Loop':<25} {'Media':<10} {'±σ':<10} {'CV%':<8} {'Min':<10} {'Max':<10}")
        print(f"{'-'*80}")
        
        for loop_name in sorted(scores_by_loop.keys()):
            scores = scores_by_loop[loop_name]
            stats = self.calculate_statistics(scores)
            
            report['loops'][loop_name] = {
                'scores': scores,
                'statistics': stats
            }
            
            # Comparación con baseline si existe
            if self.baseline_data:
                baseline_score = self.baseline_data.get('results', {}).get(loop_name, {}).get('evidence_support_score')
                if baseline_score:
                    diff = stats['mean'] - baseline_score
                    diff_pct = (diff / baseline_score * 100) if baseline_score > 0 else 0.0
                    report['loops'][loop_name]['baseline_comparison'] = {
                        'baseline_score': baseline_score,
                        'difference': diff,
                        'difference_pct': diff_pct
                    }
            
            print(f"{loop_name:<25} {stats['mean']:<10.3f} {stats['std']:<10.3f} "
                  f"{stats['cv']:<8.2f} {stats['min']:<10.3f} {stats['max']:<10.3f}")
        
        print(f"{'-'*80}\n")
        
        # Resumen de variabilidad
        all_cvs = [stats['cv'] for stats in [report['loops'][l]['statistics'] for l in report['loops']]]
        avg_cv = statistics.mean(all_cvs)
        
        print(f"📈 Coeficiente de Variación Promedio: {avg_cv:.2f}%")
        
        if avg_cv < 5:
            print(f"   ✅ Excelente consistencia (CV < 5%)")
        elif avg_cv < 10:
            print(f"   ✅ Buena consistencia (CV < 10%)")
        elif avg_cv < 20:
            print(f"   ⚠️  Consistencia moderada (CV < 20%)")
        else:
            print(f"   ❌ Alta variabilidad (CV >= 20%)")
        
        # Comparación con baseline
        if self.baseline_data:
            print(f"\n📊 Comparación con Línea Base:")
            improvements = []
            for loop_name, loop_data in report['loops'].items():
                if 'baseline_comparison' in loop_data:
                    comp = loop_data['baseline_comparison']
                    diff_pct = comp['difference_pct']
                    improvements.append(diff_pct)
                    
                    symbol = "✅" if diff_pct > 0 else "❌" if diff_pct < -5 else "→"
                    print(f"   {symbol} {loop_name}: {diff_pct:+.2f}%")
            
            if improvements:
                avg_improvement = statistics.mean(improvements)
                print(f"\n   Mejora promedio: {avg_improvement:+.2f}%")
        
        # Guardar reporte
        output_file = f"variance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Reporte guardado en: {output_file}")
        
        return report


async def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis de varianza de loops')
    parser.add_argument('--runs', type=int, default=5, help='Número de ejecuciones')
    parser.add_argument('--baseline', type=str, help='Archivo de línea base')
    
    args = parser.parse_args()
    
    analyzer = LoopVarianceAnalyzer(num_runs=args.runs, baseline_file=args.baseline)
    analyzer.load_baseline()
    
    await analyzer.run_all_iterations()
    
    if analyzer.results:
        analyzer.generate_report()
    else:
        print("❌ No se pudieron completar ejecuciones")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
