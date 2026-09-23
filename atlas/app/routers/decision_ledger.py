"""
Decision Ledger Router

Router FastAPI para seguimiento de decisiones y logging de auditoría.
Proporciona endpoints REST API para registro de procesos de toma de decisiones con justificación,
seguimiento de resultados de decisiones y métricas, auditoría de historial de decisiones por tipo,
analytics de decisiones y reportes, seguimiento de cumplimiento y gobernanza.

Capacidades principales:
- Registro de procesos de toma de decisiones con justificación detallada
- Seguimiento de resultados de decisiones y métricas de rendimiento
- Auditoría comprehensiva de historial de decisiones por tipo y categoría
- Analytics de decisiones con reportes y visualizaciones
- Seguimiento de cumplimiento normativo y gobernanza organizacional
- Búsqueda y filtrado avanzado de decisiones por criterios múltiples
- Exportación de datos de decisiones para análisis externo
- Integración con sistemas de monitoreo y alertas

Endpoints disponibles:
- POST /log: Registrar nueva decisión con justificación y métricas
- GET /list: Listar entradas de decisiones con filtrado opcional por tipo
- GET /analytics: Obtener analytics y métricas de decisiones
- GET /audit/{decision_type}: Obtener historial de auditoría por tipo de decisión
- POST /export: Exportar datos de decisiones en formato estructurado

Dependencias:
- DecisionLedgerService: Servicio principal de registro de decisiones
- DecisionLogRequest: Solicitud de registro de decisión
- DecisionAnalyticsRequest: Solicitud de analytics de decisiones

Uso típico:
    from app.routers.decision_ledger import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles bajo el prefijo /decision-ledger
"""

from fastapi import APIRouter
from typing import List, Optional
from app.services.decision_ledger_service import decision_ledger_service

router = APIRouter(prefix="/decision-ledger", tags=["decision-ledger"])

@router.post("/log")
def log(decision_type: str, subject_id: Optional[str], options: List[str], chosen: str, rationale: str):
    return decision_ledger_service.log_decision(decision_type=decision_type, subject_id=subject_id, options=options, chosen=chosen, rationale=rationale, metrics=None)

@router.get("/list")
def list_entries(decision_type: Optional[str] = None):
    return {"entries": decision_ledger_service.list_decisions(decision_type)}
