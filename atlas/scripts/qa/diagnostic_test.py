#!/usr/bin/env python3
"""
Diagnostic script for AXIOM modules - detailed error analysis
"""

import sys
import os
import traceback

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_matplotlib_detailed():
    """Detailed test of matplotlib module"""
    print("🔍 Testing matplotlib in detail...")
    try:
        from advanced_matplotlib_operations import AdvancedMatplotlibOperations
        import pandas as pd
        import numpy as np

        mpl_ops = AdvancedMatplotlibOperations()

        # Create simple test data
        dates = pd.date_range('2020-01-01', periods=10, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'price': [100 + i for i in range(10)]
        })

        print("Testing time series...")
        result1 = mpl_ops.advanced_plotting_pipeline({
            'x': [str(d) for d in data['date'].dt.strftime('%Y-%m-%d').tolist()],
            'y': data['price'].tolist(),
            'type': 'line',
            'title': 'Test Plot',
            'xlabel': 'Date',
            'ylabel': 'Price'
        })
        print(f"Time series result: {result1}")

        print("Testing statistics...")
        result2 = mpl_ops.statistical_visualization({
            'box_data': [data['price'].tolist()],
            'hist_data': data['price'].tolist()
        })
        print(f"Statistics result: {result2}")

        return True

    except Exception as e:
        print(f"❌ Matplotlib error: {e}")
        traceback.print_exc()
        return False

def test_pandas_detailed():
    """Detailed test of pandas module"""
    print("🔍 Testing pandas in detail...")
    try:
        from advanced_pandas_operations import AdvancedPandasOperations

        pd_ops = AdvancedPandasOperations()

        # Create simple test data
        data = [
            {'date': '2020-01-01', 'price': 100, 'volume': 1000},
            {'date': '2020-01-02', 'price': 101, 'volume': 1100},
            {'date': '2020-01-03', 'price': 102, 'volume': 1200}
        ]

        print("Testing data pipeline...")
        result = pd_ops.advanced_data_pipeline({
            'dataframe': data,
            'cleaning_config': {
                'remove_outliers': False,
                'handle_missing': False,
                'normalize': False
            }
        })
        print(f"Pandas result: {result}")
        return True

    except Exception as e:
        print(f"❌ Pandas error: {e}")
        traceback.print_exc()
        return False

def test_networkx_detailed():
    """Detailed test of networkx module"""
    print("🔍 Testing networkx in detail...")
    try:
        from advanced_networkx_operations import AdvancedNetworkxOperations

        nx_ops = AdvancedNetworkxOperations()

        print("Testing graph pipeline...")
        result = nx_ops.advanced_graph_pipeline({
            'graph_type': 'undirected',
            'nodes': [{'id': 1}, {'id': 2}, {'id': 3}],
            'edges': [{'source': 1, 'target': 2}, {'source': 2, 'target': 3}],
            'centrality_analysis': False,
            'community_detection': False
        })
        print(f"NetworkX result: {result}")
        return True

    except Exception as e:
        print(f"❌ NetworkX error: {e}")
        traceback.print_exc()
        return False

def test_plotly_detailed():
    """Detailed test of plotly module"""
    print("🔍 Testing plotly in detail...")
    try:
        from advanced_plotly_operations import AdvancedPlotlyOperations
        import pandas as pd

        plotly_ops = AdvancedPlotlyOperations()

        # Create simple test data
        data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [10, 20, 30, 40, 50],
            'category': ['A', 'B', 'A', 'B', 'A']
        })

        print("Testing visualization pipeline...")
        result = plotly_ops.advanced_visualization_pipeline({
            'dataframe': data,
            'type': 'scatter',
            'x': 'x',
            'y': 'y',
            'color': 'category',
            'title': 'Test Plot'
        })
        print(f"Plotly result: {'figure' in result}")
        return True

    except Exception as e:
        print(f"❌ Plotly error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Detailed Diagnostic for AXIOM Modules")
    print("="*50)

    results = {
        'matplotlib': test_matplotlib_detailed(),
        'pandas': test_pandas_detailed(),
        'networkx': test_networkx_detailed(),
        'plotly': test_plotly_detailed()
    }

    print("\n" + "="*50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*50)

    for module, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{module.upper()}: {status}")

    print(f"\nTotal passed: {sum(results.values())}/{len(results)}")
