#!/usr/bin/env python3
"""
Test script para comparar prompts antiguos vs mejorados (v2.0)

Este script ejecuta el mismo conjunto de pruebas del análisis de calidad
pero con los prompts mejorados para comparar resultados.

Basado en: analysis_agent_quality.md
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.huggingface_agent_wrapper import HuggingFaceAgentWrapper
from app.services.improved_agent_prompts import (
    validate_bio_hypothesis,
    get_agent_parameters
)
import json


async def test_bio_hypothesis_improved():
    """Test Bio Hypothesis con prompts mejorados"""
    print("\n" + "=" * 80)
    print("🧬 TEST 1: BIO HYPOTHESIS con Prompts Mejorados v2.0")
    print("=" * 80)

    wrapper = HuggingFaceAgentWrapper(
        agent_role="bio_hypothesis",
        use_improved_prompts=True  # ✨ Usando prompts v2.0
    )

    # Mismo caso de prueba que en analysis_agent_quality.md
    prompt = """Generate a hypothesis about the relationship between gut microbiome composition
and Alzheimer's disease progression, focusing on specific bacterial species and quantifiable
biomarkers."""

    print(f"\n📋 User Prompt:")
    print(prompt)
    print(f"\n⚙️ Parameters: {get_agent_parameters('bio_hypothesis')}")
    print("\n🤖 Generating hypothesis (this may take 30-60 seconds)...\n")

    response = await wrapper.generate_async(prompt)

    print("=" * 80)
    print("📤 RESPONSE:")
    print("=" * 80)
    print(response)
    print("=" * 80)

    # Validate response quality
    print("\n📊 QUALITY VALIDATION:")
    print("=" * 80)
    validation = validate_bio_hypothesis(response)

    if validation["valid"]:
        print(f"✅ Valid hypothesis (Score: {validation['score']}/10)")
    else:
        print(f"❌ Invalid hypothesis (Score: {validation['score']}/10)")

    if validation["issues"]:
        print("\n⚠️ Issues found:")
        for issue in validation["issues"]:
            print(f"   - {issue}")
    else:
        print("\n✅ No issues found - excellent quality!")

    return {
        "agent": "bio_hypothesis",
        "score": validation["score"],
        "valid": validation["valid"],
        "response_length": len(response)
    }


async def test_orchestrator_improved():
    """Test Orchestrator con prompts mejorados"""
    print("\n" + "=" * 80)
    print("🎯 TEST 2: ORCHESTRATOR con Prompts Mejorados v2.0")
    print("=" * 80)

    wrapper = HuggingFaceAgentWrapper(
        agent_role="orchestrator",
        use_improved_prompts=True
    )

    prompt = """Create a research plan to study CRISPR-Cas9 gene editing for treating
sickle cell disease. Include timeline, milestones, resources, and risk mitigation."""

    print(f"\n📋 User Prompt:")
    print(prompt)
    print(f"\n⚙️ Parameters: {get_agent_parameters('orchestrator')}")
    print("\n🤖 Generating research plan (this may take 30-60 seconds)...\n")

    response = await wrapper.generate_async(prompt)

    print("=" * 80)
    print("📤 RESPONSE:")
    print("=" * 80)
    print(response)
    print("=" * 80)

    # Manual quality checks
    has_timeline = any(week in response.lower() for week in ['week', 'month', 'phase'])
    has_numbers = any(char.isdigit() for char in response)
    has_milestones = 'milestone' in response.lower()
    has_resources = any(word in response.lower() for word in ['personnel', 'equipment', 'budget'])

    score = 5  # Base
    if has_timeline:
        score += 1
    if has_numbers:
        score += 1
    if has_milestones:
        score += 1
    if has_resources:
        score += 1
    if len(response) > 1000:  # Detailed
        score += 1

    print("\n📊 QUALITY ASSESSMENT:")
    print("=" * 80)
    print(f"{'Timeline present:':<25} {'✅' if has_timeline else '❌'}")
    print(f"{'Quantitative details:':<25} {'✅' if has_numbers else '❌'}")
    print(f"{'Milestones defined:':<25} {'✅' if has_milestones else '❌'}")
    print(f"{'Resource allocation:':<25} {'✅' if has_resources else '❌'}")
    print(f"{'Detailed (>1000 chars):':<25} {'✅' if len(response) > 1000 else '❌'}")
    print(f"\n{'Overall Score:':<25} {score}/10")

    return {
        "agent": "orchestrator",
        "score": score,
        "valid": score >= 7,
        "response_length": len(response)
    }


async def test_physchem_coder_improved():
    """Test PhysChem Coder con prompts mejorados"""
    print("\n" + "=" * 80)
    print("💻 TEST 3: PHYSCHEM CODER con Prompts Mejorados v2.0")
    print("=" * 80)

    wrapper = HuggingFaceAgentWrapper(
        agent_role="physchem_coder",
        use_improved_prompts=True
    )

    prompt = """Design a computational pipeline to analyze CRISPR editing efficiency from
