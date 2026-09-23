"""
Advanced Mathematical NLP Router

Este módulo proporciona endpoints para procesamiento de lenguaje natural avanzado aplicado
a problemas matemáticos, incluyendo análisis inteligente de problemas, solución paso a paso,
generación de problemas similares y explicación de conceptos matemáticos. Utiliza modelos
de IA para clasificación automática de problemas, evaluación de dificultad y recomendaciones
de métodos de solución.

Capacidades principales:
- Análisis inteligente de problemas matemáticos con clasificación automática
- Evaluación automática de dificultad y complejidad
- Extracción de entidades matemáticas (variables, parámetros, expresiones)
- Detección de ambigüedades y recomendaciones de métodos de solución
- Generación de soluciones paso a paso con explicaciones detalladas
- Creación de problemas similares para práctica y aprendizaje
- Explicación de conceptos matemáticos con ejemplos y aplicaciones
- Memoria de conversación para contexto en resolución de problemas
- Soporte multi-dominio (matemáticas puras, física, química, economía)

Endpoints disponibles:
- POST /analyze-problem: Análisis completo de problemas matemáticos
- POST /solve-with-steps: Solución paso a paso con explicaciones
- POST /generate-problems: Generación de problemas de práctica
- GET /conversation-history: Historial de conversación para contexto
- DELETE /conversation-history: Limpieza del historial de conversación
- GET /service-stats: Estadísticas y métricas del servicio
- GET /capabilities: Capacidades avanzadas del servicio NLP
- POST /explain-concept: Explicación detallada de conceptos matemáticos
- GET /examples: Ejemplos de consultas avanzadas
- GET /health: Verificación del estado del servicio

Dependencias:
- AdvancedMathNLPService: Servicio principal de NLP matemático avanzado
- ProblemType, Difficulty: Enumeraciones para clasificación de problemas
- BaseResponse: Modelo de respuesta estándar
- AdvancedMathNLPRequest, ProblemAnalysisResponse: Modelos de solicitud y respuesta

Uso típico:
    from app.domains.mathematics.services.advanced_math_nlp import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles sin prefijo específico
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.domains.mathematics.services.advanced_math_nlp import AdvancedMathNLPService, ProblemType, Difficulty
from app.models import BaseResponse
import logging
from app.exceptions.domain.mathematics import MathematicsError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the advanced service
try:
    advanced_service = AdvancedMathNLPService()
    logger.info("Advanced Math NLP Service initialized successfully")
except MathematicsError as e:
    logger.error(f"Failed to initialize Advanced Math NLP Service: {e}")
    advanced_service = None

class AdvancedMathNLPRequest(BaseModel):
    """Request model for advanced mathematical NLP"""
    text: str
    context: Optional[Dict[str, Any]] = None
    generate_similar: bool = False
    similar_count: int = 3

class ProblemAnalysisResponse(BaseModel):
    """Response model for problem analysis"""
    success: bool
    message: str
    data: Dict[str, Any]

@router.post("/analyze-problem", response_model=ProblemAnalysisResponse)
async def analyze_mathematical_problem(request: AdvancedMathNLPRequest):
    """
    Analyze a mathematical problem using advanced NLP techniques
    
    This endpoint provides:
    - Problem type classification
    - Difficulty assessment
    - Mathematical entity extraction
    - Ambiguity detection
    - Solution method recommendations
    """
    try:
        if advanced_service is None:
            raise HTTPException(status_code=503, detail="Advanced NLP service not available")
        
        # Analyze the problem
        problem = advanced_service.analyze_mathematical_problem(
            request.text, 
            request.context
        )
        
        # Generate similar problems if requested
        similar_problems = []
        if request.generate_similar:
            similar_problems = advanced_service.generate_similar_problems(
                problem, 
                request.similar_count
            )
        
        return ProblemAnalysisResponse(
            success=True,
            message="Problem analyzed successfully",
            data={
                "problem_analysis": {
                    "original_text": problem.original_text,
                    "problem_type": problem.problem_type.value,
                    "difficulty": problem.difficulty.value,
                    "parsed_expression": problem.parsed_expression,
                    "variables": problem.variables,
                    "parameters": problem.parameters,
                    "confidence": problem.confidence,
                    "ambiguities": problem.ambiguities,
                    "suggested_methods": problem.suggested_methods,
                    "context": problem.context
                },
                "similar_problems": similar_problems
            }
        )
    
    except MathematicsError as e:
        logger.error(f"Error analyzing problem: {e}")
        raise HTTPException(status_code=400, detail=f"Problem analysis failed: {str(e)}")

@router.post("/solve-with-steps", response_model=None)
async def solve_problem_with_steps(request: AdvancedMathNLPRequest):
    """
    Solve a mathematical problem with detailed step-by-step explanation
    
    This endpoint provides:
    - Complete problem analysis
    - Step-by-step solution process
    - Mathematical verification
    - Solution confidence assessment
    """
    try:
        if advanced_service is None:
            raise HTTPException(status_code=503, detail="Advanced NLP service not available")
        
        # First analyze the problem
        problem = advanced_service.analyze_mathematical_problem(
            request.text, 
            request.context
        )
        
        # Generate step-by-step solution
        solution = advanced_service.generate_step_by_step_solution(problem)
        
        return BaseResponse(
            success=True,
            message="Problem solved with detailed steps",
            data=solution
        )
    
    except MathematicsError as e:
        logger.error(f"Error solving problem: {e}")
        raise HTTPException(status_code=400, detail=f"Problem solving failed: {str(e)}")

@router.post("/generate-problems", response_model=None)
async def generate_practice_problems(
    problem_type: str = "algebra",
    difficulty: str = "intermediate",
    count: int = 5
):
    """
    Generate practice problems of specified type and difficulty
    
    Available problem types:
    - arithmetic, algebra, calculus, geometry, statistics, physics
    
    Available difficulty levels:
    - beginner, intermediate, advanced, expert
    """
    try:
        if advanced_service is None:
            raise HTTPException(status_code=503, detail="Advanced NLP service not available")
        
        # Create a sample problem for template generation
        sample_text = f"Generate {problem_type} problems at {difficulty} level"
        sample_problem = advanced_service.analyze_mathematical_problem(sample_text)
        
        # Override the detected type and difficulty
        sample_problem.problem_type = ProblemType(problem_type.lower())
        sample_problem.difficulty = Difficulty(difficulty.lower())
        
        # Generate problems
        generated_problems = advanced_service.generate_similar_problems(
            sample_problem, 
            count
        )
        
        return BaseResponse(
            success=True,
            message=f"Generated {len(generated_problems)} {difficulty} {problem_type} problems",
            data={
                "problem_type": problem_type,
                "difficulty": difficulty,
                "count": len(generated_problems),
                "problems": generated_problems
            }
        )
    
    except MathematicsError as e:
        logger.error(f"Error generating problems: {e}")
        raise HTTPException(status_code=400, detail=f"Problem generation failed: {str(e)}")

@router.get("/conversation-history", response_model=None)
async def get_conversation_history():
    """
    Get conversation history for context-aware problem solving
    """
    try:
        if advanced_service is None:
            raise HTTPException(status_code=503, detail="Advanced NLP service not available")
        
        history = advanced_service.get_conversation_context()
        
        return BaseResponse(
            success=True,
            message="Conversation history retrieved",
            data={
                "history": history,
                "total_problems": len(history)
            }
        )
    
    except MathematicsError as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(status_code=400, detail=f"History retrieval failed: {str(e)}")

@router.delete("/conversation-history", response_model=None)
async def clear_conversation_history():
    """
    Clear conversation history
    """
    try:
        if advanced_service is None:
            raise HTTPException(status_code=503, detail="Advanced NLP service not available")
        
        advanced_service.clear_conversation_history()
        
        return BaseResponse(
            success=True,
            message="Conversation history cleared",
            data={"status": "cleared"}
        )
    
    except MathematicsError as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(status_code=400, detail=f"History clearing failed: {str(e)}")

@router.get("/service-stats", response_model=None)
async def get_service_statistics():
    """
    Get advanced NLP service statistics and performance metrics
    """
    try:
        if advanced_service is None:
            raise HTTPException(status_code=503, detail="Advanced NLP service not available")
        
        stats = advanced_service.get_service_stats()
        
        return BaseResponse(
            success=True,
            message="Service statistics retrieved",
            data=stats
        )
    
    except MathematicsError as e:
        logger.error(f"Error retrieving service stats: {e}")
        raise HTTPException(status_code=400, detail=f"Stats retrieval failed: {str(e)}")

@router.get("/capabilities", response_model=None)
async def get_advanced_capabilities():
    """
    Get information about advanced NLP capabilities
    """
    return BaseResponse(
        success=True,
        message="Advanced NLP capabilities",
        data={
            "features": [
                "Advanced semantic analysis using AI models",
                "Intelligent problem type classification",
                "Automatic difficulty assessment",
                "Mathematical entity extraction",
                "Ambiguity detection and resolution",
                "Context-aware solution method recommendations",
                "Step-by-step solution generation",
                "Similar problem generation for practice",
                "Conversation history and context memory",
                "Multi-domain problem support (math, physics, chemistry)"
            ],
            "problem_types": [pt.value for pt in ProblemType],
            "difficulty_levels": [d.value for d in Difficulty],
            "supported_domains": [
                "pure_mathematics",
                "physics",
                "chemistry",
                "economics",
                "engineering",
                "computer_science"
            ],
            "ai_models": [
                "Question-Answering (RoBERTa-base)",
                "Text Classification",
                "Mathematical Expression Parser",
                "Symbolic Mathematics Engine (SymPy)"
            ],
            "example_queries": [
                "Solve the quadratic equation x^2 + 5x + 6 = 0",
                "Find the derivative of sin(x) * cos(x)",
                "Calculate the area of a circle with radius 7 meters",
                "What is the probability of rolling a 6 on a fair die?",
                "Optimize the function f(x) = x^2 - 4x + 3",
                "Solve the system: 2x + 3y = 7 and x - y = 1"
            ]
        }
    )

@router.post("/explain-concept", response_model=None)
async def explain_mathematical_concept(request: AdvancedMathNLPRequest):
    """
    Explain a mathematical concept in detail
    
    This endpoint analyzes the concept and provides:
    - Detailed explanation
    - Related concepts
    - Example problems
    - Applications
    """
    try:
        if advanced_service is None:
            raise HTTPException(status_code=503, detail="Advanced NLP service not available")
        
        # Analyze the concept
        problem = advanced_service.analyze_mathematical_problem(
            request.text, 
            request.context
        )
        
        # Generate explanation based on problem type
        explanation = {
            "concept": request.text,
            "problem_type": problem.problem_type.value,
            "difficulty": problem.difficulty.value,
            "explanation": f"This is a {problem.problem_type.value} concept at {problem.difficulty.value} level.",
            "key_components": problem.variables,
            "related_methods": problem.suggested_methods,
            "applications": problem.context.get("domain", "mathematics"),
            "confidence": problem.confidence
        }
        
        # Add domain-specific information
        if problem.context.get("domain") == "physics":
            explanation["physics_applications"] = [
                "Mechanics", "Electromagnetism", "Thermodynamics", "Quantum Physics"
            ]
        elif problem.context.get("domain") == "chemistry":
            explanation["chemistry_applications"] = [
                "Stoichiometry", "Kinetics", "Thermodynamics", "Quantum Chemistry"
            ]
        
        return BaseResponse(
            success=True,
            message="Mathematical concept explained",
            data=explanation
        )
    
    except MathematicsError as e:
        logger.error(f"Error explaining concept: {e}")
        raise HTTPException(status_code=400, detail=f"Concept explanation failed: {str(e)}")

@router.get("/examples", response_model=None)
async def get_advanced_examples():
    """
    Get examples of advanced mathematical NLP queries
    """
    return BaseResponse(
        success=True,
        message="Advanced NLP examples",
        data={
            "problem_analysis_examples": [
                {
                    "query": "Find the derivative of x^3 + 2x^2 - 5x + 1",
                    "expected_type": "calculus",
                    "expected_difficulty": "intermediate",
                    "features": ["derivative", "polynomial", "step-by-step"]
                },
                {
                    "query": "Solve the system of equations: 3x + 2y = 7 and x - 4y = -1",
                    "expected_type": "algebra",
                    "expected_difficulty": "intermediate",
                    "features": ["system_of_equations", "linear_algebra", "elimination"]
                }
            ],
            "step_by_step_examples": [
                {
                    "query": "Integrate x^2 * sin(x) dx",
                    "steps": ["Integration by parts", "u-substitution", "Simplification"],
                    "difficulty": "advanced"
                }
            ],
            "concept_explanation_examples": [
                {
                    "query": "Explain the chain rule in calculus",
                    "response_type": "detailed_explanation",
                    "includes": ["definition", "examples", "applications"]
                }
            ]
        }
    )

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check for the advanced NLP service
    """
    service_status = "healthy" if advanced_service is not None else "unavailable"
    
    return {
        "service": "Advanced Mathematical NLP",
        "status": service_status,
        "version": "1.0.0",
        "features": [
            "AI-powered problem analysis",
            "Step-by-step solutions",
            "Problem generation",
            "Concept explanation"
        ]
    }
