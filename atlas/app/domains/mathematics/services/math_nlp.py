"""
Mathematical Natural Language Processing Service
Provides capabilities for parsing and understanding mathematical expressions in natural language
"""

import re
import sympy as sp
from typing import Dict, List, Any
from app.services.base_service import BaseService
from app.exceptions.domain.mathematics import MathematicsError

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class MathNLPService(BaseService):
    """Service for mathematical natural language processing"""
    
    def __init__(self):
        super().__init__("MathNLPService")
        self.transformers_available = TRANSFORMERS_AVAILABLE
        self.math_keywords = {
            'add': '+',
            'plus': '+',
            'sum': '+',
            'subtract': '-',
            'minus': '-',
            'difference': '-',
            'multiply': '*',
            'times': '*',
            'product': '*',
            'divide': '/',
            'divided by': '/',
            'quotient': '/',
            'power': '**',
            'raised to': '**',
            'squared': '**2',
            'cubed': '**3',
            'square root': 'sqrt',
            'derivative': 'diff',
            'integral': 'integrate',
            'solve': 'solve',
            'equals': '=',
            'equal to': '=',
            'is': '=',
            'sin': 'sin',
            'cos': 'cos',
            'tan': 'tan',
            'ln': 'ln',
            'log': 'log',
            'exp': 'exp',
            'pi': 'pi',
            'e': 'E'
        }
        
        self.number_words = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
            'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
            'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
            'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80,
            'ninety': 90, 'hundred': 100, 'thousand': 1000, 'million': 1000000
        }
        
        self.operation_patterns = {
            'derivative': r'(?:derivative|differentiate|diff)\s+(?:of\s+)?(.+?)(?:\s+with\s+respect\s+to\s+(\w+))?',
            'integral': r'(?:integral|integrate)\s+(?:of\s+)?(.+?)(?:\s+with\s+respect\s+to\s+(\w+))?',
            'solve': r'(?:solve|find\s+the\s+solution\s+(?:to|for))\s+(.+?)(?:\s+for\s+(\w+))?',
            'limit': r'(?:limit|lim)\s+(?:of\s+)?(.+?)(?:\s+as\s+(\w+)\s+approaches\s+(.+?))?',
            'plot': r'(?:plot|graph|draw)\s+(.+)',
            'evaluate': r'(?:evaluate|calculate|compute)\s+(.+)',
            'expand': r'(?:expand|distribute)\s+(.+)',
            'factor': r'(?:factor|factorize)\s+(.+)',
            'simplify': r'(?:simplify|reduce)\s+(.+)'
        }
        self.nlp_pipeline = None # Initialize to None

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitudes de NLP matemático
        """
        action = request_data.get("action")
        
        if action == "parse_natural_language":
            return self.parse_natural_language(request_data.get("text"))
        elif action == "process_with_huggingface":
            return self.process_with_huggingface(
                text=request_data.get("text"),
                question=request_data.get("question")
            )
            
        return {"success": False, "error": f"Unknown action: {action}"}
    
    def _get_huggingface_model(self):
        """
        Loads a pre-trained Hugging Face model and tokenizer for question-answering.
        Caches the pipeline for subsequent calls.
        """
        if not self.transformers_available:
            return None
            
        if self.nlp_pipeline is None:
            # Using a smaller model for demonstration and faster loading
            self.nlp_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
        return self.nlp_pipeline
    
    def process_with_huggingface(self, text: str, question: str = None) -> Dict[str, Any]:
        """
        Process text using a Hugging Face model for deeper semantic understanding.
        
        Args:
            text: The context text to analyze.
            question: An optional question to ask the model about the text.
            
        Returns:
            A dictionary containing the Hugging Face model's analysis.
        """
        if not self.transformers_available:
            return {
                "huggingface_analysis": "Not Available",
                "error": "Transformers library not available",
                "text": text,
                "question": question
            }
            
        model = self._get_huggingface_model()
        
        if model is None:
            return {
                "huggingface_analysis": "Model Loading Failed",
                "error": "Could not load Hugging Face model",
                "text": text,
                "question": question
            }
        
        if question:
            # Use question-answering pipeline
            result = model(question=question, context=text)
            return {
                "huggingface_analysis": "Question Answering",
                "question": question,
                "context": text,
                "answer": result.get('answer', 'No answer found'),
                "score": result.get('score', 0.0)
            }
        else:
            # For general semantic analysis, we can try to extract entities or keywords
            # This is a simplified approach; a more complex model might be needed for full semantic parsing
            return {
                "huggingface_analysis": "General Semantic Analysis (Placeholder)",
                "text": text, # Keep original casing
                "extracted_info": {
                    "keywords": text.split()[:5], # Just taking first 5 words as keywords for now
                    "entities": [], # Entity recognition would require a different pipeline
                    "sentiment": "neutral" # Sentiment analysis would require a different pipeline
                }
            }

    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language mathematical text into structured format
        """
        try:
            # Clean and normalize text
            text = text.lower().strip()
            confidence = 0.0
            extracted_entities = {}
            ambiguities = []
            
            # Check for operation patterns
            operation_type = None
            parsed_expression = None
            parameters = {}
            
            for op_name, pattern in self.operation_patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    operation_type = op_name
                    parsed_expression = match.group(1)
                    confidence += 0.3
                    
                    # Extract additional parameters
                    if len(match.groups()) > 1 and match.group(2):
                        parameters['variable'] = match.group(2)
                    if len(match.groups()) > 2 and match.group(3):
                        parameters['limit_value'] = match.group(3)
                    break
            
            # If no operation pattern found, try to parse as expression
            if not operation_type:
                operation_type = 'evaluate'
                parsed_expression = text
            
            # Convert words to mathematical notation
            if parsed_expression:
                parsed_expression = self._convert_words_to_math(parsed_expression)
                confidence += 0.2
            
            # Extract numbers and variables
            if parsed_expression:
                numbers = re.findall(r'\b\d+\.?\d*\b', parsed_expression)
                extracted_entities['numbers'] = [float(n) for n in numbers]
                
                variables = re.findall(r'\b[a-zA-Z](?!sqrt|sin|cos|tan|log|exp|pi|E)\b', parsed_expression)
                extracted_entities['variables'] = list(set(variables))

            # Basic ambiguity detection
            if "plus minus" in text or "minus plus" in text:
                ambiguities.append("Ambiguous use of 'plus minus' or 'minus plus'. Please clarify.")
            if re.search(r'\b(and|or)\b', text) and operation_type != 'solve':
                ambiguities.append("Conjunctions like 'and' or 'or' might introduce ambiguity. Please rephrase if not intended for multiple operations.")

            # Try to parse as sympy expression
            try:
                sympy_expr = sp.sympify(parsed_expression)
                confidence += 0.3
                parsed_expression = str(sympy_expr)
            except Exception:  # TODO: Change to JSONDecodeError or ValueError
                confidence -= 0.1
            
            # Calculate final confidence
            confidence = min(1.0, max(0.0, confidence))
            
            return {
                'operation_type': operation_type,
                'parsed_expression': parsed_expression,
                'parameters': parameters,
                'confidence': confidence,
                'original_text': text,
                'extracted_entities': extracted_entities,
                'ambiguities': ambiguities
            }
            
        except MathematicsError as e:
            return {
                'operation_type': 'error',
                'parsed_expression': text,
                'parameters': {},
                'confidence': 0.0,
                'error': str(e),
                'original_text': text
            }
    
    def _convert_words_to_math(self, text: str) -> str:
        """Convert word-based mathematical expressions to symbolic notation"""
        # Convert number words to digits
        for word, number in self.number_words.items():
            text = re.sub(r'\b' + word + r'\b', str(number), text)
        
        # Convert mathematical operations
        for phrase, symbol in self.math_keywords.items():
            text = re.sub(r'\b' + phrase + r'\b', symbol, text)
        
        # Handle special cases
        text = re.sub(r'(\d+)\s+squared', r'\1**2', text)
        text = re.sub(r'(\d+)\s+cubed', r'\1**3', text)
        text = re.sub(r'square\s+root\s+of\s+(\d+)', r'sqrt(\1)', text)
        text = re.sub(r'(\w+)\s+to\s+the\s+power\s+of\s+(\d+)', r'\1**\2', text)
        text = re.sub(r'(\w+)\s+to\s+the\s+(\d+)', r'\1**\2', text)
        
        # Clean up spacing
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def execute_parsed_expression(self, parsed_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a parsed mathematical expression"""
        try:
            operation_type = parsed_result['operation_type']
            expression = parsed_result['parsed_expression']
            parameters = parsed_result['parameters']
            
            result = None
            
            if operation_type == 'evaluate':
                result = self._evaluate_expression(expression)
            elif operation_type == 'derivative':
                var = parameters.get('variable', 'x')
                result = self._compute_derivative(expression, var)
            elif operation_type == 'integral':
                var = parameters.get('variable', 'x')
                result = self._compute_integral(expression, var)
            elif operation_type == 'solve':
                var = parameters.get('variable', 'x')
                result = self._solve_equation(expression, var)
            elif operation_type == 'limit':
                var = parameters.get('variable', 'x')
                limit_value = parameters.get('limit_value', 0)
                result = self._compute_limit(expression, var, limit_value)
            elif operation_type == 'expand':
                result = self._expand_expression(expression)
            elif operation_type == 'factor':
                result = self._factor_expression(expression)
            elif operation_type == 'simplify':
                result = self._simplify_expression(expression)
            else:
                result = f"Operation '{operation_type}' not implemented"
            
            return {
                'success': True,
                'result': result,
                'operation_type': operation_type,
                'expression': expression,
                'parameters': parameters
            }
            
        except MathematicsError as e:
            return {
                'success': False,
                'result': None,
                'error': str(e),
                'operation_type': parsed_result.get('operation_type', 'unknown'),
                'expression': parsed_result.get('parsed_expression', '')
            }
    
    def _evaluate_expression(self, expression: str) -> str:
        """Evaluate a mathematical expression"""
        try:
            expr = sp.sympify(expression)
            result = expr.evalf()
            return str(result)
        except Exception:  # TODO: Change to JSONDecodeError or ValueError
            return f"Cannot evaluate: {expression}"
    
    def _compute_derivative(self, expression: str, variable: str) -> str:
        """Compute derivative of expression"""
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            derivative = sp.diff(expr, var)
            return str(derivative)
        except MathematicsError:
            return f"Cannot compute derivative of {expression}"
    
    def _compute_integral(self, expression: str, variable: str) -> str:
        """Compute integral of expression"""
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            integral = sp.integrate(expr, var)
            return str(integral)
        except MathematicsError:
            return f"Cannot compute integral of {expression}"
    
    def _solve_equation(self, expression: str, variable: str) -> str:
        """Solve equation"""
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            solutions = sp.solve(expr, var)
            return str(solutions)
        except MathematicsError:
            return f"Cannot solve equation: {expression}"
    
    def _compute_limit(self, expression: str, variable: str, limit_value: str) -> str:
        """Compute limit"""
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            limit_val = sp.sympify(limit_value)
            limit_result = sp.limit(expr, var, limit_val)
            return str(limit_result)
        except MathematicsError:
            return f"Cannot compute limit"
    
    def _expand_expression(self, expression: str) -> str:
        """Expand expression"""
        try:
            expr = sp.sympify(expression)
            expanded = sp.expand(expr)
            return str(expanded)
        except MathematicsError:
            return f"Cannot expand: {expression}"
    
    def _factor_expression(self, expression: str) -> str:
        """Factor expression"""
        try:
            expr = sp.sympify(expression)
            factored = sp.factor(expr)
            return str(factored)
        except MathematicsError:
            return f"Cannot factor: {expression}"
    
    def _simplify_expression(self, expression: str) -> str:
        """Simplify expression"""
        try:
            expr = sp.sympify(expression)
            simplified = sp.simplify(expr)
            return str(simplified)
        except MathematicsError:
            return f"Cannot simplify: {expression}"
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return list(self.operation_patterns.keys())
    
    def suggest_corrections(self, text: str) -> List[str]:
        """Suggest corrections for mathematical text"""
        suggestions = []
        
        # Check for common misspellings
        common_mistakes = {
            'derivitive': 'derivative',
            'diferential': 'differential',
            'intergral': 'integral',
            'logarithm': 'logarithm',
            'trignometry': 'trigonometry'
        }
        
        for mistake, correction in common_mistakes.items():
            if mistake in text.lower(): # Corrected line
                suggestions.append(f"Did you mean '{correction}' instead of '{mistake}'?")
        
        # Check for missing operators
        if re.search(r'\d+\s+\d+', text):
            suggestions.append("Consider adding an operator between numbers (e.g., +, -, *, /)")
        
        # Check for unbalanced parentheses
        if text.count('(') != text.count(')'):
            suggestions.append("Check for unbalanced parentheses")
        
        return suggestions
    
    def advanced_semantic_analysis(self, text: str) -> Dict[str, Any]:
        """
        Perform advanced semantic analysis of mathematical text
        
        Args:
            text: Natural language mathematical text
            
        Returns:
            Advanced semantic analysis results
        """
        try:
            # Enhanced keyword analysis
            basic_analysis = self.parse_math_expression(text)
            
            # Identify mathematical concepts
            concepts = self._identify_math_concepts(text)
            
            # Analyze problem type
            problem_type = self._analyze_problem_type(text)
            
            # Extract mathematical entities
            entities = self._extract_math_entities(text)
            
            # Determine solution approach
            solution_approach = self._determine_solution_approach(text, concepts, problem_type)
            
            # Generate mathematical expression candidates
            expression_candidates = self._generate_expression_candidates(text, entities)
            
            # Analyze mathematical relationships
            relationships = self._analyze_math_relationships(text, entities)
            
            # Confidence scoring
            confidence_scores = self._calculate_confidence_scores(
                text, concepts, problem_type, entities, relationships
            )
            
            return {
                'basic_analysis': basic_analysis,
                'concepts': concepts,
                'problem_type': problem_type,
                'entities': entities,
                'solution_approach': solution_approach,
                'expression_candidates': expression_candidates,
                'relationships': relationships,
                'confidence_scores': confidence_scores,
                'recommendations': self._generate_recommendations(
                    problem_type, solution_approach, confidence_scores
                )
            }
            
        except MathematicsError as e:
            return {
                'error': f"Advanced semantic analysis failed: {str(e)}",
                'basic_analysis': self.parse_math_expression(text) if text else None
            }
    
    def _identify_math_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Identify mathematical concepts in text"""
        concepts = []
        
        # Define concept patterns
        concept_patterns = {
            'calculus': ['derivative', 'integral', 'limit', 'continuous', 'differentiable'],
            'algebra': ['equation', 'solve', 'variable', 'polynomial', 'factor'],
            'geometry': ['triangle', 'circle', 'angle', 'area', 'perimeter', 'volume'],
            'statistics': ['mean', 'median', 'standard deviation', 'probability', 'distribution'],
            'linear_algebra': ['matrix', 'vector', 'determinant', 'eigenvalue', 'linear system'],
            'number_theory': ['prime', 'gcd', 'lcm', 'congruence', 'modular'],
            'optimization': ['minimize', 'maximize', 'constraint', 'optimal', 'linear programming'],
            'differential_equations': ['differential equation', 'ode', 'pde', 'initial condition'],
            'graph_theory': ['graph', 'vertex', 'edge', 'path', 'tree', 'network'],
            'combinatorics': ['permutation', 'combination', 'factorial', 'binomial coefficient']
        }
        
        text_lower = text.lower()
        
        for concept, keywords in concept_patterns.items():
            matched_keywords = [kw for kw in keywords if kw in text_lower]
            if matched_keywords:
                concepts.append({
                    'concept': concept,
                    'matched_keywords': matched_keywords,
                    'confidence': len(matched_keywords) / len(keywords)
                })
        
        return sorted(concepts, key=lambda x: x['confidence'], reverse=True)
    
    def _analyze_problem_type(self, text: str) -> Dict[str, Any]:
        """Analyze the type of mathematical problem"""
        text_lower = text.lower()
        
        # Problem type patterns
        problem_patterns = {
            'equation_solving': ['solve', 'find', 'what is', 'calculate', 'determine'],
            'optimization': ['minimize', 'maximize', 'optimal', 'best', 'least', 'most'],
            'calculus': ['derivative', 'integral', 'limit', 'rate of change'],
            'graphing': ['plot', 'graph', 'sketch', 'draw', 'visualize'],
            'proof': ['prove', 'show that', 'demonstrate', 'verify'],
            'computation': ['compute', 'calculate', 'evaluate', 'simplify'],
            'analysis': ['analyze', 'investigate', 'examine', 'study'],
            'modeling': ['model', 'represent', 'formulate', 'describe']
        }
        
        problem_scores = {}
        for problem_type, keywords in problem_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                problem_scores[problem_type] = score / len(keywords)
        
        if problem_scores:
            primary_type = max(problem_scores, key=lambda k: problem_scores[k])
            return {
                'primary_type': primary_type,
                'confidence': problem_scores[primary_type],
                'all_types': problem_scores
            }
        else:
            return {
                'primary_type': 'general',
                'confidence': 0.0,
                'all_types': {}
            }
    
    def _extract_math_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract mathematical entities from text"""
        entities = {
            'numbers': [],
            'variables': [],
            'functions': [],
            'constants': [],
            'operators': [],
            'units': []
        }
        
        # Extract numbers
        number_pattern = r'-?\d+(?:\.\d+)?'
        numbers = re.findall(number_pattern, text)
        entities['numbers'] = numbers
        
        # Extract single-letter variables
        var_pattern = r'\b[a-zA-Z]\b'
        variables = re.findall(var_pattern, text)
        entities['variables'] = list(set(variables))
        
        # Extract function names
        function_pattern = r'\b(sin|cos|tan|log|ln|exp|sqrt|abs)\b'
        functions = re.findall(function_pattern, text.lower())
        entities['functions'] = list(set(functions))
        
        # Extract constants
        constant_pattern = r'\b(pi|e|euler|phi)\b'
        constants = re.findall(constant_pattern, text.lower())
        entities['constants'] = list(set(constants))
        
        # Extract operators
        operator_pattern = r'(\+|-|\*|/|\^|=|<|>|\u2264|\u2265|\u2260)'
        operators = re.findall(operator_pattern, text)
        entities['operators'] = list(set(operators))
        
        # Extract units
        unit_pattern = r'\b(meter|metre|foot|inch|second|minute|hour|gram|kilogram|pound|degree|radian)\b'
        units = re.findall(unit_pattern, text.lower())
        entities['units'] = list(set(units))
        
        return entities
    
    def _determine_solution_approach(self, text: str, concepts: List[Dict[str, Any]], 
                                   problem_type: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the best approach to solve the problem"""
        approach_suggestions = []
        
        # Based on primary concept
        primary_concept = 'general'
        if concepts:
            primary_concept = concepts[0]['concept']
            
            concept_approaches = {
                'calculus': ['symbolic_differentiation', 'numerical_integration', 'limit_analysis'],
                'algebra': ['equation', 'solve', 'variable', 'polynomial', 'factor'],
                'geometry': ['triangle', 'circle', 'angle', 'area', 'perimeter', 'volume'],
                'statistics': ['mean', 'median', 'standard deviation', 'probability', 'distribution'],
                'linear_algebra': ['matrix', 'vector', 'determinant', 'eigenvalue', 'linear system'],
                'optimization': ['minimize', 'maximize', 'constraint', 'optimal', 'linear programming'],
                'differential_equations': ['differential equation', 'ode', 'pde', 'initial condition'],
                'graph_theory': ['graph', 'vertex', 'edge', 'path', 'tree', 'network'],
                'combinatorics': ['permutation', 'combination', 'factorial', 'binomial coefficient']
            }
            
            if primary_concept in concept_approaches:
                approach_suggestions.extend(concept_approaches[primary_concept])
        
        # Based on problem type
        primary_type = problem_type.get('primary_type', 'general')
        
        type_approaches = {
            'equation_solving': ['algebraic_methods', 'numerical_methods', 'graphical_methods'],
            'optimization': ['analytical_optimization', 'numerical_optimization', 'constraint_methods'],
            'calculus': ['symbolic_computation', 'numerical_computation'],
            'graphing': ['plotting_libraries', 'parametric_plotting', 'interactive_visualization'],
            'computation': ['symbolic_computation', 'numerical_computation', 'approximation_methods']
        }
        
        if primary_type in type_approaches:
            approach_suggestions.extend(type_approaches[primary_type])
        
        return {
            'suggested_approaches': list(set(approach_suggestions)),
            'reasoning': f"Based on {primary_concept if concepts else 'general analysis'} and {primary_type} problem type",
            'confidence': (concepts[0]['confidence'] if concepts else 0.5) * problem_type.get('confidence', 0.5)
        }
    
    def _generate_expression_candidates(self, text: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Generate candidate mathematical expressions"""
        candidates = []
        
        # Simple pattern matching for common expressions
        expression_patterns = [
            (r'(\w+)\s+equals?\s+(\w+)', lambda m: f"{m.group(1)} = {m.group(2)}"),
            (r'(\w+)\s+plus\s+(\w+)', lambda m: f"{m.group(1)} + {m.group(2)}"),
            (r'(\w+)\s+minus\s+(\w+)', lambda m: f"{m.group(1)} - {m.group(2)}"),
            (r'(\w+)\s+times\s+(\w+)', lambda m: f"{m.group(1)} * {m.group(2)}"),
            (r'(\w+)\s+divided\s+by\s+(\w+)', lambda m: f"{m.group(1)} / {m.group(2)}"),
            (r'square\s+root\s+of\s+(\w+)', lambda m: f"sqrt({m.group(1)})"),
            (r'(\w+)\s+squared', lambda m: f"{m.group(1)}**2"),
            (r'derivative\s+of\s+(\w+)', lambda m: f"diff({m.group(1)})"),
            (r'integral\s+of\s+(\w+)', lambda m: f"integrate({m.group(1)})")
        ]
        
        for pattern, transform in expression_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    expression = transform(match)
                    candidates.append({
                        'expression': expression,
                        'source_text': match.group(0),
                        'confidence': 0.8,
                        'type': 'pattern_match'
                    })
                except MathematicsError:
                    continue
        
        return candidates
    
    def _analyze_math_relationships(self, text: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Analyze mathematical relationships in the text"""
        relationships = []
        
        # Relationship patterns
        relationship_patterns = [
            (r'(\w+)\s+is\s+proportional\s+to\s+(\w+)', 'proportional'),
            (r'(\w+)\s+depends\s+on\s+(\w+)', 'dependency'),
            (r'(\w+)\s+equals?\s+(\w+)', 'equality'),
            (r'(\w+)\s+is\s+greater\s+than\s+(\w+)', 'inequality'),
            (r'(\w+)\s+is\s+less\s+than\s+(\w+)', 'inequality'),
            (r'(\w+)\s+varies\s+with\s+(\w+)', 'variation'),
            (r'(\w+)\s+is\s+a\s+function\s+of\s+(\w+)', 'function_relationship')
        ]
        
        for pattern, relationship_type in relationship_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                relationships.append({
                    'type': relationship_type,
                    'entity1': match.group(1),
                    'entity2': match.group(2),
                    'source_text': match.group(0),
                    'confidence': 0.7
                })
        
        return relationships
    
    def _calculate_confidence_scores(self, text: str, concepts: List[Dict[str, Any]], 
                                   problem_type: Dict[str, Any], entities: Dict[str, List[str]], 
                                   relationships: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate confidence scores for various aspects of the analysis"""
        scores = {}
        
        # Concept identification confidence
        if concepts:
            scores['concept_identification'] = sum(c['confidence'] for c in concepts) / len(concepts)
        else:
            scores['concept_identification'] = 0.0
        
        # Problem type confidence
        scores['problem_type'] = problem_type.get('confidence', 0.0)
        
        # Entity extraction confidence
        total_entities = sum(len(entities[key]) for key in entities)
        scores['entity_extraction'] = min(total_entities / 10, 1.0)  # Normalize to 0-1
        
        # Relationship analysis confidence
        scores['relationship_analysis'] = min(len(relationships) / 5, 1.0)
        
        # Overall confidence
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def _generate_recommendations(self, problem_type: Dict[str, Any], 
                                solution_approach: Dict[str, Any], 
                                confidence_scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if confidence_scores['overall'] < 0.3:
            recommendations.append("Consider rephrasing the problem more clearly with specific mathematical terms")
        
        if confidence_scores['concept_identification'] < 0.5:
            recommendations.append("Try including more specific mathematical concepts or keywords")
        
        if confidence_scores['entity_extraction'] < 0.3:
            recommendations.append("Include specific numbers, variables, or mathematical symbols")
        
        if problem_type['primary_type'] == 'general' and confidence_scores['problem_type'] < 0.3:
            recommendations.append("Specify what type of mathematical operation or analysis you want to perform")
        
        # Add approach-specific recommendations
        if solution_approach['suggested_approaches']:
            approach_text = ', '.join(solution_approach['suggested_approaches'])
            recommendations.append(f"Consider using: {approach_text}")
        
        if not recommendations:
            recommendations.append("The problem appears well-defined and ready for mathematical analysis")
        
        return recommendations


    def parse_math_expression(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language mathematical text into structured format.
        This is a simplified version for internal use in advanced_semantic_analysis.
        """
        # This is a placeholder. In a real scenario, this would be a more robust parser.
        # For now, it just returns the text and a dummy confidence.
        
        # Clean and normalize text
        text = text.lower().strip()
        
        # Simple attempt to identify an operation
        operation_type = 'unknown'
        if 'derivative' in text:
            operation_type = 'derivative'
        elif 'integral' in text:
            operation_type = 'integral'
        elif 'solve' in text:
            operation_type = 'solve'
        elif 'plot' in text or 'graph' in text:
            operation_type = 'plot'
        elif 'simplify' in text:
            operation_type = 'simplify'
        elif 'evaluate' in text or 'calculate' in text:
            operation_type = 'evaluate'
            
        # Dummy confidence based on length and presence of numbers/variables
        confidence = 0.1
        if len(text.split()) > 3:
            confidence += 0.2
        if re.search(r'\d', text) or re.search(r'[a-zA-Z]', text):
            confidence += 0.3
        
        return {
            'operation_type': operation_type,
            'parsed_expression': text, # For now, just return the original text
            'parameters': {},
            'confidence': min(1.0, confidence),
            'original_text': text,
            'extracted_entities': {}, # Placeholder
            'ambiguities': [] # Placeholder
        }