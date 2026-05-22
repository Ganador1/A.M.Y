"""
Computational Chemistry Router

Este módulo proporciona endpoints para química computacional intuitiva, incluyendo
análisis de propiedades moleculares, generación de conformeros, análisis de secuencias
biológicas y cálculos de química cuántica. Utiliza bibliotecas como RDKit y PySCF
para proporcionar análisis detallados con explicaciones amigables para usuarios
no expertos en computación química.

Capacidades principales:
- Análisis de propiedades moleculares con descriptores químicos
- Generación y optimización de conformeros moleculares
- Análisis de secuencias biológicas (DNA, RNA, proteínas)
- Cálculos de química cuántica con múltiples métodos
- Análisis molecular rápido con resultados simplificados
- Cálculo de contenido GC, pesos moleculares y propiedades fisicoquímicas
- Generación de secuencias complementarias y análisis de composición
- Evaluación de lipofilicidad, solubilidad y reactividad química

Endpoints disponibles:
- GET /: Página principal con información general
- GET /info: Información detallada de bibliotecas disponibles
- GET /examples: Ejemplos prácticos de uso
- POST /analyze-molecule: Análisis de propiedades moleculares
- POST /generate-conformers: Generación de conformeros
- POST /analyze-sequence: Análisis de secuencias biológicas
- POST /quantum-chemistry: Cálculos de química cuántica
- GET /quick-analysis/{smiles}: Análisis molecular rápido

Dependencias:
- ComputationalChemistryService: Servicio principal de química computacional
- BaseResponse: Modelo de respuesta estándar
- RDKit: Biblioteca para química computacional
- PySCF: Biblioteca para química cuántica

Consideraciones éticas y de seguridad:
- No usar para decisiones clínicas sin validación experta
- No subir información personal identificable
- Resultados son orientativos; validar con métodos experimentales
- Limitar tamaños de moléculas y complejidad de cálculos

Uso típico:
    from app.domains.mathematics.routers.computational_chemistry import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles sin prefijo específico
"""

from fastapi import APIRouter, HTTPException
from ..computational.computational_chemistry_service import ComputationalChemistryService
from app.domains.models import BaseResponse
from typing import Optional
from app.exceptions.domain.chemistry import ChemistryError

router = APIRouter()
service = ComputationalChemistryService()

@router.get("/", response_model=BaseResponse)
async def get_chemistry_home():
    """
    Página principal de química computacional con información general
    """
    return BaseResponse(
        success=True,
        message="Bienvenido a la química computacional de Mathematics AI",
        data={
            "description": "Análisis molecular, conformeros, secuencias biológicas y química cuántica",
            "available_operations": [
                "Análisis de propiedades moleculares",
                "Generación de conformeros",
                "Análisis de secuencias biológicas",
                "Cálculos de química cuántica"
            ],
            "examples": {
                "molecular_analysis": "POST /api/chemistry/analyze-molecule con SMILES",
                "sequence_analysis": "POST /api/chemistry/analyze-sequence con DNA/RNA/Proteína",
                "quantum_chemistry": "POST /api/chemistry/quantum-chemistry con coordenadas atómicas"
            }
        }
    )

@router.get("/info", response_model=BaseResponse)
async def get_chemistry_info():
    """
    Información detallada sobre las bibliotecas de química disponibles
    """
    try:
        result = service.get_service_info()
        return BaseResponse(
            success=True,
            message="Información de bibliotecas de química computacional",
            data=result
        )
    except ChemistryError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/examples", response_model=BaseResponse)
