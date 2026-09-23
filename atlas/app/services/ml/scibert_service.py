"""
SciBERT Service for AXIOM
General scientific text analysis using SciBERT for interdisciplinary research

Capabilities:
- Scientific literature analysis across all domains
- Research paper classification and categorization
- Scientific concept extraction and linking
- Cross-domain research similarity analysis
- Academic writing enhancement and validation

Ethics & Safety:
- Academic Integrity: Respect copyright and proper attribution requirements
- Research Ethics: Results support research, not replace peer review
- Data Accuracy: Verify scientific claims through established sources
- Interdisciplinary Respect: Honor domain expertise and methodological differences

Consulta la guía: ETHICS_AND_SAFETY.md
"""

# Optional torch import for deep learning support
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.types.scibert_service_types import (
    AnalyzeScientificTextResult,
    AnalyzeDomainOverlapResult,
    AssessImpactPotentialResult,
    FallbackScientificAnalysisResult,
    RuleBasedPaperClassificationResult,
    SimpleResearchSimilarityResult,
    GetServiceInfoResult,
)


@dataclass
class ScientificEntity:
    """Scientific entity representation"""
    text: str
    entity_type: str
    confidence: float
    domain: str
    concept_category: str
    related_terms: List[str]


@dataclass
class ScientificAnalysisResult:
    """Scientific text analysis result"""
    text: str
    entities: List[ScientificEntity]
    research_domain: str
    methodology_type: str
    complexity_score: float
    key_concepts: List[str]
    processing_info: Dict[str, Any]


@dataclass
class ResearchSimilarityResult:
    """Research similarity analysis result"""
    text1: str
    text2: str
    similarity_score: float
    domain_overlap: Dict[str, Any]
    methodological_similarity: float
    concept_alignment: Dict[str, Any]
    interdisciplinary_potential: str


from app.services.base_service import BaseService

