"""
Differential Scanning Calorimetry Router

Router FastAPI para servicio de Calorimetría Diferencial de Barrido (DSC).
Proporciona endpoints para análisis térmico avanzado DSC con adquisición de termogramas
simulados y reales, análisis automático de transiciones térmicas, análisis cinético y energías
de activación, recomendaciones de procesamiento y predicción de comportamiento térmico.

Capacidades principales:
- Adquisición de termogramas simulados y datos reales de DSC
- Análisis automático de transiciones térmicas (fusión, cristalización, descomposición)
- Cálculo de energías de transición y entalpías de reacción
- Análisis cinético avanzado con modelos de reacción múltiples
- Determinación de energías de activación por métodos iso-conversión
- Recomendaciones inteligentes de procesamiento basadas en análisis térmico
- Predicción de comportamiento térmico bajo diferentes condiciones
- Análisis de estabilidad térmica y vida útil de materiales
- Comparación de muestras y análisis de pureza

Endpoints disponibles:
- POST /acquire-thermogram: Adquirir termograma DSC con parámetros configurables
- POST /analyze-transitions: Análisis automático de transiciones térmicas
- POST /kinetics-analysis: Análisis cinético con múltiples métodos
- POST /processing-recommendations: Recomendaciones de procesamiento basadas en DSC
- POST /predict-thermal-behavior: Predicción de comportamiento térmico
- GET /examples: Ejemplos de análisis DSC para diferentes materiales
- POST /compare-samples: Comparación de termogramas de múltiples muestras

Dependencias:
- DifferentialScanningCalorimetryService: Servicio principal de análisis DSC
- ThermogramRequest: Solicitud de adquisición de termograma
- CompleteAnalysisRequest: Solicitud de análisis completo
- KineticsAnalysisRequest: Solicitud de análisis cinético
- ProcessingRecommendationsRequest: Solicitud de recomendaciones de procesamiento

Uso típico:
    from app.domains.chemistry.routers.differential_scanning_calorimetry import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles bajo el prefijo /dsc
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field

from app.exceptions.domain.chemistry import ChemistryError
from ..analytical.differential_scanning_calorimetry_service import (
    DifferentialScanningCalorimetryService,
    ThermalAnalysisResult,
)

# Initialize service and router
dsc_service = DifferentialScanningCalorimetryService()
router = APIRouter(prefix="/dsc", tags=["Differential Scanning Calorimetry"])

# Request models
class ThermogramRequest(BaseModel):
    """Request for thermogram acquisition"""
    sample_id: str = Field(..., description="Unique sample identifier", example="polymer_sample_001")
    sample_mass: float = Field(..., description="Sample mass in mg", example=5.2, gt=0)
    heating_rate: float = Field(..., description="Heating rate in °C/min", example=10.0, gt=0.1, le=100.0)
    temperature_range: Tuple[float, float] = Field(..., description="Temperature range (min, max) in °C", example=(25.0, 500.0))
    atmosphere: str = Field(default="nitrogen", description="Measurement atmosphere", example="nitrogen")
    reference_material: Optional[str] = Field(default=None, description="Reference material", example="indium")
    simulate: bool = Field(default=True, description="Whether to simulate data")

class CompleteAnalysisRequest(BaseModel):
    """Request for complete DSC analysis"""
    sample_id: str = Field(..., description="Unique sample identifier", example="polymer_sample_001")
    sample_mass: float = Field(..., description="Sample mass in mg", example=5.2, gt=0)
    heating_rate: float = Field(..., description="Heating rate in °C/min", example=10.0, gt=0.1, le=100.0)
    temperature_range: Tuple[float, float] = Field(..., description="Temperature range (min, max) in °C", example=(25.0, 500.0))
    atmosphere: str = Field(default="nitrogen", description="Measurement atmosphere", example="nitrogen")

class KineticsAnalysisRequest(BaseModel):
    """Request for kinetics analysis"""
    heating_rates: List[float] = Field(..., description="List of heating rates in °C/min", example=[5.0, 10.0, 20.0], min_items=3)
    peak_temps: List[float] = Field(..., description="Corresponding peak temperatures in °C", example=[320.5, 328.2, 336.1], min_items=3)
    reaction_type: str = Field(default="decomposition", description="Type of reaction", example="decomposition")

class ProcessingRecommendationsRequest(BaseModel):
    """Request for processing recommendations"""
    analysis_result_id: str = Field(..., description="Analysis result identifier")
    application: str = Field(default="general", description="Intended application", example="polymer_processing")

class ThermalPredictionRequest(BaseModel):
    """Request for thermal behavior prediction"""
    material_properties: Dict[str, Any] = Field(..., description="Known material properties")
    temperature_profile: List[Tuple[float, float]] = Field(..., description="Temperature-time profile")

class ComparativeAnalysisRequest(BaseModel):
    """Request for comparative analysis"""
    analysis_result_ids: List[str] = Field(..., description="List of analysis result IDs to compare", min_items=2)
    comparison_criteria: Optional[List[str]] = Field(default=None, description="Specific criteria to compare")

class ExportRequest(BaseModel):
    """Request for results export"""
    analysis_result_id: str = Field(..., description="Analysis result identifier")
    export_format: str = Field(default="json", description="Export format", example="json")
    include_raw_data: bool = Field(default=True, description="Include raw thermogram data")

# Store for analysis results (in production, use database)
analysis_results_store: Dict[str, ThermalAnalysisResult] = {}

@router.post("/thermogram", response_model=Dict[str, Any])
async def acquire_thermogram(request: ThermogramRequest):
    """
    Acquire DSC thermogram data for thermal analysis.
    
    Simulates or acquires real DSC thermogram data with configurable parameters.
    Returns thermogram with temperature and heat flow data plus metadata.
    """
    try:
        thermogram = await dsc_service.acquire_thermogram(
            sample_id=request.sample_id,
            sample_mass=request.sample_mass,
            heating_rate=request.heating_rate,
            temperature_range=request.temperature_range,
            atmosphere=request.atmosphere,
            reference_material=request.reference_material,
            simulate=request.simulate
        )
        
        return {
            "status": "success",
            "message": f"Thermogram acquired for sample {request.sample_id}",
            "thermogram": thermogram.dict(),
            "data_points": len(thermogram.temperature_data),
            "temperature_range_actual": (
                min(thermogram.temperature_data),
                max(thermogram.temperature_data)
            )
        }
        
    except ChemistryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error acquiring thermogram: {str(e)}"
        )

@router.post("/analyze", response_model=Dict[str, Any])
async def perform_complete_analysis(request: CompleteAnalysisRequest):
    """
    Perform complete DSC analysis including thermogram acquisition and thermal characterization.
    
    Executes full thermal analysis workflow:
    - Acquires thermogram data
    - Detects thermal transitions
    - Calculates thermal properties
    - Generates processing recommendations
    """
    try:
        result = await dsc_service.perform_complete_analysis(
            sample_id=request.sample_id,
            sample_mass=request.sample_mass,
            heating_rate=request.heating_rate,
            temperature_range=request.temperature_range,
            atmosphere=request.atmosphere
        )
        
        # Store result for later access
        analysis_results_store[result.analysis_id] = result
        
        return {
            "status": "success",
            "message": f"Complete DSC analysis completed for sample {request.sample_id}",
            "analysis_id": result.analysis_id,
            "summary": {
                "transitions_detected": len(result.transitions),
                "melting_point": result.melting_point,
                "glass_transition_temp": result.glass_transition_temp,
                "decomposition_temp": result.decomposition_temp,
                "thermal_stability": result.thermal_stability,
                "purity_estimate": result.purity_estimate
            },
            "transitions": [
                {
                    "type": t.transition_type,
                    "onset_temp": t.onset_temperature,
                    "peak_temp": t.peak_temperature,
                    "enthalpy": t.enthalpy
                } for t in result.transitions
            ],
            "recommendations": result.recommendations
        }
        
    except ChemistryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in DSC analysis: {str(e)}"
        )

@router.post("/kinetics", response_model=Dict[str, Any])
async def perform_kinetics_analysis(request: KineticsAnalysisRequest):
    """
    Perform kinetic analysis using multiple heating rates to determine activation energy.
    
    Uses Kissinger and Ozawa methods to calculate:
    - Activation energy (kJ/mol)
    - Pre-exponential factor
    - Reaction order
    - Correlation statistics
    """
    try:
        if len(request.heating_rates) != len(request.peak_temps):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Heating rates and peak temperatures must have same length"
            )
        
        result = await dsc_service.perform_kinetics_analysis(
            heating_rates=request.heating_rates,
            peak_temps=request.peak_temps,
            reaction_type=request.reaction_type
        )
        
        return {
            "status": "success",
            "message": "Kinetics analysis completed",
            "analysis_id": result.analysis_id,
            "kinetics": {
                "activation_energy": result.activation_energy,
                "pre_exponential_factor": result.pre_exponential_factor,
                "reaction_order": result.reaction_order,
                "correlation_coefficient": result.correlation_coefficient,
                "confidence_level": result.confidence_level
            },
            "temperature_range": result.temperature_range,
            "data_quality": {
                "correlation_rating": "excellent" if abs(result.correlation_coefficient) > 0.95 else
                                   "good" if abs(result.correlation_coefficient) > 0.90 else
                                   "acceptable" if abs(result.correlation_coefficient) > 0.85 else "poor",
                "data_points": len(request.heating_rates)
            }
        }
        
    except ChemistryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in kinetics analysis: {str(e)}"
        )

@router.post("/recommendations", response_model=Dict[str, Any])
async def generate_processing_recommendations(request: ProcessingRecommendationsRequest):
    """
    Generate processing and application recommendations based on DSC analysis results.
    
    Provides application-specific guidance for:
    - Processing conditions (temperature, pressure)
    - Storage requirements
    - Quality control parameters
    - Suitable applications and limitations
    """
    try:
        if request.analysis_result_id not in analysis_results_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis result {request.analysis_result_id} not found"
            )
        
        analysis_result = analysis_results_store[request.analysis_result_id]
        
        recommendations = await dsc_service.generate_processing_recommendations(
            analysis_result=analysis_result,
            application=request.application
        )
        
        return {
            "status": "success",
            "message": f"Processing recommendations generated for {request.application}",
            "analysis_id": request.analysis_result_id,
            "sample_id": analysis_result.sample_id,
            "recommendations": recommendations,
            "application_context": request.application
        }
        
    except HTTPException:
        raise
    except ChemistryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.post("/predict", response_model=Dict[str, Any])
async def predict_thermal_behavior(request: ThermalPredictionRequest):
    """
    Predict thermal behavior under specific temperature profiles.
    
    Models thermal response and predicts:
    - Reaction extents at each temperature
    - Degradation risk assessment
    - Recommended process modifications
    """
    try:
        predictions = await dsc_service.predict_thermal_behavior(
            material_properties=request.material_properties,
            temperature_profile=request.temperature_profile
        )
        
        return {
            "status": "success",
            "message": "Thermal behavior prediction completed",
            "predictions": predictions,
            "profile_summary": {
                "max_temperature": max(temp for temp, time in request.temperature_profile),
                "total_time": sum(time for temp, time in request.temperature_profile),
                "temperature_steps": len(request.temperature_profile)
            }
        }
        
    except ChemistryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error predicting thermal behavior: {str(e)}"
        )

@router.post("/compare", response_model=Dict[str, Any])
async def comparative_analysis(request: ComparativeAnalysisRequest):
    """
    Compare multiple DSC analysis results across various criteria.
    
    Provides statistical comparison and ranking of samples based on:
    - Thermal properties
    - Stability characteristics
    - Purity estimates
    - Processing suitability
    """
    try:
        results_list = []
        missing_ids = []
        
        for result_id in request.analysis_result_ids:
            if result_id in analysis_results_store:
                results_list.append(analysis_results_store[result_id])
            else:
                missing_ids.append(result_id)
        
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis results not found: {missing_ids}"
            )
        
        comparison = await dsc_service.comparative_analysis(
            results_list=results_list,
            comparison_criteria=request.comparison_criteria
        )
        
        return {
            "status": "success",
            "message": f"Comparative analysis completed for {len(results_list)} samples",
            "comparison": comparison,
            "analysis_summary": {
                "samples_compared": len(results_list),
                "criteria_evaluated": len(comparison.get("comparison_summary", {})),
                "overall_best": comparison.get("overall_ranking", [None])[0]
            }
        }
        
    except HTTPException:
        raise
    except ChemistryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in comparative analysis: {str(e)}"
        )

@router.post("/export", response_model=Dict[str, Any])
async def export_results(request: ExportRequest):
    """
    Export DSC analysis results in specified format.
    
    Supports multiple export formats:
    - JSON: Complete structured data
    - CSV: Key parameters and transitions
    - Excel: Formatted report (future)
    """
    try:
        if request.analysis_result_id not in analysis_results_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis result {request.analysis_result_id} not found"
            )
        
        analysis_result = analysis_results_store[request.analysis_result_id]
        
        exported_data = await dsc_service.export_results(
            results=analysis_result,
            export_format=request.export_format,
            include_raw_data=request.include_raw_data
        )
        
        return {
            "status": "success",
            "message": f"Results exported in {request.export_format} format",
            "analysis_id": request.analysis_result_id,
            "export_format": request.export_format,
            "data": exported_data,
            "metadata": {
                "include_raw_data": request.include_raw_data,
                "export_timestamp": analysis_result.analysis_timestamp.isoformat(),
                "sample_id": analysis_result.sample_id
            }
        }
        
    except HTTPException:
        raise
    except ChemistryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting results: {str(e)}"
        )

@router.get("/results/{analysis_id}", response_model=Dict[str, Any])
async def get_analysis_result(analysis_id: str):
    """
    Retrieve complete DSC analysis results by ID.
    
    Returns full analysis data including:
    - Original thermogram
    - Detected transitions
    - Calculated properties
    - Recommendations
    """
    try:
        if analysis_id not in analysis_results_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis result {analysis_id} not found"
            )
        
        result = analysis_results_store[analysis_id]
        
        return {
            "status": "success",
            "analysis_result": result.dict(),
            "summary": {
                "sample_id": result.sample_id,
                "transitions_count": len(result.transitions),
                "thermal_stability": result.thermal_stability,
                "analysis_timestamp": result.analysis_timestamp.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except ChemistryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analysis result: {str(e)}"
        )

@router.get("/results", response_model=Dict[str, Any])
async def list_analysis_results():
    """
    List all stored DSC analysis results with basic metadata.
    """
    try:
        results_summary = []
        
        for analysis_id, result in analysis_results_store.items():
            results_summary.append({
                "analysis_id": analysis_id,
                "sample_id": result.sample_id,
                "analysis_timestamp": result.analysis_timestamp.isoformat(),
                "transitions_count": len(result.transitions),
                "thermal_stability": result.thermal_stability,
                "melting_point": result.melting_point,
                "purity_estimate": result.purity_estimate
            })
        
        return {
            "status": "success",
            "message": f"Found {len(results_summary)} analysis results",
            "results": results_summary,
            "total_count": len(results_summary)
        }
        
    except ChemistryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing analysis results: {str(e)}"
        )

@router.get("/service/status", response_model=Dict[str, Any])
async def get_service_status():
    """
    Get DSC service status and configuration information.
    """
    try:
        return {
            "service_name": dsc_service.service_name,
            "version": dsc_service.version,
            "description": dsc_service.description,
            "status": "operational",
            "configuration": {
                "temperature_precision": f"{dsc_service.temperature_precision}°C",
                "heat_flow_precision": f"{dsc_service.heat_flow_precision} mW",
                "scan_rate_range": f"{dsc_service.scan_rate_range[0]}-{dsc_service.scan_rate_range[1]} °C/min",
                "max_temperature": f"{dsc_service.max_temperature}°C",
                "peak_detection_threshold": f"{dsc_service.peak_detection_threshold} mW"
            },
            "stored_results": len(analysis_results_store),
            "available_endpoints": [
                "/thermogram", "/analyze", "/kinetics", 
                "/recommendations", "/predict", "/compare", "/export"
            ]
        }
        
    except ChemistryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting service status: {str(e)}"
        )

@router.delete("/results/{analysis_id}", response_model=Dict[str, Any])
async def delete_analysis_result(analysis_id: str):
    """
    Delete stored DSC analysis result.
    """
    try:
        if analysis_id not in analysis_results_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis result {analysis_id} not found"
            )
        
        deleted_result = analysis_results_store.pop(analysis_id)
        
        return {
            "status": "success",
            "message": f"Analysis result {analysis_id} deleted",
            "deleted_sample_id": deleted_result.sample_id,
            "remaining_results": len(analysis_results_store)
        }
        
    except HTTPException:
        raise
    except ChemistryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting analysis result: {str(e)}"
        )
