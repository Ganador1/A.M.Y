#!/usr/bin/env python3
"""
Sistema de Experimentos Científicos Múltiples y Paralelos
Ejecuta múltiples experimentos científicos en diferentes dominios simultáneamente
"""

import concurrent.futures
import numpy as np
import pandas as pd
from datetime import datetime
import json
import time
from typing import Dict, List, Any
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error, r2_score

# Configuración de dominios científicos
SCIENTIFIC_DOMAINS = {
    'materials_science': {
        'focus': 'High-temperature nickel superalloys',
        'variables': ['Y_content', 'Ce_content', 'temperature_C', 'processing_time_h'],
        'targets': ['yield_strength_MPa', 'creep_resistance_h', 'oxidation_rate']
    },
    'chemistry': {
        'focus': 'Catalytic reaction optimization',
        'variables': ['catalyst_concentration', 'temperature_K', 'pressure_atm', 'reaction_time_min'],
        'targets': ['conversion_rate', 'selectivity', 'reaction_rate']
    },
    'biology': {
        'focus': 'Enzyme kinetics and protein expression',
        'variables': ['substrate_concentration', 'pH', 'temperature_C', 'incubation_time_h'],
        'targets': ['enzyme_activity', 'protein_yield', 'growth_rate']
    }
}

class ParallelScientificExperiments:
    """Sistema para ejecutar múltiples experimentos científicos en paralelo"""
    
    def __init__(self, domains: List[str] = None):
        self.domains = domains or list(SCIENTIFIC_DOMAINS.keys())
        self.results = {}
        self.optimization_history = {}
    
    def generate_hypothesis(self, domain: str) -> str:
        """Genera hipótesis científica para un dominio específico"""
        domain_config = SCIENTIFIC_DOMAINS[domain]
        
        hypotheses = {
            'materials_science': 
                "The synergistic addition of Yttrium and Cerium to nickel-based superalloys will "
                "significantly enhance high-temperature mechanical properties through grain boundary "
                "strengthening and improved oxide scale adhesion.",
            'chemistry':
                "Optimizing catalyst concentration and reaction conditions will maximize conversion "
                "rates while maintaining high selectivity in heterogeneous catalytic reactions.",
            'biology':
                "Precise control of substrate concentration and pH will optimize enzyme kinetics "
                "and maximize protein expression yields in recombinant systems."
        }
        
        return hypotheses.get(domain, "Scientific hypothesis for experimental investigation.")
    
    def design_experiments(self, domain: str, n_samples: int = 20) -> Dict:
        """Diseña experimentos para un dominio científico"""
        domain_config = SCIENTIFIC_DOMAINS[domain]
        
        experimental_design = {
            'domain': domain,
            'focus': domain_config['focus'],
            'n_samples': n_samples,
            'variables': {},
            'experimental_conditions': []
        }
        
        # Generar condiciones experimentales
        for i in range(n_samples):
            conditions = {}
            
            if domain == 'materials_science':
                conditions = {
                    'Y_content': np.round(np.random.uniform(0.1, 2.0), 2),
                    'Ce_content': np.round(np.random.uniform(0.1, 1.5), 2),
                    'temperature_C': np.random.choice([800, 850, 900, 950, 1000]),
                    'processing_time_h': np.random.choice([1, 2, 4, 8, 16])
                }
            elif domain == 'chemistry':
                conditions = {
                    'catalyst_concentration': np.round(np.random.uniform(0.01, 1.0), 3),
                    'temperature_K': np.random.choice([300, 323, 348, 373, 398]),
                    'pressure_atm': np.random.choice([1, 2, 5, 10, 20]),
                    'reaction_time_min': np.random.choice([5, 15, 30, 60, 120])
                }
            elif domain == 'biology':
                conditions = {
                    'substrate_concentration': np.round(np.random.uniform(0.1, 10.0), 2),
                    'pH': np.round(np.random.uniform(5.0, 8.0), 1),
                    'temperature_C': np.random.choice([25, 30, 37, 42, 50]),
                    'incubation_time_h': np.random.choice([12, 24, 36, 48, 72])
                }
            
            experimental_design['experimental_conditions'].append(conditions)
        
        return experimental_design
    
    def generate_synthetic_data(self, experimental_design: Dict) -> pd.DataFrame:
        """Genera datos sintéticos basados en el diseño experimental"""
        domain = experimental_design['domain']
        conditions = experimental_design['experimental_conditions']
        
        data = []
        
        for i, cond in enumerate(conditions):
            sample_data = cond.copy()
            sample_data['sample_id'] = f"{domain[:2].upper()}{i+1:02d}"
            
            # Generar resultados sintéticos basados en relaciones físicas realistas
            if domain == 'materials_science':
                # Modelo simplificado para propiedades de superaleaciones
                base_strength = 250  # MPa
                y_effect = 15 * cond['Y_content']
                ce_effect = 12 * cond['Ce_content']
                temp_effect = -0.2 * (cond['temperature_C'] - 800)
                time_effect = 2 * np.log(cond['processing_time_h'])
                
                sample_data['yield_strength_MPa'] = np.round(base_strength + y_effect + ce_effect + temp_effect + time_effect + np.random.normal(0, 5), 1)
                sample_data['creep_resistance_h'] = np.round(100 + 20 * cond['Y_content'] + 15 * cond['Ce_content'] - 0.1 * (cond['temperature_C'] - 800) + np.random.normal(0, 10), 1)
                sample_data['oxidation_rate'] = np.round(0.5 - 0.1 * cond['Y_content'] - 0.08 * cond['Ce_content'] + 0.002 * (cond['temperature_C'] - 800) + np.random.normal(0, 0.05), 3)
                
            elif domain == 'chemistry':
                # Modelo para reacciones catalíticas
                base_conversion = 0.3
                cat_effect = 0.4 * np.log(cond['catalyst_concentration'] + 0.1)
                temp_effect = 0.001 * (cond['temperature_K'] - 300)
                pressure_effect = 0.02 * np.log(cond['pressure_atm'])
                time_effect = 0.1 * np.log(cond['reaction_time_min'])
                
                sample_data['conversion_rate'] = np.round(base_conversion + cat_effect + temp_effect + pressure_effect + time_effect + np.random.normal(0, 0.05), 3)
                sample_data['selectivity'] = np.round(0.85 - 0.1 * cond['catalyst_concentration'] + 0.05 * np.log(cond['temperature_K']) + np.random.normal(0, 0.03), 3)
                sample_data['reaction_rate'] = np.round(sample_data['conversion_rate'] / cond['reaction_time_min'] * 60 + np.random.normal(0, 0.01), 4)
                
            elif domain == 'biology':
                # Modelo para cinética enzimática
                base_activity = 50
                substrate_effect = 20 * np.log(cond['substrate_concentration'] + 0.1)
                ph_effect = -2 * (cond['pH'] - 7.0)**2
                temp_effect = 1 * (cond['temperature_C'] - 25)
                time_effect = 0.5 * np.log(cond['incubation_time_h'])
                
                sample_data['enzyme_activity'] = np.round(base_activity + substrate_effect + ph_effect + temp_effect + time_effect + np.random.normal(0, 5), 1)
                sample_data['protein_yield'] = np.round(0.6 * sample_data['enzyme_activity'] + np.random.normal(0, 3), 1)
                sample_data['growth_rate'] = np.round(0.1 + 0.02 * np.log(cond['substrate_concentration'] + 0.1) + np.random.normal(0, 0.01), 3)
            
            data.append(sample_data)
        
        return pd.DataFrame(data)
    
    def analyze_results(self, df: pd.DataFrame, domain: str) -> Dict:
        """Analiza resultados experimentales"""
        # Seleccionar solo columnas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df_numeric = df[numeric_cols]
        
        analysis = {
            'descriptive_stats': df_numeric.describe().to_dict(),
            'correlations': df_numeric.corr().to_dict(),
            'model_performance': {}
        }
        
        # Modelado predictivo para cada variable objetivo
        domain_config = SCIENTIFIC_DOMAINS[domain]
        
        for target in domain_config['targets']:
            if target in df_numeric.columns:
                # Preparar datos
                X = df_numeric[domain_config['variables']].copy()
                y = df_numeric[target]
                
                # Entrenar modelo
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                
                # Validación cruzada
                cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
                
                # Entrenar modelo final
                model.fit(X, y)
                y_pred = model.predict(X)
                
                analysis['model_performance'][target] = {
                    'r2_score': float(r2_score(y, y_pred)),
                    'rmse': float(np.sqrt(mean_squared_error(y, y_pred))),
                    'cv_r2_mean': float(np.mean(cv_scores)),
                    'cv_r2_std': float(np.std(cv_scores)),
                    'feature_importance': dict(zip(X.columns, model.feature_importances_))
                }
        
        return analysis
    
    def optimize_model(self, df: pd.DataFrame, domain: str, target: str) -> Dict:
        """Optimiza el modelo predictivo usando grid search"""
        from sklearn.model_selection import GridSearchCV
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df_numeric = df[numeric_cols]
        
        X = df_numeric[SCIENTIFIC_DOMAINS[domain]['variables']]
        y = df_numeric[target]
        
        # Parámetros para optimización
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10]
        }
        
        model = RandomForestRegressor(random_state=42)
        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='r2', n_jobs=-1)
        grid_search.fit(X, y)
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': float(grid_search.best_score_),
            'best_estimator': str(grid_search.best_estimator_)
        }
    
    def run_single_experiment(self, domain: str) -> Dict:
        """Ejecuta un experimento científico completo para un dominio"""
        print(f"🔬 Ejecutando experimento en dominio: {domain}")
        
        # Paso 1: Generar hipótesis
        hypothesis = self.generate_hypothesis(domain)
        
        # Paso 2: Diseñar experimentos
        experimental_design = self.design_experiments(domain, n_samples=25)
        
        # Paso 3: Generar datos sintéticos
        df = self.generate_synthetic_data(experimental_design)
        
        # Paso 4: Analizar resultados
        analysis = self.analyze_results(df, domain)
        
        # Paso 5: Optimizar modelo (para la variable principal)
        main_target = SCIENTIFIC_DOMAINS[domain]['targets'][0]
        optimization = self.optimize_model(df, domain, main_target)
        
        # Resultados completos
        results = {
            'domain': domain,
            'hypothesis': hypothesis,
            'experimental_design': experimental_design,
            'dataset_size': len(df),
            'analysis': analysis,
            'optimization': optimization,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
        
        print(f"✅ Experimento completado: {domain}")
        return results
    
    def run_parallel_experiments(self, max_workers: int = 3) -> Dict:
        """Ejecuta experimentos en paralelo para todos los dominios"""
        print(f"🚀 INICIANDO {len(self.domains)} EXPERIMENTOS EN PARALELO")
        print("=" * 60)
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Ejecutar todos los experimentos en paralelo
            future_to_domain = {
                executor.submit(self.run_single_experiment, domain): domain 
                for domain in self.domains
            }
            
            # Recolectar resultados
            for future in concurrent.futures.as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    result = future.result()
                    self.results[domain] = result
                except Exception as e:
                    print(f"❌ Error en experimento {domain}: {e}")
                    self.results[domain] = {
                        'domain': domain,
                        'success': False,
                        'error': str(e)
                    }
        
        execution_time = time.time() - start_time
        
        # Generar reporte comparativo
        comparative_analysis = self.generate_comparative_analysis()
        
        print(f"\n🎯 TODOS LOS EXPERIMENTOS COMPLETADOS")
        print(f"⏰ Tiempo total de ejecución: {execution_time:.2f} segundos")
        print("=" * 60)
        
        return {
            'execution_time': execution_time,
            'successful_experiments': sum(1 for r in self.results.values() if r.get('success', False)),
            'failed_experiments': sum(1 for r in self.results.values() if not r.get('success', True)),
            'results': self.results,
            'comparative_analysis': comparative_analysis
        }
    
    def generate_comparative_analysis(self) -> Dict:
        """Genera análisis comparativo entre todos los dominios"""
        comparative = {
            'model_performance': {},
            'best_domains': {},
            'key_insights': []
        }
        
        # Comparar rendimiento de modelos
        for domain, result in self.results.items():
            if result.get('success', False):
                analysis = result['analysis']
                if 'model_performance' in analysis:
                    comparative['model_performance'][domain] = {}
                    for target, perf in analysis['model_performance'].items():
                        comparative['model_performance'][domain][target] = {
                            'r2_score': perf['r2_score'],
                            'cv_r2_mean': perf['cv_r2_mean']
                        }
        
        # Identificar mejores dominios por métrica
        metrics = ['r2_score', 'cv_r2_mean']
        for metric in metrics:
            best_domain = None
            best_value = -float('inf')
            
            for domain, targets in comparative['model_performance'].items():
                for target, values in targets.items():
                    if values[metric] > best_value:
                        best_value = values[metric]
                        best_domain = domain
            
            if best_domain:
                comparative['best_domains'][metric] = {
                    'domain': best_domain,
                    'value': best_value
                }
        
        # Generar insights clave
        if comparative['model_performance']:
            comparative['key_insights'] = [
                f"Dominio con mejor predictividad: {comparative['best_domains'].get('r2_score', {}).get('domain', 'N/A')}",
                f"Mejor R² score: {comparative['best_domains'].get('r2_score', {}).get('value', 0):.3f}",
                f"Número total de experimentos exitosos: {sum(1 for r in self.results.values() if r.get('success', False))}"
            ]
        
        return comparative
    
    def save_results(self, filename: str = None) -> str:
        """Guarda todos los resultados en archivos"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"parallel_experiments_results_{timestamp}"
        
        # Guardar resultados completos en JSON
        results_json = {
            'metadata': {
                'execution_date': datetime.now().isoformat(),
                'domains_studied': self.domains,
                'total_experiments': len(self.results)
            },
            'results': self.results,
            'comparative_analysis': self.generate_comparative_analysis()
        }
        
        # Función para hacer objetos serializables
        def make_serializable(obj):
            if isinstance(obj, (bool, np.bool_)):
                return bool(obj)
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            return obj
        
        # Guardar archivo JSON
        json_filename = f"{filename}.json"
        with open(json_filename, 'w') as f:
            json.dump(make_serializable(results_json), f, indent=2)
        
        # Guardar datos en CSV por dominio
        for domain, result in self.results.items():
            if result.get('success', False) and 'experimental_design' in result:
                df = self.generate_synthetic_data(result['experimental_design'])
                csv_filename = f"{filename}_{domain}_data.csv"
                df.to_csv(csv_filename, index=False)
        
        return json_filename

def main():
    """Función principal para ejecutar experimentos paralelos"""
    print("=" * 80)
    print("🔬 SISTEMA DE EXPERIMENTOS CIENTÍFICOS PARALELOS")
    print("=" * 80)
    
    # Crear sistema de experimentos
    experiment_system = ParallelScientificExperiments()
    
    # Ejecutar experimentos en paralelo
    final_results = experiment_system.run_parallel_experiments(max_workers=3)
    
    # Guardar resultados
    results_file = experiment_system.save_results()
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   • Experimentos exitosos: {final_results['successful_experiments']}/{len(experiment_system.domains)}")
    print(f"   • Tiempo de ejecución: {final_results['execution_time']:.2f} segundos")
    print(f"   • Archivo de resultados: {results_file}")
    
    # Mostrar mejores resultados
    comparative = final_results['comparative_analysis']
    if comparative.get('best_domains'):
        print(f"\n🏆 MEJORES RESULTADOS:")
        for metric, best in comparative['best_domains'].items():
            print(f"   • {metric}: {best['domain']} (valor: {best['value']:.3f})")
    
    print("\n" + "=" * 80)
    print("🎯 PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 80)

if __name__ == "__main__":
    main()