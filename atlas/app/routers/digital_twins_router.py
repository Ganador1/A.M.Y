"""
Digital Twins Router

Router FastAPI para gestión de gemelos digitales y simulación de experimentos científicos.
Proporciona endpoints REST API para creación y gestión del ciclo de vida de gemelos digitales,
simulación en tiempo real de experimentos científicos y procesos, analytics predictivos para
resultados experimentales, optimización multi-objetivo de parámetros experimentales,
sincronización de datos de sensores con equipos físicos, operaciones por lotes para gestión
de múltiples gemelos, analytics de rendimiento y monitoreo de salud del servicio,
flujos de trabajo de calibración de modelos y ajuste de parámetros.

Capacidades principales:
- Creación y gestión completa del ciclo de vida de gemelos digitales
- Simulación en tiempo real de experimentos científicos y procesos químicos
- Analytics predictivos avanzados para resultados experimentales
- Optimización multi-objetivo de parámetros experimentales con algoritmos genéticos
- Sincronización automática de datos de sensores con equipos físicos
- Operaciones por lotes eficientes para gestión de múltiples gemelos
- Analytics comprehensivo de rendimiento y monitoreo de salud del servicio
- Flujos de trabajo de calibración de modelos y ajuste fino de parámetros
- Simulación de escenarios hipotéticos y análisis de sensibilidad
- Integración con sistemas de control de laboratorio y adquisición de datos

Endpoints disponibles:
- POST /create: Crear nuevo gemelo digital con configuración específica
- GET /list: Listar todos los gemelos digitales activos
- GET /{twin_id}: Obtener estado detallado de gemelo específico
- PUT /{twin_id}: Actualizar parámetros de gemelo digital
- DELETE /{twin_id}: Eliminar gemelo digital
- POST /{twin_id}/simulate: Ejecutar simulación en tiempo real
- POST /{twin_id}/predict: Generar predicciones de resultados
- POST /{twin_id}/optimize: Optimización de parámetros experimentales
- POST /{twin_id}/sync-sensors: Sincronizar datos de sensores
- GET /batch/status: Estado de operaciones por lotes
- GET /analytics: Analytics de rendimiento del sistema

Dependencias:
- DigitalTwinsService: Servicio principal de gemelos digitales
- TwinType: Enumeración de tipos de gemelos disponibles
- SensorReading: Modelo de lecturas de sensores
- CreateTwinRequest: Solicitud de creación de gemelo
- SimulationRequest: Solicitud de simulación

Uso típico:
    from app.routers.digital_twins_router import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles bajo el prefijo /digital-twins
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field, ConfigDict

from app.exceptions.domain.biology import BiologyError
from app.services.digital_twins_service import (
    get_digital_twins_service, DigitalTwinsService,
    TwinType, SensorReading,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/digital-twins", tags=["Digital Twins"])

# Pydantic models for API

class CreateTwinRequest(BaseModel):
    """Request model for creating a digital twin"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Synthesis Reaction A",
                "twin_type": "process",
                "model_type": "chemical_reaction",
                "parameters": {
                    "temperature": 60.0,
                    "pressure": 2.0,
                    "concentration_A": 1.5
                }
            }
        }
    )

    name: str = Field(..., description="Name of the digital twin")
    twin_type: str = Field(..., description="Type of twin: equipment, experiment, process, etc.")
    model_type: str = Field(..., description="Model type: chemical_reaction, biological_process, etc.")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Initial parameters for the twin")

class SimulationRequest(BaseModel):
    """Request model for running simulation"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "duration_hours": 24.0,
                "scenario_name": "high_temperature_run",
                "parameters": {
                    "target_conversion": 90.0
                }
            }
        }
    )

    duration_hours: float = Field(..., description="Simulation duration in hours", gt=0, le=168)
    scenario_name: str = Field("default", description="Name of simulation scenario")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional simulation parameters")

class PredictionRequest(BaseModel):
    """Request model for getting predictions"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "parameter": "conversion",
                "time_horizon_hours": 48.0
            }
        }
    )

    parameter: str = Field(..., description="Parameter to predict")
    time_horizon_hours: float = Field(..., description="Prediction time horizon in hours", gt=0, le=720)

