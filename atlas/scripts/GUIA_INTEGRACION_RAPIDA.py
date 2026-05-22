#!/usr/bin/env python3
"""
GUÍA RÁPIDA DE INTEGRACIÓN - Paper Enhancement Services
========================================================

Este script demuestra cómo integrar los nuevos servicios de mejora
en pipelines existentes. Usa este como template para modificar tus
pipelines de validación.

ANTES (pipeline original):
    1. Generar hipótesis
    2. Ejecutar herramientas
    3. Generar paper con publisher agent
    4. Guardar resultado

DESPUÉS (pipeline mejorado):
    1. Generar hipótesis
    2. Ejecutar herramientas
    3. Generar paper con publisher agent
    4. ✨ MEJORAR PAPER (referencias + estadísticas + discussion)
    5. Guardar resultado mejorado

TIEMPO DE IMPLEMENTACIÓN: 10-15 minutos por pipeline
"""

from typing import Dict, Any
from app.services.paper_enhancement import enhance_pipeline_paper


# ==============================================================================
# EJEMPLO 1: Integración Básica (Mínimo código)
# ==============================================================================

def integrate_basic(original_paper: str, tool_evidence: Dict[str, Any], domain: str) -> str:
    """
    Integración básica - solo 1 línea de código
    
    Agrega:
    - Referencias automáticas (estilo APA)
    - Análisis estadístico (si hay datos numéricos)
    - Discussion section (si falta)
    """
    result = enhance_pipeline_paper(
        paper_text=original_paper,
        tool_evidence=tool_evidence,
        domain=domain,
        include_discussion=True,
        citation_style="APA"
    )
    
    return result["enhanced_paper"]


# ==============================================================================
# EJEMPLO 2: Integración Completa con Logging
# ==============================================================================

def integrate_with_logging(
    original_paper: str, 
    tool_evidence: Dict[str, Any], 
    domain: str,
    logger
) -> Dict[str, Any]:
    """
    Integración completa con logging detallado
    
    Retorna dict completo con metadata para análisis posterior
    """
    logger.info(f"Iniciando mejora de paper para dominio: {domain}")
    
    # Mejorar paper
    result = enhance_pipeline_paper(
        paper_text=original_paper,
        tool_evidence=tool_evidence,
        domain=domain,
        include_discussion=True,
        citation_style="APA"
    )
    
    # Logging detallado
    logger.info("Mejoras aplicadas:")
    for improvement in result["improvements"]:
        logger.info(f"  {improvement}")
    
    logger.info(f"Referencias agregadas: {result['references_count']}")
    logger.info(f"Incremento de longitud: +{result['percent_increase']}%")
    
    if result["statistics"]:
        logger.info("Estadísticas calculadas:")
        for metric, stats in result["statistics"].items():
            logger.info(f"  {metric}: {stats['mean']:.4f} ± {stats['std_dev']:.4f} (n={stats['sample_size']})")
    
    return result


# ==============================================================================
# EJEMPLO 3: Modificar Pipeline Existente (execute_pipeline_v33_*.py)
# ==============================================================================

"""
PASOS PARA MODIFICAR UN PIPELINE EXISTENTE:

1. Importar servicio al inicio del archivo:

    from app.services.paper_enhancement import enhance_pipeline_paper

2. Buscar la sección donde se genera el paper (publisher agent):

    # ANTES (código original)
    final_paper = publisher_agent.run(
        hypothesis=hypothesis,
        evidence=tool_evidence,
        ...
    )
    
3. Agregar mejora DESPUÉS de generar el paper:

    # DESPUÉS (código mejorado)
    original_paper = publisher_agent.run(
        hypothesis=hypothesis,
        evidence=tool_evidence,
        ...
    )
    
    # ✨ NUEVA SECCIÓN: Mejorar paper
    enhancement_result = enhance_pipeline_paper(
        paper_text=original_paper,
        tool_evidence=tool_evidence,
        domain="neuroscience",  # Cambiar según pipeline
        include_discussion=True,
        citation_style="APA"
    )
    
    final_paper = enhancement_result["enhanced_paper"]
    
    # Logging de mejoras
    logger.info("Mejoras aplicadas al paper:")
    for improvement in enhancement_result["improvements"]:
        logger.info(improvement)
    
4. Actualizar guardado de resultados para incluir metadata:

    results = {
        "hypothesis": hypothesis,
        "paper": final_paper,
        "paper_enhancement": {
            "improvements": enhancement_result["improvements"],
            "references_count": enhancement_result["references_count"],
            "statistics": enhancement_result["statistics"]
        },
        ...
    }
"""


