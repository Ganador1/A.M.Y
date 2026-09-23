"""
Earth Sciences Light Router

Router FastAPI ligero para análisis y visualización de datos de ciencias de la tierra.
Proporciona endpoints eficientes para análisis de datos climáticos, procesamiento de señales sísmicas,
estadísticas de corrientes oceánicas y capacidades básicas de visualización 2D.

Este router ofrece una interfaz optimizada para tareas de computación científica que requieren
análisis rápido sin sobrecarga computacional pesada. Todos los endpoints están diseñados
para procesamiento en tiempo real con latencia mínima.

Endpoints disponibles:
- Análisis de series temporales climáticas con detección de eventos extremos
- Análisis de señales sísmicas y computación de densidad espectral de potencia
- Estadísticas de corrientes oceánicas y detección de eddies
- Procesamiento de archivos NetCDF de datos climáticos
- Visualización de mapas de calor 2D y campos vectoriales de corrientes
- Monitoreo de salud del servicio y métricas

El router mantiene un buffer circular de solicitudes recientes para depuración y
monitoreo, con límites de historial configurables.

Dependencias:
- EarthSciencesLightService: Servicio principal de análisis
- matplotlib: Para visualización 2D (opcional, degradación graceful)
- numpy: Para computaciones numéricas
- pydantic: Para validación de solicitudes/respuestas
- prometheus: Para recolección de métricas (opcional)

Uso típico:
    Todos los endpoints aceptan solicitudes JSON y retornan resultados de análisis estructurados.
    Los endpoints de visualización retornan imágenes PNG codificadas en base64 para integración web.
    Los endpoints basados en archivos soportan formato NetCDF para datos climáticos.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from contextlib import suppress
import aiofiles

from app.services.earth_sciences_light_service import EarthSciencesLightService
from app.observability import metrics as prom
from app.core.config import settings
from app.exceptions.domain.biology import BiologyError
from app.types.earth_sciences_light_types import (
    ClimateTimeseriesResult,
    SeismicAnalysisResult,
    OceanStatsResult,
    ClimateFromFileResult,
    SeismicPsdResult,
    DetectEddies2dResult,
    MapHeatResult,
    MapCurrentsResult,
    MapHeatCurrentsResult,
    EarthLightHistoryResult,
    EarthLightHealthResult,
    EarthLightMetricsResult,
)


router = APIRouter(prefix="/api/earth-light", tags=["earth-sciences"])
_HISTORY: list[dict] = []
_HISTORY_LIMIT = 50


class ClimateSeriesRequest(BaseModel):
    times: List[str] = Field(..., description="Fechas/tiempos en orden (ISO o etiqueta)")
    temps_c: List[float] = Field(..., description="Temperaturas en °C, mismo tamaño que times")
    threshold_extreme: Optional[float] = Field(None, description="Umbral absoluto para extremos, si no se define usa mean+2*std")


@router.post("/climate-timeseries")
async def climate_timeseries(req: ClimateSeriesRequest) -> ClimateTimeseriesResult:
    svc = EarthSciencesLightService()
    if not req.times or not req.temps_c or len(req.times) != len(req.temps_c):
        return {"error": "times y temps_c deben existir y tener la misma longitud"}
    if len(req.times) < 2:
        return {"error": "Se requieren al menos 2 puntos"}
    res = await svc.analyze_temperature_timeseries(req.times, req.temps_c, req.threshold_extreme)
    if getattr(settings, 'enable_prom_service_metrics', False):
        with suppress(Exception):
            prom.inc("earth_light_requests_total", labels={"endpoint": "climate_timeseries"})
            prom.observe("earth_light_series_len", res.get("n_points", 0))
    with suppress(Exception):
        _HISTORY.append({"endpoint": "climate_timeseries", "n_points": res.get("n_points"), "extreme_events": res.get("extreme_events")})
        if len(_HISTORY) > _HISTORY_LIMIT:
            del _HISTORY[: len(_HISTORY) - _HISTORY_LIMIT]
    return res


class SeismicRequest(BaseModel):
    samples: List[float]
    sampling_rate_hz: float = 100.0


@router.post("/seismic-analysis")
async def seismic_analysis(req: SeismicRequest) -> SeismicAnalysisResult:
    svc = EarthSciencesLightService()
    if req.sampling_rate_hz <= 0 or req.sampling_rate_hz > 10000:
        return {"error": "sampling_rate_hz debe estar en (0, 10000]"}
    if not req.samples or len(req.samples) < 4:
        return {"error": "Se requieren >=4 muestras"}
    res = await svc.analyze_seismic_signal(req.samples, req.sampling_rate_hz)
    if getattr(settings, 'enable_prom_service_metrics', False):
        with suppress(Exception):
            prom.inc("earth_light_requests_total", labels={"endpoint": "seismic_analysis"})
            prom.observe("earth_light_seismic_len", len(req.samples))
    with suppress(Exception):
        _HISTORY.append({"endpoint": "seismic_analysis", "n_samples": len(req.samples)})
        if len(_HISTORY) > _HISTORY_LIMIT:
            del _HISTORY[: len(_HISTORY) - _HISTORY_LIMIT]
    return res


class OceanRequest(BaseModel):
    u: List[float]
    v: List[float]


@router.post("/ocean-stats")
async def ocean_stats(req: OceanRequest) -> OceanStatsResult:
    svc = EarthSciencesLightService()
    if not req.u or not req.v or len(req.u) != len(req.v):
        return {"error": "u y v deben existir y tener la misma longitud"}
    if len(req.u) < 2:
        return {"error": "Se requieren >=2 puntos"}
    res = await svc.ocean_current_stats(req.u, req.v)
    if getattr(settings, 'enable_prom_service_metrics', False):
        with suppress(Exception):
            prom.inc("earth_light_requests_total", labels={"endpoint": "ocean_stats"})
    with suppress(Exception):
        _HISTORY.append({"endpoint": "ocean_stats", "n_points": len(req.u)})
        if len(_HISTORY) > _HISTORY_LIMIT:
            del _HISTORY[: len(_HISTORY) - _HISTORY_LIMIT]
    return res


class ClimateFileRequest(BaseModel):
    filepath: str
    var_name: str = 'tas'


@router.post("/climate-file")
async def climate_from_file(req: ClimateFileRequest) -> ClimateFromFileResult:
    svc = EarthSciencesLightService()
    if not req.filepath:
        return {"error": "filepath requerido"}
    res = await svc.analyze_temperature_netcdf(req.filepath, req.var_name)
    if getattr(settings, 'enable_prom_service_metrics', False):
        with suppress(Exception):
            prom.inc("earth_light_requests_total", labels={"endpoint": "climate_file"})
    with suppress(Exception):
        _HISTORY.append({"endpoint": "climate_file", "filepath": req.filepath})
        if len(_HISTORY) > _HISTORY_LIMIT:
            del _HISTORY[: len(_HISTORY) - _HISTORY_LIMIT]
    return res


class SeismicPSDRequest(BaseModel):
    samples: List[float]
    sampling_rate_hz: float = 100.0
    nperseg: int = 512


@router.post("/seismic-psd")
async def seismic_psd(req: SeismicPSDRequest) -> SeismicPsdResult:
    svc = EarthSciencesLightService()
    if not req.samples or len(req.samples) < 8:
        return {"error": "Se requieren >=8 muestras"}
    if req.sampling_rate_hz <= 0 or req.sampling_rate_hz > 10000:
        return {"error": "sampling_rate_hz debe estar en (0, 10000]"}
    if req.nperseg <= 0:
        return {"error": "nperseg debe ser > 0"}
    res = await svc.seismic_psd(req.samples, req.sampling_rate_hz, req.nperseg)
    if getattr(settings, 'enable_prom_service_metrics', False):
        with suppress(Exception):
            prom.inc("earth_light_requests_total", labels={"endpoint": "seismic_psd"})
    with suppress(Exception):
        _HISTORY.append({"endpoint": "seismic_psd", "n_samples": len(req.samples), "nperseg": req.nperseg})
        if len(_HISTORY) > _HISTORY_LIMIT:
            del _HISTORY[: len(_HISTORY) - _HISTORY_LIMIT]
    return res


class Eddy2DRequest(BaseModel):
    grid: List[List[float]]
    threshold: float = 0.05


@router.post("/eddies-2d")
async def detect_eddies_2d(req: Eddy2DRequest) -> DetectEddies2dResult:
    svc = EarthSciencesLightService()
    if not req.grid or not isinstance(req.grid, list) or not isinstance(req.grid[0], list):
        return {"error": "grid debe ser matriz 2D"}
    if len(req.grid) < 2 or len(req.grid[0]) < 2:
        return {"error": "grid demasiado pequeño (>=2x2)"}
    if req.threshold <= 0:
        return {"error": "threshold debe ser > 0"}
    res = await svc.detect_eddies_2d(req.grid, req.threshold)
    if getattr(settings, 'enable_prom_service_metrics', False):
        with suppress(Exception):
            prom.inc("earth_light_requests_total", labels={"endpoint": "eddies_2d"})
    with suppress(Exception):
        _HISTORY.append({"endpoint": "eddies_2d", "threshold": req.threshold})
        if len(_HISTORY) > _HISTORY_LIMIT:
            del _HISTORY[: len(_HISTORY) - _HISTORY_LIMIT]
    return res


class HeatMapRequest(BaseModel):
    grid: List[List[float]]
    cmap: str = Field("viridis", description="Colormap de matplotlib")
    title: str | None = Field(None, description="Título opcional")
    save: bool = Field(False, description="Guardar PNG si EARTH_EXPORT_DIR está configurado")
    filename: str | None = Field(None, description="Nombre de archivo opcional")


@router.post("/map-heat")
async def map_heat(req: HeatMapRequest) -> MapHeatResult:
    """Genera un heatmap base64 PNG desde una grilla 2D (visualización ligera)."""
    try:
        import io
        import base64
        import numpy as np
        try:
            import matplotlib
            matplotlib.use('Agg')  # backend sin pantalla
            import matplotlib.pyplot as plt
        except BiologyError as e:
            return {"error": f"matplotlib no disponible: {e}"}

        arr = np.array(req.grid, dtype=float)
        if arr.ndim != 2 or arr.size == 0:
            return {"error": "grid inválido (se espera matriz 2D no vacía)"}
        if arr.shape[0] * arr.shape[1] > 2000 * 2000:
            return {"error": "grid demasiado grande (máx 4M celdas)"}

        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        im = ax.imshow(arr, cmap=req.cmap, origin='lower', aspect='auto')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        if req.title:
            ax.set_title(req.title)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='png')
        plt.close(fig)
        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        saved_path = None
        export_dir = getattr(settings, 'earth_export_dir', None)
        if req.save and export_dir:
            with suppress(Exception):
                import os
                os.makedirs(export_dir, exist_ok=True)
                fname = req.filename or f"heat_{int(np.abs(arr).mean()*1000)}.png"
                out_path = os.path.join(export_dir, fname)
                with aiofiles.open(out_path, 'wb') as f:
                    f.write(buf.getvalue())
                saved_path = out_path

        if getattr(settings, 'enable_prom_service_metrics', False):
            with suppress(Exception):
                prom.inc("earth_light_requests_total", labels={"endpoint": "map_heat"})

        with suppress(Exception):
            _HISTORY.append({"endpoint": "map_heat", "shape": list(arr.shape), "saved": bool(saved_path)})
            if len(_HISTORY) > _HISTORY_LIMIT:
                del _HISTORY[: len(_HISTORY) - _HISTORY_LIMIT]
        return {"image_base64_png": img_b64, "shape": arr.shape, "saved_path": saved_path}
    except BiologyError as e:
        return {"error": str(e)}


class CurrentsMapRequest(BaseModel):
    u: List[List[float]]
    v: List[List[float]]
    step: int = Field(1, ge=1, description="Submuestreo de flechas (cada N puntos)")
    scale: float = Field(1.0, gt=0, description="Escala de flechas")
    title: str | None = None
    save: bool = Field(False, description="Guardar PNG si EARTH_EXPORT_DIR está configurado")
    filename: str | None = None


@router.post("/map-currents")
async def map_currents(req: CurrentsMapRequest) -> MapCurrentsResult:
    """Genera un mapa quiver (corrientes) en PNG base64 (visualización ligera)."""
    try:
        import io
        import base64
        import numpy as np
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
        except BiologyError as e:
            return {"error": f"matplotlib no disponible: {e}"}

        U = np.array(req.u, dtype=float)
        V = np.array(req.v, dtype=float)
        if U.shape != V.shape or U.ndim != 2 or U.size == 0:
            return {"error": "u y v deben ser matrices 2D no vacías y del mismo tamaño"}
        if U.shape[0] * U.shape[1] > 2000 * 2000:
            return {"error": "matrices demasiado grandes (máx 4M celdas)"}

        ny, nx = U.shape
        y = np.arange(ny)
        x = np.arange(nx)
        X, Y = np.meshgrid(x, y)

        s = max(1, int(req.step))
        Xs, Ys, Us, Vs = X[::s, ::s], Y[::s, ::s], U[::s, ::s], V[::s, ::s]

        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        ax.quiver(Xs, Ys, Us, Vs, scale_units='xy', scale=1.0/req.scale)
        if req.title:
            ax.set_title(req.title)
        ax.set_xlim(-0.5, nx - 0.5)
        ax.set_ylim(-0.5, ny - 0.5)
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='png')
        plt.close(fig)
        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        saved_path = None
        export_dir = getattr(settings, 'earth_export_dir', None)
        if req.save and export_dir:
            with suppress(Exception):
                import os
                os.makedirs(export_dir, exist_ok=True)
                fname = req.filename or f"currents_{int(np.hypot(Us, Vs).mean()*1000)}.png"
                out_path = os.path.join(export_dir, fname)
                with aiofiles.open(out_path, 'wb') as f:
                    f.write(buf.getvalue())
                saved_path = out_path

        if getattr(settings, 'enable_prom_service_metrics', False):
            with suppress(Exception):
                prom.inc("earth_light_requests_total", labels={"endpoint": "map_currents"})

        with suppress(Exception):
            _HISTORY.append({"endpoint": "map_currents", "shape": [int(ny), int(nx)], "saved": bool(saved_path)})
            if len(_HISTORY) > _HISTORY_LIMIT:
                del _HISTORY[: len(_HISTORY) - _HISTORY_LIMIT]
        return {"image_base64_png": img_b64, "shape": [int(ny), int(nx)], "step": s, "saved_path": saved_path}
    except BiologyError as e:
        return {"error": str(e)}


class HeatCurrentsRequest(BaseModel):
    grid: List[List[float]]
    u: List[List[float]]
    v: List[List[float]]
    cmap: str = Field("viridis")
    step: int = Field(1, ge=1)
    scale: float = Field(1.0, gt=0)
    title: str | None = None
    save: bool = Field(False)
    filename: str | None = None


@router.post("/map-heat-currents")
async def map_heat_currents(req: HeatCurrentsRequest) -> MapHeatCurrentsResult:
    """Genera una figura combinada (heatmap + quiver) y devuelve PNG base64.
    - grid: matriz 2D para heatmap
    - u, v: matrices 2D del mismo tamaño para corrientes
    """
    try:
        import io
        import base64
        import numpy as np
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
        except BiologyError as e:
            return {"error": f"matplotlib no disponible: {e}"}

        arr = np.array(req.grid, dtype=float)
        U = np.array(req.u, dtype=float)
        V = np.array(req.v, dtype=float)
        if arr.ndim != 2 or U.ndim != 2 or V.ndim != 2:
            return {"error": "grid, u y v deben ser 2D"}
        if U.shape != V.shape or U.shape != arr.shape:
            return {"error": "grid, u y v deben tener el mismo shape"}
        if arr.size == 0:
            return {"error": "matrices vacías"}
        if arr.shape[0] * arr.shape[1] > 2000 * 2000:
            return {"error": "matrices demasiado grandes (máx 4M celdas)"}

        ny, nx = U.shape
        y = np.arange(ny)
        x = np.arange(nx)
        X, Y = np.meshgrid(x, y)
        s = max(1, int(req.step))
        Xs, Ys, Us, Vs = X[::s, ::s], Y[::s, ::s], U[::s, ::s], V[::s, ::s]

        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        im = ax.imshow(arr, cmap=req.cmap, origin='lower', aspect='auto')
        q = ax.quiver(Xs, Ys, Us, Vs, color='white', scale_units='xy', scale=1.0/req.scale, width=0.0025)
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        if req.title:
            ax.set_title(req.title)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='png')
        plt.close(fig)
        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        saved_path = None
        export_dir = getattr(settings, 'earth_export_dir', None)
        if req.save and export_dir:
            from contextlib import suppress as _s
            with _s(Exception):
                import os as _os
                _os.makedirs(export_dir, exist_ok=True)
                fname = req.filename or f"heat_currents_{int(np.hypot(Us, Vs).mean()*1000)}.png"
                out_path = _os.path.join(export_dir, fname)
                with aiofiles.open(out_path, 'wb') as f:
                    f.write(buf.getvalue())
                saved_path = out_path

        if getattr(settings, 'enable_prom_service_metrics', False):
            from contextlib import suppress as _s
            with _s(Exception):
                prom.inc("earth_light_requests_total", labels={"endpoint": "map_heat_currents"})

        from contextlib import suppress as _s
        with _s(Exception):
            _HISTORY.append({"endpoint": "map_heat_currents", "shape": [int(ny), int(nx)], "saved": bool(saved_path)})
            if len(_HISTORY) > _HISTORY_LIMIT:
                del _HISTORY[: len(_HISTORY) - _HISTORY_LIMIT]
        return {"image_base64_png": img_b64, "shape": [int(ny), int(nx)], "step": s, "saved_path": saved_path}
    except BiologyError as e:
        return {"error": str(e)}


@router.get("/history")
async def earth_light_history() -> EarthLightHistoryResult:
    """Devuelve las últimas N solicitudes procesadas (buffer circular)."""
    return {"history_len": len(_HISTORY), "items": _HISTORY}


@router.get("/health")
async def earth_light_health() -> EarthLightHealthResult:
    """Health check ligero del servicio Earth Sciences Light"""
    svc = EarthSciencesLightService()
    # Sonda mínima: tiempos/temperaturas cortos
    times = ["t0", "t1", "t2", "t3"]
    temps = [15.0, 15.1, 15.3, 15.2]
    res = await svc.analyze_temperature_timeseries(times, temps)
    return {
        "service": "EarthSciencesLightService",
        "status": "healthy" if "trend_per_step_c" in res else "degraded",
        "n_points": res.get("n_points"),
        "extreme_events": res.get("extreme_events")
    }


@router.get("/metrics")
async def earth_light_metrics() -> EarthLightMetricsResult:
    """Métricas ligeras (dummy) del servicio Earth Sciences Light"""
    return {
        "service": "EarthSciencesLightService",
        "version": "light-1.0",
        "capabilities": [
            "climate_timeseries",
            "climate_file_netcdf",
            "seismic_analysis",
            "seismic_psd",
            "ocean_stats",
            "eddies_2d"
        ]
    }