class SciBERTService(BaseService):
    """Advanced scientific text analysis using SciBERT"""
    
    def __init__(self):
        """Initialize SciBERT Service"""
        super().__init__("SciBERTService")
        
        # Model initialization
        self.tokenizer: Optional[Any] = None
        self.model: Optional[Any] = None
        self.device = "cuda" if HAS_TORCH and torch.cuda.is_available() else "cpu"
        
        # Scientific domains
        self.research_domains = [
            'biology', 'chemistry', 'physics', 'mathematics',
            'computer_science', 'engineering', 'medicine',
            'environmental_science', 'materials_science',
            'neuroscience', 'psychology', 'astronomy'
        ]
        
        # Scientific entity types
        self.entity_types = {
            'CONCEPT': 'Scientific Concept',
            'METHOD': 'Research Method/Technique',
            'THEORY': 'Scientific Theory',
            'FINDING': 'Research Finding/Result',
            'HYPOTHESIS': 'Research Hypothesis',
            'EXPERIMENT': 'Experimental Design',
            'MODEL': 'Scientific Model',
            'DATASET': 'Data/Dataset'
        }
        
        # Methodology types
        self.methodology_types = [
            'experimental', 'observational', 'computational',
            'theoretical', 'review', 'meta_analysis',
            'case_study', 'survey', 'simulation'
        ]
        
        self._initialize_model()
        logger.info(f"✅ SciBERTService initialized on {self.device}")
    
    def _initialize_model(self):
        """Initialize SciBERT model with fallback handling"""
        if not HAS_TORCH:
            logger.warning("Torch not available, running in fallback mode")
            return

        try:
            from transformers import AutoTokenizer, AutoModel
            # Primary model: SciBERT
            model_name = "allenai/scibert_scivocab_uncased"
            logger.info(f"Loading SciBERT model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("✅ SciBERT model loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to load SciBERT model: {e}")
            logger.info("Using fallback: BERT for scientific analysis")
            
            # Fallback to BERT
            try:
                from transformers import AutoTokenizer, AutoModel
                fallback_model = "bert-base-uncased"
                self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
                self.model = AutoModel.from_pretrained(fallback_model)
                self.model.to(self.device)
                self.model.eval()
                logger.info("✅ Fallback BERT model loaded")
            except BiologyError as fallback_e:
                logger.error(f"Failed to load fallback model: {fallback_e}")
                self.model = None
                self.tokenizer = None
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a service request"""
        try:
            operation = request_data.get("operation")
            if operation == "analyze_text":
                text = request_data.get("text")
                if not text:
                    return {"success": False, "error": "Text is required"}
                result = await self.analyze_scientific_text(text)
                return {"success": True, "data": result}
            elif operation == "analyze_overlap":
                text1 = request_data.get("text1")
                text2 = request_data.get("text2")
                if not text1 or not text2:
                    return {"success": False, "error": "Both text1 and text2 are required"}
                result = await self.analyze_domain_overlap(text1, text2)
                return {"success": True, "data": result}
            elif operation == "assess_impact":
                text = request_data.get("text")
                if not text:
                    return {"success": False, "error": "Text is required"}
                result = await self.assess_impact_potential(text)
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
        except Exception as e:
            return self.handle_error(e, "process_request")

    async def analyze_scientific_text(self, text: str) -> AnalyzeScientificTextResult:
        """Comprehensive scientific text analysis"""
        try:
            if len(text.strip()) < 30:
                raise ValueError("Text too short for scientific analysis")
            
            # Extract scientific entities
            entities = await self._extract_scientific_entities(text)
            
            # Classify research domain
            research_domain = await self._classify_research_domain(text)
            
            # Identify methodology type
            methodology_type = self._identify_methodology(text)
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(text, entities)
            
            # Extract key concepts
            key_concepts = self._extract_key_concepts(text, entities)
            
            result = ScientificAnalysisResult(
                text=text[:500] + "..." if len(text) > 500 else text,
                entities=entities,
                research_domain=research_domain,
                methodology_type=methodology_type,
                complexity_score=complexity_score,
                key_concepts=key_concepts,
                processing_info={
                    "model": "SciBERT" if "scibert" in str(self.model) else "BERT",
                    "device": self.device,
                    "text_length": len(text),
                    "entities_found": len(entities)
                }
            )
            
            return {
                "success": True,
                "message": "Scientific text analyzed successfully",
                "data": {
                    "entities": [
                        {
                            "text": e.text,
                            "type": e.entity_type,
                            "domain": e.domain,
                            "category": e.concept_category,
                            "confidence": e.confidence,
                            "related_terms": e.related_terms
                        } for e in result.entities
                    ],
                    "research_domain": result.research_domain,
                    "methodology_type": result.methodology_type,
                    "complexity_score": result.complexity_score,
                    "key_concepts": result.key_concepts,
                    "research_insights": self._generate_research_insights(result),
                    "processing_info": result.processing_info
                }
            }
            
        except BiologyError as e:
            logger.error(f"Scientific text analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_analysis": await self._fallback_scientific_analysis(text)
            }
    
    async def calculate_research_similarity(
        self, 
        text1: str, 
        text2: str
    ) -> Dict[str, Any]:
        """Calculate similarity between research texts across domains"""
        try:
            if not self.model or not self.tokenizer:
                return {
                    "success": False,
                    "error": "SciBERT model not available",
                    "fallback_similarity": self._simple_research_similarity(text1, text2)
                }
            
            # Get embeddings for both texts
            embedding1 = await self._get_scientific_embedding(text1)
            embedding2 = await self._get_scientific_embedding(text2)
            
            if embedding1 is None or embedding2 is None:
                raise ValueError("Failed to generate scientific text embeddings")
            
            # Calculate similarity
            similarity_score = cosine_similarity(
                embedding1.reshape(1, -1),
                embedding2.reshape(1, -1)
            )[0][0]
            
            # Analyze domain overlap
            domain1 = await self._classify_research_domain(text1)
            domain2 = await self._classify_research_domain(text2)
            domain_overlap = self._analyze_domain_overlap(domain1, domain2, text1, text2)
            
            # Calculate methodological similarity
            method1 = self._identify_methodology(text1)
            method2 = self._identify_methodology(text2)
            methodological_similarity = self._calculate_methodological_similarity(method1, method2)
            
            # Analyze concept alignment
            entities1 = await self._extract_scientific_entities(text1)
            entities2 = await self._extract_scientific_entities(text2)
            concept_alignment = self._analyze_concept_alignment(entities1, entities2)
            
            # Assess interdisciplinary potential
            interdisciplinary_potential = self._assess_interdisciplinary_potential(
                similarity_score, domain_overlap, concept_alignment
            )
            
            result = ResearchSimilarityResult(
                text1=text1[:100] + "..." if len(text1) > 100 else text1,
                text2=text2[:100] + "..." if len(text2) > 100 else text2,
                similarity_score=float(similarity_score),
                domain_overlap=domain_overlap,
                methodological_similarity=methodological_similarity,
                concept_alignment=concept_alignment,
                interdisciplinary_potential=interdisciplinary_potential
            )
            
            return {
                "success": True,
                "message": "Research similarity calculated successfully",
                "data": {
                    "similarity_score": result.similarity_score,
                    "domain_overlap": result.domain_overlap,
                    "methodological_similarity": result.methodological_similarity,
                    "concept_alignment": result.concept_alignment,
                    "interdisciplinary_potential": result.interdisciplinary_potential,
                    "collaboration_opportunities": self._identify_collaboration_opportunities(result),
                    "similarity_interpretation": self._interpret_similarity_score(result.similarity_score)
                }
            }
            
        except BiologyError as e:
            logger.error(f"Research similarity calculation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_similarity": self._simple_research_similarity(text1, text2)
            }
    
    async def classify_research_paper(
        self, 
        abstract: str, 
        title: str = ""
    ) -> Dict[str, Any]:
        """Classify research paper by domain and methodology"""
        try:
            full_text = f"{title} {abstract}" if title else abstract
            
            if not self.model or not self.tokenizer:
                return {
                    "success": False,
                    "error": "SciBERT model not available",
                    "fallback_classification": self._rule_based_paper_classification(full_text)
                }
            
            # Perform comprehensive analysis
            analysis_result = await self.analyze_scientific_text(full_text)
            
            if not analysis_result.get('success'):
                raise ValueError("Failed to analyze paper text")
            
            data = analysis_result['data']
            
            # Extract additional paper-specific insights
            paper_type = self._classify_paper_type(full_text)
            novelty_indicators = self._identify_novelty_indicators(full_text, data['entities'])
            impact_potential = self._assess_impact_potential(data)
            
            return {
                "success": True,
                "message": "Research paper classified successfully",
                "data": {
                    "primary_domain": data['research_domain'],
                    "methodology_type": data['methodology_type'],
                    "paper_type": paper_type,
                    "complexity_score": data['complexity_score'],
                    "key_concepts": data['key_concepts'],
                    "novelty_indicators": novelty_indicators,
                    "impact_potential": impact_potential,
                    "interdisciplinary_connections": self._find_interdisciplinary_connections(data),
                    "research_classification": {
                        "domain_confidence": 0.8,
                        "methodology_confidence": 0.7,
                        "paper_type_confidence": 0.75
                    }
                }
            }
            
        except BiologyError as e:
            logger.error(f"Research paper classification error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_classification": self._rule_based_paper_classification(f"{title} {abstract}")
            }
    
    async def _get_scientific_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate SciBERT embedding for scientific text"""
        try:
            # Tokenize and encode
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            ).to(self.device)
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling of last hidden state
                embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
            
            return embeddings
            
        except BiologyError as e:
            logger.error(f"Scientific embedding generation error: {e}")
            return None
    
    async def _extract_scientific_entities(self, text: str) -> List[ScientificEntity]:
        """Extract scientific entities from text"""
        entities = []
        text_lower = text.lower()
        
        # Scientific concept keywords by domain
        concept_keywords = {
            'biology': ['protein', 'gene', 'cell', 'organism', 'dna', 'rna', 'enzyme', 'mutation'],
            'chemistry': ['molecule', 'reaction', 'catalyst', 'compound', 'bond', 'synthesis', 'element'],
            'physics': ['particle', 'energy', 'force', 'field', 'quantum', 'electromagnetic', 'relativity'],
            'mathematics': ['theorem', 'proof', 'equation', 'function', 'algorithm', 'optimization'],
            'computer_science': ['algorithm', 'data', 'network', 'machine learning', 'artificial intelligence'],
            'medicine': ['treatment', 'therapy', 'diagnosis', 'clinical', 'patient', 'disease', 'drug'],
            'engineering': ['design', 'system', 'optimization', 'control', 'manufacturing', 'process'],
            'materials_science': ['material', 'structure', 'property', 'synthesis', 'characterization']
        }
        
        # Method/technique keywords
        method_keywords = [
            'analysis', 'spectroscopy', 'microscopy', 'simulation', 'modeling',
            'experiment', 'measurement', 'observation', 'calculation', 'survey'
        ]
        
        for domain, keywords in concept_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entity = ScientificEntity(
                        text=keyword,
                        entity_type='CONCEPT',
                        confidence=0.7,
                        domain=domain,
                        concept_category=self._categorize_concept(keyword, domain),
                        related_terms=self._find_related_terms(keyword, text_lower)
                    )
                    entities.append(entity)
        
        for method in method_keywords:
            if method in text_lower:
                entity = ScientificEntity(
                    text=method,
                    entity_type='METHOD',
                    confidence=0.6,
                    domain='general',
                    concept_category='methodology',
                    related_terms=[]
                )
                entities.append(entity)
        
        return entities
    
    async def _classify_research_domain(self, text: str) -> str:
        """Classify the research domain of the text"""
        text_lower = text.lower()
        
        domain_scores = {}
        
        # Domain-specific keyword scoring
        domain_keywords = {
            'biology': ['biological', 'organism', 'species', 'evolution', 'genetic', 'molecular biology'],
            'chemistry': ['chemical', 'reaction', 'synthesis', 'molecular', 'organic', 'inorganic'],
            'physics': ['physical', 'quantum', 'electromagnetic', 'thermodynamic', 'mechanical'],
            'mathematics': ['mathematical', 'theorem', 'proof', 'equation', 'statistical', 'computational'],
            'computer_science': ['algorithm', 'computational', 'software', 'data mining', 'artificial intelligence'],
            'medicine': ['medical', 'clinical', 'therapeutic', 'diagnostic', 'pharmaceutical', 'health'],
            'engineering': ['engineering', 'design', 'optimization', 'manufacturing', 'control', 'system'],
            'neuroscience': ['neural', 'brain', 'cognitive', 'neurological', 'synaptic', 'neuron']
        }
        
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            domain_scores[domain] = score
        
        if not domain_scores or max(domain_scores.values()) == 0:
            return 'interdisciplinary'
        
        return max(domain_scores.items(), key=lambda x: x[1])[0]
    
    def _identify_methodology(self, text: str) -> str:
        """Identify the research methodology used"""
        text_lower = text.lower()
        
        methodology_patterns = {
            'experimental': r'experiment|trial|test|measurement|observation',
            'computational': r'simulation|modeling|algorithm|computation|numerical',
            'theoretical': r'theory|theoretical|model|framework|mathematical',
            'review': r'review|survey|systematic|meta-analysis|literature',
            'observational': r'observational|longitudinal|cross-sectional|cohort',
            'case_study': r'case study|case report|individual|single case'
        }
        
        for methodology, pattern in methodology_patterns.items():
            if re.search(pattern, text_lower):
                return methodology
        
        return 'general'
    
    def _calculate_complexity_score(self, text: str, entities: List[ScientificEntity]) -> float:
        """Calculate research complexity score"""
        # Base complexity from text characteristics
        complexity = 0.0
        
        # Text length factor
        complexity += min(len(text) / 1000, 1.0) * 0.3
        
        # Entity diversity factor
        unique_domains = len(set(e.domain for e in entities))
        complexity += min(unique_domains / 5, 1.0) * 0.3
        
        # Technical terminology density
        technical_terms = ['analysis', 'synthesis', 'optimization', 'characterization', 'methodology']
        term_count = sum(1 for term in technical_terms if term in text.lower())
        complexity += min(term_count / 10, 1.0) * 0.4
        
        return round(complexity, 2)
    
    def _extract_key_concepts(self, text: str, entities: List[ScientificEntity]) -> List[str]:
        """Extract key scientific concepts from analysis"""
        key_concepts = []
        
        # Get top entities by confidence
        top_entities = sorted(entities, key=lambda x: x.confidence, reverse=True)[:10]
        key_concepts.extend([e.text for e in top_entities])
        
        # Add domain-specific concepts
        if entities:
            primary_domain = max(set(e.domain for e in entities), 
                               key=lambda x: sum(1 for e in entities if e.domain == x))
            key_concepts.append(f"{primary_domain}_research")
        
        return list(set(key_concepts))  # Remove duplicates
    
    def _categorize_concept(self, concept: str, domain: str) -> str:
        """Categorize scientific concept"""
        concept_categories = {
            'biology': {'protein': 'biomolecule', 'gene': 'genetics', 'cell': 'cellular_biology'},
            'chemistry': {'molecule': 'molecular_chemistry', 'reaction': 'chemical_process'},
            'physics': {'particle': 'particle_physics', 'energy': 'thermodynamics'},
            'mathematics': {'theorem': 'mathematical_theory', 'algorithm': 'computational_method'}
        }
        
        domain_categories = concept_categories.get(domain, {})
        return domain_categories.get(concept, 'general_concept')
    
    def _find_related_terms(self, keyword: str, text: str) -> List[str]:
        """Find terms related to the keyword in text"""
        # Simple co-occurrence based relation finding
        words = text.split()
        keyword_positions = [i for i, word in enumerate(words) if keyword in word.lower()]
        
        related_terms = []
        for pos in keyword_positions[:3]:  # Limit to first 3 occurrences
            # Get surrounding words
            start = max(0, pos - 3)
            end = min(len(words), pos + 4)
            surrounding = words[start:end]
            
            # Filter for potential technical terms (longer than 4 characters)
            technical_terms = [w for w in surrounding if len(w) > 4 and w.lower() != keyword.lower()]
            related_terms.extend(technical_terms[:2])  # Limit per occurrence
        
        return list(set(related_terms))[:5]  # Return top 5 unique terms
    
    def _analyze_domain_overlap(self, domain1: str, domain2: str, text1: str, text2: str) -> AnalyzeDomainOverlapResult:
        """Analyze overlap between research domains"""
        overlap_info = {
            'primary_domains': [domain1, domain2],
            'domain_match': domain1 == domain2,
            'cross_domain_potential': 0.0,
            'shared_concepts': []
        }
        
        if domain1 == domain2:
            overlap_info['cross_domain_potential'] = 1.0
        else:
            # Check for interdisciplinary connections
            interdisciplinary_pairs = {
                ('biology', 'chemistry'): 0.8,
                ('physics', 'chemistry'): 0.7,
                ('mathematics', 'computer_science'): 0.9,
                ('biology', 'medicine'): 0.85,
                ('engineering', 'materials_science'): 0.8
            }
            
            pair = tuple(sorted([domain1, domain2]))
            overlap_info['cross_domain_potential'] = interdisciplinary_pairs.get(pair, 0.3)
        
        return overlap_info
    
    def _calculate_methodological_similarity(self, method1: str, method2: str) -> float:
        """Calculate similarity between research methodologies"""
        if method1 == method2:
            return 1.0
        
        # Methodology similarity matrix
        method_similarity = {
            ('experimental', 'observational'): 0.6,
            ('computational', 'theoretical'): 0.7,
            ('experimental', 'computational'): 0.4,
            ('theoretical', 'review'): 0.3
        }
        
        pair = tuple(sorted([method1, method2]))
        return method_similarity.get(pair, 0.2)
    
    def _analyze_concept_alignment(
        self, 
        entities1: List[ScientificEntity], 
        entities2: List[ScientificEntity]
    ) -> Dict[str, Any]:
        """Analyze alignment of scientific concepts"""
        concepts1 = {e.text.lower() for e in entities1}
        concepts2 = {e.text.lower() for e in entities2}
        
        common_concepts = concepts1.intersection(concepts2)
        total_unique = len(concepts1.union(concepts2))
        
        return {
            'common_concepts': list(common_concepts),
            'concept_overlap_ratio': len(common_concepts) / max(total_unique, 1),
            'total_concepts': {
                'text1': len(concepts1),
                'text2': len(concepts2),
                'common': len(common_concepts)
            }
        }
    
    def _assess_interdisciplinary_potential(
        self, 
        similarity_score: float, 
        domain_overlap: Dict[str, Any], 
        concept_alignment: Dict[str, Any]
    ) -> str:
        """Assess potential for interdisciplinary collaboration"""
        if domain_overlap['domain_match']:
            return "within_domain_collaboration"
        
        if (similarity_score >= 0.6 and 
            domain_overlap['cross_domain_potential'] >= 0.6 and
            concept_alignment['concept_overlap_ratio'] >= 0.3):
            return "high_interdisciplinary_potential"
        elif similarity_score >= 0.4 and domain_overlap['cross_domain_potential'] >= 0.4:
            return "moderate_interdisciplinary_potential"
        elif concept_alignment['concept_overlap_ratio'] >= 0.2:
            return "some_interdisciplinary_potential"
        else:
            return "limited_interdisciplinary_potential"
    
    def _classify_paper_type(self, text: str) -> str:
        """Classify the type of research paper"""
        text_lower = text.lower()
        
        paper_type_patterns = {
            'original_research': r'we present|we propose|we demonstrate|novel|new method',
            'review': r'review|survey|comprehensive|systematic review',
            'case_study': r'case study|case report|case analysis',
            'technical_note': r'technical note|brief communication|letter',
            'meta_analysis': r'meta-analysis|meta analysis|systematic review and meta'
        }
        
        for paper_type, pattern in paper_type_patterns.items():
            if re.search(pattern, text_lower):
                return paper_type
        
        return 'general_research'
    
    def _identify_novelty_indicators(self, text: str, entities: List[Dict]) -> List[str]:
        """Identify indicators of research novelty"""
        novelty_indicators = []
        text_lower = text.lower()
        
        novelty_patterns = [
            'first time', 'novel', 'new approach', 'innovative', 'breakthrough',
            'unprecedented', 'original', 'pioneering', 'cutting-edge', 'state-of-the-art'
        ]
        
        for pattern in novelty_patterns:
            if pattern in text_lower:
                novelty_indicators.append(pattern)
        
        return novelty_indicators
    
    def _assess_impact_potential(self, analysis_data: AssessImpactPotentialResult) -> AssessImpactPotentialResult:
        """Assess potential research impact"""
        impact_score = 0.0
        
        # Complexity factor
        impact_score += min(analysis_data['complexity_score'] * 0.3, 0.3)
        
        # Interdisciplinary factor
        if analysis_data['research_domain'] == 'interdisciplinary':
            impact_score += 0.2
        
        # Key concepts factor
        impact_score += min(len(analysis_data['key_concepts']) / 20, 0.3)
        
        # Methodology factor
        if analysis_data['methodology_type'] in ['experimental', 'computational']:
            impact_score += 0.2
        
        impact_level = 'high' if impact_score >= 0.7 else 'medium' if impact_score >= 0.4 else 'low'
        
        return {
            'impact_score': round(impact_score, 2),
            'impact_level': impact_level,
            'contributing_factors': ['complexity', 'interdisciplinarity', 'methodology']
        }
    
    def _generate_research_insights(self, result: ScientificAnalysisResult) -> List[str]:
        """Generate research insights from analysis"""
        insights = []
        
        insights.append(f"Research primarily in {result.research_domain} domain")
        insights.append(f"Using {result.methodology_type} methodology")
        
        if result.complexity_score >= 0.7:
            insights.append("High complexity research requiring specialized expertise")
        elif result.complexity_score >= 0.4:
            insights.append("Moderate complexity with interdisciplinary connections")
        
        if len(result.key_concepts) >= 8:
            insights.append("Rich conceptual framework with multiple research themes")
        
        return insights
    
    def _find_interdisciplinary_connections(self, data: Dict[str, Any]) -> List[str]:
        """Find potential interdisciplinary connections"""
        connections = []
        
        primary_domain = data['research_domain']
        
        # Domain-specific interdisciplinary connections
        interdisciplinary_map = {
            'biology': ['chemistry', 'medicine', 'computer_science'],
            'chemistry': ['biology', 'physics', 'materials_science'],
            'physics': ['chemistry', 'engineering', 'mathematics'],
            'computer_science': ['mathematics', 'biology', 'engineering'],
            'medicine': ['biology', 'chemistry', 'psychology']
        }
        
        if primary_domain in interdisciplinary_map:
            connections = interdisciplinary_map[primary_domain]
        
        return connections[:3]  # Limit to top 3
    
    def _identify_collaboration_opportunities(self, result: ResearchSimilarityResult) -> List[str]:
        """Identify collaboration opportunities from similarity analysis"""
        opportunities = []
        
        if result.similarity_score >= 0.8:
            opportunities.append("Direct collaboration - highly similar research focus")
        elif result.similarity_score >= 0.6:
            opportunities.append("Complementary collaboration - shared methodological approaches")
        
        if result.methodological_similarity >= 0.7:
            opportunities.append("Methodological expertise sharing")
        
        if result.concept_alignment['concept_overlap_ratio'] >= 0.4:
            opportunities.append("Knowledge sharing in common research areas")
        
        if result.interdisciplinary_potential == "high_interdisciplinary_potential":
            opportunities.append("Novel interdisciplinary research development")
        
        return opportunities
    
    def _interpret_similarity_score(self, score: float) -> str:
        """Provide human-readable similarity interpretation"""
        if score >= 0.8:
            return "Very similar research - likely same field and methodology"
        elif score >= 0.6:
            return "Moderately similar - overlapping research interests or methods"
        elif score >= 0.4:
            return "Some similarity - potential for interdisciplinary connections"
        else:
            return "Different research areas - limited direct overlap"
    
    async def _fallback_scientific_analysis(self, text: str) -> FallbackScientificAnalysisResult:
        """Fallback analysis using keyword matching"""
        domain = await self._classify_research_domain(text)
        entities = await self._extract_scientific_entities(text)
        
        return {
            "research_domain": domain,
            "entities": [e.text for e in entities],
            "method": "keyword_based_fallback",
            "note": "SciBERT not available - using rule-based analysis"
        }
    
    def _rule_based_paper_classification(self, text: str) -> RuleBasedPaperClassificationResult:
        """Fallback rule-based paper classification"""
        domain = self._classify_research_domain(text)
        
        return {
            "primary_domain": domain,
            "paper_type": "general_research",
            "method": "rule_based_fallback",
            "note": "SciBERT not available"
        }
    
    def _simple_research_similarity(self, text1: str, text2: str) -> SimpleResearchSimilarityResult:
        """Fallback simple research similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        jaccard_score = intersection / union if union > 0 else 0.0
        
        return {
            "similarity_score": jaccard_score,
            "method": "jaccard_similarity",
            "note": "SciBERT not available - using word overlap"
        }
    
    def get_service_info(self) -> GetServiceInfoResult:
        """Get SciBERT service information"""
        return {
            "service_name": "SciBERT Service",
            "model_loaded": self.model is not None,
            "device": self.device,
            "capabilities": [
                "Scientific literature analysis",
                "Research domain classification",
                "Cross-domain similarity analysis",
                "Paper type classification",
                "Interdisciplinary connection identification"
            ],
            "supported_domains": self.research_domains,
            "methodology_types": self.methodology_types,
            "model_info": "allenai/scibert_scivocab_uncased" if self.model else "Not loaded"
        }
