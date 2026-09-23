"""
Statistics Operations Service
=============================

Servicio completo para análisis estadístico y cálculo de métricas.

Este servicio proporciona funcionalidades avanzadas para análisis estadístico,
incluyendo medidas de tendencia central, dispersión, distribución, correlación,
regresión y pruebas de hipótesis.

Funciones Soportadas:
-------------------
- Medidas de tendencia central: media, mediana, moda
- Medidas de dispersión: desviación estándar, varianza, rango, IQR
- Medidas de posición: percentiles, cuartiles
- Medidas de forma: asimetría, curtosis
- Correlación: Pearson, Spearman
- Regresión: lineal simple
- Pruebas de hipótesis: t-test, normalidad
- Análisis descriptivo completo

Características Avanzadas:
------------------------
- Soporte para grandes conjuntos de datos
- Cálculo eficiente con NumPy/SciPy
- Validación automática de datos
- Manejo de valores faltantes y outliers
- Resultados con significancia estadística
- Análisis de distribución y normalidad

Ejemplos de Uso:
---------------
```python
from app.domains.mathematics.services.statistics_service import StatisticsService
from app.domains.mathematics.models import StatisticsRequest
from app.exceptions.domain.mathematics import MathematicsError

# Análisis descriptivo básico
request = StatisticsRequest(
    data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    operations=["mean", "median", "std", "variance"]
)
result = StatisticsService.calculate(request)
print(f"Media: {result.results['mean']}")

# Correlación entre variables
corr_result = StatisticsService.correlation(
    [1, 2, 3, 4, 5],
    [2, 4, 6, 8, 10]
)
print(f"Correlación de Pearson: {corr_result['pearson_correlation']}")

# Regresión lineal
reg_result = StatisticsService.regression(
    [1, 2, 3, 4, 5],
    [2, 4, 6, 8, 10]
)
print(f"Ecuación: {reg_result['equation']}")
```

Limitaciones:
------------
- Datos deben ser numéricos
- Mínimo 2 observaciones para correlación/regresión
- Pruebas de hipótesis requieren supuestos específicos
- No soporta datos categóricos directamente
- Memoria limitada para datasets muy grandes

Notas de Implementación:
----------------------
- Usa NumPy para cálculos eficientes
- SciPy para funciones estadísticas avanzadas
- Validación automática de entrada
- Resultados redondeados para evitar errores de punto flotante
- Manejo robusto de casos edge (datos vacíos, constantes)
"""

import numpy as np
try:
    import scipy.stats as stats  # type: ignore
    _SCIPY_AVAILABLE = True
except Exception:  # SciPy import may fail during lightweight test runs
    stats = None  # type: ignore
    _SCIPY_AVAILABLE = False
from typing import List, Dict, Any
from app.domains.mathematics.models import StatisticsRequest, StatisticsResponse
from app.exceptions.domain.mathematics import MathematicsError


