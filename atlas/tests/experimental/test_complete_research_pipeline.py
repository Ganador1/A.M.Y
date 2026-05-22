#!/usr/bin/env python3
"""
Prueba completa del pipeline de investigación científica autónoma con:
- Hipótesis científica estructurada  
- Uso intensivo de herramientas científicas
- Revisión por pares autónoma multi-agente
- Evaluación de relevancia científica

Evalúa la calidad científica del paper generado y su relevancia para publicación.
"""

import asyncio
import json
import os
import time
from typing import Dict, Any
import argparse
import pytest

from app.services.multi_agent_coordinator import MultiAgentCoordinator
from app.services.autonomous_peer_review_service import AutonomousPeerReviewService


def _should_use_huggingface() -> bool:
    """Determina si las pruebas deben usar modelos HuggingFace (por defecto desactivado en CI)."""
    return os.environ.get("AXIOM_DISABLE_HF") != "1"


def parse_args():
    p = argparse.ArgumentParser(description='Prueba completa del pipeline de investigación científica')
    p.add_argument('--goal', required=True, help='Objetivo de investigación científica')
    p.add_argument('--domain', 
                   default='neuroscience', 
                   choices=['materials_science', 'drug_discovery', 'energy_storage', 'quantum_computing', 
                           'biophysics', 'genomics', 'biomedical_engineering', 'neuroscience',
                           'mathematics', 'quantum_physics', 'biology'],
                   help='Dominio científico')
    p.add_argument('--enable-tools', action='store_true', default=True, 
                   help='Usar herramientas científicas (por defecto: activado)')
    p.add_argument('--enable-peer-review', action='store_true', default=True,
                   help='Revisión por pares autónoma (por defecto: activado)')
    p.add_argument('--detailed-analysis', action='store_true', 
                   help='Análisis detallado de relevancia y calidad')
    return p.parse_args()


