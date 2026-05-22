"""
AXIOM AI Scientist Router

Este módulo proporciona endpoints FastAPI para el servicio de Científico IA con capacidades
de análisis temporal. Permite acceso RESTful al servicio de Científico IA, habilitando
análisis avanzado de tendencias temporales y generación de insights científicos.

Capacidades principales:
- Análisis temporal comprehensivo de tendencias científicas
- Detección automática de patrones estacionales y cíclicos
- Generación de pronósticos y predicciones basadas en datos históricos
- Análisis de correlaciones entre variables científicas
- Identificación de anomalías y eventos significativos
- Visualización de tendencias temporales con anotaciones
- Análisis de causalidad y relaciones temporales
- Generación automática de hipótesis basadas en tendencias
- Evaluación de la significancia estadística de tendencias

Endpoints disponibles:
- GET /status: Estado del servicio de Científico IA
- POST /analyze-temporal-trends: Análisis de tendencias temporales
- POST /generate-scientific-insights: Generación de insights científicos
- POST /forecast-scientific-data: Pronósticos de datos científicos
- POST /detect-anomalies: Detección de anomalías en series temporales
- GET /temporal-analysis-history: Historial de análisis temporales
- POST /correlation-analysis: Análisis de correlaciones temporales
- POST /causality-analysis: Análisis de causalidad temporal

Dependencias:
- AIScientistService: Servicio principal de Científico IA
- TemporalAnalysisRequest: Solicitud de análisis temporal
- ScientificInsightsRequest: Solicitud de generación de insights
- ForecastingRequest: Solicitud de pronósticos

Uso típico:
    from app.routers.ai_scientist_router import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles bajo el prefijo /ai-scientist
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Optional, Any, List
import logging
from datetime import datetime
import json

from app.services.ai_scientist_service import AIScientistService
from app.exceptions.domain.biology import BiologyError

logger = logging.getLogger(__name__)

# Initialize AI Scientist service
ai_scientist_service = AIScientistService()

router = APIRouter(
    prefix="/ai-scientist",
    tags=["AI Scientist"],
    responses={404: {"description": "Not found"}}
)

@router.get("/status")
async def get_service_status():
    """
    🔬 Get AI Scientist Service Status
    
    Returns comprehensive status information including supported capabilities,
    temporal analysis features, and service health.
    """
    try:
        return ai_scientist_service.get_service_info()
    except BiologyError as e:
        logger.error(f"❌ Error getting service status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-temporal-trends")
async def analyze_temporal_trends(
    data: List[Dict[str, Any]] = Body(..., description="Time series data for analysis"),
    analysis_type: str = Query("comprehensive", description="Type of analysis: comprehensive, trend, seasonal, forecast"),
    target_column: str = Query("value", description="Name of the column containing values to analyze"),
    timestamp_column: str = Query("timestamp", description="Name of the column containing timestamps"),
    frequency: str = Query("D", description="Data frequency (D=daily, W=weekly, M=monthly, Q=quarterly, Y=yearly)"),
    forecast_periods: int = Query(30, description="Number of periods to forecast")
):
    """
    📈 Analyze Temporal Trends in Scientific Data
    
    Performs comprehensive time series analysis including:
    - Descriptive statistics and data quality assessment
    - Trend analysis and decomposition
    - Seasonality detection
    - Stationarity testing
    - Forecasting with multiple models
    - Anomaly detection
    - Scientific insights generation
    
    Returns detailed analysis results with visualizations and insights.
    """
    try:
        # Validate input data
        if not data:
            raise HTTPException(status_code=400, detail="No data provided for analysis")
        
        if len(data) < 10:
            raise HTTPException(status_code=400, detail="Insufficient data points for meaningful analysis")
        
        # Perform temporal analysis
        return ai_scientist_service.analyze_temporal_trends(
            data=data,
            analysis_type=analysis_type,
            target_column=target_column,
            timestamp_column=timestamp_column,
            frequency=frequency,
            forecast_periods=forecast_periods
        )
        
    except ValueError as e:
        logger.error(f"❌ Validation error in temporal analysis: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except BiologyError as e:
        logger.error(f"❌ Error performing temporal analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-test-data")
async def generate_test_data(
    data_type: str = Query("scientific", description="Type of test data: scientific, economic, environmental, medical"),
    num_points: int = Query(100, description="Number of data points to generate"),
    start_date: str = Query("2023-01-01", description="Start date for generated data"),
    end_date: str = Query("2024-01-01", description="End date for generated data")
):
    """
    🧪 Generate Realistic Test Data for Temporal Analysis
    
    Creates realistic time series data for testing and demonstration purposes.
    Supports multiple scientific domains with realistic patterns and noise.
    """
    try:
        test_data = _generate_realistic_test_data(
            data_type=data_type,
            num_points=num_points,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "data_type": data_type,
            "num_points": num_points,
            "start_date": start_date,
            "end_date": end_date,
            "data": test_data
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error generating test data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def _generate_realistic_test_data(data_type: str, num_points: int, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Generate realistic test data for temporal analysis
    """
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Parse dates
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Generate date range
    dates = pd.date_range(start=start_dt, end=end_dt, periods=num_points)
    
    # Generate data based on type
    if data_type == "scientific":
        # Scientific experimental data with trends and seasonality
        trend = np.linspace(50, 200, num_points)
        seasonal = 20 * np.sin(2 * np.pi * np.arange(num_points) / 12)  # Monthly seasonality
        noise = np.random.normal(0, 5, num_points)
        values = trend + seasonal + noise
        
        data = [
            {
                "timestamp": date.isoformat(),
                "value": float(value),
                "experiment_id": f"exp_{i:03d}",
                "temperature": np.random.uniform(20, 30),
                "pressure": np.random.uniform(900, 1100),
                "measurement_type": np.random.choice(["optical", "electrical", "thermal"])
            }
            for i, (date, value) in enumerate(zip(dates, values))
        ]
        
    elif data_type == "economic":
        # Economic data with growth trends
        trend = np.linspace(1000, 5000, num_points)
        seasonal = 200 * np.sin(2 * np.pi * np.arange(num_points) / 4)  # Quarterly seasonality
        noise = np.random.normal(0, 50, num_points)
        values = trend + seasonal + noise
        
        data = [
            {
                "timestamp": date.isoformat(),
                "gdp": float(value),
                "unemployment_rate": np.random.uniform(3, 8),
                "inflation_rate": np.random.uniform(1, 5),
                "region": np.random.choice(["North", "South", "East", "West"])
            }
            for i, (date, value) in enumerate(zip(dates, values))
        ]
        
    elif data_type == "environmental":
        # Environmental data with seasonal patterns
        base_temp = 15
        seasonal = 10 * np.sin(2 * np.pi * np.arange(num_points) / 365)  # Yearly seasonality
        trend = 0.01 * np.arange(num_points)  # Slight warming trend
        noise = np.random.normal(0, 2, num_points)
        values = base_temp + seasonal + trend + noise
        
        data = [
            {
                "timestamp": date.isoformat(),
                "temperature": float(value),
                "humidity": np.random.uniform(40, 80),
                "precipitation": np.random.exponential(5),
                "location": np.random.choice(["urban", "rural", "coastal"])
            }
            for i, (date, value) in enumerate(zip(dates, values))
        ]
        
    elif data_type == "medical":
        # Medical data with weekly patterns
        base_value = 100
        seasonal = 20 * np.sin(2 * np.pi * np.arange(num_points) / 7)  # Weekly seasonality
        trend = 0.5 * np.arange(num_points)  # Gradual increase
        noise = np.random.normal(0, 8, num_points)
        values = base_value + seasonal + trend + noise
        
        data = [
            {
                "timestamp": date.isoformat(),
                "patient_count": int(max(0, value)),
                "disease_type": np.random.choice(["viral", "bacterial", "chronic"]),
                "age_group": np.random.choice(["child", "adult", "elderly"]),
                "severity": np.random.choice(["mild", "moderate", "severe"])
            }
            for i, (date, value) in enumerate(zip(dates, values))
        ]
        
    else:
        # Default: random walk
        values = np.cumsum(np.random.normal(0, 2, num_points)) + 100
        
        data = [
            {
                "timestamp": date.isoformat(),
                "value": float(value),
                "category": np.random.choice(["A", "B", "C", "D"])
            }
            for i, (date, value) in enumerate(zip(dates, values))
        ]
    
    return data

