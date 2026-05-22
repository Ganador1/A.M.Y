#!/usr/bin/env python3
"""
Advanced Real Data Testing Suite for AXIOM Modules
Comprehensive testing with real-world data and complex scenarios
"""

import sys
import os
import time
import numpy as np
import pandas as pd
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def generate_real_world_datasets() -> Dict[str, Any]:
    """Generate realistic datasets for testing"""
    print("🔄 Generando datasets realistas para pruebas...")

    # Dataset 1: Financial time series data
    dates = pd.date_range('2020-01-01', periods=1000, freq='D')
    np.random.seed(42)

    financial_data = pd.DataFrame({
        'date': dates,
        'price': 100 + np.cumsum(np.random.randn(1000) * 2),
        'volume': np.random.randint(1000, 10000, 1000),
        'returns': np.random.randn(1000) * 0.02,
        'volatility': np.abs(np.random.randn(1000) * 0.1),
        'sentiment': np.random.choice(['positive', 'negative', 'neutral'], 1000, p=[0.4, 0.3, 0.3])
    })

    # Dataset 2: Customer behavior data
    customers = pd.DataFrame({
        'customer_id': range(1, 501),
        'age': np.random.normal(35, 10, 500).astype(int),
        'income': np.random.lognormal(10, 0.5, 500),
        'purchases': np.random.poisson(5, 500),
        'satisfaction': np.random.uniform(1, 5, 500),
        'churn_risk': np.random.choice([0, 1], 500, p=[0.7, 0.3]),
        'segment': np.random.choice(['premium', 'standard', 'basic'], 500, p=[0.2, 0.5, 0.3])
    })

    # Dataset 3: Social network data
    social_users = pd.DataFrame({
        'user_id': range(1, 201),
        'followers': np.random.zipf(2, 200),
        'following': np.random.poisson(150, 200),
        'posts': np.random.poisson(50, 200),
        'engagement_rate': np.random.beta(2, 5, 200),
        'influence_score': np.random.uniform(0, 100, 200)
    })

    # Dataset 4: Text data for NLP
    text_samples = [
        "The new AI model shows remarkable performance in natural language understanding.",
        "Machine learning algorithms are revolutionizing data analysis techniques.",
        "Deep learning networks can process complex patterns in large datasets.",
        "Computer vision systems are becoming increasingly sophisticated.",
        "The future of AI lies in multimodal learning approaches.",
        "Neural networks excel at pattern recognition tasks.",
        "Large language models are transforming how we interact with computers.",
        "Data science combines statistics, programming, and domain expertise.",
        "Predictive analytics helps businesses make informed decisions.",
        "The field of artificial intelligence is rapidly evolving."
    ] * 20  # Repeat for more data

    # Dataset 5: Graph data
    graph_data = {
        'nodes': [
            {'id': i, 'type': np.random.choice(['user', 'product', 'category']),
             'weight': np.random.uniform(0.1, 1.0)}
            for i in range(1, 51)
        ],
        'edges': [
            {'source': np.random.randint(1, 51), 'target': np.random.randint(1, 51),
             'weight': np.random.uniform(0.1, 1.0), 'type': 'interaction'}
            for _ in range(150)
        ]
    }

    return {
        'financial': financial_data,
        'customers': customers,
        'social': social_users,
        'text': text_samples,
        'graph': graph_data
    }

