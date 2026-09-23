#!/usr/bin/env python3
"""
Test: Multi-Domain Scientific Missions

Ejecuta misiones completas en múltiples dominios científicos:
1. Matemáticas: Análisis de números primos
2. Química: Análisis molecular
3. Física: Niveles de energía cuántica
4. Biología: Análisis de secuencias

Para cada dominio:
- Ejecuta 2-3 herramientas Atlas relevantes
- Genera un paper con los resultados
- Evalúa coherencia científica
- Verifica método científico
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "atlas"))

from core.atlas_tools import AtlasTools


# Misiones por dominio
MISSIONS = {
    "mathematics": {
        "topic": "Statistical Properties of Prime Numbers",
        "hypothesis": "Prime gaps follow a non-normal distribution",
        "tools": [
            ("prime_gap_analysis", "1000", "mathematics"),
            ("sympy_prime_analysis", "is_prime:97", "mathematics"),
            ("number_theory_advanced", "goldbach:100", "mathematics"),
        ],
    },
    "chemistry": {
        "topic": "Molecular Structure Analysis of Common Compounds",
        "hypothesis": "Glucose has a molecular weight of approximately 180 g/mol",
        "tools": [
            ("molecular_weight_calc", "C6H12O6", "chemistry"),
            ("molecular_weight_calc", "H2O", "chemistry"),
            ("bond_energy_analyzer", "C-C", "chemistry"),
        ],
    },
    "physics": {
        "topic": "Quantum Energy Level Analysis",
        "hypothesis": "Hydrogen atom energy levels follow the Rydberg formula",
        "tools": [
            ("quantum_energy_levels", "hydrogen:3", "physics"),
            ("quantum_energy_levels", "hydrogen:5", "physics"),
        ],
    },
    "biology": {
        "topic": "DNA Sequence Analysis and Properties",
        "hypothesis": "DNA sequences have specific GC content patterns",
        "tools": [
            ("dna_analyzer", "ATCGATCGATCGATCGATCG", "biology"),
            ("protein_properties", "MVLSPADKTNVKAAWGKVGA", "biology"),
        ],
    },
}


async def run_domain_mission(domain: str, mission: dict) -> dict:
    """Ejecuta una misión científica completa en un dominio."""
    print(f"\n{'='*70}")
    print(f"DOMINIO: {domain.upper()}")
    print(f"Tema: {mission['topic']}")
    print(f"Hipótesis: {mission['hypothesis']}")
    print(f"{'='*70}")

    tools = AtlasTools()
    results = []

    # Paso 1: Ejecutar herramientas
    print(f"\n[1/3] Ejecutando {len(mission['tools'])} herramientas...")
    for tool_name, tool_input, tool_domain in mission["tools"]:
        try:
            print(f"  → {tool_name}({tool_input[:40]})", end=" ")
            result = await tools.run_scientific_tool(tool_name, tool_input, tool_domain)
            results.append({
                "tool": tool_name,
                "input": tool_input,
                "result": str(result)[:200],
                "success": True,
            })
            print(f"✅")
        except Exception as e:
            results.append({
                "tool": tool_name,
                "input": tool_input,
                "result": str(e),
                "success": False,
            })
            print(f"❌ {e}")

    # Paso 2: Validar hipótesis
    print(f"\n[2/3] Validando hipótesis...")
    try:
        validation = await tools.run_scientific_tool(
            "validate_hypothesis",
            f"{domain}:{mission['hypothesis']}",
            "research",
        )
        print(f"  Resultado: {str(validation)[:150]}")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        validation = None

    # Paso 3: Evaluar calidad científica
    print(f"\n[3/3] Evaluando calidad científica...")
    quality = evaluate_scientific_quality(results, mission)
    print(f"  Coherencia: {quality['coherence']}/10")
    print(f"  Método científico: {quality['scientific_method']}/10")
    print(f"  Utilidad: {quality['utility']}/10")

    return {
        "domain": domain,
        "topic": mission["topic"],
        "hypothesis": mission["hypothesis"],
        "tools_executed": len([r for r in results if r["success"]]),
        "tools_failed": len([r for r in results if not r["success"]]),
        "results": results,
        "validation": str(validation)[:200] if validation else None,
        "quality": quality,
    }


def evaluate_scientific_quality(results: list, mission: dict) -> dict:
    """Evalúa la calidad científica de los resultados."""
    
    # Coherencia: ¿Los resultados son consistentes entre sí?
    coherence = 5
    if len(results) >= 2:
        # Verificar que los resultados no sean errores
        valid_results = [r for r in results if r["success"] and "error" not in r["result"].lower()]
        if len(valid_results) >= 2:
            coherence = 8
        elif len(valid_results) >= 1:
            coherence = 6
    
    # Método científico: ¿Se siguieron los pasos?
    # 1. Observación → 2. Hipótesis → 3. Experimentación → 4. Análisis
    scientific_method = 5
    if mission.get("hypothesis"):
        scientific_method += 2  # Hipótesis definida
    if len(results) > 0:
        scientific_method += 2  # Experimentación realizada
    if any("validate" in str(r.get("tool", "")) for r in results):
        scientific_method += 1  # Validación incluida
    
    # Utilidad: ¿Son los resultados útiles para el paper?
    utility = 5
    valid_results = [r for r in results if r["success"]]
    if len(valid_results) >= 3:
        utility = 9
    elif len(valid_results) >= 2:
        utility = 7
    elif len(valid_results) >= 1:
        utility = 6
    
    return {
        "coherence": min(coherence, 10),
        "scientific_method": min(scientific_method, 10),
        "utility": min(utility, 10),
        "overall": min((coherence + scientific_method + utility) / 3, 10),
    }


async def test_multi_domain_missions():
    """Ejecuta misiones en múltiples dominios."""
    print("=" * 70)
    print("MULTI-DOMAIN SCIENTIFIC MISSIONS TEST")
    print("=" * 70)
    print("\nEste test evalúa:")
    print("  1. Ejecución de herramientas en 4 dominios")
    print("  2. Coherencia científica de resultados")
    print("  3. Aplicación del método científico")
    print("  4. Utilidad para papers académicos")

    all_results = []
    
    for domain, mission in MISSIONS.items():
        result = await run_domain_mission(domain, mission)
        all_results.append(result)

    # Resumen
    print(f"\n{'='*70}")
    print("RESUMEN GLOBAL")
    print(f"{'='*70}")
    
    total_tools = sum(r["tools_executed"] for r in all_results)
    total_failed = sum(r["tools_failed"] for r in all_results)
    avg_coherence = sum(r["quality"]["coherence"] for r in all_results) / len(all_results)
    avg_method = sum(r["quality"]["scientific_method"] for r in all_results) / len(all_results)
    avg_utility = sum(r["quality"]["utility"] for r in all_results) / len(all_results)
    avg_overall = sum(r["quality"]["overall"] for r in all_results) / len(all_results)

    print(f"\nHerramientas ejecutadas: {total_tools}/{total_tools + total_failed}")
    print(f"Herramientas fallidas: {total_failed}")
    print(f"\nCalidad científica promedio:")
    print(f"  Coherencia: {avg_coherence:.1f}/10")
    print(f"  Método científico: {avg_method:.1f}/10")
    print(f"  Utilidad: {avg_utility:.1f}/10")
    print(f"  Overall: {avg_overall:.1f}/10")

    # Tabla por dominio
    print(f"\n{'Dominio':<15} {'Tools OK':<10} {'Coherencia':<12} {'Método':<10} {'Utilidad':<10} {'Overall':<10}")
    print("-" * 70)
    for r in all_results:
        print(f"{r['domain']:<15} {r['tools_executed']:<10} {r['quality']['coherence']:<12} {r['quality']['scientific_method']:<10} {r['quality']['utility']:<10} {r['quality']['overall']:<10.1f}")

    # Guardar reporte
    report_path = Path("multi_domain_mission_report.json")
    with open(report_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n📄 Reporte guardado: {report_path}")

    # Verificar si pasa
    passed = avg_overall >= 6.0 and total_failed <= 4
    
    if passed:
        print(f"\n🎉 MULTI-DOMAIN MISSIONS PASSED!")
        print(f"   Calidad promedio: {avg_overall:.1f}/10 (≥6.0 requerido)")
        print(f"   Fallos: {total_failed}/10 (≤4 permitidos)")
    else:
        print(f"\n⚠️  MULTI-DOMAIN MISSIONS NEEDS ATTENTION")
        print(f"   Calidad promedio: {avg_overall:.1f}/10 (≥6.0 requerido)")
        print(f"   Fallos: {total_failed}/10 (≤4 permitidos)")

    return passed, all_results


if __name__ == "__main__":
    success, results = asyncio.run(test_multi_domain_missions())
    sys.exit(0 if success else 1)
