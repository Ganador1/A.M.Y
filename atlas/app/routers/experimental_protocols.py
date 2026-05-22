"""
Router de Protocolos Experimentales - Gestión y Ejecución de Protocolos AXIOM META 4

Módulo FastAPI para gestión integral de protocolos experimentales en la plataforma AXIOM META 4.
Proporciona endpoints REST API para crear, convertir, ejecutar y optimizar protocolos científicos,
facilitando la automatización de procedimientos de laboratorio y análisis de datos.

Capacidades principales:
- Gestión completa de protocolos: creación, validación y almacenamiento estructurado
- Conversión de formatos: transformación entre diferentes representaciones de protocolos
- Ejecución automatizada: procesamiento de protocolos con seguimiento de estado
- Parsing de lenguaje natural: conversión de texto humano a protocolos ejecutables
- Optimización inteligente: mejora automática de protocolos basada en objetivos
- Monitoreo de ejecución: seguimiento en tiempo real del progreso experimental
- Validación de protocolos: verificación de integridad y completitud

Catálogo de Endpoints:
- GET /api/v1/protocols/list: Listado de protocolos con filtros opcionales
- GET /api/v1/protocols/{protocol_id}: Consulta detallada de protocolo específico
- POST /api/v1/protocols/create: Creación de nuevos protocolos experimentales
- POST /api/v1/protocols/validate: Validación de protocolos existentes
- POST /api/v1/protocols/execute: Ejecución de protocolos con operador opcional
- GET /api/v1/protocols/execution/{execution_id}: Estado de ejecución en tiempo real
- POST /api/v1/protocols/convert: Conversión de protocolos a diferentes formatos
- POST /api/v1/protocols/parse-human: Parsing de texto humano a protocolos ejecutables
- POST /api/v1/protocols/optimize: Optimización automática de protocolos
- GET /api/v1/protocols/health: Health check del servicio de protocolos

Dependencias:
- ExperimentalProtocols: Servicio central de gestión de protocolos
- logging_config: Configuración de logging para trazabilidad
- require_scopes: Sistema de autorización por scopes de seguridad
- Pydantic BaseModel: Modelos de validación para requests/responses
- FastAPI Depends: Sistema de inyección de dependencias con autenticación

Uso del Servicio:
    El router permite gestión completa del ciclo de vida de protocolos experimentales.
    Soporta conversión automática de instrucciones escritas en lenguaje natural
    a protocolos ejecutables, optimización basada en criterios específicos y
    ejecución supervisada con monitoreo continuo del progreso.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.bootstrap_logging import logger
from app.security import require_scopes
from app.services.experimental_protocols import ExperimentalProtocols

router = APIRouter(
    prefix="/api/v1/protocols",
    tags=["Experimental Protocols"],
    dependencies=[Depends(require_scopes(["lab-equipment"]))],
)

_service = ExperimentalProtocols()


class ProtocolFilter(BaseModel):
    protocol_type: Optional[str] = None
    status: Optional[str] = None


class CreateProtocolRequest(BaseModel):
    protocol_data: Dict[str, Any]


class ConvertProtocolRequest(BaseModel):
    protocol_id: str
    target_format: str = Field(default="json")


class ExecuteProtocolRequest(BaseModel):
    protocol_id: str
    operator: Optional[str] = "system"


class HumanProtocolParseRequest(BaseModel):
    text: str
    name: Optional[str] = "Human Parsed Protocol"
    author: Optional[str] = "Unknown"
    protocol_type: Optional[str] = "analysis"


class OptimizeProtocolRequest(BaseModel):
    protocol_id: str
    objective: str = Field(default="minimize_time")
    constraints: Dict[str, Any] = Field(default_factory=dict)


@router.get("/list", summary="Listar protocolos")
async def list_protocols(protocol_type: Optional[str] = None, status: Optional[str] = None):
    result = await _service.list_protocols({"protocol_type": protocol_type, "status": status})
    return result


@router.get("/{protocol_id}", summary="Obtener protocolo")
async def get_protocol(protocol_id: str):
    result = await _service.get_protocol({"protocol_id": protocol_id})
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@router.post("/create", summary="Crear protocolo")
async def create_protocol(req: CreateProtocolRequest):
    result = await _service.create_protocol(req.dict())
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/validate", summary="Validar protocolo")
async def validate_protocol(protocol_id: str):
    result = await _service.validate_protocol({"protocol_id": protocol_id})
    return result


@router.post("/execute", summary="Ejecutar protocolo")
async def execute_protocol(req: ExecuteProtocolRequest):
    result = await _service.execute_protocol(req.dict())
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/execution/{execution_id}", summary="Estado de ejecución")
async def get_execution(execution_id: str):
    result = await _service.get_execution_status({"execution_id": execution_id})
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@router.post("/convert", summary="Convertir protocolo a otro formato")
async def convert_protocol(req: ConvertProtocolRequest):
    result = await _service.convert_protocol(req.dict())
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/parse-human", summary="Parsear texto humano a protocolo ejecutable")
async def parse_human(req: HumanProtocolParseRequest):
    result = await _service.parse_human_protocol(req.dict())
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/optimize", summary="Optimizar protocolo")
async def optimize(req: OptimizeProtocolRequest):
    result = await _service.optimize_protocol(req.dict())
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/health", summary="Health Check")
async def health():
    return {"success": True, "service": "ExperimentalProtocols", "status": "healthy"}


