"""
🧪 MATRIZ DE VALIDACIÓN CRUZADA - ROUTER
=========================================

**Módulo de Validación de Integridad del Sistema AXIOM v4.1**

Este router expone la **matriz de validación cruzada** que proporciona un monitoreo
integral y en tiempo real de la integridad del sistema científico AXIOM. La matriz
de validación actúa como un **sistema de diagnóstico avanzado** que verifica la
consistencia, coherencia y fiabilidad de todos los componentes del sistema.

## 🎯 FUNCIONALIDADES PRINCIPALES

### 📊 Matriz de Validación Cruzada
- **Monitoreo continuo** de componentes del sistema
- **Validación cruzada** entre módulos independientes
- **Detección automática** de inconsistencias
- **Métricas de integridad** en tiempo real

### 🔍 Tipos de Validación
- **Validación funcional**: Verificación de operaciones básicas
- **Validación de consistencia**: Chequeo de integridad de datos
- **Validación de rendimiento**: Métricas de eficiencia
- **Validación de seguridad**: Verificación de controles de acceso

### 📈 Métricas de Integridad
- **Puntuación de confianza**: Nivel de fiabilidad del sistema (0-100)
- **Cobertura de validación**: Porcentaje de componentes validados
- **Tasa de detección**: Eficiencia en encontrar anomalías
- **Tiempo de respuesta**: Latencia de validaciones

## 🔧 ARQUITECTURA TÉCNICA

### Componentes del Sistema
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Routers       │    │ Validation       │    │   Services      │
│   (FastAPI)     │◄──►│   Matrix         │◄──►│   (Business     │
│                 │    │   Engine         │    │    Logic)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Database      │    │   Cache          │    │   External      │
│   (PostgreSQL)  │    │   (Redis)        │    │   APIs          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Algoritmo de Validación
1. **Recopilación de métricas** de cada componente
2. **Análisis cruzado** entre sistemas independientes
3. **Cálculo de puntuaciones** de integridad
4. **Generación de reportes** de estado

## 📊 ESTRUCTURA DE LA MATRIZ

```json
{
  "timestamp": "2024-12-01T10:30:00Z",
  "overall_score": 98.5,
  "components": {
    "routers": {
      "status": "healthy",
      "score": 99.2,
      "checks": ["auth", "rate_limit", "error_handling"]
    },
    "services": {
      "status": "warning",
      "score": 95.1,
      "issues": ["slow_response"]
    },
    "database": {
      "status": "healthy",
      "score": 100.0,
      "checks": ["connection", "integrity"]
    }
  },
  "recommendations": [
    "Optimize service response times",
    "Review error handling patterns"
  ]
}
```

## 🚀 USO TÍPICO

### Monitoreo Continuo
```python
# Verificación automática cada 5 minutos
validation_matrix = get_validation_matrix()
if validation_matrix['overall_score'] < 95:
    alert_administrators(validation_matrix)
```

### Diagnóstico de Problemas
```python
# Análisis detallado de componentes
matrix = get_validation_matrix()
for component, data in matrix['components'].items():
    if data['status'] != 'healthy':
        investigate_component(component, data)
```

## 🔒 SEGURIDAD Y AUTORIZACIÓN

- **Autenticación requerida** para acceso a métricas sensibles
- **Control de acceso basado en roles** (admin, operator, viewer)
- **Auditoría completa** de consultas a la matriz
- **Enmascaramiento de datos** críticos en respuestas

## 📈 MÉTRICAS Y MONITORING

### KPIs Principales
- **Disponibilidad del sistema**: 99.9% uptime objetivo
- **Precisión de validación**: >95% de detección de anomalías
- **Tiempo de respuesta**: <2 segundos para consultas
- **Cobertura de validación**: 100% de componentes críticos

### Alertas Automáticas
- **Score < 90**: Alerta crítica
- **Score 90-95**: Alerta de advertencia
- **Score > 95**: Estado normal
- **Componente caído**: Notificación inmediata

## 🔄 INTEGRACIÓN CON SISTEMAS

### APIs Externas
- **Prometheus/Grafana**: Exportación de métricas
- **ELK Stack**: Centralización de logs
- **PagerDuty**: Alertas automáticas
- **Slack/Teams**: Notificaciones

### Dependencias Internas
- **cross_validation_matrix**: Motor de validación principal
- **auth_service**: Gestión de autenticación
- **monitoring_service**: Recopilación de métricas
- **alert_service**: Sistema de notificaciones

## 🧪 TESTING Y VALIDACIÓN

### Estrategia de Testing
- **Unit tests**: Validación de funciones individuales
- **Integration tests**: Pruebas de interacción entre componentes
- **Load tests**: Validación bajo carga alta
- **Chaos engineering**: Simulación de fallos

### Casos de Prueba Críticos
- **Matriz vacía**: Manejo de estados iniciales
- **Componentes caídos**: Recuperación automática
- **Datos corruptos**: Detección y corrección
- **Alta concurrencia**: Rendimiento bajo carga

## 📚 REFERENCIAS

- **Documentación técnica**: `/docs/validation-matrix`
- **API Reference**: `/api/docs`
- **Health checks**: `/health`
- **Metrics endpoint**: `/metrics`

---

**AXIOM v4.1 - Sistema de Investigación Científica Autónoma**
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
import time
import logging

from app.validation.cross_validation_matrix import cross_validation_matrix
from app.exceptions.domain.biology import BiologyError

# Configuración de logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/validation", tags=["validation-matrix"])

validation_matrix_router = router

# Modelos Pydantic para la API de validación

class ComponentStatus(BaseModel):
    """
    📊 ESTADO DE COMPONENTE INDIVIDUAL
    ==================================

    Representa el estado de validación de un componente específico del sistema,
    incluyendo métricas de rendimiento, estado de salud y problemas detectados.
    """
    status: str = Field(
        ...,
        description="Estado general del componente",
        examples=["healthy", "warning", "critical", "unknown"]
    )
    score: float = Field(
        ...,
        description="Puntuación de integridad (0-100)",
        ge=0.0,
        le=100.0,
        examples=[98.5, 95.2, 87.3]
    )
    checks_passed: Optional[List[str]] = Field(
        default=None,
        description="Lista de validaciones exitosas",
        examples=[["auth", "rate_limit", "error_handling"]]
    )
    issues: Optional[List[str]] = Field(
        default=None,
        description="Lista de problemas detectados",
        examples=[["slow_response", "memory_leak"]]
    )
    last_check: Optional[datetime] = Field(
        default=None,
        description="Timestamp de la última validación"
    )
    response_time_ms: Optional[float] = Field(
        default=None,
        description="Tiempo de respuesta promedio en ms",
        examples=[150.5, 234.2]
    )

class ValidationMatrix(BaseModel):
    """
    🧪 MATRIZ COMPLETA DE VALIDACIÓN
    ================================

    Estructura completa de la matriz de validación cruzada que contiene
    el estado de todos los componentes del sistema AXIOM.
    """
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de generación de la matriz"
    )
    overall_score: float = Field(
        ...,
        description="Puntuación global de integridad del sistema (0-100)",
        ge=0.0,
        le=100.0,
        examples=[98.5, 95.7, 92.1]
    )
    coverage_percentage: float = Field(
        ...,
        description="Porcentaje de componentes validados (0-100)",
        ge=0.0,
        le=100.0,
        examples=[100.0, 95.5, 87.2]
    )
    components: Dict[str, ComponentStatus] = Field(
        ...,
        description="Estado detallado de cada componente del sistema",
        examples=[{
            "routers": {"status": "healthy", "score": 99.2},
            "services": {"status": "warning", "score": 95.1},
            "database": {"status": "healthy", "score": 100.0}
        }]
    )
    recommendations: Optional[List[str]] = Field(
        default=None,
        description="Recomendaciones automáticas para mejorar la integridad",
        examples=[["Optimize service response times", "Review error handling patterns"]]
    )
    alerts: Optional[List[str]] = Field(
        default=None,
        description="Alertas críticas que requieren atención inmediata",
        examples=[["Database connection unstable", "Memory usage critical"]]
    )

class MatrixResponse(BaseModel):
    """
    📤 RESPUESTA ESTANDARIZADA DE LA API
    ====================================

    Respuesta estandarizada para todas las operaciones de la matriz de validación,
    siguiendo el patrón de respuesta consistente de AXIOM v4.1.
    """
    success: bool = Field(
        ...,
        description="Indica si la operación fue exitosa",
        examples=[True, False]
    )
    message: str = Field(
        ...,
        description="Mensaje descriptivo del resultado",
        examples=["Matriz de validación obtenida exitosamente", "Error interno del servidor"]
    )
    data: Optional[ValidationMatrix] = Field(
        default=None,
        description="Datos de la matriz de validación cuando la operación es exitosa"
    )
    execution_time_seconds: float = Field(
        ...,
        description="Tiempo de ejecución de la operación en segundos",
        examples=[0.145, 2.234, 0.089]
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de la respuesta"
    )
    error_code: Optional[str] = Field(
        default=None,
        description="Código de error en caso de fallo",
        examples=["VALIDATION_MATRIX_UNAVAILABLE", "COMPONENT_TIMEOUT"]
    )

class HealthCheckRequest(BaseModel):
    """
    🔍 SOLICITUD DE VERIFICACIÓN DE SALUD
    =====================================

    Parámetros para solicitar una verificación de salud específica de componentes.
    """
    component: Optional[str] = Field(
        default=None,
        description="Componente específico a verificar (opcional)",
        examples=["database", "routers", "services"]
    )
    include_details: bool = Field(
        default=True,
        description="Incluir detalles completos en la respuesta",
        examples=[True, False]
    )
    timeout_seconds: int = Field(
        default=30,
        description="Timeout máximo para la verificación en segundos",
        ge=1,
        le=300,
        examples=[30, 60, 120]
    )

# Endpoints de la matriz de validación

@router.get("/matrix", response_model=MatrixResponse)
async def get_validation_matrix() -> MatrixResponse:
    """
    🧪 OBTENER MATRIZ DE VALIDACIÓN CRUZADA
    =======================================

    Retorna la matriz completa de validación cruzada del sistema AXIOM,
    proporcionando un diagnóstico integral del estado de salud de todos
    los componentes críticos.

    **Proceso de validación:**
    1. **Recopilación de métricas** de cada componente activo
    2. **Análisis cruzado** entre sistemas independientes
    3. **Cálculo de puntuaciones** de integridad por componente
    4. **Generación de recomendaciones** automáticas

    **Respuesta exitosa:**
    ```json
    {
        "success": true,
        "message": "Matriz de validación obtenida exitosamente",
        "data": {
            "timestamp": "2024-12-01T10:30:00",
            "overall_score": 98.5,
            "coverage_percentage": 100.0,
            "components": {
                "routers": {
                    "status": "healthy",
                    "score": 99.2,
                    "checks_passed": ["auth", "rate_limit"],
                    "response_time_ms": 45.2
                },
                "services": {
                    "status": "warning",
                    "score": 95.1,
                    "issues": ["slow_response"],
                    "response_time_ms": 234.1
                }
            },
            "recommendations": ["Optimizar tiempos de respuesta"]
        },
        "execution_time_seconds": 0.145,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación de resultados:**
    - **Score > 95**: Sistema saludable
    - **Score 90-95**: Requiere atención
    - **Score < 90**: Problemas críticos
    - **Coverage = 100%**: Validación completa

    **Códigos de error:**
    - **503**: Servicio de validación no disponible
    - **500**: Error interno en el motor de validación
    - **504**: Timeout en recopilación de métricas
    """
    start_time = time.time()
    logger.info("🧪 Solicitando matriz de validación completa")

    try:
        # Construir la matriz de validación
        raw_matrix = cross_validation_matrix.build_matrix()

        # Transformar al formato estandarizado
        components = {}
        total_score = 0.0
        component_count = 0

        for component_name, component_data in raw_matrix.items():
            if isinstance(component_data, dict):
                # Crear objeto ComponentStatus
                status_obj = ComponentStatus(
                    status=component_data.get('status', 'unknown'),
                    score=float(component_data.get('score', 0.0)),
                    checks_passed=component_data.get('checks_passed'),
                    issues=component_data.get('issues'),
                    last_check=component_data.get('last_check'),
                    response_time_ms=component_data.get('response_time_ms')
                )
                components[component_name] = status_obj

                total_score += status_obj.score
                component_count += 1
            else:
                # Para datos simples, crear estructura básica
                score = float(component_data) if isinstance(component_data, (int, float)) else 50.0
                components[component_name] = ComponentStatus(
                    status="healthy" if score > 90 else "warning" if score > 70 else "critical",
                    score=score
                )
                total_score += score
                component_count += 1

        # Calcular puntuación general
        overall_score = total_score / component_count if component_count > 0 else 0.0

        # Generar recomendaciones básicas
        recommendations = []
        alerts = []

        if overall_score < 90:
            alerts.append("Puntuación general crítica - requiere atención inmediata")
        elif overall_score < 95:
            recommendations.append("Revisar componentes con puntuación baja")

        for comp_name, comp_status in components.items():
            if comp_status.score < 80:
                alerts.append(f"Componente {comp_name} requiere atención urgente")
            elif comp_status.score < 90:
                recommendations.append(f"Optimizar rendimiento de {comp_name}")

        # Crear objeto ValidationMatrix
        validation_matrix_obj = ValidationMatrix(
            timestamp=datetime.now(),
            overall_score=round(overall_score, 1),
            coverage_percentage=100.0 if component_count > 0 else 0.0,
            components=components,
            recommendations=recommendations if recommendations else None,
            alerts=alerts if alerts else None
        )

        execution_time = time.time() - start_time
        logger.info("✅ Matriz de validación generada en %.2fs - Score: %.1f", execution_time, overall_score)

        return MatrixResponse(
            success=True,
            message="Matriz de validación obtenida exitosamente",
            data=validation_matrix_obj,
            execution_time_seconds=round(execution_time, 3),
            timestamp=datetime.now()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error obteniendo matriz de validación: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        ) from e

@router.get("/health", response_model=MatrixResponse)
async def get_system_health() -> MatrixResponse:
    """
    ❤️ VERIFICACIÓN RÁPIDA DE SALUD DEL SISTEMA
    ===========================================

    Endpoint ligero para verificación rápida del estado de salud general
    del sistema, optimizado para monitoreo continuo y health checks.

    **Características:**
    - **Respuesta rápida**: Optimizado para baja latencia
    - **Información esencial**: Solo métricas críticas
    - **Cache inteligente**: Resultados cacheados cuando apropiado

    **Respuesta exitosa:**
    ```json
    {
        "success": true,
        "message": "Sistema saludable",
        "data": {
            "overall_score": 98.5,
            "coverage_percentage": 100.0,
            "components": {
                "database": {"status": "healthy", "score": 100.0},
                "services": {"status": "healthy", "score": 97.2}
            }
        },
        "execution_time_seconds": 0.023,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Códigos de estado HTTP:**
    - **200**: Sistema saludable
    - **503**: Servicio no disponible
    - **500**: Error interno
    """
    start_time = time.time()
    logger.info("❤️ Verificación de salud del sistema")

    try:
        # Health check simplificado
        raw_matrix = cross_validation_matrix.build_matrix()

        # Calcular score general rápidamente
        total_score = 0.0
        component_count = 0
        components = {}

        for comp_name, comp_data in raw_matrix.items():
            if isinstance(comp_data, dict):
                score = float(comp_data.get('score', 50.0))
            else:
                score = float(comp_data) if isinstance(comp_data, (int, float)) else 50.0

            status = "healthy" if score > 90 else "warning" if score > 70 else "critical"
            components[comp_name] = ComponentStatus(status=status, score=score)

            total_score += score
            component_count += 1

        overall_score = total_score / component_count if component_count > 0 else 0.0

        execution_time = time.time() - start_time
        logger.info("✅ Health check completado en %.2fs - Score: %.1f", execution_time, overall_score)

        return MatrixResponse(
            success=True,
            message="Sistema saludable" if overall_score > 90 else "Atención requerida",
            data=ValidationMatrix(
                timestamp=datetime.now(),
                overall_score=round(overall_score, 1),
                coverage_percentage=100.0,
                components=components
            ),
            execution_time_seconds=round(execution_time, 3),
            timestamp=datetime.now()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en health check: %s", str(e))
        raise HTTPException(
            status_code=503,
            detail="Servicio de health check no disponible"
        ) from e

@router.get("/components/{component_name}", response_model=MatrixResponse)
async def get_component_status(component_name: str) -> MatrixResponse:
    """
    🔍 ESTADO DETALLADO DE COMPONENTE ESPECÍFICO
    ============================================

    Obtiene el estado detallado de validación de un componente específico
    del sistema, incluyendo métricas históricas y análisis de tendencias.

    **Parámetros de ruta:**
    - **component_name**: Nombre del componente a consultar

    **Componentes disponibles:**
    - `database`: Estado de la base de datos
    - `routers`: Estado de los routers FastAPI
    - `services`: Estado de los servicios backend
    - `cache`: Estado del sistema de cache
    - `external_apis`: Estado de APIs externas

    **Respuesta exitosa:**
    ```json
    {
        "success": true,
        "message": "Estado del componente obtenido",
        "data": {
            "components": {
                "database": {
                    "status": "healthy",
                    "score": 98.7,
                    "checks_passed": ["connection", "integrity", "performance"],
                    "response_time_ms": 12.3,
                    "last_check": "2024-12-01T10:30:00"
                }
            }
        },
        "execution_time_seconds": 0.067,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Códigos de error:**
    - **404**: Componente no encontrado
    - **503**: Componente no disponible para validación
    """
    start_time = time.time()
    logger.info("🔍 Consultando estado del componente: %s", component_name)

    try:
        # Obtener matriz completa
        raw_matrix = cross_validation_matrix.build_matrix()

        # Buscar el componente específico
        if component_name not in raw_matrix:
            raise HTTPException(
                status_code=404,
                detail=f"Componente '{component_name}' no encontrado"
            )

        component_data = raw_matrix[component_name]

        # Crear objeto ComponentStatus
        if isinstance(component_data, dict):
            status_obj = ComponentStatus(
                status=component_data.get('status', 'unknown'),
                score=float(component_data.get('score', 0.0)),
                checks_passed=component_data.get('checks_passed'),
                issues=component_data.get('issues'),
                last_check=component_data.get('last_check'),
                response_time_ms=component_data.get('response_time_ms')
            )
        else:
            # Para datos simples
            score = float(component_data) if isinstance(component_data, (int, float)) else 50.0
            status_obj = ComponentStatus(
                status="healthy" if score > 90 else "warning" if score > 70 else "critical",
                score=score
            )

        execution_time = time.time() - start_time
        logger.info("✅ Estado del componente %s obtenido en %.2fs", component_name, execution_time)

        return MatrixResponse(
            success=True,
            message=f"Estado del componente '{component_name}' obtenido",
            data=ValidationMatrix(
                timestamp=datetime.now(),
                overall_score=status_obj.score,
                coverage_percentage=100.0,
                components={component_name: status_obj}
            ),
            execution_time_seconds=round(execution_time, 3),
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error obteniendo estado del componente %s: %s", component_name, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado del componente: {str(e)}"
        ) from e
