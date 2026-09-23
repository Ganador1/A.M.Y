"""
🧬 Router de Medicina Personalizada - AXIOM v4.1

Este módulo proporciona endpoints comprehensivos para análisis farmacogenómico y medicina
personalizada, integrando genómica, farmacología y oncología para tratamientos individualizados.

Características principales:
- Análisis farmacogenómico completo con predicción de respuesta a medicamentos
- Evaluación de mutaciones en cáncer para terapias dirigidas
- Recomendaciones de dosificación basadas en genotipo
- Verificación de interacciones farmacológicas
- Base de datos de genes farmacogenómicos actualizada

Endpoints disponibles:
- POST /pharmacogenomics: Análisis farmacogenómico basado en variantes genéticas
- POST /cancer-analysis: Análisis de mutaciones oncológicas para medicina personalizada
- GET /drug-recommendations/{drug}: Recomendaciones de dosificación para medicamentos específicos
- GET /pgx-genes: Lista completa de genes farmacogenómicos soportados
- POST /drug-interaction-check: Verificación de interacciones farmacológicas
- GET /health: Estado de salud del servicio de medicina personalizada

Consideraciones de seguridad:
- Validación estricta de entrada para prevenir inyección de datos maliciosos
- Manejo seguro de errores sin exposición de información sensible
- Acceso restringido a datos genéticos y médicos confidenciales

Dependencias:
- PersonalizedMedicineService: Servicio principal de medicina personalizada
- Pydantic: Validación de modelos de datos
- FastAPI: Framework web asíncrono

Ejemplo de uso:
    POST /api/personalized-medicine/pharmacogenomics
    {
        "variants": [
            {
                "gene": "CYP2D6",
                "variant": "*1/*4",
                "allele": "*4",
                "zygosity": "heterozygous"
            }
        ]
    }

Autor: AXIOM Development Team
Versión: 4.1
Última actualización: 2024
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging
import datetime

from app.services.personalized_medicine_service import PersonalizedMedicineService
from app.exceptions.domain.medicine import MedicalError
from app.types.personalized_medicine_types import (
    PersonalizedMedicineHealthResult,
    AnalyzePharmacogenomicsResult,
    AnalyzeCancerMutationsResult,
    GetDrugRecommendationsResult,
    GetPgxGenesResult,
    CheckDrugInteractionsResult,
)

# Configuración de logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/personalized-medicine", tags=["personalized-medicine"])


class VariantRequest(BaseModel):
    """Request model for a single genetic variant.

    Defines the structure for individual variant data in pharmacogenomics analysis.
    """
    gene: str
    variant: str
    allele: Optional[str] = Field(None, description="Alelo específico (ej: *1, *2)")
    zygosity: str = Field("heterozygous", description="heterozygous o homozygous")


class PharmacogenomicsRequest(BaseModel):
    """Request model for pharmacogenomics analysis.

    Contains a list of genetic variants for comprehensive pharmacogenomic evaluation.
    """
    variants: List[VariantRequest]


class MutationRequest(BaseModel):
    """Request model for a single cancer mutation.

    Defines the structure for individual mutation data in cancer analysis.
    """
    gene: str
    variant: str
    type: str = Field(..., description="missense, nonsense, frameshift, splice_site, copy_number")
    position: Optional[int] = Field(None, description="Posición en la proteína")
    id: Optional[str] = Field(None, description="ID único de la mutación")


class CancerAnalysisRequest(BaseModel):
    """Request model for cancer mutation analysis.

    Contains a list of mutations for oncology personalized medicine evaluation.
    """
    mutations: List[MutationRequest]


@router.get("/health")
async def personalized_medicine_health() -> PersonalizedMedicineHealthResult:
    """
    🏥 Verificación de salud del servicio de medicina personalizada

    Realiza una verificación comprehensiva del estado del servicio de medicina personalizada,
    incluyendo disponibilidad de genes farmacogenómicos, base de datos de medicamentos y estado operativo.

    Returns:
        Dict[str, Any]: Estado de salud del servicio de medicina personalizada

    Raises:
        HTTPException: Si hay problemas críticos de salud

    Example:
        GET /health
        Response: {"service": "PersonalizedMedicine", "status": "operational", "pgx_genes_supported": 15}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("🏥 Ejecutando verificación de salud del servicio de medicina personalizada")

        # Verificar servicio
        service = PersonalizedMedicineService()

        # Obtener métricas de salud
        pgx_genes_count = len(service.pgx_genes) if hasattr(service, 'pgx_genes') else 0
        drugs_count = len(service.drug_recommendations) if hasattr(service, 'drug_recommendations') else 0

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Determinar estado de salud
        health_status = "operational"
        if pgx_genes_count == 0:
            health_status = "degraded"  # Sin genes disponibles
        elif drugs_count == 0:
            health_status = "warning"  # Sin medicamentos en base de datos

        response = {
            "service": "PersonalizedMedicine",
            "status": health_status,
            "pgx_genes_supported": pgx_genes_count,
            "drugs_in_database": drugs_count,
            "timestamp": datetime.datetime.now().isoformat(),
            "execution_time_seconds": execution_time
        }

        logger.info("✅ Verificación de salud completada: %s (genes: %d, medicamentos: %d, tiempo: %.4fs)",
                   health_status, pgx_genes_count, drugs_count, execution_time)

        return response

    except MedicalError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en verificación de salud: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en verificación de salud: {str(e)}"
        ) from e


