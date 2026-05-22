"""
AlphaFold 3 Protein Structure Router

Este módulo proporciona endpoints para predicción avanzada de estructuras proteicas
utilizando AlphaFold 3, incluyendo predicción de estructuras individuales, modelado
de interacciones proteína-proteína, análisis de sitios de unión y evaluación de calidad
estructural. Soporta predicción de complejos multi-cadena y análisis proteína-ligando
para investigación en biología estructural y descubrimiento de fármacos.

Capacidades principales:
- Predicción de estructuras proteicas 3D de alta precisión
- Modelado de interacciones proteína-proteína y complejos
- Análisis de sitios de unión y evaluación de druggability
- Predicción de interacciones proteína-ligando
- Evaluación de calidad estructural con puntuaciones pLDDT
- Predicción de complejos multi-cadena (hasta 10 cadenas)
- Análisis de interfaces de unión y afinidad
- Identificación de regiones desordenadas y confiables

Endpoints disponibles:
- POST /predict-structure: Predicción de estructura proteica individual
- POST /analyze-binding-sites: Análisis de sitios de unión
- POST /predict-interaction: Predicción de interacción proteína-proteína
- POST /structure-quality: Evaluación de calidad estructural
- POST /predict-complex: Predicción de complejo multi-cadena
- POST /predict-protein-ligand: Predicción de interacción proteína-ligando
- GET /health: Verificación del estado del servicio
- GET /capabilities: Capacidades del servicio
- GET /examples: Ejemplos de uso prácticos

Dependencias:
- AlphaFold3ProteinStructureService: Servicio principal de predicción
- ProteinStructurePredictionRequest: Solicitud de predicción de estructura
- BindingSiteAnalysisRequest: Solicitud de análisis de sitios de unión
- ProteinInteractionRequest: Solicitud de interacción proteína-proteína
- StructureQualityRequest: Solicitud de evaluación de calidad
- ComplexPredictionRequest: Solicitud de predicción de complejo
- ProteinLigandRequest: Solicitud de interacción proteína-ligando

Uso típico:
    from app.domains.medicine.routers.alphafold3 import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles sin prefijo específico
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..personalized.alphafold3_service import AlphaFold3ProteinStructureService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.medicine import MedicalError

# Create router
router = APIRouter()

# Initialize service with lazy loading
alphafold_service = None

def get_alphafold_service():
    global alphafold_service
    if alphafold_service is None:
        alphafold_service = AlphaFold3ProteinStructureService()
    return alphafold_service

# Request/Response Models
class ProteinStructurePredictionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
                "options": {
                    "confidence_threshold": 0.7,
                    "include_pdb": True
                }
            }
        }
    )

    sequence: str = Field(..., description="Protein amino acid sequence (single letter codes)")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Additional prediction options")

class BindingSiteAnalysisRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "structure_id": "af3_abc123def456_1234567890",
                "options": {
                    "min_cavity_volume": 100,
                    "druggability_threshold": 0.5
                }
            }
        }
    )

    structure_id: str = Field(..., description="ID of previously predicted structure")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Analysis options")

class ProteinInteractionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sequence_a": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
                "sequence_b": "MSIIGATRLQNDKSDTYSAGPCYAGGCSAFTPRGTCGKDWDLGEQTCASGFCTSQPLCARIKKT"
            }
        }
    )

    sequence_a: str = Field(..., description="First protein sequence")
    sequence_b: str = Field(..., description="Second protein sequence")

class StructureQualityRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "structure_id": "af3_abc123def456_1234567890"
            }
        }
    )

    structure_id: str = Field(..., description="Structure ID for quality analysis")


class ComplexPredictionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chains": [
                    {"sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG", "type": "protein"},
                    {"sequence": "MSIIGATRLQNDKSDTYSAGPCYAGGCSAFTPRGTCGKDWDLGEQTCASGFCTSQPLCARIKKT", "type": "protein"}
                ]
            }
        }
    )

    chains: List[Dict[str, str]] = Field(..., description="List of chains with sequence and type")


class ProteinLigandRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "protein_sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
                "ligand_smiles": "CC(=O)Oc1ccccc1C(=O)O"
            }
        }
    )

    protein_sequence: str = Field(..., description="Protein amino acid sequence")
    ligand_smiles: str = Field(..., description="Small molecule SMILES string")


@router.post("/predict-structure")
async def predict_protein_structure(request: ProteinStructurePredictionRequest):
    """
    Predict protein 3D structure using AlphaFold 3

    **Features:**
    - High-accuracy structure prediction
    - Per-residue confidence scores (pLDDT)
    - PDB format output
    - Quality assessment metrics

    **Use Cases:**
    - Drug discovery and design
    - Protein engineering
    - Functional annotation
    - Structural biology research

    **Input Requirements:**
    - Amino acid sequence (10-2700 residues)
    - Standard single-letter codes (A, C, D, E, F, G, H, I, K, L, M, N, P, Q, R, S, T, V, W, Y)
    """
    try:
        if not request.sequence or len(request.sequence.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Protein sequence must be at least 10 amino acids long"
            )

        if len(request.sequence.strip()) > 2700:
            raise HTTPException(
                status_code=400,
                detail="Protein sequence too long (maximum 2700 residues for AlphaFold 3)"
            )

        service = get_alphafold_service()
        result = await service.predict_protein_structure(
            request.sequence,
            request.options
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Structure prediction failed')
            )

        return {
            "status": "success",
            "message": "Protein structure predicted successfully",
            "data": result['data'],
            "metadata": {
                "service": "AlphaFold3ProteinStructureService",
                "model": "AlphaFold 3",
                "sequence_length": len(request.sequence.strip()),
                "timestamp": datetime.now().isoformat()
            }
        }

    except HTTPException:
        raise
    except MedicalError as e:
        logger.error(f"Error in structure prediction endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-binding-sites")
async def analyze_binding_sites(request: BindingSiteAnalysisRequest):
    """
    Analyze potential drug binding sites in predicted protein structure

    **Features:**
    - Cavity detection and volume calculation
    - Druggability scoring
    - Binding site ranking by confidence
    - Residue mapping for each site

    **Use Cases:**
    - Drug discovery target identification
    - Lead compound optimization
    - Allosteric site discovery
    - Structure-based drug design
    """
    try:
        if not request.structure_id:
            raise HTTPException(
                status_code=400,
                detail="Structure ID is required for binding site analysis"
            )

        service = get_alphafold_service()
        result = await service.analyze_binding_sites(
            request.structure_id,
            request.options
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Binding site analysis failed')
            )

        return {
            "status": "success",
            "message": "Binding site analysis completed successfully",
            "data": result['data'],
            "metadata": {
                "service": "AlphaFold3ProteinStructureService",
                "analysis_type": "binding_sites",
                "structure_id": request.structure_id,
                "timestamp": datetime.now().isoformat()
            }
        }

    except HTTPException:
        raise
    except MedicalError as e:
        logger.error(f"Error in binding site analysis endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-interaction")
async def predict_protein_interaction(request: ProteinInteractionRequest):
    """
    Predict protein-protein interaction using AlphaFold 3

    **Features:**
    - Interaction confidence scoring
    - Interface residue identification
    - Binding mode prediction
    - Structural compatibility assessment

    **Use Cases:**
    - Protein complex modeling
    - Interaction network analysis
    - Therapeutic target validation
    - Protein engineering for interactions
    """
    try:
        if not request.sequence_a or not request.sequence_b:
            raise HTTPException(
                status_code=400,
                detail="Both protein sequences are required for interaction prediction"
            )

        # Validate sequence lengths
        for seq_name, sequence in [("sequence_a", request.sequence_a), ("sequence_b", request.sequence_b)]:
            if len(sequence.strip()) < 10:
                raise HTTPException(
                    status_code=400,
                    detail=f"{seq_name} must be at least 10 amino acids long"
                )
            if len(sequence.strip()) > 2700:
                raise HTTPException(
                    status_code=400,
                    detail=f"{seq_name} too long (maximum 2700 residues)"
                )

        service = get_alphafold_service()
        result = await service.predict_protein_interaction(
            request.sequence_a,
            request.sequence_b
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Protein interaction prediction failed')
            )

        return {
            "status": "success",
            "message": "Protein interaction predicted successfully",
            "data": result['data'],
            "metadata": {
                "service": "AlphaFold3ProteinStructureService",
                "analysis_type": "protein_interaction",
                "sequences_analyzed": 2,
                "timestamp": datetime.now().isoformat()
            }
        }

    except HTTPException:
        raise
    except MedicalError as e:
        logger.error(f"Error in protein interaction endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/structure-quality")
async def get_structure_quality_metrics(request: StructureQualityRequest):
    """
    Get detailed quality assessment for predicted protein structure

    **Features:**
    - pLDDT score analysis and distribution
    - Confidence region mapping
    - Disorder region identification
    - Reliability assessment

    **Use Cases:**
    - Structure validation
    - Quality control for modeling
    - Confidence-based filtering
    - Experimental design guidance
    """
    try:
        if not request.structure_id:
            raise HTTPException(
                status_code=400,
                detail="Structure ID is required for quality assessment"
            )

        service = get_alphafold_service()
        result = await service.get_structure_quality_metrics(request.structure_id)

        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Quality assessment failed')
            )

        return {
            "status": "success",
            "message": "Structure quality assessment completed",
            "data": result['data'],
            "metadata": {
                "service": "AlphaFold3ProteinStructureService",
                "analysis_type": "quality_metrics",
                "structure_id": request.structure_id,
                "timestamp": datetime.now().isoformat()
            }
        }

    except HTTPException:
        raise
    except MedicalError as e:
        logger.error(f"Error in structure quality endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check for AlphaFold 3 Protein Structure Service

    Returns service status, API connectivity, and performance metrics
    """
    try:
        service = get_alphafold_service()
        health_status = await service.health_check()

        return {
            "status": "success",
            "message": "Health check completed",
            "data": health_status,
            "timestamp": datetime.now().isoformat()
        }

    except MedicalError as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "error",
            "message": "Health check failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/capabilities")
