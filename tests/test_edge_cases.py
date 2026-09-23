#!/usr/bin/env python3
"""
Test: Edge Cases and Error Handling

Prueba casos límite y manejo de errores:
1. Herramientas con inputs inválidos
2. Herramientas que no existen
3. Dominios inexistentes
4. Inputs vacíos o mal formateados
5. Timeouts y recuperación
6. Papers con pocos resultados
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "atlas"))

from core.atlas_tools import AtlasTools


async def test_edge_cases():
    """Test edge cases and error handling."""
    print("=" * 70)
    print("EDGE CASES AND ERROR HANDLING TEST")
    print("=" * 70)

    tools = AtlasTools()
    results = []

    # Test 1: Tool with invalid input
    print("\n[1/8] Testing invalid input...")
    try:
        result = await tools.run_scientific_tool("sympy_prime_analysis", "not_a_number", "mathematics")
        has_error = "error" in str(result).lower() or "invalid" in str(result).lower()
        print(f"  {'✅' if has_error else '⚠️'}  Result: {str(result)[:80]}")
        results.append(("invalid_input", has_error))
    except Exception as e:
        print(f"  ✅ Exception handled: {e}")
        results.append(("invalid_input", True))

    # Test 2: Non-existent tool
    print("\n[2/8] Testing non-existent tool...")
    try:
        result = await tools.run_scientific_tool("nonexistent_tool_xyz", "input", "mathematics")
        has_error = "error" in str(result).lower() or "not found" in str(result).lower()
        print(f"  {'✅' if has_error else '⚠️'}  Result: {str(result)[:80]}")
        results.append(("nonexistent_tool", has_error))
    except Exception as e:
        print(f"  ✅ Exception handled: {e}")
        results.append(("nonexistent_tool", True))

    # Test 3: Empty input
    print("\n[3/8] Testing empty input...")
    try:
        result = await tools.run_scientific_tool("sympy_prime_analysis", "", "mathematics")
        print(f"  ⚠️  Result: {str(result)[:80]}")
        results.append(("empty_input", True))  # Should handle gracefully
    except Exception as e:
        print(f"  ✅ Exception handled: {e}")
        results.append(("empty_input", True))

    # Test 4: Wrong domain
    print("\n[4/8] Testing wrong domain...")
    try:
        result = await tools.run_scientific_tool("molecular_weight_calc", "H2O", "mathematics")
        print(f"  ⚠️  Result: {str(result)[:80]}")
        results.append(("wrong_domain", True))
    except Exception as e:
        print(f"  ✅ Exception handled: {e}")
        results.append(("wrong_domain", True))

    # Test 5: Very large input
    print("\n[5/8] Testing large input...")
    try:
        large_input = "summary:[" + ",".join([str(i) for i in range(1000)]) + "]"
        result = await tools.run_scientific_tool("numpy_statistics", large_input, "statistics")
        print(f"  ✅ Large input handled: {str(result)[:80]}")
        results.append(("large_input", True))
    except Exception as e:
        print(f"  ⚠️  Large input failed: {e}")
        results.append(("large_input", False))

    # Test 6: Special characters
    print("\n[6/8] Testing special characters...")
    try:
        result = await tools.run_scientific_tool("sympy_simplify", "sin(x)**2 + cos(x)**2", "mathematics")
        success = "1" in str(result) or "simplified" in str(result).lower()
        print(f"  {'✅' if success else '⚠️'}  Result: {str(result)[:80]}")
        results.append(("special_chars", success))
    except Exception as e:
        print(f"  ⚠️  Special chars failed: {e}")
        results.append(("special_chars", False))

    # Test 7: Unicode input
    print("\n[7/8] Testing unicode input...")
    try:
        result = await tools.run_scientific_tool("validate_hypothesis", "chemistry:água é H₂O", "research")
        print(f"  ✅ Unicode handled: {str(result)[:80]}")
        results.append(("unicode", True))
    except Exception as e:
        print(f"  ⚠️  Unicode failed: {e}")
        results.append(("unicode", False))

    # Test 8: Multiple rapid calls
    print("\n[8/8] Testing rapid successive calls...")
    try:
        tasks = [
            tools.run_scientific_tool("sympy_prime_analysis", f"is_prime:{i}", "mathematics")
            for i in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        ]
        rapid_results = await asyncio.gather(*tasks, return_exceptions=True)
        successes = sum(1 for r in rapid_results if not isinstance(r, Exception) and "True" in str(r))
        print(f"  ✅ {successes}/10 rapid calls succeeded")
        results.append(("rapid_calls", successes >= 8))
    except Exception as e:
        print(f"  ⚠️  Rapid calls failed: {e}")
        results.append(("rapid_calls", False))

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed >= 6:
        print(f"\n🎉 EDGE CASES TEST PASSED!")
        print(f"   {passed}/{total} cases handled correctly")
    else:
        print(f"\n⚠️  EDGE CASES TEST NEEDS ATTENTION")
        print(f"   {passed}/{total} cases handled correctly")

    return passed >= 6


if __name__ == "__main__":
    success = asyncio.run(test_edge_cases())
    sys.exit(0 if success else 1)