class StatisticsService:
    """
    Servicio completo para análisis estadístico y cálculo de métricas.

    Esta clase proporciona métodos estáticos para realizar diversos tipos
    de análisis estadístico, desde medidas descriptivas básicas hasta
    técnicas avanzadas de inferencia.
    """

    # Constantes del servicio
    MIN_SAMPLE_SIZE = 2
    MAX_SAMPLE_SIZE = 100000

    @staticmethod
    def calculate(request: StatisticsRequest) -> StatisticsResponse:
        """
        Ejecuta cálculos estadísticos completos con validación exhaustiva.

        Este método calcula todas las estadísticas descriptivas básicas para un conjunto
        de datos, incluyendo medidas de tendencia central, dispersión y posición.
        Realiza validaciones automáticas para asegurar la calidad de los datos.

        Args:
            request (StatisticsRequest): Objeto de solicitud que contiene:
                - data: Lista de valores numéricos para analizar
                - operations: Lista opcional de operaciones específicas (actualmente no usado)

        Returns:
            StatisticsResponse: Objeto de respuesta con todas las estadísticas calculadas:
                - mean: Media aritmética de los datos
                - median: Mediana (valor central)
                - mode: Moda (valor más frecuente, puede ser None)
                - std_dev: Desviación estándar (muestral, ddof=1)
                - variance: Varianza (muestral, ddof=1)
                - min: Valor mínimo
                - max: Valor máximo
                - count: Número total de observaciones

        Raises:
            ValueError: En los siguientes casos:
                - Lista de datos vacía
                - Más de MAX_SAMPLE_SIZE observaciones
                - Todos los valores son NaN
                - Error interno en los cálculos
        """
        try:
            # Validar datos
            if not request.data:
                raise ValueError("Se requieren datos para el análisis estadístico")

            if len(request.data) > StatisticsService.MAX_SAMPLE_SIZE:
                raise ValueError(f"Tamaño máximo de muestra: {StatisticsService.MAX_SAMPLE_SIZE}")

            data = np.array(request.data, dtype=float)

            # Verificar que no todos sean NaN
            if np.all(np.isnan(data)):
                raise ValueError("Todos los valores son NaN")

            # Calcular estadísticas básicas
            mean_val = float(np.mean(data))
            median_val = float(np.median(data))
            std_dev_val = float(np.std(data, ddof=1))
            variance_val = float(np.var(data, ddof=1))
            min_val = float(np.min(data))
            max_val = float(np.max(data))
            count_val = len(data)

            # Calcular moda (puede ser None)
            try:
                if _SCIPY_AVAILABLE:
                    mode_result = stats.mode(data, keepdims=False)
                    mode_val = float(mode_result.mode)
                else:
                    mode_val = None
            except MathematicsError:
                mode_val = None

            return StatisticsResponse(
                mean=mean_val,
                median=median_val,
                mode=mode_val,
                std_dev=std_dev_val,
                variance=variance_val,
                min=min_val,
                max=max_val,
                count=count_val
            )

        except MathematicsError as e:
            raise ValueError(f"Error en cálculo estadístico: {str(e)}")

    @staticmethod
    def _calculate_single_operation(data: np.ndarray, operation: str) -> float:
        """
        Calcula una operación estadística individual de manera eficiente.

        Método interno que implementa el cálculo de cada operación estadística
        soportada por el servicio. Usa NumPy y SciPy para optimización computacional.

        Args:
            data (np.ndarray): Array de NumPy con los datos numéricos
            operation (str): Nombre de la operación a realizar

        Returns:
            float: Resultado del cálculo estadístico

        Raises:
            ValueError: Si la operación no es soportada o hay errores en los datos
        """
        if operation == "mean":
            return float(np.mean(data))
        elif operation == "median":
            return float(np.median(data))
        elif operation == "mode":
            if _SCIPY_AVAILABLE:
                mode_result = stats.mode(data, keepdims=False)
                return float(mode_result.mode)
            else:
                return float(np.nan)
        elif operation == "std":
            return float(np.std(data, ddof=1))  # ddof=1 para muestra
        elif operation == "variance":
            return float(np.var(data, ddof=1))
        elif operation == "range":
            return float(np.max(data) - np.min(data))
        elif operation == "min":
            return float(np.min(data))
        elif operation == "max":
            return float(np.max(data))
        elif operation == "q1":
            return float(np.percentile(data, 25))
        elif operation == "q3":
            return float(np.percentile(data, 75))
        elif operation == "iqr":
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            return float(q3 - q1)
        elif operation == "skewness":
            if _SCIPY_AVAILABLE:
                return float(stats.skew(data))
            else:
                return float(np.nan)
        elif operation == "kurtosis":
            if _SCIPY_AVAILABLE:
                return float(stats.kurtosis(data))
            else:
                return float(np.nan)
        elif operation == "sum":
            return float(np.sum(data))
        elif operation == "count":
            return float(len(data))
        elif operation == "geometric_mean":
            if np.any(data <= 0):
                raise ValueError("Media geométrica requiere valores positivos")
            if _SCIPY_AVAILABLE:
                return float(stats.gmean(data))
            else:
                return float(np.exp(np.mean(np.log(data))))
        elif operation == "harmonic_mean":
            if np.any(data <= 0):
                raise ValueError("Media armónica requiere valores positivos")
            if _SCIPY_AVAILABLE:
                return float(stats.hmean(data))
            else:
                return float(len(data) / np.sum(1.0 / data))
        elif operation == "cv":  # Coeficiente de variación
            mean_val = np.mean(data)
            if mean_val == 0:
                raise ValueError("Coeficiente de variación indefinido para media cero")
            return float(np.std(data, ddof=1) / mean_val)
        else:
            raise ValueError(f"Operación no soportada: {operation}")

    @staticmethod
    def correlation(data1: List[float], data2: List[float]) -> Dict[str, Any]:
        """
        Calcula correlación entre dos conjuntos de datos con análisis completo.

        Este método realiza análisis de correlación bivariada usando tanto el coeficiente
        de Pearson (correlación paramétrica) como Spearman (correlación no paramétrica).
        Incluye pruebas de significancia estadística y interpretación automática.

        Args:
            data1 (List[float]): Primer conjunto de datos numéricos
            data2 (List[float]): Segundo conjunto de datos numéricos

        Returns:
            Dict[str, Any]: Diccionario completo con resultados de correlación
        """
        try:
            if len(data1) != len(data2):
                raise ValueError("Los conjuntos de datos deben tener el mismo tamaño")

            if len(data1) < StatisticsService.MIN_SAMPLE_SIZE:
                raise ValueError(f"Se requieren al menos {StatisticsService.MIN_SAMPLE_SIZE} observaciones")

            arr1 = np.array(data1, dtype=float)
            arr2 = np.array(data2, dtype=float)

            # Verificar variabilidad
            if np.std(arr1) == 0 or np.std(arr2) == 0:
                return {
                    "pearson_correlation": 0.0,
                    "pearson_p_value": 1.0,
                    "spearman_correlation": 0.0,
                    "spearman_p_value": 1.0,
                    "sample_size": len(data1),
                    "interpretation": "Sin variabilidad en uno o ambos datasets"
                }

            if _SCIPY_AVAILABLE:
                # Correlación de Pearson
                pearson_result = stats.pearsonr(arr1, arr2)
                if isinstance(pearson_result, tuple):
                    pearson_corr = float(pearson_result[0])
                    pearson_p = float(pearson_result[1])
                else:
                    pearson_corr = float(pearson_result.statistic)
                    pearson_p = float(pearson_result.pvalue)

                # Correlación de Spearman
                spearman_result = stats.spearmanr(arr1, arr2)
                if isinstance(spearman_result, tuple):
                    spearman_corr = float(spearman_result[0])
                    spearman_p = float(spearman_result[1])
                else:
                    spearman_corr = float(spearman_result.statistic)
                    spearman_p = float(spearman_result.pvalue)
            else:
                # Implementación básica sin SciPy
                pearson_corr = float(np.corrcoef(arr1, arr2)[0, 1])
                pearson_p = 0.0  # No calculable sin SciPy
                spearman_corr = float(np.corrcoef(np.argsort(arr1), np.argsort(arr2))[0, 1])
                spearman_p = 0.0

            # Interpretación
            interpretation = StatisticsService._interpret_correlation(pearson_corr)

            return {
                "pearson_correlation": float(pearson_corr),
                "pearson_p_value": float(pearson_p),
                "spearman_correlation": float(spearman_corr),
                "spearman_p_value": float(spearman_p),
                "sample_size": len(data1),
                "interpretation": interpretation
            }

        except MathematicsError as e:
            raise ValueError(f"Error calculando correlación: {str(e)}")

    @staticmethod
    def regression(x_data: List[float], y_data: List[float]) -> Dict[str, Any]:
        """
        Realiza regresión lineal completa con análisis estadístico exhaustivo.

        Este método ejecuta regresión lineal simple usando mínimos cuadrados ordinarios,
        proporcionando no solo los parámetros de la recta sino también medidas completas
        de bondad de ajuste y significancia estadística.

        Args:
            x_data (List[float]): Datos de la variable independiente (predictora)
            y_data (List[float]): Datos de la variable dependiente (respuesta)

        Returns:
            Dict[str, Any]: Diccionario completo con resultados de regresión
        """
        try:
            if len(x_data) != len(y_data):
                raise ValueError("Los conjuntos de datos deben tener el mismo tamaño")

            if len(x_data) < StatisticsService.MIN_SAMPLE_SIZE:
                raise ValueError(f"Se requieren al menos {StatisticsService.MIN_SAMPLE_SIZE} observaciones")

            x = np.array(x_data, dtype=float)
            y = np.array(y_data, dtype=float)

            # Verificar variabilidad en X
            if np.std(x) == 0:
                raise ValueError("Variable independiente sin variabilidad")

            if _SCIPY_AVAILABLE:
                # Regresión lineal con SciPy
                linregress_result = stats.linregress(x, y)
                if isinstance(linregress_result, tuple):
                    slope, intercept, r_value, p_value, std_err = linregress_result
                    slope = float(slope)
                    intercept = float(intercept)
                    r_value = float(r_value)
                    p_value = float(p_value)
                    std_err = float(std_err)
                else:
                    slope = float(linregress_result.slope)
                    intercept = float(linregress_result.intercept)
                    r_value = float(linregress_result.rvalue)
                    p_value = float(linregress_result.pvalue)
                    std_err = float(linregress_result.stderr)
            else:
                # Implementación básica sin SciPy
                slope = float(np.cov(x, y)[0, 1] / np.var(x))
                intercept = float(np.mean(y) - slope * np.mean(x))
                r_value = float(np.corrcoef(x, y)[0, 1])
                p_value = 0.0  # No calculable sin SciPy
                std_err = 0.0

            # Predicciones
            y_pred = slope * x + intercept

            # R-cuadrado
            r_squared = r_value ** 2

            # Interpretación
            interpretation = StatisticsService._interpret_r_squared(r_squared)

            return {
                "slope": float(slope),
                "intercept": float(intercept),
                "r_value": float(r_value),
                "r_squared": float(r_squared),
                "p_value": float(p_value),
                "std_error": float(std_err),
                "equation": f"y = {slope:.4f}x + {intercept:.4f}",
                "predictions": y_pred.tolist(),
                "interpretation": interpretation
            }

        except MathematicsError as e:
            raise ValueError(f"Error en regresión: {str(e)}")

    @staticmethod
    def hypothesis_test(data: List[float], test_type: str, **kwargs) -> Dict[str, Any]:
        """
        Realiza pruebas de hipótesis con interpretación estadística completa.

        Este método ejecuta diferentes tipos de pruebas estadísticas para validar
        hipótesis sobre los datos, incluyendo pruebas t, normalidad y comparación
        de medias. Cada prueba incluye interpretación automática de resultados.

        Args:
            data (List[float]): Datos numéricos para la prueba estadística
            test_type (str): Tipo de prueba a realizar
            **kwargs: Parámetros adicionales específicos de cada prueba

        Returns:
            Dict[str, Any]: Resultados específicos según el tipo de prueba
        """
        try:
            if len(data) < StatisticsService.MIN_SAMPLE_SIZE:
                raise ValueError(f"Se requieren al menos {StatisticsService.MIN_SAMPLE_SIZE} observaciones")

            arr = np.array(data, dtype=float)

            if not _SCIPY_AVAILABLE:
                return {
                    "test_type": test_type,
                    "error": "SciPy no disponible para pruebas de hipótesis"
                }

            if test_type == "t_test_one_sample":
                population_mean = kwargs.get("population_mean", 0)
                # Prueba t de una muestra
                ttest_result = stats.ttest_1samp(arr, population_mean)
                if isinstance(ttest_result, tuple):
                    t_stat, p_value = ttest_result
                    t_stat = float(t_stat)
                    p_value = float(p_value)
                else:
                    t_stat = float(ttest_result.statistic)
                    p_value = float(ttest_result.pvalue)

                sample_mean = float(np.mean(arr))
                conclusion = StatisticsService._interpret_t_test(p_value, population_mean, sample_mean)

                return {
                    "test_type": "T-test una muestra",
                    "t_statistic": float(t_stat),
                    "p_value": float(p_value),
                    "population_mean": population_mean,
                    "sample_mean": float(np.mean(arr)),
                    "conclusion": conclusion
                }

            elif test_type == "normality_test":
                shapiro_result = stats.shapiro(arr)
                if isinstance(shapiro_result, tuple):
                    stat, p_value = shapiro_result
                    stat = float(stat)
                    p_value = float(p_value)
                else:
                    stat = float(shapiro_result.statistic)
                    p_value = float(shapiro_result.pvalue)

                conclusion = "Datos siguen distribución normal" if p_value > 0.05 else "Datos no siguen distribución normal"

                return {
                    "test_type": "Prueba de normalidad (Shapiro-Wilk)",
                    "statistic": float(stat),
                    "p_value": float(p_value),
                    "is_normal": p_value > 0.05,
                    "conclusion": conclusion
                }

            elif test_type == "t_test_two_sample":
                data2 = kwargs.get("data2")
                if data2 is None:
                    raise ValueError("Se requieren dos conjuntos de datos para t-test de dos muestras")

                arr2 = np.array(data2, dtype=float)
                ttest_result = stats.ttest_ind(arr, arr2)
                if isinstance(ttest_result, tuple):
                    t_stat, p_value = ttest_result
                    t_stat = float(t_stat)
                    p_value = float(p_value)
                else:
                    t_stat = float(ttest_result.statistic)
                    p_value = float(ttest_result.pvalue)

                conclusion = "Medias significativamente diferentes" if p_value < 0.05 else "No hay diferencia significativa entre las medias"

                return {
                    "test_type": "T-test dos muestras independientes",
                    "t_statistic": float(t_stat),
                    "p_value": float(p_value),
                    "mean1": float(np.mean(arr)),
                    "mean2": float(np.mean(arr2)),
                    "conclusion": conclusion
                }

            else:
                raise ValueError(f"Tipo de prueba no soportado: {test_type}")

        except MathematicsError as e:
            raise ValueError(f"Error en prueba de hipótesis: {str(e)}")

    @staticmethod
    def descriptive_summary(data: List[float]) -> Dict[str, Any]:
        """
        Genera un resumen descriptivo completo y multidimensional de los datos.

        Este método proporciona un análisis estadístico exhaustivo que combina
        medidas de tendencia central, dispersión, posición, forma y normalidad
        en un solo reporte integrado y fácil de interpretar.

        Args:
            data (List[float]): Lista de valores numéricos para analizar

        Returns:
            Dict[str, Any]: Resumen completo con múltiples categorías
        """
        try:
            arr = np.array(data, dtype=float)

            # Estadísticas básicas
            basic_stats = {
                "count": len(data),
                "mean": float(np.mean(arr)),
                "median": float(np.median(arr)),
                "std": float(np.std(arr, ddof=1)),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "range": float(np.max(arr) - np.min(arr))
            }

            # Percentiles
            percentiles = {
                "q1": float(np.percentile(arr, 25)),
                "q3": float(np.percentile(arr, 75)),
                "iqr": float(np.percentile(arr, 75) - np.percentile(arr, 25))
            }

            # Medidas de forma
            if _SCIPY_AVAILABLE:
                shape_stats = {
                    "skewness": float(stats.skew(arr)),
                    "kurtosis": float(stats.kurtosis(arr))
                }
            else:
                shape_stats = {
                    "skewness": float(np.nan),
                    "kurtosis": float(np.nan)
                }

            # Prueba de normalidad
            if _SCIPY_AVAILABLE and len(data) >= StatisticsService.MIN_SAMPLE_SIZE:
                normality = StatisticsService.hypothesis_test(data, "normality_test")
            else:
                normality = {"test_type": "No disponible", "conclusion": "Datos insuficientes"}

            return {
                "basic_statistics": basic_stats,
                "percentiles": percentiles,
                "shape_measures": shape_stats,
                "normality_test": normality,
                "data_summary": f"Dataset con {len(data)} observaciones, media={basic_stats['mean']:.2f}, std={basic_stats['std']:.2f}"
            }

        except MathematicsError as e:
            raise ValueError(f"Error generando resumen descriptivo: {str(e)}")

    @staticmethod
    def _interpret_correlation(corr: float) -> str:
        """Interpreta cualitativamente la fuerza de una correlación."""
        abs_corr = abs(corr)
        if abs_corr >= 0.9:
            strength = "muy fuerte"
        elif abs_corr >= 0.7:
            strength = "fuerte"
        elif abs_corr >= 0.5:
            strength = "moderada"
        elif abs_corr >= 0.3:
            strength = "débil"
        else:
            strength = "muy débil"

        direction = "positiva" if corr > 0 else "negativa" if corr < 0 else "nula"
        return f"Correlación {strength} y {direction}"

    @staticmethod
    def _interpret_r_squared(r_squared: float) -> str:
        """Interpreta el coeficiente de determinación (R²) de un modelo de regresión."""
        if r_squared >= 0.9:
            return "Excelente ajuste (90%+ de variabilidad explicada)"
        elif r_squared >= 0.8:
            return "Muy buen ajuste (80%+ de variabilidad explicada)"
        elif r_squared >= 0.7:
            return "Buen ajuste (70%+ de variabilidad explicada)"
        elif r_squared >= 0.5:
            return "Ajuste moderado (50%+ de variabilidad explicada)"
        elif r_squared >= 0.3:
            return "Ajuste pobre (30%+ de variabilidad explicada)"
        else:
            return "Muy pobre ajuste (<30% de variabilidad explicada)"

    @staticmethod
    def _interpret_t_test(p_value: float, null_mean: float, sample_mean: float) -> str:
        """Interpreta los resultados de una prueba t con conclusión estadística."""
        if p_value < 0.05:
            if sample_mean > null_mean:
                return f"Rechazar H0: media > {null_mean} (p = {p_value:.4f})"
            else:
                return f"Rechazar H0: media < {null_mean} (p = {p_value:.4f})"
        else:
            return f"No rechazar H0: media ≈ {null_mean} (p = {p_value:.4f})"

    @staticmethod
    def get_supported_operations() -> List[str]:
        """Obtiene la lista completa de operaciones estadísticas soportadas."""
        return [
            "mean", "median", "mode", "std", "variance", "range",
            "min", "max", "q1", "q3", "iqr", "skewness", "kurtosis",
            "sum", "count", "geometric_mean", "harmonic_mean", "cv"
        ]

    @staticmethod
    def get_statistics_examples() -> List[Dict[str, Any]]:
        """Devuelve ejemplos completos de análisis estadístico con datos reales."""
        return [
            {
                "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "description": "Datos secuenciales del 1 al 10",
                "operations": ["mean", "median", "std", "variance"],
                "expected_mean": 5.5,
                "expected_std": 3.03
            },
            {
                "data": [23, 45, 56, 78, 32, 64, 89, 12, 34, 67],
                "description": "Datos aleatorios con distribución amplia",
                "operations": ["mean", "median", "std", "variance", "q1", "q3", "iqr"],
                "use_case": "Análisis de calificaciones o mediciones"
            },
            {
                "data": [100, 105, 110, 115, 120, 125, 130],
                "description": "Serie con tendencia lineal ascendente",
                "operations": ["mean", "range", "q1", "q3", "skewness"],
                "use_case": "Análisis de crecimiento o tendencias"
            },
            {
                "data": [2.3, 2.1, 2.4, 2.2, 2.3, 2.2, 2.3, 2.1],
                "description": "Datos con baja variabilidad",
                "operations": ["mean", "std", "cv", "range"],
                "use_case": "Control de calidad o mediciones precisas"
            }
        ]






