#!/usr/bin/env python3
"""
Manual test script for improvements - runs outside of the installation script
"""

import sys
import asyncio
from pathlib import Path

# Add improvements to path
sys.path.insert(0, str(Path(__file__).parent / 'improvements'))

async def test_plausibility_scorer():
    """Test the advanced plausibility scorer"""
    try:
        from improvements.advanced_plausibility_scorer import AdvancedPlausibilityScorerV2

        print("🧪 Testing Advanced Plausibility Scorer...")

        scorer = AdvancedPlausibilityScorerV2()

        hypothesis = {
            "title": "Graphene-based room temperature superconductor",
            "description": "Novel doping mechanism enables superconductivity at 25°C in graphene",
            "variables": ["doping_concentration", "temperature", "pressure"],
            "domain": "materials_science",
            "assumptions": ["Graphene maintains 2D structure", "Doping is uniform"],
            "expected_outcome": "Zero electrical resistance at room temperature"
        }

        result = await scorer.score_hypothesis(hypothesis)

        print(f"✅ Plausibility scorer test passed")
        print(f"   Final score: {result.get('final_score', 0):.3f}")
        print(f"   Semantic score: {result.get('confidence_breakdown', {}).get('semantic', 0):.3f}")
        print(f"   Literature score: {result.get('confidence_breakdown', {}).get('literature', 0):.3f}")

        return True

    except Exception as e:
        print(f"❌ Plausibility scorer test failed: {e}")
        return False

async def test_scientific_databases():
    """Test the real scientific databases"""
    try:
        from improvements.real_scientific_databases import RealScientificDatabasesV2

        print("🧪 Testing Real Scientific Databases...")

        db = RealScientificDatabasesV2()

        # Test with a simple query
        results = await db.search_all_databases(
            "COVID-19",
            databases=["crossref"],  # Use crossref which doesn't require API keys
            max_results_per_db=5
        )

        print(f"✅ Database test passed")
        print(f"   Papers found: {len(results.get('papers', []))}")
        print(f"   Compounds found: {len(results.get('compounds', []))}")
        print(f"   Proteins found: {len(results.get('proteins', []))}")

        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing AXIOM/ATLAS Improvements\n")

    tests = [
        test_plausibility_scorer,
        test_scientific_databases
    ]

    passed = 0
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("✅ All improvements are working correctly!")
        return True
    else:
        print("❌ Some improvements need attention")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
