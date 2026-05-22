#!/usr/bin/env python3
"""
AXIOM Hardware Abstraction Layer
Universal interface for laboratory instruments using industrial standards

Supports:
- SiLA2 (Standardization in Lab Automation 2)
- OPC-UA (OPC Unified Architecture)  
- MQTT (Message Queuing Telemetry Transport)
- Modbus TCP/RTU
- HTTP/REST APIs

Author: AXIOM Autonomous Laboratory System
Date: September 13, 2025
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

import aiohttp
# import paho.mqtt.client as mqtt  # Optional - for real MQTT implementation
from pydantic import BaseModel, Field
from app.exceptions.domain.biology import BiologyError

logger = logging.getLogger(__name__)

class InstrumentType(Enum):
    """Types of laboratory instruments"""
    SPECTROMETER = "spectrometer"
    CHROMATOGRAPH = "chromatograph"
    MICROSCOPE = "microscope"
    CENTRIFUGE = "centrifuge"
    PIPETTE = "pipette"
    BALANCE = "balance"
    THERMOCYCLER = "thermocycler"
    PLATE_READER = "plate_reader"
    LIQUID_HANDLER = "liquid_handler"
    INCUBATOR = "incubator"
    SHAKER = "shaker"
    REACTOR = "reactor"
    SENSOR = "sensor"
    PUMP = "pump"
    VALVE = "valve"
    GENERIC = "generic"

class ConnectionProtocol(Enum):
    """Supported connection protocols"""
    SILA2 = "sila2"
    OPC_UA = "opc_ua"
    MQTT = "mqtt"
    MODBUS_TCP = "modbus_tcp"
    MODBUS_RTU = "modbus_rtu"
    HTTP_REST = "http_rest"
    SERIAL = "serial"
    ETHERNET = "ethernet"

class InstrumentStatus(Enum):
    """Instrument operational status"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    CALIBRATING = "calibrating"

@dataclass
class InstrumentCommand:
    """Command to send to an instrument"""
    instrument_id: str
    command: str
    parameters: Dict[str, Any]
    priority: int = 5  # 1=highest, 10=lowest
    timeout: int = 30  # seconds
    callback: Optional[Callable] = None

@dataclass
class InstrumentResponse:
    """Response from an instrument"""
    instrument_id: str
    command: str
    status: str
    data: Optional[Dict[str, Any]]
    timestamp: datetime
    execution_time: float
    error: Optional[str] = None

class InstrumentConfiguration(BaseModel):
    """Configuration for laboratory instrument"""
    id: str = Field(..., description="Unique instrument identifier")
    name: str = Field(..., description="Human-readable instrument name")
    type: InstrumentType = Field(..., description="Type of instrument")
    protocol: ConnectionProtocol = Field(..., description="Communication protocol")
    connection_params: Dict[str, Any] = Field(..., description="Protocol-specific parameters")
    capabilities: List[str] = Field(default_factory=list, description="Available commands/features")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    calibration_date: Optional[datetime] = Field(None, description="Last calibration")
    maintenance_schedule: Optional[str] = Field(None, description="Maintenance schedule")

class AbstractInstrumentDriver(ABC):
    """Abstract base class for instrument drivers"""
    
    def __init__(self, config: InstrumentConfiguration):
        self.config = config
        self.status = InstrumentStatus.OFFLINE
        self.connected = False
        self.last_response = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the instrument"""
        pass
        
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the instrument"""
        pass
        
    @abstractmethod
    async def send_command(self, command: InstrumentCommand) -> InstrumentResponse:
        """Send command to instrument"""
        pass
        
    @abstractmethod
    async def get_status(self) -> InstrumentStatus:
        """Get current instrument status"""
        pass
        
    @abstractmethod
    async def get_capabilities(self) -> List[str]:
        """Get instrument capabilities"""
        pass

