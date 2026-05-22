#!/usr/bin/env python3
"""
Test: Sandbox + Atlas Integration (Simplified)

Verifies that code executed in the sandbox can invoke Atlas tools
via core.atlas_tools (which is available in the current Python env).
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "atlas"))

from sandbox.executor import SandboxExecutor


async def test_sandbox_atlas_integration():
    """Test that sandbox code can call Atlas tools."""
    print("=" * 70)
    print("SANDBOX + ATLAS INTEGRATION TEST")
    print("=" * 70)

    executor = SandboxExecutor({
        "max_execution_time": 120,
        "max_memory_mb": 512,
    })

    # Test 1: Sandbox code imports core.atlas_tools and runs a tool
    print("\n[1/3] Testing sandbox code calling Atlas tool via core.atlas_tools...")
    
    sandbox_code = """
import sys
import os

# Add project root to path (sandbox runs with cwd=project_root)
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.atlas_tools import AtlasTools
import asyncio

async def main():
    tools = AtlasTools()
    result = await tools.run_scientific_tool("sympy_prime_analysis", "is_prime:97", "mathematics")
    print("RESULT:", result)

asyncio.run(main())
"""

    result = await executor.execute(sandbox_code, language="python")
    if result["success"] and "97 is prime" in result["stdout"]:
        print("  ✅ Sandbox can invoke Atlas tools via core.atlas_tools")
        print(f"  Output: {result['stdout'][:100]}")
    else:
        print("  ❌ Sandbox failed to invoke Atlas tools")
        print(f"  stdout: {result['stdout'][:200]}")
        print(f"  stderr: {result['stderr'][:200]}")
        return False

    # Test 2: Sandbox code runs numpy_statistics
    print("\n[2/3] Testing sandbox code calling numpy_statistics...")
    
    sandbox_code2 = """
import sys
import os

project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.atlas_tools import AtlasTools
import asyncio

async def main():
    tools = AtlasTools()
    result = await tools.run_scientific_tool("numpy_statistics", "summary:[1,2,3,4,5]", "statistics")
    print("RESULT:", result)

asyncio.run(main())
"""

    result2 = await executor.execute(sandbox_code2, language="python")
    if result2["success"] and "Mean" in result2["stdout"]:
        print("  ✅ numpy_statistics works from sandbox")
    else:
        print("  ❌ numpy_statistics failed from sandbox")
        print(f"  stdout: {result2['stdout'][:200]}")
        print(f"  stderr: {result2['stderr'][:200]}")
        return False

    # Test 3: Sandbox code validates a hypothesis
    print("\n[3/3] Testing sandbox code calling validate_hypothesis...")
    
    sandbox_code3 = """
import sys
import os

project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.atlas_tools import AtlasTools
import asyncio

async def main():
    tools = AtlasTools()
    result = await tools.run_scientific_tool("validate_hypothesis", "mathematics:all primes greater than 2 are odd", "research")
    print("RESULT:", result)

asyncio.run(main())
"""

    result3 = await executor.execute(sandbox_code3, language="python")
    if result3["success"] and "Hypothesis" in result3["stdout"]:
        print("  ✅ validate_hypothesis works from sandbox")
    else:
        print("  ❌ validate_hypothesis failed from sandbox")
        print(f"  stdout: {result3['stdout'][:200]}")
        print(f"  stderr: {result3['stderr'][:200]}")
        return False

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("🎉 ALL SANDBOX + ATLAS INTEGRATION TESTS PASSED!")
    print("\nA.M.Y can now:")
    print("  1. Generate experimental code in sandbox")
    print("  2. Execute Atlas tools from within sandbox code")
    print("  3. Get scientific results back to the cognitive cycle")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_sandbox_atlas_integration())
    sys.exit(0 if success else 1)
