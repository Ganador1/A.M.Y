#!/usr/bin/env python3
"""
Análisis de Calidad para Papers Químicos v3.3
==============================================

Analiza la calidad de un paper químico generado por el pipeline v3.3
"""

import json
import sys
from typing import Dict, List, Tuple


def analyze_paper_structure_chemistry(paper_text: str) -> Tuple[float, Dict[str, bool]]:
    """
    Analiza la estructura de un paper químico.
    
    Expected sections:
    1. Abstract
    2. Introduction
    3. Experimental Section (Materials/Methods/Synthesis)
    4. Results and Discussion
    5. Conclusions
    6. References
    7. Supporting Information (optional)
    """
    paper_lower = paper_text.lower()
    
    sections = {
        "Abstract": any(marker in paper_lower for marker in ["abstract", "# abstract"]),
        "Introduction": any(marker in paper_lower for marker in ["introduction", "# introduction", "background"]),
        "Experimental": any(marker in paper_lower for marker in [
            "experimental", "materials and methods", "synthesis", "procedure",
            "# experimental", "# methods"
        ]),
        "Results": any(marker in paper_lower for marker in [
            "results", "discussion", "# results", "characterization"
        ]),
        "Conclusions": any(marker in paper_lower for marker in [
            "conclusion", "# conclusion", "summary"
        ]),
        "References": any(marker in paper_lower for marker in ["references", "# references", "bibliography"])
    }
    
    present_count = sum(sections.values())
    total_sections = len(sections)
    
    return (present_count / total_sections, sections)


def analyze_chemical_content(paper_text: str) -> Tuple[float, Dict[str, bool]]:
    """
    Analiza el contenido químico del paper.
    
    Expected elements:
    1. Chemical formulas/notation
    2. Synthetic procedures
    3. Characterization methods (XRD, TEM, XPS, NMR, IR, etc.)
    4. Quantitative results (yield, selectivity, TOF, etc.)
    5. Reaction conditions (temperature, pressure, time, solvent)
    6. Catalyst description
    7. Mechanistic discussion
    8. Control experiments
    9. Error analysis/statistics
    10. Comparison with literature
    """
    paper_lower = paper_text.lower()
    
    elements = {
        "Chemical_formulas": any(term in paper_text for term in [
            "Pd", "rGO", "H2", "CO", "C=C", "°C", "nm", "wt%"
        ]),
        "Synthetic_procedures": any(term in paper_lower for term in [
            "synthesis", "preparation", "procedure", "reaction", "stirred", "heated"
        ]),
        "Characterization_methods": any(term in paper_lower for term in [
            "xrd", "tem", "xps", "nmr", "ir", "spectroscopy", "diffraction", "microscopy"
        ]),
        "Quantitative_results": any(term in paper_lower for term in [
            "yield", "%", "selectivity", "conversion", "tof", "turnover"
        ]),
        "Reaction_conditions": any(term in paper_lower for term in [
            "temperature", "pressure", "solvent", "time", "catalyst loading"
        ]),
        "Catalyst_description": any(term in paper_lower for term in [
            "catalyst", "nanoparticle", "support", "active site", "surface area"
        ]),
        "Mechanistic_discussion": any(term in paper_lower for term in [
            "mechanism", "pathway", "intermediate", "activation", "deactivation"
        ]),
        "Control_experiments": any(term in paper_lower for term in [
            "control", "blank", "without catalyst", "comparison"
        ]),
        "Error_analysis": any(term in paper_lower for term in [
            "error", "standard deviation", "±", "uncertainty", "reproducibility"
        ]),
        "Literature_comparison": any(term in paper_lower for term in [
            "compared to", "literature", "reported", "previous", "state-of-the-art"
        ])
    }
    
    present_count = sum(elements.values())
    total_elements = len(elements)
    
    return (present_count / total_elements, elements)


def analyze_chemical_rigor(paper_text: str) -> Tuple[float, Dict[str, bool]]:
    """
    Analiza el rigor químico del paper.
    
    Criteria:
    1. Detailed synthetic procedure
    2. Complete characterization data
    3. Quantitative performance metrics
    4. Statistical analysis
    5. Reproducibility statement
    6. Safety considerations
    7. Scalability discussion
    8. Mechanistic insights
    9. Literature references
    """
    paper_lower = paper_text.lower()
    
    criteria = {
        "Detailed_synthesis": len([w for w in paper_lower.split() if w in [
            "synthesis", "procedure", "preparation", "method"
        ]]) >= 3,
        "Complete_characterization": len([w for w in paper_lower.split() if w in [
            "xrd", "tem", "xps", "nmr", "ir", "uv", "bet"
        ]]) >= 2,
        "Quantitative_metrics": len([w for w in paper_lower.split() if w in [
            "yield", "selectivity", "conversion", "tof", "%"
        ]]) >= 3,
        "Statistical_analysis": any(term in paper_lower for term in [
            "standard deviation", "error", "±", "average", "mean"
        ]),
        "Reproducibility": any(term in paper_lower for term in [
            "reproducible", "repeated", "triplicate", "consistency"
        ]),
        "Safety_considerations": any(term in paper_lower for term in [
            "safety", "hazard", "precaution", "handling"
        ]),
        "Scalability": any(term in paper_lower for term in [
            "scale", "industrial", "production", "scale-up"
        ]),
        "Mechanistic_insights": any(term in paper_lower for term in [
            "mechanism", "pathway", "activation", "intermediate"
        ]),
        "References_cited": "references" in paper_lower or "bibliography" in paper_lower
    }
    
    present_count = sum(criteria.values())
    total_criteria = len(criteria)
    
    return (present_count / total_criteria, criteria)