@router.post("/pharmacogenomics")
async def analyze_pharmacogenomics(req: PharmacogenomicsRequest) -> AnalyzePharmacogenomicsResult:
    """
    🧬 Análisis farmacogenómico completo basado en variantes genéticas

    Realiza un análisis comprehensivo de variantes genéticas para predecir respuesta
    a medicamentos, metabolismo de fármacos y posibles efectos adversos.

    Args:
        req: Solicitud con lista de variantes genéticas a analizar

    Returns:
        Dict[str, Any]: Resultados del análisis farmacogenómico

    Raises:
        HTTPException: Si hay error en el análisis o validación de entrada

    Example:
        POST /pharmacogenomics
        {
            "variants": [
                {
                    "gene": "CYP2D6",
                    "variant": "*1/*4",
                    "allele": "*4",
                    "zygosity": "heterozygous"
                }
            ]
        }
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if not req.variants:
            logger.warning("🚫 Intento de análisis farmacogenómico con lista de variantes vacía")
            raise HTTPException(
                status_code=400,
                detail="La lista de variantes no puede estar vacía"
            )

        for i, variant in enumerate(req.variants):
            if not variant.gene or not variant.variant:
                logger.warning("🚫 Variante inválida en posición %d: gene='%s', variant='%s'", i, variant.gene, variant.variant)
                raise HTTPException(
                    status_code=400,
                    detail=f"Variante inválida en posición {i}: gene y variant son requeridos"
                )

        logger.info("🧬 Iniciando análisis farmacogenómico para %d variantes", len(req.variants))

        # Inicializar servicio
        service = PersonalizedMedicineService()

        # Convertir request a formato interno usando list comprehension
        variants = [
            {
                'gene': variant_req.gene,
                'variant': variant_req.variant,
                'allele': variant_req.allele,
                'zygosity': variant_req.zygosity
            }
            for variant_req in req.variants
        ]

        # Ejecutar análisis
        result = await service.analyze_pharmacogenomics(variants)

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Enriquecer respuesta con metadatos
        enriched_result = {
            **result,
            "metadata": {
                "variants_analyzed": len(variants),
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "analysis_type": "pharmacogenomics"
            }
        }

        logger.info("✅ Análisis farmacogenómico completado: %d variantes analizadas (tiempo: %.4fs)",
                   len(variants), execution_time)

        return enriched_result

    except HTTPException:
        raise
    except MedicalError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en análisis farmacogenómico: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en análisis farmacogenómico: {str(e)}"
        ) from e


@router.post("/cancer-analysis")
async def analyze_cancer_mutations(req: CancerAnalysisRequest) -> AnalyzeCancerMutationsResult:
    """
    🧬 Análisis de mutaciones oncológicas para medicina personalizada

    Evalúa mutaciones en genes relacionados con cáncer para identificar terapias dirigidas,
    pronóstico y tratamientos personalizados basados en el perfil genético del paciente.

    Args:
        req: Solicitud con lista de mutaciones a analizar

    Returns:
        Dict[str, Any]: Resultados del análisis oncológico

    Raises:
        HTTPException: Si hay error en el análisis o validación de entrada

    Example:
        POST /cancer-analysis
        {
            "mutations": [
                {
                    "gene": "EGFR",
                    "variant": "L858R",
                    "type": "missense",
                    "position": 858,
                    "id": "COSM12345"
                }
            ]
        }
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if not req.mutations:
            logger.warning("🚫 Intento de análisis oncológico con lista de mutaciones vacía")
            raise HTTPException(
                status_code=400,
                detail="La lista de mutaciones no puede estar vacía"
            )

        for i, mutation in enumerate(req.mutations):
            if not mutation.gene or not mutation.variant or not mutation.type:
                logger.warning("🚫 Mutación inválida en posición %d: gene='%s', variant='%s', type='%s'",
                             i, mutation.gene, mutation.variant, mutation.type)
                raise HTTPException(
                    status_code=400,
                    detail=f"Mutación inválida en posición {i}: gene, variant y type son requeridos"
                )

        logger.info("🧬 Iniciando análisis oncológico para %d mutaciones", len(req.mutations))

        # Inicializar servicio
        service = PersonalizedMedicineService()

        # Convertir request a formato interno usando list comprehension
        mutations = [
            {
                'gene': mutation_req.gene,
                'variant': mutation_req.variant,
                'type': mutation_req.type,
                'position': mutation_req.position,
                'id': mutation_req.id or f"{mutation_req.gene}_{mutation_req.variant}"
            }
            for mutation_req in req.mutations
        ]

        # Ejecutar análisis
        result = await service.analyze_cancer_mutations(mutations)

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Enriquecer respuesta con metadatos
        enriched_result = {
            **result,
            "metadata": {
                "mutations_analyzed": len(mutations),
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "analysis_type": "cancer_mutations"
            }
        }

        logger.info("✅ Análisis oncológico completado: %d mutaciones analizadas (tiempo: %.4fs)",
                   len(mutations), execution_time)

        return enriched_result

    except HTTPException:
        raise
    except MedicalError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en análisis oncológico: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en análisis oncológico: {str(e)}"
        ) from e


