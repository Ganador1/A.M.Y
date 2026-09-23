"""
Router de Genómica - Análisis Genómico y Validación de Variantes

Módulo FastAPI seguro para análisis genómico y validación de llamadas de variantes.
Proporciona validación de entorno y capacidades de ejecución en seco para pipelines
genómicos sin ejecutar flujos de trabajo computacionales reales.

Capacidades principales:
- Validación de entorno: verificación de herramientas de análisis genómico
- Validación de entrada DeepVariant: comprobación de archivos y parámetros
- Simulación de ejecución DeepVariant: simulación sin ejecución real
- Validación de entrada MuTect2: verificación de archivos de variantes somáticas
- Simulación de ejecución MuTect2: simulación sin procesamiento real
- Seguridad integral: todas las operaciones son solo de validación

Catálogo de Endpoints:
- GET /api/genomics/env: Validación de entorno DeepVariant y dependencias
- POST /api/genomics/deepvariant/validate: Validación de archivos de entrada DeepVariant
- POST /api/genomics/deepvariant/dry-run: Simulación de ejecución DeepVariant
- POST /api/genomics/mutect2/validate: Validación de archivos de entrada MuTect2
- POST /api/genomics/mutect2/dry-run: Simulación de ejecución MuTect2

Dependencias:
- GenomicsService: Servicio central de análisis y validación genómica
- DeepVariant: Llamador de variantes de aprendizaje profundo de Google (solo validación)
- MuTect2: Llamador de variantes somáticas de GATK (solo validación)
- pydantic: Validación de requests/responses

Uso del Servicio:
    Todos los endpoints realizan validación y simulación sin ejecución real.
    Útil para verificaciones previas al vuelo, validación de entorno y
    pruebas de pipeline antes del despliegue a flujos de trabajo de análisis
    genómico en producción.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.domains.biology.services.genomics_service import GenomicsService


router = APIRouter(prefix="/api/genomics", tags=["genomics"])

_svc: Optional[GenomicsService] = None


def get_service() -> GenomicsService:
    global _svc
    if _svc is None:
        _svc = GenomicsService()
    return _svc


@router.get("/env")
def environment_check() -> Dict[str, Any]:
    svc = get_service()
    return svc.validate_deepvariant_environment()


class DVValidateRequest(BaseModel):
    bam_file: str = Field(..., description="Ruta al archivo BAM")
    reference_fasta: str = Field(..., description="Ruta al FASTA de referencia")
    output_dir: Optional[str] = Field(None, description="Directorio de salida")


@router.post("/deepvariant/validate")
def validate_inputs(req: DVValidateRequest) -> Dict[str, Any]:
    svc = get_service()
    return svc.validate_inputs(req.bam_file, req.reference_fasta, req.output_dir)


@router.post("/deepvariant/dry-run")
def deepvariant_dry_run(req: DVValidateRequest) -> Dict[str, Any]:
    svc = get_service()
    return svc.dry_run_deepvariant(req.bam_file, req.reference_fasta, req.output_dir)


class Mutect2ValidateRequest(BaseModel):
    tumor_bam: str
    normal_bam: str
    reference_fasta: str
    output_dir: Optional[str] = None


@router.post("/mutect2/validate")
def mutect2_validate(req: Mutect2ValidateRequest) -> Dict[str, Any]:
    svc = get_service()
    return svc.validate_mutect2_inputs(req.tumor_bam, req.normal_bam, req.reference_fasta, req.output_dir)


@router.post("/mutect2/dry-run")
def mutect2_dry_run(req: Mutect2ValidateRequest) -> Dict[str, Any]:
    svc = get_service()
    return svc.dry_run_mutect2(req.tumor_bam, req.normal_bam, req.reference_fasta, req.output_dir)


