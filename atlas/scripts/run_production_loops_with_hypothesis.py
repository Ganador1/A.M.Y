#!/usr/bin/env python3
"""
Ejecución de Loops en Producción con Generación de Hipótesis
=============================================================

Ejecuta cada loop autónomo individualmente con:
- Generación de hipótesis científicas novedosas
- Validación con servicios reales (SciPy, Scikit, Matplotlib)
- Reportes detallados por loop
- Métricas de novedad y support_score

Uso:
    python run_production_loops_with_hypothesis.py --loop QuantumLoop
    python run_production_loops_with_hypothesis.py --all
"""

import asyncio
import json
import sys
import inspect
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionLoopRunner:
    """Ejecutor de loops en producción con generación de hipótesis"""
    
    AVAILABLE_LOOPS = [
        'QuantumLoop',
        'BiologyLoop',
        'ChemistryLoop',
        'MathematicsLoop',
        'NeuroscienceLoop',
        'MaterialsLoop',
        'ClimateLoop',
        'EngineeringLoop',
        'MedicineLoop',
        'AstronomyLoop'
    ]
    
    # Research questions específicas por dominio (FIX #1)
    DOMAIN_RESEARCH_QUESTIONS = {
        'quantum_physics': 'Investigate quantum entanglement dynamics in superconducting qubits using quantum simulation',
        'biology': 'Investigate CD8+ T cell activation dynamics and phosphorylation pathways using proteomics and single-cell analysis',
        'chemistry': 'Design novel catalysts for CO2 reduction using computational chemistry and machine learning',
        'mathematics': 'Explore convergence properties of optimization algorithms in high-dimensional spaces',
        'neuroscience': 'Analyze synaptic plasticity mechanisms in hippocampal neurons using patch-clamp electrophysiology',
        'materials_science': 'Discover novel battery materials with high energy density using crystal structure prediction',
        'climate_science': 'Model feedback mechanisms in Arctic climate systems using coupled ocean-atmosphere models',
        'engineering': 'Optimize structural design for additive manufacturing using topology optimization',
        'medicine': 'Identify biomarkers for early cancer detection using multi-omics data integration',
        'astronomy': 'Characterize exoplanet atmospheres using transit spectroscopy and radiative transfer models'
    }
    
    # Keywords por dominio científico (reutilizados de v3.3)
    DOMAIN_KEYWORDS = {
        'quantum_physics': [
            'qubit', 'entanglement', 'superposition', 'decoherence', 'quantum', 
            'hamiltonian', 'eigenstate', 'measurement', 'wavefunction', 'operator'
        ],
        'biology': [
            'gene', 'protein', 'DNA', 'RNA', 'genome', 'mutation', 'expression',
            'cellular', 'pathway', 'enzyme', 'metabolism', 'transcription'
        ],
        'chemistry': [
            'molecule', 'reaction', 'synthesis', 'catalyst', 'bond', 'structure',
            'spectroscopy', 'compound', 'electron', 'orbital', 'energy'
        ],
        'mathematics': [
            'theorem', 'proof', 'lemma', 'convergence', 'topology', 'algebra',
            'differential', 'integral', 'matrix', 'optimization', 'eigenvalue'
        ],
        'neuroscience': [
            'neuron', 'synapse', 'neural', 'plasticity', 'hippocampus', 'cortex',
            'neurotransmitter', 'dendrite', 'axon', 'receptor', 'potential'
        ],
        'materials_science': [
            'crystal', 'lattice', 'phase', 'defect', 'microstructure', 'alloy',
            'composite', 'mechanical', 'thermal', 'electronic', 'properties'
        ],
        'climate_science': [
            'temperature', 'precipitation', 'carbon', 'emission', 'atmosphere',
            'ocean', 'glacier', 'feedback', 'forcing', 'climate', 'model'
        ],
        'engineering': [
            'design', 'optimization', 'system', 'control', 'efficiency', 'load',
            'stress', 'material', 'fabrication', 'testing', 'performance'
        ],
        'medicine': [
            'patient', 'diagnosis', 'treatment', 'therapy', 'clinical', 'drug',
            'disease', 'symptom', 'biomarker', 'trial', 'outcome'
        ],
        'astronomy': [
            'star', 'galaxy', 'nebula', 'planet', 'orbit', 'luminosity',
            'spectrum', 'redshift', 'magnitude', 'telescope', 'observation'
        ],
        'general': [
            'hypothesis', 'experiment', 'data', 'analysis', 'method', 'result',
            'theory', 'model', 'measurement', 'error', 'significance'
        ]
    }
    
    def __init__(self, output_dir: str = "production_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    async def generate_hypothesis(self, domain: str) -> Dict:
        """Genera hipótesis científica usando el generador"""
        print(f"\n🧠 Generando hipótesis para {domain}...")
        
        try:
            from app.autonomous.generators.hypothesis_generator import HypothesisGenerator
            
            generator = HypothesisGenerator()
            
            # Mapear loops a dominios
            domain_map = {
                'QuantumLoop': 'quantum_physics',
                'BiologyLoop': 'biology',
                'ChemistryLoop': 'chemistry',
                'MathematicsLoop': 'mathematics',
                'NeuroscienceLoop': 'neuroscience',
                'MaterialsLoop': 'materials_science',
                'ClimateLoop': 'climate_science',
                'EngineeringLoop': 'engineering',
                'MedicineLoop': 'medicine',
                'AstronomyLoop': 'astronomy'
            }
            
            domain_name = domain_map.get(domain, 'general')
            
            # FIX #1: Obtener research_question específica del dominio
            research_question = self.DOMAIN_RESEARCH_QUESTIONS.get(domain_name)
            
            print(f"   🔍 Research question: {research_question[:80] if research_question else 'N/A'}...")
            
            # Generar hipótesis con literatura search (Fase 4) + research_question (FIX #1)
            hypothesis = await generator.generate_hypothesis(
                domain=domain_name,
                context={
                    'mode': 'production',
                    'use_real_services': True,
                    'novelty_threshold': 0.7,
                    'require_evidence': True,
                    'enable_literature_search': True,  # ← FASE 4: Literatura search habilitado
                    'literature_year': 2024,
                    'literature_limit': 20,
                    'research_question': research_question  # ← FIX #1: Research question específica
                }
            )
            
            print("   ✅ Hipótesis generada:")
            print(f"      Título: {hypothesis.get('title', 'N/A')[:80]}...")
            print(f"      Novedad: {hypothesis.get('novelty_score', 0.0):.3f}")
            
            return hypothesis
            
        except Exception as e:
            logger.error(f"Error generando hipótesis: {e}")
            return {
                'title': f'Exploración autónoma en {domain}',
                'description': f'Investigación dirigida por IA en {domain}',
                'novelty_score': 0.5,
                'error': str(e)
            }
    
    async def run_single_loop(self, loop_name: str) -> Dict:
        """Ejecuta un loop individual con hipótesis"""
        print(f"\n{'='*80}")
        print(f"🚀 EJECUTANDO LOOP EN PRODUCCIÓN: {loop_name}")
        print(f"{'='*80}")
        
        start_time = datetime.now()
        
        # 1. Generar hipótesis
        hypothesis = await self.generate_hypothesis(loop_name)
        
        # 2. Ejecutar loop
        print("\n🔬 Ejecutando loop con hipótesis...")
        
        try:
            # Importar el loop específico
            loop_module = self._import_loop(loop_name)
            
            if loop_module:
                # Crear instancia del loop
                loop_instance = loop_module()
                
                # Ejecutar respetando la firma del método y si es sync/async
                run_method = getattr(loop_instance, "run_iteration", None)
                if run_method is None:
                    raise AttributeError(f"{loop_name} no tiene método run_iteration")

                params = inspect.signature(run_method).parameters
                call_kwargs = {}
                # Intentar rellenar argumentos comunes sin romper firmas existentes
                if "iteration" in params:
                    call_kwargs["iteration"] = 1
                if "iteration_data" in params:
                    call_kwargs["iteration_data"] = {"candidate_count": 10}
                if "limit" in params:
                    call_kwargs["limit"] = 10
                if "production_mode" in params:
                    call_kwargs["production_mode"] = True
                if "hypothesis" in params:
                    call_kwargs["hypothesis"] = hypothesis

                if inspect.iscoroutinefunction(run_method):
                    result = await run_method(**call_kwargs)
                else:
                    # Ejecutar función síncrona en hilo para no bloquear el bucle si fuera costosa
                    result = await asyncio.to_thread(run_method, **call_kwargs)
                
                elapsed = (datetime.now() - start_time).total_seconds()
                
                # Compilar resultados
                # FIX: Usar validated_novelty de hypothesis (TF-IDF) si existe
                hypothesis_novelty = hypothesis.get('validated_novelty', hypothesis.get('novelty_score', 0.0))
                
                output = {
                    'loop_name': loop_name,
                    'timestamp': datetime.now().isoformat(),
                    'elapsed_seconds': elapsed,
                    'hypothesis': hypothesis,
                    'result': result,
                    'success': result.get('success', False),
                    'metrics': {
                        'avg_support_score': result.get('avg_support_score', 0.0),
                        'avg_novelty': result.get('avg_novelty', 0.0),
                        'validated_novelty': hypothesis_novelty,  # ⭐ NUEVO: Novedad validada por LLM/TF-IDF
                        # Compatibilidad con diferentes estructuras de retorno
                        'selected_count': (
                            result.get('selected', 0)
                            if isinstance(result.get('selected'), (int, float))
                            else len(result.get('selected', []))
                        ),
                        'mutations': (
                            result.get('mutations', 0)
                            if isinstance(result.get('mutations'), (int, float))
                            else len(result.get('mutations', []))
                        )
                    }
                }
                
                # 3. Post-proceso: Peer Review y Publicación (opción B)
                try:
                    print("\n📖 Generando peer review...")
                    peer_review = await self._generate_peer_review(loop_name, hypothesis, output)
                    print(f"   ✅ Review: {peer_review.get('length', 0)} caracteres")
                    
                    print("📄 Generando publicación...")
                    publication = await self._generate_publication(loop_name, hypothesis, peer_review, output)
                    print(f"   ✅ Paper: {publication.get('word_count', 0)} palabras")
                    
                    # Calcular keyword coverage
                    keywords = self._get_domain_keywords(loop_name)
                    coverage, keywords_found = self._calculate_keyword_coverage(
                        publication.get('text', ''), 
                        keywords
                    )
                    publication['keyword_coverage'] = coverage
                    publication['keywords_found'] = keywords_found
                    print(f"   📊 Keyword coverage: {coverage:.1%} ({len(keywords_found)}/{len(keywords)})")
                    
                    # Mejorar publicación con referencias y estadísticas
                    print("🚀 Mejorando publicación...")
                    publication = await self._enhance_publication(publication, loop_name, output)
                    if publication.get('enhanced'):
                        print(f"   ✨ Referencias: {publication.get('references_count', 0)}")
                        print(f"   ✨ Mejoras: {len(publication.get('improvements', []))}")
                    
                    output['peer_review'] = peer_review
                    output['publication'] = publication
                    
                except Exception as post_exc:
                    logger.error(f"Post-proceso (peer review/publication) falló: {post_exc}")
                    output['post_processing_error'] = str(post_exc)

                print(f"\n✅ Loop completado en {elapsed:.1f}s")
                print(f"   📊 Support Score: {output['metrics']['avg_support_score']:.3f}")
                print(f"   🆕 Novedad: {output['metrics']['avg_novelty']:.3f}")
                print(f"   🎯 Candidatos: {output['metrics']['selected_count']}")
                
                if 'publication' in output:
                    pub = output['publication']
                    print(f"   📝 Paper: {pub.get('word_count', 0)} palabras")
                    if 'keyword_coverage' in pub:
                        print(f"   🔍 Keywords: {pub['keyword_coverage']:.1%}")
                    if pub.get('enhanced'):
                        print(f"   ✨ Referencias: {pub.get('references_count', 0)}")
                
                return output
                
            else:
                raise ImportError(f"No se pudo importar {loop_name}")
                
        except Exception as e:
            logger.error(f"Error ejecutando {loop_name}: {e}")
            elapsed = (datetime.now() - start_time).total_seconds()
            
            return {
                'loop_name': loop_name,
                'timestamp': datetime.now().isoformat(),
                'elapsed_seconds': elapsed,
                'hypothesis': hypothesis,
                'success': False,
                'error': str(e),
                'traceback': None  # Podríamos agregar traceback si es necesario
            }

    async def _generate_peer_review(self, loop_name: str, hypothesis: Dict, output: Dict) -> Dict:
        """Genera un peer review usando el agente de reviewer (HuggingFace/Hybrid)."""
        try:
            from app.services.huggingface_agent_wrapper import create_agent_wrapper
        except Exception as e:
            logger.error(f"No se pudo importar create_agent_wrapper: {e}")
            return {"text": "", "length": 0, "error": str(e)}

        domain = hypothesis.get('domain', 'general')
        # Usar hybrid para fallback a Ollama si HF falla
        reviewer = create_agent_wrapper(agent_role="reviewer", provider="hybrid", domain=domain)
        hyp_text = hypothesis.get('description') or hypothesis.get('title', '')
        tools_info = output.get('metrics', {})
        
        # FIX: Usar validated_novelty de hypothesis (TF-IDF) en lugar de avg_novelty de metrics (candidatos)
        hypothesis_novelty = hypothesis.get('validated_novelty', hypothesis.get('novelty_score', 0.0))

        review_prompt = (
            f"Conduct a rigorous peer review for the following hypothesis in {domain}:\n\n"
            f"Title: {hypothesis.get('title','N/A')}\n"
            f"Hypothesis: {hyp_text[:600]}...\n\n"
            f"Evidence summary: support_score={tools_info.get('avg_support_score',0):.3f},"
            f" novelty={hypothesis_novelty:.3f}, selected={tools_info.get('selected_count',0)}\n\n"
            "Evaluate rigor, novelty, methodology, computational validation, clarity, and give an overall recommendation."
        )

        # Hybrid wrapper tiene generate (sync) que maneja async internamente o generate_async?
        # Revisando el código de HybridAgentWrapper, tiene generate() pero no generate_async() explícito que haga fallback
        # Espera, HybridAgentWrapper.generate es sync pero llama a hf_wrapper.generate (sync wrapper)
        # Si queremos async, deberíamos verificar si Hybrid soporta async.
        # El código de HybridAgentWrapper mostrado anteriormente solo tenía generate() sync.
        # Vamos a usar generate() sync envuelto en to_thread para no bloquear, o usar generate() directo si es rápido.
        # Dado que generate() de HF wrapper ya hace run_until_complete, es bloqueante.
        # Mejor lo ejecutamos en un thread.
        
        if hasattr(reviewer, 'generate_async'):
            review_text = await reviewer.generate_async(review_prompt)
        else:
            review_text = await asyncio.to_thread(reviewer.generate, review_prompt)
            
        review_text = review_text if isinstance(review_text, str) else str(review_text)
        return {"text": review_text, "length": len(review_text)}

    async def _generate_publication(self, loop_name: str, hypothesis: Dict, peer_review: Dict, output: Dict) -> Dict:
        """Genera un borrador de artículo usando el agente de publicación (HuggingFace/Hybrid)."""
        try:
            from app.services.huggingface_agent_wrapper import create_agent_wrapper
        except Exception as e:
            logger.error(f"No se pudo importar create_agent_wrapper: {e}")
            return {"text": "", "word_count": 0, "error": str(e)}

        domain = hypothesis.get('domain', 'general')
        # Usar hybrid para fallback a Ollama si HF falla
        publisher = create_agent_wrapper(agent_role="publisher", provider="hybrid", domain=domain)
        hyp_text = hypothesis.get('description') or hypothesis.get('title', '')
        tools_info = output.get('metrics', {})
        review_snippet = (peer_review or {}).get('text', '')[:400]

        publication_prompt = (
            f"Write a concise research paper draft for domain {domain}.\n\n"
            f"Title: {hypothesis.get('title','N/A')}\n\n"
            f"Hypothesis: {hyp_text[:500]}...\n\n"
            f"Evidence summary: support_score={tools_info.get('avg_support_score',0):.3f},"
            f" novelty={tools_info.get('avg_novelty',0):.3f}, candidates={tools_info.get('selected_count',0)}\n\n"
            f"Peer review (excerpt): {review_snippet}\n\n"
            "Structure: Abstract, Introduction, Methods, Results, Discussion, References."
        )

        paper_text = await asyncio.to_thread(publisher.generate, publication_prompt)
        if hasattr(publisher, 'generate_async'):
            paper_text = await publisher.generate_async(publication_prompt)
        else:
            paper_text = await asyncio.to_thread(publisher.generate, publication_prompt)
            
        paper_text = paper_text if isinstance(paper_text, str) else str(paper_text)
        return {"text": paper_text, "word_count": len(paper_text.split())}
    
    def _get_domain_keywords(self, loop_name: str) -> List[str]:
        """Obtiene keywords del dominio basado en el nombre del loop"""
        # Mapear loop a dominio
        domain_map = {
            'QuantumLoop': 'quantum_physics',
            'BiologyLoop': 'biology',
            'ChemistryLoop': 'chemistry',
            'MathematicsLoop': 'mathematics',
            'NeuroscienceLoop': 'neuroscience',
            'MaterialsLoop': 'materials_science',
            'ClimateLoop': 'climate_science',
            'EngineeringLoop': 'engineering',
            'MedicineLoop': 'medicine',
            'AstronomyLoop': 'astronomy'
        }
        
        domain = domain_map.get(loop_name, 'general')
        return self.DOMAIN_KEYWORDS.get(domain, self.DOMAIN_KEYWORDS['general'])
    
    def _calculate_keyword_coverage(self, paper_text: str, keywords: List[str]) -> Tuple[float, List[str]]:
        """Calcula cobertura de keywords en el paper"""
        paper_lower = paper_text.lower()
        keywords_found = [kw for kw in keywords if kw.lower() in paper_lower]
        coverage = len(keywords_found) / len(keywords) if keywords else 0.0
        return coverage, keywords_found
    
    async def _enhance_publication(self, publication: Dict, loop_name: str, output: Dict) -> Dict:
        """Mejora la publicación con referencias y análisis estadístico (estilo v3.3)"""
        paper_text = publication.get('text', '')
        
        if not paper_text:
            return publication
        
        try:
            from app.services.paper_enhancement import enhance_pipeline_paper
            
            # Preparar tool_evidence en formato Dict (convertir si es necesario)
            tool_evidence = output.get('result', {})
            if not isinstance(tool_evidence, dict):
                tool_evidence = {'raw_result': tool_evidence}
            
            # Aplicar mejoras
            enhancement_result = enhance_pipeline_paper(
                paper_text=paper_text,
                tool_evidence=tool_evidence,
                domain=self._get_domain_from_loop(loop_name),
                include_discussion=True,
                citation_style="APA"
            )
            
            # Actualizar publicación con paper mejorado
            publication['text'] = enhancement_result.get('enhanced_paper', paper_text)
            publication['word_count'] = len(publication['text'].split())
            publication['references_count'] = enhancement_result.get('references_count', 0)
            publication['improvements'] = enhancement_result.get('improvements', [])
            publication['enhanced'] = True
            
            logger.info(f"✨ Paper mejorado: {publication['references_count']} referencias, {len(publication['improvements'])} mejoras")
            
        except Exception as e:
            logger.warning(f"⚠️ Error mejorando publicación: {e}")
            publication['enhanced'] = False
            publication['enhancement_error'] = str(e)
        
        return publication
    
    def _get_domain_from_loop(self, loop_name: str) -> str:
        """Obtiene el nombre del dominio científico desde el nombre del loop"""
        domain_map = {
            'QuantumLoop': 'physics',
            'BiologyLoop': 'biology',
            'ChemistryLoop': 'chemistry',
            'MathematicsLoop': 'mathematics',
            'NeuroscienceLoop': 'neuroscience',
            'MaterialsLoop': 'materials_science',
            'ClimateLoop': 'climate',
            'EngineeringLoop': 'engineering',
            'MedicineLoop': 'medicine',
            'AstronomyLoop': 'astronomy'
        }
        return domain_map.get(loop_name, 'general')
    
    def _import_loop(self, loop_name: str):
        """Importa dinámicamente el módulo del loop"""
        try:
            # Mapeo de nombres a módulos
            loop_map = {
                'QuantumLoop': 'app.autonomous.pipelines.quantum_loop',
                'BiologyLoop': 'app.autonomous.pipelines.biology_loop',
                'ChemistryLoop': 'app.autonomous.pipelines.chemistry_loop',
                'MathematicsLoop': 'app.autonomous.pipelines.mathematics_loop',
                'NeuroscienceLoop': 'app.autonomous.pipelines.neuroscience_loop',
                'MaterialsLoop': 'app.autonomous.pipelines.materials_loop',
                'ClimateLoop': 'app.autonomous.pipelines.climate_loop',
                'EngineeringLoop': 'app.autonomous.pipelines.engineering_loop',
                'MedicineLoop': 'app.autonomous.pipelines.medicine_loop',
                'AstronomyLoop': 'app.autonomous.pipelines.astronomy_loop'
            }
            
            module_path = loop_map.get(loop_name)
            if not module_path:
                logger.error(f"Loop {loop_name} no encontrado en el mapeo")
                return None
            
            import importlib
            module = importlib.import_module(module_path)
            
            # Obtener la clase del loop
            loop_class = getattr(module, loop_name)
            return loop_class
            
        except Exception as e:
            logger.error(f"Error importando {loop_name}: {e}")
            return None
    
    async def run_all_loops(self):
        """Ejecuta todos los loops disponibles"""
        print(f"\n{'='*80}")
        print("🌟 EJECUCIÓN DE TODOS LOS LOOPS EN PRODUCCIÓN")
        print(f"{'='*80}")
        print(f"\nLoops a ejecutar: {len(self.AVAILABLE_LOOPS)}")
        print(f"Timestamp: {self.timestamp}\n")
        
        results = []
        successful = 0
        failed = 0
        
        for loop_name in self.AVAILABLE_LOOPS:
            result = await self.run_single_loop(loop_name)
            results.append(result)
            
            if result.get('success'):
                successful += 1
            else:
                failed += 1
            
            # Guardar resultado individual
            self._save_result(result, f"{loop_name}_{self.timestamp}.json")
            
            # Pausa entre loops
            await asyncio.sleep(2)
        
        # Compilar resumen
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_loops': len(self.AVAILABLE_LOOPS),
            'successful': successful,
            'failed': failed,
            'success_rate': successful / len(self.AVAILABLE_LOOPS) if self.AVAILABLE_LOOPS else 0,
            'results': results
        }
        
        # Guardar resumen
        summary_file = f"production_summary_{self.timestamp}.json"
        self._save_result(summary, summary_file)
        
        # Imprimir resumen
        self._print_summary(summary)
        
        return summary
    
    def _save_result(self, result: Dict, filename: str):
        """Guarda resultado en archivo JSON"""
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"💾 Resultado guardado: {filepath}")
    
    def _print_summary(self, summary: Dict):
        """Imprime resumen ejecutivo"""
        print(f"\n{'='*80}")
        print("📊 RESUMEN EJECUTIVO")
        print(f"{'='*80}")
        print(f"\nTotal loops ejecutados: {summary['total_loops']}")
        print(f"✅ Exitosos: {summary['successful']}")
        print(f"❌ Fallidos: {summary['failed']}")
        print(f"📈 Tasa de éxito: {summary['success_rate']*100:.1f}%\n")
        
        # Top 5 por support score
        successful_results = [r for r in summary['results'] if r.get('success')]
        if successful_results:
            sorted_by_score = sorted(
                successful_results,
                key=lambda x: x.get('metrics', {}).get('avg_support_score', 0),
                reverse=True
            )
            
            print("🏆 Top 5 por Support Score:")
            for i, result in enumerate(sorted_by_score[:5], 1):
                print(f"   {i}. {result['loop_name']}: "
                      f"{result['metrics']['avg_support_score']:.3f}")
        
        # Top 5 por novedad
        if successful_results:
            sorted_by_novelty = sorted(
                successful_results,
                key=lambda x: x.get('metrics', {}).get('validated_novelty', x.get('metrics', {}).get('avg_novelty', 0)),
                reverse=True
            )
            
            print("\n🆕 Top 5 por Novedad (Validada):")
            for i, result in enumerate(sorted_by_novelty[:5], 1):
                novelty = result['metrics'].get('validated_novelty', result['metrics'].get('avg_novelty', 0))
                print(f"   {i}. {result['loop_name']}: {novelty:.3f}")
        
        print(f"\n{'='*80}\n")


async def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ejecutar loops en producción con generación de hipótesis'
    )
    parser.add_argument(
        '--loop',
        type=str,
        help='Nombre del loop a ejecutar (ej: QuantumLoop)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Ejecutar todos los loops disponibles'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='production_results',
        help='Directorio de salida para resultados'
    )
    
    args = parser.parse_args()
    
    runner = ProductionLoopRunner(output_dir=args.output_dir)
    
    if args.all:
        # Ejecutar todos
        await runner.run_all_loops()
    elif args.loop:
        # Ejecutar uno específico
        if args.loop not in runner.AVAILABLE_LOOPS:
            print(f"❌ Loop '{args.loop}' no disponible")
            print("\nLoops disponibles:")
            for loop in runner.AVAILABLE_LOOPS:
                print(f"  - {loop}")
            sys.exit(1)
        
        result = await runner.run_single_loop(args.loop)
        
        # Guardar resultado
        filename = f"{args.loop}_{runner.timestamp}.json"
        runner._save_result(result, filename)
        
    else:
        print("❌ Debes especificar --loop NOMBRE o --all")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
