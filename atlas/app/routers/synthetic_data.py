"""
FastAPI Router for Synthetic Data Generation Service

This router provides endpoints for generating synthetic data using various methods
including GANs, statistical models, and rule-based generation.

Endpoints:
- POST /generate-tabular: Generate synthetic tabular data
- POST /generate-ctgan: Generate data using CTGAN specifically  
- POST /generate-timeseries: Generate synthetic time series data
- POST /generate-multitable: Generate synthetic multi-table data
- POST /generate-fake: Generate fake data using Faker
- POST /assess-privacy: Assess privacy risks in synthetic data
- GET /methods: Get available generation methods
- GET /health: Health check endpoint
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import json
from datetime import datetime
import logging

from app.services.synthetic_data_service import SyntheticDataService
from app.exceptions.domain.biology import BiologyError

# Initialize router and service
router = APIRouter()
synthetic_service = SyntheticDataService()
logger = logging.getLogger(__name__)

# Pydantic Models for Request/Response

class TabularDataRequest(BaseModel):
    """Request model for tabular data generation"""
    data: List[Dict[str, Any]] = Field(..., description="Original dataset as list of records")
    num_rows: int = Field(1000, ge=1, le=100000, description="Number of synthetic rows to generate")
    method: str = Field("gaussian_copula", description="Generation method")
    constraints: Optional[List[Dict[str, Any]]] = Field(None, description="Data constraints")
    additional_params: Optional[Dict[str, Any]] = Field({}, description="Additional parameters")

class CTGANRequest(BaseModel):
    """Request model for CTGAN generation"""
    data: List[Dict[str, Any]] = Field(..., description="Original dataset as list of records")
    num_rows: int = Field(1000, ge=1, le=100000, description="Number of synthetic rows to generate")
    epochs: int = Field(300, ge=10, le=1000, description="Training epochs")
    batch_size: int = Field(500, ge=32, le=2048, description="Batch size")
    additional_params: Optional[Dict[str, Any]] = Field({}, description="Additional CTGAN parameters")

class TimeSeriesRequest(BaseModel):
    """Request model for time series generation"""
    data: List[Dict[str, Any]] = Field(..., description="Time series data as list of records")
    time_column: str = Field(..., description="Name of the time column")
    num_sequences: int = Field(100, ge=1, le=10000, description="Number of synthetic sequences")
    sequence_length: Optional[int] = Field(None, description="Length of each sequence")
    additional_params: Optional[Dict[str, Any]] = Field({}, description="Additional parameters")

class MultiTableRequest(BaseModel):
    """Request model for multi-table generation"""
    tables: Dict[str, List[Dict[str, Any]]] = Field(..., description="Dictionary of table data")
    relationships: List[Dict[str, str]] = Field(..., description="Table relationships")
    num_rows: Optional[Dict[str, int]] = Field(None, description="Rows per table")
    additional_params: Optional[Dict[str, Any]] = Field({}, description="Additional parameters")

class FakeDataRequest(BaseModel):
    """Request model for fake data generation"""
    schema: Dict[str, str] = Field(..., description="Column to faker provider mapping")
    num_rows: int = Field(1000, ge=1, le=100000, description="Number of rows to generate")
    locale: str = Field("en_US", description="Locale for fake data")

class PrivacyAssessmentRequest(BaseModel):
    """Request model for privacy assessment"""
    original_data: List[Dict[str, Any]] = Field(..., description="Original dataset")
    synthetic_data: List[Dict[str, Any]] = Field(..., description="Synthetic dataset")
    quasi_identifiers: Optional[List[str]] = Field(None, description="Quasi-identifier columns")

class SyntheticDataResponse(BaseModel):
    """Response model for synthetic data generation"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    generation_time: Optional[str] = None

class PrivacyAssessmentResponse(BaseModel):
    """Response model for privacy assessment"""
    success: bool
    privacy_metrics: Optional[Dict[str, Any]] = None
    risk_level: Optional[str] = None
    recommendations: Optional[List[str]] = None
    error: Optional[str] = None

class MethodsResponse(BaseModel):
    """Response model for available methods"""
    methods: List[str]
    descriptions: Dict[str, str]
    capabilities: List[str]