deep sequencing data. Include statistical analysis, visualization, and validation."""

    print(f"\n📋 User Prompt:")
    print(prompt)
    print(f"\n⚙️ Parameters: {get_agent_parameters('physchem_coder')}")
    print("\n🤖 Generating computational design (this may take 30-60 seconds)...\n")

    response = await wrapper.generate_async(prompt)

    print("=" * 80)
    print("📤 RESPONSE:")
    print("=" * 80)
    print(response)
    print("=" * 80)

    # Check for ACTUAL code vs descriptions
    has_imports = "import " in response
    has_functions = "def " in response
    has_statistics = any(word in response.lower() for word in ['t-test', 'anova', 'p-value', 'cohen'])
    has_plot_code = any(word in response for word in ['plt.', 'plot(', 'fig,'])
    code_lines = len([line for line in response.split('\n') if line.strip().startswith('def ') or
                      line.strip().startswith('import ')])

    score = 3  # Base (for generating something)
    if has_imports:
        score += 1
    if has_functions:
        score += 2
    if has_statistics:
        score += 1
    if has_plot_code:
        score += 1
    if code_lines >= 5:  # At least 5 lines of actual code
        score += 2

    print("\n📊 QUALITY ASSESSMENT:")
    print("=" * 80)
    print(f"{'Has imports:':<30} {'✅' if has_imports else '❌'}")
    print(f"{'Has function definitions:':<30} {'✅' if has_functions else '❌'}")
    print(f"{'Statistical analysis code:':<30} {'✅' if has_statistics else '❌'}")
    print(f"{'Visualization code:':<30} {'✅' if has_plot_code else '❌'}")
    print(f"{'Code lines (≥5):':<30} {'✅' if code_lines >= 5 else '❌'} ({code_lines} lines)")
    print(f"\n{'Overall Score:':<30} {score}/10")

    print("\n💡 KEY FIX: Should generate EXECUTABLE CODE, not text descriptions")

    return {
        "agent": "physchem_coder",
        "score": score,
        "valid": score >= 7,
        "response_length": len(response),
        "code_lines": code_lines
    }


async def test_reviewer_improved():
    """Test Reviewer con prompts mejorados (más crítico)"""
    print("\n" + "=" * 80)
    print("🔍 TEST 4: REVIEWER con Prompts Mejorados v2.0 (CRITICAL MODE)")
    print("=" * 80)

    wrapper = HuggingFaceAgentWrapper(
        agent_role="reviewer",
        use_improved_prompts=True
    )

    # Same flawed content from analysis
    content_to_review = """
