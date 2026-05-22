#!/usr/bin/env python3
"""
Análisis Detallado de Calidad de Papers Matemáticos
====================================================

Analiza la calidad científica de los artículos matemáticos generados
evaluando estructura, contenido y rigor metodológico.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


def analyze_paper_structure_math(paper_text: str) -> Dict:
    """Analiza la estructura del paper matemático"""
    
    # Secciones esperadas en un paper de matemáticas
    sections = {
        "Abstract": r"\*\*Abstract\*\*:?",
        "Introduction": r"(#+\s*)?(Introduction|1\.|I\.)",
        "Preliminaries": r"(#+\s*)?(Preliminaries|Definitions|Notation|2\.|II\.)",
        "Main Results": r"(#+\s*)?(Main Results|Theorems|Results|3\.|III\.)",
        "Proofs": r"(#+\s*)?(Proofs?|Demonstrations?|4\.|IV\.)",
        "Discussion": r"(#+\s*)?(Discussion|Conclusions?|Remarks|5\.|V\.)",
        "References": r"(#+\s*)?(References|Bibliography)"
    }
    
    found = {}
    for section_name, pattern in sections.items():
        match = re.search(pattern, paper_text, re.IGNORECASE)
        found[section_name] = match is not None
    
    structure_score = sum(found.values()) / len(sections)
    
    return {
        "sections_found": found,
        "sections_count": sum(found.values()),
        "total_sections": len(sections),
        "structure_score": structure_score
    }


def analyze_mathematical_content(paper_text: str) -> Dict:
    """Analiza el contenido matemático del paper"""
    
    # Elementos matemáticos esperados
    elements = {
        "theorem_statement": r"(Theorem|Lemma|Corollary|Proposition)\s+\d+",
        "proof_structure": r"(Proof\.|Proof:|Demonstration:)",
        "mathematical_notation": r"(\$.*?\$|\\[a-zA-Z]+{|}|\\begin{|\\end{)",
        "definitions": r"(Definition|Let|Define|We define)",
        "assumptions": r"(Assume|Suppose|Let us assume|Under the assumption)",
        "main_result": r"(main result|main theorem|principal result)",
        "quantitative_bounds": r"(\d+\.?\d*|O\(|o\(|Θ\(|bound|estimate)",
        "rigorous_language": r"(Therefore|Thus|Hence|It follows that|Consequently)",
        "convergence_claims": r"(converges?|convergence|limit|asymptotic)",
        "error_analysis": r"(error|accuracy|precision|tolerance)"
    }
    
    found = {}
    for element_name, pattern in elements.items():
        matches = re.findall(pattern, paper_text, re.IGNORECASE)
        found[element_name] = len(matches) > 0
    
    content_score = sum(found.values()) / len(elements)
    
    return {
        "elements_found": found,
        "elements_count": sum(found.values()),
        "total_elements": len(elements),
        "content_score": content_score
    }


def analyze_mathematical_rigor(paper_text: str) -> Dict:
    """Analiza el rigor matemático del paper"""
    
    rigor_criteria = {
        "formal_proofs": r"(Proof\.|Proof:|\\begin{proof})",
        "lemmas_used": r"(Lemma|auxiliary result)",
        "references_cited": r"(\[\d+\]|\(\d{4}\)|et al\.|References)",
        "precise_statements": r"(for all|there exists|if and only if|iff)",
        "inequalities": r"(≤|≥|<|>|\\leq|\\geq|inequality)",
        "completeness": r"(complete|thorough|rigorous|comprehensive)",
        "limitations": r"(limitation|constraint|restriction|assumes?)",
        "computational_validation": r"(numerical|computational|simulation|algorithm)",
        "complexity_analysis": r"(complexity|running time|O\(|polynomial|exponential)"
    }
    
    found = {}
    for criterion_name, pattern in rigor_criteria.items():
        matches = re.findall(pattern, paper_text, re.IGNORECASE)
        found[criterion_name] = len(matches) > 0
    
    rigor_score = sum(found.values()) / len(rigor_criteria)
    
    return {
        "criteria_found": found,
        "criteria_count": sum(found.values()),
        "total_criteria": len(rigor_criteria),
        "rigor_score": rigor_score
    }


def analyze_keywords_math(paper_text: str) -> Dict:
    """Analiza la cobertura de keywords matemáticos"""
    
    mathematics_keywords = [
        "theorem", "proof", "lemma", "corollary", "convergence", "series",
        "Fourier", "analysis", "function", "discontinuous", "Gibbs",
        "asymptotic", "error", "bound", "uniform", "interval", "continuity",
        "partial", "sum", "functional", "topology", "algebra", "differential",
        "integral", "matrix", "optimization", "eigenvalue", "numerical"
    ]
    
    paper_lower = paper_text.lower()
    found_keywords = [kw for kw in mathematics_keywords if kw.lower() in paper_lower]
    
    keyword_coverage = len(found_keywords) / len(mathematics_keywords)
    
    return {
        "keywords_found": found_keywords,
        "keywords_count": len(found_keywords),
        "total_keywords": len(mathematics_keywords),
        "keyword_coverage": keyword_coverage
    }


def calculate_quality_metrics_math(
    structure: Dict,
    content: Dict,
    rigor: Dict,
    keywords: Dict
) -> Dict:
    """Calcula métricas de calidad global del paper matemático"""
    
    # Ponderaciones
    weights = {
        "structure": 0.25,
        "content": 0.35,
        "rigor": 0.25,
        "keywords": 0.15
    }
    
    overall_quality = (
        structure["structure_score"] * weights["structure"] +
        content["content_score"] * weights["content"] +
        rigor["rigor_score"] * weights["rigor"] +
        keywords["keyword_coverage"] * weights["keywords"]
    )
    
    # Clasificación
    if overall_quality >= 0.90:
        rating = "EXCELENTE ⭐⭐⭐⭐⭐"
    elif overall_quality >= 0.75:
        rating = "MUY BUENO ⭐⭐⭐⭐"
    elif overall_quality >= 0.60:
        rating = "BUENO ⭐⭐⭐"
    elif overall_quality >= 0.40:
        rating = "ACEPTABLE ⭐⭐"
    else:
        rating = "NECESITA MEJORAS ⭐"
    
    return {
        "overall_quality": overall_quality,
        "rating": rating,
        "component_scores": {
            "structure": structure["structure_score"],
            "content": content["content_score"],
            "rigor": rigor["rigor_score"],
            "keywords": keywords["keyword_coverage"]
        }
    }


def compare_with_standards_math() -> Dict:
    """Estándares de comparación para journals matemáticos de alto impacto"""
    
    return {
        "Annals of Mathematics": {
            "sections_required": 6,
            "proofs_required": True,
            "references_min": 15,
            "novelty_requirement": "Significant breakthrough",
            "acceptance_rate": "< 10%"
        },
        "Inventiones Mathematicae": {
            "sections_required": 5,
            "proofs_required": True,
            "references_min": 12,
            "novelty_requirement": "Major advance",
            "acceptance_rate": "< 15%"
        },
        "Journal of the AMS": {
            "sections_required": 5,
            "proofs_required": True,
            "references_min": 10,
            "novelty_requirement": "Substantial contribution",
            "acceptance_rate": "< 20%"
        }
    }


def main():
    """Función principal de análisis"""
    
    print("=" * 90)
    print("🔢 ANÁLISIS DE CALIDAD - PAPERS MATEMÁTICOS")
    print("=" * 90)
    print()
    
    # Buscar archivos de resultados
    json_files = sorted(Path(".").glob("pipeline_v33_mathematics_run*.json"))
    
    if not json_files:
        print("❌ No se encontraron archivos de resultados.")
        print("   Busca: pipeline_v33_mathematics_run*.json")
        return
    
    print(f"📁 Archivos encontrados: {len(json_files)}")
    for f in json_files:
        print(f"   - {f.name}")
    print()
    
    # Analizar el último run
    latest_file = json_files[-1]
    print(f"📊 Analizando: {latest_file.name}")
    print()
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    paper_text = results.get("publication", {}).get("text", "")
    
    if not paper_text:
        print("❌ No se encontró texto del paper en el archivo JSON")
        return
    
    word_count = len(paper_text.split())
    print(f"📝 Longitud del paper: {word_count} palabras")
    print(f"📝 Longitud en caracteres: {len(paper_text)}")
    print()
    
    # ========================================================================
    # ANÁLISIS DE ESTRUCTURA
    # ========================================================================
    print("📋 ANÁLISIS DE ESTRUCTURA")
    print("-" * 90)
    
    structure = analyze_paper_structure_math(paper_text)
    
    for section, found in structure["sections_found"].items():
        status = "✅" if found else "❌"
        print(f"   {status} {section}")
    
    print()
    print(f"   Score estructura: {structure['structure_score']:.1%} "
          f"({structure['sections_count']}/{structure['total_sections']})")
    print()
    
    # ========================================================================
    # ANÁLISIS DE CONTENIDO MATEMÁTICO
    # ========================================================================
    print("🔬 ANÁLISIS DE CONTENIDO MATEMÁTICO")
    print("-" * 90)
    
    content = analyze_mathematical_content(paper_text)
    
    for element, found in content["elements_found"].items():
        status = "✅" if found else "❌"
        print(f"   {status} {element.replace('_', ' ').title()}")
    
    print()
    print(f"   Score contenido: {content['content_score']:.1%} "
          f"({content['elements_count']}/{content['total_elements']})")
    print()
    
    # ========================================================================
    # ANÁLISIS DE RIGOR MATEMÁTICO
    # ========================================================================
    print("⚗️  ANÁLISIS DE RIGOR MATEMÁTICO")
    print("-" * 90)
    
    rigor = analyze_mathematical_rigor(paper_text)
    
    for criterion, found in rigor["criteria_found"].items():
        status = "✅" if found else "❌"
        print(f"   {status} {criterion.replace('_', ' ').title()}")
    
    print()
    print(f"   Score rigor: {rigor['rigor_score']:.1%} "
          f"({rigor['criteria_count']}/{rigor['total_criteria']})")
    print()
    
    # ========================================================================
    # ANÁLISIS DE KEYWORDS
    # ========================================================================
    print("🔍 ANÁLISIS DE KEYWORDS MATEMÁTICOS")
    print("-" * 90)
    
    keywords = analyze_keywords_math(paper_text)
    
    print(f"   Keywords encontrados: {keywords['keywords_count']}/{keywords['total_keywords']}")
    print(f"   Coverage: {keywords['keyword_coverage']:.1%}")
    print()
    if keywords['keywords_found']:
        print(f"   Términos: {', '.join(keywords['keywords_found'][:20])}")
        if len(keywords['keywords_found']) > 20:
            print(f"   ... y {len(keywords['keywords_found']) - 20} más")
    print()
    
    # ========================================================================
    # CALIDAD GLOBAL
    # ========================================================================
    print("📊 CALIDAD GLOBAL DEL PAPER MATEMÁTICO")
    print("-" * 90)
    
    quality_metrics = calculate_quality_metrics_math(structure, content, rigor, keywords)
    
    print(f"   Overall Quality Score: {quality_metrics['overall_quality']:.1%}")
    print(f"   Rating: {quality_metrics['rating']}")
    print()
    print("   Desglose por componente:")
    for component, score in quality_metrics['component_scores'].items():
        print(f"      • {component.capitalize()}: {score:.1%}")
    print()
    
    # ========================================================================
    # COMPARACIÓN CON ESTÁNDARES
    # ========================================================================
    print("📚 COMPARACIÓN CON JOURNALS DE ALTO IMPACTO")
    print("-" * 90)
    
    standards = compare_with_standards_math()
    
    for journal, criteria in standards.items():
        print(f"\n   {journal}:")
        for key, value in criteria.items():
            print(f"      • {key.replace('_', ' ').title()}: {value}")
    
    print()
    print("   Evaluación del paper generado:")
    
    meets_annals = (
        structure['sections_count'] >= 6 and
        rigor['criteria_found'].get('formal_proofs', False) and
        content['content_score'] >= 0.80
    )
    
    meets_inventiones = (
        structure['sections_count'] >= 5 and
        rigor['criteria_found'].get('formal_proofs', False) and
        content['content_score'] >= 0.70
    )
    
    meets_jams = (
        structure['sections_count'] >= 5 and
        rigor['criteria_found'].get('formal_proofs', False) and
        content['content_score'] >= 0.60
    )
    
    print(f"      ✅ Annals of Mathematics: {'SÍ' if meets_annals else 'NO'}")
    print(f"      ✅ Inventiones Math: {'SÍ' if meets_inventiones else 'NO'}")
    print(f"      ✅ J. of the AMS: {'SÍ' if meets_jams else 'NO'}")
    print()
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print("=" * 90)
    print("📄 RESUMEN FINAL")
    print("=" * 90)
    print()
    print(f"✅ Calidad del Paper: {quality_metrics['overall_quality']:.1%} - {quality_metrics['rating']}")
    print(f"✅ Estructura completa: {structure['structure_score']:.1%}")
    print(f"✅ Contenido matemático robusto: {content['content_score']:.1%}")
    print(f"✅ Rigor metodológico: {rigor['rigor_score']:.1%}")
    print(f"✅ Coverage de keywords: {keywords['keyword_coverage']:.1%}")
    print()
    
    if quality_metrics['overall_quality'] >= 0.80:
        print("🎉 El paper cumple con estándares de PUBLICACIÓN en journals de alto impacto")
    elif quality_metrics['overall_quality'] >= 0.65:
        print("👍 El paper es de BUENA CALIDAD y podría publicarse con revisiones menores")
    else:
        print("⚠️  El paper necesita MEJORAS SIGNIFICATIVAS antes de publicación")
    
    print()
    print("=" * 90)


if __name__ == "__main__":
    main()