def check_chemistry_keywords(paper_text: str, chemistry_keywords: List[str]) -> Tuple[float, List[str]]:
    """Verifica la presencia de keywords químicos"""
    paper_lower = paper_text.lower()
    found = [kw for kw in chemistry_keywords if kw.lower() in paper_lower]
    coverage = len(found) / len(chemistry_keywords)
    return (coverage, found)


def compare_with_standards_chemistry(
    structure_score: float,
    content_score: float,
    rigor_score: float,
    keyword_score: float
) -> Dict[str, bool]:
    """
    Compara con estándares de journals químicos top.
    
    Standards:
    - Journal of the American Chemical Society (JACS): >85% all categories
    - Angewandte Chemie: >80% all categories
    - Chemical Science: >75% structure, >80% content/rigor
    """
    standards = {
        "JACS": all([
            structure_score >= 0.85,
            content_score >= 0.85,
            rigor_score >= 0.85,
            keyword_score >= 0.70
        ]),
        "Angewandte_Chemie": all([
            structure_score >= 0.80,
            content_score >= 0.80,
            rigor_score >= 0.80,
            keyword_score >= 0.65
        ]),
        "Chemical_Science": all([
            structure_score >= 0.75,
            content_score >= 0.80,
            rigor_score >= 0.80,
            keyword_score >= 0.60
        ])
    }
    
    return standards