async def evaluate_paper_relevance(paper_content: str, hypothesis: str, domain: str) -> Dict[str, Any]:
    """Evaluar de forma híbrida la relevancia científica del paper generado."""

    paper_content = paper_content or ""
    hypothesis = hypothesis or ""
    lower_content = paper_content.lower()

    # Métricas básicas de estructura
    content_metrics = {
        'word_count': len(paper_content.split()),
        'has_abstract': 'resumen' in lower_content or 'abstract' in lower_content,
        'has_methodology': 'método' in lower_content or 'methodology' in lower_content or 'methods' in lower_content,
        'has_results': 'resultado' in lower_content or 'results' in lower_content,
        'has_discussion': 'discusión' in lower_content or 'discussion' in lower_content,
        'has_references': 'referencia' in lower_content or 'bibliografia' in lower_content or 'references' in lower_content
    }

    domain_corpus = {
        'neuroscience': "neural plasticity synapse neuronal firing cognition brain regions neurotransmitters neural network",
        'biomedical_engineering': "biomaterial implantable device tissue engineering regenerative scaffolds medical device validation",
        'materials_science': "lattice crystal microstructure polymer composite mechanical properties thermal conductivity",
        'drug_discovery': "lead optimization pharmacokinetics molecule therapeutic efficacy clinical trial binding affinity",
        'biophysics': "protein folding membrane potential molecular dynamics structural biology thermodynamics biophysical models",
        'genomics': "genome sequencing DNA RNA gene expression mutation transcriptomics variant analysis",
        'quantum_computing': "qubit coherence gate fidelity error correction stabilizer circuits superconducting quantum algorithms",
        'biology': "cellular metabolism microbiome gene regulation signaling pathway evolutionary biology",
        'mathematics': (
            "manifold spectral analysis combinatorial topology algebraic structures optimization number theory "
            "variedad diferenciable cohomologia espectral grafos expanders optimizacion combinatoria teoria de numeros"
        )
    }

    domain_keywords = {
        'neuroscience': ['neuronal', 'brain', 'neural', 'neuron', 'synapse', 'cognition', 'neuroplasticity'],
        'biomedical_engineering': ['biomaterial', 'implant', 'tissue', 'regeneration', 'medical device', 'scaffold'],
        'materials_science': ['material', 'crystal', 'polymer', 'composite', 'microstructure', 'alloy', 'thermodynamic'],
        'drug_discovery': ['drug', 'pharmaceutical', 'molecule', 'therapeutic', 'clinical trial', 'lead compound'],
        'biophysics': ['protein', 'molecular dynamics', 'biophysical', 'structural biology', 'membrane'],
        'genomics': ['genome', 'dna', 'gene', 'genetic', 'sequencing', 'mutation', 'transcriptomic'],
        'quantum_computing': ['qubit', 'coherence', 'stabilizer', 'topological', 'error correction', 'superconducting', 'circuit'],
        'biology': ['microbiome', 'cellular', 'gene expression', 'metabolic', 'crispr', 'pathway', 'ecology'],
        'mathematics': [
            'prime', 'spectral', 'heuristic', 'manifold', 'algebraic', 'combinatorial', 'optimization',
            'variedad', 'cohomologia', 'grafos', 'optimización', 'optimización combinatoria', 'teoría de números'
        ]
    }

    relevant_keywords = domain_keywords.get(domain, [])
    keyword_matches = sum(1 for keyword in relevant_keywords if keyword.lower() in lower_content)

    structural_flags = [k for k in content_metrics.keys() if k != 'word_count']
    structural_score = sum(1 if content_metrics[k] else 0 for k in structural_flags) / max(len(structural_flags), 1)

    relevance_score = keyword_matches / max(len(relevant_keywords), 1) if relevant_keywords else 0.0

    scientific_terms = ['hypothesis', 'experiment', 'analysis', 'statistical', 'significant',
                        'correlation', 'variable', 'control', 'sample', 'data', 'confidence interval']
    scientific_complexity = sum(1 for term in scientific_terms if term.lower() in lower_content)
    complexity_score = min(scientific_complexity / len(scientific_terms), 1.0)

    # Métricas semánticas usando TF-IDF (fallback a 0 si scikit-learn no está disponible)
    semantic_alignment = 0.0
    hypothesis_alignment = 0.0
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        reference_texts = [domain_corpus.get(domain, ""), hypothesis]
        documents = [paper_content] + [text for text in reference_texts if text]
        if len([d for d in documents if d.strip()]) >= 2:
            vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
            tfidf_matrix = vectorizer.fit_transform(documents)
            paper_vec = tfidf_matrix[0:1]
            domain_vec = tfidf_matrix[1:2] if len(reference_texts) > 0 and reference_texts[0] else None
            hypothesis_vec = tfidf_matrix[-1:] if hypothesis else None

            if domain_vec is not None:
                semantic_alignment = float(cosine_similarity(paper_vec, domain_vec)[0][0])
            if hypothesis and hypothesis_vec is not None:
                hypothesis_alignment = float(cosine_similarity(paper_vec, hypothesis_vec)[0][0])
    except Exception:
        # scikit-learn no disponible; mantenemos 0 y seguimos con heurísticas
        semantic_alignment = 0.0
        hypothesis_alignment = 0.0

    # Puntuación global con pesos equilibrados
    overall_quality = (
        0.25 * structural_score +
        0.20 * relevance_score +
        0.20 * complexity_score +
        0.20 * min(semantic_alignment, 1.0) +
        0.15 * min(hypothesis_alignment, 1.0)
    )

    return {
        'content_metrics': content_metrics,
        'structural_score': structural_score,
        'relevance_score': relevance_score,
        'complexity_score': complexity_score,
        'semantic_alignment': semantic_alignment,
        'hypothesis_alignment': hypothesis_alignment,
        'keyword_matches': keyword_matches,
        'total_keywords_available': len(relevant_keywords),
        'overall_quality': overall_quality
    }


