#!/usr/bin/env python3
"""
Test: Complete Mission - Mathematics Deep Dive

Ejecuta una misión completa en matemáticas:
1. 5 herramientas diferentes
2. Validación de hipótesis
3. Paper con todos los resultados
4. Verificación de calidad
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "atlas"))

from core.atlas_tools import AtlasTools
from communication.paper_generator import PaperGenerator


async def test_mathematics_deep_dive():
    """Misión completa de matemáticas."""
    print("=" * 70)
    print("COMPLETE MISSION: MATHEMATICS DEEP DIVE")
    print("=" * 70)

    tools = AtlasTools()
    
    # Herramientas a ejecutar
    mission_tools = [
        ("prime_gap_analysis", "1000", "mathematics", "Prime gap distribution"),
        ("sympy_prime_analysis", "is_prime:97", "mathematics", "Prime verification"),
        ("number_theory_advanced", "goldbach:100", "mathematics", "Goldbach conjecture"),
        ("sympy_solve_equation", "x**2 - 4 = 0", "mathematics", "Equation solving"),
        ("sympy_derivative", "x**3, x", "mathematics", "Derivative calculation"),
    ]
    
    results = []
    
    # Ejecutar herramientas
    print("\n[1/3] Executing 5 mathematical tools...")
    for tool_name, tool_input, domain, description in mission_tools:
        try:
            result = await asyncio.wait_for(
                tools.run_scientific_tool(tool_name, tool_input, domain),
                timeout=60,
            )
            results.append({
                "tool": tool_name,
                "description": description,
                "input": tool_input,
                "result": str(result)[:300],
                "success": True,
            })
            print(f"  ✅ {description}: {str(result)[:60]}")
        except Exception as e:
            results.append({
                "tool": tool_name,
                "description": description,
                "input": tool_input,
                "result": str(e),
                "success": False,
            })
            print(f"  ❌ {description}: {e}")

    # Validar hipótesis
    print("\n[2/3] Validating hypothesis...")
    try:
        validation = await asyncio.wait_for(
            tools.run_scientific_tool(
                "validate_hypothesis",
                "mathematics:prime numbers have infinite twin primes",
                "research",
            ),
            timeout=30,
        )
        print(f"  Result: {str(validation)[:150]}")
    except Exception as e:
        print(f"  ⚠️  Validation error: {e}")
        validation = None

    # Generar paper
    print("\n[3/3] Generating comprehensive paper...")
    
    tool_sections = []
    experiment_ids = []
    
    for i, r in enumerate(results):
        if r["success"]:
            tool_sections.append({
                "heading": f"{r['description']} ({r['tool']})",
                "content": f"**Input:** `{r['input']}`\n\n**Result:**\n{r['result'][:500]}",
            })
            experiment_ids.append(f"math_{r['tool']}_{i}")

    sections = [
        {
            "heading": "Introduction",
            "content": "This study presents a comprehensive computational analysis of prime numbers, equation solving, and calculus using the AXIOM Atlas platform.",
        },
        {
            "heading": "Methods",
            "content": f"We employed {len([r for r in results if r['success']])} computational tools from the Atlas mathematics domain.",
        },
        {
            "heading": "Results",
            "content": "\n\n".join([f"### {s['heading']}\n{s['content']}" for s in tool_sections]),
        },
        {
            "heading": "Discussion",
            "content": "The computational results demonstrate the power of symbolic computation for mathematical analysis.",
        },
        {
            "heading": "Conclusion",
            "content": "Our analysis confirms the utility of automated mathematical tools for research.",
        },
    ]

    pg = PaperGenerator(reasoning_engine=None)
    paper = await pg.generate_paper(
        title="Comprehensive Mathematical Analysis via Computational Tools",
        abstract="This paper presents results from 5 computational mathematical tools analyzing prime numbers, equations, and calculus.",
        sections=sections,
        references=[
            "A.M.Y (2026). AXIOM Atlas Mathematical Tools.",
            "SymPy Development Team (2024). SymPy: Symbolic Mathematics.",
        ],
        knowledge_facts=[
            {"subject": "mathematics", "predicate": "analyzed_with", "object": "Atlas tools", "confidence": 0.95},
        ],
        experiment_ids=experiment_ids,
    )

    print(f"  ✅ Paper: {paper.get('title', 'Untitled')}")
    print(f"     Words: {paper.get('word_count', 0)}")
    print(f"     Sections: {paper.get('sections', 0)}")
    print(f"     Path: {paper.get('markdown_path', 'N/A')}")

    # Verificar paper
    md_path = paper.get("markdown_path", "")
    if md_path and Path(md_path).exists():
        content = Path(md_path).read_text()
        has_all_tools = all(r["tool"] in content for r in results if r["success"])
        has_data = "Data Availability" in content
        
        print(f"\n  Paper verification:")
        print(f"    {'✅' if has_all_tools else '❌'} All tools cited")
        print(f"    {'✅' if has_data else '❌'} Data Availability section")

    # Resumen
    print("\n" + "=" * 70)
    print("MISSION SUMMARY")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r["success"])
    print(f"\nTools executed: {success_count}/{len(results)}")
    print(f"Paper generated: {paper.get('word_count', 0)} words")
    print(f"Quality: {'✅ HIGH' if success_count >= 4 else '⚠️ MEDIUM'}")
    
    if success_count >= 4:
        print(f"\n🎉 MATHEMATICS DEEP DIVE COMPLETED!")
        return True
    else:
        print(f"\n⚠️  Mission incomplete")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mathematics_deep_dive())
    sys.exit(0 if success else 1)
