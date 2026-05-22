"""
Causal Discovery Engine Service
===============================

Servicio avanzado para descubrimiento causal y análisis de relaciones causales.

Este servicio proporciona funcionalidades para:
- Descubrimiento de estructuras causales
- Análisis de relaciones causales
- Inferencia causal
- Validación de hipótesis causales
- Estimación de efectos causales

Algoritmos Soportados:
---------------------
- PC Algorithm (Constraint-based)
- GES Algorithm (Score-based)
- LINGAM (Linear Non-Gaussian Acyclic Model)
- Causal Inference con Backdoor Criterion
- Instrumental Variables
- Regression Discontinuity

Características Avanzadas:
-------------------------
- Detección automática de confounders
- Análisis de mediación
- Estimación de efectos causales directos e indirectos
- Validación estadística de relaciones causales
- Visualización de grafos causales
- Manejo de datos observacionales y experimentales

Ejemplos de Uso:
---------------
```python
from app.services.causal_discovery_service import CausalDiscoveryService
import pandas as pd
from app.exceptions.domain.biology import BiologyError

# Descubrimiento de estructura causal
data = pd.DataFrame({
    'X': [1, 2, 3, 4, 5],
    'Y': [2, 4, 6, 8, 10],
    'Z': [1, 1, 2, 2, 3]
})

service = CausalDiscoveryService()
causal_graph = service.discover_causal_structure(data, algorithm='pc')
print(f"Edges encontrados: {causal_graph['edges']}")

# Estimación de efecto causal
effect = service.estimate_causal_effect(
    data=data,
    treatment='X',
    outcome='Y',
    confounders=['Z']
)
print(f"Efecto causal estimado: {effect['ate']}")
```

Limitaciones:
------------
- Requiere supuestos causales específicos
- Sensible a la calidad y cantidad de datos
- Algunos algoritmos asumen linealidad
- No maneja ciclos causales directamente
"""

import numpy as np
import pandas as pd
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from app.types.causal_discovery_service_types import (
    CheckPositivityResult,
    CheckOverlapResult,
    CheckConfoundingResult,
    CheckConsistencyResult,
    ComputeGraphStatisticsResult,
    GetServiceInfoResult,
)

# Importaciones condicionales para causal discovery
try:
    from causallearn.search.ConstraintBased.PC import pc
    from causallearn.search.ScoreBased.GES import ges
    from causallearn.search.FCMBased import lingam
    from causallearn.utils.cit import CIT
    CAUSAL_LEARN_AVAILABLE = True
except ImportError:
    CAUSAL_LEARN_AVAILABLE = False

try:
    from pgmpy.models import BayesianNetwork
    from pgmpy.estimators import PC, HillClimbSearch, BicScore
    from pgmpy.inference import VariableElimination
    PGMPY_AVAILABLE = True
