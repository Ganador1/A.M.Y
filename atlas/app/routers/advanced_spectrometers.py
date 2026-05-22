"""
Advanced Spectrometers Router

Este módulo proporciona endpoints para control y análisis avanzado de espectrómetros científicos,
incluyendo espectroscopia NMR, espectrometría de masas, UV-Vis, IR, Raman, fluorescencia,
dicrorismo circular y XPS. Soporta escaneo automatizado, análisis de espectros, calibración
y procesamiento por lotes para investigación científica de alto rendimiento.

Capacidades principales:
- Control multi-espectrómetro con parámetros configurables
- Escaneo automatizado con modos continuo, paso a paso y alta resolución
- Análisis de espectros con detección de picos y corrección de baseline
- Procesamiento por lotes para screening de alto rendimiento
- Calibración automática y validación de instrumentos
- Historial completo de escaneos y análisis
- Soporte para múltiples tipos de espectroscopía
- Control de calidad y evaluación de ruido

Endpoints disponibles:
- GET /spectrometers: Lista de espectrómetros disponibles
- GET /spectrometers/{name}: Información detallada de espectrómetro
- POST /scan: Realizar escaneo de espectrómetro
- POST /analyze-spectrum: Analizar espectro
- POST /batch-scan: Escaneo por lotes
- POST /calibrate: Calibrar espectrómetro
- GET /scan-history/{name}: Historial de escaneos
- GET /spectrometer-types: Tipos de espectrómetros disponibles
- GET /scan-modes: Modos de escaneo disponibles
- GET /health: Verificación del estado del servicio

Dependencias:
- AdvancedSpectrometers: Servicio principal de espectrómetros
- ScanParametersModel: Parámetros de escaneo
- ScanRequest: Solicitud de escaneo individual
- SpectrumAnalysisRequest: Solicitud de análisis de espectro
- BatchScanRequest: Solicitud de escaneo por lotes
- CalibrationRequest: Solicitud de calibración

Uso típico:
    from app.domains.chemistry.services.advanced_spectrometers import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles bajo el prefijo /api/v1/advanced-spectrometers
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Tuple

from app.core.bootstrap_logging import logger
from app.domains.chemistry.services.advanced_spectrometers import AdvancedSpectrometers
from app.security import require_scopes
from app.exceptions.domain.biology import BiologyError

router = APIRouter(
    prefix="/api/v1/advanced-spectrometers",
    tags=["Advanced Spectrometers"],
    dependencies=[Depends(require_scopes(["lab-equipment"]))]
)
advanced_spectrometers_router = router


class ScanParametersModel(BaseModel):
    """Scan parameters for spectrometer"""
    wavelength_start: float = Field(..., description="Start wavelength")
    wavelength_end: float = Field(..., description="End wavelength")
    scan_speed: float = Field(default=1.0, description="Scan speed")
    resolution: float = Field(default=1.0, description="Resolution")
    scan_mode: str = Field(default="continuous", description="Scan mode")
    integration_time: float = Field(default=1.0, description="Integration time")
    number_of_scans: int = Field(default=1, description="Number of scans")
    temperature: Optional[float] = Field(default=None, description="Temperature")
    pressure: Optional[float] = Field(default=None, description="Pressure")


class ScanRequest(BaseModel):
    """Request model for spectrometer scan"""
    spectrometer_name: str = Field(..., description="Spectrometer name")
    scan_parameters: ScanParametersModel = Field(..., description="Scan parameters")
    sample_info: Dict[str, Any] = Field(default_factory=dict, description="Sample information")


class SpectrumAnalysisRequest(BaseModel):
    """Request model for spectrum analysis"""
    spectrum_data: Dict[str, Any] = Field(..., description="Spectrum data")
    analysis_type: str = Field(default="peak_detection", description="Analysis type")


class BatchScanRequest(BaseModel):
    """Request model for batch scanning"""
    spectrometer_name: str = Field(..., description="Spectrometer name")
    scan_requests: List[Dict[str, Any]] = Field(..., description="List of scan requests")


class CalibrationRequest(BaseModel):
    """Request model for spectrometer calibration"""
    spectrometer_name: str = Field(..., description="Spectrometer name")
    calibration_type: str = Field(default="standard", description="Calibration type")


# Initialize advanced spectrometers service
advanced_spectrometers = AdvancedSpectrometers()


@router.get("/spectrometers", summary="List Available Spectrometers")
async def list_spectrometers(spectrometer_type: Optional[str] = None):
    """
    List all available spectrometers or filter by type.
    
    Supported spectrometer types:
    - nmr: Nuclear Magnetic Resonance
    - mass_spec: Mass Spectrometry
    - uv_vis: UV-Visible Spectroscopy
    - ir: Infrared Spectroscopy
    - raman: Raman Spectroscopy
    - fluorescence: Fluorescence Spectroscopy
    - cd: Circular Dichroism
    - xps: X-ray Photoelectron Spectroscopy
    """
    try:
        result = await advanced_spectrometers.list_spectrometers({
            "action": "list_spectrometers",
            "spectrometer_type": spectrometer_type
        })
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error listing spectrometers: {e}")
        raise HTTPException(status_code=500, detail=f"Spectrometer listing failed: {str(e)}")


@router.get("/spectrometers/{spectrometer_name}", summary="Get Spectrometer Information")
async def get_spectrometer_info(spectrometer_name: str):
    """
    Get detailed information about a specific spectrometer.
    
    Returns specifications, capabilities, and status information.
    """
    try:
        result = await advanced_spectrometers.get_spectrometer_info({
            "action": "get_spectrometer_info",
            "spectrometer_name": spectrometer_name
        })
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error getting spectrometer info: {e}")
        raise HTTPException(status_code=500, detail=f"Spectrometer info retrieval failed: {str(e)}")


@router.post("/scan", summary="Perform Spectrometer Scan")
async def perform_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Perform a spectrometer scan with specified parameters.
    
    This endpoint simulates realistic spectrometer scans including:
    - Parameter validation
    - Realistic spectrum generation
    - Quality assessment
    - Metadata collection
    """
    try:
        result = await advanced_spectrometers.perform_scan({
            "action": "perform_scan",
            "spectrometer_name": request.spectrometer_name,
            "scan_parameters": request.scan_parameters.dict(),
            "sample_info": request.sample_info
        })
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error performing scan: {e}")
        raise HTTPException(status_code=500, detail=f"Spectrometer scan failed: {str(e)}")


