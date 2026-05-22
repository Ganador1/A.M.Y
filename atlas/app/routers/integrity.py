"""
Router de Integridad y Riesgo - AXIOM Meta 4.1
===========================================

Módulo especializado para gestión integral de integridad de artefactos científicos
y evaluación de riesgos en el ecosistema AXIOM. Proporciona capacidades avanzadas
de registro, verificación y trazabilidad de datos científicos con soporte opcional
para anclaje en blockchain.

Capacidades Principales
----------------------
- **Registro de Artefactos**: Almacenamiento seguro con hashing criptográfico
- **Verificación de Integridad**: Validación de autenticidad y consistencia
- **Trazabilidad (Lineage)**: Seguimiento de dependencias y relaciones padre-hijo
- **Registro de Servicios**: Catálogo dinámico de servicios disponibles
- **Evaluación de Riesgos**: Análisis automatizado de riesgos por dominio
- **Políticas de Riesgo**: Configuración flexible de umbrales y niveles
- **Estadísticas de Cache**: Monitoreo del rendimiento del adaptador de herramientas
- **Persistencia de Validación**: Snapshots históricos de matrices de validación
- **Reportes Integrales**: Métricas comprehensivas de salud del sistema

Endpoints Disponibles
--------------------
**Artefactos:**
- `POST /api/integrity/artifacts/register` - Registrar nuevo artefacto
- `GET /api/integrity/artifacts/{id}/verify` - Verificar integridad
- `GET /api/integrity/artifacts` - Listar todos los artefactos
- `GET /api/integrity/artifacts/{id}/lineage` - Obtener linaje completo
- `POST /api/integrity/artifacts/link` - Vincular artefactos padre-hijo

**Servicios:**
- `GET /api/integrity/services` - Listar servicios registrados

**Evaluación de Riesgos:**
- `POST /api/integrity/risk/assess` - Evaluar riesgo de operación
- `GET /api/integrity/risk/policy` - Obtener política de riesgo actual
- `PUT /api/integrity/risk/policy` - Actualizar configuración de riesgo

**Monitoreo y Estadísticas:**
- `GET /api/integrity/cache-stats` - Estadísticas del cache de herramientas
- `GET /api/integrity/validation-snapshots` - Snapshots de validación histórica
- `GET /api/integrity/validation-trends` - Análisis de tendencias
- `POST /api/integrity/validation-snapshot` - Registrar snapshot manual
- `GET /api/integrity/integrity-report` - Reporte integral de integridad

Dependencias
-----------
- **integrity_core**: Núcleo de gestión de integridad y hashing
- **service_registry**: Registro dinámico de servicios del sistema
- **risk_policy**: Almacén de políticas de evaluación de riesgos
- **risk_assessment**: Módulo de evaluación de riesgos (opcional)
- **tool_adapter_cache**: Cache del adaptador de herramientas
- **validation_matrix_persistence**: Persistencia de matrices de validación
- **cross_validation_matrix**: Matriz de validación cruzada

Uso y Ejemplos
--------------
**Registro de artefacto básico:**
```python
response = await client.post("/api/integrity/artifacts/register", json={
    "artifact_type": "experiment_result",
    "data": {"temperature": 25.5, "pressure": 1013.25},
    "metadata": {"experiment_id": "exp_001", "timestamp": "2024-01-15T10:30:00Z"}
})
```

**Verificación de integridad:**
```python
response = await client.get("/api/integrity/artifacts/123e4567-e89b-12d3-a456-426614174000/verify")
# Retorna estado de integridad y hashes
```

**Evaluación de riesgo:**
```python
response = await client.post("/api/integrity/risk/assess", json={
    "domain": "genomics",
    "description": "Análisis de secuencias CRISPR",
    "declared_intent": "research",
    "data_sensitivity": "confidential",
    "justification": "Proyecto aprobado IRB-2024-001"
})
```

Notas de Seguridad
-----------------
- Todos los artefactos se almacenan con hashes SHA-256 para integridad
- Soporte opcional para anclaje en blockchain mediante integración externa
- Validación UUID estricta para todos los identificadores
- Políticas de riesgo configurables con niveles de firma digital
- Manejo centralizado de excepciones para prevenir fugas de información
- Rate limiting aplicado globalmente en main.py

Consideraciones de Rendimiento
-----------------------------
- Los snapshots de validación se almacenan con límite configurable
- Cache de herramientas compartido entre adaptadores para optimización
- Análisis de tendencias limitado a últimas 24 horas por defecto
- Reportes integrales incluyen métricas de salud del sistema en tiempo real
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
import uuid

from app.integrity_core import integrity_core
from app.infrastructure.service_registry import list_services
from app.risk_policy import risk_policy_store
from app.exceptions.domain.biology import BiologyError
try:  # opcional
    from app.compliance.risk_assessment import risk_assessment
except BiologyError:  # pragma: no cover
    risk_assessment = None  # type: ignore

router = APIRouter(prefix="/api/integrity", tags=["integrity", "risk"])  # se incluye directamente en main

# ---- Modelos ----
class ArtifactRegisterRequest(BaseModel):
    artifact_type: str = Field("result", description="Tipo lógico del artefacto")
    data: Any = Field(..., description="Payload serializable o representable")
    metadata: Dict[str, Any] | None = Field(default=None)
    blockchain: bool = Field(False, description="Anchor async en blockchain")
    parent_id: Optional[str] = Field(None, description="Para lineage opcional")

class ArtifactRegisterResponse(BaseModel):
    success: bool
    artifact_id: str
    data_hash: str
    metadata_hash: str
    blockchain_anchoring: bool = False

class ArtifactVerifyResponse(BaseModel):
    success: bool
    status: Dict[str, Any]

class ArtifactListResponse(BaseModel):
    success: bool
    items: List[Dict[str, Any]]

class LineageResponse(BaseModel):
    success: bool
    lineage: Dict[str, Any]

class LinkChildRequest(BaseModel):
    parent_id: str
    child_id: str

class ServiceListResponse(BaseModel):
    success: bool
    services: List[Dict[str, Any]]

class RiskAssessRequest(BaseModel):
    domain: str
    description: str
    declared_intent: str = "research"
    data_sensitivity: str = "none"
    justification: Optional[str] = None
    justification_signature: Optional[str] = None
    resources: Dict[str, Any] | None = None

class RiskAssessResponse(BaseModel):
    success: bool
    risk_level: str
    blocked: bool
    reasons: List[str]

class RiskPolicyResponse(BaseModel):
    success: bool
    policy: Dict[str, Any]

class RiskPolicyUpdateRequest(BaseModel):
    signature_levels: Optional[List[str]] = None
    thresholds: Optional[Dict[str, int]] = None

# ---- Helpers ----
def _validate_uuid(id_str: str) -> None:
    try:
        uuid.UUID(id_str)
    except BiologyError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

# ---- Endpoints ----
@router.post("/artifacts/register", response_model=ArtifactRegisterResponse)
async def register_artifact(req: ArtifactRegisterRequest):
    try:
        meta = req.metadata or {}
        if req.parent_id:
            meta["parent_id"] = req.parent_id
        record = integrity_core.register_artifact(
            data=req.data,
            artifact_type=req.artifact_type,
            metadata=meta,
            blockchain=req.blockchain,
        )
        return ArtifactRegisterResponse(
            success=True,
            artifact_id=record.artifact_id,
            data_hash=record.data_hash,
            metadata_hash=record.metadata_hash,
            blockchain_anchoring=req.blockchain,
        )
    except HTTPException:
        raise
    except BiologyError as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artifacts/{artifact_id}/verify", response_model=ArtifactVerifyResponse)
async def verify_artifact(artifact_id: str):
    _validate_uuid(artifact_id)
    status = await integrity_core.verify_artifact(artifact_id)
    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Artifact not found")
    return ArtifactVerifyResponse(success=True, status=status)

@router.get("/artifacts", response_model=ArtifactListResponse)
async def list_artifacts():
    return ArtifactListResponse(success=True, items=integrity_core.list_artifacts())

@router.get("/artifacts/{artifact_id}/lineage", response_model=LineageResponse)
async def get_lineage(artifact_id: str):
    _validate_uuid(artifact_id)
    lineage = integrity_core.get_lineage(artifact_id)
    if lineage.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Artifact not found")
    return LineageResponse(success=True, lineage=lineage)

@router.post("/artifacts/link", response_model=LineageResponse)
async def link_child(req: LinkChildRequest):
    _validate_uuid(req.parent_id)
    _validate_uuid(req.child_id)
    if not integrity_core.link_child(req.parent_id, req.child_id):
        raise HTTPException(status_code=400, detail="Link failed (ids exist? already linked? cycle?)")
    return LineageResponse(success=True, lineage=integrity_core.get_lineage(req.parent_id))

@router.get("/services", response_model=ServiceListResponse)
async def services():
    return ServiceListResponse(success=True, services=list_services())

@router.post("/risk/assess", response_model=RiskAssessResponse)
async def assess_risk(req: RiskAssessRequest):
    if not risk_assessment:
        raise HTTPException(status_code=503, detail="Risk assessment module not available")
    rr = risk_assessment.assess(
        domain=req.domain,
        description=req.description,
        declared_intent=req.declared_intent,
        data_sensitivity=req.data_sensitivity,
        justification=req.justification,
        justification_signature=req.justification_signature,
        resources=req.resources or {},
    )
    return RiskAssessResponse(success=True, risk_level=rr.level, blocked=rr.blocked, reasons=rr.reasons)

@router.get("/risk/policy", response_model=RiskPolicyResponse)
async def get_risk_policy():
    return RiskPolicyResponse(success=True, policy=risk_policy_store.get())

@router.put("/risk/policy", response_model=RiskPolicyResponse)
async def update_risk_policy(req: RiskPolicyUpdateRequest):
    patch: Dict[str, Any] = {}
    if req.signature_levels is not None:
        patch["signature_levels"] = req.signature_levels
    if req.thresholds is not None:
        patch["thresholds"] = req.thresholds
    updated = risk_policy_store.update(patch)
    return RiskPolicyResponse(success=True, policy=updated)


# ---- Tool Adapter Cache Stats ----
class CacheStatsResponse(BaseModel):
    success: bool = True
    cache_stats: Dict[str, Any]

@router.get("/cache-stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """Get tool adapter cache statistics"""
    try:
        from app.adapters.tool_adapter import get_tool_registry
        registry = get_tool_registry()
        if not registry.list():
            return CacheStatsResponse(cache_stats={"cache_enabled": False})
        
        # Get first adapter to check cache stats (they share the global cache)
        from app.adapters.tool_adapter_cache import tool_adapter_cache
        if tool_adapter_cache:
            stats = tool_adapter_cache.stats()
            return CacheStatsResponse(cache_stats=stats)
        
        return CacheStatsResponse(cache_stats={"cache_enabled": False})
    except BiologyError as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Cache stats error: {str(e)}")


# ---- Validation Matrix Persistence ----
class ValidationSnapshotsResponse(BaseModel):
    success: bool = True
    snapshots: List[Dict[str, Any]]
    hours_analyzed: int

class ValidationTrendsResponse(BaseModel):
    success: bool = True
    trend_analysis: Dict[str, Any]

@router.get("/validation-snapshots", response_model=ValidationSnapshotsResponse)
async def get_validation_snapshots(hours_back: int = 24, limit: int = 100):
    """Get recent validation matrix snapshots"""
    try:
        from app.validation_matrix_persistence import get_validation_persistence
        persistence = get_validation_persistence()
        snapshots = persistence.get_snapshots(hours_back, limit)
        
        return ValidationSnapshotsResponse(
            snapshots=[s.to_dict() for s in snapshots],
            hours_analyzed=hours_back
        )
    except BiologyError as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Snapshots error: {str(e)}")

@router.get("/validation-trends", response_model=ValidationTrendsResponse)
async def get_validation_trends(hours_back: int = 24):
    """Get validation matrix trend analysis"""
    try:
        from app.validation_matrix_persistence import get_validation_persistence
        persistence = get_validation_persistence()
        trends = persistence.get_trend_analysis(hours_back)
        
        return ValidationTrendsResponse(trend_analysis=trends)
    except BiologyError as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Trends error: {str(e)}")

@router.post("/validation-snapshot")
async def record_validation_snapshot():
    """Manually record a validation matrix snapshot"""
    try:
        from app.validation_matrix_persistence import get_validation_recorder
        recorder = get_validation_recorder()
        success = recorder.record_current_state({"manual_trigger": True})
        
        return {"success": success, "recorded": success}
    except BiologyError as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Record error: {str(e)}")


# ---- Comprehensive Integrity Reports ----
class IntegrityReportResponse(BaseModel):
    success: bool = True
    report: Dict[str, Any]
    generated_at: str

@router.get("/integrity-report", response_model=IntegrityReportResponse)
async def get_comprehensive_integrity_report():
    """Generate comprehensive integrity report with all metrics"""
    try:
        from datetime import datetime
        from app.validation_matrix_persistence import get_validation_persistence
        from app.adapters.tool_adapter_cache import tool_adapter_cache
        from app.cross_validation_matrix import cross_validation_matrix
        
        # Core metrics
        artifacts = integrity_core.list_artifacts()
        services = list_services()
        
        # Validation matrix current state
        validation_result = cross_validation_matrix.build_matrix()
        
        # Recent snapshots and trends
        persistence = get_validation_persistence()
        recent_snapshots = persistence.get_snapshots(hours_back=24, limit=50)
        trends = persistence.get_trend_analysis(hours_back=24)
        
        # Cache statistics
        cache_stats = tool_adapter_cache.stats() if tool_adapter_cache else {"cache_enabled": False}
        
        # Integrity health metrics
        valid_artifacts = len([a for a in artifacts if a.get("integrity_status") == "valid"])
        total_artifacts = len(artifacts)
        integrity_health = (valid_artifacts / total_artifacts * 100) if total_artifacts > 0 else 100
        
        # Lineage analysis
        artifacts_with_lineage = len([a for a in artifacts if a.get("parent_id") or a.get("children")])
        lineage_coverage = (artifacts_with_lineage / total_artifacts * 100) if total_artifacts > 0 else 0
        
        # Risk assessment summary
        risk_flags = validation_result.get("flags", [])
        risk_level = "LOW"
        if any("integrity" in flag.lower() for flag in risk_flags):
            risk_level = "HIGH"
        elif len(risk_flags) > 2:
            risk_level = "MEDIUM"
        
        # Service diversity
        service_types = set()
        for service in services:
            # Extract service type from name (services are dicts with 'name' field)
            service_name = service.get("name", "")
            if "_service" in service_name:
                service_types.add(service_name.replace("_service", ""))
        
        report = {
            "summary": {
                "total_artifacts": total_artifacts,
                "valid_artifacts": valid_artifacts,
                "integrity_health_percent": round(integrity_health, 2),
                "total_services": len(services),
                "service_types": len(service_types),
                "validation_score": validation_result["score"],
                "risk_level": risk_level,
                "lineage_coverage_percent": round(lineage_coverage, 2),
            },
            "artifacts": {
                "total": total_artifacts,
                "valid": valid_artifacts,
                "invalid": total_artifacts - valid_artifacts,
                "with_lineage": artifacts_with_lineage,
                "sample": artifacts[:5],  # First 5 for preview
            },
            "services": {
                "total": len(services),
                "types": list(service_types),
                "active": services,
            },
            "validation": {
                "current_score": validation_result["score"],
                "flags": risk_flags,
                "artifact_count": validation_result["artifact_count"],
                "service_count": validation_result["service_count"],
            },
            "trends": {
                "analysis_available": trends["trend"] == "analyzed",
                "snapshots_count": len(recent_snapshots),
                **trends,
            },
            "cache": {
                "enabled": cache_stats.get("cache_enabled", False),
                **cache_stats,
            },
            "health_indicators": {
                "integrity_ok": integrity_health >= 95,
                "service_diversity_ok": len(service_types) >= 3,
                "validation_score_ok": validation_result["score"] >= 70,
                "risk_level_ok": risk_level in {"LOW", "MEDIUM"},
                "lineage_coverage_ok": lineage_coverage >= 50,
            },
        }
        
        return IntegrityReportResponse(
            report=report,
            generated_at=f"{datetime.utcnow().isoformat()}Z"
        )
        
    except BiologyError as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")