class SiLA2Driver(AbstractInstrumentDriver):
    """SiLA2 (Standardization in Lab Automation 2) driver"""
    
    def __init__(self, config: InstrumentConfiguration):
        super().__init__(config)
        self.server_url = config.connection_params.get("server_url")
        self.client_cert = config.connection_params.get("client_cert")
        self.server_cert = config.connection_params.get("server_cert")
        
    async def connect(self) -> bool:
        """Connect to SiLA2 server"""
        try:
            logger.info(f"🔗 Connecting to SiLA2 instrument: {self.config.name} at {self.server_url}")
            
            # Simulate SiLA2 connection (in real implementation would use sila2lib)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/ServerInfo") as response:
                    if response.status == 200:
                        self.connected = True
                        self.status = InstrumentStatus.IDLE
                        logger.info(f"✅ SiLA2 connection established: {self.config.name}")
                        return True
                        
        except BiologyError as e:
            logger.error(f"❌ SiLA2 connection failed: {e}")
            self.status = InstrumentStatus.ERROR
            
        return False
        
    async def disconnect(self) -> bool:
        """Disconnect from SiLA2 server"""
        self.connected = False
        self.status = InstrumentStatus.OFFLINE
        logger.info(f"🔌 SiLA2 disconnected: {self.config.name}")
        return True
        
    async def send_command(self, command: InstrumentCommand) -> InstrumentResponse:
        """Send SiLA2 command"""
        start_time = datetime.now()
        
        try:
            if not self.connected:
                raise Exception("Instrument not connected")
                
            logger.info(f"📤 SiLA2 Command: {command.command} to {self.config.name}")
            
            # Simulate SiLA2 command execution
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Mock response based on command type
            if command.command == "StartMeasurement":
                data = {
                    "measurement_id": f"meas_{int(datetime.now().timestamp())}",
                    "expected_duration": "30s",
                    "status": "started"
                }
            elif command.command == "GetResults":
                data = {
                    "results": [1.23, 4.56, 7.89],
                    "units": "mg/mL",
                    "quality": "good"
                }
            else:
                data = {"response": "command_executed", "parameters": command.parameters}
                
            execution_time = (datetime.now() - start_time).total_seconds()
            
            response = InstrumentResponse(
                instrument_id=command.instrument_id,
                command=command.command,
                status="success",
                data=data,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            
            self.last_response = response
            logger.info(f"✅ SiLA2 response received in {execution_time:.2f}s")
            return response
            
        except BiologyError as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ SiLA2 command failed: {e}")
            
            return InstrumentResponse(
                instrument_id=command.instrument_id,
                command=command.command,
                status="error",
                data=None,
                timestamp=datetime.now(),
                execution_time=execution_time,
                error=str(e)
            )
            
    async def get_status(self) -> InstrumentStatus:
        """Get SiLA2 instrument status"""
        if not self.connected:
            return InstrumentStatus.OFFLINE
            
        # Simulate status check
        return self.status
        
    async def get_capabilities(self) -> List[str]:
        """Get SiLA2 instrument capabilities"""
        return [
            "StartMeasurement",
            "StopMeasurement", 
            "GetResults",
            "Calibrate",
            "Reset",
            "GetStatus"
        ]

class OPCUADriver(AbstractInstrumentDriver):
    """OPC-UA (OPC Unified Architecture) driver"""
    
    def __init__(self, config: InstrumentConfiguration):
        super().__init__(config)
        self.server_url = config.connection_params.get("server_url")
        self.namespace = config.connection_params.get("namespace", 0)
        self.username = config.connection_params.get("username")
        self.password = config.connection_params.get("password")
        
    async def connect(self) -> bool:
        """Connect to OPC-UA server"""
        try:
            logger.info(f"🔗 Connecting to OPC-UA instrument: {self.config.name} at {self.server_url}")
            
            # In real implementation would use asyncua library
            # from asyncua import Client
            # self.client = Client(url=self.server_url)
            # await self.client.connect()
            
            # Simulate connection
            await asyncio.sleep(0.2)
            self.connected = True
            self.status = InstrumentStatus.IDLE
            
            logger.info(f"✅ OPC-UA connection established: {self.config.name}")
            return True
            
        except BiologyError as e:
            logger.error(f"❌ OPC-UA connection failed: {e}")
            self.status = InstrumentStatus.ERROR
            return False
            
    async def disconnect(self) -> bool:
        """Disconnect from OPC-UA server"""
        try:
            # await self.client.disconnect()
            self.connected = False
            self.status = InstrumentStatus.OFFLINE
            logger.info(f"🔌 OPC-UA disconnected: {self.config.name}")
            return True
        except EngineeringError:
            return False
            
    async def send_command(self, command: InstrumentCommand) -> InstrumentResponse:
        """Send OPC-UA command via method call or variable write"""
        start_time = datetime.now()
        
        try:
            if not self.connected:
                raise Exception("Instrument not connected")
                
            logger.info(f"📤 OPC-UA Command: {command.command} to {self.config.name}")
            
            # Simulate OPC-UA method call or variable write
            await asyncio.sleep(0.3)
            
            # Mock response
            data = {
                "node_id": f"ns={self.namespace};s={command.command}",
                "method_result": "success",
                "output_args": command.parameters
            }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            response = InstrumentResponse(
                instrument_id=command.instrument_id,
                command=command.command,
                status="success",
                data=data,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            
            self.last_response = response
            logger.info(f"✅ OPC-UA response received in {execution_time:.2f}s")
            return response
            
        except BiologyError as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ OPC-UA command failed: {e}")
            
            return InstrumentResponse(
                instrument_id=command.instrument_id,
                command=command.command,
                status="error",
                data=None,
                timestamp=datetime.now(),
                execution_time=execution_time,
                error=str(e)
            )
            
    async def get_status(self) -> InstrumentStatus:
        """Get OPC-UA instrument status"""
        if not self.connected:
            return InstrumentStatus.OFFLINE
        return self.status
        
    async def get_capabilities(self) -> List[str]:
        """Get OPC-UA instrument capabilities"""
        return [
            "ReadValue",
            "WriteValue",
            "CallMethod",
            "Subscribe",
            "Unsubscribe"
        ]

class MQTTDriver(AbstractInstrumentDriver):
    """MQTT (Message Queuing Telemetry Transport) driver"""
    
    def __init__(self, config: InstrumentConfiguration):
        super().__init__(config)
        self.broker_host = config.connection_params.get("broker_host")
        self.broker_port = config.connection_params.get("broker_port", 1883)
        self.username = config.connection_params.get("username")
        self.password = config.connection_params.get("password")
        self.command_topic = config.connection_params.get("command_topic")
        self.response_topic = config.connection_params.get("response_topic")
        self.client = None
        self.response_queue = asyncio.Queue()
        
    async def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            logger.info(f"🔗 Connecting to MQTT instrument: {self.config.name} at {self.broker_host}:{self.broker_port}")
            
            # In real implementation would use aiomqtt or paho-mqtt
            # self.client = mqtt.Client()
            self.client = "mock_mqtt_client"  # Mock for now
            
            if self.username and self.password:
                # self.client.username_pw_set(self.username, self.password)
                pass  # Mock for now
                
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    self.connected = True
                    self.status = InstrumentStatus.IDLE
                    # Subscribe to response topic
                    client.subscribe(self.response_topic)
                    logger.info(f"✅ MQTT connection established: {self.config.name}")
                else:
                    logger.error(f"❌ MQTT connection failed with code {rc}")
                    
            def on_message(client, userdata, msg):
                # Handle response messages
                try:
                    response_data = json.loads(msg.payload.decode())
                    asyncio.create_task(self.response_queue.put(response_data))
                except BiologyError:
                    pass
                    
            # self.client.on_connect = on_connect
            # self.client.on_message = on_message
            
            # Simulate connection
            await asyncio.sleep(0.1)
            self.connected = True
            self.status = InstrumentStatus.IDLE
            
            return True
            
        except BiologyError as e:
            logger.error(f"❌ MQTT connection failed: {e}")
            self.status = InstrumentStatus.ERROR
            return False
            
    async def disconnect(self) -> bool:
        """Disconnect from MQTT broker"""
        try:
            if self.client:
                # self.client.disconnect()
                pass  # Mock for now
            self.connected = False
            self.status = InstrumentStatus.OFFLINE
            logger.info(f"🔌 MQTT disconnected: {self.config.name}")
            return True
        except BiologyError:
            return False
            
    async def send_command(self, command: InstrumentCommand) -> InstrumentResponse:
        """Send MQTT command"""
        start_time = datetime.now()
        
        try:
            if not self.connected:
                raise Exception("Instrument not connected")
                
            logger.info(f"📤 MQTT Command: {command.command} to {self.config.name}")
            
            # Prepare MQTT message (mock implementation)
            # message = {
            #     "command": command.command,
            #     "parameters": command.parameters,
            #     "timestamp": datetime.now().isoformat(),
            #     "id": f"cmd_{int(datetime.now().timestamp())}"
            # }
            
            # Simulate publishing command
            await asyncio.sleep(0.1)
            
            # Wait for response (with timeout)
            try:
                response_data = await asyncio.wait_for(
                    self.response_queue.get(), 
                    timeout=command.timeout
                )
            except asyncio.TimeoutError:
                raise Exception("Command timeout")
                
            execution_time = (datetime.now() - start_time).total_seconds()
            
            response = InstrumentResponse(
                instrument_id=command.instrument_id,
                command=command.command,
                status="success",
                data=response_data,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            
            self.last_response = response
            logger.info(f"✅ MQTT response received in {execution_time:.2f}s")
            return response
            
        except BiologyError as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ MQTT command failed: {e}")
            
            return InstrumentResponse(
                instrument_id=command.instrument_id,
                command=command.command,
                status="error",
                data=None,
                timestamp=datetime.now(),
                execution_time=execution_time,
                error=str(e)
            )
            
    async def get_status(self) -> InstrumentStatus:
        """Get MQTT instrument status"""
        if not self.connected:
            return InstrumentStatus.OFFLINE
        return self.status
        
    async def get_capabilities(self) -> List[str]:
        """Get MQTT instrument capabilities"""
        return [
            "PublishCommand",
            "SubscribeResponse",
            "GetTelemetry",
            "SetParameters"
        ]

class HardwareAbstractionService:
    """
    Main Hardware Abstraction Layer service
    Manages multiple instruments with different protocols
    """
    
    def __init__(self):
        self.instruments: Dict[str, AbstractInstrumentDriver] = {}
        self.command_queue = asyncio.Queue()
        self.response_callbacks: Dict[str, Callable] = {}
        self.running = False
        
        logger.info("🔧 HardwareAbstractionService initialized")
        
    async def register_instrument(self, config: InstrumentConfiguration) -> bool:
        """Register a new instrument"""
        try:
            logger.info(f"📋 Registering instrument: {config.name} ({config.type.value}) via {config.protocol.value}")
            
            # Create appropriate driver based on protocol
            driver = self._create_driver(config)
            
            # Attempt connection
            if await driver.connect():
                self.instruments[config.id] = driver
                logger.info(f"✅ Instrument registered successfully: {config.name}")
                return True
            else:
                logger.error(f"❌ Failed to connect to instrument: {config.name}")
                return False
                
        except BiologyError as e:
            logger.error(f"❌ Error registering instrument {config.name}: {e}")
            return False
            
    def _create_driver(self, config: InstrumentConfiguration) -> AbstractInstrumentDriver:
        """Create appropriate driver for the protocol"""
        protocol_drivers = {
            ConnectionProtocol.SILA2: SiLA2Driver,
            ConnectionProtocol.OPC_UA: OPCUADriver,
            ConnectionProtocol.MQTT: MQTTDriver,
            # Add more drivers as needed
        }
        
        driver_class = protocol_drivers.get(config.protocol)
        if not driver_class:
            raise Exception(f"Unsupported protocol: {config.protocol}")
            
        return driver_class(config)
        
    async def unregister_instrument(self, instrument_id: str) -> bool:
        """Unregister an instrument"""
        try:
            if instrument_id in self.instruments:
                driver = self.instruments[instrument_id]
                await driver.disconnect()
                del self.instruments[instrument_id]
                logger.info(f"📤 Instrument unregistered: {instrument_id}")
                return True
            return False
        except BiologyError as e:
            logger.error(f"❌ Error unregistering instrument {instrument_id}: {e}")
            return False
            
    async def send_command(self, command: InstrumentCommand) -> InstrumentResponse:
        """Send command to specific instrument"""
        try:
            if command.instrument_id not in self.instruments:
                raise Exception(f"Instrument not found: {command.instrument_id}")
                
            driver = self.instruments[command.instrument_id]
            response = await driver.send_command(command)
            
            # Execute callback if provided
            if command.callback:
                try:
                    await command.callback(response)
                except BiologyError as e:
                    logger.error(f"❌ Callback error: {e}")
                    
            return response
            
        except BiologyError as e:
            logger.error(f"❌ Command execution failed: {e}")
            return InstrumentResponse(
                instrument_id=command.instrument_id,
                command=command.command,
                status="error",
                data=None,
                timestamp=datetime.now(),
                execution_time=0.0,
                error=str(e)
            )
            
    async def get_instrument_status(self, instrument_id: str) -> Optional[InstrumentStatus]:
        """Get status of specific instrument"""
        try:
            if instrument_id in self.instruments:
                return await self.instruments[instrument_id].get_status()
            return None
        except BiologyError as e:
            logger.error(f"❌ Error getting status for {instrument_id}: {e}")
            return InstrumentStatus.ERROR
            
    async def get_all_instruments(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered instruments"""
        instruments_info = {}
        
        for instrument_id, driver in self.instruments.items():
            try:
                status = await driver.get_status()
                capabilities = await driver.get_capabilities()
                
                instruments_info[instrument_id] = {
                    "name": driver.config.name,
                    "type": driver.config.type.value,
                    "protocol": driver.config.protocol.value,
                    "status": status.value,
                    "connected": driver.connected,
                    "capabilities": capabilities,
                    "last_response": driver.last_response.timestamp.isoformat() if driver.last_response else None
                }
            except BiologyError as e:
                logger.error(f"❌ Error getting info for {instrument_id}: {e}")
                instruments_info[instrument_id] = {
                    "error": str(e)
                }
                
        return instruments_info
        
    async def start_command_processor(self):
        """Start background command processor"""
        self.running = True
        logger.info("🚀 Command processor started")
        
        while self.running:
            try:
                # Process commands from queue
                command = await asyncio.wait_for(self.command_queue.get(), timeout=1.0)
                await self.send_command(command)
            except asyncio.TimeoutError:
                continue
            except BiologyError as e:
                logger.error(f"❌ Command processor error: {e}")
                
    def stop_command_processor(self):
        """Stop background command processor"""
        self.running = False
        logger.info("⏹️ Command processor stopped")
        
    async def queue_command(self, command: InstrumentCommand):
        """Queue command for background processing"""
        await self.command_queue.put(command)
        
    async def shutdown(self):
        """Shutdown service and disconnect all instruments"""
        logger.info("🛑 Shutting down Hardware Abstraction Service")
        
        self.stop_command_processor()
        
        # Disconnect all instruments
        for instrument_id in list(self.instruments.keys()):
            await self.unregister_instrument(instrument_id)
            
        logger.info("✅ Hardware Abstraction Service shutdown complete")
    
    def check_compatibility(self, equipment: str, experiment_type: str) -> Dict[str, Any]:
        """
        Check hardware compatibility for experiment type
        
        Args:
            equipment: Equipment identifier or type
            experiment_type: Type of experiment to perform
            
        Returns:
            Compatibility information
        """
        # Compatibility mapping
        compatibility_matrix = {
            'spectrometer': ['spectral_analysis', 'material_characterization', 'chemical_analysis'],
            'chromatograph': ['separation', 'chemical_analysis', 'purification'],
            'microscope': ['imaging', 'structural_analysis', 'cell_analysis'],
            'thermocycler': ['pcr', 'dna_amplification', 'thermal_cycling'],
            'plate_reader': ['assay', 'fluorescence', 'absorbance'],
        }
        
        equipment_lower = equipment.lower()
        experiment_lower = experiment_type.lower()
        
        compatible_experiments = []
        for equip, experiments in compatibility_matrix.items():
            if equip in equipment_lower:
                compatible_experiments = experiments
                break
        
        is_compatible = experiment_lower in compatible_experiments
        
        return {
            "success": True,
            "equipment": equipment,
            "experiment_type": experiment_type,
            "is_compatible": is_compatible,
            "compatible_experiments": compatible_experiments,
            "confidence": 0.95 if is_compatible else 0.5
        }

# Global service instance
hardware_service = HardwareAbstractionService()