# ==============================================================================
# EJEMPLO 4: Pipeline Completo Modificado (Neuroscience)
# ==============================================================================

def example_neuroscience_pipeline_enhanced():
    """
    Ejemplo completo de pipeline de Neurociencia con mejoras integradas
    
    BASADO EN: execute_pipeline_v33_neuroscience.py
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # =========================================================================
    # FASE 1: Generación de hipótesis (código original sin cambios)
    # =========================================================================
    
    hypothesis = {
        "title": "STDP-based learning in cortical networks",
        "objective": "Investigate synaptic plasticity mechanisms...",
        "domain": "neuroscience"
    }
    
    logger.info(f"Hipótesis generada: {hypothesis['title']}")
    
    # =========================================================================
    # FASE 2: Ejecución de herramientas (código original sin cambios)
    # =========================================================================
    
    tool_evidence = {
        "evidence_items": [
            {
                "tool_name": "pubmed",
                "metadata": {
                    "title": "STDP and synaptic plasticity",
                    "authors": "Caporale, N. and Dan, Y.",
                    "year": "2008",
                    "journal": "Annual Review of Neuroscience"
                },
                "signal_strength": 0.95
            }
        ]
    }
    
    logger.info(f"Herramientas ejecutadas: {len(tool_evidence['evidence_items'])}")
    
    # =========================================================================
    # FASE 3: Generación de paper (código original sin cambios)
    # =========================================================================
    
    original_paper = """# STDP-based Learning in Cortical Networks

## Abstract
We investigate spike-timing-dependent plasticity (STDP) mechanisms...

## Introduction
Neural plasticity is fundamental to learning and memory formation...

## Methods
Spiking neural network simulations with STDP learning rules...

## Results
Classification accuracy: 0.891 (trials: 0.895, 0.889, 0.893, 0.890)
F1 score = 0.875, precision = 0.912

## Conclusions
STDP-based learning achieves high performance in cortical networks...
"""
    
    logger.info(f"Paper original generado: {len(original_paper)} caracteres")
    
    # =========================================================================
    # ✨ FASE 4: MEJORA DE PAPER (NUEVA SECCIÓN)
    # =========================================================================
    
    logger.info("Iniciando mejora de paper...")
    
    enhancement_result = enhance_pipeline_paper(
        paper_text=original_paper,
        tool_evidence=tool_evidence,
        domain="neuroscience",
        include_discussion=True,
        citation_style="APA"
    )
    
    final_paper = enhancement_result["enhanced_paper"]
    
    # Logging detallado de mejoras
    logger.info("✅ Paper mejorado exitosamente")
    logger.info("Mejoras aplicadas:")
    for improvement in enhancement_result["improvements"]:
        logger.info(f"  {improvement}")
    
    logger.info(f"Referencias: {enhancement_result['references_count']}")
    logger.info(f"Incremento: +{enhancement_result['percent_increase']}%")
    
    # =========================================================================
    # FASE 5: Guardado de resultados (código modificado para incluir metadata)
    # =========================================================================
    
    results = {
        "hypothesis": hypothesis,
        "paper": final_paper,
        "tool_evidence": tool_evidence,
        # ✨ NUEVA metadata de mejoras
        "paper_enhancement": {
            "improvements": enhancement_result["improvements"],
            "references_count": enhancement_result["references_count"],
            "statistics": enhancement_result["statistics"],
            "length_increase": enhancement_result["length_increase"],
            "percent_increase": enhancement_result["percent_increase"]
        }
    }
    
    logger.info("Pipeline completado con mejoras integradas")
    
    return results


# ==============================================================================
# EJEMPLO 5: Configuración por Dominio
# ==============================================================================

DOMAIN_CONFIG = {
    "neuroscience": {
        "citation_style": "APA",
        "include_discussion": True,
        "keywords_for_extraction": ["accuracy", "f1_score", "precision", "recall"]
    },
    "physics": {
        "citation_style": "APA",  # Physical Review usa APA-like
        "include_discussion": True,
        "keywords_for_extraction": ["fidelity", "gate_fidelity", "error_rate", "success_rate"]
    },
    "chemistry": {
        "citation_style": "ACS",  # American Chemical Society (usa APA como fallback)
        "include_discussion": True,
        "keywords_for_extraction": ["yield", "selectivity", "binding_affinity", "ic50"]
    },
    "mathematics": {
        "citation_style": "AMS",  # American Mathematical Society (usa APA como fallback)
        "include_discussion": True,
        "keywords_for_extraction": ["convergence_rate", "error", "iterations"]
    }
}


def integrate_with_domain_config(
    original_paper: str, 
    tool_evidence: Dict[str, Any], 
    domain: str
) -> Dict[str, Any]:
    """
    Integración usando configuración por dominio
    """
    config = DOMAIN_CONFIG.get(domain, DOMAIN_CONFIG["neuroscience"])
    
    result = enhance_pipeline_paper(
        paper_text=original_paper,
        tool_evidence=tool_evidence,
        domain=domain,
        include_discussion=config["include_discussion"],
        citation_style=config["citation_style"]
    )
    
    return result


# ==============================================================================
# CHECKLIST DE INTEGRACIÓN
# ==============================================================================

"""
CHECKLIST PARA INTEGRAR EN UN PIPELINE:

□ 1. Importar servicio:
     from app.services.paper_enhancement import enhance_pipeline_paper

□ 2. Localizar generación de paper (buscar "publisher_agent.run" o similar)

□ 3. Agregar mejora después de generar paper:
     enhancement_result = enhance_pipeline_paper(...)
     final_paper = enhancement_result["enhanced_paper"]

□ 4. Agregar logging de mejoras (opcional pero recomendado):
     for improvement in enhancement_result["improvements"]:
         logger.info(improvement)

□ 5. Actualizar guardado de resultados para incluir metadata:
     results["paper_enhancement"] = {...}

□ 6. Probar pipeline modificado:
     python execute_pipeline_v33_DOMINIO_enhanced.py

□ 7. Verificar mejoras en output:
     - Buscar "## References" en paper
     - Buscar "Statistical Analysis" en paper
     - Buscar "## Discussion" en paper

□ 8. Comparar calidad antes/después usando analyze_paper_quality_*.py

TIEMPO ESTIMADO: 10-15 minutos por pipeline
"""


# ==============================================================================
# MAIN - DEMO DE INTEGRACIÓN
# ==============================================================================

if __name__ == "__main__":
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    print("="*80)
    print("DEMO: INTEGRACIÓN DE PAPER ENHANCEMENT SERVICES")
    print("="*80)
    
    # Paper de ejemplo
    sample_paper = """# Neural Network Training Optimization

## Abstract
We present a novel optimization approach...

## Methods
Neural networks were trained using Adam optimizer...

## Results
Training accuracy: 0.891, 0.895, 0.889, 0.893, 0.890
Validation F1 score = 0.875
Test precision was 0.912

## Conclusions
The proposed method achieves state-of-the-art results...
"""
    
    # Tool evidence de ejemplo
    sample_evidence = {
        "evidence_items": [
            {
                "tool_name": "arxiv",
                "metadata": {
                    "title": "Adam: A Method for Stochastic Optimization",
                    "authors": "Kingma, D. P. and Ba, J.",
                    "year": "2014",
                    "arxiv_id": "1412.6980"
                },
                "signal_strength": 0.92
            }
        ]
    }
    
    print("\n1️⃣  INTEGRACIÓN BÁSICA:")
    print("-" * 80)
    
    enhanced_paper = integrate_basic(sample_paper, sample_evidence, "neuroscience")
    print(f"Paper mejorado: {len(enhanced_paper)} caracteres (original: {len(sample_paper)})")
    print(f"Incremento: +{((len(enhanced_paper) - len(sample_paper)) / len(sample_paper) * 100):.1f}%")
    
    print("\n2️⃣  INTEGRACIÓN CON LOGGING:")
    print("-" * 80)
    
    result = integrate_with_logging(sample_paper, sample_evidence, "neuroscience", logger)
    print(f"\nMetadata disponible: {list(result.keys())}")
    
    print("\n3️⃣  INTEGRACIÓN CON CONFIG POR DOMINIO:")
    print("-" * 80)
    
    for domain in ["neuroscience", "physics", "chemistry", "mathematics"]:
        result = integrate_with_domain_config(sample_paper, sample_evidence, domain)
        print(f"{domain:15} → {result['references_count']} referencias, {result['percent_increase']:.1f}% incremento")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETADO")
    print("="*80)
    print("\nPRÓXIMOS PASOS:")
    print("1. Modificar execute_pipeline_v33_neuroscience.py usando EJEMPLO 3")
    print("2. Ejecutar pipeline modificado")
    print("3. Comparar calidad antes/después")
    print("4. Repetir para otros dominios (physics, chemistry, mathematics)")
    print("="*80)