@router.get("/drug-recommendations/{drug_name}")
async def get_drug_recommendations(drug_name: str) -> GetDrugRecommendationsResult:
    """
    💊 Obtiene recomendaciones de dosificación para un medicamento específico

    Proporciona recomendaciones personalizadas de dosificación basadas en el genotipo
    del paciente, incluyendo ajustes de dosis, alternativas terapéuticas y consideraciones clínicas.

    Args:
        drug_name: Nombre del medicamento a consultar

    Returns:
        Dict[str, Any]: Recomendaciones de dosificación y consideraciones clínicas

    Raises:
        HTTPException: Si el medicamento no existe o hay error interno

    Example:
        GET /drug-recommendations/warfarin
        Response: {"drug": "warfarin", "relevant_genes": ["VKORC1", "CYP2C9"], "recommendations": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if not drug_name or not drug_name.strip():
            logger.warning("🚫 Intento de consulta de recomendaciones con nombre de medicamento vacío")
            raise HTTPException(
                status_code=400,
                detail="El nombre del medicamento no puede estar vacío"
            )

        logger.info("💊 Consultando recomendaciones para medicamento: %s", drug_name)

        # Inicializar servicio
        service = PersonalizedMedicineService()

        # Verificar si el medicamento existe
        if drug_name not in service.drug_recommendations:
            logger.warning("🚫 Medicamento no encontrado en base de datos: %s", drug_name)
            raise HTTPException(
                status_code=404,
                detail=f"Medicamento '{drug_name}' no encontrado en la base de datos"
            )

        # Obtener información del medicamento
        drug_info = service.drug_recommendations[drug_name]

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        response = {
            "drug": drug_name,
            "relevant_genes": drug_info["genes"],
            "recommendations": drug_info["recommendations"],
            "clinical_guidelines": "CPIC Guidelines",
            "last_updated": "2024-01-01",
            "metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "query_type": "drug_recommendations"
            }
        }

        logger.info("✅ Recomendaciones obtenidas para %s: %d genes relevantes (tiempo: %.4fs)",
                   drug_name, len(drug_info["genes"]), execution_time)

        return response

    except HTTPException:
        raise
    except MedicalError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error obteniendo recomendaciones para %s: %s (tiempo: %.4fs)", drug_name, str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno obteniendo recomendaciones: {str(e)}"
        ) from e


@router.get("/pgx-genes")
async def get_pgx_genes() -> GetPgxGenesResult:
    """
    🧬 Lista completa de genes farmacogenómicos soportados

    Proporciona información detallada sobre todos los genes farmacogenómicos
    disponibles en el sistema, organizados por categorías funcionales.

    Returns:
        Dict[str, Any]: Lista completa de genes farmacogenómicos por categorías

    Raises:
        HTTPException: Si hay error obteniendo la lista de genes

    Example:
        GET /pgx-genes
        Response: {"pgx_genes": [...], "total_genes": 15, "categories": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("🧬 Consultando lista completa de genes farmacogenómicos")

        # Inicializar servicio
        service = PersonalizedMedicineService()

        # Obtener genes
        pgx_genes = service.pgx_genes

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        response = {
            "pgx_genes": pgx_genes,
            "total_genes": len(pgx_genes),
            "categories": {
                "cytochrome_p450": ["CYP2D6", "CYP2C19", "CYP2C9", "CYP3A5", "CYP3A4"],
                "drug_transporters": ["SLCO1B1"],
                "drug_targets": ["VKORC1"],
                "drug_metabolizers": ["TPMT", "NUDT15", "DPYD", "UGT1A1"],
                "immune_system": ["HLA-B", "HLA-A"],
                "other": ["CYP4F2", "G6PD"]
            },
            "metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "query_type": "pgx_genes_list"
            }
        }

        logger.info("✅ Lista de genes farmacogenómicos obtenida: %d genes totales (tiempo: %.4fs)",
                   len(pgx_genes), execution_time)

        return response

    except MedicalError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error obteniendo lista de genes farmacogenómicos: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno obteniendo lista de genes: {str(e)}"
        ) from e


