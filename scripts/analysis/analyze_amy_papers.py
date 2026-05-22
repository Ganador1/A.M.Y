#!/usr/bin/env python3
"""
A.M.Y Paper Analysis Tool

Analiza papers generados autónomamente por A.M.Y evaluando:
1. Estructura del método científico
2. Relevancia científica
3. Calidad de datos
4. Verificabilidad
5. Cobertura de dominios
"""
import json
import re
from pathlib import Path
from datetime import datetime

PAPERS_DIR = Path("/Volumes/Ganador disk/A.M.Y/papers")

def analyze_papers():
    """Analiza todos los papers generados por A.M.Y."""
    
    # Encontrar papers recientes (generados hoy)
    today = datetime.now().strftime("%Y%m%d")
    papers = sorted(PAPERS_DIR.glob(f"*_{today}_*.md"))
    
    if not papers:
        print("No se encontraron papers recientes.")
        return
    
    print("=" * 80)
    print(f"ANÁLISIS DE PAPERS GENERADOS POR A.M.Y")
    print(f"Total papers encontrados: {len(papers)}")
    print("=" * 80)
    
    results = {
        "total_papers": len(papers),
        "domains": {},
        "scientific_method_score": 0,
        "relevance_score": 0,
        "quality_score": 0,
        "papers": [],
    }
    
    for paper_path in papers:
        analysis = analyze_single_paper(paper_path)
        results["papers"].append(analysis)
        
        # Contar por dominio
        domain = analysis.get("domain", "unknown")
        results["domains"][domain] = results["domains"].get(domain, 0) + 1
    
    # Calcular promedios
    if results["papers"]:
        results["scientific_method_score"] = sum(p["scientific_method_score"] for p in results["papers"]) / len(results["papers"])
        results["relevance_score"] = sum(p["relevance_score"] for p in results["papers"]) / len(results["papers"])
        results["quality_score"] = sum(p["quality_score"] for p in results["papers"]) / len(results["papers"])
    
    # Reporte
    print("\n" + "=" * 80)
    print("RESUMEN EJECUTIVO")
    print("=" * 80)
    print(f"📄 Total papers analizados: {results['total_papers']}")
    print(f"📊 Puntuación método científico: {results['scientific_method_score']:.1f}/10")
    print(f"🔬 Puntuación relevancia: {results['relevance_score']:.1f}/10")
    print(f"✨ Puntuación calidad general: {results['quality_score']:.1f}/10")
    print(f"\n🌍 Distribución por dominios:")
    for domain, count in sorted(results["domains"].items(), key=lambda x: -x[1]):
        print(f"   • {domain}: {count} papers")
    
    # Guardar reporte
    report_path = Path("/Volumes/Ganador disk/A.M.Y/amy_paper_analysis.json")
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Reporte guardado en: {report_path}")
    
    return results


def analyze_single_paper(paper_path: Path) -> dict:
    """Analiza un paper individual."""
    content = paper_path.read_text(encoding="utf-8")
    
    # Detectar dominio del título
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Unknown"
    
    domain = "unknown"
    if "Mathematical" in title:
        domain = "mathematics"
    elif "DNA" in title or "Protein" in title:
        domain = "biology"
    elif "Quantum" in title or "Energy" in title:
        domain = "physics"
    elif "Statistical" in title:
        domain = "statistics"
    elif "Molecular" in title or "Chemistry" in title:
        domain = "chemistry"
    
    # Verificar estructura del método científico
    has_abstract = "## Abstract" in content
    has_intro = "## Introduction" in content
    has_methods = "## Methods" in content
    has_results = "## Results" in content
    has_discussion = "## Discussion" in content
    has_conclusion = "## Conclusion" in content
    has_references = "## References" in content
    
    scientific_sections = sum([has_abstract, has_intro, has_methods, has_results, has_discussion, has_conclusion, has_references])
    scientific_method_score = (scientific_sections / 7) * 10
    
    # Verificar datos computacionales
    has_data = "**Result:**" in content
    has_experiments = "Experiment `" in content
    has_tool_results = "### " in content and "(" in content
    
    # Calcular relevancia
    relevance_indicators = [
        has_data,
        has_experiments,
        has_tool_results,
        len(re.findall(r'\d+\.\d+', content)) > 3,  # Tiene números con decimales
        "Confidence" in content,
        "Data Availability" in content,
    ]
    relevance_score = (sum(relevance_indicators) / len(relevance_indicators)) * 10
    
    # Calidad general
    word_count = len(content.split())
    has_tables = "|" in content and "---" in content
    has_equations = "=" in content or "**" in content
    
    quality_indicators = [
        word_count > 150,
        word_count > 200,
        has_tables,
        has_equations,
        "autonomously" in content.lower(),
        "verified" in content.lower(),
    ]
    quality_score = (sum(quality_indicators) / len(quality_indicators)) * 10
    
    return {
        "title": title,
        "domain": domain,
        "file": str(paper_path.name),
        "word_count": word_count,
        "scientific_method_score": round(scientific_method_score, 1),
        "relevance_score": round(relevance_score, 1),
        "quality_score": round(quality_score, 1),
        "has_all_sections": scientific_sections == 7,
        "has_computational_data": has_data and has_tool_results,
    }


if __name__ == "__main__":
    analyze_papers()