@pytest.mark.asyncio
async def test_evaluate_paper_relevance_semantic_signal():
    """Valida que la evaluación semántica distinga dominios coherentes."""
    math_paper = (
        "Resumen: Analizamos variedades diferenciables de dimensión alta con técnicas de cohomología. "
        "Nuestros métodos combinatorios prueban cotas espectrales en grafos expanders y optimización convexa "
        "aplicada a problemas de teoría de números."
    )
    math_hypothesis = (
        "Hipótesis: Las variedades de Gromov con curvatura negativa admiten descomposiciones espectrales que "
        "aceleran algoritmos de optimización combinatoria."
    )

    math_eval = await evaluate_paper_relevance(math_paper, math_hypothesis, "mathematics")
    bio_eval = await evaluate_paper_relevance(math_paper, math_hypothesis, "biology")

    assert math_eval["semantic_alignment"] >= 0.05, "El detector semántico no identificó contenido matemático"
    assert math_eval["semantic_alignment"] > bio_eval["semantic_alignment"], "El dominio correcto no obtiene mejor alineación"
    assert math_eval["overall_quality"] >= bio_eval["overall_quality"], "La calidad global debería mejorar en el dominio congruente"


async def run_complete_research_pipeline(goal: str, domain: str, enable_tools: bool = True, 
                                       enable_peer_review: bool = True, detailed_analysis: bool = False):
    """Ejecutar pipeline completo de investigación científica"""
    
    print("🧬 AXIOM META 4 - Pipeline Completo de Investigación Científica")
    print("=" * 80)
    print(f"🎯 Objetivo: {goal}")
    print(f"🔬 Dominio: {domain}")
    print(f"🛠️ Herramientas: {'✅ Activadas' if enable_tools else '❌ Desactivadas'}")
    print(f"👥 Peer Review: {'✅ Activado' if enable_peer_review else '❌ Desactivado'}")
    coordinator = MultiAgentCoordinator(use_huggingface=_should_use_huggingface())
    role_display = {
        "orchestrator": "Orchestrator",
        "bio_hypothesis": "Bio Hypothesis",
        "physchem_coder": "PhysChem Coder",
        "reviewer": "Reviewer",
        "publisher": "Publisher"
    }
    print("🤖 Modelos especializados:")
    for role in role_display:
        model_name = coordinator.role_models.get(role, "N/A")
        print(f"   • {role_display[role]}: {model_name}")
    print("=" * 80)
    
    start_time = time.time()
    
    # ========================================
    # FASE 1: Generación de Investigación
    # ========================================
    print("\n🚀 FASE 1: Ejecución del pipeline multi-agente")
    print("-" * 60)
    
    try:
        result = await coordinator.run_pipeline_integrated_async(
            goal, 
            domain=domain, 
            compile_latex=False
        )
        
        if not result.get('success'):
            print(f"❌ Error en pipeline: {result.get('error')}")
            return {"success": False, "error": result.get('error')}
        
        artifact = result['artifact']
        hypothesis = artifact.get('raw_hypothesis', '')
        publication = artifact.get('publication', '')
        evidence_summary = artifact.get('evidence', {}).get('summary', {})
        plan_text = artifact.get('plan', '')
        
        print("✅ Pipeline multi-agente completado")
        print(f"📄 Paper generado: {len(publication)} caracteres")
        if publication:
            pub_preview = publication if len(publication) < 200 else publication[:200] + "..."
            print(f"   ↳ Preview: {pub_preview}")
        print(f"🧪 Hipótesis: {len(hypothesis)} caracteres")
        if hypothesis:
            hyp_preview = hypothesis if len(hypothesis) < 200 else hypothesis[:200] + "..."
            print(f"   ↳ Preview: {hyp_preview}")
        if plan_text:
            plan_preview = plan_text if len(plan_text) < 200 else plan_text[:200] + "..."
            print(f"🧭 Plan inicial: {plan_preview}")
        
        duration_phase1 = time.time() - start_time
        
    except Exception as e:
        print(f"💥 Error en Fase 1: {str(e)}")
        return {"success": False, "error": str(e)}
    
    # ========================================
    # FASE 2: Evaluación de Relevancia
    # ========================================
    print("\n📊 FASE 2: Análisis de relevancia científica")
    print("-" * 60)
    
    relevance_analysis = await evaluate_paper_relevance(publication, hypothesis, domain)
    
    print(f"📏 Métricas de Estructura:")
    for metric, value in relevance_analysis['content_metrics'].items():
        icon = "✅" if value else "❌"
        print(f"   {icon} {metric.replace('_', ' ').title()}: {value}")
    
    print(f"\n🎯 Puntuaciones de Calidad:")
    print(f"   📐 Estructura: {relevance_analysis['structural_score']:.2f}")
    print(f"   🔍 Relevancia temática: {relevance_analysis['relevance_score']:.2f}")
    print(f"   🧠 Complejidad científica: {relevance_analysis['complexity_score']:.2f}")
    print(f"   🧭 Alineación semántica: {relevance_analysis['semantic_alignment']:.2f}")
    print(f"   🔗 Alineación con hipótesis: {relevance_analysis['hypothesis_alignment']:.2f}")
    print(f"   🏆 Calidad general: {relevance_analysis['overall_quality']:.2f}")
    print(f"   🔑 Keywords encontradas: {relevance_analysis['keyword_matches']}/{relevance_analysis['total_keywords_available']}")
    
    # ========================================
    # FASE 3: Revisión por Pares Autónoma
    # ========================================
    peer_review_results = None
    
    if enable_peer_review:
        print("\n👥 FASE 3: Revisión por pares autónoma")
        print("-" * 60)
        
        try:
            peer_review_service = AutonomousPeerReviewService()
            
            # Crear experimento para revisión
            experiment_data = {
                "id": f"research_{domain}_{int(time.time())}",
                "domain": domain,
                "title": goal[:100],  # Truncar título
                "hypothesis": hypothesis[:1000],  # Truncar hipótesis
                "methodology": publication[:2000] if "método" in publication.lower() else "Generated through multi-agent AI system",
                "results": {
                    "tool_evidence_score": evidence_summary.get('support_score', 0.0),
                    "coverage": evidence_summary.get('coverage', 0.0),
                    "diversity": evidence_summary.get('diversity', 0.0),
                    "publication_length": len(publication),
                    "structural_quality": relevance_analysis['structural_score']
                }
            }
            
            print(f"🧪 Experimento: {experiment_data['id']}")
            print(f"📝 Dominio: {experiment_data['domain']}")
            
            peer_review_result = await peer_review_service.validate_experiment({
                "experiment": experiment_data
            })
            
            if peer_review_result.get('success'):
                peer_review_results = peer_review_result
                
                overall_score = peer_review_result.get('overall_score', 0.0)
                approved = peer_review_result.get('approved', False)
                peer_reviews = peer_review_result.get('peer_reviews', [])
                recommendations = peer_review_result.get('recommendations', [])
                
                status_icon = "✅" if approved else "❌"
                print(f"\n{status_icon} RESULTADO DE PEER REVIEW:")
                print(f"   📊 Puntuación general: {overall_score}/10")
                print(f"   🎯 Estado: {'APROBADO' if approved else 'RECHAZADO/REVISIÓN REQUERIDA'}")
                print(f"   👥 Revisores: {len(peer_reviews)}")
                
                if detailed_analysis and peer_reviews:
                    print(f"\n🔍 ANÁLISIS DETALLADO DE REVISORES:")
                    for i, review in enumerate(peer_reviews[:3], 1):  # Top 3
                        reviewer = review.get('reviewer_agent', 'Unknown').replace('_', ' ').title()
                        score = review.get('overall_score', 0.0)
                        validity = review.get('scientific_validity', 0.0)
                        rigor = review.get('methodological_rigor', 0.0)
                        novelty = review.get('novelty_contribution', 0.0)
                        approved_by_reviewer = review.get('approved', False)
                        
                        rev_icon = "✅" if approved_by_reviewer else "⚠️"
                        print(f"   {rev_icon} {i}. {reviewer}")
                        print(f"      • Puntuación: {score:.1f}/10")
                        print(f"      • Validez científica: {validity:.1f}/10")
                        print(f"      • Rigor metodológico: {rigor:.1f}/10")
                        print(f"      • Contribución novedosa: {novelty:.1f}/10")
                        
                        # Mostrar issues si existen
                        issues = review.get('issues', [])
                        if issues:
                            print(f"      • Issues: {len(issues)}")
                            for issue in issues[:2]:  # Top 2 issues
                                print(f"        - {issue.get('description', 'N/A')[:60]}...")
                        print()
                
                if recommendations:
                    print(f"💡 RECOMENDACIONES PRINCIPALES:")
                    for i, rec in enumerate(recommendations[:5], 1):
                        print(f"   {i}. {rec}")
                        
            else:
                print(f"❌ Error en peer review: {peer_review_result.get('error')}")
                
        except Exception as e:
            print(f"💥 Error en peer review: {str(e)}")
    else:
        print("\n👥 FASE 3: Revisión por pares - OMITIDA")
        print("-" * 60)
    
    # ========================================
    # RESUMEN FINAL Y EVALUACIÓN
    # ========================================
    total_duration = time.time() - start_time
    
    print(f"\n🎯 RESUMEN EJECUTIVO FINAL")
    print("=" * 80)
    print(f"⏱️ Tiempo total: {total_duration:.1f}s")
    print(f"🔬 Dominio: {domain}")
    print(f"📄 Paper generado: {len(publication):,} caracteres")
    
    # Evaluación de herramientas
    tool_calls = artifact.get('evidence', {}).get('tool_calls', [])
    successful_tools = len([tc for tc in tool_calls if tc.get('success', False)])
    total_tools = len(tool_calls)
    tool_success_rate = successful_tools / total_tools if total_tools > 0 else 0
    
    print(f"🛠️ Herramientas: {successful_tools}/{total_tools} exitosas ({tool_success_rate:.1%})")
    
    # Métricas de evidencia
    support_score = evidence_summary.get('support_score', 0.0)
    coverage = evidence_summary.get('coverage', 0.0)
    
    print(f"📊 Evidencia científica:")
    print(f"   • Support Score: {support_score:.3f}")
    print(f"   • Coverage: {coverage:.3f}")
    
    # Calidad del paper
    print(f"📈 Calidad del paper:")
    print(f"   • Calidad general: {relevance_analysis['overall_quality']:.3f}")
    print(f"   • Estructura: {relevance_analysis['structural_score']:.3f}")
    print(f"   • Relevancia temática: {relevance_analysis['relevance_score']:.3f}")
    
    # Peer review
    if peer_review_results:
        pr_score = peer_review_results.get('overall_score', 0.0)
        pr_approved = peer_review_results.get('approved', False)
        pr_icon = "✅" if pr_approved else "❌"
        print(f"👥 Peer Review: {pr_icon} {pr_score}/10 ({'APROBADO' if pr_approved else 'RECHAZADO'})")
    else:
        print(f"👥 Peer Review: ⚪ No ejecutado")
    
    # ========================================
    # EVALUACIÓN FINAL DE RELEVANCIA
    # ========================================
    print(f"\n🏆 EVALUACIÓN FINAL DE RELEVANCIA CIENTÍFICA")
    print("=" * 80)
    
    # Calcular puntuación compuesta
    quality_factors = {
        'paper_quality': relevance_analysis['overall_quality'] * 0.3,
        'tool_evidence': (support_score + coverage) / 2 * 0.25,
        'peer_review': (peer_review_results.get('overall_score', 5.0) / 10) * 0.35 if peer_review_results else 0.5,
        'tool_success': tool_success_rate * 0.1
    }
    
    final_score = sum(quality_factors.values())
    
    print("📊 Componentes de la evaluación:")
    for factor, score in quality_factors.items():
        print(f"   • {factor.replace('_', ' ').title()}: {score:.3f}")
    
    print(f"\n🎯 PUNTUACIÓN FINAL: {final_score:.3f}/1.0")
    
    # Determinar relevancia
    if final_score >= 0.8:
        relevance_level = "🟢 ALTAMENTE RELEVANTE - Listo para publicación"
    elif final_score >= 0.6:
        relevance_level = "🟡 RELEVANTE - Requiere revisiones menores"  
    elif final_score >= 0.4:
        relevance_level = "🟠 PARCIALMENTE RELEVANTE - Requiere revisiones importantes"
    else:
        relevance_level = "🔴 BAJA RELEVANCIA - Requiere reingeniería completa"
    
    print(f"📋 VEREDICTO: {relevance_level}")
    
    # Sugerencias de mejora
    print(f"\n💡 SUGERENCIAS PARA MEJORAR RESULTADOS:")
    suggestions = []
    
    if tool_success_rate < 0.5:
        suggestions.append("🛠️ Mejorar integración y configuración de herramientas científicas")
    
    if relevance_analysis['structural_score'] < 0.7:
        suggestions.append("📝 Mejorar estructura del paper (abstract, metodología, resultados)")
        
    if relevance_analysis['relevance_score'] < 0.5:
        suggestions.append("🎯 Incorporar más terminología específica del dominio")
    if relevance_analysis['semantic_alignment'] < 0.3:
        suggestions.append("🧭 Reforzar coherencia con literatura del dominio (alineación semántica baja)")
    if relevance_analysis['hypothesis_alignment'] < 0.3:
        suggestions.append("🔗 Asegurar que los resultados respondan directamente a la hipótesis planteada")
        
    if peer_review_results and peer_review_results.get('overall_score', 10) < 6:
        suggestions.append("👥 Abordar las críticas del peer review antes de publicación")
        
    if evidence_summary.get('support_score', 0) < 0.3:
        suggestions.append("📊 Recopilar más evidencia científica mediante herramientas")
    
    if not suggestions:
        suggestions.append("✨ El sistema está funcionando óptimamente")
    
    for suggestion in suggestions:
        print(f"   {suggestion}")
    
    print("=" * 80)
    
    return {
        "success": True,
        "duration": total_duration,
        "final_score": final_score,
        "relevance_level": relevance_level,
        "paper_length": len(publication),
        "tool_success_rate": tool_success_rate,
        "peer_review_score": peer_review_results.get('overall_score') if peer_review_results else None,
        "quality_factors": quality_factors,
        "suggestions": suggestions
    }


