"""
Enhanced Health Check Endpoints for AXIOM ATLAS

Provides comprehensive health monitoring endpoints that integrate:
- Database layer health and metrics
- Tool adapter status and circuit breaker state
- Medical imaging system status
- System resource monitoring
- Performance metrics
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, Optional
from datetime import datetime
import time
import psutil
import platform
import asyncio

from app.core.database import get_database_status, init_database
from app.core.database_health import health_checker as db_health_checker
from app.core.logging_config import log_performance, log_security_event
from app.monitoring.health import health_checker
from app.adapters.tool_adapter import get_tool_registry, AdapterStatus
from app.domains.medicine.imaging.medical_imaging_types import MedicalImage, ImageModality
from app.exceptions.domain.physics import QuantumError
from app.types.health_checks_types import (
    HealthCheckResult,
    HealthCheckNoSlashResult,
    DetailedHealthCheckResult,
    DatabaseHealthCheckResult,
    ToolAdaptersHealthCheckResult,
    MedicalImagingHealthCheckResult,
    SystemHealthCheckResult,
    ResetDatabaseHealthResult,
    GetToolAdaptersStatusResult,
    GetMedicalImagingStatusResult,
    GetSystemResourcesResult,
)

router = APIRouter(prefix="/health", tags=["Health Checks"])


@router.get("/",)
async def health_check(request: Request) -> HealthCheckResult:
    """Basic health check endpoint"""
    start_time = time.perf_counter()

    try:
        # Increment request counter
        health_checker.increment_request()

        # Basic system health
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "service": "AXIOM ATLAS",
            "uptime": health_checker.get_application_metrics()["uptime_formatted"],
            "total_requests": health_checker.get_application_metrics()["total_requests"]
        }

        # Log performance
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_performance("health_check", duration_ms, endpoint="/health/")

        return health_status

    except QuantumError as e:
        health_checker.increment_error()
        log_security_event("health_check_error", f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

# Accept "/health" without trailing slash as well
@router.get("", include_in_schema=False)
async def health_check_no_slash(request: Request) -> HealthCheckNoSlashResult:
    return await health_check(request)

@router.get("/detailed")
async def detailed_health_check(request: Request) -> DetailedHealthCheckResult:
    """Comprehensive health check with all system components"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        # Get comprehensive health data
        health_data = health_checker.get_comprehensive_health()

        # Add database status
        try:
            db_status = get_database_status()
            health_data["database"] = db_status
        except QuantumError as e:
            health_data["database"] = {"status": "error", "error": str(e)}

        # Add tool adapters status
        try:
            health_data["tool_adapters"] = get_tool_adapters_status()
        except QuantumError as e:
            health_data["tool_adapters"] = {"status": "error", "error": str(e)}

        # Add medical imaging status
        try:
            health_data["medical_imaging"] = get_medical_imaging_status()
        except QuantumError as e:
            health_data["medical_imaging"] = {"status": "error", "error": str(e)}

        # Add system resources
        health_data["system_resources"] = get_system_resources()

        # Determine overall status
        health_data["overall_status"] = determine_overall_status(health_data)

        # Log performance
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_performance("detailed_health_check", duration_ms, endpoint="/health/detailed")

        return health_data

    except QuantumError as e:
        health_checker.increment_error()
        log_security_event("detailed_health_check_error", f"Detailed health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Detailed health check failed: {str(e)}")