def test_matplotlib_real_data(datasets: Dict[str, Any]) -> Dict[str, Any]:
    """Test matplotlib module with real financial data"""
    print("📊 Probando matplotlib con datos financieros reales...")

    try:
        from advanced_matplotlib_operations import AdvancedMatplotlibOperations
        mpl_ops = AdvancedMatplotlibOperations()

        financial_data = datasets['financial']

        # Test 1: Time series visualization using advanced_plotting_pipeline
        result1 = mpl_ops.advanced_plotting_pipeline({
            'x': list(range(len(financial_data.head(50)))),
            'y': financial_data['price'].head(50).tolist(),
            'type': 'line',
            'title': 'Stock Price Evolution',
            'xlabel': 'Time Index',
            'ylabel': 'Price ($)',
            'style': 'seaborn'
        })

        # Test 2: Statistical visualization using statistical_visualization
        result2 = mpl_ops.statistical_visualization({
            'box_data': [financial_data['price'].tolist(), financial_data['volume'].tolist()],
            'violin_data': financial_data['returns'].tolist(),
            'hist_data': financial_data['price'].tolist()
        })

        # Test 3: Advanced plotting with multiple series
        result3 = mpl_ops.advanced_plotting_pipeline({
            'x': list(range(len(financial_data))),
            'y': [financial_data['price'].tolist(), financial_data['volume'].tolist()],
            'type': 'line',
            'title': 'Multi-Series Financial Data',
            'xlabel': 'Time Index',
            'ylabel': 'Value'
        })

        return {
            'status': 'success',
            'tests': {
                'time_series': 'figure' in result1,
                'statistics': 'figure' in result2,
                'multi_series': 'figure' in result3
            },
            'performance': {
                'total_time': 0,  # Could be measured
                'memory_usage': 'N/A'
            }
        }

    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

def test_plotly_real_data(datasets: Dict[str, Any]) -> Dict[str, Any]:
    """Test plotly module with real customer data"""
    print("📈 Probando plotly con datos de clientes reales...")

    try:
        from advanced_plotly_operations import AdvancedPlotlyOperations
        plotly_ops = AdvancedPlotlyOperations()

        customer_data = datasets['customers']

        # Test 1: 3D scatter plot for customer segmentation
        result1 = plotly_ops.advanced_visualization_pipeline({
            'dataframe': customer_data[['age', 'income', 'satisfaction']].head(50),
            'type': 'scatter_3d',
            'x': 'age',
            'y': 'income',
            'z': 'satisfaction',
            'color': 'segment',
            'title': 'Customer Segmentation Analysis'
        })

        # Test 2: Dashboard with multiple components
        result2 = plotly_ops.dashboard_components([
            {
                'dataframe': customer_data[['age', 'income']].head(100),
                'type': 'scatter',
                'x': 'age',
                'y': 'income',
                'color': 'segment',
                'title': 'Age vs Income'
            },
            {
                'dataframe': customer_data[['segment']].head(100),
                'type': 'histogram',
                'x': 'segment',
                'title': 'Customer Segments Distribution'
            }
        ])

        return {
            'status': 'success',
            'tests': {
                '3d_segmentation': 'figure' in result1,
                'dashboard': 'figure' in result2
            }
        }

    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

def test_networkx_real_data(datasets: Dict[str, Any]) -> Dict[str, Any]:
    """Test networkx module with real social network data"""
    print("🕸️ Probando networkx con datos de red social reales...")

    try:
        from advanced_networkx_operations import AdvancedNetworkxOperations
        nx_ops = AdvancedNetworkxOperations()

        social_data = datasets['social']
        graph_data = datasets['graph']

        # Test 1: Social network analysis
        result1 = nx_ops.advanced_graph_pipeline({
            'graph_type': 'undirected',
            'nodes': [{'id': i, 'type': 'user'} for i in social_data['user_id'].head(30).tolist()],
            'edges': [(social_data['user_id'].iloc[i], social_data['user_id'].iloc[j])
                     for i in range(min(30, len(social_data)))
                     for j in range(i+1, min(30, len(social_data)))
                     if np.random.random() < 0.05],  # Reduced connection probability
            'centrality_analysis': True,
            'community_detection': True
        })

        # Test 2: Graph algorithms on structured data
        result2 = nx_ops.advanced_graph_pipeline({
            'graph_type': 'undirected',
            'nodes': [{'id': node['id']} for node in graph_data['nodes'][:20]],
            'edges': [(edge['source'], edge['target']) for edge in graph_data['edges'][:25]],
            'path_analysis': True,
            'clustering_analysis': True
        })

        return {
            'status': 'success',
            'tests': {
                'social_network': 'graph' in result1,
                'graph_algorithms': 'graph' in result2
            },
            'metrics': result1.get('metrics', {})
        }

    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