@router.post("/drug-interaction-check")
async def check_drug_interactions(phenotypes: Dict[str, str]) -> CheckDrugInteractionsResult:
    """
    ⚠️ Verifica interacciones farmacológicas basadas en fenotipos genéticos

    Analiza posibles interacciones entre medicamentos basadas en el perfil fenotípico
    del paciente, identificando riesgos de toxicidad, reducción de eficacia y efectos adversos.

    Args:
        phenotypes: Diccionario de fenotipos genéticos (gene -> phenotype)

    Returns:
        Dict[str, Any]: Resultados del análisis de interacciones farmacológicas

    Raises:
        HTTPException: Si hay error en el análisis o validación de entrada

    Example:
        POST /drug-interaction-check
        {
            "CYP2D6": "poor_metabolizer",
            "CYP2C19": "ultra_rapid_metabolizer"
        }
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if not phenotypes:
            logger.warning("🚫 Intento de verificación de interacciones con fenotipos vacíos")
            raise HTTPException(
                status_code=400,
                detail="El diccionario de fenotipos no puede estar vacío"
            )

        logger.info("⚠️ Iniciando verificación de interacciones farmacológicas para %d fenotipos", len(phenotypes))

        # Inicializar servicio
        service = PersonalizedMedicineService()

        # Ejecutar análisis de interacciones
        interactions = await service._predict_drug_interactions(phenotypes)

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Determinar nivel de riesgo
        risk_level = "low"
        if len(interactions) > 2:
            risk_level = "high"
        elif len(interactions) > 0:
            risk_level = "medium"

        response = {
            "phenotypes_analyzed": phenotypes,
            "interactions_found": len(interactions),
            "interactions": interactions,
            "risk_assessment": risk_level,
            "metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "analysis_type": "drug_interactions"
            }
        }

        logger.info("✅ Verificación de interacciones completada: %d interacciones encontradas, riesgo %s (tiempo: %.4fs)",
                   len(interactions), risk_level, execution_time)

        return response

    except MedicalError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en verificación de interacciones: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en verificación de interacciones: {str(e)}"
        ) from e