@router.get("/database")
async def database_health_check(request: Request) -> DatabaseHealthCheckResult:
    """Enhanced database health check with comprehensive monitoring"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        # Use our new comprehensive database health checker
        db_health = await db_health_checker.full_health_check()

        # Add metadata
        db_health["timestamp"] = datetime.utcnow().isoformat()
        db_health["health_check_duration_ms"] = (time.perf_counter() - start_time) * 1000
        db_health["endpoint"] = "/health/database"
        db_health["version"] = "2.0.0"

        # Log performance
        log_performance("database_health_check", db_health.get("health_check_duration_ms", 0), endpoint="/health/database")

        return db_health

    except QuantumError as e:
        health_checker.increment_error()
        log_security_event("database_health_check_error", f"Database health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Database health check failed: {str(e)}")


@router.get("/tool-adapters")
async def tool_adapters_health_check(request: Request) -> ToolAdaptersHealthCheckResult:
    """Tool adapters health check"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        adapters_status = get_tool_adapters_status()

        # Add metadata
        adapters_status["timestamp"] = datetime.utcnow().isoformat()
        adapters_status["health_check_duration_ms"] = (time.perf_counter() - start_time) * 1000

        # Log performance
        log_performance("tool_adapters_health_check", adapters_status.get("health_check_duration_ms", 0), endpoint="/health/tool-adapters")

        return adapters_status

    except QuantumError as e:
        health_checker.increment_error()
        log_security_event("tool_adapters_health_check_error", f"Tool adapters health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Tool adapters health check failed: {str(e)}")


@router.get("/medical-imaging")
async def medical_imaging_health_check(request: Request) -> MedicalImagingHealthCheckResult:
    """Medical imaging system health check"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        medical_status = get_medical_imaging_status()

        # Add metadata
        medical_status["timestamp"] = datetime.utcnow().isoformat()
        medical_status["health_check_duration_ms"] = (time.perf_counter() - start_time) * 1000

        # Log performance
        log_performance("medical_imaging_health_check", medical_status.get("health_check_duration_ms", 0), endpoint="/health/medical-imaging")

        return medical_status

    except QuantumError as e:
        health_checker.increment_error()
        log_security_event("medical_imaging_health_check_error", f"Medical imaging health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Medical imaging health check failed: {str(e)}")


@router.get("/system")
async def system_health_check(request: Request) -> SystemHealthCheckResult:
    """System resources health check"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        system_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_resources": get_system_resources(),
            "python_info": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation()
            },
            "health_check_duration_ms": (time.perf_counter() - start_time) * 1000
        }

        # Log performance
        log_performance("system_health_check", system_status.get("health_check_duration_ms", 0), endpoint="/health/system")

        return system_status

    except QuantumError as e:
        health_checker.increment_error()
        log_security_event("system_health_check_error", f"System health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"System health check failed: {str(e)}")


@router.post("/reset-database")
async def reset_database_health(request: Request) -> ResetDatabaseHealthResult:
    """Reset database health status (admin endpoint)"""
    try:
        # Check if request has admin privileges (simplified for demo)
        # In production, this should verify authentication/authorization

        # Reset database health
        from app.core.database import db_health
        db_health.mark_healthy()
        db_health.consecutive_failures = 0

        # Reset metrics
        from app.core.database import db_metrics
        db_metrics.total_connections = 0
        db_metrics.failed_connections = 0

        log_security_event("database_reset", "Database health status reset", action="admin_reset")

        return {
            "status": "success",
            "message": "Database health status reset",
            "timestamp": datetime.utcnow().isoformat()
        }

    except QuantumError as e:
        log_security_event("database_reset_error", f"Failed to reset database health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset database health: {str(e)}")


def get_tool_adapters_status() -> GetToolAdaptersStatusResult:
    """Get status of all tool adapters"""
    try:
        registry = get_tool_registry()
        adapters = registry.list()

        adapter_details = {}
        overall_status = "healthy"

        for name, info in adapters.items():
            # Get adapter instance
            adapter = registry.get(name)
            if adapter:
                adapter_details[name] = {
                    "version": adapter.version,
                    "description": adapter.description,
                    "status": adapter.get_status().value,
                    "circuit_breaker_state": adapter.circuit_breaker._state,
                    "circuit_breaker_failures": adapter.circuit_breaker._failures,
                    "rate_limiter_enabled": adapter.rate_limiter is not None,
                    "cache_enabled": adapter.allow_cache,
                    "supports_async": adapter.supports_async,
                    "last_result": adapter.last_result().dict() if adapter.last_result() else None,
                    "cache_stats": adapter.cache_stats()
                }

                # Determine overall status
                if adapter.get_status() == AdapterStatus.UNHEALTHY:
                    overall_status = "unhealthy"
                elif adapter.get_status() == AdapterStatus.DEGRADED and overall_status == "healthy":
                    overall_status = "degraded"

        return {
            "status": overall_status,
            "total_adapters": len(adapters),
            "adapters": adapter_details
        }

    except QuantumError as e:
        return {
            "status": "error",
            "error": str(e),
            "total_adapters": 0,
            "adapters": {}
        }


def get_medical_imaging_status() -> GetMedicalImagingStatusResult:
    """Get medical imaging system status"""
    try:
        # Test creating a medical image
        test_image = MedicalImage(
            image_id="health_check_test",
            modality=ImageModality.MRI,
            pixel_spacing=(0.5, 0.5),
            slice_thickness=1.0,
            image_dimensions=(256, 256)
        )

        # Test calculations
        pixel_area = test_image.get_pixel_area()
        image_area = test_image.get_image_area()
        volume = test_image.volume

        # Test serialization
        image_dict = test_image.to_dict()

        return {
            "status": "healthy",
            "test_image": {
                "image_id": test_image.image_id,
                "modality": test_image.modality.value,
                "pixel_area": pixel_area,
                "image_area": image_area,
                "volume": volume,
                "is_multiframe": test_image.is_multiframe
            },
            "serialization_test": "passed" if isinstance(image_dict, dict) else "failed",
            "supported_modalities": [modality.value for modality in ImageModality],
            "validation_rules": {
                "pixel_spacing_precision": "6 decimal places",
                "heart_rate_range": "60-100 bpm",
                "slice_thickness_positive": True
            }
        }

    except QuantumError as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "supported_modalities": [],
            "validation_rules": {}
        }