async def get_service_capabilities():
    """
    Get detailed information about AlphaFold 3 service capabilities
    """
    return {
        "status": "success",
        "data": {
            "service_name": "AlphaFold3ProteinStructureService",
            "version": "1.0.0",
            "model_version": "AlphaFold 3",
            "capabilities": [
                {
                    "name": "Protein Structure Prediction",
                    "description": "Predict 3D structure from amino acid sequence",
                    "endpoint": "/predict-structure",
                    "method": "POST",
                    "max_sequence_length": 2700
                },
                {
                    "name": "Binding Site Analysis",
                    "description": "Identify and analyze potential drug binding sites",
                    "endpoint": "/analyze-binding-sites",
                    "method": "POST"
                },
                {
                    "name": "Protein Interaction Prediction",
                    "description": "Model protein-protein interactions",
                    "endpoint": "/predict-interaction",
                    "method": "POST"
                },
                {
                    "name": "Structure Quality Assessment",
                    "description": "Comprehensive quality metrics and validation",
                    "endpoint": "/structure-quality",
                    "method": "POST"
                }
            ],
            "supported_formats": ["FASTA", "PDB", "JSON"],
            "confidence_metrics": [
                "pLDDT (per-residue confidence)",
                "Overall prediction confidence",
                "Domain reliability scores",
                "Disorder region identification"
            ],
            "applications": [
                "Drug Discovery",
                "Protein Engineering",
                "Structural Biology",
                "Functional Annotation",
                "Interaction Networks"
            ],
            "limitations": {
                "min_sequence_length": 10,
                "max_sequence_length": 2700,
                "prediction_time": "2-5 seconds per structure",
                "cache_duration": "24 hours"
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/examples")
async def get_usage_examples():
    """
    Get practical usage examples for different protein analysis scenarios
    """
    return {
        "status": "success",
        "data": {
            "drug_discovery_workflow": {
                "step_1": "Predict target protein structure",
                "step_2": "Analyze binding sites for druggability",
                "step_3": "Identify high-confidence cavities",
                "step_4": "Use for virtual screening"
            },
            "protein_engineering_workflow": {
                "step_1": "Predict wild-type structure",
                "step_2": "Assess quality and confidence",
                "step_3": "Model mutations or modifications",
                "step_4": "Compare structural changes"
            },
            "interaction_analysis_workflow": {
                "step_1": "Predict individual protein structures",
                "step_2": "Model protein-protein interaction",
                "step_3": "Analyze interface residues",
                "step_4": "Assess interaction confidence"
            },
            "sample_sequences": {
                "small_protein": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
                "medium_protein": "MSIIGATRLQNDKSDTYSAGPCYAGGCSAFTPRGTCGKDWDLGEQTCASGFCTSQPLCARIKKTQPAVIPRRGCYAGKGTSAFTPRGTCGKDWDLGEQTCASGFCTS",
                "enzyme_example": "MAEGEITTFTALTEKFNLPPGNYKKPKLLYCSNGGHFLRILPDGTVDGTRDRSDQHIQLQLSAESVGEVYIKSTETGQYLAMDTSGLLYGSQTPSEECLFLERLEENHYNTYTSKKHAEKNWFVGLKKNGSCKRGPRTHYGQKAILFLPLPV"
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@router.post("/predict-complex")
async def predict_complex_structure(request: ComplexPredictionRequest):
    """
    Predict structure of multi-chain protein complex using AlphaFold 3

    **Features:**
    - Multi-protein complex modeling
    - Interface analysis and binding affinity estimation
    - Per-chain confidence assessment
    - Complex stability prediction

    **Use Cases:**
    - Protein complex assembly
    - Interaction interface mapping
    - Therapeutic target validation
    - Structural biology research

    **Input Requirements:**
    - 2-10 chains (protein, DNA, or RNA)
    - Each chain: sequence and type specification
    """
    try:
        if not request.chains or len(request.chains) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 chains required for complex prediction"
            )

        if len(request.chains) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 chains supported"
            )

        service = get_alphafold_service()
        result = await service.predict_complex(request.chains)

        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Complex prediction failed')
            )

        return {
            "status": "success",
            "message": "Complex structure predicted successfully",
            "data": result['data'],
            "metadata": {
                "service": "AlphaFold3ProteinStructureService",
                "analysis_type": "complex_prediction",
                "chain_count": len(request.chains),
                "timestamp": datetime.now().isoformat()
            }
        }

    except HTTPException:
        raise
    except MedicalError as e:
        logger.error(f"Error in complex prediction endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-protein-ligand")
async def predict_protein_ligand_interaction(request: ProteinLigandRequest):
    """
    Predict protein-ligand interaction using AlphaFold 3

    **Features:**
    - Binding affinity prediction
    - Binding site identification
    - Ligand pose prediction
    - Druggability assessment
    - Pharmacophore mapping

    **Use Cases:**
    - Drug discovery and design
    - Lead compound optimization
    - ADMET prediction
    - Virtual screening validation

    **Input Requirements:**
    - Protein amino acid sequence (10-2700 residues)
    - Small molecule SMILES string
    """
    try:
        if not request.protein_sequence or len(request.protein_sequence.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Protein sequence must be at least 10 amino acids long"
            )

        if not request.ligand_smiles or len(request.ligand_smiles.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Valid SMILES string required for ligand"
            )

        service = get_alphafold_service()
        result = await service.predict_protein_ligand(
            request.protein_sequence,
            request.ligand_smiles
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Protein-ligand prediction failed')
            )

        return {
            "status": "success",
            "message": "Protein-ligand interaction predicted successfully",
            "data": result['data'],
            "metadata": {
                "service": "AlphaFold3ProteinStructureService",
                "analysis_type": "protein_ligand_interaction",
                "protein_length": len(request.protein_sequence.strip()),
                "ligand_smiles": request.ligand_smiles,
                "timestamp": datetime.now().isoformat()
            }
        }

    except HTTPException:
        raise
    except MedicalError as e:
        logger.error(f"Error in protein-ligand prediction endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
