#!/usr/bin/env python3
"""
Análisis de calidad de papers científicos - Dominio FÍSICA
Evalúa estructura, contenido físico y rigor científico
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Keywords de física que deben aparecer
PHYSICS_KEYWORDS = [
    "quantum", "qubit", "superposition", "entanglement", "decoherence",
    "quantum computing", "quantum algorithm", "quantum gate", "quantum circuit",
    "quantum information", "quantum state", "quantum channel", "fidelity",
    "Grover", "Shor", "VQE", "QAOA",
    "superconducting", "ion trap", "photonic",
    "gate fidelity", "coherence time", "error rate",
    "Hilbert space", "unitary", "Hamiltonian", "operator"
]


def analyze_paper_structure_physics(paper_text: str) -> Tuple[float, List[str], List[str]]:
    """
    Analiza la estructura de un paper de física
    
    Secciones esperadas:
    - Abstract
    - Introduction
    - Theory / Theoretical Framework
    - Methods / Experimental Setup
    - Results
    - Discussion
    - Conclusions
    - References
    
    Returns:
        (score, secciones_encontradas, secciones_faltantes)
    """
    expected_sections = [
        "Abstract",
        "Introduction", 
        "Theory",
        "Methods",
        "Results",
        "Discussion",
        "Conclusions",
        "References"
    ]
    
    # Alternativas aceptadas
    section_patterns = {
        "Abstract": [r"##\s*Abstract", r"\*\*Abstract\*\*"],
        "Introduction": [r"##\s*Introduction", r"##\s*1\.\s*Introduction"],
        "Theory": [r"##\s*Theory", r"##\s*Theoretical Framework", r"##\s*Quantum Framework"],
        "Methods": [r"##\s*Methods", r"##\s*Methodology", r"##\s*Experimental Setup", r"##\s*Implementation"],
        "Results": [r"##\s*Results", r"##\s*Experimental Results", r"##\s*Numerical Results"],
        "Discussion": [r"##\s*Discussion", r"##\s*Analysis"],
        "Conclusions": [r"##\s*Conclusions?", r"##\s*Summary"],
        "References": [r"##\s*References", r"##\s*Bibliography"]
    }
    
    found_sections = []
    missing_sections = []
    
    for section, patterns in section_patterns.items():
        found = False
        for pattern in patterns:
            if re.search(pattern, paper_text, re.IGNORECASE):
                found = True
                break
        
        if found:
            found_sections.append(section)
        else:
            missing_sections.append(section)
    
    score = len(found_sections) / len(expected_sections) * 100
    
    return score, found_sections, missing_sections


def analyze_physics_content(paper_text: str) -> Tuple[float, List[str], List[str]]:
    """
    Analiza el contenido específico de física en el paper
    
    Elementos esperados:
    - Quantum formalism (kets, operators, etc.)
    - Algorithm descriptions (VQE, QAOA, Grover, Shor)
    - Hardware specifications (qubits, gates, coherence)
    - Quantitative metrics (fidelity, error rates, etc.)
    - Theoretical framework (Hamiltonian, unitary operations)
    - Experimental/numerical results
    - Comparison with classical algorithms
    - Error analysis
    - Circuit diagrams or descriptions
    - Scalability discussion
    
    Returns:
        (score, elementos_encontrados, elementos_faltantes)
    """
    elements = {
        "Quantum_formalism": [
            r"\|[0-9⟩]+\>",  # Ket notation
            r"\<[0-9⟨]+\|",  # Bra notation
            r"Hilbert space",
            r"wave function",
            r"quantum state"
        ],
        "Algorithm_descriptions": [
            r"\b(VQE|QAOA|Grover|Shor)\b",
            r"quantum algorithm",
            r"variational",
            r"optimization"
        ],
        "Hardware_specs": [
            r"qubit",
            r"superconducting",
            r"ion trap",
            r"photonic",
            r"quantum gate"
        ],
        "Quantitative_metrics": [
            r"fidelity",
            r"error rate",
            r"coherence time",
            r"gate fidelity",
            r"\d+\.?\d*\s*%",  # Percentages
            r"\d+\.?\d*\s*(ns|μs|ms)"  # Time units
        ],
        "Theoretical_framework": [
            r"Hamiltonian",
            r"unitary",
            r"operator",
            r"eigenvalue",
            r"eigenvector"
        ],
        "Results": [
            r"(experimental|numerical|simulation)\s+results?",
            r"measurements?",
            r"observations?"
        ],
        "Classical_comparison": [
            r"classical algorithm",
            r"classical computer",
            r"quantum advantage",
            r"speedup"
        ],
        "Error_analysis": [
            r"error",
            r"noise",
            r"decoherence",
            r"mitigation"
        ],
        "Circuit_description": [
            r"quantum circuit",
            r"gate sequence",
            r"circuit depth"
        ],
        "Scalability": [
            r"scalability",
            r"scaling",
            r"multi-qubit",
            r"system size"
        ]
    }
    
    found_elements = []
    missing_elements = []
    
    for element, patterns in elements.items():
        found = False
        for pattern in patterns:
            if re.search(pattern, paper_text, re.IGNORECASE):
                found = True
                break
        
        if found:
            found_elements.append(element)
        else:
            missing_elements.append(element)
    
    score = len(found_elements) / len(elements) * 100
    
    return score, found_elements, missing_elements


def analyze_physics_rigor(paper_text: str) -> Tuple[float, List[str], List[str]]:
    """
    Analiza el rigor científico del paper de física
    
    Criterios:
    - Mathematical formulation
    - Algorithm complexity analysis
    - Error bounds or uncertainty
    - Reproducibility details
    - Hardware specifications
    - Comparison with literature
    - Statistical analysis
    - Limitations discussed
    - References cited
    
    Returns:
        (score, criterios_cumplidos, criterios_faltantes)
    """
    criteria = {
        "Mathematical_formulation": [
            r"equation",
            r"Hamiltonian",
            r"operator",
            r"matrix"
        ],
        "Complexity_analysis": [
            r"O\([nN]\^?\d*\)",  # Big-O notation
            r"complexity",
            r"polynomial",
            r"exponential"
        ],
        "Error_bounds": [
            r"error bound",
            r"uncertainty",
            r"confidence interval",
            r"standard deviation"
        ],
        "Reproducibility": [
            r"reproducib",
            r"repeated",
            r"parameter",
            r"setting"
        ],
        "Hardware_details": [
            r"qubit",
            r"processor",
            r"quantum computer",
            r"IBM|Google|Rigetti"  # Platforms
        ],
        "Literature_comparison": [
            r"previous work",
            r"compared to",
            r"literature",
            r"state-of-the-art"
        ],
        "Statistical_analysis": [
            r"statistical",
            r"p-value",
            r"significance",
            r"average"
        ],
        "Limitations": [
            r"limitation",
            r"challenge",
            r"future work",
            r"constraint"
        ],
        "References": [
            r"##\s*References",
            r"\[\d+\]",  # Citation markers
            r"et al\."
        ]
    }
    
    met_criteria = []
    unmet_criteria = []
    
    for criterion, patterns in criteria.items():
        met = False
        for pattern in patterns:
            if re.search(pattern, paper_text, re.IGNORECASE):
                met = True
                break
        
        if met:
            met_criteria.append(criterion)
        else:
            unmet_criteria.append(criterion)
    
    score = len(met_criteria) / len(criteria) * 100
    
    return score, met_criteria, unmet_criteria


def count_keywords(paper_text: str) -> Tuple[int, float, List[str]]:
    """
    Cuenta keywords de física en el paper
    
    Returns:
        (num_encontrados, coverage, keywords_encontrados)
    """
    text_lower = paper_text.lower()
    found_keywords = []
    
    for keyword in PHYSICS_KEYWORDS:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    coverage = len(found_keywords) / len(PHYSICS_KEYWORDS) * 100
    
    return len(found_keywords), coverage, found_keywords


def compare_with_standards_physics(
    structure_score: float,
    content_score: float,
    rigor_score: float
) -> Dict[str, bool]:
    """
    Compara con estándares de journals de física de alto impacto
    
    Journals de referencia:
    - Physical Review Letters (PRL): >85% en todas las categorías
    - Nature Physics: >90% estructura, >85% contenido/rigor
    - Science: >90% en todas las categorías
    - Physical Review X: >80% en todas las categorías
    
    Returns:
        Dict con cumplimiento de estándares por journal
    """
    standards = {
        "Physical Review Letters": all([
            structure_score >= 85,
            content_score >= 85,
            rigor_score >= 85
        ]),
        "Nature Physics": all([
            structure_score >= 90,
            content_score >= 85,
            rigor_score >= 85
        ]),
        "Science": all([
            structure_score >= 90,
            content_score >= 90,
            rigor_score >= 90
        ]),
        "Physical Review X": all([
            structure_score >= 80,
            content_score >= 80,
            rigor_score >= 80
        ])
    }
    
    return standards


def get_quality_rating(overall_score: float) -> Tuple[str, str]:
    """
    Obtiene rating de calidad basado en score
    
    Returns:
        (rating, emoji)
    """
    if overall_score >= 90:
        return "EXCELENTE", "⭐⭐⭐⭐⭐"
    elif overall_score >= 80:
        return "MUY BUENO", "⭐⭐⭐⭐"
    elif overall_score >= 70:
        return "BUENO", "⭐⭐⭐"
    elif overall_score >= 60:
        return "ACEPTABLE", "⭐⭐"
    else:
        return "NECESITA MEJORAS", "⭐"


def analyze_physics_paper_quality(json_file: str) -> None:
    """
    Analiza la calidad de papers de física desde archivo JSON
    
    Args:
        json_file: Ruta al archivo JSON con resultados del pipeline
    """
    print("=" * 80)
    print("🌌 ANÁLISIS DE CALIDAD - PHYSICS PAPERS")
    print("=" * 80)
    
    # Cargar resultados
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    runs = data.get("runs", [])
    stats = data.get("statistics", {})
    
    print(f"\n📁 Archivo: {json_file}")
    print(f"🔢 Runs analizados: {len(runs)}")
    
    # Analizar cada run
    all_structure_scores = []
    all_content_scores = []
    all_rigor_scores = []
    all_overall_scores = []
    
    for i, run in enumerate(runs, 1):
        print(f"\n{'='*80}")
        print(f"📄 RUN {i}/{len(runs)}")
        print(f"{'='*80}")
        
        # Extraer paper
        paper_text = run.get("phases", {}).get("publication", {}).get("text", "")
        
        if not paper_text:
            print("⚠️  No se encontró texto del paper")
            continue
        
        # Análisis de estructura
        struct_score, found_sections, missing_sections = analyze_paper_structure_physics(paper_text)
        all_structure_scores.append(struct_score)
        
        print(f"\n📋 ESTRUCTURA: {struct_score:.1f}% ({len(found_sections)}/{len(found_sections) + len(missing_sections)} secciones)")
        print(f"   ✅ Encontradas: {', '.join(found_sections)}")
        if missing_sections:
            print(f"   ❌ Faltantes: {', '.join(missing_sections)}")
        
        # Análisis de contenido
        content_score, found_content, missing_content = analyze_physics_content(paper_text)
        all_content_scores.append(content_score)
        
        print(f"\n⚛️  CONTENIDO FÍSICO: {content_score:.1f}% ({len(found_content)}/{len(found_content) + len(missing_content)} elementos)")
        print(f"   ✅ Incluidos: {', '.join(found_content)}")
        if missing_content:
            print(f"   ❌ Faltantes: {', '.join(missing_content)}")
        
        # Análisis de rigor
        rigor_score, met_criteria, unmet_criteria = analyze_physics_rigor(paper_text)
        all_rigor_scores.append(rigor_score)
        
        print(f"\n🔬 RIGOR CIENTÍFICO: {rigor_score:.1f}% ({len(met_criteria)}/{len(met_criteria) + len(unmet_criteria)} criterios)")
        print(f"   ✅ Cumplidos: {', '.join(met_criteria)}")
        if unmet_criteria:
            print(f"   ❌ Faltantes: {', '.join(unmet_criteria)}")
        
        # Keywords
        num_kw, kw_coverage, found_kw = count_keywords(paper_text)
        
        print(f"\n🔑 KEYWORDS: {kw_coverage:.1f}% ({num_kw}/{len(PHYSICS_KEYWORDS)} términos)")
        print(f"   Encontrados: {', '.join(found_kw[:10])}{'...' if len(found_kw) > 10 else ''}")
        
        # Score general
        overall = (struct_score + content_score + rigor_score) / 3
        all_overall_scores.append(overall)
        rating, emoji = get_quality_rating(overall)
        
        print(f"\n📊 CALIDAD GLOBAL: {overall:.1f}% - {rating} {emoji}")
        
        # Comparación con journals
        standards = compare_with_standards_physics(struct_score, content_score, rigor_score)
        
        print(f"\n📚 JOURNALS:")
        for journal, meets in standards.items():
            status = "✅ SÍ" if meets else "❌ NO"
            print(f"   {status} {journal}")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if missing_sections:
            print(f"   ⚠️  Agregar secciones: {', '.join(missing_sections)}")
        if missing_content:
            print(f"   ⚠️  Incluir: {', '.join(missing_content[:3])}")
        if unmet_criteria:
            print(f"   ⚠️  Mejorar rigor: {', '.join(unmet_criteria[:3])}")
        if kw_coverage < 70:
            print(f"   ⚠️  Aumentar keywords de física (actual: {kw_coverage:.1f}%)")
    
    # Estadísticas agregadas
    if all_overall_scores:
        import statistics
        
        print(f"\n{'='*80}")
        print("📊 ESTADÍSTICAS AGREGADAS")
        print(f"{'='*80}")
        
        print(f"\n🏆 ESTRUCTURA:")
        print(f"   Promedio: {statistics.mean(all_structure_scores):.1f}%")
        print(f"   Desv. Std: {statistics.stdev(all_structure_scores) if len(all_structure_scores) > 1 else 0:.2f}%")
        
        print(f"\n⚛️  CONTENIDO FÍSICO:")
        print(f"   Promedio: {statistics.mean(all_content_scores):.1f}%")
        print(f"   Desv. Std: {statistics.stdev(all_content_scores) if len(all_content_scores) > 1 else 0:.2f}%")
        
        print(f"\n🔬 RIGOR:")
        print(f"   Promedio: {statistics.mean(all_rigor_scores):.1f}%")
        print(f"   Desv. Std: {statistics.stdev(all_rigor_scores) if len(all_rigor_scores) > 1 else 0:.2f}%")
        
        print(f"\n📊 CALIDAD GLOBAL:")
        print(f"   Promedio: {statistics.mean(all_overall_scores):.1f}%")
        print(f"   Desv. Std: {statistics.stdev(all_overall_scores) if len(all_overall_scores) > 1 else 0:.2f}%")
        
        avg_rating, avg_emoji = get_quality_rating(statistics.mean(all_overall_scores))
        print(f"   Rating: {avg_rating} {avg_emoji}")
    
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80)


def main():
    """Punto de entrada principal"""
    if len(sys.argv) < 2:
        # Buscar archivo más reciente
        json_files = list(Path(".").glob("pipeline_v33_physics_multirun_*.json"))
        if not json_files:
            print("❌ No se encontraron archivos de resultados")
            print("Uso: python analyze_paper_quality_physics.py <archivo.json>")
            return 1
        
        json_file = str(max(json_files, key=lambda p: p.stat().st_mtime))
        print(f"📁 Usando archivo más reciente: {json_file}")
    else:
        json_file = sys.argv[1]
    
    if not Path(json_file).exists():
        print(f"❌ Archivo no encontrado: {json_file}")
        return 1
    
    analyze_physics_paper_quality(json_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
