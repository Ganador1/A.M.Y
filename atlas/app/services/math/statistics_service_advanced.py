"""
Advanced Statistics Service - AXIOM ATLAS
==========================================

Servicio avanzado de análisis estadístico con capacidades de nivel enterprise.
Extiende el StatisticsService básico con modelos bayesianos, análisis multivariado,
pruebas estadísticas avanzadas y visualizaciones interactivas.

Características Avanzadas:
-------------------------
- Modelos Bayesianos (PyMC)
- Análisis Multivariado (PCA, Factor Analysis, Clustering)
- Pruebas Estadísticas Avanzadas (Multiple Testing, Survival Analysis)
- Visualizaciones Interactivas (Plotly/Dash)
- Machine Learning Integration
- Statistical Power Analysis
- Time Series Analysis
- Experimental Design Support

Autor: AXIOM ATLAS Team
Fecha: Septiembre 2025
Versión: 2.0.0-Advanced
"""

import numpy as np
import pandas as pd
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
from app.exceptions.domain.biology import BiologyError

# Advanced statistical libraries
try:
    import pymc as pm
    import arviz as az
    PYMC_AVAILABLE = True
except ImportError:
    PYMC_AVAILABLE = False

try:
    from sklearn.decomposition import PCA, FactorAnalysis
    from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_val_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import statsmodels.api as sm
    from statsmodels.stats.multitest import multipletests
    from statsmodels.stats.power import ttest_power, tt_solve_power
    from statsmodels.stats.contingency_tables import mcnemar
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    from scipy import stats
    from scipy.cluster.hierarchy import dendrogram, linkage
    from scipy.spatial.distance import pdist, squareform
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from app.services.base_service import BaseService
from app.types.statistics_service_advanced_types import (
    GetServiceCapabilitiesResult,
    HealthCheckResult,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BayesianModelResult:
    """Resultado de análisis bayesiano"""
    model_name: str
    posterior_samples: Dict[str, np.ndarray]
    summary_stats: Dict[str, Any]
    convergence_diagnostics: Dict[str, Any]
    model_comparison: Optional[Dict[str, Any]] = None
    predictions: Optional[np.ndarray] = None
    credible_intervals: Optional[Dict[str, Tuple[float, float]]] = None

@dataclass
class MultivariateAnalysisResult:
    """Resultado de análisis multivariado"""
    analysis_type: str
    components: Optional[np.ndarray] = None
    explained_variance: Optional[np.ndarray] = None
    loadings: Optional[np.ndarray] = None
    scores: Optional[np.ndarray] = None
    clusters: Optional[np.ndarray] = None
    silhouette_score: Optional[float] = None
    interpretation: Optional[str] = None

@dataclass
class StatisticalTestResult:
    """Resultado de prueba estadística avanzada"""
    test_name: str
    statistic: float
    p_value: float
    effect_size: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    interpretation: Optional[str] = None
    assumptions_met: Optional[bool] = None

@dataclass
class PowerAnalysisResult:
    """Resultado de análisis de potencia"""
    effect_size: float
    sample_size: int
    power: float
    alpha: float
    test_type: str
    recommendations: List[str] = field(default_factory=list)

class AdvancedStatisticsService(BaseService):
    """
    Servicio avanzado de análisis estadístico con capacidades de nivel enterprise.
    
    Extiende las funcionalidades del StatisticsService básico con:
    - Modelos bayesianos avanzados
    - Análisis multivariado completo
    - Pruebas estadísticas sofisticadas
    - Visualizaciones interactivas
    - Machine learning integration
    """
    
    def __init__(self):
        super().__init__("AdvancedStatisticsService")
        self.version = "2.0.0-advanced"
        
        # Configuración avanzada
        self.advanced_config = {
            "bayesian": {
                "default_samples": 2000,
                "default_chains": 4,
                "default_tune": 1000,
                "convergence_threshold": 1.01
            },
            "multivariate": {
                "max_components": 10,
                "clustering_methods": ["kmeans", "hierarchical", "dbscan"],
                "scaling_method": "standard"
            },
            "visualization": {
                "default_width": 800,
                "default_height": 600,
                "theme": "plotly_white",
                "export_formats": ["png", "pdf", "html"]
            },
            "power_analysis": {
                "default_alpha": 0.05,
                "default_power": 0.8,
                "effect_size_range": (0.1, 2.0)
            }
        }
        
        # Verificar disponibilidad de librerías
        self._check_dependencies()
        
    def _check_dependencies(self):
        """Verificar disponibilidad de dependencias avanzadas"""
        dependencies = {
            "PyMC": PYMC_AVAILABLE,
            "Scikit-learn": SKLEARN_AVAILABLE,
            "Plotly": PLOTLY_AVAILABLE,
            "Statsmodels": STATSMODELS_AVAILABLE,
            "SciPy": SCIPY_AVAILABLE
        }
        
        missing = [lib for lib, available in dependencies.items() if not available]
        if missing:
            logger.warning(f"Dependencias faltantes: {missing}. Algunas funcionalidades estarán limitadas.")
        
        self.dependencies_status = dependencies
    
    async def bayesian_linear_regression(self, 
                                       x_data: List[float], 
                                       y_data: List[float],
                                       prior_type: str = "weakly_informative",
                                       samples: int = 2000) -> BayesianModelResult:
        """
        Regresión lineal bayesiana usando PyMC.
        
        Args:
            x_data: Variable independiente
            y_data: Variable dependiente
            prior_type: Tipo de priores ("weakly_informative", "informative", "non_informative")
            samples: Número de muestras para MCMC
            
        Returns:
            BayesianModelResult con resultados del modelo bayesiano
        """
        if not PYMC_AVAILABLE:
            raise ImportError("PyMC no está disponible. Instale con: pip install pymc")
        
        try:
            x = np.array(x_data)
            y = np.array(y_data)
            
            # Definir modelo bayesiano
            with pm.Model() as model:
                # Priores según el tipo
                if prior_type == "weakly_informative":
                    alpha = pm.Normal("alpha", mu=0, sigma=10)
                    beta = pm.Normal("beta", mu=0, sigma=10)
                    sigma = pm.HalfNormal("sigma", sigma=1)
                elif prior_type == "informative":
                    alpha = pm.Normal("alpha", mu=np.mean(y), sigma=np.std(y))
                    beta = pm.Normal("beta", mu=0, sigma=1)
                    sigma = pm.HalfNormal("sigma", sigma=np.std(y))
                else:  # non_informative
                    alpha = pm.Flat("alpha")
                    beta = pm.Flat("beta")
                    sigma = pm.HalfFlat("sigma")
                
                # Likelihood
                mu = alpha + beta * x
                likelihood = pm.Normal("y", mu=mu, sigma=sigma, observed=y)
                
                # Sampling
                trace = pm.sample(
                    samples=samples,
                    chains=self.advanced_config["bayesian"]["default_chains"],
                    tune=self.advanced_config["bayesian"]["default_tune"],
                    return_inferencedata=True
                )
            
            # Análisis de convergencia
            convergence = az.summary(trace)
            
            # Estadísticas posteriores
            posterior_samples = {
                "alpha": trace.posterior.alpha.values.flatten(),
                "beta": trace.posterior.beta.values.flatten(),
                "sigma": trace.posterior.sigma.values.flatten()
            }
            
            # Intervalos creíbles
            credible_intervals = {}
            for param in ["alpha", "beta", "sigma"]:
                samples = posterior_samples[param]
                credible_intervals[param] = (
                    np.percentile(samples, 2.5),
                    np.percentile(samples, 97.5)
                )
            
            # Predicciones
            alpha_samples = posterior_samples["alpha"]
            beta_samples = posterior_samples["beta"]
            predictions = np.array([
                alpha_samples[i] + beta_samples[i] * x 
                for i in range(len(alpha_samples))
            ])
            
            return BayesianModelResult(
                model_name="Bayesian Linear Regression",
                posterior_samples=posterior_samples,
                summary_stats=convergence.to_dict(),
                convergence_diagnostics={
                    "rhat_max": float(convergence["r_hat"].max()),
                    "ess_min": float(convergence["ess_bulk"].min()),
                    "converged": float(convergence["r_hat"].max()) < self.advanced_config["bayesian"]["convergence_threshold"]
                },
                predictions=predictions.mean(axis=0),
                credible_intervals=credible_intervals
            )
            
        except BiologyError as e:
            logger.error(f"Error en regresión bayesiana: {e}")
            raise ValueError(f"Error en análisis bayesiano: {str(e)}")
    
    async def principal_component_analysis(self, 
                                          data: List[List[float]], 
                                          n_components: Optional[int] = None,
                                          scaling: bool = True) -> MultivariateAnalysisResult:
        """
        Análisis de Componentes Principales (PCA) avanzado.
        
        Args:
            data: Matriz de datos (observaciones x variables)
            n_components: Número de componentes (None para automático)
            scaling: Si aplicar escalado estándar
            
        Returns:
            MultivariateAnalysisResult con resultados del PCA
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("Scikit-learn no está disponible")
        
        try:
            X = np.array(data)
            
            # Escalado si se requiere
            if scaling:
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
            else:
                X_scaled = X
            
            # Determinar número de componentes
            if n_components is None:
                n_components = min(X.shape[1], self.advanced_config["multivariate"]["max_components"])
            
            # PCA
            pca = PCA(n_components=n_components)
            pca.fit(X_scaled)
            
            # Componentes y varianza explicada
            components = pca.components_
            explained_variance = pca.explained_variance_ratio_
            scores = pca.transform(X_scaled)
            
            # Interpretación
            cumsum_variance = np.cumsum(explained_variance)
            n_significant = np.argmax(cumsum_variance >= 0.95) + 1
            
            interpretation = f"""
            PCA completado con {n_components} componentes.
            Los primeros {n_significant} componentes explican el {cumsum_variance[n_significant-1]:.1%} de la varianza.
            Componente 1: {explained_variance[0]:.1%} de varianza
            Componente 2: {explained_variance[1]:.1%} de varianza
            """
            
            return MultivariateAnalysisResult(
                analysis_type="PCA",
                components=components,
                explained_variance=explained_variance,
                scores=scores,
                interpretation=interpretation.strip()
            )
            
        except BiologyError as e:
            logger.error(f"Error en PCA: {e}")
            raise ValueError(f"Error en análisis PCA: {str(e)}")
    
    async def clustering_analysis(self, 
                                 data: List[List[float]], 
                                 method: str = "kmeans",
                                 n_clusters: Optional[int] = None) -> MultivariateAnalysisResult:
        """
        Análisis de clustering avanzado.
        
        Args:
            data: Matriz de datos
            method: Método de clustering ("kmeans", "hierarchical", "dbscan")
            n_clusters: Número de clusters (None para automático)
            
        Returns:
            MultivariateAnalysisResult con resultados del clustering
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("Scikit-learn no está disponible")
        
        try:
            X = np.array(data)
            
            # Escalado estándar
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Seleccionar método de clustering
            if method == "kmeans":
                if n_clusters is None:
                    # Método del codo para determinar k
                    from sklearn.metrics import silhouette_score
                    silhouette_scores = []
                    K_range = range(2, min(11, X.shape[0]))
                    
                    for k in K_range:
                        kmeans = KMeans(n_clusters=k, random_state=42)
                        cluster_labels = kmeans.fit_predict(X_scaled)
                        silhouette_scores.append(silhouette_score(X_scaled, cluster_labels))
                    
                    n_clusters = K_range[np.argmax(silhouette_scores)]
                
                clusterer = KMeans(n_clusters=n_clusters, random_state=42)
                
            elif method == "hierarchical":
                if n_clusters is None:
                    n_clusters = 3  # Default
                clusterer = AgglomerativeClustering(n_clusters=n_clusters)
                
            elif method == "dbscan":
                clusterer = DBSCAN(eps=0.5, min_samples=5)
                
            else:
                raise ValueError(f"Método de clustering no soportado: {method}")
            
            # Ejecutar clustering
            cluster_labels = clusterer.fit_predict(X_scaled)
            
            # Calcular silhouette score si es posible
            silhouette_score_val = None
            if len(set(cluster_labels)) > 1 and -1 not in cluster_labels:
                from sklearn.metrics import silhouette_score
                silhouette_score_val = silhouette_score(X_scaled, cluster_labels)
            
            # Interpretación
            n_clusters_found = len(set(cluster_labels))
            silhouette_str = f"{silhouette_score_val:.3f}" if silhouette_score_val is not None else "N/A"
            interpretation = f"""
            Clustering {method} completado.
            Clusters encontrados: {n_clusters_found}
            Silhouette Score: {silhouette_str}
            """
            
            return MultivariateAnalysisResult(
                analysis_type=f"Clustering_{method}",
                clusters=cluster_labels,
                silhouette_score=silhouette_score_val,
                interpretation=interpretation.strip()
            )
            
        except BiologyError as e:
            logger.error(f"Error en clustering: {e}")
            raise ValueError(f"Error en análisis de clustering: {str(e)}")
    
    async def multiple_testing_correction(self, 
                                         p_values: List[float], 
                                         method: str = "fdr_bh",
                                         alpha: float = 0.05) -> Dict[str, Any]:
        """
        Corrección para pruebas múltiples.
        
        Args:
            p_values: Lista de valores p
            method: Método de corrección ("fdr_bh", "bonferroni", "holm", "hochberg")
            alpha: Nivel de significancia
            
        Returns:
            Diccionario con resultados de la corrección
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("Statsmodels no está disponible")
        
        try:
            p_values_array = np.array(p_values)
            
            # Aplicar corrección
            rejected, p_corrected, alpha_sidak, alpha_bonf = multipletests(
                p_values_array, 
                alpha=alpha, 
                method=method
            )
            
            # Estadísticas
            n_tests = len(p_values)
            n_rejected = np.sum(rejected)
            n_significant_original = np.sum(p_values_array < alpha)
            
            interpretation = f"""
            Corrección {method} aplicada a {n_tests} pruebas.
            Pruebas significativas originales: {n_significant_original}
            Pruebas significativas después de corrección: {n_rejected}
            Tasa de descubrimiento falso controlada: {alpha}
            """
            
            return {
                "method": method,
                "original_p_values": p_values_array.tolist(),
                "corrected_p_values": p_corrected.tolist(),
                "rejected": rejected.tolist(),
                "alpha": alpha,
                "n_tests": n_tests,
                "n_rejected": int(n_rejected),
                "n_significant_original": int(n_significant_original),
                "interpretation": interpretation.strip()
            }
            
        except BiologyError as e:
            logger.error(f"Error en corrección múltiple: {e}")
            raise ValueError(f"Error en corrección de pruebas múltiples: {str(e)}")
    
    async def power_analysis(self, 
                           effect_size: float,
                           sample_size: Optional[int] = None,
                           power: Optional[float] = None,
                           alpha: float = 0.05,
                           test_type: str = "t-test") -> PowerAnalysisResult:
        """
        Análisis de potencia estadística.
        
        Args:
            effect_size: Tamaño del efecto (Cohen's d)
            sample_size: Tamaño de muestra (None para calcular)
            power: Potencia deseada (None para calcular)
            alpha: Nivel de significancia
            test_type: Tipo de prueba ("t-test", "anova", "correlation")
            
        Returns:
            PowerAnalysisResult con análisis de potencia
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("Statsmodels no está disponible")
        
        try:
            recommendations = []
            
            if test_type == "t-test":
                if sample_size is None and power is not None:
                    # Calcular tamaño de muestra necesario
                    sample_size = int(tt_solve_power(effect_size, power=power, alpha=alpha))
                    recommendations.append(f"Para detectar efecto d={effect_size:.2f} con potencia {power:.1%}, se necesitan {sample_size} observaciones por grupo.")
                
                elif power is None and sample_size is not None:
                    # Calcular potencia
                    power = ttest_power(effect_size, nobs=sample_size, alpha=alpha)
                    recommendations.append(f"Con {sample_size} observaciones por grupo, la potencia para detectar efecto d={effect_size:.2f} es {power:.1%}.")
                
                else:
                    # Calcular ambos
                    power = ttest_power(effect_size, nobs=sample_size, alpha=alpha)
                    recommendations.append(f"Potencia calculada: {power:.1%}")
            
            # Interpretación del tamaño del efecto
            if effect_size < 0.2:
                recommendations.append("Tamaño del efecto pequeño (d < 0.2). Considere aumentar el tamaño de muestra.")
            elif effect_size < 0.5:
                recommendations.append("Tamaño del efecto mediano (0.2 ≤ d < 0.5).")
            elif effect_size < 0.8:
                recommendations.append("Tamaño del efecto grande (0.5 ≤ d < 0.8).")
            else:
                recommendations.append("Tamaño del efecto muy grande (d ≥ 0.8).")
            
            return PowerAnalysisResult(
                effect_size=effect_size,
                sample_size=sample_size or 0,
                power=power or 0.0,
                alpha=alpha,
                test_type=test_type,
                recommendations=recommendations
            )
            
        except BiologyError as e:
            logger.error(f"Error en análisis de potencia: {e}")
            raise ValueError(f"Error en análisis de potencia: {str(e)}")
    
    async def create_interactive_plot(self, 
                                    plot_type: str,
                                    data: Dict[str, Any],
                                    title: str = "Statistical Plot",
                                    width: int = 800,
                                    height: int = 600) -> Dict[str, Any]:
        """
        Crear visualización interactiva con Plotly.
        
        Args:
            plot_type: Tipo de gráfico ("scatter", "histogram", "box", "heatmap", "pca")
            data: Datos para el gráfico
            title: Título del gráfico
            width: Ancho en píxeles
            height: Alto en píxeles
            
        Returns:
            Diccionario con información del gráfico generado
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly no está disponible")
        
        try:
            fig = None
            
            if plot_type == "scatter":
                fig = px.scatter(
                    x=data.get("x", []),
                    y=data.get("y", []),
                    title=title,
                    labels={"x": data.get("x_label", "X"), "y": data.get("y_label", "Y")}
                )
                
            elif plot_type == "histogram":
                fig = px.histogram(
                    x=data.get("values", []),
                    title=title,
                    labels={"x": data.get("x_label", "Value"), "y": "Frequency"}
                )
                
            elif plot_type == "box":
                fig = px.box(
                    y=data.get("values", []),
                    title=title,
                    labels={"y": data.get("y_label", "Value")}
                )
                
            elif plot_type == "heatmap":
                fig = px.imshow(
                    data.get("matrix", []),
                    title=title,
                    color_continuous_scale="RdBu"
                )
                
            elif plot_type == "pca":
                # Gráfico PCA 2D
                scores = data.get("scores", [])
                explained_var = data.get("explained_variance", [])
                
                fig = px.scatter(
                    x=scores[:, 0],
                    y=scores[:, 1],
                    title=f"{title} - PC1 ({explained_var[0]:.1%}) vs PC2 ({explained_var[1]:.1%})",
                    labels={"x": f"PC1 ({explained_var[0]:.1%})", "y": f"PC2 ({explained_var[1]:.1%})"}
                )
            
            else:
                raise ValueError(f"Tipo de gráfico no soportado: {plot_type}")
            
            # Configurar layout
            fig.update_layout(
                width=width,
                height=height,
                template=self.advanced_config["visualization"]["theme"]
            )
            
            # Generar HTML
            html_content = fig.to_html(include_plotlyjs=True)
            
            return {
                "plot_type": plot_type,
                "title": title,
                "html_content": html_content,
                "width": width,
                "height": height,
                "created_at": datetime.now().isoformat()
            }
            
        except BiologyError as e:
            logger.error(f"Error creando gráfico interactivo: {e}")
            raise ValueError(f"Error en visualización: {str(e)}")
    
    async def comprehensive_statistical_analysis(self, 
                                                data: List[List[float]],
                                                analysis_types: List[str] = None) -> Dict[str, Any]:
        """
        Análisis estadístico comprehensivo que combina múltiples técnicas.
        
        Args:
            data: Matriz de datos
            analysis_types: Tipos de análisis a realizar
            
        Returns:
            Diccionario con resultados de todos los análisis
        """
        if analysis_types is None:
            analysis_types = ["descriptive", "pca", "clustering", "correlation"]
        
        results = {
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "data_shape": (len(data), len(data[0]) if data else 0),
                "analysis_types": analysis_types
            }
        }
        
        try:
            # Análisis descriptivo básico
            if "descriptive" in analysis_types:
                X = np.array(data)
                descriptive_stats = {
                    "mean": np.mean(X, axis=0).tolist(),
                    "std": np.std(X, axis=0, ddof=1).tolist(),
                    "min": np.min(X, axis=0).tolist(),
                    "max": np.max(X, axis=0).tolist(),
                    "median": np.median(X, axis=0).tolist()
                }
                results["descriptive"] = descriptive_stats
            
            # PCA
            if "pca" in analysis_types and SKLEARN_AVAILABLE:
                pca_result = await self.principal_component_analysis(data)
                results["pca"] = {
                    "explained_variance": pca_result.explained_variance.tolist() if pca_result.explained_variance is not None else None,
                    "interpretation": pca_result.interpretation
                }
            
            # Clustering
            if "clustering" in analysis_types and SKLEARN_AVAILABLE:
                clustering_result = await self.clustering_analysis(data, method="kmeans")
                results["clustering"] = {
                    "clusters": clustering_result.clusters.tolist() if clustering_result.clusters is not None else None,
                    "silhouette_score": clustering_result.silhouette_score,
                    "interpretation": clustering_result.interpretation
                }
            
            # Correlación
            if "correlation" in analysis_types and len(data[0]) > 1:
                X = np.array(data)
                corr_matrix = np.corrcoef(X.T)
                results["correlation"] = {
                    "correlation_matrix": corr_matrix.tolist(),
                    "max_correlation": float(np.max(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))
                }
            
            return results
            
        except BiologyError as e:
            logger.error(f"Error en análisis comprehensivo: {e}")
            raise ValueError(f"Error en análisis estadístico comprehensivo: {str(e)}")
    
    def get_service_capabilities(self) -> GetServiceCapabilitiesResult:
        """Obtener capacidades del servicio avanzado"""
        return {
            "service_name": "AdvancedStatisticsService",
            "version": self.version,
            "capabilities": {
                "bayesian_analysis": PYMC_AVAILABLE,
                "multivariate_analysis": SKLEARN_AVAILABLE,
                "interactive_visualization": PLOTLY_AVAILABLE,
                "advanced_testing": STATSMODELS_AVAILABLE,
                "power_analysis": STATSMODELS_AVAILABLE
            },
            "dependencies_status": self.dependencies_status,
            "advanced_config": self.advanced_config
        }
    
    async def health_check(self) -> HealthCheckResult:
        """Verificar salud del servicio"""
        return {
            "status": "healthy",
            "service": "AdvancedStatisticsService",
            "version": self.version,
            "dependencies": self.dependencies_status,
            "timestamp": datetime.now().isoformat()
        }

# Instancia del servicio
advanced_statistics_service = AdvancedStatisticsService()
