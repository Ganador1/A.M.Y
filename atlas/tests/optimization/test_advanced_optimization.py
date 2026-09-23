"""
Independent test script for advanced optimization methods
Tests the algorithms directly without project dependencies
"""

import numpy as np
import sympy as sp
from typing import Dict, List, Any, Optional
import random
from scipy.optimize import minimize, differential_evolution, basinhopping

def test_differential_evolution():
    """Test differential evolution optimization"""
    print("🧪 Testing Differential Evolution...")
    
    # Test function: sphere function
    def sphere(x):
        return sum(xi**2 for xi in x)
    
    bounds = [(-5, 5), (-5, 5)]
    
    try:
        result = differential_evolution(sphere, bounds, maxiter=10, popsize=5, disp=False)
        
        if result.success:
            print(f"   ✅ Success: Optimal value = {result.fun:.6f}")
            print(f"   📍 Solution: {result.x}")
            return {'status': 'optimal', 'value': result.fun, 'solution': result.x}
        else:
            print(f"   ❌ Failed: {result.message}")
            return {'status': 'failed', 'message': result.message}
            
    except Exception as e:
        print(f"   💥 Error: {e}")
        return {'status': 'error', 'message': str(e)}

def test_multi_start_optimization():
    """Test multi-start optimization"""
    print("🧪 Testing Multi-Start Optimization...")
    
    def sphere(x):
        return sum(xi**2 for xi in x)
    
    bounds = [(-5, 5), (-5, 5)]
    results = []
    
    for i in range(3):
        x0 = [random.uniform(-5, 5), random.uniform(-5, 5)]
        
        try:
            result = minimize(sphere, x0, method='L-BFGS-B', bounds=bounds, options={'maxiter': 10})
            
            if result.success:
                results.append({
                    'start': x0,
                    'value': result.fun,
                    'solution': result.x,
                    'success': True
                })
            else:
                results.append({
                    'start': x0,
                    'value': result.fun,
                    'solution': result.x,
                    'success': False
                })
                
        except Exception as e:
            print(f"   💥 Error in start {i+1}: {e}")
    
    if results:
        best = min(results, key=lambda x: x['value'])
        if best['success']:
            print(f"   ✅ Best result: {best['value']:.6f}")
            return {'status': 'optimal', 'value': best['value'], 'solution': best['solution']}
        else:
            print(f"   ⚠️ Best result (failed): {best['value']:.6f}")
            return {'status': 'failed', 'value': best['value']}
    else:
        print("   ❌ No successful results")
        return {'status': 'error', 'message': 'No results'}

def test_basin_hopping():
    """Test basin hopping optimization"""
    print("🧪 Testing Basin Hopping...")
    
    def sphere(x):
        return sum(xi**2 for xi in x)
    
    x0 = [2.5, 2.5]  # Start away from optimum
    
    try:
        result = basinhopping(sphere, x0, niter=5, minimizer_kwargs={'method': 'L-BFGS-B'})
        
        if result.lowest_optimization_result.success:
            print(f"   ✅ Success: Optimal value = {result.fun:.6f}")
            print(f"   📍 Solution: {result.x}")
            return {'status': 'optimal', 'value': result.fun, 'solution': result.x}
        else:
            print(f"   ❌ Failed")
            return {'status': 'failed'}
            
    except Exception as e:
        print(f"   💥 Error: {e}")
        return {'status': 'error', 'message': str(e)}

def test_all_methods():
    """Test all optimization methods"""
    print("🚀 Testing Advanced Optimization Methods")
    print("=" * 50)
    
    results = {}
    
    # Test each method
    results['differential_evolution'] = test_differential_evolution()
    results['multi_start'] = test_multi_start_optimization()
    results['basin_hopping'] = test_basin_hopping()
    
    # Print summary
    print(f"\n{'='*50}")
    print("📋 SUMMARY")
    print(f"{'='*50}")
    
    successful = 0
    total = len(results)
    
    for method, result in results.items():
        status = '✅' if result.get('status') == 'optimal' else '❌'
        value = f"{result.get('value', 'N/A'):.6f}" if 'value' in result else 'N/A'
        print(f"{status} {method}: {result.get('status', 'error')} (value: {value})")
        if result.get('status') == 'optimal':
            successful += 1
    
    print(f"\n🎯 Success rate: {successful}/{total} ({successful/total*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    test_all_methods()
