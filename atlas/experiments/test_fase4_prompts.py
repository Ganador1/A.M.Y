#!/usr/bin/env python3
"""
Test Fase 4: Validar que prompts integran literatura context

Verifica que:
1. format_literature_context() genera sección correcta
2. get_improved_prompt() incluye literatura context
3. ScientificHypothesisAgent recibe literatura en prompt
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.improved_agent_prompts import format_literature_context, get_improved_prompt


def test_format_literatura_context():
    """Test 1: format_literature_context generates correct section"""
    print("=" * 80)
    print("TEST 1: format_literature_context()")
    print("=" * 80)
    
    # Mock literatura context
    lit_ctx = {
        'papers': [
            {'title': 'Paper 1', 'arxiv_id': '2401.00001'},
            {'title': 'Paper 2', 'arxiv_id': '2401.00002'},
        ],
        'studied_topics': ['protein', 'genomic', 'genome'],
        'identified_gaps': [
            'cell-type-specific dynamics',
            'temporal resolution at single-cell level',
            'pathway crosstalk mechanisms'
        ],
        'saturated_keywords': ['genomic', 'protein']
    }
    
    section = format_literature_context(lit_ctx)
    
    print(f"\n📋 Generated Section ({len(section)} chars):\n")
    print(section)
    print()
    
    # Validate content
    checks = [
        ('Has papers count', 'Papers reviewed: 2' in section),
        ('Has saturated keywords', 'SATURATED KEYWORDS' in section),
        ('Lists genomic as saturated', '`genomic`' in section),
        ('Has research gaps', 'IDENTIFIED RESEARCH GAPS' in section),
        ('Lists gap #1', 'cell-type-specific' in section),
        ('Has novelty strategy', 'NOVELTY STRATEGY' in section),
    ]
    
    passed = 0
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Result: {passed}/{len(checks)} checks passed")
    print()
    
    return passed == len(checks)


def test_get_improved_prompt_with_literatura():
    """Test 2: get_improved_prompt() includes literatura context"""
    print("=" * 80)
    print("TEST 2: get_improved_prompt() with literatura_context")
    print("=" * 80)
    
    # Mock literatura context
    lit_ctx = {
        'papers': [
            {'title': 'Paper 1', 'arxiv_id': '2401.00001'},
        ],
        'studied_topics': ['protein', 'genomic'],
        'identified_gaps': [
            'cell-type-specific dynamics',
            'temporal resolution'
        ],
        'saturated_keywords': ['genomic']
    }
    
    user_prompt = "What biological mechanisms can be discovered?"
    
    # Generate prompt WITH literatura
    prompt_with_lit = get_improved_prompt(
        agent_role="bio_hypothesis",
        user_prompt=user_prompt,
        domain="biology",
        literature_context=lit_ctx
    )
    
    # Generate prompt WITHOUT literatura
    prompt_without_lit = get_improved_prompt(
        agent_role="bio_hypothesis",
        user_prompt=user_prompt,
        domain="biology",
        literature_context=None
    )
    
    print(f"\n📏 Prompt WITH literatura: {len(prompt_with_lit)} chars")
    print(f"📏 Prompt WITHOUT literatura: {len(prompt_without_lit)} chars")
    print(f"📈 Difference: +{len(prompt_with_lit) - len(prompt_without_lit)} chars\n")
    
    # Show literatura section (extract between markers)
    if '## 📚 RECENT LITERATURE ANALYSIS' in prompt_with_lit:
        start_idx = prompt_with_lit.index('## 📚 RECENT LITERATURE ANALYSIS')
        end_idx = prompt_with_lit.index('USER REQUEST:', start_idx)
        lit_section = prompt_with_lit[start_idx:end_idx]
        
        print("📚 Literatura section in prompt:")
        print("-" * 80)
        print(lit_section[:500])  # First 500 chars
        if len(lit_section) > 500:
            print(f"... (truncated, total {len(lit_section)} chars)")
        print("-" * 80)
        print()
    
    # Validate content
    checks = [
        ('Prompt WITH has literatura section', '📚 RECENT LITERATURE ANALYSIS' in prompt_with_lit),
        ('Prompt WITHOUT lacks literatura section', '📚 RECENT LITERATURE ANALYSIS' not in prompt_without_lit),
        ('Lists saturated keywords', 'SATURATED KEYWORDS' in prompt_with_lit),
        ('Lists research gaps', 'IDENTIFIED RESEARCH GAPS' in prompt_with_lit),
        ('Includes user prompt', user_prompt in prompt_with_lit),
        ('Prompt is longer with literatura', len(prompt_with_lit) > len(prompt_without_lit)),
    ]
    
    passed = 0
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Result: {passed}/{len(checks)} checks passed")
    print()
    
    return passed == len(checks)


def test_prompt_integration_dry_run():
    """Test 3: Dry run of full hypothesis generation with literatura"""
    print("=" * 80)
    print("TEST 3: Dry Run - Hypothesis Generation with Literatura")
    print("=" * 80)
    
    # This test just validates the prompt gets built correctly
    # Does NOT call the LLM (would require Ollama running)
    
    lit_ctx = {
        'papers': [
            {'title': 'Advances in single-cell genomics', 'arxiv_id': '2410.05467'},
            {'title': 'Protein function annotation', 'arxiv_id': '2408.06402'},
        ],
        'studied_topics': ['protein', 'genomic', 'genome', 'annotation'],
        'identified_gaps': [
            'cell-type-specific dynamics',
            'post-translational modification crosstalk',
            'temporal resolution at single-cell level',
        ],
        'saturated_keywords': ['genomic', 'protein', 'genome']
    }
    
    research_question = "What biological mechanisms can be discovered through autonomous data analysis?"
    
    prompt = get_improved_prompt(
        agent_role="bio_hypothesis",
        user_prompt=f"""Generate a hypothesis about the relationship between {research_question}.
