"""
Router de Validación Estadística Rigurosa para AXIOM
====================================================

Endpoints para validación estadística avanzada de hipótesis científicas.
Implementa herramientas de rigor científico incluyendo power analysis,
corrección múltiple, análisis bayesiano y validación de supuestos.

Endpoints:
- POST /validate-hypothesis: Validación comprehensiva de hipótesis
- POST /power-analysis: Análisis de poder estadístico
- POST /multiple-testing: Corrección por múltiples comparaciones
- POST /effect-sizes: Cálculo de tamaños de efecto
- GET /validation-config: Configuraciones de validación disponibles

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import numpy as np

from app.core.bootstrap_logging import logger
from app.services.statistical_validation_service import StatisticalValidationService
from app.services.statistical_validation import ValidationConfig, ValidationReport
from app.exceptions.domain.biology import BiologyError
from app.types.statistical_validation_types import (
    CalculatePowerAnalysisResult,
    CorrectMultipleTestingResult,
    CalculateEffectSizesResult,
    GetValidationConfigResult,
)
router = APIRouter()

# Instancia global del servicio
validation_service = StatisticalValidationService()


class HypothesisValidationRequest(BaseModel):
    """Request para validación de hipótesis"""
    data: List[float] = Field(..., description="Datos experimentales")
    hypothesis_type: str = Field(
        default="one_sample_ttest", 
        description="Tipo de prueba estadística"
    )
    mu: Optional[float] = Field(None, description="Valor de referencia para prueba t")
    data2: Optional[List[float]] = Field(None, description="Segunda muestra para comparación")
    p_values: Optional[List[float]] = Field(None, description="Valores p para corrección múltiple")
    confidence_level: float = Field(0.95, ge=0.8, le=0.99, description="Nivel de confianza")
    alpha: float = Field(0.05, ge=0.01, le=0.1, description="Nivel de significancia")
    power: float = Field(0.8, ge=0.5, le=0.99, description="Poder estadístico deseado")
    effect_size: Optional[float] = Field(None, description="Tamaño de efecto esperado")
    multiple_comparisons_method: str = Field(
        "bonferroni", 
        description="Método para corrección múltiple"
    )
    bootstrap_iterations: int = Field(1000, ge=100, le=10000, description="Iteraciones bootstrap")


class PowerAnalysisRequest(BaseModel):
    """Request para análisis de poder"""
    effect_size: float = Field(..., description="Tamaño de efecto")
    sample_size: Optional[int] = Field(None, description="Tamaño de muestra actual")
    power: Optional[float] = Field(None, description="Poder deseado")
    alpha: float = Field(0.05, description="Nivel de significancia")


class MultipleTestingRequest(BaseModel):
    """Request para corrección múltiple"""
    p_values: List[float] = Field(..., description="Lista de valores p")
    method: str = Field("bonferroni", description="Método de corrección")
    alpha: float = Field(0.05, description="Nivel de significancia")


class EffectSizeRequest(BaseModel):
    """Request para cálculo de tamaños de efecto"""
    data1: List[float] = Field(..., description="Primera muestra")
    data2: Optional[List[float]] = Field(None, description="Segunda muestra")
    test_type: str = Field("cohen_d", description="Tipo de efecto a calcular")


@router.post("/validate-hypothesis")
async def validate_hypothesis_comprehensively(
    request: HypothesisValidationRequest
) -> Dict[str, Any]:
    """
    🔬 Validación Estadística Comprehensiva de Hipótesis
    
    Realiza una validación multi-nivel de hipótesis científicas utilizando
    herramientas estadísticas avanzadas para garantizar rigor científico.
    
    **Validaciones incluidas:**
    - Power analysis para tamaño de muestra adecuado
    - Corrección por múltiples comparaciones
    - Análisis bayesiano con intervalos de credibilidad
    - Intervalos de confianza bootstrap
    - Cálculo de tamaños de efecto
    - Verificación de supuestos estadísticos
    
    **Respuesta exitosa:**
    ```json
    {
        "is_valid": true,
        "power_analysis": {
            "achieved_power": 0.85,
            "required_sample_size": 30,
            "power_adequate": true
        },
        "multiple_testing": {
            "method": "bonferroni",
            "significant_after_correction": 2
        },
        "bayesian_analysis": {
            "posterior_mean_mu": 5.2,
            "hdi_mu": [4.1, 6.3]
        },
        "bootstrap_ci": {
            "confidence_interval": [4.8, 5.7],
            "confidence_level": 0.95
        },
        "effect_sizes": {
            "cohens_d": 0.65,
            "interpretation": "Efecto mediano"
        },
        "assumptions_check": {
            "normality": {"passed": true},
            "outliers": {"count": 1, "percentage": 2.5}
        },
        "recommendations": [
            "El estudio cumple con los criterios de rigor estadístico"
        ]
    }
    ```
    """
    try:
        logger.info("🔬 Iniciando validación estadística comprehensiva")
        logger.info(f"📊 Datos: {len(request.data)} observaciones, tipo: {request.hypothesis_type}")
        
        # Validaciones de entrada
        if len(request.data) < 3:
            raise HTTPException(
                status_code=400,
                detail="Se requieren al menos 3 observaciones para validación estadística"
            )
        
        # Verificar que los datos sean válidos
        if not all(isinstance(x, (int, float)) and not np.isnan(x) and np.isfinite(x) for x in request.data):
            raise HTTPException(
                status_code=400,
                detail="Todos los valores deben ser números finitos"
            )
        
        # Crear configuración
        config = ValidationConfig(
            confidence_level=request.confidence_level,
            alpha=request.alpha,
            power=request.power,
            effect_size=request.effect_size,
            multiple_comparisons_method=request.multiple_comparisons_method,
            bootstrap_iterations=request.bootstrap_iterations
        )
        
        # Preparar kwargs para la validación
        kwargs = {}
        if request.mu is not None:
            kwargs['mu'] = request.mu
        if request.data2 is not None:
            kwargs['data2'] = request.data2
        if request.p_values is not None:
            kwargs['p_values'] = request.p_values
        
        # Ejecutar validación
        data_array = np.array(request.data)
        result = await validation_service.validate_hypothesis_rigorously(
            data_array, 
            request.hypothesis_type,
            config,
            **kwargs
        )
        
        logger.info(f"✅ Validación completada. Válido: {result.is_valid}")
        
        return {
            "is_valid": result.is_valid,
            "power_analysis": result.power_analysis,
            "multiple_testing": result.multiple_testing,
            "bayesian_analysis": result.bayesian_analysis,
            "bootstrap_ci": result.bootstrap_ci,
            "effect_sizes": result.effect_sizes,
            "assumptions_check": result.assumptions_check,
            "recommendations": result.recommendations,
            "validation_summary": {
                "hypothesis_type": request.hypothesis_type,
                "sample_size": len(request.data),
                "confidence_level": request.confidence_level,
                "alpha": request.alpha
            }
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"❌ Error en validación estadística: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en validación estadística: {str(e)}"
        )


@router.post("/power-analysis")
async def calculate_power_analysis(request: PowerAnalysisRequest) -> CalculatePowerAnalysisResult:
    """
    📈 Análisis de Poder Estadístico
    
    Calcula el poder estadístico, tamaño de muestra requerido o efecto
    detectable dado los otros parámetros.
    
    **Parámetros:**
    - effect_size: Tamaño de efecto esperado
    - sample_size: Tamaño de muestra (opcional)
    - power: Poder deseado (opcional)
    - alpha: Nivel de significancia
    
    **Respuesta exitosa:**
    ```json
    {
        "effect_size": 0.5,
        "given_parameters": {
            "sample_size": 30,
            "alpha": 0.05
        },
        "calculated": {
            "achieved_power": 0.75,
            "required_sample_size_for_80_power": 45
        },
        "interpretation": "Poder insuficiente con muestra actual"
    }
    ```
    """
    try:
        logger.info("📈 Calculando análisis de poder estadístico")
        
        from app.services.statistical_validation import STATSMODELS_AVAILABLE
        if not STATSMODELS_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="statsmodels no disponible para análisis de poder"
            )
        
        from statsmodels.stats.power import TTestPower
        power_calc = TTestPower()
        
        results = {
            "effect_size": request.effect_size,
            "alpha": request.alpha,
            "given_parameters": {},
            "calculated": {}
        }
        
        # Calcular según los parámetros proporcionados
        if request.sample_size and request.power:
            # Verificar consistencia
            achieved_power = power_calc.solve_power(
                effect_size=abs(request.effect_size),
                nobs=request.sample_size,
                alpha=request.alpha
            )
            results["given_parameters"] = {
                "sample_size": request.sample_size,
                "power": request.power
            }
            results["calculated"]["achieved_power"] = float(achieved_power)
            
        elif request.sample_size:
            # Calcular poder
            achieved_power = power_calc.solve_power(
                effect_size=abs(request.effect_size),
                nobs=request.sample_size,
                alpha=request.alpha
            )
            results["given_parameters"]["sample_size"] = request.sample_size
            results["calculated"]["achieved_power"] = float(achieved_power)
            
        elif request.power:
            # Calcular tamaño de muestra
            required_n = power_calc.solve_power(
                effect_size=abs(request.effect_size),
                power=request.power,
                alpha=request.alpha
            )
            results["given_parameters"]["power"] = request.power
            results["calculated"]["required_sample_size"] = int(np.ceil(required_n))
        
        # Siempre calcular tamaño para poder 0.8 como referencia
        ref_n = power_calc.solve_power(
            effect_size=abs(request.effect_size),
            power=0.8,
            alpha=request.alpha
        )
        results["calculated"]["required_sample_size_for_80_power"] = int(np.ceil(ref_n))
        
        # Interpretación
        if "achieved_power" in results["calculated"]:
            power = results["calculated"]["achieved_power"]
            if power >= 0.8:
                interpretation = "Poder adecuado para detectar el efecto"
            elif power >= 0.7:
                interpretation = "Poder marginalmente adecuado"
            else:
                interpretation = "Poder insuficiente, aumentar tamaño de muestra"
        else:
            interpretation = "Análisis de tamaño de muestra completado"
        
        results["interpretation"] = interpretation
        
        logger.info("✅ Análisis de poder completado")
        return results
        
    except BiologyError as e:
        logger.error(f"❌ Error en análisis de poder: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis de poder: {str(e)}"
        )


@router.post("/multiple-testing")
async def correct_multiple_testing(request: MultipleTestingRequest) -> CorrectMultipleTestingResult:
    """
    🔢 Corrección por Múltiples Comparaciones
    
    Aplica corrección estadística para múltiples comparaciones usando
    diferentes métodos (Bonferroni, FDR, Holm, etc.).
    
    **Métodos disponibles:**
    - bonferroni: Corrección conservadora de Bonferroni
    - fdr_bh: False Discovery Rate (Benjamini-Hochberg)
    - holm: Método de Holm (menos conservador que Bonferroni)
    - sidak: Corrección de Šidák
    
    **Respuesta exitosa:**
    ```json
    {
        "method": "bonferroni",
        "original_p_values": [0.03, 0.01, 0.08, 0.002],
        "corrected_p_values": [0.12, 0.04, 0.32, 0.008],
        "rejected_hypotheses": [false, true, false, true],
        "significant_before": 3,
        "significant_after": 2,
        "alpha_corrected": 0.0125
    }
    ```
    """
    try:
        logger.info("🔢 Aplicando corrección por múltiples comparaciones")
        logger.info(f"📊 {len(request.p_values)} valores p, método: {request.method}")
        
        from app.services.statistical_validation import STATSMODELS_AVAILABLE
        if not STATSMODELS_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="statsmodels no disponible para corrección múltiple"
            )
        
        # Validaciones
        if len(request.p_values) < 2:
            raise HTTPException(
                status_code=400,
                detail="Se requieren al menos 2 valores p para corrección múltiple"
            )
        
        if any(p < 0 or p > 1 for p in request.p_values):
            raise HTTPException(
                status_code=400,
                detail="Todos los valores p deben estar entre 0 y 1"
            )
        
        from statsmodels.stats.multitest import multipletests
        
        # Aplicar corrección
        corrected = multipletests(
            request.p_values,
            alpha=request.alpha,
            method=request.method
        )
        
        significant_before = sum(1 for p in request.p_values if p < request.alpha)
        significant_after = int(np.sum(corrected[0]))
        
        result = {
            "method": request.method,
            "alpha": request.alpha,
            "original_p_values": request.p_values,
            "corrected_p_values": corrected[1].tolist(),
            "rejected_hypotheses": corrected[0].tolist(),
            "significant_before": significant_before,
            "significant_after": significant_after,
            "alpha_corrected": float(corrected[3]) if len(corrected) > 3 else request.alpha,
            "family_wise_error_rate": float(corrected[3]) if len(corrected) > 3 else None
        }
        
        # Interpretación
        if significant_after < significant_before:
            result["interpretation"] = f"La corrección redujo de {significant_before} a {significant_after} comparaciones significativas"
        elif significant_after == significant_before:
            result["interpretation"] = "La corrección no cambió el número de comparaciones significativas"
        else:
            result["interpretation"] = "Resultado inesperado en la corrección"
        
        logger.info(f"✅ Corrección completada: {significant_before} → {significant_after} significativas")
        return result
        
    except BiologyError as e:
        logger.error(f"❌ Error en corrección múltiple: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en corrección múltiple: {str(e)}"
        )


@router.post("/effect-sizes")
async def calculate_effect_sizes(request: EffectSizeRequest) -> CalculateEffectSizesResult:
    """
    📏 Cálculo de Tamaños de Efecto
    
    Calcula diferentes medidas de tamaño de efecto para cuantificar
    la magnitud práctica de los hallazgos estadísticos.
    
    **Tipos de efecto:**
    - cohen_d: d de Cohen para diferencias de medias
    - glass_delta: Delta de Glass (usa SD del grupo control)
    - hedge_g: g de Hedges (corrección para muestras pequeñas)
    - eta_squared: Eta cuadrado (proporción de varianza explicada)
    
    **Respuesta exitosa:**
    ```json
    {
        "test_type": "cohen_d",
        "effect_sizes": {
            "cohens_d": 0.65,
            "glass_delta": 0.58,
            "hedges_g": 0.62
        },
        "interpretation": {
            "cohens_d": "Efecto mediano",
            "magnitude": "moderado",
            "practical_significance": "meaningful"
        },
        "sample_info": {
            "n1": 30,
            "n2": 28,
            "mean_difference": 2.3
        }
    }
    ```
    """
    try:
        logger.info("📏 Calculando tamaños de efecto")
        
        # Validaciones
        if len(request.data1) < 2:
            raise HTTPException(
                status_code=400,
                detail="Se requieren al menos 2 observaciones en data1"
            )
        
        data1 = np.array(request.data1)
        
        results = {
            "test_type": request.test_type,
            "effect_sizes": {},
            "interpretation": {},
            "sample_info": {
                "n1": len(data1),
                "mean1": float(np.mean(data1)),
                "std1": float(np.std(data1, ddof=1))
            }
        }
        
        if request.data2 is not None:
            # Comparación de dos grupos
            data2 = np.array(request.data2)
            
            if len(data2) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Se requieren al menos 2 observaciones en data2"
                )
            
            mean1, mean2 = np.mean(data1), np.mean(data2)
            std1, std2 = np.std(data1, ddof=1), np.std(data2, ddof=1)
            n1, n2 = len(data1), len(data2)
            
            # Cohen's d
            pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
            cohens_d = (mean1 - mean2) / pooled_std
            
            # Glass's delta (usando std del grupo 2 como control)
            glass_delta = (mean1 - mean2) / std2
            
            # Hedges' g (corrección para muestras pequeñas)
            correction_factor = 1 - (3 / (4 * (n1 + n2) - 9))
            hedges_g = cohens_d * correction_factor
            
            results["effect_sizes"] = {
                "cohens_d": float(cohens_d),
                "glass_delta": float(glass_delta),
                "hedges_g": float(hedges_g)
            }
            
            results["sample_info"].update({
                "n2": n2,
                "mean2": float(mean2),
                "std2": float(std2),
                "mean_difference": float(mean1 - mean2),
                "pooled_std": float(pooled_std)
            })
            
            # Interpretación de Cohen's d
            abs_d = abs(cohens_d)
            if abs_d < 0.2:
                magnitude = "trivial"
                practical = "negligible"
            elif abs_d < 0.5:
                magnitude = "pequeño"
                practical = "small but meaningful"
            elif abs_d < 0.8:
                magnitude = "mediano"
                practical = "meaningful"
            else:
                magnitude = "grande"
                practical = "large and important"
            
            results["interpretation"] = {
                "cohens_d": f"Efecto {magnitude}",
                "magnitude": magnitude,
                "practical_significance": practical,
                "direction": "positivo" if cohens_d > 0 else "negativo"
            }
            
        else:
            # Una sola muestra
            results["interpretation"] = {
                "note": "Análisis de una muestra. Proporcione data2 para comparación de grupos."
            }
        
        logger.info("✅ Cálculo de tamaños de efecto completado")
        return results
        
    except BiologyError as e:
        logger.error(f"❌ Error calculando tamaños de efecto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculando tamaños de efecto: {str(e)}"
        )


@router.get("/validation-config")
async def get_validation_config() -> GetValidationConfigResult:
    """
    ⚙️ Configuraciones de Validación Disponibles
    
    Retorna las configuraciones y opciones disponibles para
    validación estadística rigurosa.
    
    **Respuesta:**
    ```json
    {
        "hypothesis_types": [
            "one_sample_ttest",
            "two_sample_ttest",
            "paired_ttest"
        ],
        "multiple_testing_methods": [
            "bonferroni",
            "fdr_bh",
            "holm",
            "sidak"
        ],
        "effect_size_types": [
            "cohen_d",
            "glass_delta",
            "hedge_g"
        ],
        "default_config": {
            "confidence_level": 0.95,
            "alpha": 0.05,
            "power": 0.8,
            "bootstrap_iterations": 1000
        },
        "dependencies": {
            "scipy": true,
            "statsmodels": true,
            "pymc": false
        }
    }
    ```
    """
    try:
        # Verificar dependencias disponibles
        from app.services.statistical_validation import (
            SCIPY_AVAILABLE, 
            STATSMODELS_AVAILABLE, 
            PYMC_AVAILABLE,
            PINGOUIN_AVAILABLE
        )
        
        config = {
            "hypothesis_types": [
                "one_sample_ttest",
                "two_sample_ttest", 
                "paired_ttest"
            ],
            "multiple_testing_methods": [
                "bonferroni",
                "fdr_bh", 
                "holm",
                "sidak",
                "fdr_by"
            ],
            "effect_size_types": [
                "cohen_d",
                "glass_delta", 
                "hedge_g",
                "eta_squared"
            ],
            "default_config": {
                "confidence_level": 0.95,
                "alpha": 0.05,
                "power": 0.8,
                "bootstrap_iterations": 1000,
                "bayesian_samples": 2000
            },
            "dependencies": {
                "scipy": SCIPY_AVAILABLE,
                "statsmodels": STATSMODELS_AVAILABLE,
                "pymc": PYMC_AVAILABLE,
                "pingouin": PINGOUIN_AVAILABLE
            },
            "interpretation_scales": {
                "cohens_d": {
                    "trivial": "< 0.2",
                    "small": "0.2 - 0.5",
                    "medium": "0.5 - 0.8", 
                    "large": "> 0.8"
                },
                "power": {
                    "insufficient": "< 0.7",
                    "marginal": "0.7 - 0.8",
                    "adequate": "> 0.8"
                }
            }
        }
        
        return config
        
    except BiologyError as e:
        logger.error(f"❌ Error obteniendo configuración: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo configuración: {str(e)}"
        )
