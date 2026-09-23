"""
Metrics and Monitoring Endpoints for AXIOM ATLAS

Provides endpoints for:
- Prometheus metrics export
- Custom metrics in JSON format
- System performance metrics
- Health status integration
- Metrics collection control

SECURITY: All metrics endpoints require admin authentication or IP allowlist.
Public access can expose sensitive system information.
"""

from fastapi import APIRouter, HTTPException, Response, Request, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import time

from app.core.metrics import (
    metrics,
    get_system_metrics,
    export_metrics_to_file,
    print_metrics_summary
)
from app.core.logging_config import log_performance, log_security_event
from app.monitoring.health import health_checker
from app.security.auth import require_scopes
from app.types.metrics_types import (
    GetMetricsResult,
    GetSystemMetricsEndpointResult,
    GetDatabaseMetricsResult,
    GetToolAdaptersMetricsResult,
    GetMedicalImagingMetricsResult,
    ExportMetricsResult,
    GetMetricsSummaryResult,
    GetHealthWithMetricsResult,
    GetPerformanceMetricsResult,
    ResetMetricsResult,
)

router = APIRouter(
    prefix="/metrics", 
    tags=["Metrics"],
    dependencies=[Depends(require_scopes(["system:admin", "metrics:read"]))]  # Require admin or metrics read scope
)


@router.get("/")
async def get_metrics(request: Request) -> GetMetricsResult:
    """Get custom metrics in JSON format"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        # Get metrics
        custom_metrics = metrics.get_custom_metrics()
        system_metrics = get_system_metrics()

        response_data = {
            **custom_metrics,
            "system_detailed": system_metrics
        }

        # Log performance
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_performance("metrics_collection", duration_ms, endpoint="/metrics/")

        return response_data

    except Exception as e:
        health_checker.increment_error()
        log_security_event("metrics_collection_error", f"Failed to collect metrics: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Metrics collection failed: {str(e)}")


@router.get("/prometheus")
async def get_prometheus_metrics(request: Request) -> Response:
    """Get metrics in Prometheus format"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        # Get Prometheus metrics
        prometheus_data = metrics.get_metrics_text()

        # Log performance
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_performance("prometheus_metrics", duration_ms, endpoint="/metrics/prometheus")

        return Response(
            content=prometheus_data,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )

    except Exception as e:
        health_checker.increment_error()
        log_security_event("prometheus_metrics_error", f"Failed to get Prometheus metrics: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Prometheus metrics failed: {str(e)}")


@router.get("/system")
async def get_system_metrics_endpoint(request: Request) -> GetSystemMetricsEndpointResult:
    """Get detailed system metrics"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        system_metrics = get_system_metrics()

        # Add additional system info
        system_metrics["timestamp"] = time.time()
        system_metrics["health_check_duration_ms"] = (time.perf_counter() - start_time) * 1000

        # Log performance
        log_performance("system_metrics", system_metrics["health_check_duration_ms"], endpoint="/metrics/system")

        return system_metrics

    except Exception as e:
        health_checker.increment_error()
        log_security_event("system_metrics_error", f"Failed to get system metrics: {str(e)}")
        raise HTTPException(status_code=503, detail=f"System metrics failed: {str(e)}")


@router.get("/database")
async def get_database_metrics(request: Request) -> GetDatabaseMetricsResult:
    """Get database-specific metrics"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        # Get database status
        from app.core.database import get_database_status
        db_status = get_database_status()

        # Add metrics collection timestamp
        db_status["metrics_collection_timestamp"] = time.time()
        db_status["metrics_collection_duration_ms"] = (time.perf_counter() - start_time) * 1000

        # Log performance
        log_performance("database_metrics", db_status["metrics_collection_duration_ms"], endpoint="/metrics/database")

        return db_status

    except Exception as e:
        health_checker.increment_error()
        log_security_event("database_metrics_error", f"Failed to get database metrics: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Database metrics failed: {str(e)}")


@router.get("/tool-adapters")
async def get_tool_adapters_metrics(request: Request) -> GetToolAdaptersMetricsResult:
    """Get tool adapters metrics"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        # Get tool adapters status
        from app.routers.health_checks import get_tool_adapters_status
        adapters_status = get_tool_adapters_status()

        # Add metrics collection timestamp
        adapters_status["metrics_collection_timestamp"] = time.time()
        adapters_status["metrics_collection_duration_ms"] = (time.perf_counter() - start_time) * 1000

        # Log performance
        log_performance("tool_adapters_metrics", adapters_status["metrics_collection_duration_ms"], endpoint="/metrics/tool-adapters")

        return adapters_status

    except Exception as e:
        health_checker.increment_error()
        log_security_event("tool_adapters_metrics_error", f"Failed to get tool adapters metrics: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Tool adapters metrics failed: {str(e)}")


@router.get("/medical-imaging")
async def get_medical_imaging_metrics(request: Request) -> GetMedicalImagingMetricsResult:
    """Get medical imaging metrics"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        # Get medical imaging status
        from app.routers.health_checks import get_medical_imaging_status
        medical_status = get_medical_imaging_status()

        # Add metrics collection timestamp
        medical_status["metrics_collection_timestamp"] = time.time()
        medical_status["metrics_collection_duration_ms"] = (time.perf_counter() - start_time) * 1000

        # Log performance
        log_performance("medical_imaging_metrics", medical_status["metrics_collection_duration_ms"], endpoint="/metrics/medical-imaging")

        return medical_status

    except Exception as e:
        health_checker.increment_error()
        log_security_event("medical_imaging_metrics_error", f"Failed to get medical imaging metrics: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Medical imaging metrics failed: {str(e)}")