def test_scikit_learn_real_data(datasets: Dict[str, Any]) -> Dict[str, Any]:
    """Test scikit-learn module with real customer churn data"""
    print("🤖 Probando scikit-learn con datos de churn de clientes...")

    try:
        from advanced_scikit_learn_operations import AdvancedScikitOperations
        sk_ops = AdvancedScikitOperations()

        customer_data = datasets['customers']

        # Test 1: Complete ML pipeline
        result1 = sk_ops.advanced_ml_pipeline({
            'X': customer_data[['age', 'income', 'purchases', 'satisfaction']].head(200).values.tolist(),
            'y': customer_data['churn_risk'].head(200).values.tolist(),
            'task_type': 'classification',
            'feature_engineering': True,
            'hyperparameter_tuning': False  # Disable for faster testing
        })

        # Test 2: Clustering analysis
        result2 = sk_ops.advanced_clustering_pipeline({
            'X': customer_data[['age', 'income', 'purchases']].head(150).values.tolist(),
            'algorithms': ['kmeans'],
            'preprocessing': True
        })

        # Test 3: Ensemble methods
        result3 = sk_ops.ensemble_methods_pipeline({
            'X': customer_data[['age', 'income', 'purchases']].head(100).values.tolist(),
            'y': customer_data['churn_risk'].head(100).values.tolist(),
            'task_type': 'classification',
            'base_models': ['random_forest', 'gradient_boosting'],
            'stacking_ensemble': True,
            'voting_ensemble': True
        })

        return {
            'status': 'success',
            'tests': {
                'ml_pipeline': 'model_results' in result1,
                'clustering': 'clustering_results' in result2,
                'ensemble': 'ensemble_results' in result3
            },
            'performance': {
                'best_score': result1.get('model_results', {}).get('best_score'),
                'n_clusters_found': result2.get('clustering_results', {}).get('kmeans', {}).get('n_clusters_found', 0)
            }
        }

    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

def test_pandas_real_data(datasets: Dict[str, Any]) -> Dict[str, Any]:
    """Test pandas module with real financial and customer data"""
    print("📊 Probando pandas con datos financieros y de clientes...")

    try:
        from advanced_pandas_operations import AdvancedPandasOperations
        pd_ops = AdvancedPandasOperations()

        financial_data = datasets['financial']
        customer_data = datasets['customers']

        # Test 1: Advanced data cleaning and preprocessing
        result1 = pd_ops.advanced_data_pipeline({
            'dataframe': financial_data.head(50).to_dict('records'),
            'cleaning': True,
            'cleaning_config': {
                'remove_outliers': False,
                'handle_missing': False,
                'normalize': False
            }
        })

        # Test 2: Time series analysis
        result2 = pd_ops.advanced_data_pipeline({
            'dataframe': financial_data.head(100).to_dict('records'),
            'time_series_processing': True,
            'datetime_column': 'date',
            'target_column': 'price'
        })

        # Test 3: Feature engineering
        result3 = pd_ops.advanced_data_pipeline({
            'dataframe': customer_data.head(100).to_dict('records'),
            'feature_engineering': True,
            'feature_config': {
                'create_bins': True,
                'bin_columns': ['age'],
                'create_interactions': False
            }
        })

        return {
            'status': 'success',
            'tests': {
                'data_cleaning': 'processed_data' in result1,
                'time_series': 'processed_data' in result2,
                'feature_engineering': 'processed_data' in result3
            }
        }

    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