@router.post("/analyze-spectrum", summary="Analyze Spectrum")
async def analyze_spectrum(request: SpectrumAnalysisRequest):
    """
    Analyze a spectrum for peaks, features, and interpretation.
    
    Analysis types include:
    - peak_detection: Detect and characterize peaks
    - baseline_correction: Correct baseline drift
    - noise_analysis: Analyze noise characteristics
    - quantitative_analysis: Perform quantitative measurements
    """
    try:
        result = await advanced_spectrometers.analyze_spectrum({
            "action": "analyze_spectrum",
            "spectrum_data": request.spectrum_data,
            "analysis_type": request.analysis_type
        })
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error analyzing spectrum: {e}")
        raise HTTPException(status_code=500, detail=f"Spectrum analysis failed: {str(e)}")


@router.post("/batch-scan", summary="Perform Batch Scanning")
async def batch_scan(request: BatchScanRequest, background_tasks: BackgroundTasks):
    """
    Perform multiple spectrometer scans in batch.
    
    Useful for:
    - High-throughput screening
    - Method development
    - Quality control testing
    - Automated analysis workflows
    """
    try:
        result = await advanced_spectrometers.batch_scan({
            "action": "batch_scan",
            "spectrometer_name": request.spectrometer_name,
            "scan_requests": request.scan_requests
        })
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error performing batch scan: {e}")
        raise HTTPException(status_code=500, detail=f"Batch scanning failed: {str(e)}")


@router.post("/calibrate", summary="Calibrate Spectrometer")
async def calibrate_spectrometer(request: CalibrationRequest):
    """
    Calibrate a spectrometer for optimal performance.
    
    Calibration types:
    - standard: Standard calibration procedure
    - wavelength: Wavelength calibration
    - intensity: Intensity calibration
    - resolution: Resolution calibration
    """
    try:
        result = await advanced_spectrometers.calibrate_spectrometer({
            "action": "calibrate_spectrometer",
            "spectrometer_name": request.spectrometer_name,
            "calibration_type": request.calibration_type
        })
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error calibrating spectrometer: {e}")
        raise HTTPException(status_code=500, detail=f"Spectrometer calibration failed: {str(e)}")


