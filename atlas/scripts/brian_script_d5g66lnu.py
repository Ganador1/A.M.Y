# Sat Nov  1 21:52:37 2025
# Run as: execute_pipeline_v3_neuroscience.py

#!/usr/bin/env python3
"""
Pipeline v3.0 - Neuroscience Research con PlotlyService ACTIVADO
================================================================

Ejecuta el flujo completo de investigación autónoma:
1. Generación de hipótesis (Bio Hypothesis Agent)
2. Ejecución de herramientas científicas (Tool Evidence Orchestrator)
3. Peer Review (Reviewer Agent)
4. Publicación (Publisher Agent con keywords mandatorios)

Versión 3.0 mejoras:
- PlotlyService activado (fix en tool_evidence_orchestrator.py)
- Keywords de neurociencia obligatorios en Publisher
- Objetivo científico mejorado con términos específicos
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

# Importaciones directas de los servicios que sabemos que funcionan
from app.services.huggingface_agent_wrapper import HuggingFaceAgentWrapper
from app.services.tool_evidence_orchestrator import ToolEvidenceOrchestrator
from app.services.peer_review_service import PeerReviewService


async def execute_neuroscience_pipeline_v3():
    """Ejecuta pipeline completo de investigación en neurociencia"""
    
    print("=" * 90)
    print("🧠 AXIOM ATLAS - Pipeline v3.0: Investigación Autónoma en Neurociencia")
    print("=" * 90)
    print()
    
    # Objetivo científico mejorado con keywords de dominio
    scientific_objective = """
    Investigar plasticidad sináptica DEPENDIENTE DE RECEPTORES NMDA en neuronas 
    PIRAMIDALES del hipocampo CA1 durante la POTENCIACIÓN A LARGO PLAZO (LTP), 
    mediante análisis de CORRIENTES POSTSINÁPTICAS EXCITATORIAS (EPSC) y cambios 
    en la TRANSMISIÓN SINÁPTICA mediada por receptores AMPA y NMDA.
    """
    
    domain = "neuroscience"
    start_time = datetime.now()
    
    # ============================================================================
    # FASE 1: Generación de Hipótesis
    # ============================================================================
    print("📝 FASE 1: Generación de Hipótesis")
    print("-" * 90)
    
    hypothesis_agent = HuggingFaceAgentWrapper(
        agent_role="bio_hypothesis",
        domain=domain
    )
    
    hypothesis_prompt = f"""Generate a detailed scientific hypothesis about: {scientific_objective}

Requirements:
- Clear research question
- Testable predictions
- Specific molecular mechanisms
- Expected experimental outcomes"""
    
    print(f"🤖 Agente: Bio Hypothesis (Qwen 2.5-72B-Instruct)")
    print(f"🎯 Objetivo: {scientific_objective.strip()[:100]}...")
    
    hypothesis_response = await hypothesis_agent.generate_async(hypothesis_prompt)
    hypothesis_text = hypothesis_response.get("text", "")
    
    print(f"✅ Hipótesis generada ({len(hypothesis_text)} caracteres)")
    print()
    
    # Crear objeto de hipótesis para las siguientes fases
    hypothesis = {
        "title": "NMDA-Dependent Synaptic Plasticity in Hippocampal CA1 Neurons",
        "text": hypothesis_text,
        "domain": domain,
        "objective": scientific_objective.strip(),
        "timestamp": datetime.now().isoformat()
    }
    
    # ============================================================================
    # FASE 2: Ejecución de Herramientas Científicas
    # ============================================================================
    print("🔧 FASE 2: Ejecución de Herramientas Científicas")
    print("-" * 90)
    
    tool_orchestrator = ToolEvidenceOrchestrator()
    
    print(f"🛠️  ToolEvidenceOrchestrator inicializado")
    print(f"📊 Dominio: {domain}")
    print(f"🎯 Herramientas disponibles: Plotly, Matplotlib, SymPy, etc.")
    print()
    print(f"⚙️  Ejecutando herramientas...")
    
    tool_request = {
        "action": "corroborate",
        "hypothesis": hypothesis,
        "domain": domain
    }
    
    tool_evidence = await tool_orchestrator.process_request(tool_request)
    
    tools_executed = len(tool_evidence.get("evidence_items", []))
    tool_success_rate = tool_evidence.get("aggregate", {}).get("avg_signal", 0)
    
    print(f"✅ Herramientas ejecutadas: {tools_executed}")
    print(f"⚡ Tasa de éxito: {tool_success_rate:.3f}")
    print()
    
    # ============================================================================
    # FASE 3: Peer Review Autónomo
    # ============================================================================
    print("📖 FASE 3: Peer Review Autónomo")
    print("-" * 90)
    
    reviewer_agent = HuggingFaceAgentWrapper(
        agent_role="reviewer",
        domain=domain
    )
    
    review_prompt = f"""Conduct a rigorous peer review of this scientific hypothesis:

**Hypothesis:** {hypothesis_text[:500]}...

**Tool Evidence:** {tools_executed} scientific tools executed, success rate: {tool_success_rate:.2f}

Evaluate:
1. Scientific rigor and methodology
2. Novelty and significance
3. Experimental design quality
4. Evidence support
5. Overall quality (score 1-10)