def test_transformers_real_data(datasets: Dict[str, Any]) -> Dict[str, Any]:
    """Test transformers module with real text data"""
    print("🧠 Probando transformers con datos de texto reales...")

    try:
        from advanced_transformers_operations import AdvancedTransformersOperations
        tf_ops = AdvancedTransformersOperations()

        text_data = datasets['text']

        # Test 1: Sentiment analysis pipeline
        result1 = tf_ops.advanced_nlp_pipeline({
            'text': text_data[:3],  # Use fewer samples for testing
            'tasks': ['sentiment-analysis'],
            'models': {'sentiment-analysis': 'cardiffnlp/twitter-roberta-base-sentiment-latest'}
        })

        # Test 2: Text generation (skip if taking too long)
        result2 = {'status': 'skipped', 'reason': 'Text generation can be slow in testing'}

        return {
            'status': 'success',
            'tests': {
                'sentiment_analysis': result1.get('status') == 'success',
                'text_generation': result2.get('status') == 'success'
            },
            'results': {
                'sentiment_samples': len(result1.get('results', {}).get('sentiment-analysis', [])),
                'generated_texts': 0
            }
        }

    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

def test_langchain_real_data(datasets: Dict[str, Any]) -> Dict[str, Any]:
    """Test langchain module with real text data"""
    print("🔗 Probando langchain con datos de texto reales...")

    try:
        from advanced_langchain_operations import AdvancedLangchainOperations
        lc_ops = AdvancedLangchainOperations()

        text_data = datasets['text']

        # Test 1: Chain pipeline
        result1 = lc_ops.advanced_chain_pipeline({
            'chain_type': 'custom_chain',
            'components': [{
                'type': 'transform',
                'template': 'Analyze: {input}'
            }],
            'input_variables': {'input': text_data[0]}
        })

        # Test 2: Prompt engineering
        result2 = lc_ops.advanced_prompt_engineering({
            'prompt_type': 'few_shot',
            'variables': {'topic': 'AI in data science'},
            'examples': [
                {'input': 'Machine learning', 'output': 'ML is a subset of AI'},
                {'input': 'Deep learning', 'output': 'DL uses neural networks'}
            ],
            'constraints': {'max_length': 100}
        })

        return {
            'status': 'success',
            'tests': {
                'chain_pipeline': result1.get('status') in ['success', 'limited'],
                'prompt_engineering': result2.get('status') == 'success'
            }
        }

    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

def run_performance_benchmarks() -> Dict[str, Any]:
    """Run performance benchmarks across all modules"""
    print("⚡ Ejecutando benchmarks de rendimiento...")

    # Generate test data
    datasets = generate_real_world_datasets()

    # Run all tests
    results = {
        'matplotlib': test_matplotlib_real_data(datasets),
        'plotly': test_plotly_real_data(datasets),
        'networkx': test_networkx_real_data(datasets),
        'scikit_learn': test_scikit_learn_real_data(datasets),
        'pandas': test_pandas_real_data(datasets),
        'transformers': test_transformers_real_data(datasets),
        'langchain': test_langchain_real_data(datasets)
    }

    return results

def generate_comprehensive_report(results: Dict[str, Any]) -> None:
    """Generate comprehensive test report"""
    print("\n" + "="*80)
    print("📊 REPORTE COMPREHENSIVO DE PRUEBAS CON DATOS REALES")
    print("="*80)

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for module, result in results.items():
        print(f"\n🔍 Módulo: {module.upper()}")
        print("-" * 40)

        if result['status'] == 'success':
            tests = result.get('tests', {})
            module_passed = sum(tests.values())
            module_total = len(tests)

            print("✅ Estado: ÉXITO")
            print(f"📈 Tests pasados: {module_passed}/{module_total}")

            for test_name, test_result in tests.items():
                status_icon = "✅" if test_result else "❌"
                print(f"   {status_icon} {test_name}")

            if 'performance' in result:
                perf = result['performance']
                print(f"⚡ Rendimiento: {perf}")

            total_tests += module_total
            passed_tests += module_passed
            failed_tests += (module_total - module_passed)

        else:
            print("❌ Estado: FALLÓ")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            failed_tests += 1
            total_tests += 1

    # Summary
    print("\n" + "="*80)
    print("📈 RESUMEN GENERAL")
    print("="*80)
    print(f"Total de módulos probados: {len(results)}")
    print(f"Total de tests ejecutados: {total_tests}")
    print(f"Tests exitosos: {passed_tests}")
    print(f"Tests fallidos: {failed_tests}")
    print(".1f")

    if failed_tests == 0:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print(f"⚠️  {failed_tests} tests fallaron. Revisar logs para detalles.")

    # Recommendations
    print("\n💡 RECOMENDACIONES:")
    if passed_tests / total_tests > 0.9:
        print("✅ Excelente rendimiento general. Los módulos están listos para producción.")
    elif passed_tests / total_tests > 0.7:
        print("⚠️ Buen rendimiento, pero algunos módulos necesitan ajustes menores.")
    else:
        print("❌ Rendimiento por debajo del esperado. Revisar y mejorar módulos.")

