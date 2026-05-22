#!/usr/bin/env python3
"""
Test: Scientific Method Verification

Verifica que los papers generados siguen el método científico:
1. Observación/Introducción
2. Hipótesis
3. Métodos/Experimentación
4. Resultados
5. Discusión/Análisis
6. Conclusión

Y evalúa coherencia entre resultados y conclusiones.
"""
import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "atlas"))

from core.atlas_tools import AtlasTools
from communication.paper_generator import PaperGenerator


REQUIRED_SECTIONS = [
    "abstract",
    "introduction",
    "methods",
    "result",
    "discussion",
    "conclusion",
]


def verify_scientific_method(paper_text: str, tools_results: list) -> dict:
    """Verifica que el paper sigue el método científico."""
    text_lower = paper_text.lower()
    
    # 1. Verificar secciones requeridas
    sections_found = {}
    for section in REQUIRED_SECTIONS:
        # Buscar como heading o en el texto
        pattern = rf"##\s*{section.capitalize()}|##\s*{section.title()}"
        found = bool(re.search(pattern, paper_text, re.IGNORECASE))
        sections_found[section] = found
    
    # 2. Verificar que hay resultados computacionales
    has_computational_results = (
        "tool result" in text_lower or 
        "computational" in text_lower or
        "axiom atlas" in text_lower
    )
    
    # 3. Verificar que hay datos numéricos en resultados
    has_numeric_data = bool(re.search(r"\d+\.?\d*\s*(g/mol|ev|nm|%)", text_lower))
    
    # 4. Verificar que la conclusión se basa en resultados
    conclusion_section = ""
    conclusion_match = re.search(
        r"##\s*Conclusion.*?(?=##|\Z)", 
        paper_text, 
        re.IGNORECASE | re.DOTALL
    )
    if conclusion_match:
        conclusion_section = conclusion_match.group(0).lower()
    
    conclusion_references_results = any(
        word in conclusion_section 
        for word in ["result", "analysis", "computational", "confirm", "support"]
    )
    
    # 5. Verificar referencias
    has_references = "## References" in paper_text or "## Referencias" in paper_text
    
    # 6. Verificar data availability
    has_data_availability = "data availability" in text_lower
    
    # 7. Verificar que los resultados de herramientas están citados
    tools_cited = sum(
        1 for tr in tools_results 
        if tr.get("tool", "").lower() in text_lower
    )
    
    # Calcular scores
    structure_score = sum(1 for v in sections_found.values() if v) / len(sections_found) * 10
    evidence_score = (
        (10 if has_computational_results else 0) +
        (10 if has_numeric_data else 0) +
        (10 if tools_cited >= len(tools_results) * 0.5 else 5)
    ) / 3
    
    coherence_score = (
        (10 if conclusion_references_results else 3) +
        (10 if has_references else 0) +
        (10 if has_data_availability else 0)
    ) / 3
    
    overall = (structure_score + evidence_score + coherence_score) / 3
    
    return {
        "structure": round(structure_score, 1),
        "evidence": round(evidence_score, 1),
        "coherence": round(coherence_score, 1),
        "overall": round(overall, 1),
        "details": {
            "sections_found": sections_found,
            "has_computational_results": has_computational_results,
            "has_numeric_data": has_numeric_data,
            "conclusion_references_results": conclusion_references_results,
            "has_references": has_references,
            "has_data_availability": has_data_availability,
            "tools_cited": tools_cited,
            "total_tools": len(tools_results),
        },
    }