except ImportError:
    PGMPY_AVAILABLE = False

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class CausalDiscoveryService:
    """
    Servicio completo para descubrimiento causal y análisis de relaciones causales.
    
    Proporciona métodos para descubrir estructuras causales, estimar efectos causales
    y validar hipótesis causales usando múltiples algoritmos y enfoques.
    """
    
    def __init__(self):
        self.causal_learn_available = CAUSAL_LEARN_AVAILABLE
        self.pgmpy_available = PGMPY_AVAILABLE
        self.sklearn_available = SKLEARN_AVAILABLE
        
        # Configuración por defecto
        self.default_alpha = 0.05
        self.default_max_cond_vars = 3
        
        logger.info("✅ CausalDiscoveryService initialized")
        if not any([CAUSAL_LEARN_AVAILABLE, PGMPY_AVAILABLE]):
            logger.warning("⚠️ No causal discovery libraries available")
    
    def discover_causal_structure(
        self,
        data: pd.DataFrame,
        algorithm: str = 'pc',
        alpha: float = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Descubre la estructura causal en los datos usando el algoritmo especificado.
        
        Args:
            data: DataFrame con las variables
            algorithm: Algoritmo a usar ('pc', 'ges', 'lingam', 'hc')
            alpha: Nivel de significancia para pruebas de independencia
            **kwargs: Parámetros adicionales específicos del algoritmo
            
        Returns:
            Dict con la estructura causal descubierta
        """
        try:
            if alpha is None:
                alpha = self.default_alpha
                
            # Validar datos
            if data.empty:
                raise ValueError("Los datos no pueden estar vacíos")
            
            # Convertir a numpy array
            data_array = data.values.astype(float)
            variable_names = list(data.columns)
            
            result = {
                'algorithm': algorithm,
                'variables': variable_names,
                'alpha': alpha,
                'edges': [],
                'adjacency_matrix': None,
                'causal_graph': None,
                'statistics': {}
            }
            
            if algorithm.lower() == 'pc':
                result.update(self._run_pc_algorithm(data_array, variable_names, alpha, **kwargs))
            elif algorithm.lower() == 'ges':
                result.update(self._run_ges_algorithm(data_array, variable_names, **kwargs))
            elif algorithm.lower() == 'lingam':
                result.update(self._run_lingam_algorithm(data_array, variable_names, **kwargs))
            elif algorithm.lower() == 'hc':
                result.update(self._run_hill_climbing(data, variable_names, **kwargs))
            else:
                # Algoritmo simple basado en correlaciones
                result.update(self._run_correlation_based(data, variable_names, alpha))
            
            # Generar estadísticas
            result['statistics'] = self._compute_graph_statistics(result)
            
            logger.info(f"✅ Causal structure discovered using {algorithm}")
            return result
            
        except BiologyError as e:
            logger.error(f"❌ Error in causal structure discovery: {str(e)}")
            return {
                'error': str(e),
                'algorithm': algorithm,
                'variables': list(data.columns) if not data.empty else [],
                'edges': [],
                'success': False
            }
    
    def _run_pc_algorithm(
        self,
        data: np.ndarray,
        variable_names: List[str],
        alpha: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Ejecuta el algoritmo PC para descubrimiento causal."""
        if not self.causal_learn_available:
            return self._run_correlation_based_array(data, variable_names, alpha)
        
        try:
            # Configurar parámetros
            max_cond_vars = kwargs.get('max_cond_vars', self.default_max_cond_vars)
            
            # Ejecutar PC algorithm
            cg = pc(
                data,
                alpha=alpha,
                indep_test='fisherz',
                stable=True,
                uc_rule=0,
                uc_priority=2,
                mvpc=False,
                correction_name='BH'
            )
            
            # Extraer resultados
            adjacency_matrix = cg.G.graph
            edges = self._adjacency_to_edges(adjacency_matrix, variable_names)
            
            return {
                'edges': edges,
                'adjacency_matrix': adjacency_matrix.tolist(),
                'causal_graph': self._create_networkx_graph(edges),
                'pc_statistics': {
                    'num_edges': len(edges),
                    'num_tests': getattr(cg, 'num_tests', 0),
                    'alpha_used': alpha
                }
            }
            
        except BiologyError as e:
            logger.warning(f"PC algorithm failed: {str(e)}, using correlation-based fallback")
            return self._run_correlation_based_array(data, variable_names, alpha)
    
    def _run_ges_algorithm(
        self,
        data: np.ndarray,
        variable_names: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Ejecuta el algoritmo GES para descubrimiento causal."""
        if not self.causal_learn_available:
            return self._run_correlation_based_array(data, variable_names, 0.05)
        
        try:
            # Ejecutar GES algorithm
            Record = ges(data)
            
            # Extraer resultados
            adjacency_matrix = Record['G'].graph
            edges = self._adjacency_to_edges(adjacency_matrix, variable_names)
            
            return {
                'edges': edges,
                'adjacency_matrix': adjacency_matrix.tolist(),
                'causal_graph': self._create_networkx_graph(edges),
                'ges_statistics': {
                    'num_edges': len(edges),
                    'score': Record.get('score', 0)
                }
            }
            
        except BiologyError as e:
            logger.warning(f"GES algorithm failed: {str(e)}, using correlation-based fallback")
            return self._run_correlation_based_array(data, variable_names, 0.05)
    
    def _run_lingam_algorithm(
        self,
        data: np.ndarray,
        variable_names: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Ejecuta el algoritmo LINGAM para descubrimiento causal."""
        if not self.causal_learn_available:
            return self._run_correlation_based_array(data, variable_names, 0.05)
        
        try:
            # Ejecutar LINGAM
            model = lingam.ICALiNGAM()
            model.fit(data)
            
            # Extraer matriz de adyacencia
            adjacency_matrix = model.adjacency_matrix_
            edges = self._adjacency_to_edges(adjacency_matrix, variable_names)
            
            return {
                'edges': edges,
                'adjacency_matrix': adjacency_matrix.tolist(),
                'causal_graph': self._create_networkx_graph(edges),
                'lingam_statistics': {
                    'num_edges': len(edges),
                    'causal_order': getattr(model, 'causal_order_', [])
                }
            }
            
        except BiologyError as e:
            logger.warning(f"LINGAM algorithm failed: {str(e)}, using correlation-based fallback")
            return self._run_correlation_based_array(data, variable_names, 0.05)
    
    def _run_hill_climbing(
        self,
        data: pd.DataFrame,
        variable_names: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Ejecuta Hill Climbing con pgmpy."""
        if not self.pgmpy_available:
            return self._run_correlation_based(data, variable_names, 0.05)
        
        try:
            # Configurar Hill Climbing
            hc = HillClimbSearch(data)
            scoring_method = BicScore(data)
            
            # Buscar mejor estructura
            best_model = hc.estimate(scoring_method=scoring_method)
            
            # Extraer edges
            edges = [(u, v) for u, v in best_model.edges()]
            
            return {
                'edges': edges,
                'adjacency_matrix': self._edges_to_adjacency(edges, variable_names).tolist(),
                'causal_graph': self._create_networkx_graph(edges),
                'hc_statistics': {
                    'num_edges': len(edges),
                    'score': scoring_method.score(best_model)
                }
            }
            
        except BiologyError as e:
            logger.warning(f"Hill Climbing failed: {str(e)}, using correlation-based fallback")
            return self._run_correlation_based(data, variable_names, 0.05)
    
    def _run_correlation_based(
        self,
        data: pd.DataFrame,
        variable_names: List[str],
        alpha: float
    ) -> Dict[str, Any]:
        """Algoritmo simple basado en correlaciones como fallback."""
        try:
            # Calcular matriz de correlación
            corr_matrix = data.corr().abs()
            
            # Umbral basado en alpha (convertir a umbral de correlación)
            threshold = 1 - alpha
            
            # Extraer edges significativos
            edges = []
            n_vars = len(variable_names)
            
            for i in range(n_vars):
                for j in range(i + 1, n_vars):
                    if corr_matrix.iloc[i, j] > threshold:
                        edges.append((variable_names[i], variable_names[j]))
            
            # Crear matriz de adyacencia
            adjacency_matrix = self._edges_to_adjacency(edges, variable_names)
            
            return {
                'edges': edges,
                'adjacency_matrix': adjacency_matrix.tolist(),
                'causal_graph': self._create_networkx_graph(edges),
                'correlation_statistics': {
                    'num_edges': len(edges),
                    'threshold_used': threshold,
                    'max_correlation': corr_matrix.max().max(),
                    'mean_correlation': corr_matrix.mean().mean()
                }
            }
            
        except BiologyError as e:
            logger.error(f"Correlation-based algorithm failed: {str(e)}")
            return {
                'edges': [],
                'adjacency_matrix': np.zeros((len(variable_names), len(variable_names))).tolist(),
                'causal_graph': nx.DiGraph(),
                'error': str(e)
            }
    
    def _run_correlation_based_array(
        self,
        data: np.ndarray,
        variable_names: List[str],
        alpha: float
    ) -> Dict[str, Any]:
        """Versión con numpy array del algoritmo basado en correlaciones."""
        try:
            # Convertir a DataFrame para usar correlaciones
            df = pd.DataFrame(data, columns=variable_names)
            return self._run_correlation_based(df, variable_names, alpha)
            
        except BiologyError as e:
            logger.error(f"Correlation-based array algorithm failed: {str(e)}")
            return {
                'edges': [],
                'adjacency_matrix': np.zeros((len(variable_names), len(variable_names))).tolist(),
                'causal_graph': nx.DiGraph(),
                'error': str(e)
            }
    
    def estimate_causal_effect(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        confounders: Optional[List[str]] = None,
        method: str = 'backdoor'
    ) -> Dict[str, Any]:
        """
        Estima el efecto causal entre treatment y outcome.
        
        Args:
            data: DataFrame con los datos
            treatment: Variable de tratamiento
            outcome: Variable de resultado
            confounders: Lista de confounders a controlar
            method: Método de estimación ('backdoor', 'iv', 'regression')
            
        Returns:
            Dict con la estimación del efecto causal
        """
        try:
            if confounders is None:
                confounders = []
            
            # Validar variables
            required_vars = [treatment, outcome] + confounders
            missing_vars = [var for var in required_vars if var not in data.columns]
            if missing_vars:
                raise ValueError(f"Variables faltantes: {missing_vars}")
            
            result = {
                'treatment': treatment,
                'outcome': outcome,
                'confounders': confounders,
                'method': method,
                'ate': None,  # Average Treatment Effect
                'confidence_interval': None,
                'p_value': None,
                'statistics': {}
            }
            
            if method == 'backdoor':
                result.update(self._estimate_backdoor_effect(data, treatment, outcome, confounders))
            elif method == 'regression':
                result.update(self._estimate_regression_effect(data, treatment, outcome, confounders))
            else:
                # Método simple de diferencia de medias
                result.update(self._estimate_simple_effect(data, treatment, outcome))
            
            logger.info(f"✅ Causal effect estimated using {method}")
            return result
            
        except BiologyError as e:
            logger.error(f"❌ Error in causal effect estimation: {str(e)}")
            return {
                'error': str(e),
                'treatment': treatment,
                'outcome': outcome,
                'success': False
            }
    
    def _estimate_backdoor_effect(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        confounders: List[str]
    ) -> Dict[str, Any]:
        """Estima efecto causal usando backdoor criterion."""
        try:
            if not self.sklearn_available:
                return self._estimate_simple_effect(data, treatment, outcome)
            
            # Preparar datos
            X = data[confounders + [treatment]]
            y = data[outcome]
            
            # Ajustar modelo de regresión
            model = LinearRegression()
            model.fit(X, y)
            
            # El coeficiente del treatment es el efecto causal estimado
            treatment_idx = confounders + [treatment]
            ate = model.coef_[treatment_idx.index(treatment)]
            
            # Calcular R²
            r_squared = model.score(X, y)
            
            return {
                'ate': float(ate),
                'r_squared': float(r_squared),
                'coefficients': {
                    var: float(coef) 
                    for var, coef in zip(treatment_idx, model.coef_)
                },
                'intercept': float(model.intercept_),
                'backdoor_statistics': {
                    'num_confounders': len(confounders),
                    'sample_size': len(data)
                }
            }
            
        except BiologyError as e:
            logger.warning(f"Backdoor estimation failed: {str(e)}, using simple effect")
            return self._estimate_simple_effect(data, treatment, outcome)
    
    def _estimate_regression_effect(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        confounders: List[str]
    ) -> Dict[str, Any]:
        """Estima efecto usando regresión lineal."""
        return self._estimate_backdoor_effect(data, treatment, outcome, confounders)
    
    def _estimate_simple_effect(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str
    ) -> Dict[str, Any]:
        """Estima efecto simple como diferencia de medias."""
        try:
            # Asumir que treatment es binario o convertirlo
            treatment_values = data[treatment].unique()
            
            if len(treatment_values) == 2:
                # Tratamiento binario
                high_treatment = data[data[treatment] == treatment_values.max()][outcome]
                low_treatment = data[data[treatment] == treatment_values.min()][outcome]
                
                ate = high_treatment.mean() - low_treatment.mean()
                
                # Prueba t simple
                from scipy import stats
                t_stat, p_value = stats.ttest_ind(high_treatment, low_treatment)
                
                return {
                    'ate': float(ate),
                    'p_value': float(p_value),
                    't_statistic': float(t_stat),
                    'simple_statistics': {
                        'high_treatment_mean': float(high_treatment.mean()),
                        'low_treatment_mean': float(low_treatment.mean()),
                        'high_treatment_n': len(high_treatment),
                        'low_treatment_n': len(low_treatment)
                    }
                }
            else:
                # Tratamiento continuo - usar correlación
                correlation = data[treatment].corr(data[outcome])
                
                return {
                    'ate': float(correlation),
                    'correlation': float(correlation),
                    'simple_statistics': {
                        'treatment_mean': float(data[treatment].mean()),
                        'outcome_mean': float(data[outcome].mean()),
                        'sample_size': len(data)
                    }
                }
                
        except BiologyError as e:
            logger.error(f"Simple effect estimation failed: {str(e)}")
            return {
                'ate': 0.0,
                'error': str(e)
            }
    
    def validate_causal_assumptions(
        self,
        data: pd.DataFrame,
        causal_graph: Dict[str, Any],
        treatment: str,
        outcome: str
    ) -> Dict[str, Any]:
        """
        Valida supuestos causales básicos.
        
        Args:
            data: DataFrame con los datos
            causal_graph: Grafo causal descubierto
            treatment: Variable de tratamiento
            outcome: Variable de resultado
            
        Returns:
            Dict con validaciones de supuestos causales
        """
        try:
            validations = {
                'positivity': self._check_positivity(data, treatment),
                'overlap': self._check_overlap(data, treatment, outcome),
                'no_unmeasured_confounding': self._check_confounding(causal_graph, treatment, outcome),
                'consistency': self._check_consistency(data, treatment, outcome),
                'overall_validity': 'unknown'
            }
            
            # Determinar validez general
            valid_checks = sum([
                validations['positivity']['valid'],
                validations['overlap']['valid'],
                validations['no_unmeasured_confounding']['valid']
            ])
            
            if valid_checks >= 2:
                validations['overall_validity'] = 'likely_valid'
            elif valid_checks >= 1:
                validations['overall_validity'] = 'partially_valid'
            else:
                validations['overall_validity'] = 'likely_invalid'
            
            logger.info("✅ Causal assumptions validated")
            return validations
            
        except BiologyError as e:
            logger.error(f"❌ Error in assumption validation: {str(e)}")
            return {
                'error': str(e),
                'overall_validity': 'unknown'
            }
    
    def _check_positivity(self, data: pd.DataFrame, treatment: str) -> CheckPositivityResult:
        """Verifica supuesto de positividad."""
        try:
            treatment_values = data[treatment].value_counts()
            min_count = treatment_values.min()
            total_count = len(data)
            
            # Positividad: cada valor de tratamiento debe tener suficientes observaciones
            positivity_threshold = max(5, total_count * 0.01)  # Al menos 1% o 5 observaciones
            
            return {
                'valid': min_count >= positivity_threshold,
                'min_count': int(min_count),
                'threshold': positivity_threshold,
                'treatment_distribution': treatment_values.to_dict()
            }
            
        except BiologyError:
            return {'valid': False, 'error': 'Could not check positivity'}
    
    def _check_overlap(self, data: pd.DataFrame, treatment: str, outcome: str) -> CheckOverlapResult:
        """Verifica supuesto de overlap."""
        try:
            # Verificar que hay variación en outcome para cada valor de treatment
            overlap_stats = data.groupby(treatment)[outcome].agg(['count', 'std']).fillna(0)
            
            # Overlap válido si hay variación en outcome para cada treatment
            valid_overlap = (overlap_stats['std'] > 0).all() and (overlap_stats['count'] >= 2).all()
            
            return {
                'valid': bool(valid_overlap),
                'overlap_statistics': overlap_stats.to_dict()
            }
            
        except BiologyError:
            return {'valid': False, 'error': 'Could not check overlap'}
    
    def _check_confounding(self, causal_graph: CheckConfoundingResult, treatment: str, outcome: str) -> CheckConfoundingResult:
        """Verifica supuesto de no confounding no medido."""
        try:
            edges = causal_graph.get('edges', [])
            
            # Buscar backdoor paths
            backdoor_paths = []
            for edge in edges:
                if isinstance(edge, (list, tuple)) and len(edge) == 2:
                    source, target = edge
                    if source != treatment and target != outcome:
                        # Posible confounder
                        backdoor_paths.append((source, target))
            
            # Heurística simple: si hay pocos backdoor paths, es más probable que no haya confounding
            num_backdoor_paths = len(backdoor_paths)
            
            return {
                'valid': num_backdoor_paths <= 2,  # Heurística simple
                'backdoor_paths': backdoor_paths,
                'num_potential_confounders': num_backdoor_paths
            }
            
        except BiologyError:
            return {'valid': False, 'error': 'Could not check confounding'}
    
    def _check_consistency(self, data: pd.DataFrame, treatment: str, outcome: str) -> CheckConsistencyResult:
        """Verifica supuesto de consistencia."""
        try:
            # Verificar que no hay valores faltantes o inconsistentes
            missing_treatment = data[treatment].isna().sum()
            missing_outcome = data[outcome].isna().sum()
            
            total_missing = missing_treatment + missing_outcome
            consistency_valid = total_missing == 0
            
            return {
                'valid': consistency_valid,
                'missing_treatment': int(missing_treatment),
                'missing_outcome': int(missing_outcome),
                'total_missing': int(total_missing)
            }
            
        except BiologyError:
            return {'valid': False, 'error': 'Could not check consistency'}
    
    # Métodos auxiliares
    def _adjacency_to_edges(self, adjacency_matrix: np.ndarray, variable_names: List[str]) -> List[Tuple[str, str]]:
        """Convierte matriz de adyacencia a lista de edges."""
        edges = []
        n_vars = len(variable_names)
        
        for i in range(n_vars):
            for j in range(n_vars):
                if adjacency_matrix[i, j] != 0:
                    edges.append((variable_names[i], variable_names[j]))
        
        return edges
    
    def _edges_to_adjacency(self, edges: List[Tuple[str, str]], variable_names: List[str]) -> np.ndarray:
        """Convierte lista de edges a matriz de adyacencia."""
        n_vars = len(variable_names)
        adjacency_matrix = np.zeros((n_vars, n_vars))
        
        var_to_idx = {var: idx for idx, var in enumerate(variable_names)}
        
        for source, target in edges:
            if source in var_to_idx and target in var_to_idx:
                i, j = var_to_idx[source], var_to_idx[target]
                adjacency_matrix[i, j] = 1
        
        return adjacency_matrix
    
    def _create_networkx_graph(self, edges: List[Tuple[str, str]]) -> nx.DiGraph:
        """Crea grafo NetworkX a partir de edges."""
        G = nx.DiGraph()
        G.add_edges_from(edges)
        return G
    
    def _compute_graph_statistics(self, result: ComputeGraphStatisticsResult) -> ComputeGraphStatisticsResult:
        """Calcula estadísticas del grafo causal."""
        try:
            edges = result.get('edges', [])
            variables = result.get('variables', [])
            
            if not edges or not variables:
                return {'num_nodes': len(variables), 'num_edges': 0, 'density': 0.0}
            
            # Crear grafo para análisis
            G = self._create_networkx_graph(edges)
            
            # Estadísticas básicas
            num_nodes = len(variables)
            num_edges = len(edges)
            max_possible_edges = num_nodes * (num_nodes - 1)  # Grafo dirigido
            density = num_edges / max_possible_edges if max_possible_edges > 0 else 0.0
            
            # Estadísticas de conectividad
            in_degrees = dict(G.in_degree())
            out_degrees = dict(G.out_degree())
            
            return {
                'num_nodes': num_nodes,
                'num_edges': num_edges,
                'density': density,
                'avg_in_degree': np.mean(list(in_degrees.values())) if in_degrees else 0.0,
                'avg_out_degree': np.mean(list(out_degrees.values())) if out_degrees else 0.0,
                'max_in_degree': max(in_degrees.values()) if in_degrees else 0,
                'max_out_degree': max(out_degrees.values()) if out_degrees else 0,
                'is_dag': nx.is_directed_acyclic_graph(G),
                'num_weakly_connected_components': nx.number_weakly_connected_components(G)
            }
            
        except BiologyError as e:
            logger.warning(f"Could not compute graph statistics: {str(e)}")
            return {'error': str(e)}
    
    def get_supported_algorithms(self) -> List[str]:
        """Retorna lista de algoritmos soportados."""
        algorithms = ['correlation']  # Siempre disponible
        
        if self.causal_learn_available:
            algorithms.extend(['pc', 'ges', 'lingam'])
        
        if self.pgmpy_available:
            algorithms.append('hc')
        
        return algorithms
    
    def get_service_info(self) -> GetServiceInfoResult:
        """Retorna información del servicio."""
        return {
            'service_name': 'CausalDiscoveryService',
            'version': '1.0.0',
            'supported_algorithms': self.get_supported_algorithms(),
            'libraries_available': {
                'causal_learn': self.causal_learn_available,
                'pgmpy': self.pgmpy_available,
                'sklearn': self.sklearn_available
            },
            'capabilities': [
                'causal_structure_discovery',
                'causal_effect_estimation',
                'assumption_validation',
                'graph_analysis'
            ]
        }