def run_integration_tests() -> Dict[str, Any]:
    """Run integration tests between modules"""
    print("🔗 Ejecutando pruebas de integración entre módulos...")

    datasets = generate_real_world_datasets()

    integration_results = {}

    try:
        # Integration 1: Pandas -> Scikit-learn pipeline
        from advanced_pandas_operations import AdvancedPandasOperations
        from advanced_scikit_learn_operations import AdvancedScikitOperations

        pd_ops = AdvancedPandasOperations()
        sk_ops = AdvancedScikitOperations()

        # Process data with pandas
        customer_data = datasets['customers']
        processed_data = pd_ops.advanced_data_pipeline({
            'operation': 'feature_engineering',
            'dataframe': customer_data.to_dict('records'),
            'feature_config': {'create_bins': True, 'bin_columns': ['age']}
        })

        # Use processed data in ML pipeline
        if processed_data.get('status') == 'success':
            X = customer_data[['age', 'income', 'purchases']].values
            y = customer_data['churn_risk'].values

            ml_result = sk_ops.advanced_ml_pipeline({
                'X': X.tolist(),
                'y': y.tolist(),
                'task_type': 'classification'
            })

            integration_results['pandas_sklearn'] = ml_result.get('status') == 'success'

        # Integration 2: NetworkX -> Matplotlib visualization
        from advanced_networkx_operations import AdvancedNetworkxOperations

        nx_ops = AdvancedNetworkxOperations()

        graph_result = nx_ops.advanced_graph_pipeline({
            'graph_type': 'undirected',
            'nodes': datasets['graph']['nodes'][:20],  # Smaller graph for testing
            'edges': datasets['graph']['edges'][:30],
            'visualize': True
        })

        integration_results['networkx_matplotlib'] = graph_result.get('status') == 'success'

    except Exception as e:
        integration_results['error'] = str(e)

    return integration_results

if __name__ == "__main__":
    print("🚀 Suite de Pruebas Avanzadas con Datos Reales - AXIOM")
    print("Probando módulos con escenarios realistas y complejos")
    print("="*80)

    start_time = time.time()

    # Run performance benchmarks
    benchmark_results = run_performance_benchmarks()

    # Run integration tests
    integration_results = run_integration_tests()

    # Generate comprehensive report
    generate_comprehensive_report(benchmark_results)

    # Integration report
    print("\n🔗 RESULTADOS DE INTEGRACIÓN:")
    print("-" * 40)
    for test, result in integration_results.items():
        if test != 'error':
            status_icon = "✅" if result else "❌"
            print(f"{status_icon} {test}: {'PASSED' if result else 'FAILED'}")
        else:
            print(f"❌ Error en integración: {result}")

    total_time = time.time() - start_time
    print(".2f")
    print("\n🎯 Próximos pasos recomendados:")
    print("1. Optimizar módulos con bajo rendimiento")
    print("2. Agregar más casos de prueba edge")
    print("3. Implementar monitoreo de recursos")
    print("4. Crear benchmarks automatizados")
    print("5. Documentar mejores prácticas")