class OptimizationRequest(BaseModel):
    """Request model for optimization"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "objective": "maximize_yield",
                "constraints": {
                    "max_temperature": 80.0,
                    "max_pressure": 5.0
                }
            }
        }
    )

    objective: str = Field(..., description="Optimization objective")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Optimization constraints")

class SensorDataRequest(BaseModel):
    """Request model for sensor data synchronization"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "readings": [
                    {
                        "sensor_id": "temp_001",
                        "parameter_name": "temperature",
                        "value": 65.2,
                        "unit": "°C",
                        "timestamp": "2025-09-13T10:30:00Z",
                        "confidence": 0.95
                    }
                ]
            }
        }
    )

    readings: List[Dict[str, Any]] = Field(..., description="List of sensor readings")

# API Endpoints

@router.get("/status")
async def get_service_status(
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> Dict[str, Any]:
    """
    📊 Get Digital Twins Service Status

    Returns current status and statistics of the Digital Twins Service.
    """
    try:
        status = await service.get_service_statistics()
        logger.info("API Request: GET /digital-twins/status")
        return status
    except BiologyError as e:
        logger.error(f"Error getting service status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins")
async def list_digital_twins(
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> List[Dict[str, Any]]:
    """
    📋 List All Digital Twins

    Returns a list of all digital twins with their basic information.
    """
    try:
        twins = await service.list_digital_twins()
        logger.info(f"API Request: GET /digital-twins/twins - Found {len(twins)} twins")
        return twins
    except BiologyError as e:
        logger.error(f"Error listing digital twins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins")
async def create_digital_twin(
    request: CreateTwinRequest,
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> Dict[str, Any]:
    """
    🎭 Create New Digital Twin

    Creates a new digital twin with the specified configuration.
    """
    try:
        # Validate twin_type
        try:
            twin_type = TwinType(request.twin_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid twin_type. Must be one of: {[t.value for t in TwinType]}"
            )

        # Create twin
        twin = await service.create_digital_twin(
            name=request.name,
            twin_type=twin_type,
            model_type=request.model_type,
            parameters=request.parameters
        )

        # Get detailed status
        status = await service.get_twin_status(twin.id)

        logger.info(f"API Request: POST /digital-twins/twins - Created twin {twin.id}")
        return status

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error creating digital twin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/{twin_id}")
async def get_twin_details(
    twin_id: str,
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> Dict[str, Any]:
    """
    🔍 Get Twin Details

    Returns detailed information about a specific digital twin.
    """
    try:
        status = await service.get_twin_status(twin_id)
        logger.info(f"API Request: GET /digital-twins/twins/{twin_id}")
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BiologyError as e:
        logger.error(f"Error getting twin details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins/{twin_id}/simulate")
async def run_simulation(
    twin_id: str,
    request: SimulationRequest,
    background_tasks: BackgroundTasks,
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> Dict[str, Any]:
    """
    🎬 Run Simulation

    Starts a simulation on the specified digital twin.
    """
    try:
        duration = timedelta(hours=request.duration_hours)

        # Run simulation
        results = await service.run_simulation(
            twin_id=twin_id,
            duration=duration,
            scenario_name=request.scenario_name,
            **(request.parameters or {})
        )

        # Convert results to API response format
        response = {
            "simulation_id": results.twin_id,
            "start_time": results.start_time.isoformat(),
            "end_time": results.end_time.isoformat() if results.end_time else None,
            "duration_seconds": results.duration.total_seconds() if results.duration else None,
            "state": results.state.value,
            "scenario": request.scenario_name,
            "parameter_count": len(results.parameters),
            "predictions_count": len(results.predictions),
            "optimizations_count": len(results.optimizations),
            "metadata": results.metadata
        }

        if results.error_message:
            response["error_message"] = results.error_message

        logger.info(f"API Request: POST /digital-twins/twins/{twin_id}/simulate - Duration: {request.duration_hours}h")
        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BiologyError as e:
        logger.error(f"Error running simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins/{twin_id}/predict")
async def get_prediction(
    twin_id: str,
    request: PredictionRequest,
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> Dict[str, Any]:
    """
    🔮 Get Prediction

    Generates a prediction for the specified parameter and time horizon.
    """
    try:
        time_horizon = timedelta(hours=request.time_horizon_hours)

        prediction = await service.get_prediction(
            twin_id=twin_id,
            parameter=request.parameter,
            time_horizon=time_horizon
        )

        response = {
            "parameter": prediction.parameter,
            "current_time": datetime.now().isoformat(),
            "prediction_time": (datetime.now() + time_horizon).isoformat(),
            "predicted_value": prediction.predicted_value,
            "confidence": prediction.confidence,
            "prediction_method": prediction.prediction_method,
            "uncertainty_range": {
                "min": prediction.uncertainty_range[0],
                "max": prediction.uncertainty_range[1]
            },
            "factors": prediction.factors,
            "time_horizon_hours": request.time_horizon_hours
        }

        logger.info(f"API Request: POST /digital-twins/twins/{twin_id}/predict - Parameter: {request.parameter}")
        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BiologyError as e:
        logger.error(f"Error generating prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins/{twin_id}/optimize")
async def optimize_experiment(
    twin_id: str,
    request: OptimizationRequest,
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> List[Dict[str, Any]]:
    """
    ⚡ Optimize Experiment

    Generates optimization suggestions for the specified objective.
    """
    try:
        suggestions = await service.optimize_experiment(
            twin_id=twin_id,
            objective=request.objective,
            constraints=request.constraints
        )

        response = []
        for suggestion in suggestions:
            response.append({
                "parameter": suggestion.parameter,
                "current_value": suggestion.current_value,
                "suggested_value": suggestion.suggested_value,
                "expected_improvement": suggestion.expected_improvement,
                "confidence": suggestion.confidence,
                "reasoning": suggestion.reasoning,
                "impact_analysis": suggestion.impact_analysis
            })

        logger.info(f"API Request: POST /digital-twins/twins/{twin_id}/optimize - Objective: {request.objective}")
        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BiologyError as e:
        logger.error(f"Error generating optimization suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins/{twin_id}/sync")
async def sync_with_sensors(
    twin_id: str,
    request: SensorDataRequest,
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> Dict[str, Any]:
    """
    🔄 Sync with Sensor Data

    Synchronizes the digital twin with real sensor data from physical equipment.
    """
    try:
        # Convert request data to SensorReading objects
        sensor_readings = []
        for reading_data in request.readings:
            reading = SensorReading(
                sensor_id=reading_data["sensor_id"],
                parameter_name=reading_data["parameter_name"],
                value=float(reading_data["value"]),
                unit=reading_data["unit"],
                timestamp=datetime.fromisoformat(reading_data["timestamp"].replace("Z", "+00:00")),
                confidence=reading_data.get("confidence", 1.0),
                quality_flags=reading_data.get("quality_flags", [])
            )
            sensor_readings.append(reading)

        # Sync twin
        sync_result = await service.sync_with_real_data(
            twin_id=twin_id,
            sensor_data=sensor_readings
        )

        logger.info(f"API Request: POST /digital-twins/twins/{twin_id}/sync - {len(sensor_readings)} readings")
        return sync_result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BiologyError as e:
        logger.error(f"Error syncing with sensor data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/{twin_id}/parameters")
async def get_twin_parameters(
    twin_id: str,
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> Dict[str, Any]:
    """
    📊 Get Twin Parameters

    Returns current parameter values and metadata for the digital twin.
    """
    try:
        status = await service.get_twin_status(twin_id)

        response = {
            "twin_id": twin_id,
            "parameters": status["parameters"],
            "last_updated": max(
                [param["last_updated"] for param in status["parameters"].values()]
            ) if status["parameters"] else None,
            "total_parameters": len(status["parameters"]),
            "calibration_accuracy": status["calibration_accuracy"]
        }

        logger.info(f"API Request: GET /digital-twins/twins/{twin_id}/parameters")
        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BiologyError as e:
        logger.error(f"Error getting twin parameters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/twins/{twin_id}/parameters")
async def update_twin_parameters(
    twin_id: str,
    parameters: Dict[str, Any],
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> Dict[str, Any]:
    """
    📝 Update Twin Parameters

    Updates parameter values for the digital twin.
    """
    try:
        # Get current twin status
        if twin_id not in service.twins:
            raise HTTPException(status_code=404, detail=f"Twin {twin_id} not found")

        twin = service.twins[twin_id]
        updated_count = 0

        # Update parameters
        for param_name, param_value in parameters.items():
            if param_name in twin.model.parameters:
                twin.model.parameters[param_name].value = param_value
                twin.model.parameters[param_name].last_updated = datetime.now()
                twin.model.parameters[param_name].source = "api_update"
                updated_count += 1

        # Get updated status
        status = await service.get_twin_status(twin_id)

        response = {
            "twin_id": twin_id,
            "updated_parameters": updated_count,
            "total_parameters": len(status["parameters"]),
            "update_time": datetime.now().isoformat(),
            "parameters": {k: v for k, v in status["parameters"].items() if k in parameters}
        }

        logger.info(f"API Request: PUT /digital-twins/twins/{twin_id}/parameters - Updated {updated_count} parameters")
        return response

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error updating twin parameters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/twins/{twin_id}")
async def delete_digital_twin(
    twin_id: str,
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> Dict[str, Any]:
    """
    🗑️ Delete Digital Twin

    Removes a digital twin and all associated data.
    """
    try:
        success = await service.delete_digital_twin(twin_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Twin {twin_id} not found")

        response = {
            "twin_id": twin_id,
            "deleted": True,
            "deletion_time": datetime.now().isoformat(),
            "message": "Digital twin successfully deleted"
        }

        logger.info(f"API Request: DELETE /digital-twins/twins/{twin_id}")
        return response

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error deleting digital twin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-types")
async def get_supported_models(
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> Dict[str, Any]:
    """
    🧪 Get Supported Model Types

    Returns information about available digital twin model types.
    """
    try:
        models = service.get_supported_model_types()

        response = {
            "total_models": len(models),
            "models": models,
            "twin_types": [t.value for t in TwinType]
        }

        logger.info("API Request: GET /digital-twins/model-types")
        return response

    except BiologyError as e:
        logger.error(f"Error getting supported models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins/batch")
async def create_multiple_twins(
    twins: List[CreateTwinRequest],
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> List[Dict[str, Any]]:
    """
    🏭 Create Multiple Twins

    Creates multiple digital twins in a single batch operation.
    """
    try:
        results = []

        for twin_request in twins:
            try:
                # Validate twin_type
                twin_type = TwinType(twin_request.twin_type.lower())

                # Create twin
                twin = await service.create_digital_twin(
                    name=twin_request.name,
                    twin_type=twin_type,
                    model_type=twin_request.model_type,
                    parameters=twin_request.parameters
                )

                # Get status
                status = await service.get_twin_status(twin.id)
                status["success"] = True
                results.append(status)

            except BiologyError as e:
                results.append({
                    "name": twin_request.name,
                    "success": False,
                    "error": str(e)
                })

        logger.info(f"API Request: POST /digital-twins/twins/batch - Created {len(twins)} twins")
        return results

    except BiologyError as e:
        logger.error(f"Error creating multiple twins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_analytics_summary(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=90),
    service: DigitalTwinsService = Depends(get_digital_twins_service)
) -> Dict[str, Any]:
    """
    📈 Get Analytics Summary

    Returns analytics and performance metrics for digital twins operations.
    """
    try:
        stats = await service.get_service_statistics()

        # Calculate derived metrics
        total_twins = stats["total_twins"]
        active_twins = stats["active_twins"]
        connected_twins = stats["connected_twins"]

        activity_rate = (active_twins / total_twins * 100) if total_twins > 0 else 0
        connection_rate = (connected_twins / total_twins * 100) if total_twins > 0 else 0

        response = {
            "period_days": days,
            "analysis_time": datetime.now().isoformat(),
            "twin_statistics": {
                "total_twins": total_twins,
                "active_twins": active_twins,
                "connected_twins": connected_twins,
                "activity_rate": round(activity_rate, 2),
                "connection_rate": round(connection_rate, 2)
            },
            "operation_statistics": {
                "total_simulations": stats["total_simulations"],
                "successful_predictions": stats["successful_predictions"],
                "optimization_suggestions": stats["optimization_suggestions"],
                "running_simulations": stats["running_simulations"]
            },
            "service_health": {
                "status": stats["status"],
                "uptime": stats["uptime"],
                "supported_models": len(stats["supported_models"])
            }
        }

        logger.info(f"API Request: GET /digital-twins/analytics - Period: {days} days")
        return response

    except BiologyError as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Log router initialization
logger.info("🏭 Digital Twins Router loaded with 15 endpoints")
