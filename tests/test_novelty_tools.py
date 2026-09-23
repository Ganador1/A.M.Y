#!/usr/bin/env python3
"""Test novelty-capable Atlas tools to find ones that generate novel findings."""
import sys, os, asyncio
sys.path.insert(0, '.')
os.environ['ENABLE_REDIS_CACHE'] = 'false'

from run_agent_with_tools import DynamicToolRegistry

async def main():
    reg = DynamicToolRegistry()
    tests = [
        # Novelty-capable tools with correct format
        ('conjecture_engine', 'generate:prime_gaps'),
        ('number_theory_advanced', 'twin_primes:1000'),
        ('number_theory_advanced', 'prime_gaps:500'),
        ('quantum_circuit', 'bell'),
        ('quantum_energy_levels', 'hydrogen:10'),
        ('numpy_correlation', 'correlation:[1,2,3,4,5];[2,4,6,8,10]'),
        ('hypothesis_tester', 'ttest:[1,2,3,4,5];[6,7,8,9,10]'),
        ('molecular_orbital_energy', '6'),
        ('prime_gap_analysis', '5000'),
        ('sympy_prime_analysis', 'is_prime:104729'),
    ]
    for tool, inp in tests:
        try:
            result = await asyncio.wait_for(reg.execute_tool(tool, inp), timeout=30)
            preview = str(result)[:200].replace('\n', ' ')
            print(f'OK {tool}({inp[:30]}): {preview}')
        except Exception as e:
            print(f'ERR {tool}({inp[:30]}): {str(e)[:80]}')

asyncio.run(main())