@router.post("/generate-scientific-insights")
async def generate_scientific_insights(
    data: List[Dict[str, Any]] = Body(..., description="Scientific data for insights generation"),
    analysis_focus: str = Query("comprehensive", description="Focus area: comprehensive, trends, patterns, anomalies, correlations"),
    domain: str = Query("general", description="Scientific domain: general, physics, chemistry, biology, materials, environmental"),
    confidence_threshold: float = Query(0.7, description="Minimum confidence threshold for insights (0.0-1.0)"),
    max_insights: int = Query(10, description="Maximum number of insights to generate")
):
    """
    🧠 Generate Scientific Insights from Data
    
    Analyzes scientific data to generate meaningful insights, patterns, and recommendations.
    Uses advanced AI techniques to identify trends, correlations, and anomalies in scientific datasets.
    
    Returns structured insights with confidence scores and scientific interpretations.
    """
    try:
        # Validate input data
        if not data:
            raise HTTPException(status_code=400, detail="No data provided for insights generation")
        
        if len(data) < 5:
            raise HTTPException(status_code=400, detail="Insufficient data points for meaningful insights")
        
        # Validate confidence threshold
        if not 0.0 <= confidence_threshold <= 1.0:
            raise HTTPException(status_code=400, detail="Confidence threshold must be between 0.0 and 1.0")
        
        # Generate scientific insights
        insights = ai_scientist_service.generate_scientific_insights(
            data=data,
            analysis_focus=analysis_focus,
            domain=domain,
            confidence_threshold=confidence_threshold,
            max_insights=max_insights
        )
        
        return {
            "success": True,
            "message": "Scientific insights generated successfully",
            "data": insights,
            "metadata": {
                "analysis_focus": analysis_focus,
                "domain": domain,
                "confidence_threshold": confidence_threshold,
                "data_points_analyzed": len(data),
                "insights_generated": len(insights.get("insights", [])),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except ValueError as e:
        logger.error(f"❌ Validation error in insights generation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except BiologyError as e:
        logger.error(f"❌ Error generating scientific insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/capabilities")
async def get_capabilities():
    """
    🔧 Get AI Scientist Service Capabilities
    
    Returns detailed information about supported features, analysis types,
    data formats, and integration capabilities.
    """
    try:
        capabilities = {
            "service_name": "AI Scientist Service",
            "version": "1.0.0",
            "description": "Advanced temporal analysis and scientific insights generation",
            "features": [
                {
                    "name": "Temporal Analysis",
                    "description": "Comprehensive time series analysis capabilities",
                    "features": [
                        "Descriptive statistics and data quality assessment",
                        "Trend analysis and decomposition",
                        "Seasonality detection and analysis",
                        "Stationarity testing",
                        "Forecasting with multiple models",
                        "Anomaly detection",
                        "Scientific insights generation"
                    ],
                    "supported_analysis_types": ["comprehensive", "trend", "seasonal", "forecast"]
                },
                {
                    "name": "Scientific Insights",
                    "description": "AI-powered scientific insights generation",
                    "features": [
                        "Pattern recognition and analysis",
                        "Correlation detection",
                        "Anomaly identification",
                        "Trend interpretation",
                        "Scientific hypothesis generation",
                        "Domain-specific analysis"
                    ],
                    "supported_domains": ["general", "physics", "chemistry", "biology", "materials", "environmental"]
                },
                {
                    "name": "Data Integration",
                    "description": "Support for multiple data formats and scientific domains",
                    "features": [
                        "JSON data input",
                        "CSV file support",
                        "Real-time data streaming",
                        "Multiple scientific domains"
                    ]
                },
                {
                    "name": "Visualization",
                    "description": "Advanced data visualization capabilities",
                    "features": [
                        "Interactive charts",
                        "Statistical plots",
                        "Forecast visualizations",
                        "Anomaly highlighting"
                    ]
                }
            ],
            "integrations": ai_scientist_service.get_service_info().get("integrations", {}),
            "supported_data_types": ["scientific", "economic", "environmental", "medical", "custom"],
            "timestamp_formats": ["ISO8601", "YYYY-MM-DD", "YYYY-MM-DD HH:MM:SS"],
            "max_data_points": 10000,
            "min_data_points": 10
        }
        
        return capabilities
        
    except BiologyError as e:
        logger.error(f"❌ Error getting capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))