Provide critical feedback and improvement suggestions."""
    
    print(f"🤖 Agente: Reviewer (DeepSeek-R1)")
    
    review_response = await reviewer_agent.generate_async(review_prompt)
    review_text = review_response.get("text", "")
    
    print(f"✅ Review completado ({len(review_text)} caracteres)")
    print()
    
    # ============================================================================
    # FASE 4: Publicación de Artículo Científico
    # ============================================================================
    print("📄 FASE 4: Publicación de Artículo Científico")
    print("-" * 90)
    
    publisher_agent = HuggingFaceAgentWrapper(
        agent_role="publisher",
        domain=domain  # Esto activa keywords de neurociencia
    )
    
    publication_prompt = f"""Write a complete scientific paper about this research:

**Title:** {hypothesis['title']}

**Hypothesis:** {hypothesis_text[:300]}...

**Evidence:** {tools_executed} tools executed
- Tool success rate: {tool_success_rate:.3f}
- Domain: {domain}

**Peer Review Feedback:** {review_text[:300]}...

Structure:
1. Abstract
2. Introduction (with neuroscience context)
3. Methods (experimental design)
4. Results (expected outcomes)
5. Discussion
6. Conclusion

Use rigorous scientific language and domain-specific terminology."""
    
    print(f"🤖 Agente: Publisher (Meta-Llama-3.1-70B-Instruct)")
    print(f"📚 Keywords de neurociencia: ACTIVADOS (30+ términos obligatorios)")
    
    publication_response = await publisher_agent.generate_async(publication_prompt)
    paper_text = publication_response.get("text", "")
    
    word_count = len(paper_text.split())
    print(f"✅ Artículo generado ({word_count} palabras)")
    print()
    
    # ============================================================================
    # EVALUACIÓN FINAL
    # ============================================================================
    print("📊 EVALUACIÓN FINAL")
    print("-" * 90)
    
    # Análisis de keywords (lista completa de neurociencia)
    neuroscience_keywords = [
        "neuronal", "neural", "brain", "neuron", "synapse", "hippocampus",
        "plasticity", "LTP", "NMDA", "AMPA", "EPSC", "pyramidal", "CA1",
        "dendritic", "spine", "receptor", "glutamate", "calcium", "signaling",
        "potentiation", "depression", "LTD", "CREB", "CaMKII", "PKA",
        "postsynaptic", "presynaptic", "neurotransmitter", "axon"
    ]
    
    paper_lower = paper_text.lower()
    keywords_found = [kw for kw in neuroscience_keywords if kw.lower() in paper_lower]
    keyword_coverage = len(keywords_found) / len(neuroscience_keywords)
    
    # Scoring (similar a v1 y v2)
    paper_quality_score = min(word_count / 600, 1.0)  # Target: 600 palabras
    tool_usage_score = min(tools_executed / 3, 1.0)  # Target: 3+ herramientas
    tool_success_score = tool_success_rate
    keyword_score = keyword_coverage
    
    # Peso ponderado
    overall_score = (
        paper_quality_score * 0.30 +  # Calidad del paper (30%)
        tool_usage_score * 0.25 +      # Uso de herramientas (25%)
        tool_success_score * 0.25 +    # Éxito de herramientas (25%)
        keyword_score * 0.20            # Cobertura de keywords (20%)
    )
    
    duration = (datetime.now() - start_time).total_seconds()
    
    print(f"⏱️  Duración total: {duration:.1f}s")
    print()
    print(f"📈 Componentes del Score:")
    print(f"   • Calidad del paper:       {paper_quality_score:.3f} (palabras: {word_count}/600)")
    print(f"   • Uso de herramientas:     {tool_usage_score:.3f} (ejecutadas: {tools_executed}/3)")
    print(f"   • Éxito de herramientas:   {tool_success_score:.3f}")
    print(f"   • Cobertura de keywords:   {keyword_score:.3f} ({len(keywords_found)}/{len(neuroscience_keywords)})")
    print()
    print(f"🏆 SCORE FINAL: {overall_score:.3f}/1.0")
    print()
    
    if keywords_found:
        print(f"✅ Keywords encontrados: {', '.join(keywords_found[:10])}...")
    else:
        print(f"⚠️  No se encontraron keywords de neurociencia")
    
    print()
    
    # ============================================================================
    # GUARDAR RESULTADOS
    # ============================================================================
    results = {
        "version": "3.0",
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": duration,
        "domain": domain,
        "objective": scientific_objective.strip(),
        "hypothesis": hypothesis,
        "tool_evidence": {
            "tools_executed": tools_executed,
            "success_rate": tool_success_score,
            "details": tool_evidence
        },
        "peer_review": {
            "text": review_text,
            "length": len(review_text)
        },
        "publication": {
            "text": paper_text,
            "word_count": word_count,
            "keywords_found": keywords_found,
            "keyword_coverage": keyword_coverage
        },
        "scores": {
            "paper_quality": paper_quality_score,
            "tool_usage": tool_usage_score,
            "tool_success": tool_success_score,
            "keyword_coverage": keyword_score,
            "overall": overall_score
        }
    }
    
    output_file = f"pipeline_v3_neuroscience_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultados guardados: {output_file}")
    print()
    print("=" * 90)
    
    return results


if __name__ == "__main__":
    print()
    results = asyncio.run(execute_neuroscience_pipeline_v3())
    
    # Resumen final
    score = results["scores"]["overall"]
    tools = results["tool_evidence"]["tools_executed"]
    
    print()
    print(f"✨ Pipeline v3.0 completado exitosamente")
    print(f"📊 Score: {score:.3f}/1.0")
    print(f"🔧 Herramientas: {tools}")
    print()