@router.get("/scan-history/{spectrometer_name}", summary="Get Scan History")
async def get_scan_history(spectrometer_name: str, limit: int = 50):
    """
    Get scan history for a specific spectrometer.
    
    Returns recent scans with metadata including:
    - Scan timestamps
    - Sample information
    - Quality scores
    - Scan parameters
    """
    try:
        result = await advanced_spectrometers.get_scan_history({
            "action": "get_scan_history",
            "spectrometer_name": spectrometer_name,
            "limit": limit
        })
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error getting scan history: {e}")
        raise HTTPException(status_code=500, detail=f"Scan history retrieval failed: {str(e)}")


@router.get("/spectrometer-types", summary="Get Spectrometer Types")
async def get_spectrometer_types():
    """
    Get information about available spectrometer types and their characteristics.
    """
    return {
        "success": True,
        "spectrometer_types": {
            "nmr": {
                "name": "Nuclear Magnetic Resonance",
                "description": "Analyzes nuclear spin properties",
                "wavelength_range": "0-20 ppm",
                "resolution": "0.1 Hz",
                "applications": ["structure_elucidation", "quantitative_analysis", "metabolomics"]
            },
            "mass_spec": {
                "name": "Mass Spectrometry",
                "description": "Measures mass-to-charge ratios",
                "wavelength_range": "50-2000 m/z",
                "resolution": "40000",
                "applications": ["molecular_weight", "fragmentation", "proteomics"]
            },
            "uv_vis": {
                "name": "UV-Visible Spectroscopy",
                "description": "Measures electronic transitions",
                "wavelength_range": "190-1100 nm",
                "resolution": "0.1 nm",
                "applications": ["concentration_analysis", "kinetics", "chromatography"]
            },
            "ir": {
                "name": "Infrared Spectroscopy",
                "description": "Measures molecular vibrations",
                "wavelength_range": "400-4000 cm⁻¹",
                "resolution": "0.25 cm⁻¹",
                "applications": ["functional_groups", "polymer_analysis", "quality_control"]
            },
            "raman": {
                "name": "Raman Spectroscopy",
                "description": "Measures vibrational modes",
                "wavelength_range": "100-4000 cm⁻¹",
                "resolution": "0.5 cm⁻¹",
                "applications": ["crystal_analysis", "forensics", "materials_science"]
            },
            "fluorescence": {
                "name": "Fluorescence Spectroscopy",
                "description": "Measures fluorescence emission",
                "wavelength_range": "200-800 nm",
                "resolution": "0.5 nm",
                "applications": ["protein_analysis", "drug_discovery", "environmental_monitoring"]
            },
            "cd": {
                "name": "Circular Dichroism",
                "description": "Measures circular dichroism",
                "wavelength_range": "180-800 nm",
                "resolution": "0.1 nm",
                "applications": ["protein_structure", "chirality", "conformational_analysis"]
            },
            "xps": {
                "name": "X-ray Photoelectron Spectroscopy",
                "description": "Measures electron binding energies",
                "wavelength_range": "0-1400 eV",
                "resolution": "0.1 eV",
                "applications": ["surface_analysis", "catalysis", "materials_characterization"]
            }
        }
    }


@router.get("/scan-modes", summary="Get Scan Modes")
async def get_scan_modes():
    """
    Get information about available scan modes and their applications.
    """
    return {
        "success": True,
        "scan_modes": {
            "continuous": {
                "description": "Continuous wavelength scanning",
                "use_case": "Standard spectral acquisition",
                "speed": "Medium",
                "resolution": "Standard"
            },
            "step": {
                "description": "Step-wise wavelength scanning",
                "use_case": "High-resolution measurements",
                "speed": "Slow",
                "resolution": "High"
            },
            "fast": {
                "description": "Fast scanning mode",
                "use_case": "Kinetic studies and screening",
                "speed": "Fast",
                "resolution": "Lower"
            },
            "high_resolution": {
                "description": "High-resolution scanning",
                "use_case": "Detailed spectral analysis",
                "speed": "Slow",
                "resolution": "Highest"
            }
        }
    }


@router.get("/health", summary="Health Check")
async def health_check():
    """Check if the advanced spectrometers service is healthy"""
    return {
        "success": True,
        "service": "AdvancedSpectrometers",
        "status": "healthy",
        "available_spectrometers": 8,
        "supported_types": ["nmr", "mass_spec", "uv_vis", "ir", "raman", "fluorescence", "cd", "xps"],
        "scan_modes": ["continuous", "step", "fast", "high_resolution"]
    }
