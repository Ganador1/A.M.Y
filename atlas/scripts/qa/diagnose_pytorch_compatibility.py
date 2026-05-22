#!/usr/bin/env python3
"""
Diagnóstico de compatibilidad PyTorch/transformers para ProtGPT2
"""

import sys
import subprocess
import importlib

def check_pytorch_version():
    """Check PyTorch version and installation"""
    print("🔍 Checking PyTorch installation...")

    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        print(f"   MPS available: {torch.backends.mps.is_available()}")

        # Check dynamo availability
        try:
            import torch._dynamo
            print("✅ torch._dynamo available")
            print(f"   external_utils available: {hasattr(torch._dynamo, 'external_utils')}")
        except AttributeError as e:
            print(f"⚠️  torch._dynamo issue: {e}")

        return True
    except ImportError as e:
        print(f"❌ PyTorch not found: {e}")
        return False

def check_transformers_version():
    """Check transformers version and compatibility"""
    print("\n🔍 Checking transformers installation...")

    try:
        import transformers
        print(f"✅ Transformers version: {transformers.__version__}")

        # Check if ProtGPT2 model is accessible
        from transformers import AutoConfig
        config = AutoConfig.from_pretrained("nferruz/ProtGPT2")
        print(f"✅ ProtGPT2 config loaded: {config.model_type}")

        return True
    except ImportError as e:
        print(f"❌ Transformers not found: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Transformers issue: {e}")
        return False

def test_model_loading_isolation():
    """Test model loading in isolated environment"""
    print("\n🔍 Testing isolated model loading...")

    test_code = '''
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

try:
    model_name = "nferruz/ProtGPT2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    print("SUCCESS: Model loaded in subprocess")
except Exception as e:
    print(f"FAILED: {e}")
'''

    try:
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
            timeout=30
        )

        if "SUCCESS" in result.stdout:
            print("✅ Isolated model loading: SUCCESS")
            return True
        else:
            print("❌ Isolated model loading: FAILED")
            print(f"   Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Isolated model loading: TIMEOUT")
        return False

def test_service_import_isolation():
    """Test service import in isolation"""
    print("\n🔍 Testing service import isolation...")

    # Create minimal test
    test_code = '''
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies
class MockDB:
    def __enter__(self): return self
    def __exit__(self, *args): pass

sys.modules["app.database"] = type("mock", (), {"get_db_session": lambda: MockDB()})
sys.modules["app.logging_config"] = type("mock", (), {"logger": type("mock", (), {"info": print, "error": print})()})

try:
    from app.services.protgpt2_service import ProtGPT2ProteinDesignService
    service = ProtGPT2ProteinDesignService()
    print(f"SUCCESS: Service created, model_loaded={service.model_loaded}")
except Exception as e:
    print(f"FAILED: {e}")
'''

    try:
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="."
        )

        if "SUCCESS" in result.stdout:
            print("✅ Isolated service import: SUCCESS")
            return True
        else:
            print("❌ Isolated service import: FAILED")
            print(f"   Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Isolated service import: TIMEOUT")
        return False

def suggest_fixes():
    """Suggest fixes based on findings"""
    print("\n🔧 RECOMMENDED FIXES:")

    print("\n1. Update PyTorch and transformers:")
    print("   pip install --upgrade torch torchvision torchaudio")
    print("   pip install --upgrade transformers")

    print("\n2. Try specific compatible versions:")
    print("   pip install torch==2.1.0 transformers==4.30.0")

    print("\n3. Alternative: Use conda for better dependency management:")
    print("   conda install pytorch torchvision torchaudio -c pytorch")
    print("   conda install transformers -c huggingface")

    print("\n4. If issues persist, implement model loading in subprocess:")
    print("   - Move model loading to separate process")
    print("   - Use multiprocessing for isolation")
    print("   - Implement lazy loading with process communication")

def main():
    """Run all diagnostic tests"""
    print("🩺 PyTorch/transformers Diagnostic Tool")
    print("=" * 50)

    results = []

    # Run diagnostic tests
    results.append(("PyTorch Version", check_pytorch_version()))
    results.append(("Transformers Version", check_transformers_version()))
    results.append(("Isolated Model Loading", test_model_loading_isolation()))
    results.append(("Isolated Service Import", test_service_import_isolation()))

    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC RESULTS:")

    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")

    if passed < len(results):
        print("\n⚠️  Some issues detected. See recommendations below.")
        suggest_fixes()
    else:
        print("\n🎉 All diagnostics passed! ProtGPT2 should work correctly.")

if __name__ == "__main__":
    main()