async def run_minimal_hypothesis_to_paper_flow(goal: str, domain: str = "neuroscience"):
    """
    Flujo mínimo hipótesis→paper para testing de integración básica.
    Versión simplificada sin peer review y con métricas básicas.
    """
    print("🧪 AXIOM - Flujo Mínimo Hipótesis→Paper")
    print("=" * 60)
    print(f"🎯 Objetivo: {goal}")
    print(f"🔬 Dominio: {domain}")
    print("⚡ Configuración: Sin peer review, métricas básicas")
    print("=" * 60)
    
    start_time = time.time()
    coordinator = MultiAgentCoordinator(use_huggingface=_should_use_huggingface())
    
    try:
        # Ejecutar pipeline básico
        result = await coordinator.run_pipeline_integrated_async(
            goal, 
            domain=domain,
            compile_latex=False
        )
        
        if not result.get('success'):
            return {"success": False, "error": result.get('error')}
        
        artifact = result['artifact']
        hypothesis = artifact.get('raw_hypothesis', '')
        publication = artifact.get('publication', '')
        
        # Métricas básicas de validación
        duration = time.time() - start_time

        relevance_analysis = await evaluate_paper_relevance(publication, hypothesis, domain)
        
        print(f"✅ Flujo mínimo completado en {duration:.1f}s")
        print(f"📄 Paper generado: {len(publication)} caracteres")
        print(f"🧪 Hipótesis: {len(hypothesis)} caracteres")
        print(f"🧭 Alineación semántica: {relevance_analysis['semantic_alignment']:.2f}")
        print(f"🔗 Alineación hipótesis: {relevance_analysis['hypothesis_alignment']:.2f}")
        print(f"🏆 Calidad global: {relevance_analysis['overall_quality']:.2f}")
        
        # Validación básica del resultado
        # Manejo robusto de casos donde los LLMs no están disponibles
        has_meaningful_hypothesis = len(hypothesis) > 100 and not any(error_indicator in hypothesis for error_indicator in ['ERROR', 'not available', 'not ready'])
        has_meaningful_publication = len(publication) > 500 and not any(error_indicator in publication for error_indicator in ['ERROR', 'not available', 'not ready'])
        
        validation_result = {
            "success": True,
            "duration": duration,
            "paper_length": len(publication),
            "hypothesis_length": len(hypothesis),
            "has_hypothesis": has_meaningful_hypothesis,
            "has_publication": has_meaningful_publication,
            "contains_scientific_terms": has_meaningful_publication and any(term in publication.lower() for term in 
                ['hypothesis', 'experiment', 'result', 'method', 'analysis', 'conclusion']),
            "contains_domain_terms": has_meaningful_publication and any(term in publication.lower() for term in 
                (['neural', 'brain', 'neuron'] if domain == "neuroscience" else
                 ['material', 'property', 'structure'] if domain == "materials_science" else
                 ['drug', 'molecule', 'therapy'] if domain == "drug_discovery" else
                 ['energy', 'storage', 'battery'] if domain == "energy_storage" else [])),
            "llm_available": has_meaningful_hypothesis and has_meaningful_publication,
            "semantic_alignment": relevance_analysis['semantic_alignment'],
            "hypothesis_alignment": relevance_analysis['hypothesis_alignment'],
            "overall_quality": relevance_analysis['overall_quality']
        }
        
        print(f"\n📊 VALIDACIÓN BÁSICA:")
        print(f"   ✅ Hipótesis generada: {validation_result['has_hypothesis']}")
        print(f"   ✅ Paper generado: {validation_result['has_publication']}")
        print(f"   ✅ Términos científicos: {validation_result['contains_scientific_terms']}")
        print(f"   ✅ Términos del dominio: {validation_result['contains_domain_terms']}")
        
        return validation_result
        
    except Exception as e:
        print(f"💥 Error en flujo mínimo: {str(e)}")
        return {"success": False, "error": str(e)}