def analyze_chemistry_paper(json_file: str):
    """Analiza un paper químico desde el archivo JSON del pipeline"""
    
    print("\n" + "=" * 80)
    print("🧪 ANÁLISIS DE CALIDAD - PAPER QUÍMICO v3.3")
    print("=" * 80)
    print()
    
    # Cargar JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    paper_text = data["publication"]["text"]
    
    print(f"📄 Archivo: {json_file}")
    print(f"🔬 Dominio: {data.get('domain', 'N/A')}")
    print(f"📝 Palabras: {data['publication']['word_count']}")
    print(f"🏆 Score pipeline: {data['scores']['overall']:.3f}")
    print()
    
    # 1. Estructura
    structure_score, sections = analyze_paper_structure_chemistry(paper_text)
    
    print("📋 ESTRUCTURA DEL PAPER:")
    print(f"   Score: {structure_score:.1%} ({sum(sections.values())}/{len(sections)} secciones)")
    print()
    print("   Secciones presentes:")
    for section, present in sections.items():
        status = "✅" if present else "❌"
        print(f"      {status} {section}")
    print()
    
    # 2. Contenido químico
    content_score, elements = analyze_chemical_content(paper_text)
    
    print("🔬 CONTENIDO QUÍMICO:")
    print(f"   Score: {content_score:.1%} ({sum(elements.values())}/{len(elements)} elementos)")
    print()
    print("   Elementos presentes:")
    for element, present in elements.items():
        status = "✅" if present else "❌"
        print(f"      {status} {element.replace('_', ' ')}")
    print()
    
    # 3. Rigor químico
    rigor_score, criteria = analyze_chemical_rigor(paper_text)
    
    print("⚗️ RIGOR QUÍMICO:")
    print(f"   Score: {rigor_score:.1%} ({sum(criteria.values())}/{len(criteria)} criterios)")
    print()
    print("   Criterios cumplidos:")
    for criterion, met in criteria.items():
        status = "✅" if met else "❌"
        print(f"      {status} {criterion.replace('_', ' ')}")
    print()
    
    # 4. Keywords
    chemistry_keywords = [
        "catalyst", "catalysis", "synthesis", "nanoparticle", "palladium",
        "graphene", "oxide", "hydrogenation", "alkyne", "alkene", "selectivity",
        "yield", "characterization", "XRD", "TEM", "XPS", "kinetics",
        "mechanism", "reaction", "temperature", "solvent", "TOF", "conversion",
        "spectroscopy", "support", "metal", "surface", "particle"
    ]
    
    keyword_score, keywords_found = check_chemistry_keywords(paper_text, chemistry_keywords)
    
    print("🔍 KEYWORDS QUÍMICOS:")
    print(f"   Score: {keyword_score:.1%} ({len(keywords_found)}/{len(chemistry_keywords)} términos)")
    print()
    if keywords_found:
        print(f"   Encontrados: {', '.join(keywords_found[:10])}...")
    print()
    
    # 5. Score global
    overall_quality = (
        structure_score * 0.25 +
        content_score * 0.30 +
        rigor_score * 0.30 +
        keyword_score * 0.15
    )
    
    print("=" * 80)
    print("📊 CALIDAD GLOBAL DEL PAPER QUÍMICO")
    print("=" * 80)
    print()
    print(f"   📋 Estructura:        {structure_score:.1%}")
    print(f"   🔬 Contenido químico: {content_score:.1%}")
    print(f"   ⚗️ Rigor químico:     {rigor_score:.1%}")
    print(f"   🔍 Keywords:          {keyword_score:.1%}")
    print()
    print(f"   🏆 CALIDAD GLOBAL:    {overall_quality:.1%}")
    print()
    
    # Rating
    if overall_quality >= 0.90:
        rating = "EXCELENTE ⭐⭐⭐⭐⭐"
    elif overall_quality >= 0.80:
        rating = "MUY BUENO ⭐⭐⭐⭐"
    elif overall_quality >= 0.70:
        rating = "BUENO ⭐⭐⭐"
    elif overall_quality >= 0.60:
        rating = "ACEPTABLE ⭐⭐"
    else:
        rating = "NECESITA MEJORAS ⭐"
    
    print(f"   Clasificación: {rating}")
    print()
    
    # 6. Comparación con journals
    standards = compare_with_standards_chemistry(
        structure_score, content_score, rigor_score, keyword_score
    )
    
    print("📚 COMPARACIÓN CON JOURNALS:")
    print()
    for journal, meets in standards.items():
        status = "✅ SÍ" if meets else "❌ NO"
        print(f"   {status} {journal.replace('_', ' ')}")
    print()
    
    # 7. Recomendaciones
    print("💡 RECOMENDACIONES:")
    print()
    
    if structure_score < 0.80:
        missing_sections = [s for s, p in sections.items() if not p]
        print(f"   ⚠️  Agregar secciones faltantes: {', '.join(missing_sections)}")
    
    if content_score < 0.80:
        missing_elements = [e for e, p in elements.items() if not p][:3]
        print(f"   ⚠️  Incluir elementos químicos: {', '.join(missing_elements)}")
    
    if rigor_score < 0.80:
        missing_criteria = [c for c, m in criteria.items() if not m][:3]
        print(f"   ⚠️  Mejorar rigor en: {', '.join(missing_criteria)}")
    
    if keyword_score < 0.70:
        print(f"   ⚠️  Aumentar cobertura de keywords químicos ({keyword_score:.1%} actual)")
    
    if overall_quality >= 0.80:
        print("   ✅ Paper de alta calidad - listo para revisión")
    
    print()
    print("=" * 80)
    
    return {
        "structure_score": structure_score,
        "content_score": content_score,
        "rigor_score": rigor_score,
        "keyword_score": keyword_score,
        "overall_quality": overall_quality,
        "rating": rating,
        "meets_standards": standards
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Buscar el archivo JSON más reciente de chemistry
        import glob
        import os
        
        chemistry_files = glob.glob("pipeline_v33_chemistry_*.json")
        
        if not chemistry_files:
            print("❌ No se encontraron archivos de química v3.3")
            print()
            print("Uso: python analyze_paper_quality_chemistry.py <archivo.json>")
            sys.exit(1)
        
        # Usar el archivo multirun si existe, sino el más reciente
        multirun_files = [f for f in chemistry_files if "multirun" in f]
        
        if multirun_files:
            json_file = max(multirun_files, key=os.path.getctime)
            print(f"\n📊 Analizando archivo multirun más reciente: {json_file}")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                multirun_data = json.load(f)
            
            # Analizar el primer run como ejemplo
            if "individual_results" in multirun_data and multirun_data["individual_results"]:
                print("\n🔬 Analizando Run #1 del multirun...\n")
                
                # Crear archivo temporal con el primer run
                temp_file = "temp_chemistry_run1.json"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(multirun_data["individual_results"][0], f, indent=2, ensure_ascii=False)
                
                result = analyze_chemistry_paper(temp_file)
                
                # Limpiar archivo temporal
                os.remove(temp_file)
                
                # Mostrar estadísticas multirun
                print("\n" + "=" * 80)
                print("📈 ESTADÍSTICAS MULTI-RUN")
                print("=" * 80)
                print()
                stats = multirun_data["statistics"]
                print(f"   Runs ejecutados: {multirun_data['num_runs']}")
                print(f"   Score promedio:  {stats['scores']['mean']:.3f}")
                print(f"   CV (variabilidad): {stats['scores']['cv_percent']:.2f}%")
                print(f"   Keywords promedio: {stats['keyword_coverage']['mean']:.1%}")
                print()
        else:
            json_file = max(chemistry_files, key=os.path.getctime)
            result = analyze_chemistry_paper(json_file)
    else:
        json_file = sys.argv[1]
        result = analyze_chemistry_paper(json_file)
