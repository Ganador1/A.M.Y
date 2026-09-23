import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'improvements'))

async def test_plausibility_scorer():
    from improvements.advanced_plausibility_scorer import AdvancedPlausibilityScorerV2
    
    scorer = AdvancedPlausibilityScorerV2()
    
    hypothesis = {
        "title": "Test hypothesis",
        "description": "This is a test",
        "variables": ["x", "y"],
        "domain": "test"
    }
    
    result = await scorer.score_hypothesis(hypothesis)
    assert "final_score" in result
    assert 0 <= result["final_score"] <= 1
    print("✅ Plausibility scorer test passed")

async def test_databases():
    from improvements.real_scientific_databases import RealScientificDatabasesV2
    
    db = RealScientificDatabasesV2()
    
    # Test with a known query
    results = await db.search_all_databases(
        "COVID-19",
        databases=["crossref"],
        max_results_per_db=5
    )
    
    assert "papers" in results
    print(f"✅ Database test passed - found {len(results['papers'])} papers")

async def main():
    await test_plausibility_scorer()
    await test_databases()
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(main())
