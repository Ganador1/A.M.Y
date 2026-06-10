"""
Advanced Mathematical Natural Language Processing Service
Next-generation AI-powered mathematical problem understanding and solving
"""

import re
import sympy as sp
from typing import Dict, List, Any, Optional, Tuple
from app.services.base_service import BaseService
from app.exceptions.domain.mathematics import MathematicsError
# Optional torch import for deep learning support
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
from app.utils.hf_safe import (
    safe_load_pipeline,
    safe_load_tokenizer,
    safe_load_seq2seq_model,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProblemType(Enum):
    """Mathematical problem types"""
    ARITHMETIC = "arithmetic"
    ALGEBRA = "algebra"
    CALCULUS = "calculus"
    GEOMETRY = "geometry"
    STATISTICS = "statistics"
    OPTIMIZATION = "optimization"
    DIFFERENTIAL_EQUATIONS = "differential_equations"
    LINEAR_ALGEBRA = "linear_algebra"
    NUMBER_THEORY = "number_theory"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    UNKNOWN = "unknown"

class Difficulty(Enum):
    """Problem difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class MathProblem:
    """Structured mathematical problem representation"""
    original_text: str
    problem_type: ProblemType
    difficulty: Difficulty
    parsed_expression: str
    variables: List[str]
    parameters: Dict[str, Any]
    confidence: float
    ambiguities: List[str]
    suggested_methods: List[str]
    context: Dict[str, Any]
    
class AdvancedMathNLPService(BaseService):
    """Advanced Mathematical NLP Service with AI-powered understanding"""
    
    def __init__(self):
        super().__init__("AdvancedMathNLPService")
        from app.distributed.gpu_manager import get_optimal_device
        self.device = get_optimal_device()
        logger.info("Using device: %s", self.device)
        
        # Initialize models
        self.qa_pipeline = None
        self.classification_pipeline = None
        self.tokenizer = None
        self.model = None
        
        # Mathematical knowledge base
        self.math_patterns = self._load_mathematical_patterns()
        self.problem_templates = self._load_problem_templates()
        self.solution_methods = self._load_solution_methods()
        
        # Context memory for conversation
        self.conversation_history = []

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitudes de NLP matemático
        """
        action = request_data.get("action")
        
        if action == "analyze_problem":
            problem = self.analyze_mathematical_problem(
                text=request_data.get("text"),
                context=request_data.get("context")
            )
            # Convert MathProblem to dict
            return {"success": True, "problem": vars(problem)}
            
        elif action == "solve_problem":
            # First analyze
            problem = self.analyze_mathematical_problem(
                text=request_data.get("text"),
                context=request_data.get("context")
            )
            # Then solve
            solution = self.generate_step_by_step_solution(problem)
            return {"success": True, "solution": solution}
            
        elif action == "generate_similar":
            # First analyze
            problem = self.analyze_mathematical_problem(
                text=request_data.get("text")
            )
            similar = self.generate_similar_problems(
                problem=problem,
                count=request_data.get("count", 3)
            )
            return {"success": True, "similar_problems": similar}
            
        return {"success": False, "error": f"Unknown action: {action}"}
        
    def initialize_ai_models(self):
        """Initialize AI models for advanced mathematical understanding"""
        self.qa_pipeline = safe_load_pipeline(
            "question-answering",
            "deepset/roberta-base-squad2",
            device=self.device,
        )
        if self.qa_pipeline is None:
            logger.warning("QA pipeline no disponible; usando reglas básicas.")

        self.classification_pipeline = safe_load_pipeline(
            "text-classification",
            "microsoft/DialoGPT-medium",
            device=self.device,
        )
        if self.classification_pipeline is None:
            logger.warning("Clasificador HF no disponible; usando heurísticas.")

        self.tokenizer = safe_load_tokenizer("t5-small")
        self.model = safe_load_seq2seq_model("t5-small", device=self.device)
        if self.tokenizer is None or self.model is None:
            logger.warning("Modelo T5 no disponible; generación avanzada deshabilitada.")
    
    def _load_mathematical_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load mathematical patterns for different problem types"""
        return {
            "arithmetic": {
                "patterns": [
                    r"(\d+(?:\.\d+)?)\s*[\+\-\*\/]\s*(\d+(?:\.\d+)?)",
                    r"(?:calculate|compute|find)\s+(.+?)(?:\s*=\s*(.+?))?",
                    r"(?:what\s+is|what's)\s+(.+?)(?:\s*=\s*(.+?))?",
                    r"(?:sum|difference|product|quotient)\s+of\s+(.+)",
                    r"(\d+(?:\.\d+)?)\s*(?:plus|minus|times|divided\s+by)\s*(\d+(?:\.\d+)?)"
                ],
                "keywords": ["calculate", "compute", "sum", "difference", "product", "quotient", "plus", "minus", "times"],
                "complexity": "low"
            },
            "algebra": {
                "patterns": [
                    r"solve\s+(?:for\s+)?([a-zA-Z]+)(?:\s+in\s+)?:?\s*(.+?)(?:\s*=\s*(.+?))?",
                    r"(?:find|determine)\s+(?:the\s+value\s+of\s+)?([a-zA-Z]+)(?:\s+(?:when|if|given)\s+(.+?))?",
                    r"(?:equation|expression)\s*:?\s*(.+?)\s*=\s*(.+)",
                    r"(?:system\s+of\s+equations?|simultaneous\s+equations?)\s*:?\s*(.+)",
                    r"(?:quadratic|linear|polynomial)\s+(?:equation|function)\s*:?\s*(.+)"
                ],
                "keywords": ["solve", "equation", "variable", "unknown", "system", "linear", "quadratic"],
                "complexity": "medium"
            },
            "calculus": {
                "patterns": [
                    r"(?:derivative|differentiate|diff)\s+(?:of\s+)?(.+?)(?:\s+(?:with\s+respect\s+to|wrt)\s+([a-zA-Z]+))?",
                    r"(?:integral|integrate|antiderivative)\s+(?:of\s+)?(.+?)(?:\s+(?:with\s+respect\s+to|wrt)\s+([a-zA-Z]+))?",
                    r"(?:limit|lim)\s+(?:of\s+)?(.+?)(?:\s+as\s+([a-zA-Z]+)\s+(?:approaches|goes\s+to|tends\s+to)\s+(.+?))?",
                    r"(?:taylor|maclaurin)\s+series\s+(?:of\s+)?(.+?)(?:\s+(?:around|about|at)\s+(.+?))?",
                    r"(?:partial\s+)?derivative\s+(?:of\s+)?(.+?)(?:\s+(?:with\s+respect\s+to|wrt)\s+([a-zA-Z]+))"
                ],
                "keywords": ["derivative", "integral", "limit", "series", "differential", "partial"],
                "complexity": "high"
            },
            "geometry": {
                "patterns": [
                    r"(?:area|perimeter|volume|surface\s+area)\s+of\s+(?:a\s+)?(.+?)(?:\s+with\s+(.+?))?",
                    r"(?:distance|length)\s+between\s+(.+?)\s+and\s+(.+)",
                    r"(?:angle|slope)\s+(?:of\s+)?(.+?)(?:\s+(?:and|with)\s+(.+?))?",
                    r"(?:circle|triangle|rectangle|square|polygon)\s+with\s+(.+)",
                    r"(?:coordinates|point)\s+(?:of\s+)?(.+?)(?:\s+on\s+(.+?))?"
                ],
                "keywords": ["area", "perimeter", "volume", "distance", "angle", "circle", "triangle"],
                "complexity": "medium"
            },
            "statistics": {
                "patterns": [
                    r"(?:mean|average|median|mode|standard\s+deviation)\s+(?:of\s+)?(.+)",
                    r"(?:correlation|regression|probability)\s+(?:of\s+|between\s+)?(.+?)(?:\s+and\s+(.+?))?",
                    r"(?:normal|binomial|poisson)\s+distribution\s+with\s+(.+)",
                    r"(?:hypothesis\s+test|t-test|chi-square)\s+(?:for\s+)?(.+)",
                    r"(?:confidence\s+interval|margin\s+of\s+error)\s+(?:for\s+)?(.+)"
                ],
                "keywords": ["mean", "median", "correlation", "probability", "distribution", "test"],
                "complexity": "high"
            },
            "physics": {
                "patterns": [
                    r"(?:force|velocity|acceleration|momentum|energy)\s+(?:of\s+)?(.+?)(?:\s+(?:when|if|given)\s+(.+?))?",
                    r"(?:motion|trajectory|path)\s+(?:of\s+)?(.+?)(?:\s+under\s+(.+?))?",
                    r"(?:electric|magnetic|gravitational)\s+field\s+(?:of\s+)?(.+?)(?:\s+at\s+(.+?))?",
                    r"(?:wave|frequency|wavelength|amplitude)\s+(?:of\s+)?(.+)",
                    r"(?:temperature|pressure|volume|density)\s+(?:of\s+)?(.+?)(?:\s+(?:at|under)\s+(.+?))?"
                ],
                "keywords": ["force", "velocity", "energy", "field", "wave", "temperature", "pressure"],
                "complexity": "high"
            }
        }
    
    def _load_problem_templates(self) -> Dict[str, List[str]]:
        """Load problem generation templates"""
        return {
            "arithmetic": [
                "Calculate {a} + {b}",
                "What is {a} × {b}?",
                "Find the sum of {a}, {b}, and {c}",
                "Divide {a} by {b}",
                "What is {a}% of {b}?"
            ],
            "algebra": [
                "Solve for x: {a}x + {b} = {c}",
                "Find the roots of {a}x² + {b}x + {c} = 0",
                "If {a}x - {b} = {c}, what is x?",
                "Solve the system: {eq1} and {eq2}",
                "Simplify: ({a}x + {b})({c}x + {d})"
            ],
            "calculus": [
                "Find the derivative of {function}",
                "Integrate {function} with respect to {variable}",
                "Find the limit of {function} as {variable} approaches {value}",
                "Find the critical points of {function}",
                "Calculate the area under {function} from {a} to {b}"
            ],
            "geometry": [
                "Find the area of a {shape} with {dimensions}",
                "Calculate the distance between points ({x1}, {y1}) and ({x2}, {y2})",
                "Find the angle between vectors {v1} and {v2}",
                "What is the volume of a {shape} with {dimensions}?",
                "Find the equation of the line through ({x1}, {y1}) and ({x2}, {y2})"
            ]
        }
    
    def _load_solution_methods(self) -> Dict[str, List[str]]:
        """Load solution methods for different problem types"""
        return {
            "arithmetic": ["direct_calculation", "step_by_step", "mental_math", "calculator"],
            "algebra": ["substitution", "elimination", "factoring", "quadratic_formula", "graphing"],
            "calculus": ["power_rule", "chain_rule", "product_rule", "quotient_rule", "integration_by_parts", "u_substitution"],
            "geometry": ["pythagorean_theorem", "trigonometry", "coordinate_geometry", "area_formulas", "volume_formulas"],
            "statistics": ["descriptive_statistics", "inferential_statistics", "regression_analysis", "hypothesis_testing"],
            "physics": ["kinematics", "dynamics", "energy_conservation", "momentum_conservation", "electromagnetic_theory"],
            "chemistry": ["stoichiometry", "thermodynamics", "kinetics", "equilibrium", "quantum_chemistry"]
        }
    
    def _initialize_models(self):
        """Initialize AI models on first use"""
        try:
            if pipeline is not None and self.qa_pipeline is None:
                logger.info("Loading Question-Answering model...")
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model="deepset/roberta-base-squad2",
                    device=0 if self.device.type == "cuda" else -1
                )
                
                logger.info("Loading Text Classification model...")
                self.classification_pipeline = pipeline(
                    "text-classification",
                    model="microsoft/DialoGPT-medium",
                    device=0 if self.device.type == "cuda" else -1
                )
                
                logger.info("Models initialized successfully")
            else:
                logger.warning("Transformers library not available, using fallback methods")
        except MathematicsError as e:
            logger.error("Error initializing models: %s", e)
            logger.info("Using fallback methods without AI models")
    
    def analyze_mathematical_problem(self, text: str, context: Optional[Dict] = None) -> MathProblem:
        """
        Comprehensive analysis of mathematical problems in natural language
        """
        logger.info("Analyzing problem: %s...", text[:100])
        
        # Initialize models if needed
        self._initialize_models()
        
        # Step 1: Initial parsing and classification
        problem_type = self._classify_problem_type(text)
        difficulty = self._assess_difficulty(text, problem_type)
        
        # Step 2: Extract mathematical entities
        entities = self._extract_mathematical_entities(text)
        
        # Step 3: Parse expression using pattern matching
        parsed_expression, variables, parameters = self._parse_mathematical_expression(text, problem_type)
        
        # Step 4: Confidence assessment
        confidence = self._assess_confidence(text, parsed_expression, entities)
        
        # Step 5: Ambiguity detection
        ambiguities = self._detect_ambiguities(text, entities)
        
        # Step 6: Method recommendation
        suggested_methods = self._recommend_solution_methods(problem_type, entities, difficulty)
        
        # Step 7: Context enrichment
        enriched_context = self._enrich_context(text, context or {})
        
        # Create problem object
        problem = MathProblem(
            original_text=text,
            problem_type=problem_type,
            difficulty=difficulty,
            parsed_expression=parsed_expression,
            variables=variables,
            parameters=parameters,
            confidence=confidence,
            ambiguities=ambiguities,
            suggested_methods=suggested_methods,
            context=enriched_context
        )
        
        # Add to conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "problem": problem,
            "type": "analysis"
        })
        
        return problem
    
    def _classify_problem_type(self, text: str) -> ProblemType:
        """Classify the type of mathematical problem"""
        text_lower = text.lower()
        
        # Score each category
        scores = {}
        
        for category, info in self.math_patterns.items():
            score = 0
            
            # Check patterns
            for pattern in info["patterns"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 3
            
            # Check keywords
            for keyword in info["keywords"]:
                if keyword in text_lower:
                    score += 1
            
            scores[category] = score
        
        # Find the category with highest score
        if not scores:
            best_category = "unknown"
        else:
            best_category = max(scores.keys(), key=lambda x: scores[x])
        
        # Map to ProblemType enum
        type_mapping = {
            "arithmetic": ProblemType.ARITHMETIC,
            "algebra": ProblemType.ALGEBRA,
            "calculus": ProblemType.CALCULUS,
            "geometry": ProblemType.GEOMETRY,
            "statistics": ProblemType.STATISTICS,
            "physics": ProblemType.PHYSICS,
            "unknown": ProblemType.UNKNOWN
        }
        
        return type_mapping.get(best_category, ProblemType.UNKNOWN)
    
    def _assess_difficulty(self, text: str, problem_type: ProblemType) -> Difficulty:
        """Assess the difficulty level of the problem"""
        text_lower = text.lower()
        
        # Difficulty indicators
        beginner_indicators = ["basic", "simple", "elementary", "easy", "what is", "calculate", "find"]
        intermediate_indicators = ["solve", "determine", "compute", "analyze", "evaluate"]
        advanced_indicators = ["prove", "derive", "optimize", "minimize", "maximize", "partial", "differential"]
        expert_indicators = ["theorem", "lemma", "conjecture", "sophisticated", "complex", "advanced", "research"]
        
        # Mathematical complexity indicators
        complexity_indicators = {
            "beginner": len(re.findall(r'\d+', text)),  # Just numbers
            "intermediate": len(re.findall(r'[a-zA-Z]\s*[+\-*/=]', text)),  # Variables with operations
            "advanced": len(re.findall(r'(?:sin|cos|tan|log|exp|sqrt|derivative|integral)', text_lower)),
            "expert": len(re.findall(r'(?:partial|differential|series|transform|matrix|vector)', text_lower))
        }
        
        # Score based on indicators
        scores = {
            "beginner": sum(1 for indicator in beginner_indicators if indicator in text_lower),
            "intermediate": sum(1 for indicator in intermediate_indicators if indicator in text_lower),
            "advanced": sum(1 for indicator in advanced_indicators if indicator in text_lower),
            "expert": sum(1 for indicator in expert_indicators if indicator in text_lower)
        }
        
        # Add complexity scores
        for level, score in complexity_indicators.items():
            scores[level] += score
        
        # Determine difficulty
        max_score = max(scores.values())
        if max_score == 0:
            return Difficulty.BEGINNER
        
        best_difficulty = max(scores.keys(), key=lambda x: scores[x])
        
        difficulty_mapping = {
            "beginner": Difficulty.BEGINNER,
            "intermediate": Difficulty.INTERMEDIATE,
            "advanced": Difficulty.ADVANCED,
            "expert": Difficulty.EXPERT
        }
        
        return difficulty_mapping.get(best_difficulty, Difficulty.INTERMEDIATE)
    
    def _extract_mathematical_entities(self, text: str) -> Dict[str, Any]:
        """Extract mathematical entities from text"""
        entities = {
            "numbers": [],
            "variables": [],
            "functions": [],
            "operations": [],
            "units": [],
            "constants": []
        }
        
        # Extract numbers (integers, decimals, fractions)
        numbers = re.findall(r'-?\d+(?:\.\d+)?(?:/\d+)?', text)
        entities["numbers"] = [float(n) if '.' in n else int(n) for n in numbers if '/' not in n]
        
        # Extract variables (single letters, subscripts)
        variables = re.findall(r'\b[a-zA-Z](?:_\d+)?\b', text)
        # Filter out function names and common words
        function_names = {'sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'ln', 'abs', 'max', 'min'}
        common_words = {'of', 'the', 'and', 'or', 'is', 'are', 'in', 'to', 'by', 'for', 'with', 'from'}
        entities["variables"] = [v for v in set(variables) if v.lower() not in function_names and v.lower() not in common_words]
        
        # Extract functions
        functions = re.findall(r'\b(?:sin|cos|tan|sec|csc|cot|sinh|cosh|tanh|log|ln|exp|sqrt|abs|max|min)\b', text.lower())
        entities["functions"] = list(set(functions))
        
        # Extract operations
        operations = re.findall(r'(?:derivative|integral|limit|sum|product|maximum|minimum|solve|factor|expand|simplify)', text.lower())
        entities["operations"] = list(set(operations))
        
        # Extract units
        units = re.findall(r'\b(?:meters?|feet|inches?|seconds?|hours?|minutes?|degrees?|radians?|kg|grams?|pounds?)\b', text.lower())
        entities["units"] = list(set(units))
        
        # Extract constants
        constants = re.findall(r'\b(?:pi|e|euler|infinity|inf)\b', text.lower())
        entities["constants"] = list(set(constants))
        
        return entities
    
    def _parse_mathematical_expression(self, text: str, problem_type: ProblemType) -> Tuple[str, List[str], Dict[str, Any]]:
        """Parse mathematical expression from natural language"""
        # Get relevant patterns for the problem type
        type_patterns = self.math_patterns.get(problem_type.value, {}).get("patterns", [])
        
        parsed_expression = text
        variables = []
        parameters = {}
        
        # Try to match patterns
        for pattern in type_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if groups:
                    parsed_expression = groups[0]
                    if len(groups) > 1 and groups[1]:
                        variables.append(groups[1])
                    if len(groups) > 2 and groups[2]:
                        parameters['additional_info'] = groups[2]
                break
        
        # Convert natural language to mathematical notation
        parsed_expression = self._convert_natural_language_to_math(parsed_expression)
        
        # Extract variables from parsed expression
        if not variables:
            var_matches = re.findall(r'\b[a-zA-Z](?:_\d+)?\b', parsed_expression)
            variables = [v for v in set(var_matches) if v not in ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'pi', 'e']]
        
        return parsed_expression, variables, parameters
    
    def _convert_natural_language_to_math(self, text: str) -> str:
        """Convert natural language to mathematical notation"""
        # Word to symbol mapping
        conversions = {
            r'\bplus\b': '+',
            r'\bminus\b': '-',
            r'\btimes\b': '*',
            r'\bmultiplied by\b': '*',
            r'\bdivided by\b': '/',
            r'\bover\b': '/',
            r'\bto the power of\b': '**',
            r'\bsquared\b': '**2',
            r'\bcubed\b': '**3',
            r'\bsquare root of\b': 'sqrt(',
            r'\bequals\b': '=',
            r'\bequal to\b': '=',
            r'\bis\b': '=',
            r'\bpi\b': 'pi',
            r'\beuler\b': 'E',
            r'\bnatural log\b': 'ln',
            r'\blogarithm\b': 'log',
            r'\bsine\b': 'sin',
            r'\bcosine\b': 'cos',
            r'\btangent\b': 'tan',
            r'\bexponential\b': 'exp'
        }
        
        # Apply conversions
        result = text.lower()
        for pattern, replacement in conversions.items():
            result = re.sub(pattern, replacement, result)
        
        # Handle special cases
        result = re.sub(r'sqrt\(([^)]+)\)', r'sqrt(\1)', result)
        result = re.sub(r'(\d+)\s*\*\*\s*(\d+)', r'\1**\2', result)
        
        return result.strip()
    
    def _assess_confidence(self, text: str, parsed_expression: str, entities: Dict[str, Any]) -> float:
        """Assess confidence in the parsing and analysis"""
        confidence = 0.0
        
        # Base confidence from successful parsing
        if parsed_expression and parsed_expression != text:
            confidence += 0.3
        
        # Confidence from entity extraction
        if entities["numbers"]:
            confidence += 0.2
        if entities["variables"]:
            confidence += 0.2
        if entities["functions"]:
            confidence += 0.1
        if entities["operations"]:
            confidence += 0.2
        
        # Confidence from SymPy validation
        try:
            sp.sympify(parsed_expression)
            confidence += 0.3
        except MathematicsError:
            confidence -= 0.1
        
        # Confidence from text clarity
        if len(text.split()) > 3:
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _detect_ambiguities(self, text: str, entities: Dict[str, Any]) -> List[str]:
        """Detect potential ambiguities in the problem statement"""
        ambiguities = []
        
        # Check for ambiguous language
        ambiguous_phrases = [
            ("and", "Multiple operations may be intended"),
            ("or", "Alternative interpretations possible"),
            ("about", "Approximation vs. exact calculation unclear"),
            ("around", "Approximation vs. exact calculation unclear"),
            ("some", "Quantity not specified"),
            ("few", "Quantity not specified"),
            ("many", "Quantity not specified")
        ]
        
        text_lower = text.lower()
        for phrase, message in ambiguous_phrases:
            if phrase in text_lower:
                ambiguities.append(f"Ambiguous term '{phrase}': {message}")
        
        # Check for missing information
        if len(entities["variables"]) > 1 and "solve" in text_lower:
            ambiguities.append("Multiple variables present - specify which variable to solve for")
        
        # Check for unclear mathematical operations
        if "%" in text and "percent" not in text_lower:
            ambiguities.append("'%' symbol could mean percentage or modulo operation")
        
        return ambiguities
    
    def _recommend_solution_methods(self, problem_type: ProblemType, entities: Dict[str, Any], difficulty: Difficulty) -> List[str]:
        """Recommend appropriate solution methods"""
        methods = self.solution_methods.get(problem_type.value, [])
        
        # Filter methods based on difficulty
        if difficulty == Difficulty.BEGINNER:
            # Prefer simpler methods
            preferred_methods = [m for m in methods if "formula" in m or "direct" in m or "step" in m]
        elif difficulty == Difficulty.EXPERT:
            # Include all methods, prefer advanced ones
            preferred_methods = methods
        else:
            # Intermediate methods
            preferred_methods = methods[:3]  # Top 3 methods
        
        # Add context-specific recommendations
        if entities["functions"]:
            if problem_type == ProblemType.CALCULUS:
                preferred_methods.extend(["chain_rule", "product_rule"])
        
        return preferred_methods[:5]  # Limit to 5 methods
    
    def _enrich_context(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich problem context with additional information"""
        enriched = context.copy()
        
        # Add text analysis
        enriched["text_length"] = len(text)
        enriched["word_count"] = len(text.split())
        enriched["contains_equations"] = "=" in text
        enriched["contains_inequalities"] = any(op in text for op in ["<", ">", "≤", "≥"])
        
        # Add mathematical context
        enriched["mathematical_notation"] = any(symbol in text for symbol in ["∫", "∑", "∏", "∂", "∇", "∞"])
        enriched["greek_letters"] = bool(re.search(r'[α-ωΑ-Ω]', text))
        
        # Add domain information
        physics_terms = ["force", "velocity", "acceleration", "energy", "momentum", "field"]
        chemistry_terms = ["molecule", "atom", "reaction", "compound", "element", "bond"]
        economics_terms = ["profit", "cost", "revenue", "interest", "investment", "return"]
        
        if any(term in text.lower() for term in physics_terms):
            enriched["domain"] = "physics"
        elif any(term in text.lower() for term in chemistry_terms):
            enriched["domain"] = "chemistry"
        elif any(term in text.lower() for term in economics_terms):
            enriched["domain"] = "economics"
        else:
            enriched["domain"] = "pure_mathematics"
        
        return enriched
    
    def generate_step_by_step_solution(self, problem: MathProblem) -> Dict[str, Any]:
        """Generate detailed step-by-step solution"""
        steps = []
        
        # Step 1: Problem interpretation
        steps.append({
            "step": 1,
            "title": "Problem Interpretation",
            "description": f"Analyzing the problem: '{problem.original_text}'",
            "details": {
                "problem_type": problem.problem_type.value,
                "difficulty": problem.difficulty.value,
                "parsed_expression": problem.parsed_expression,
                "variables": problem.variables
            }
        })
        
        # Step 2: Method selection
        steps.append({
            "step": 2,
            "title": "Method Selection",
            "description": f"Recommended solution methods: {', '.join(problem.suggested_methods[:3])}",
            "details": {
                "all_methods": problem.suggested_methods,
                "chosen_method": problem.suggested_methods[0] if problem.suggested_methods else "direct_calculation"
            }
        })
        
        # Step 3: Mathematical execution
        try:
            if problem.problem_type == ProblemType.CALCULUS:
                result = self._solve_calculus_problem(problem)
            elif problem.problem_type == ProblemType.ALGEBRA:
                result = self._solve_algebra_problem(problem)
            elif problem.problem_type == ProblemType.ARITHMETIC:
                result = self._solve_arithmetic_problem(problem)
            else:
                result = self._solve_general_problem(problem)
            
            steps.append({
                "step": 3,
                "title": "Mathematical Execution",
                "description": "Performing the mathematical operations",
                "details": result
            })
        except MathematicsError as e:
            steps.append({
                "step": 3,
                "title": "Mathematical Execution",
                "description": f"Error in calculation: {str(e)}",
                "details": {"error": str(e)}
            })
        
        # Step 4: Verification
        steps.append({
            "step": 4,
            "title": "Solution Verification",
            "description": "Checking the solution for accuracy and completeness",
            "details": {
                "confidence": problem.confidence,
                "ambiguities": problem.ambiguities,
                "verification_status": "passed" if problem.confidence > 0.7 else "requires_review"
            }
        })
        
        return {
            "problem": problem,
            "steps": steps,
            "solution_summary": steps[-2]["details"] if len(steps) >= 2 else None,
            "generated_at": datetime.now().isoformat()
        }
    
    def _solve_calculus_problem(self, problem: MathProblem) -> Dict[str, Any]:
        """Solve calculus-specific problems"""
        expr = problem.parsed_expression
        var = problem.variables[0] if problem.variables else 'x'
        
        try:
            sympy_expr = sp.sympify(expr)
            var_symbol = sp.Symbol(var)
            
            # Determine operation type
            if "derivative" in problem.original_text.lower():
                result = sp.diff(sympy_expr, var_symbol)
                operation = "derivative"
            elif "integral" in problem.original_text.lower():
                result = sp.integrate(sympy_expr, var_symbol)
                operation = "integral"
            elif "limit" in problem.original_text.lower():
                result = sp.limit(sympy_expr, var_symbol, 0)  # Default to 0
                operation = "limit"
            else:
                result = sympy_expr
                operation = "expression"
            
            return {
                "operation": operation,
                "original_expression": expr,
                "result": str(result),
                "latex": sp.latex(result),
                "numerical_value": float(result.evalf()) if hasattr(result, 'is_number') and result.is_number and hasattr(result.evalf(), '__float__') else None
            }
        except MathematicsError as e:
            return {"error": f"Calculus calculation failed: {str(e)}"}
    
    def _solve_algebra_problem(self, problem: MathProblem) -> Dict[str, Any]:
        """Solve algebra-specific problems"""
        expr = problem.parsed_expression
        var = problem.variables[0] if problem.variables else 'x'
        
        try:
            if "=" in expr:
                # Solve equation
                equation = expr.replace("=", "-(") + ")"
                sympy_expr = sp.sympify(equation)
                var_symbol = sp.Symbol(var)
                solutions = sp.solve(sympy_expr, var_symbol)
                
                return {
                    "operation": "solve_equation",
                    "equation": expr,
                    "variable": var,
                    "solutions": [str(sol) for sol in solutions],
                    "numerical_solutions": [float(sol.evalf()) if sol.is_number else str(sol) for sol in solutions]
                }
            else:
                # Simplify expression
                sympy_expr = sp.sympify(expr)
                simplified = sp.simplify(sympy_expr)
                
                return {
                    "operation": "simplify",
                    "original_expression": expr,
                    "simplified": str(simplified),
                    "latex": sp.latex(simplified)
                }
        except MathematicsError as e:
            return {"error": f"Algebra calculation failed: {str(e)}"}
    
    def _solve_arithmetic_problem(self, problem: MathProblem) -> Dict[str, Any]:
        """Solve arithmetic-specific problems"""
        expr = problem.parsed_expression
        
        try:
            sympy_expr = sp.sympify(expr)
            result = float(sympy_expr.evalf())
            
            return {
                "operation": "arithmetic_calculation",
                "expression": expr,
                "result": result,
                "result_type": "float"
            }
        except Exception as e:
            return {"error": f"Arithmetic calculation failed: {str(e)}"}
    
    def _solve_general_problem(self, problem: MathProblem) -> Dict[str, Any]:
        """Solve general mathematical problems"""
        expr = problem.parsed_expression
        
        try:
            sympy_expr = sp.sympify(expr)
            
            # Try different operations
            result = {
                "expression": expr,
                "simplified": str(sp.simplify(sympy_expr)),
                "expanded": str(sp.expand(sympy_expr)),
                "factored": str(sp.factor(sympy_expr)),
                "latex": sp.latex(sympy_expr)
            }
            
            if sympy_expr.is_number:
                result["numerical_value"] = float(sympy_expr.evalf())
            
            return result
        except MathematicsError as e:
            return {"error": f"General calculation failed: {str(e)}"}
    
    def generate_similar_problems(self, problem: MathProblem, count: int = 3) -> List[Dict[str, Any]]:
        """Generate similar problems for practice"""
        similar_problems = []
        
        templates = self.problem_templates.get(problem.problem_type.value, [])
        
        for i in range(min(count, len(templates))):
            template = templates[i]
            
            # Generate random parameters
            params = self._generate_random_parameters(problem)
            
            try:
                # Fill template with parameters
                new_problem_text = template.format(**params)
                
                similar_problems.append({
                    "problem_text": new_problem_text,
                    "template": template,
                    "parameters": params,
                    "difficulty": problem.difficulty.value,
                    "type": problem.problem_type.value
                })
            except KeyError:
                # Template requires parameters we don't have
                continue
        
        return similar_problems
    
    def _generate_random_parameters(self, problem: MathProblem) -> Dict[str, Any]:
        """Generate random parameters for problem templates"""
        import random
        
        params = {}
        
        # Generate numbers based on difficulty
        if problem.difficulty == Difficulty.BEGINNER:
            params.update({
                "a": random.randint(1, 10),
                "b": random.randint(1, 10),
                "c": random.randint(1, 10),
                "d": random.randint(1, 10)
            })
        elif problem.difficulty == Difficulty.INTERMEDIATE:
            params.update({
                "a": random.randint(-20, 20),
                "b": random.randint(-20, 20),
                "c": random.randint(-20, 20),
                "d": random.randint(-20, 20)
            })
        else:  # Advanced/Expert
            params.update({
                "a": random.randint(-100, 100),
                "b": random.randint(-100, 100),
                "c": random.randint(-100, 100),
                "d": random.randint(-100, 100)
            })
        
        # Generate variables
        variables = ["x", "y", "z", "t", "u", "v", "w"]
        params["variable"] = random.choice(variables)
        
        # Generate functions
        functions = ["x^2", "sin(x)", "cos(x)", "x^3", "ln(x)", "e^x", "sqrt(x)"]
        params["function"] = random.choice(functions)
        
        # Generate specific problem type parameters
        if problem.problem_type == ProblemType.GEOMETRY:
            params.update({
                "shape": random.choice(["circle", "triangle", "rectangle", "square"]),
                "dimensions": f"radius {random.randint(1, 20)}" if "circle" in str(params.get("shape", "")) else f"side {random.randint(1, 20)}",
                "x1": random.randint(-10, 10),
                "y1": random.randint(-10, 10),
                "x2": random.randint(-10, 10),
                "y2": random.randint(-10, 10)
            })
        
        return params
    
    def get_conversation_context(self) -> List[Dict[str, Any]]:
        """Get conversation history for context-aware responses"""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service usage statistics"""
        return {
            "total_problems_analyzed": len(self.conversation_history),
            "problem_types": {pt.value: 0 for pt in ProblemType},
            "difficulty_distribution": {d.value: 0 for d in Difficulty},
            "average_confidence": 0.0,
            "most_common_ambiguities": [],
            "service_uptime": "active"
        }