def get_system_resources() -> GetSystemResourcesResult:
    """Get detailed system resource information"""
    try:
        # CPU information
        cpu_info = {
            "count": psutil.cpu_count(),
            "percent": psutil.cpu_percent(interval=1),
            "count_logical": psutil.cpu_count(logical=True),
            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "times": {
                "user": psutil.cpu_times().user,
                "system": psutil.cpu_times().system,
                "idle": psutil.cpu_times().idle
            }
        }

        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free
        }

        # Disk information
        disk = psutil.disk_usage('/')
        disk_info = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }

        # Network information
        network = psutil.net_if_addrs()
        network_info = {
            "interfaces": list(network.keys()),
            "io_counters": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv,
                "packets_sent": psutil.net_io_counters().packets_sent,
                "packets_recv": psutil.net_io_counters().packets_recv
            }
        }

        # Process information
        process = psutil.Process()
        process_info = {
            "pid": process.pid,
            "memory_percent": process.memory_percent(),
            "cpu_percent": process.cpu_percent(),
            "threads": process.num_threads(),
            "connections": len(process.connections())
        }

        return {
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info,
            "network": network_info,
            "process": process_info,
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }

    except QuantumError as e:
        return {
            "status": "error",
            "error": str(e)
        }


def determine_overall_status(health_data: Dict[str, Any]) -> str:
    """Determine overall system health status"""
    # Check database status
    if health_data.get("database", {}).get("status") == "unhealthy":
        return "unhealthy"

    # Check tool adapters status
    if health_data.get("tool_adapters", {}).get("status") == "unhealthy":
        return "unhealthy"

    # Check medical imaging status
    if health_data.get("medical_imaging", {}).get("status") == "unhealthy":
        return "unhealthy"

    # Check system resources
    system = health_data.get("system", {})
    if system.get("cpu_percent", 0) > 95:
        return "warning"

    if system.get("memory", {}).get("percent", 0) > 95:
        return "warning"

    # Check error rate
    if health_data.get("application", {}).get("error_rate", 0) > 15:
        return "degraded"

    # Default to healthy
    return health_data.get("status", "healthy")