async def get_chemistry_examples():
    """
    Ejemplos prácticos de uso de química computacional
    """
    return BaseResponse(
        success=True,
        message="Ejemplos de química computacional",
        data={
            "molecular_examples": [
                {
                    "name": "Análisis de etanol",
                    "smiles": "CCO",
                    "description": "Análisis de propiedades del etanol",
                    "endpoint": "POST /api/chemistry/analyze-molecule",
                    "expected_properties": ["peso molecular", "logP", "TPSA"]
                },
                {
                    "name": "Análisis de benceno",
                    "smiles": "c1ccccc1",
                    "description": "Análisis del benceno aromático",
                    "endpoint": "POST /api/chemistry/analyze-molecule",
                    "expected_properties": ["estructura aromática", "descriptores moleculares"]
                },
                {
                    "name": "Análisis de cafeína",
                    "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
                    "description": "Análisis de la cafeína",
                    "endpoint": "POST /api/chemistry/analyze-molecule",
                    "expected_properties": ["peso molecular alto", "múltiples grupos funcionales"]
                }
            ],
            "sequence_examples": [
                {
                    "name": "Análisis de DNA simple",
                    "sequence": "ATCGATCG",
                    "sequence_type": "dna",
                    "description": "Análisis de secuencia de DNA corta",
                    "endpoint": "POST /api/chemistry/analyze-sequence",
                    "expected_results": ["GC content: 50%", "peso molecular"]
                },
                {
                    "name": "Análisis de RNA",
                    "sequence": "AUGCUAGU",
                    "sequence_type": "rna",
                    "description": "Análisis de secuencia de RNA",
                    "endpoint": "POST /api/chemistry/analyze-sequence",
                    "expected_results": ["tipo RNA", "contenido GC"]
                },
                {
                    "name": "Análisis de proteína",
                    "sequence": "MAKETLK",
                    "sequence_type": "protein",
                    "description": "Análisis de secuencia peptídica",
                    "endpoint": "POST /api/chemistry/analyze-sequence",
                    "expected_results": ["tipo proteína", "peso molecular"]
                }
            ],
            "quantum_examples": [
                {
                    "name": "Molécula de hidrógeno",
                    "atom": "H 0 0 0; H 0 0 0.74",
                    "basis": "sto-3g",
                    "description": "Cálculo cuántico de H₂",
                    "endpoint": "POST /api/chemistry/quantum-chemistry",
                    "expected_results": ["energía molecular", "propiedades cuánticas"]
                }
            ],
            "tips": [
                "Usa SMILES para representar moléculas (ej: CCO = etanol)",
                "Los tipos de secuencia soportados son: dna, rna, protein",
                "Para química cuántica necesitas coordenadas atómicas en formato PySCF",
                "Verifica /api/chemistry/info para disponibilidad de bibliotecas"
            ]
        }
    )

@router.post("/analyze-molecule", response_model=BaseResponse)
async def analyze_molecule(
    smiles: str,
    detailed: Optional[bool] = False
):
    """
    Analiza propiedades moleculares de forma intuitiva

    Args:
        smiles: Notación SMILES de la molécula (ej: "CCO" para etanol)
        detailed: Si es True, incluye análisis más detallado

    Returns:
        Propiedades moleculares con explicaciones
    """
    try:
        result = service.analyze_molecule(smiles)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Agregar explicaciones amigables
        if "descriptors" in result:
            explanations = {
                "molecular_weight": "Peso molecular total de la molécula",
                "logp": "Coeficiente de partición octanol-agua (lipofilicidad)",
                "tpsa": "Área superficial polar topológica (relación con solubilidad)",
                "hbd": "Número de donadores de enlaces de hidrógeno",
                "hba": "Número de aceptores de enlaces de hidrógeno",
                "rotatable_bonds": "Enlaces rotables (afectan flexibilidad molecular)",
                "rings": "Número de anillos en la molécula",
                "heavy_atoms": "Átomos que no son hidrógeno"
            }
            result["explanations"] = explanations

        response_message = f"Análisis molecular completado para {smiles}"
        if detailed:
            response_message += " (análisis detallado)"

        return BaseResponse(
            success=True,
            message=response_message,
            data=result
        )
    except ChemistryError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error analizando molécula: {str(e)}. Verifica el formato SMILES."
        )

@router.post("/generate-conformers", response_model=BaseResponse)
async def generate_conformers(
    smiles: str,
    num_conformers: int = 10,
    optimize: Optional[bool] = True
):
    """
    Genera conformeros moleculares de forma intuitiva

    Args:
        smiles: SMILES de la molécula
        num_conformers: Número de conformeros a generar (1-50)
        optimize: Si optimizar la geometría de los conformeros

    Returns:
        Conformeros generados con información detallada
    """
    try:
        if num_conformers < 1 or num_conformers > 50:
            raise HTTPException(
                status_code=400,
                detail="El número de conformeros debe estar entre 1 y 50"
            )

        result = service.generate_conformers(smiles, num_conformers)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Agregar información adicional
        result["parameters"] = {
            "smiles": smiles,
            "num_conformers_requested": num_conformers,
            "optimization": optimize
        }

        return BaseResponse(
            success=True,
            message=f"Generados {len(result.get('conformers', []))} conformeros para {smiles}",
            data=result
        )
    except ChemistryError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error generando conformeros: {str(e)}. Verifica el SMILES y parámetros."
        )

