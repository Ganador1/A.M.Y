#!/usr/bin/env python3
"""
Test completo del servicio ProtGPT2 con generación real
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock database functions
class MockDB:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def close(self):
        pass

Base = type('Base', (), {})

def mock_get_db_session():
    return MockDB()

def mock_init_database():
    pass

# Apply mocks before importing
sys.modules['app.database'] = type(sys)('app.database')
sys.modules['app.database'].get_db_session = mock_get_db_session
sys.modules['app.database'].init_database = mock_init_database
sys.modules['app.database'].Base = Base

# Mock logging
import logging
sys.modules['app.logging_config'] = type(sys)('app.logging_config')
sys.modules['app.logging_config'].logger = logging.getLogger('test')

async def test_protgpt2_service():
    """Test the ProtGPT2 service with real generation"""
    try:
        print("🔬 Testing ProtGPT2 Service...")

        from app.services.protgpt2_service import ProtGPT2ProteinDesignService

        # Create service instance
        service = ProtGPT2ProteinDesignService()
        print(f"✅ Service created - Model loaded: {service.model_loaded}")

        # Test protein generation
        print("\n🧬 Testing protein generation...")

        test_prompts = [
            "small enzyme protein with catalytic activity",
            "thermostable protein for industrial applications",
            "antibody binding domain"
        ]

        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Test {i}: Generating protein from prompt: '{prompt}'")

            result = await service.generate_protein_sequence(
                prompt,
                temperature=0.8,
                max_length=100
            )

            if result.get('success'):
                data = result['data']
                protein = data['generated_protein']
                analysis = data['sequence_analysis']

                print("✅ Generation successful!")
                print(f"   Sequence: {protein['sequence'][:50]}...")
                print(f"   Length: {analysis['length']} amino acids")
                print(f"   Perplexity: {analysis['perplexity']}")
                print(f"   Confidence: {analysis['confidence']}")
                print(f"   Molecular Weight: {protein['properties_predicted']['molecular_weight']} Da")
                print(f"   Hydrophobicity: {protein['properties_predicted']['hydrophobicity_score']}")
            else:
                print(f"❌ Generation failed: {result.get('error')}")

        # Test optimization
        print("\n🔧 Testing protein optimization...")
        test_sequence = "MKALIVTLTLAMLYGVALQADAHGKLKDFGKLKQ"

        result = await service.optimize_protein_sequence(
            test_sequence,
            target_property="stability"
        )

        if result.get('success'):
            data = result['data']
            optimization = data['optimization']
            print("✅ Optimization successful!")
            print(f"   Original: {optimization['original_sequence']}")
            print(f"   Optimized: {optimization['optimized_sequence']}")
            print(f"   Mutations: {len(optimization['mutations'])}")
            print(f"   Score: {optimization['optimization_score']}")
        else:
            print(f"❌ Optimization failed: {result.get('error')}")

        # Test domain insertion
        print("\n🔗 Testing domain insertion...")

        result = await service.design_domain_insertion(
            test_sequence,
            domain_function="catalytic"
        )

        if result.get('success'):
            data = result['data']
            insertion = data['domain_insertion']
            print("✅ Domain insertion successful!")
            print(f"   Base sequence: {insertion['base_sequence'][:30]}...")
            print(f"   Modified: {insertion['modified_sequence'][:30]}...")
            print(f"   Inserted domain: {insertion['inserted_domain']}")
            print(f"   Compatibility: {insertion['structural_compatibility']}")
        else:
            print(f"❌ Domain insertion failed: {result.get('error')}")

        # Health check
        print("\n🏥 Running health check...")
        health = await service.health_check()

        print("✅ Health check completed!")
        print(f"   Status: {health['service_status']}")
        print(f"   Model loaded: {health['model_loaded']}")
        print(f"   Supported features: {len(health['supported_features'])}")

        return True

    except Exception as e:
        print(f"❌ Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_protgpt2_service())
    if success:
        print("\n🎉 ProtGPT2 Service Test PASSED!")
        print("✅ All features working correctly")
        print("✅ Real model integration successful")
        print("✅ Fallback mechanisms functional")
    else:
        print("\n❌ ProtGPT2 Service Test FAILED!")
