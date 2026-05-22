#!/usr/bin/env python3
"""
Integration Test Script for Advanced AXIOM Modules
Tests all advanced modules for visualization, graph analysis, ML, data manipulation, NLP, and orchestration
"""

import sys
import os
import traceback
from typing import Dict, Any

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_module(module_name: str, test_function: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test a specific module function with given data"""
    try:
        module = __import__(module_name)
        operations_class = getattr(module, f'Advanced{module_name.split("_")[1].title()}Operations')
        operations = operations_class()

        method = getattr(operations, test_function)
        result = method(test_data)

        return {
            'module': module_name,
            'function': test_function,
            'status': 'success',
            'result': result
        }

    except Exception as e:
        return {
            'module': module_name,
            'function': test_function,
            'status': 'failed',
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def run_integration_tests():
    """Run integration tests for all advanced modules"""

    print("🚀 Starting AXIOM Advanced Modules Integration Tests")
    print("=" * 60)

    test_results = []

    # Test data for each module
    test_cases = [
        {
            'module': 'advanced_matplotlib_operations',
            'function': 'advanced_plotting_pipeline',
            'data': {
                'plot_type': 'scatter',
                'data': {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 6, 8, 10]},
                'style': {'color': 'blue', 'marker': 'o'}
            }
        },
        {
            'module': 'advanced_plotly_operations',
            'function': 'advanced_visualization_pipeline',
            'data': {
                'chart_type': 'scatter',
                'data': [{'x': [1, 2, 3], 'y': [4, 5, 6]}],
                'layout': {'title': 'Test Plot'}
            }
        },
        {
            'module': 'advanced_networkx_operations',
            'function': 'advanced_graph_pipeline',
            'data': {
                'graph_type': 'erdos_renyi',
                'nodes': 10,
                'edges': 15,
                'analysis_type': 'centrality'
            }
        },
        {
            'module': 'advanced_scikit_learn_operations',
            'function': 'advanced_ml_pipeline',
            'data': {
                'task': 'classification',
                'data': {'X': [[1, 2], [3, 4], [5, 6]], 'y': [0, 1, 0]},
                'model_type': 'random_forest'
            }
        },
        {
            'module': 'advanced_pandas_operations',
            'function': 'advanced_data_pipeline',
            'data': {
                'operation': 'clean',
                'data': {'col1': [1, 2, None], 'col2': ['a', 'b', 'c']},
                'cleaning_config': {'remove_nulls': True}
            }
        },
        {
            'module': 'advanced_transformers_operations',
            'function': 'advanced_nlp_pipeline',
            'data': {
                'text': 'Hello world',
                'tasks': ['sentiment-analysis'],
                'models': {'sentiment-analysis': 'cardiffnlp/twitter-roberta-base-sentiment-latest'}
            }
        },
        {
            'module': 'advanced_langchain_operations',
            'function': 'advanced_chain_pipeline',
            'data': {
                'chain_type': 'custom_chain',
                'components': [{'type': 'transform', 'template': 'Process: {input}'}],
                'input_variables': {'input': 'test data'}
            }
        }
    ]

    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{len(test_cases)}: {test_case['module']} - {test_case['function']}")

        result = test_module(
            test_case['module'],
            test_case['function'],
            test_case['data']
        )

        test_results.append(result)

        if result['status'] == 'success':
            print(f"✅ PASSED - {result['module']}")
        else:
            print(f"❌ FAILED - {result['module']}")
            print(f"   Error: {result['error']}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in test_results if r['status'] == 'success')
    failed = len(test_results) - passed

    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(".1f")

    if failed > 0:
        print("\n❌ Failed Tests:")
        for result in test_results:
            if result['status'] == 'failed':
                print(f"  - {result['module']}: {result['error']}")

    # Detailed results
    print("\n📋 Detailed Results:")
    for result in test_results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_icon} {result['module']} - {result['function']}: {result['status']}")

    return test_results

def test_module_availability():
    """Test if all modules can be imported successfully"""

    print("\n🔍 Testing Module Availability")
    print("-" * 40)

    modules_to_test = [
        'advanced_matplotlib_operations',
        'advanced_plotly_operations',
        'advanced_networkx_operations',
        'advanced_scikit_learn_operations',
        'advanced_pandas_operations',
        'advanced_transformers_operations',
        'advanced_langchain_operations'
    ]

    available_modules = []
    unavailable_modules = []

    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}: Available")
            available_modules.append(module_name)
        except ImportError as e:
            print(f"❌ {module_name}: Import Error - {e}")
            unavailable_modules.append(module_name)
        except Exception as e:
            print(f"⚠️  {module_name}: Other Error - {e}")
            unavailable_modules.append(module_name)

    print(f"\nAvailable: {len(available_modules)}/{len(modules_to_test)}")
    return available_modules, unavailable_modules

if __name__ == "__main__":
    print("AXIOM Advanced Modules Integration Test Suite")
    print("Testing comprehensive functionality across all advanced modules")

    # Test module availability first
    available, unavailable = test_module_availability()

    if not available:
        print("\n❌ No modules available for testing!")
        sys.exit(1)

    # Run integration tests
    results = run_integration_tests()

    # Exit with appropriate code
    failed_tests = sum(1 for r in results if r['status'] == 'failed')
    sys.exit(0 if failed_tests == 0 else 1)
