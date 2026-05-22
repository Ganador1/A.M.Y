"""
Protein Analysis Pipeline Example

This example demonstrates end-to-end protein analysis using AXIOM ATLAS,
including fetching protein data, analyzing structure, and checking disease relevance.

Requirements:
    - AXIOM ATLAS running at http://localhost:8000
    - httpx installed: pip install httpx

Usage:
    python examples/biology/protein_analysis_pipeline.py
"""

import asyncio
import httpx
from typing import Dict, Any


async def analyze_protein(uniprot_id: str) -> Dict[str, Any]:
    """
    Analyze a protein using AXIOM ATLAS API.

    Args:
        uniprot_id: UniProt identifier (e.g., 'P04637' for TP53)

    Returns:
        Dict with protein analysis results
    """
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(base_url=base_url, timeout=60.0) as client:
        # Step 1: Analyze protein
        print(f"🔬 Analyzing protein {uniprot_id}...")

        try:
            response = await client.post(
                "/api/biology/protein/analyze",
                json={
                    "uniprot_id": uniprot_id,
                    "predict_structure": False  # Set True to enable AlphaFold prediction
                }
            )
            response.raise_for_status()
            protein_data = response.json()

        except httpx.HTTPStatusError as e:
            print(f"❌ API Error: {e.response.status_code}")
            print(f"   Details: {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"❌ Connection Error: {e}")
            print("   Ensure AXIOM ATLAS is running at http://localhost:8000")
            raise

        return protein_data


async def check_disease_relevance(protein_data: Dict[str, Any]) -> None:
    """
    Check if protein is linked to diseases.

    Args:
        protein_data: Protein analysis results
    """
    print(f"\n📊 Protein: {protein_data.get('gene_name', 'Unknown')}")
    print(f"   UniProt ID: {protein_data.get('uniprot_id')}")
    print(f"   Length: {protein_data.get('length', 'N/A')} amino acids")

    # Check disease associations
    diseases = protein_data.get('disease_relevance', [])

    if diseases:
        print(f"\n⚠️  Disease Associations Found:")
        for disease in diseases[:5]:  # Show first 5
            print(f"   - {disease}")
    else:
        print(f"\n✅ No disease associations found")

    # Check functional annotations
    functions = protein_data.get('functions', [])
    if functions:
        print(f"\n🧬 Functions:")
        for func in functions[:3]:  # Show first 3
            print(f"   - {func}")


async def analyze_multiple_proteins(uniprot_ids: list[str]) -> None:
    """
    Analyze multiple proteins concurrently.

    Args:
        uniprot_ids: List of UniProt IDs to analyze
    """
    print(f"🚀 Starting analysis of {len(uniprot_ids)} proteins...\n")

    # Run analyses concurrently
    tasks = [analyze_protein(uid) for uid in uniprot_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"\n❌ Failed to analyze {uniprot_ids[i]}: {result}")
        else:
            await check_disease_relevance(result)
            print("\n" + "="*60)


async def main():
    """Main execution."""

    # Example 1: Single protein analysis (TP53 - tumor suppressor)
    print("="*60)
    print("Example 1: Single Protein Analysis (TP53)")
    print("="*60)

    tp53_data = await analyze_protein("P04637")
    await check_disease_relevance(tp53_data)

    print("\n\n")

    # Example 2: Multiple proteins (concurrent analysis)
    print("="*60)
    print("Example 2: Multiple Protein Analysis")
    print("="*60)

    proteins_of_interest = [
        "P04637",  # TP53 - Tumor suppressor
        "P01308",  # INS - Insulin
        "P68871",  # HBB - Hemoglobin beta
    ]

    await analyze_multiple_proteins(proteins_of_interest)

    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    # Check if server is running
    print("🔍 Checking AXIOM ATLAS server...")

    try:
        # Quick health check
        import httpx
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        if response.status_code == 200:
            print("✅ Server is running\n")
            asyncio.run(main())
        else:
            print(f"⚠️  Server returned status: {response.status_code}")
            print("   Try restarting with: uvicorn main_refactored:app --reload")
    except httpx.RequestError:
        print("❌ Server not running!")
        print("   Start with: uvicorn main_refactored:app --reload")
        print("   Then run this script again.")
