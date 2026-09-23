
import asyncio
import os
import logging
from app.autonomous.interfaces.external_apis import fetch_material_candidates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mp_api():
    print("Testing Materials Project API...")
    
    # Check if API key is set
    api_key = os.getenv("MATERIALS_PROJECT_API_KEY")
    if not api_key:
        print("WARNING: MATERIALS_PROJECT_API_KEY not set. This test might fail or use stubs.")
    else:
        print(f"API Key found: {api_key[:4]}...")

    try:
        results = await fetch_material_candidates("Si-O", limit=3)
        print(f"Results: {len(results)}")
        for r in results:
            print(f" - {r.get('material_id')}: {r.get('formula')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mp_api())