HYPOTHESIS: CRISPR editing of BRCA1 will be effective.
METHODS: We used HEK293T cells and Cas9. We saw editing.
RESULTS: Editing worked well (p<0.05).
CONCLUSION: This is ready for clinical trials.
"""

    prompt = f"Review the following research for publication:\n\n{content_to_review}"

    print(f"\n📋 Content to Review (intentionally flawed):")
    print(content_to_review)
    print(f"\n⚙️ Parameters: {get_agent_parameters('reviewer')}")
    print("\n🤖 Generating critical review (this may take 30-60 seconds)...\n")

    response = await wrapper.generate_async(prompt)

    print("=" * 80)
    print("📤 RESPONSE:")
    print("=" * 80)
    print(response)
    print("=" * 80)

    # Check if reviewer caught the major flaws
    caught_sample_size = "sample size" in response.lower() or "n=" in response.lower()
    caught_off_target = "off-target" in response.lower()
    caught_overstated = "overstat" in response.lower() or "clinical" in response.lower()
    has_major_issues = "major" in response.lower() and ("issue" in response.lower() or "revision" in response.lower())
    verdict = "reject" in response.lower() or "major revision" in response.lower()

    score = 3  # Base
    if caught_sample_size:
        score += 2
    if caught_off_target:
        score += 2
    if caught_overstated:
        score += 1
    if has_major_issues:
        score += 1
    if verdict:
        score += 1

    print("\n📊 CRITICAL ANALYSIS QUALITY:")
    print("=" * 80)
    print(f"{'Caught missing sample size:':<35} {'✅' if caught_sample_size else '❌ MISSED'}")
    print(f"{'Caught missing off-target analysis:':<35} {'✅' if caught_off_target else '❌ MISSED'}")
    print(f"{'Caught overstated conclusions:':<35} {'✅' if caught_overstated else '❌ MISSED'}")
    print(f"{'Identified major issues:':<35} {'✅' if has_major_issues else '❌'}")
    print(f"{'Appropriate verdict (reject/major):':<35} {'✅' if verdict else '❌'}")
    print(f"\n{'Overall Score:':<35} {score}/10")

    print("\n💡 KEY FIX: Should be MORE CRITICAL, catch safety issues like missing off-target analysis")

    return {
        "agent": "reviewer",
        "score": score,
        "valid": score >= 7,
        "caught_major_flaws": caught_sample_size and caught_off_target
    }


async def main():
    """Run all improved prompt tests"""
    print("\n" + "=" * 80)
    print("🚀 TESTING IMPROVED PROMPTS v2.0")
    print("=" * 80)
    print("\nComparing with previous scores from analysis_agent_quality.md:")
    print("  - Bio Hypothesis: 3.0-7.2/10 (avg 5.1)")
    print("  - Orchestrator: 6.0/10")
    print("  - PhysChem Coder: 5.5/10")
    print("  - Reviewer: 6.5/10")
    print("  - Overall Average: 5.6/10 ❌ NOT SUFFICIENT")
    print("\nTarget: ≥8.0/10 for all agents")

    results = []

    try:
        # Test 1: Bio Hypothesis
        result = await test_bio_hypothesis_improved()
        results.append(result)
        await asyncio.sleep(2)  # Rate limiting

        # Test 2: Orchestrator
        result = await test_orchestrator_improved()
        results.append(result)
        await asyncio.sleep(2)

        # Test 3: PhysChem Coder
        result = await test_physchem_coder_improved()
        results.append(result)
        await asyncio.sleep(2)

        # Test 4: Reviewer
        result = await test_reviewer_improved()
        results.append(result)

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY - Improved Prompts v2.0")
    print("=" * 80)

    if results:
        avg_score = sum(r["score"] for r in results) / len(results)
        valid_count = sum(1 for r in results if r["valid"])

        print("\nIndividual Scores:")
        for r in results:
            status = "✅" if r["valid"] else "❌"
            print(f"  {status} {r['agent']:<20} {r['score']}/10")

        print(f"\n{'Average Score:':<30} {avg_score:.1f}/10")
        print(f"{'Valid Responses:':<30} {valid_count}/{len(results)}")

        print("\n📈 COMPARISON:")
        print(f"{'Previous Average:':<30} 5.6/10 ❌")
        print(f"{'New Average:':<30} {avg_score:.1f}/10 {'✅' if avg_score >= 8.0 else '⚠️'}")
        improvement = avg_score - 5.6
        print(f"{'Improvement:':<30} {improvement:+.1f} points")

        if avg_score >= 8.0:
            print("\n🎉 SUCCESS! Quality is now sufficient for research approval!")
        elif avg_score >= 7.0:
            print("\n⚠️ GOOD PROGRESS but still needs minor improvements")
        else:
            print("\n❌ Still needs significant work to reach 8.0/10 target")

    print("\n" + "=" * 80)
    print("✅ Testing completed")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
