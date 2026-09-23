"""
Advanced Genomics Router

Este módulo proporciona endpoints para análisis genómicos avanzados, incluyendo llamada de variantes,
genómica del cáncer y farmacogenómica. Soporta análisis de datos de secuenciación de nueva generación
con algoritmos de vanguardia para investigación biomédica y medicina personalizada.

Capacidades principales:
- Llamada de variantes germinales con DeepVariant para WGS y WES
- Análisis de mutaciones somáticas con Mutect2 para genómica del cáncer
- Análisis farmacogenómico para medicina personalizada
- Detección y caracterización de variantes estructurales
- Análisis de firmas mutacionales en cáncer
- Soporte multi-plataforma (Illumina, PacBio, Oxford Nanopore)
- Control de calidad y análisis de cobertura
- Seguimiento histórico de análisis y gestión de resultados

Endpoints disponibles:
- GET /health: Verificación del estado del servicio
- GET /supported-analyses: Tipos de análisis genómicos soportados
- POST /variant-calling/deepvariant: Llamada de variantes con DeepVariant
- POST /cancer-analysis: Análisis de mutaciones somáticas en cáncer
- POST /pharmacogenomics: Análisis farmacogenómico
- POST /structural-variants: Análisis de variantes estructurales
- GET /analysis-history: Historial de análisis genómicos
- POST /quick/wgs-analysis: Análisis WGS rápido
- POST /quick/wes-analysis: Análisis WES rápido
- POST /quick/cancer-analysis: Análisis de cáncer rápido
- POST /quick/pgx-analysis: Análisis farmacogenómico rápido

Dependencias:
- AdvancedGenomicsService: Servicio principal de genómica avanzada
- SampleInfo: Modelo para información de muestras
- VariantCallingRequest: Solicitud de llamada de variantes
- CancerAnalysisRequest: Solicitud de análisis de cáncer
- PharmacogenomicsRequest: Solicitud de análisis farmacogenómico
- StructuralVariantRequest: Solicitud de análisis de variantes estructurales

Uso típico:
    from app.domains.biology.routers.advanced_genomics import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles bajo el prefijo /advanced-genomics (agregado bajo /biology)
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from datetime import datetime

from app.domains.biology.services.advanced_genomics_service import AdvancedGenomicsService


router = APIRouter(prefix="/advanced-genomics", tags=["advanced-genomics"])

# Singleton del servicio para evitar recreación por request
_svc: Optional[AdvancedGenomicsService] = None

def get_service() -> AdvancedGenomicsService:
    global _svc
    if _svc is None:
        _svc = AdvancedGenomicsService()
    return _svc


class SampleInfo(BaseModel):
    sample_id: str = Field(..., description="ID único de la muestra")
    file_path: Optional[str] = Field(None, description="Ruta al archivo BAM/CRAM")
    coverage: Optional[float] = Field(None, description="Cobertura promedio")
    sequencing_platform: Optional[str] = Field("illumina", description="Plataforma de secuenciación")
    library_type: Optional[str] = Field("wgs", description="Tipo de librería (wgs/wes/panel)")


class VariantCallingRequest(BaseModel):
    sample_info: SampleInfo
    analysis_type: str = Field("wgs", description="Tipo de análisis (wgs/wes)")
    reference_genome: str = Field("GRCh38", description="Genoma de referencia")
    quality_threshold: float = Field(30.0, description="Umbral de calidad mínimo")


class CancerAnalysisRequest(BaseModel):
    tumor_sample: SampleInfo
    normal_sample: Optional[SampleInfo] = Field(None, description="Muestra normal (opcional)")
    cancer_type: Optional[str] = Field(None, description="Tipo de cáncer si es conocido")
    include_signatures: bool = Field(True, description="Incluir análisis de firmas mutacionales")


class PharmacogenomicsRequest(BaseModel):
    sample_info: SampleInfo
    drug_list: Optional[List[str]] = Field(None, description="Lista de fármacos a evaluar")
    include_interactions: bool = Field(True, description="Incluir análisis de interacciones")


class StructuralVariantRequest(BaseModel):
    sample_info: SampleInfo
    min_sv_size: int = Field(50, description="Tamaño mínimo de SV en bp")
    include_repeats: bool = Field(False, description="Incluir regiones repetitivas")


@router.get("/health")
async def advanced_genomics_health() -> Dict[str, Any]:
    """Health check para genómica avanzada"""
    svc = get_service()
    return {
        "service": "AdvancedGenomics",
        "status": "operational",
        "simulation_mode": True,
        "analyses_available": 5,
        "timestamp": datetime.utcnow().isoformat(),
        "service_info": svc.get_service_info(),
    }


@router.get("/supported-analyses")
async def get_supported_analyses() -> Dict[str, Any]:
    """
    Obtiene tipos de análisis genómicos soportados
    """
    service = get_service()
    return await service.get_supported_analyses()


@router.post("/variant-calling/deepvariant")
async def call_variants_deepvariant(req: VariantCallingRequest) -> Dict[str, Any]:
    """
    Ejecuta llamada de variantes con DeepVariant
    """
    service = get_service()
    
    # Convertir request a formato interno
    sample_info = {
        'sample_id': req.sample_info.sample_id,
        'file_path': req.sample_info.file_path,
        'coverage': req.sample_info.coverage,
        'sequencing_platform': req.sample_info.sequencing_platform,
        'library_type': req.sample_info.library_type,
        'reference_genome': req.reference_genome,
        'quality_threshold': req.quality_threshold
    }
    
    return await service.call_variants_deepvariant(sample_info, req.analysis_type)


@router.post("/cancer-analysis")
async def analyze_cancer_mutations(req: CancerAnalysisRequest) -> Dict[str, Any]:
    """
    Ejecuta análisis de mutaciones somáticas en cáncer
    """
    service = get_service()
    
    # Convertir tumor sample
    tumor_sample = {
        'sample_id': req.tumor_sample.sample_id,
        'file_path': req.tumor_sample.file_path,
        'coverage': req.tumor_sample.coverage,
        'sequencing_platform': req.tumor_sample.sequencing_platform,
        'library_type': req.tumor_sample.library_type,
        'cancer_type': req.cancer_type,
        'include_signatures': req.include_signatures
    }
    
    # Convertir normal sample si existe
    normal_sample = None
    if req.normal_sample:
        normal_sample = {
            'sample_id': req.normal_sample.sample_id,
            'file_path': req.normal_sample.file_path,
            'coverage': req.normal_sample.coverage,
            'sequencing_platform': req.normal_sample.sequencing_platform,
            'library_type': req.normal_sample.library_type
        }
    
    return await service.analyze_cancer_mutations(tumor_sample, normal_sample)


@router.post("/pharmacogenomics")
async def analyze_pharmacogenomics(req: PharmacogenomicsRequest) -> Dict[str, Any]:
    """
    Ejecuta análisis farmacogenómico para medicina personalizada
    """
    service = get_service()
    
    # Convertir request a formato interno
    sample_info = {
        'sample_id': req.sample_info.sample_id,
        'file_path': req.sample_info.file_path,
        'coverage': req.sample_info.coverage,
        'sequencing_platform': req.sample_info.sequencing_platform,
        'library_type': req.sample_info.library_type,
        'include_interactions': req.include_interactions
    }
    
    return await service.pharmacogenomics_analysis(sample_info, req.drug_list)


@router.post("/structural-variants")
async def analyze_structural_variants(req: StructuralVariantRequest) -> Dict[str, Any]:
    """
    Ejecuta análisis de variantes estructurales
    """
    service = get_service()
    
    # Convertir request a formato interno
    sample_info = {
        'sample_id': req.sample_info.sample_id,
        'file_path': req.sample_info.file_path,
        'coverage': req.sample_info.coverage,
        'sequencing_platform': req.sample_info.sequencing_platform,
        'library_type': req.sample_info.library_type,
        'min_sv_size': req.min_sv_size,
        'include_repeats': req.include_repeats
    }
    
    return await service.structural_variant_analysis(sample_info)


@router.get("/analysis-history")
async def get_analysis_history(limit: int = Query(20, ge=1, le=100)) -> Dict[str, Any]:
    """
    Obtiene historial de análisis genómicos
    """
    service = get_service()
    return await service.get_analysis_history(limit)


# Endpoints específicos simplificados
@router.post("/quick/wgs-analysis")
async def quick_wgs_analysis(sample_id: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Análisis WGS rápido (shortcut)
    """
    service = get_service()
    
    sample_info = {
        'sample_id': sample_id,
        'file_path': file_path,
        'library_type': 'wgs'
    }
    
    return await service.call_variants_deepvariant(sample_info, 'wgs')


@router.post("/quick/wes-analysis")
async def quick_wes_analysis(sample_id: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Análisis WES rápido (shortcut)
    """
    service = get_service()
    
    sample_info = {
        'sample_id': sample_id,
        'file_path': file_path,
        'library_type': 'wes'
    }
    
    return await service.call_variants_deepvariant(sample_info, 'wes')


@router.post("/quick/cancer-analysis")
async def quick_cancer_analysis(tumor_sample_id: str, normal_sample_id: Optional[str] = None,
                               cancer_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Análisis de cáncer rápido (shortcut)
    """
    service = get_service()
    
    tumor_sample = {
        'sample_id': tumor_sample_id,
        'cancer_type': cancer_type
    }
    
    normal_sample = None
    if normal_sample_id:
        normal_sample = {
            'sample_id': normal_sample_id
        }
    
    return await service.analyze_cancer_mutations(tumor_sample, normal_sample)


@router.post("/quick/pgx-analysis")
async def quick_pgx_analysis(sample_id: str, drugs: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Análisis farmacogenómico rápido (shortcut)
    """
    service = get_service()
    
    sample_info = {
        'sample_id': sample_id
    }
    
    return await service.pharmacogenomics_analysis(sample_info, drugs)