@router.post("/analyze-sequence", response_model=BaseResponse)
async def analyze_sequence(
    sequence: str,
    sequence_type: str = "dna"
):
    """
    Analiza secuencias biológicas de forma intuitiva

    Args:
        sequence: Secuencia biológica (DNA, RNA o proteína)
        sequence_type: Tipo de secuencia ("dna", "rna", "protein")

    Returns:
        Análisis completo de la secuencia
    """
    try:
        if sequence_type not in ["dna", "rna", "protein"]:
            raise HTTPException(
                status_code=400,
                detail="Tipo de secuencia debe ser: dna, rna, o protein"
            )

        result = service.analyze_sequence(sequence, sequence_type)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Agregar explicaciones
        explanations = {
            "sequence": f"Secuencia original ({sequence_type.upper()})",
            "type": f"Tipo identificado: {sequence_type.upper()}",
            "length": "Longitud total de la secuencia",
            "gc_content": "Porcentaje de nucleótidos G+C (solo para DNA/RNA)",
            "molecular_weight": "Peso molecular calculado",
            "complement": "Secuencia complementaria",
            "reverse_complement": "Secuencia complementaria reversa"
        }
        result["explanations"] = explanations

        return BaseResponse(
            success=True,
            message=f"Análisis de secuencia {sequence_type.upper()} completado",
            data=result
        )
    except ChemistryError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error analizando secuencia: {str(e)}. Verifica el tipo y formato."
        )

@router.post("/quantum-chemistry", response_model=BaseResponse)
async def quantum_chemistry_calculation(
    atom: str = "H 0 0 0; H 0 0 0.74",
    basis: str = "sto-3g",
    method: Optional[str] = "hf"
):
    """
    Realiza cálculos de química cuántica

    Args:
        atom: Coordenadas atómicas en formato PySCF
        basis: Base para el cálculo (sto-3g, 6-31g, etc.)
        method: Método cuántico (hf, dft, mp2, etc.)

    Returns:
        Resultados del cálculo cuántico
    """
    try:
        molecule_data = {"atom": atom, "basis": basis, "method": method}
        result = service.quantum_chemistry_calculation(molecule_data)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Agregar información sobre el cálculo
        result["calculation_info"] = {
            "method": method or "hf",
            "basis_set": basis,
            "atomic_coordinates": atom,
            "description": f"Cálculo {(method or 'hf').upper()} con base {basis}"
        }

        return BaseResponse(
            success=True,
            message="Cálculo de química cuántica completado exitosamente",
            data=result
        )
    except ChemistryError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en cálculo cuántico: {str(e)}. Verifica las coordenadas atómicas."
        )

@router.get("/quick-analysis/{smiles}")
async def quick_molecular_analysis(smiles: str):
    """
    Análisis molecular rápido con parámetros en la URL

    Ejemplos:
    - /api/chemistry/quick-analysis/CCO (etanol)
    - /api/chemistry/quick-analysis/c1ccccc1 (benceno)

    Args:
        smiles: SMILES de la molécula

    Returns:
        Análisis molecular básico
    """
    try:
        result = service.analyze_molecule(smiles)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return BaseResponse(
            success=True,
            message=f"Análisis rápido de {smiles}",
            data={
                "smiles": smiles,
                "molecular_weight": result.get("descriptors", {}).get("molecular_weight"),
                "formula": result.get("descriptors", {}).get("formula"),
                "quick_facts": [
                    f"Peso molecular: {result.get('descriptors', {}).get('molecular_weight', 'N/A')} Da",
                    f"Fórmula: {result.get('descriptors', {}).get('formula', 'N/A')}",
                    f"Átomos pesados: {result.get('descriptors', {}).get('heavy_atoms', 'N/A')}"
                ]
            }
        )
    except ChemistryError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en análisis rápido: {str(e)}. Verifica el SMILES."
        )
