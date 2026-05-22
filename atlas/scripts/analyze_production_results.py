#!/usr/bin/env python3
"""
Analizador de Resultados de Production Loops
=============================================

Analiza todos los resultados JSON generados por los loops de producción
y genera reportes detallados con métricas, comparaciones y hallazgos.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import defaultdict


class ProductionResultsAnalyzer:
    """Analiza resultados de loops en producción"""
    
    def __init__(self, results_dir: str = "production_results"):
        self.results_dir = Path(results_dir)
        self.results = []
        self.successful_results = []
        self.failed_results = []
        
    def load_all_results(self):
        """Carga todos los archivos JSON de resultados"""
        print(f"\n🔍 Buscando resultados en: {self.results_dir}")
        
        json_files = list(self.results_dir.glob("*Loop_*.json"))
        print(f"   Encontrados: {len(json_files)} archivos\n")
        
        for json_file in sorted(json_files):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    data['_filename'] = json_file.name
                    self.results.append(data)
                    
                    if data.get('success'):
                        self.successful_results.append(data)
                    else:
                        self.failed_results.append(data)
                        
            except Exception as e:
                print(f"   ⚠️  Error leyendo {json_file.name}: {e}")
        
        print(f"   ✅ Exitosos: {len(self.successful_results)}")
        print(f"   ❌ Fallidos: {len(self.failed_results)}")
        print(f"   📊 Total: {len(self.results)}\n")
    
    def generate_summary_report(self) -> str:
        """Genera reporte resumen"""
        lines = []
        lines.append("="*80)
        lines.append("REPORTE RESUMEN - LOOPS EN PRODUCCIÓN")
        lines.append("="*80)
        lines.append("")
        lines.append(f"Timestamp del análisis: {datetime.now().isoformat()}")
        lines.append(f"Total de ejecuciones: {len(self.results)}")
        lines.append(f"Exitosas: {len(self.successful_results)} ({len(self.successful_results)/len(self.results)*100:.1f}%)")
        lines.append(f"Fallidas: {len(self.failed_results)} ({len(self.failed_results)/len(self.results)*100:.1f}%)")
        lines.append("")
        
        # Agrupar por loop
        by_loop = defaultdict(list)
        for r in self.results:
            by_loop[r.get('loop_name', 'Unknown')].append(r)
        
        lines.append("RESULTADOS POR LOOP:")
        lines.append("-" * 80)
        
        for loop_name, loop_results in sorted(by_loop.items()):
            successful = [r for r in loop_results if r.get('success')]
            lines.append(f"\n{loop_name}:")
            lines.append(f"  Ejecuciones: {len(loop_results)}")
            lines.append(f"  Exitosas: {len(successful)}")
            lines.append(f"  Tasa de éxito: {len(successful)/len(loop_results)*100:.1f}%")
            
            if successful:
                # Promediar métricas
                avg_metrics = self._average_metrics(successful)
                if avg_metrics:
                    lines.append(f"  Métricas promedio:")
                    lines.append(f"    Support Score: {avg_metrics['avg_support_score']:.3f}")
                    lines.append(f"    Novedad: {avg_metrics['avg_novelty']:.3f}")
                    lines.append(f"    Seleccionados: {avg_metrics['selected']:.1f}")
                    lines.append(f"    Mutaciones: {avg_metrics['mutations']:.1f}")
                
                # Tiempo promedio
                avg_time = sum(r.get('elapsed_seconds', 0) for r in successful) / len(successful)
                lines.append(f"  Tiempo promedio: {avg_time:.1f}s")
        
        lines.append("")
        return "\n".join(lines)
    
    def generate_ranking_report(self) -> str:
        """Genera reporte de rankings"""
        if not self.successful_results:
            return "No hay resultados exitosos para rankear."
        
        lines = []
        lines.append("="*80)
        lines.append("RANKINGS - TOP RESULTADOS")
        lines.append("="*80)
        lines.append("")
        
        # Top por Support Score
        sorted_by_score = sorted(
            [r for r in self.successful_results if 'metrics' in r],
            key=lambda x: x['metrics'].get('avg_support_score', 0),
            reverse=True
        )
        
        lines.append("🏆 TOP 10 POR SUPPORT SCORE:")
        lines.append("-" * 80)
        for i, r in enumerate(sorted_by_score[:10], 1):
            metrics = r['metrics']
            lines.append(f"{i:2}. {r['loop_name']:20} | "
                        f"Score: {metrics['avg_support_score']:.3f} | "
                        f"Novedad: {metrics['avg_novelty']:.3f} | "
                        f"Seleccionados: {metrics['selected']}")
        
        # Top por Novedad
        sorted_by_novelty = sorted(
            [r for r in self.successful_results if 'metrics' in r],
            key=lambda x: x['metrics'].get('avg_novelty', 0),
            reverse=True
        )
        
        lines.append("")
        lines.append("🆕 TOP 10 POR NOVEDAD:")
        lines.append("-" * 80)
        for i, r in enumerate(sorted_by_novelty[:10], 1):
            metrics = r['metrics']
            lines.append(f"{i:2}. {r['loop_name']:20} | "
                        f"Novedad: {metrics['avg_novelty']:.3f} | "
                        f"Score: {metrics['avg_support_score']:.3f} | "
                        f"Seleccionados: {metrics['selected']}")
        
        # Top por Candidatos Seleccionados
        def get_selected_count(result):
            selected = result['metrics'].get('selected', 0)
            if isinstance(selected, list):
                return len(selected)
            return selected if isinstance(selected, (int, float)) else 0
        
        sorted_by_candidates = sorted(
            [r for r in self.successful_results if 'metrics' in r],
            key=get_selected_count,
            reverse=True
        )
        
        lines.append("")
        lines.append("🎯 TOP 10 POR CANDIDATOS SELECCIONADOS:")
        lines.append("-" * 80)
        for i, r in enumerate(sorted_by_candidates[:10], 1):
            metrics = r['metrics']
            selected = metrics['selected']
            selected_count = len(selected) if isinstance(selected, list) else selected
            lines.append(f"{i:2}. {r['loop_name']:20} | "
                        f"Seleccionados: {selected_count} | "
                        f"Score: {metrics['avg_support_score']:.3f} | "
                        f"Novedad: {metrics['avg_novelty']:.3f}")
        
        lines.append("")
        return "\n".join(lines)
    
    def generate_detailed_report(self) -> str:
        """Genera reporte detallado de cada ejecución exitosa"""
        if not self.successful_results:
            return "No hay resultados exitosos para detallar."
        
        lines = []
        lines.append("="*80)
        lines.append("REPORTE DETALLADO - EJECUCIONES EXITOSAS")
        lines.append("="*80)
        lines.append("")
        
        for i, r in enumerate(self.successful_results, 1):
            lines.append(f"\n{'─'*80}")
            lines.append(f"Ejecución #{i}: {r['loop_name']}")
            lines.append(f"{'─'*80}")
            lines.append(f"Archivo: {r['_filename']}")
            lines.append(f"Timestamp: {r['timestamp']}")
            lines.append(f"Tiempo de ejecución: {r['elapsed_seconds']:.2f}s")
            
            if 'metrics' in r:
                m = r['metrics']
                lines.append(f"\nMétricas:")
                lines.append(f"  Support Score promedio: {m.get('avg_support_score', 0):.3f}")
                lines.append(f"  Novedad promedio: {m.get('avg_novelty', 0):.3f}")
                lines.append(f"  Candidatos seleccionados: {m.get('selected', 0)}")
                lines.append(f"  Mutaciones: {m.get('mutations', 0)}")
            
            # Información del resultado
            if 'result' in r:
                result = r['result']
                if isinstance(result, dict):
                    if 'candidates' in result and isinstance(result['candidates'], list):
                        lines.append(f"\nCandidatos generados: {len(result['candidates'])}")
                        
                        # Mostrar top 3 candidatos
                        sorted_candidates = sorted(
                            result['candidates'],
                            key=lambda x: x.get('support_score', 0),
                            reverse=True
                        )
                        
                        if sorted_candidates:
                            lines.append("\nTop 3 Candidatos:")
                            for j, cand in enumerate(sorted_candidates[:3], 1):
                                lines.append(f"  {j}. Score: {cand.get('support_score', 0):.3f} | "
                                           f"Novedad: {cand.get('novelty', 0):.3f}")
                                if 'description' in cand:
                                    desc = cand['description'][:100]
                                    lines.append(f"     Descripción: {desc}...")
        
        lines.append("\n")
        return "\n".join(lines)
    
    def _average_metrics(self, results: List[Dict]) -> Dict:
        """Calcula promedio de métricas"""
        metrics_list = [r['metrics'] for r in results if 'metrics' in r]
        
        if not metrics_list:
            return {}
        
        avg = {
            'avg_support_score': sum(m.get('avg_support_score', 0) for m in metrics_list) / len(metrics_list),
            'avg_novelty': sum(m.get('avg_novelty', 0) for m in metrics_list) / len(metrics_list),
            'selected': sum(
                len(m.get('selected', [])) if isinstance(m.get('selected'), list) else m.get('selected', 0)
                for m in metrics_list
            ) / len(metrics_list),
            'mutations': sum(
                len(m.get('mutations', [])) if isinstance(m.get('mutations'), list) else m.get('mutations', 0)
                for m in metrics_list
            ) / len(metrics_list),
        }
        
        return avg
    
    def save_reports(self):
        """Genera y guarda todos los reportes"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Reporte resumen
        summary = self.generate_summary_report()
        summary_file = self.results_dir / f"analysis_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)
        print(f"💾 Resumen guardado: {summary_file}")
        print(summary)
        print()
        
        # Reporte de rankings
        ranking = self.generate_ranking_report()
        ranking_file = self.results_dir / f"analysis_ranking_{timestamp}.txt"
        with open(ranking_file, 'w') as f:
            f.write(ranking)
        print(f"💾 Rankings guardados: {ranking_file}")
        print(ranking)
        print()
        
        # Reporte detallado
        detailed = self.generate_detailed_report()
        detailed_file = self.results_dir / f"analysis_detailed_{timestamp}.txt"
        with open(detailed_file, 'w') as f:
            f.write(detailed)
        print(f"💾 Detallado guardado: {detailed_file}")


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analizar resultados de loops en producción')
    parser.add_argument('--dir', type=str, default='production_results',
                       help='Directorio de resultados')
    
    args = parser.parse_args()
    
    analyzer = ProductionResultsAnalyzer(results_dir=args.dir)
    analyzer.load_all_results()
    
    if not analyzer.results:
        print("❌ No se encontraron resultados para analizar")
        sys.exit(1)
    
    analyzer.save_reports()


if __name__ == "__main__":
    main()
