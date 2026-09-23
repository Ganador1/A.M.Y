#!/usr/bin/env python3
"""
Script para registrar los prompts mejorados en el PromptRegistryService

Este script registra las plantillas de alta calidad identificadas en el
análisis de calidad (analysis_agent_quality.md) en el sistema de registro
de prompts existente.

Usage:
    python scripts/tools/register_improved_prompts.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.prompting.prompt_registry_service import prompt_registry_service
from app.services.improved_agent_prompts import (
    BIO_HYPOTHESIS_PROMPT_TEMPLATE,
    PHYSCHEM_CODER_PROMPT_TEMPLATE,
    REVIEWER_PROMPT_TEMPLATE,
    ORCHESTRATOR_PROMPT_TEMPLATE,
    AGENT_PARAMETERS
)


def register_all_improved_prompts():
    """Registrar todas las plantillas mejoradas en el prompt registry"""

    print("🔧 Registrando prompts mejorados en PromptRegistryService...")
    print("=" * 70)

    # 1. Bio Hypothesis Prompt
    print("\n📝 Registrando Bio Hypothesis Prompt (v2.0_quantitative)...")
    result = prompt_registry_service.register(
        name="bio_hypothesis",
        version="2.0_quantitative",
        template=BIO_HYPOTHESIS_PROMPT_TEMPLATE,
        variables=["user_prompt"],
        metadata={
            "description": "Improved biological hypothesis generator with strict quantitative requirements",
            "quality_improvements": [
                "Requires numerical predictions (50±10%, ≥2-fold, etc.)",
                "Forces specific entities (not 'bacteria' but 'Faecalibacterium prausnitzii')",
                "Demands mechanistic detail with concentrations/timescales",
                "Includes statistical design (power ≥0.8, alpha=0.05)",
                "Structured JSON output for validation"
            ],
            "parameters": AGENT_PARAMETERS["bio_hypothesis"],
            "previous_score": "3-7/10",
            "target_score": "8-9/10",
            "author": "AXIOM ATLAS Quality Improvement Team",
            "date": "2025-10-10",
            "based_on": "analysis_agent_quality.md findings"
        }
    )

    if result["success"]:
        print("✅ Bio Hypothesis Prompt registrado exitosamente")
        print(f"   - Template length: {len(BIO_HYPOTHESIS_PROMPT_TEMPLATE)} chars")
        print(f"   - Temperature: {AGENT_PARAMETERS['bio_hypothesis']['temperature']}")
        print(f"   - Max tokens: {AGENT_PARAMETERS['bio_hypothesis']['max_new_tokens']}")
    else:
        print(f"❌ Error: {result.get('error')}")

    # 2. PhysChem Coder Prompt
    print("\n📝 Registrando PhysChem Coder Prompt (v2.0_executable_code)...")
    result = prompt_registry_service.register(
        name="physchem_coder",
        version="2.0_executable_code",
        template=PHYSCHEM_CODER_PROMPT_TEMPLATE,
        variables=["user_prompt"],
        metadata={
            "description": "Improved computational scientist that writes EXECUTABLE code, not descriptions",
            "quality_improvements": [
                "Generates complete working Python code (not pseudocode)",
                "Includes statistical analysis with power calculations",
                "Publication-quality visualization with error bars",
                "Unit tests and validation checks",
                "Detailed computational parameters and resources"
            ],
            "parameters": AGENT_PARAMETERS["physchem_coder"],
            "previous_score": "5.5/10",
            "target_score": "8-9/10",
            "key_fix": "MUST provide actual code, not text descriptions",
            "author": "AXIOM ATLAS Quality Improvement Team",
            "date": "2025-10-10"
        }
    )

    if result["success"]:
        print("✅ PhysChem Coder Prompt registrado exitosamente")
        print(f"   - Template length: {len(PHYSCHEM_CODER_PROMPT_TEMPLATE)} chars")
        print(f"   - Temperature: {AGENT_PARAMETERS['physchem_coder']['temperature']} (low for precision)")
        print(f"   - Max tokens: {AGENT_PARAMETERS['physchem_coder']['max_new_tokens']} (high for complete code)")
    else:
        print(f"❌ Error: {result.get('error')}")

    # 3. Reviewer Prompt
    print("\n📝 Registrando Reviewer Prompt (v2.0_critical)...")
    result = prompt_registry_service.register(
        name="reviewer",
        version="2.0_critical",
        template=REVIEWER_PROMPT_TEMPLATE,
        variables=["user_prompt"],
        metadata={
            "description": "CRITICAL scientific reviewer (Nature/Science/Cell standards)",
            "quality_improvements": [
                "Be SKEPTICAL - find flaws, demand rigor",
                "Verify sample size justification and power analysis",
                "Check for multiple testing corrections",
                "Demand effect sizes (not just p-values)",
                "Identify missing controls and confounders",
                "Harsh but fair - better to reject bad science"
            ],
            "parameters": AGENT_PARAMETERS["reviewer"],
            "previous_score": "6.5/10 (too benevolent)",
            "target_score": "8-9/10",
            "key_fix": "More critical, catches major errors like missing off-target analysis",
            "scoring_rubric": {
                "9-10": "Exceptional, paradigm-shifting",
                "7-8": "Strong, publishable in top journal",
                "5-6": "Adequate but needs improvement",
                "3-4": "Significant flaws, major revision",
                "1-2": "Fundamentally flawed, reject"
            },
            "author": "AXIOM ATLAS Quality Improvement Team",
            "date": "2025-10-10"
        }
    )

    if result["success"]:
        print("✅ Reviewer Prompt registrado exitosamente")
        print(f"   - Template length: {len(REVIEWER_PROMPT_TEMPLATE)} chars")
        print(f"   - Temperature: {AGENT_PARAMETERS['reviewer']['temperature']} (medium-low for consistency)")
        print(f"   - Max tokens: {AGENT_PARAMETERS['reviewer']['max_new_tokens']}")
    else:
        print(f"❌ Error: {result.get('error')}")

    # 4. Orchestrator Prompt
    print("\n📝 Registrando Orchestrator Prompt (v2.0_detailed_timeline)...")
    result = prompt_registry_service.register(
        name="orchestrator",
        version="2.0_detailed_timeline",
        template=ORCHESTRATOR_PROMPT_TEMPLATE,
        variables=["user_prompt"],
        metadata={
            "description": "Research coordinator with concrete timelines and quantitative milestones",
            "quality_improvements": [
                "Specific weeks/months for each phase (not 'short-term')",
                "Quantitative milestones (not 'analyze data' but 'complete statistical analysis of n=30')",
                "Resource allocation (personnel FTE, equipment, budget)",
                "Risk mitigation with backup plans",
                "Critical path and go/no-go decision points"
            ],
            "parameters": AGENT_PARAMETERS["orchestrator"],
            "previous_score": "6.0/10 (too generic)",
            "target_score": "8-9/10",
            "key_fix": "Concrete timeline with task dependencies and resource estimates",
            "author": "AXIOM ATLAS Quality Improvement Team",
            "date": "2025-10-10"
        }
    )

    if result["success"]:
        print("✅ Orchestrator Prompt registrado exitosamente")
        print(f"   - Template length: {len(ORCHESTRATOR_PROMPT_TEMPLATE)} chars")
        print(f"   - Temperature: {AGENT_PARAMETERS['orchestrator']['temperature']} (low for structured planning)")
        print(f"   - Max tokens: {AGENT_PARAMETERS['orchestrator']['max_new_tokens']}")
    else:
        print(f"❌ Error: {result.get('error')}")

    # List all registered prompts
    print("\n" + "=" * 70)
    print("📋 Prompts registrados en el sistema:\n")
    all_prompts = prompt_registry_service.list()

    if all_prompts["success"]:
        improved_prompts = [p for p in all_prompts["prompts"] if "2.0" in p["version"]]
        print(f"Total de prompts v2.0 mejorados: {len(improved_prompts)}")

        for p in improved_prompts:
            print(f"\n📌 {p['name']} v{p['version']}")
            print(f"   Variables: {', '.join(p['variables'])}")
            print(f"   Creado: {p['created_at']}")
            meta = p.get("metadata", {})
            if "previous_score" in meta:
                print(f"   Score anterior: {meta['previous_score']}")
                print(f"   Target: {meta['target_score']}")

    print("\n" + "=" * 70)
    print("✅ Registro de prompts mejorados completado")
    print("\nPara usar estos prompts:")
    print("  from app.services.prompting.prompt_registry_service import prompt_registry_service")
    print("  result = prompt_registry_service.render(")
    print("      name='bio_hypothesis',")
    print("      version='2.0_quantitative',")
    print("      context={'user_prompt': 'Generate hypothesis about...'}")
    print("  )")
    print("  improved_prompt = result['rendered']")


if __name__ == "__main__":
    register_all_improved_prompts()