Domain: biology
Context: {{
    'mode': 'autonomous',
    'novelty_threshold': 0.7,
    'enable_literature_search': True
}}

Focus on specific entities, quantifiable predictions, and testable experiments.""",
        domain="biology",
        literature_context=lit_ctx
    )
    
    print(f"\n📋 Full Prompt Generated: {len(prompt)} chars\n")
    
    # Show key sections
    sections = [
        ('CRITICAL REQUIREMENTS', 'CRITICAL REQUIREMENTS'),
        ('FORMAT - JSON', 'FORMAT - Return ONLY valid JSON'),
        ('EXAMPLE - High quality', 'EXAMPLE - High quality hypothesis:'),
        ('BAD EXAMPLE', 'BAD EXAMPLE - What NOT to do:'),
        ('LITERATURE ANALYSIS', '📚 RECENT LITERATURE ANALYSIS'),
        ('USER REQUEST', 'USER REQUEST:'),
    ]
    
    print("📑 Prompt Structure:")
    for section_name, marker in sections:
        if marker in prompt:
            idx = prompt.index(marker)
            status = "✅ FOUND"
        else:
            idx = -1
            status = "❌ MISSING"
        
        print(f"  {status}: {section_name:30s} (pos: {idx:5d})")
    
    print()
    
    # Validate
    checks = [
        ('Has CRITICAL REQUIREMENTS', 'CRITICAL REQUIREMENTS' in prompt),
        ('Has JSON format spec', 'FORMAT - Return ONLY valid JSON' in prompt),
        ('Has high-quality example', 'EXAMPLE - High quality hypothesis' in prompt),
        ('Has literatura analysis', '📚 RECENT LITERATURE ANALYSIS' in prompt),
        ('Lists gaps to TARGET', 'IDENTIFIED RESEARCH GAPS' in prompt),
        ('Lists keywords to AVOID', 'SATURATED KEYWORDS' in prompt),
        ('Has user request', 'USER REQUEST:' in prompt),
        ('Mentions cell-type-specific gap', 'cell-type-specific' in prompt),
    ]
    
    passed = 0
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Result: {passed}/{len(checks)} checks passed")
    print()
    
    # Show literatura section snippet
    if '📚 RECENT LITERATURE ANALYSIS' in prompt:
        start = prompt.index('📚 RECENT LITERATURE ANALYSIS')
        end = prompt.index('USER REQUEST:', start)
        lit_section = prompt[start:end]
        
        print("📚 Literatura Section Preview:")
        print("=" * 80)
        print(lit_section)
        print("=" * 80)
        print()
    
    return passed == len(checks)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print(" FASE 4: TEST - LITERATURA CONTEXT INTEGRATION IN PROMPTS")
    print("=" * 80)
    print()
    
    results = []
    
    # Test 1
    try:
        results.append(("format_literature_context()", test_format_literatura_context()))
    except Exception as e:
        print(f"❌ Test 1 FAILED with exception: {e}\n")
        results.append(("format_literature_context()", False))
    
    # Test 2
    try:
        results.append(("get_improved_prompt() integration", test_get_improved_prompt_with_literatura()))
    except Exception as e:
        print(f"❌ Test 2 FAILED with exception: {e}\n")
        results.append(("get_improved_prompt() integration", False))
    
    # Test 3
    try:
        results.append(("Dry run full integration", test_prompt_integration_dry_run()))
    except Exception as e:
        print(f"❌ Test 3 FAILED with exception: {e}\n")
        results.append(("Dry run full integration", False))
    
    # Summary
    print("\n" + "=" * 80)
    print(" SUMMARY")
    print("=" * 80)
    print()
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print()
    print(f"📊 Overall: {passed_count}/{total_count} tests passed")
    print()
    
    if passed_count == total_count:
        print("🎉 ✅ ALL TESTS PASSED - Fase 4 integration complete!")
        print()
        print("✅ Literatura context is now integrated into prompts")
        print("✅ LLM will receive gaps and saturated keywords")
        print("✅ Ready to re-run A/B test with updated prompts")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    exit(main())
