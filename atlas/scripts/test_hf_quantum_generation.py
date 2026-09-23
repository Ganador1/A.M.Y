"""
Test HuggingFace API generation para Quantum loop.
Verifica que los modelos grandes de HF generan candidatos únicos.
"""
import asyncio
import os
from app.autonomous.pipelines.quantum_loop import QuantumLoop

async def test_hf_generation():
    print("\n" + "="*80)
    print("🚀 TEST: HuggingFace API Generation (Phase 8.4)")
    print("="*80 + "\n")
    
    # Verificar API key desde almacenamiento cifrado
    from app.config.api_keys_manager import get_api_key
    
    hf_token = get_api_key("HUGGINGFACE")
    if not hf_token:
        print("❌ ERROR: HUGGINGFACE API key not found")
        print("   Configure it with:")
        print("   python -c 'from app.config.api_keys_manager import APIKeysManager; mgr = APIKeysManager(); mgr.set_api_key(\"HUGGINGFACE\", \"your_key\")'")
        return False
    
    print(f"✅ HuggingFace API key found: {hf_token[:12]}...{hf_token[-4:]}")
    print(f"   Length: {len(hf_token)} characters\n")
    
    loop = QuantumLoop()
    
    # Test con modelo Qwen2.5-Coder-32B
    print("\n📝 Test: Generating 3 quantum circuits with Qwen2.5-Coder-32B...")
    print("-" * 80)
    
    try:
        candidates = await loop._generate_candidates_with_huggingface(
            limit=3,
            model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
            temperature=0.85
        )
        
        if not candidates:
            print("❌ FAIL: No candidates generated")
            return False
        
        print(f"\n✅ Generated {len(candidates)} candidates\n")
        
        for idx, cand in enumerate(candidates, 1):
            print(f"Candidate {idx}:")
            print(f"  Name: {cand.get('name')}")
            print(f"  Algorithm: {cand.get('algorithm')}")
            print(f"  Qubits: {cand.get('n_qubits')}")
            print(f"  Depth: {cand.get('depth')}")
            print(f"  Motivation: {cand.get('motivation', 'N/A')[:100]}")
            print()
        
        # Verificar diversidad
        unique_names = len(set(c['name'] for c in candidates))
        print(f"📊 Unique names: {unique_names}/{len(candidates)}")
        
        if unique_names >= len(candidates) * 0.8:
            print("✅ PASS: High diversity in candidates")
        else:
            print("⚠️ WARNING: Low diversity")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = asyncio.run(test_hf_generation())
    sys.exit(0 if success else 1)
