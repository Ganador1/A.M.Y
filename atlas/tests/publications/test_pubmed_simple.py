#!/usr/bin/env python3
"""
Test simplificado de conectividad con PubMed
"""
import asyncio
import httpx
import xml.etree.ElementTree as ET
import time

async def test_pubmed_simple():
    print("🧬 Testing basic PubMed connectivity")
    print("=" * 50)
    
    client = httpx.AsyncClient(timeout=30.0)
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    try:
        # Test simple search
        print("🔍 Searching for neuroscience papers...")
        search_response = await client.get(
            f"{base_url}esearch.fcgi",
            params={
                "db": "pubmed",
                "term": "nanoparticles neural regeneration",
                "retmax": 3,
                "retmode": "xml"
            }
        )
        
        print(f"   Status: {search_response.status_code}")
        if search_response.status_code == 200:
            print("   ✅ Successfully connected to PubMed")
            
            # Parse results
            root = ET.fromstring(search_response.text)
            pmids = [id_elem.text for id_elem in root.findall(".//Id") if id_elem.text]
            count_elem = root.find(".//Count")
            total_count = int(count_elem.text) if count_elem is not None and count_elem.text else 0
            
            print(f"   📚 Total results available: {total_count}")
            print(f"   📄 PMIDs retrieved: {len(pmids)}")
            
            if pmids:
                print(f"   🔗 Example PMIDs: {', '.join(pmids[:3])}")
                
                # Test fetching details for one paper
                print(f"\n📖 Fetching details for PMID: {pmids[0]}...")
                fetch_response = await client.get(
                    f"{base_url}efetch.fcgi",
                    params={
                        "db": "pubmed",
                        "id": pmids[0],
                        "retmode": "xml"
                    }
                )
                
                if fetch_response.status_code == 200:
                    print("   ✅ Successfully retrieved paper details")
                    
                    # Parse basic info
                    detail_root = ET.fromstring(fetch_response.text)
                    title_elem = detail_root.find(".//ArticleTitle")
                    journal_elem = detail_root.find(".//Journal/Title")
                    
                    if title_elem is not None:
                        title = title_elem.text or "".join(title_elem.itertext())
                        print(f"   📝 Title: {title[:100]}...")
                    
                    if journal_elem is not None:
                        journal = journal_elem.text
                        print(f"   📰 Journal: {journal}")
                        
                else:
                    print(f"   ❌ Failed to fetch details: {fetch_response.status_code}")
        else:
            print(f"   ❌ Failed to connect: {search_response.status_code}")
            print(f"   Response: {search_response.text[:200]}...")
    
    except Exception as e:
        print(f"💥 Error: {str(e)}")
    
    finally:
        await client.aclose()
    
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_pubmed_simple())
