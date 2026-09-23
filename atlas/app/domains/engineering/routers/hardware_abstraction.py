"""
Router de Abstracción de Hardware - Control de Instrumentos de Laboratorio

Módulo FastAPI para control de instrumentos de laboratorio y capa de abstracción de hardware.
Proporciona endpoints API unificados para gestión y control de instrumentos de laboratorio
a través de protocolos de comunicación industrial como SiLA2, OPC-UA, MQTT y Modbus.

Capacidades principales:
- Registro y gestión de instrumentos: conexión y configuración de equipos
- Ejecución de comandos en tiempo real: envío directo de instrucciones
- Monitoreo de estado: health checks y verificación de conectividad
- Soporte multi-protocolo: comunicación estandarizada con diversos equipos
- Configuración de demostración: instrumentos de prueba para desarrollo
- Reporte de estado del servicio: estadísticas y capacidades del sistema

Catálogo de Endpoints:
- POST /api/hardware/instruments/register: Registro de nuevos instrumentos de laboratorio
- DELETE /api/hardware/instruments/{id}: Desregistro de instrumentos del sistema
- GET /api/hardware/instruments: Listado de todos los instrumentos registrados
- GET /api/hardware/instruments/{id}: Información detallada de instrumento específico
- POST /api/hardware/instruments/{id}/commands: Envío de comandos a instrumentos
- POST /api/hardware/instruments/{id}/commands/queue: Cola de comandos para ejecución en segundo plano
- GET /api/hardware/instruments/{id}/status: Estado operacional del instrumento
- GET /api/hardware/protocols: Protocolos de comunicación soportados
- GET /api/hardware/instrument-types: Tipos de instrumentos soportados
- GET /api/hardware/service/status: Estado general de salud del servicio
- POST /api/hardware/demo/setup: Configuración de instrumentos de demostración
- DELETE /api/hardware/demo/cleanup: Eliminación de instrumentos de demostración

Dependencias:
- HardwareAbstractionService: Servicio central de abstracción y gestión de hardware
- SiLA2: Protocolo de estandarización en automatización de laboratorio 2
- OPC-UA: Arquitectura unificada OPC para comunicación industrial
- MQTT: Transporte de telemetría de colas de mensajes para dispositivos IoT
- Modbus TCP: Protocolo Ethernet industrial
- pydantic: Validación de requests/responses

Uso del Servicio:
    Registra instrumentos usando sus protocolos específicos de comunicación,
    luego envía comandos estandarizados a través de la API unificada. La cola
    en segundo plano permite operación no bloqueante para tareas de larga duración.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, Optional
import logging

from app.domains.engineering.services.hardware_abstraction_service import (
    HardwareAbstractionService,
    hardware_service,
    InstrumentConfiguration,
    InstrumentCommand,
    InstrumentType,
    ConnectionProtocol
)
from app.exceptions.domain.biology import BiologyError


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/hardware",
    tags=["Hardware Abstraction", "Laboratory Instruments", "SiLA2", "OPC-UA", "MQTT"]
)

@router.post("/instruments/register")
async def register_instrument(
    config: InstrumentConfiguration,
    service: HardwareAbstractionService = Depends(lambda: hardware_service)
):
    """
    🔧 Register new laboratory instrument
    
    Registers and connects to a laboratory instrument using
    industrial protocols like SiLA2, OPC-UA, or MQTT.
    """
    try:
        logger.info(f"🔧 Registering instrument: {config.name} ({config.type.value})")
        
        success = await service.register_instrument(config)
        
        if success:
            return {
                "success": True,
                "message": f"Instrument {config.name} registered successfully",
                "instrument_id": config.id,
                "protocol": config.protocol.value,
                "type": config.type.value
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to register instrument {config.name}"
            )
            
    except BiologyError as e:
        logger.error(f"❌ Error registering instrument: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@router.delete("/instruments/{instrument_id}")
async def unregister_instrument(
    instrument_id: str,
    service: HardwareAbstractionService = Depends(lambda: hardware_service)
):
    """
    🔌 Unregister laboratory instrument
    
    Disconnects and removes instrument from the system.
    """
    try:
        logger.info(f"🔌 Unregistering instrument: {instrument_id}")
        
        success = await service.unregister_instrument(instrument_id)
        
        if success:
            return {
                "success": True,
                "message": f"Instrument {instrument_id} unregistered successfully"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Instrument {instrument_id} not found"
            )
            
    except BiologyError as e:
        logger.error(f"❌ Error unregistering instrument: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unregistration error: {str(e)}")

@router.get("/instruments")
async def list_instruments(
    service: HardwareAbstractionService = Depends(lambda: hardware_service)
):
    """
    📋 List all registered instruments
    
    Returns information about all connected laboratory instruments
    including their status, capabilities, and last response times.
    """
    try:
        logger.info("📋 Listing all registered instruments")
        
        instruments = await service.get_all_instruments()
        
        return {
            "success": True,
            "message": f"Found {len(instruments)} registered instruments",
            "instruments": instruments,
            "total_count": len(instruments)
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error listing instruments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Listing error: {str(e)}")

@router.get("/instruments/{instrument_id}")
async def get_instrument_info(
    instrument_id: str,
    service: HardwareAbstractionService = Depends(lambda: hardware_service)
):
    """
    🔍 Get specific instrument information
    
    Returns detailed information about a specific instrument
    including status, capabilities, and configuration.
    """
    try:
        logger.info(f"🔍 Getting info for instrument: {instrument_id}")
        
        instruments = await service.get_all_instruments()
        
        if instrument_id not in instruments:
            raise HTTPException(
                status_code=404,
                detail=f"Instrument {instrument_id} not found"
            )
            
        instrument_info = instruments[instrument_id]
        status = await service.get_instrument_status(instrument_id)
        
        return {
            "success": True,
            "message": f"Information for instrument {instrument_id}",
            "instrument": {
                **instrument_info,
                "current_status": status.value if status else "unknown"
            }
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"❌ Error getting instrument info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Info retrieval error: {str(e)}")

@router.post("/instruments/{instrument_id}/commands")
async def send_instrument_command(
    instrument_id: str,
    command: str,
    parameters: Optional[Dict[str, Any]] = None,
    priority: int = 5,
    timeout: int = 30,
    service: HardwareAbstractionService = Depends(lambda: hardware_service)
):
    """
    📤 Send command to instrument
    
    Sends a command to a specific laboratory instrument and
    returns the response with execution details.
    """
    try:
        logger.info(f"📤 Sending command '{command}' to instrument: {instrument_id}")
        
        # Create command object
        instrument_command = InstrumentCommand(
            instrument_id=instrument_id,
            command=command,
            parameters=parameters or {},
            priority=priority,
            timeout=timeout
        )
        
        # Send command
        response = await service.send_command(instrument_command)
        
        return {
            "success": response.status == "success",
            "message": f"Command '{command}' executed",
            "response": {
                "instrument_id": response.instrument_id,
                "command": response.command,
                "status": response.status,
                "data": response.data,
                "timestamp": response.timestamp.isoformat(),
                "execution_time": response.execution_time,
                "error": response.error
            }
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error sending command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Command execution error: {str(e)}")

@router.post("/instruments/{instrument_id}/commands/queue")
async def queue_instrument_command(
    instrument_id: str,
    command: str,
    parameters: Optional[Dict[str, Any]] = None,
    priority: int = 5,
    timeout: int = 30,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: HardwareAbstractionService = Depends(lambda: hardware_service)
):
    """
    📥 Queue command for background execution
    
    Queues a command for background processing without blocking.
    Useful for long-running operations.
    """
    try:
        logger.info(f"📥 Queuing command '{command}' for instrument: {instrument_id}")
        
        # Create command object
        instrument_command = InstrumentCommand(
            instrument_id=instrument_id,
            command=command,
            parameters=parameters or {},
            priority=priority,
            timeout=timeout
        )
        
        # Queue command for background processing
        await service.queue_command(instrument_command)
        
        return {
            "success": True,
            "message": f"Command '{command}' queued for execution",
            "instrument_id": instrument_id,
            "command": command,
            "priority": priority,
            "estimated_execution": "background"
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error queuing command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Command queueing error: {str(e)}")

@router.get("/instruments/{instrument_id}/status")
async def get_instrument_status(
    instrument_id: str,
    service: HardwareAbstractionService = Depends(lambda: hardware_service)
):
    """
    📊 Get instrument status
    
    Returns current operational status of the instrument.
    """
    try:
        logger.info(f"📊 Getting status for instrument: {instrument_id}")
        
        status = await service.get_instrument_status(instrument_id)
        
        if status is None:
            raise HTTPException(
                status_code=404,
                detail=f"Instrument {instrument_id} not found"
            )
            
        return {
            "success": True,
            "message": f"Status for instrument {instrument_id}",
            "instrument_id": instrument_id,
            "status": status.value,
            "status_description": {
                "idle": "Instrument ready for commands",
                "running": "Instrument executing operation", 
                "error": "Instrument has error condition",
                "maintenance": "Instrument under maintenance",
                "offline": "Instrument not connected",
                "initializing": "Instrument starting up",
                "calibrating": "Instrument performing calibration"
            }.get(status.value, "Unknown status")
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"❌ Error getting instrument status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status retrieval error: {str(e)}")

@router.get("/protocols")
async def list_supported_protocols():
    """
    🔗 List supported communication protocols
    
    Returns information about all supported laboratory
    communication protocols and their capabilities.
    """
    try:
        protocols_info = {
            "sila2": {
                "name": "SiLA2 - Standardization in Lab Automation 2",
                "description": "Industry standard for laboratory automation",
                "features": ["gRPC-based", "Service-oriented", "Standardized commands"],
                "typical_instruments": ["Liquid handlers", "Pipettes", "Analytical instruments"],
                "connection_params": ["server_url", "client_cert", "server_cert"]
            },
            "opc_ua": {
                "name": "OPC-UA - OPC Unified Architecture", 
                "description": "Industrial communication standard",
                "features": ["Secure communication", "Real-time data", "Cross-platform"],
                "typical_instruments": ["PLCs", "Sensors", "Industrial equipment"],
                "connection_params": ["server_url", "username", "password", "namespace"]
            },
            "mqtt": {
                "name": "MQTT - Message Queuing Telemetry Transport",
                "description": "Lightweight IoT messaging protocol",
                "features": ["Publish/Subscribe", "Low bandwidth", "Real-time"],
                "typical_instruments": ["IoT sensors", "Smart devices", "Environmental monitors"],
                "connection_params": ["broker_host", "broker_port", "username", "password", "command_topic", "response_topic"]
            },
            "modbus_tcp": {
                "name": "Modbus TCP",
                "description": "Industrial Ethernet protocol",
                "features": ["TCP/IP based", "Master/Slave", "Register-based"],
                "typical_instruments": ["PLCs", "Temperature controllers", "Flow meters"],
                "connection_params": ["host", "port", "unit_id"]
            },
            "http_rest": {
                "name": "HTTP REST API",
                "description": "Standard web API protocol",
                "features": ["HTTP-based", "RESTful", "JSON payloads"],
                "typical_instruments": ["Modern lab equipment", "Web-enabled devices"],
                "connection_params": ["base_url", "api_key", "headers"]
            }
        }
        
        return {
            "success": True,
            "message": "Supported communication protocols",
            "protocols": protocols_info,
            "total_protocols": len(protocols_info)
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error listing protocols: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Protocol listing error: {str(e)}")

@router.get("/instrument-types")
async def list_instrument_types():
    """
    🔬 List supported instrument types
    
    Returns information about all supported laboratory
    instrument types and their typical capabilities.
    """
    try:
        instrument_types_info = {
            "spectrometer": {
                "name": "Spectrometer",
                "description": "Optical analysis instruments",
                "typical_commands": ["StartSpectrum", "GetSpectrum", "SetWavelength", "Calibrate"],
                "applications": ["Chemical analysis", "Material characterization", "Quality control"]
            },
            "chromatograph": {
                "name": "Chromatograph", 
                "description": "Separation and analysis instruments",
                "typical_commands": ["StartRun", "LoadMethod", "GetResults", "SetTemperature"],
                "applications": ["Compound separation", "Purity analysis", "Quantitative analysis"]
            },
            "microscope": {
                "name": "Microscope",
                "description": "Imaging instruments",
                "typical_commands": ["CaptureImage", "SetMagnification", "FocusAdjust", "MoveLens"],
                "applications": ["Cell imaging", "Material inspection", "Quality control"]
            },
            "liquid_handler": {
                "name": "Liquid Handler",
                "description": "Automated pipetting systems",
                "typical_commands": ["Aspirate", "Dispense", "MoveTip", "WashTips"],
                "applications": ["Sample prep", "Assay setup", "Dilution series"]
            },
            "balance": {
                "name": "Analytical Balance",
                "description": "Precision weighing instruments", 
                "typical_commands": ["Weigh", "Tare", "Calibrate", "GetStability"],
                "applications": ["Sample weighing", "Formulation", "Quality control"]
            }
        }
        
        return {
            "success": True,
            "message": "Supported instrument types",
            "instrument_types": instrument_types_info,
            "total_types": len(instrument_types_info),
            "available_types": [t.value for t in InstrumentType]
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error listing instrument types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Instrument types listing error: {str(e)}")

@router.get("/service/status")
async def get_service_status(
    service: HardwareAbstractionService = Depends(lambda: hardware_service)
):
    """
    📊 Get Hardware Abstraction Service status
    
    Returns overall service health, registered instruments count,
    and system capabilities.
    """
    try:
        instruments = await service.get_all_instruments()
        
        # Count instruments by status
        status_counts = {}
        for instrument_info in instruments.values():
            if "error" not in instrument_info:
                status = instrument_info.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "success": True,
            "message": "Hardware Abstraction Service operational",
            "service": {
                "name": "HardwareAbstractionService",
                "status": "operational",
                "version": "1.0.0"
            },
            "statistics": {
                "total_instruments": len(instruments),
                "status_breakdown": status_counts,
                "supported_protocols": len(ConnectionProtocol),
                "supported_types": len(InstrumentType)
            },
            "capabilities": {
                "protocols": [p.value for p in ConnectionProtocol],
                "instrument_types": [t.value for t in InstrumentType],
                "features": [
                    "Real-time command execution",
                    "Background command queuing", 
                    "Status monitoring",
                    "Multi-protocol support",
                    "Industrial standards compliance"
                ]
            }
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error getting service status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service status error: {str(e)}")

@router.post("/demo/setup")
async def setup_demo_instruments(
    service: HardwareAbstractionService = Depends(lambda: hardware_service)
):
    """
    🧪 Setup demo laboratory instruments
    
    Creates mock instruments for testing and demonstration purposes.
    Useful for development and training.
    """
    try:
        logger.info("🧪 Setting up demo instruments")
        
        # Demo instrument configurations
        demo_instruments = [
            {
                "id": "demo_spectrometer_01",
                "name": "Demo UV-Vis Spectrometer",
                "type": InstrumentType.SPECTROMETER,
                "protocol": ConnectionProtocol.SILA2,
                "connection_params": {
                    "server_url": "http://localhost:50051",
                    "client_cert": None,
                    "server_cert": None
                },
                "capabilities": ["StartSpectrum", "GetSpectrum", "Calibrate"],
                "metadata": {
                    "manufacturer": "AXIOM Demo",
                    "model": "UV-Vis-2000",
                    "serial": "DEMO001"
                }
            },
            {
                "id": "demo_liquid_handler_01", 
                "name": "Demo Liquid Handler",
                "type": InstrumentType.LIQUID_HANDLER,
                "protocol": ConnectionProtocol.OPC_UA,
                "connection_params": {
                    "server_url": "opc.tcp://localhost:4840",
                    "namespace": 2,
                    "username": "demo",
                    "password": "demo123"
                },
                "capabilities": ["Aspirate", "Dispense", "MoveTip"],
                "metadata": {
                    "manufacturer": "AXIOM Demo",
                    "model": "LH-1000", 
                    "serial": "DEMO002"
                }
            },
            {
                "id": "demo_sensor_01",
                "name": "Demo Temperature Sensor",
                "type": InstrumentType.SENSOR,
                "protocol": ConnectionProtocol.MQTT,
                "connection_params": {
                    "broker_host": "localhost",
                    "broker_port": 1883,
                    "command_topic": "lab/sensor/cmd",
                    "response_topic": "lab/sensor/resp"
                },
                "capabilities": ["ReadTemperature", "SetAlarms"],
                "metadata": {
                    "manufacturer": "AXIOM Demo",
                    "model": "TEMP-101",
                    "serial": "DEMO003"
                }
            }
        ]
        
        # Register demo instruments
        results = []
        for demo_config in demo_instruments:
            config = InstrumentConfiguration(**demo_config)
            success = await service.register_instrument(config)
            results.append({
                "instrument_id": config.id,
                "name": config.name,
                "registered": success
            })
        
        successful_registrations = len([r for r in results if r["registered"]])
        
        return {
            "success": True,
            "message": f"Demo setup complete: {successful_registrations}/{len(demo_instruments)} instruments registered",
            "demo_instruments": results,
            "total_registered": successful_registrations,
            "next_steps": [
                "Use GET /api/hardware/instruments to see registered instruments",
                "Send commands with POST /api/hardware/instruments/{id}/commands",
                "Check status with GET /api/hardware/instruments/{id}/status"
            ]
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error setting up demo instruments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo setup error: {str(e)}")

@router.delete("/demo/cleanup")
async def cleanup_demo_instruments(
    service: HardwareAbstractionService = Depends(lambda: hardware_service)
):
    """
    🧹 Cleanup demo instruments
    
    Removes all demo instruments from the system.
    """
    try:
        logger.info("🧹 Cleaning up demo instruments")
        
        instruments = await service.get_all_instruments()
        demo_instruments = [
            instrument_id for instrument_id in instruments.keys()
            if instrument_id.startswith("demo_")
        ]
        
        cleanup_results = []
        for instrument_id in demo_instruments:
            success = await service.unregister_instrument(instrument_id)
            cleanup_results.append({
                "instrument_id": instrument_id,
                "removed": success
            })
        
        successful_removals = sum(1 for r in cleanup_results if r["removed"])
        
        return {
            "success": True,
            "message": f"Demo cleanup complete: {successful_removals}/{len(demo_instruments)} instruments removed",
            "removed_instruments": cleanup_results,
            "total_removed": successful_removals
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error cleaning up demo instruments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo cleanup error: {str(e)}")