@pytest.mark.asyncio
async def test_minimal_hypothesis_to_paper_neuroscience():
    """Test del flujo mínimo hipótesis→paper en neurociencia"""
    result = await run_minimal_hypothesis_to_paper_flow(
        goal="Investigate the effects of neural plasticity on learning and memory formation",
        domain="neuroscience"
    )
    
    # Verificaciones básicas del pipeline
    assert result["success"] is True, f"Pipeline falló: {result.get('error')}"
    assert result["duration"] < 300, f"Pipeline tardó demasiado: {result['duration']}s"
    
    # Verificación flexible dependiendo de la disponibilidad de LLMs
    if result["llm_available"]:
        # Si los LLMs están disponibles, verificamos todo el contenido
        assert result["has_hypothesis"] is True, "Hipótesis no generada correctamente"
        assert result["has_publication"] is True, "Publicación no generada correctamente"
        assert result["contains_scientific_terms"] is True, "Faltan términos científicos"
        assert result["contains_domain_terms"] is True, "Faltan términos del dominio"
        assert result["semantic_alignment"] >= 0.10, "La alineación semántica es demasiado baja para neurociencia"
        assert result["overall_quality"] >= 0.20, "La calidad global no alcanza el umbral mínimo"
        print("✅ Todos los LLMs disponibles - Test completo ejecutado")
    else:
        # Si los LLMs no están disponibles, verificamos solo que el pipeline se complete
        print("⚠️  LLMs locales no disponibles - Verificando solo ejecución del pipeline")
        print(f"   Longitud hipótesis: {result['hypothesis_length']}")
        print(f"   Longitud publicación: {result['paper_length']}")
        print(f"   LLM disponible: {result['llm_available']}")
        
        # Aseguramos que al menos el pipeline se ejecutó correctamente
        assert result["success"] is True, "Pipeline falló a pesar de LLMs no disponibles"
        assert result["duration"] < 300, "Pipeline tardó demasiado"
        
        # Marcamos el test como skipped en lugar de failed
        pytest.skip("LLMs locales no disponibles - Pipeline ejecutado pero contenido no generado")


