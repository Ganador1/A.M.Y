"""
Analizador de Persistencia Topológica Real para AXIOM
=====================================================

Implementa análisis de persistencia topológica usando bibliotecas especializadas
como Gudhi o algoritmos propios para cálculo correcto de diagramas de persistencia.

Características:
- Construcción de complejos de Vietoris-Rips con filtración
- Cálculo real de homología persistente
- Generación de diagramas de persistencia precisos
- Métricas de estabilidad (distancias bottleneck y Wasserstein)
- Análisis de características topológicas robustas

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from scipy.spatial.distance import pdist, squareform
import networkx as nx

# Intentar importar Gudhi para análisis real
try:
    import gudhi
    GUDHI_AVAILABLE = True
except ImportError:
    GUDHI_AVAILABLE = False
    gudhi = None

logger = logging.getLogger(__name__)


class PersistenceAnalyzer:
    """
    Analizador avanzado de persistencia topológica
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def compute_persistence_diagram(
        self,
        points: List[Tuple[float, float]],
        max_edge_length: float = 2.0,
        max_dimension: int = 2
    ) -> Dict[str, Any]:
        """
        Computa diagrama de persistencia real usando Gudhi o implementación propia
        
        Args:
            points: Lista de puntos 2D
            max_edge_length: Longitud máxima de aristas en el complejo
            max_dimension: Dimensión máxima para homología
            
        Returns:
            Diagrama de persistencia con pares (birth, death)
        """
        try:
            if GUDHI_AVAILABLE:
                return await self._compute_with_gudhi(points, max_edge_length, max_dimension)
            else:
                return await self._compute_with_custom_algorithm(points, max_edge_length, max_dimension)
                
        except Exception as e:
            self.logger.error(f"Error computing persistence diagram: {str(e)}")
            raise
    
    async def _compute_with_gudhi(
        self,
        points: List[Tuple[float, float]],
        max_edge_length: float,
        max_dimension: int
    ) -> Dict[str, Any]:
        """Implementación usando Gudhi para persistencia real"""
        
        # Crear complejo de Vietoris-Rips
        rips_complex = gudhi.RipsComplex(
            points=points,
            max_edge_length=max_edge_length
        )
        
        # Crear árbol simplicial
        simplex_tree = rips_complex.create_simplex_tree(max_dimension=max_dimension)
        
        # Computar persistencia
        persistence = simplex_tree.persistence(
            min_persistence=0.0
        )
        
        # Procesar resultados
        persistence_diagram = []
        
        for dim, (birth, death) in persistence:
            # Filtrar infinitos (puntos que nunca mueren)
            if death != float('inf'):
                persistence_val = death - birth
                persistence_diagram.append({
                    "dimension": int(dim),
                    "birth": float(birth),
                    "death": float(death),
                    "persistence": float(persistence_val)
                })
        
        # Calcular números de Betti en función del parámetro de filtración
        betti_curves = self._compute_betti_curves_gudhi(simplex_tree, max_dimension)
        
        # Métricas adicionales
        persistence_entropy = self._calculate_persistence_entropy(persistence_diagram)
        lifetime_mean = np.mean([p["persistence"] for p in persistence_diagram]) if persistence_diagram else 0.0
        lifetime_std = np.std([p["persistence"] for p in persistence_diagram]) if persistence_diagram else 0.0
        
        return {
            "persistence_diagram": persistence_diagram,
            "betti_curves": betti_curves,
            "persistence_entropy": persistence_entropy,
            "lifetime_statistics": {
                "mean": float(lifetime_mean),
                "std": float(lifetime_std),
                "total_features": len(persistence_diagram)
            },
            "algorithm": "gudhi_rips",
            "max_dimension": max_dimension
        }
    
    async def _compute_with_custom_algorithm(
        self,
        points: List[Tuple[float, float]],
        max_edge_length: float,
        max_dimension: int
    ) -> Dict[str, Any]:
        """Implementación personalizada para persistencia topológica"""
        
        # Matriz de distancias
        points_array = np.array(points)
        dist_matrix = squareform(pdist(points_array))
        
        # Crear filtración de grafos por umbral de distancia
        filtration_values = np.linspace(0, max_edge_length, 50)
        
        persistence_diagram = []
        betti_curves = {i: [] for i in range(max_dimension + 1)}
        
        previous_components = {}
        component_birth_times = {}
        
        for i, threshold in enumerate(filtration_values):
            # Crear grafo para este umbral
            graph = nx.Graph()
            graph.add_nodes_from(range(len(points)))
            
            # Agregar aristas dentro del umbral
            for u in range(len(points)):
                for v in range(u + 1, len(points)):
                    if dist_matrix[u, v] <= threshold:
                        graph.add_edge(u, v)
            
            # Analizar componentes conexas (homología H0)
            current_components = list(nx.connected_components(graph))
            n_components = len(current_components)
            betti_curves[0].append(n_components)
            
            # Detectar nacimiento y muerte de componentes
            if i == 0:
                # Primer paso: todas las componentes nacen
                for j, comp in enumerate(current_components):
                    component_id = f"comp_{j}_{threshold}"
                    component_birth_times[component_id] = threshold
            else:
                # Detectar fusiones (muerte de componentes)
                prev_n_components = len(previous_components.get(i-1, []))
                if n_components < prev_n_components:
                    # Algunas componentes se fusionaron (murieron)
                    n_died = prev_n_components - n_components
                    for _ in range(n_died):
                        persistence_diagram.append({
                            "dimension": 0,
                            "birth": filtration_values[max(0, i-1)],
                            "death": threshold,
                            "persistence": threshold - filtration_values[max(0, i-1)]
                        })
            
            # Detectar ciclos (homología H1) - simplificado
            if max_dimension >= 1:
                n_edges = graph.number_of_edges()
                n_nodes = graph.number_of_nodes()
                # Número de Betti H1 = E - N + C (para grafo conexo)
                if n_components == 1 and n_nodes > 0:
                    betti_1 = max(0, n_edges - n_nodes + 1)
                else:
                    betti_1 = max(0, n_edges - n_nodes + n_components)
                betti_curves[1].append(betti_1)
            
            previous_components[i] = current_components
        
        # Completar componentes que nunca murieron
        final_components = previous_components.get(len(filtration_values)-1, [])
        for comp in final_components[1:]:  # Excepto la componente principal
            persistence_diagram.append({
                "dimension": 0,
                "birth": 0.0,
                "death": max_edge_length,
                "persistence": max_edge_length
            })
        
        # Métricas adicionales
        persistence_entropy = self._calculate_persistence_entropy(persistence_diagram)
        lifetime_mean = np.mean([p["persistence"] for p in persistence_diagram]) if persistence_diagram else 0.0
        lifetime_std = np.std([p["persistence"] for p in persistence_diagram]) if persistence_diagram else 0.0
        
        return {
            "persistence_diagram": persistence_diagram,
            "betti_curves": betti_curves,
            "persistence_entropy": persistence_entropy,
            "lifetime_statistics": {
                "mean": float(lifetime_mean),
                "std": float(lifetime_std),
                "total_features": len(persistence_diagram)
            },
            "algorithm": "custom_filtration",
            "max_dimension": max_dimension,
            "filtration_values": filtration_values.tolist()
        }
    
    def _compute_betti_curves_gudhi(
        self,
        simplex_tree,
        max_dimension: int
    ) -> Dict[int, List[float]]:
        """Computa curvas de Betti usando Gudhi"""
        
        try:
            # Obtener valores de filtración
            filtration_values = []
            for simplex, filt_val in simplex_tree.get_filtration():
                filtration_values.append(filt_val)
            
            unique_filtrations = sorted(list(set(filtration_values)))
            
            betti_curves = {i: [] for i in range(max_dimension + 1)}
            
            for filt_val in unique_filtrations:
                # Crear sub-complejo hasta este valor de filtración
                sub_tree = gudhi.SimplexTree()
                for simplex, f_val in simplex_tree.get_filtration():
                    if f_val <= filt_val:
                        sub_tree.insert(simplex, f_val)
                
                # Calcular números de Betti
                betti_numbers = sub_tree.betti_numbers()
                
                for dim in range(max_dimension + 1):
                    if dim < len(betti_numbers):
                        betti_curves[dim].append(betti_numbers[dim])
                    else:
                        betti_curves[dim].append(0)
            
            return betti_curves
            
        except Exception as e:
            self.logger.warning(f"Error computing Betti curves with Gudhi: {str(e)}")
            # Fallback a curvas vacías
            return {i: [0] for i in range(max_dimension + 1)}
    
    def _calculate_persistence_entropy(self, persistence_diagram: List[Dict[str, Any]]) -> float:
        """Calcula la entropía de persistencia"""
        
        if not persistence_diagram:
            return 0.0
        
        try:
            # Obtener valores de persistencia
            lifetimes = [p["persistence"] for p in persistence_diagram if p["persistence"] > 0]
            
            if not lifetimes:
                return 0.0
            
            # Normalizar para crear distribución de probabilidad
            total_lifetime = sum(lifetimes)
            if total_lifetime == 0:
                return 0.0
            
            probabilities = [l / total_lifetime for l in lifetimes]
            
            # Calcular entropía de Shannon
            entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
            
            return float(entropy)
            
        except Exception as e:
            self.logger.warning(f"Error calculating persistence entropy: {str(e)}")
            return 0.0
    
    async def compute_persistence_stability(
        self,
        diagram1: List[Dict[str, Any]],
        diagram2: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Computa métricas de estabilidad entre dos diagramas de persistencia
        """
        
        if not GUDHI_AVAILABLE:
            return {
                "bottleneck_distance": None,
                "wasserstein_distance": None,
                "note": "Gudhi not available for stability metrics"
            }
        
        try:
            # Convertir a formato Gudhi
            def to_gudhi_format(diagram):
                return [(d["dimension"], (d["birth"], d["death"])) for d in diagram]
            
            gudhi_diag1 = to_gudhi_format(diagram1)
            gudhi_diag2 = to_gudhi_format(diagram2)
            
            # Calcular distancias
            bottleneck_dist = gudhi.bottleneck_distance(gudhi_diag1, gudhi_diag2)
            wasserstein_dist = gudhi.wasserstein_distance(gudhi_diag1, gudhi_diag2, order=2)
            
            return {
                "bottleneck_distance": float(bottleneck_dist),
                "wasserstein_distance": float(wasserstein_dist)
            }
            
        except Exception as e:
            self.logger.error(f"Error computing persistence stability: {str(e)}")
            return {
                "bottleneck_distance": None,
                "wasserstein_distance": None,
                "error": str(e)
            }


# Instancia global
persistence_analyzer = PersistenceAnalyzer()