# Router Endpoints

@router.post("/generate-tabular", response_model=SyntheticDataResponse)
async def generate_tabular_data(request: TabularDataRequest):
    """
    Generate synthetic tabular data using various methods
    
    Supports multiple generation methods:
    - gaussian_copula: Statistical method using Gaussian copulas
    - ctgan: Conditional Tabular GAN
    - tvae: Tabular Variational Autoencoder
    """
    try:
        start_time = datetime.now()
        
        # Convert request data to DataFrame
        df = pd.DataFrame(request.data)
        
        # Generate synthetic data
        result = synthetic_service.generate_tabular_data(
            data=df,
            num_rows=request.num_rows,
            method=request.method,
            constraints=request.constraints,
            **request.additional_params
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return SyntheticDataResponse(
            success=True,
            data=result,
            metadata={
                "method": request.method,
                "original_rows": len(df),
                "synthetic_rows": request.num_rows,
                "generation_time_seconds": generation_time
            },
            generation_time=datetime.now().isoformat()
        )
        
    except BiologyError as e:
        logger.error(f"Error in tabular data generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-ctgan", response_model=SyntheticDataResponse)
async def generate_ctgan_data(request: CTGANRequest):
    """
    Generate synthetic data using CTGAN specifically
    
    CTGAN (Conditional Tabular GAN) is particularly effective for:
    - Mixed data types (numerical and categorical)
    - Imbalanced datasets
    - Complex data distributions
    """
    try:
        start_time = datetime.now()
        
        # Convert request data to DataFrame
        df = pd.DataFrame(request.data)
        
        # Generate synthetic data using CTGAN
        result = synthetic_service.generate_ctgan_data(
            data=df,
            num_rows=request.num_rows,
            epochs=request.epochs,
            batch_size=request.batch_size,
            **request.additional_params
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return SyntheticDataResponse(
            success=True,
            data=result,
            metadata={
                "method": "ctgan",
                "epochs": request.epochs,
                "batch_size": request.batch_size,
                "generation_time_seconds": generation_time
            },
            generation_time=datetime.now().isoformat()
        )
        
    except BiologyError as e:
        logger.error(f"Error in CTGAN generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-timeseries", response_model=SyntheticDataResponse)
async def generate_time_series_data(request: TimeSeriesRequest):
    """
    Generate synthetic time series data
    
    Supports:
    - Univariate and multivariate time series
    - Trend and seasonality preservation
    - Custom sequence lengths
    """
    try:
        start_time = datetime.now()
        
        # Convert request data to DataFrame
        df = pd.DataFrame(request.data)
        
        # Ensure time column is datetime
        if request.time_column in df.columns:
            df[request.time_column] = pd.to_datetime(df[request.time_column])
        
        # Generate synthetic time series
        result = synthetic_service.generate_time_series_data(
            data=df,
            time_column=request.time_column,
            num_sequences=request.num_sequences,
            sequence_length=request.sequence_length,
            **request.additional_params
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return SyntheticDataResponse(
            success=True,
            data=result,
            metadata={
                "method": "time_series",
                "time_column": request.time_column,
                "num_sequences": request.num_sequences,
                "generation_time_seconds": generation_time
            },
            generation_time=datetime.now().isoformat()
        )
        
    except BiologyError as e:
        logger.error(f"Error in time series generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-multitable", response_model=SyntheticDataResponse)
async def generate_multi_table_data(request: MultiTableRequest):
    """
    Generate synthetic data for multiple related tables
    
    Preserves:
    - Referential integrity
    - Cross-table relationships
    - Individual table distributions
    """
    try:
        start_time = datetime.now()
        
        # Convert request tables to DataFrames
        tables = {}
        for table_name, table_data in request.tables.items():
            tables[table_name] = pd.DataFrame(table_data)
        
        # Generate synthetic multi-table data
        result = synthetic_service.generate_multi_table_data(
            tables=tables,
            relationships=request.relationships,
            num_rows=request.num_rows,
            **request.additional_params
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return SyntheticDataResponse(
            success=True,
            data=result,
            metadata={
                "method": "multi_table",
                "num_tables": len(request.tables),
                "relationships": len(request.relationships),
                "generation_time_seconds": generation_time
            },
            generation_time=datetime.now().isoformat()
        )
        
    except BiologyError as e:
        logger.error(f"Error in multi-table generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-fake", response_model=SyntheticDataResponse)
async def generate_fake_data(request: FakeDataRequest):
    """
    Generate fake data using Faker library
    
    Useful for:
    - Realistic test data
    - Quick prototyping
    - Privacy-safe development data
    """
    try:
        start_time = datetime.now()
        
        # Generate fake data
        result = synthetic_service.generate_fake_data(
            schema=request.schema,
            num_rows=request.num_rows,
            locale=request.locale
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return SyntheticDataResponse(
            success=True,
            data=result,
            metadata={
                "method": "faker",
                "locale": request.locale,
                "schema_columns": len(request.schema),
                "generation_time_seconds": generation_time
            },
            generation_time=datetime.now().isoformat()
        )
        
    except BiologyError as e:
        logger.error(f"Error in fake data generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assess-privacy", response_model=PrivacyAssessmentResponse)
async def assess_privacy_risk(request: PrivacyAssessmentRequest):
    """
    Assess privacy risks in synthetic data
    
    Evaluates:
    - Exact record matches
    - Statistical similarity
    - Membership inference risk
    - Re-identification potential
    """
    try:
        # Convert request data to DataFrames
        original_df = pd.DataFrame(request.original_data)
        synthetic_df = pd.DataFrame(request.synthetic_data)
        
        # Assess privacy risks
        result = synthetic_service.assess_privacy_risk(
            original_data=original_df,
            synthetic_data=synthetic_df,
            quasi_identifiers=request.quasi_identifiers
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return PrivacyAssessmentResponse(
            success=True,
            privacy_metrics=result.get("privacy_metrics"),
            risk_level=result.get("risk_level"),
            recommendations=result.get("recommendations")
        )
        
    except BiologyError as e:
        logger.error(f"Error in privacy assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/methods", response_model=MethodsResponse)
async def get_available_methods():
    """
    Get available synthetic data generation methods
    """
    try:
        service_info = synthetic_service.get_service_info()
        
        method_descriptions = {
            "gaussian_copula": "Statistical method using Gaussian copulas for tabular data",
            "ctgan": "Conditional Tabular GAN for mixed data types",
            "tvae": "Tabular Variational Autoencoder",
            "faker": "Rule-based fake data generation",
            "time_series": "Time series synthetic data generation",
            "multi_table": "Multi-table relational data synthesis"
        }
        
        return MethodsResponse(
            methods=service_info["methods"],
            descriptions=method_descriptions,
            capabilities=service_info["capabilities"]
        )
        
    except BiologyError as e:
        logger.error(f"Error getting methods: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the synthetic data service
    """
    try:
        service_info = synthetic_service.get_service_info()
        
        return {
            "status": "healthy",
            "service": service_info["service_name"],
            "version": service_info["version"],
            "dependencies": service_info["dependencies"],
            "timestamp": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/examples")
async def get_examples():
    """
    Get example requests for different generation methods
    """
    return {
        "tabular_example": {
            "data": [
                {"age": 25, "income": 50000, "category": "A"},
                {"age": 30, "income": 60000, "category": "B"},
                {"age": 35, "income": 70000, "category": "A"}
            ],
            "num_rows": 1000,
            "method": "gaussian_copula"
        },
        "ctgan_example": {
            "data": [
                {"feature1": 1.5, "feature2": "category1", "target": 0},
                {"feature1": 2.3, "feature2": "category2", "target": 1}
            ],
            "num_rows": 500,
            "epochs": 300,
            "batch_size": 500
        },
        "fake_data_example": {
            "schema": {
                "name": "name",
                "email": "email",
                "phone": "phone_number",
                "address": "address",
                "company": "company"
            },
            "num_rows": 1000,
            "locale": "en_US"
        },
        "time_series_example": {
            "data": [
                {"timestamp": "2023-01-01", "value": 100, "category": "A"},
                {"timestamp": "2023-01-02", "value": 105, "category": "A"}
            ],
            "time_column": "timestamp",
            "num_sequences": 10,
            "sequence_length": 100
        }
    }