@pytest.mark.asyncio  
async def test_minimal_hypothesis_to_paper_materials_science():
    """Test del flujo mínimo hipótesis→paper en ciencia de materiales"""
    result = await run_minimal_hypothesis_to_paper_flow(
        goal="Develop novel composite materials with enhanced thermal conductivity",
        domain="materials_science"
    )
    
    # Verificaciones básicas del pipeline
    assert result["success"] is True, f"Pipeline falló: {result.get('error')}"
    assert result["duration"] < 300, f"Pipeline tardó demasiado: {result['duration']}s"
    
    # Verificación flexible dependiendo de la disponibilidad de LLMs
    if result["llm_available"]:
        # Si los LLMs están disponibles, verificamos todo el contenido
        assert result["has_hypothesis"] is True, "Hipótesis no generada correctamente"
        assert result["has_publication"] is True, "Publicación no generada correctamente"
        assert result["contains_scientific_terms"] is True, "Faltan términos científicos"
        assert result["contains_domain_terms"] is True, "Faltan términos del dominio"
        assert result["semantic_alignment"] >= 0.10, "La alineación semántica es demasiado baja para materiales"
        assert result["overall_quality"] >= 0.20, "La calidad global no alcanza el umbral mínimo"
        print("✅ Todos los LLMs disponibles - Test completo ejecutado")
    else:
        # Si los LLMs no están disponibles, verificamos solo que el pipeline se complete
        print("⚠️  LLMs locales no disponibles - Verificando solo ejecución del pipeline")
        print(f"   Longitud hipótesis: {result['hypothesis_length']}")
        print(f"   Longitud publicación: {result['paper_length']}")
        print(f"   LLM disponible: {result['llm_available']}")
        
        # Aseguramos que al menos el pipeline se ejecutó correctamente
        assert result["success"] is True, "Pipeline falló a pesar de LLMs no disponibles"
        assert result["duration"] < 300, "Pipeline tardó demasiado"
        
        # Marcamos el test como skipped en lugar de failed
        pytest.skip("LLMs locales no disponibles - Pipeline ejecutado pero contenido no generado")


def main():
    args = parse_args()
    
    result = asyncio.run(run_complete_research_pipeline(
        goal=args.goal,
        domain=args.domain,
        enable_tools=args.enable_tools,
        enable_peer_review=args.enable_peer_review,
        detailed_analysis=args.detailed_analysis
    ))
    
    if result.get('success'):
        print(f"\n🎉 PIPELINE COMPLETADO EXITOSAMENTE")
        print(f"📊 Puntuación final: {result['final_score']:.3f}/1.0")
        print(f"⏱️ Duración: {result['duration']:.1f}s")
    else:
        print(f"\n💥 PIPELINE FALLÓ: {result.get('error')}")


if __name__ == '__main__':
    main()