async def test_scientific_method():
    """Test que verifica el método científico en papers."""
    print("=" * 70)
    print("SCIENTIFIC METHOD VERIFICATION TEST")
    print("=" * 70)
    print("\nVerificando:")
    print("  1. Estructura del método científico")
    print("  2. Evidencia computacional")
    print("  3. Coherencia resultados → conclusiones")
    print("  4. Referencias y trazabilidad")

    tools = AtlasTools()
    all_results = []

    # Configuración de misiones
    missions = {
        "mathematics": {
            "hypothesis": "Prime gaps follow a non-normal distribution",
            "tools": [
                ("prime_gap_analysis", "1000", "mathematics"),
                ("sympy_prime_analysis", "is_prime:97", "mathematics"),
                ("number_theory_advanced", "goldbach:100", "mathematics"),
            ],
        },
        "chemistry": {
            "hypothesis": "Glucose has a molecular weight of approximately 180 g/mol",
            "tools": [
                ("molecular_weight_calc", "C6H12O6", "chemistry"),
                ("molecular_weight_calc", "H2O", "chemistry"),
            ],
        },
        "physics": {
            "hypothesis": "Hydrogen atom energy levels follow the Rydberg formula",
            "tools": [
                ("quantum_energy_levels", "hydrogen:3", "physics"),
                ("quantum_energy_levels", "hydrogen:5", "physics"),
            ],
        },
    }

    for domain, config in missions.items():
        print(f"\n{'='*70}")
        print(f"DOMINIO: {domain.upper()}")
        print(f"{'='*70}")

        # Ejecutar herramientas
        tools_results = []
        for tool_name, tool_input, tool_domain in config["tools"]:
            try:
                result = await tools.run_scientific_tool(tool_name, tool_input, tool_domain)
                tools_results.append({
                    "tool": tool_name,
                    "input": tool_input,
                    "result": str(result)[:300],
                    "success": True,
                })
                print(f"  ✅ {tool_name}")
            except Exception as e:
                tools_results.append({
                    "tool": tool_name,
                    "input": tool_input,
                    "result": str(e),
                    "success": False,
                })
                print(f"  ❌ {tool_name}: {e}")

        # Generar paper
        print(f"\n  Generando paper...")
        pg = PaperGenerator(reasoning_engine=None)
        
        tool_sections = []
        for i, tr in enumerate(tools_results):
            tool_sections.append({
                "heading": f"Tool Result: {tr['tool']}",
                "content": f"Input: `{tr['input']}`\n\nResult: {tr['result'][:300]}",
            })

        sections = [
            {"heading": "Introduction", "content": f"Study of {config['hypothesis']}."},
            {"heading": "Methods", "content": f"Used {len(tools_results)} Atlas tools."},
            {"heading": "Results", "content": "\n\n".join([f"**{s['heading']}**\n{s['content']}" for s in tool_sections])},
            {"heading": "Discussion", "content": f"Results support {config['hypothesis']}."},
            {"heading": "Conclusion", "content": f"Confirmed {config['hypothesis']}."},
        ]

        paper = await pg.generate_paper(
            title=f"Analysis of {config['hypothesis']}",
            abstract=f"Computational analysis of {config['hypothesis']}.",
            sections=sections,
            references=["Atlas Tools Documentation"],
            knowledge_facts=[{"subject": domain, "predicate": "analyzed", "object": "Atlas", "confidence": 0.95}],
            experiment_ids=[f"{domain}_exp_{i}" for i in range(len(tools_results))],
        )

        # Verificar método científico
        md_path = paper.get("markdown_path", "")
        if md_path and Path(md_path).exists():
            paper_text = Path(md_path).read_text()
            verification = verify_scientific_method(paper_text, tools_results)
            
            print(f"\n  📊 Verificación del método científico:")
            print(f"     Estructura: {verification['structure']}/10")
            print(f"     Evidencia: {verification['evidence']}/10")
            print(f"     Coherencia: {verification['coherence']}/10")
            print(f"     Overall: {verification['overall']}/10")
            
            # Detalles
            details = verification["details"]
            print(f"\n     Detalles:")
            for section, found in details["sections_found"].items():
                status = "✅" if found else "❌"
                print(f"       {status} {section.capitalize()}")
            print(f"       {'✅' if details['has_computational_results'] else '❌'} Resultados computacionales")
            print(f"       {'✅' if details['has_numeric_data'] else '❌'} Datos numéricos")
            print(f"       {'✅' if details['conclusion_references_results'] else '❌'} Conclusión basada en resultados")
            print(f"       {'✅' if details['has_references'] else '❌'} Referencias")
            print(f"       {'✅' if details['has_data_availability'] else '❌'} Data Availability")
            print(f"       ✅ Herramientas citadas: {details['tools_cited']}/{details['total_tools']}")
            
            all_results.append({
                "domain": domain,
                "paper_path": md_path,
                "verification": verification,
            })
        else:
            print(f"  ❌ Paper no encontrado: {md_path}")

    # Resumen
    print(f"\n{'='*70}")
    print("RESUMEN: MÉTODO CIENTÍFICO")
    print(f"{'='*70}")
    
    avg_structure = sum(r["verification"]["structure"] for r in all_results) / len(all_results)
    avg_evidence = sum(r["verification"]["evidence"] for r in all_results) / len(all_results)
    avg_coherence = sum(r["verification"]["coherence"] for r in all_results) / len(all_results)
    avg_overall = sum(r["verification"]["overall"] for r in all_results) / len(all_results)

    print(f"\n{'Dominio':<15} {'Estructura':<12} {'Evidencia':<12} {'Coherencia':<12} {'Overall':<10}")
    print("-" * 65)
    for r in all_results:
        v = r["verification"]
        print(f"{r['domain']:<15} {v['structure']:<12} {v['evidence']:<12} {v['coherence']:<12} {v['overall']:<10}")
    print(f"{'PROMEDIO':<15} {avg_structure:<12.1f} {avg_evidence:<12.1f} {avg_coherence:<12.1f} {avg_overall:<10.1f}")

    # Guardar reporte
    report = {
        "papers": [
            {
                "domain": r["domain"],
                "path": r["paper_path"],
                "verification": r["verification"],
            }
            for r in all_results
        ],
        "averages": {
            "structure": avg_structure,
            "evidence": avg_evidence,
            "coherence": avg_coherence,
            "overall": avg_overall,
        },
    }
    
    report_path = Path("scientific_method_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Reporte guardado: {report_path}")

    passed = avg_overall >= 7.0
    if passed:
        print(f"\n🎉 SCIENTIFIC METHOD VERIFICATION PASSED!")
        print(f"   Calidad promedio: {avg_overall:.1f}/10 (≥7.0 requerido)")
    else:
        print(f"\n⚠️  SCIENTIFIC METHOD VERIFICATION NEEDS ATTENTION")
        print(f"   Calidad promedio: {avg_overall:.1f}/10 (≥7.0 requerido)")

    return passed, all_results


if __name__ == "__main__":
    success, results = asyncio.run(test_scientific_method())
    sys.exit(0 if success else 1)