@router.post("/export")
async def export_metrics(request: Request, filename: Optional[str] = None) -> ExportMetricsResult:
    """Export metrics to JSON file"""
    try:
        health_checker.increment_request()

        # Use provided filename or default
        if not filename:
            filename = f"metrics_export_{int(time.time())}.json"

        # Export metrics
        export_metrics_to_file(filename)

        log_security_event("metrics_export", f"Metrics exported to {filename}")

        return {
            "status": "success",
            "message": f"Metrics exported to {filename}",
            "timestamp": time.time(),
            "filename": filename
        }

    except Exception as e:
        health_checker.increment_error()
        log_security_event("metrics_export_error", f"Failed to export metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Metrics export failed: {str(e)}")


@router.get("/summary")
async def get_metrics_summary(request: Request) -> GetMetricsSummaryResult:
    """Get a human-readable summary of current metrics"""
    try:
        health_checker.increment_request()

        # Get metrics
        custom_metrics = metrics.get_custom_metrics()

        # Create summary
        summary = {
            "timestamp": custom_metrics["timestamp"],
            "summary": {
                "system_health": "healthy" if custom_metrics["system"]["cpu"]["percent"] < 80 else "warning",
                "database_connections": custom_metrics["database"]["connections_total"],
                "database_failures": custom_metrics["database"]["connection_failures"],
                "tool_adapter_executions": custom_metrics["tool_adapters"]["executions_total"],
                "api_requests": custom_metrics["api"]["requests_total"],
                "active_connections": custom_metrics["system"]["active_connections"]
            },
            "alerts": []
        }

        # Generate alerts
        if custom_metrics["system"]["cpu"]["percent"] > 90:
            summary["alerts"].append({
                "level": "critical",
                "message": f"High CPU usage: {custom_metrics['system']['cpu']['percent']}%",
                "metric": "cpu_usage"
            })

        if custom_metrics["system"]["memory"]["percent"] > 90:
            summary["alerts"].append({
                "level": "critical",
                "message": f"High memory usage: {custom_metrics['system']['memory']['percent']}%",
                "metric": "memory_usage"
            })

        if custom_metrics["database"]["connection_failures"] > 0:
            failure_rate = (custom_metrics["database"]["connection_failures"] /
                          max(custom_metrics["database"]["connections_total"], 1)) * 100
            if failure_rate > 10:
                summary["alerts"].append({
                    "level": "warning",
                    "message": f"High database connection failure rate: {failure_rate:.2f}%",
                    "metric": "db_failure_rate"
                })

        return summary

    except Exception as e:
        health_checker.increment_error()
        log_security_event("metrics_summary_error", f"Failed to get metrics summary: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Metrics summary failed: {str(e)}")


@router.get("/health-integration")
async def get_health_with_metrics(request: Request) -> GetHealthWithMetricsResult:
    """Get health status integrated with metrics"""
    start_time = time.perf_counter()

    try:
        health_checker.increment_request()

        # Get comprehensive health data
        health_data = health_checker.get_comprehensive_health()

        # Add metrics data
        try:
            custom_metrics = metrics.get_custom_metrics()
            health_data["metrics"] = {
                "system": custom_metrics["system"],
                "database": custom_metrics["database"],
                "tool_adapters": custom_metrics["tool_adapters"],
                "api": custom_metrics["api"]
            }
        except Exception as e:
            health_data["metrics"] = {"error": str(e)}

        # Add metrics collection timestamp
        health_data["metrics_collection_timestamp"] = time.time()
        health_data["metrics_collection_duration_ms"] = (time.perf_counter() - start_time) * 1000

        # Log performance
        log_performance("health_with_metrics", health_data["metrics_collection_duration_ms"], endpoint="/metrics/health-integration")

        return health_data

    except Exception as e:
        health_checker.increment_error()
        log_security_event("health_metrics_integration_error", f"Failed to get health with metrics: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Health metrics integration failed: {str(e)}")


@router.get("/performance")
async def get_performance_metrics(request: Request) -> GetPerformanceMetricsResult:
    """Get performance-specific metrics"""
    try:
        health_checker.increment_request()

        # Get Prometheus metrics text
        prometheus_data = metrics.get_metrics_text()

        # Parse performance metrics
        performance_data = {
            "timestamp": time.time(),
            "prometheus_metrics": prometheus_data,
            "custom_performance": {
                "database_query_times": "histogram: axiom_db_query_duration_seconds",
                "api_response_times": "histogram: axiom_api_request_duration_seconds",
                "tool_adapter_times": "histogram: axiom_adapter_execution_duration_seconds",
                "system_resources": {
                    "cpu": "gauge: axiom_cpu_usage_percent",
                    "memory": "gauge: axiom_memory_usage_percent",
                    "disk": "gauge: axiom_disk_usage_percent"
                }
            }
        }

        return performance_data

    except Exception as e:
        health_checker.increment_error()
        log_security_event("performance_metrics_error", f"Failed to get performance metrics: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Performance metrics failed: {str(e)}")


@router.post("/reset")
async def reset_metrics(request: Request) -> ResetMetricsResult:
    """Reset all metrics (admin endpoint)"""
    try:
        health_checker.increment_request()

        # This would need to be implemented in the MetricsCollector class
        # For now, just log the action
        log_security_event("metrics_reset", "Metrics reset requested", action="admin_reset")

        return {
            "status": "success",
            "message": "Metrics reset requested (implementation pending)",
            "timestamp": time.time()
        }

    except Exception as e:
        health_checker.increment_error()
        log_security_event("metrics_reset_error", f"Failed to reset metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Metrics reset failed: {str(e)}")
