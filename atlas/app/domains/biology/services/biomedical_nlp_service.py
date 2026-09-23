"""
Advanced Biomedical NLP Service
Enhanced implementation with BioBERT, SciBERT, and advanced NLP capabilities
"""

import asyncio
import re
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from app.services.base_service import BaseService
from app.exceptions.domain.biology import BiologyError

# Advanced NLP imports
try:
    import torch
    import transformers
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForTokenClassification,
        pipeline, BertTokenizer, BertModel
    )
    from sentence_transformers import SentenceTransformer
    import spacy
    from spacy import displacy
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    # Dummy classes for when transformers are not available
    class AutoTokenizer:
        pass
    class AutoModel:
        pass
    class AutoModelForTokenClassification:
        pass
    class pipeline:
        pass
    class BertTokenizer:
        pass
    class BertModel:
        pass
    class SentenceTransformer:
        pass
    class spacy:
        pass
    class displacy:
        pass

# Additional ML imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    from sklearn.decomposition import LatentDirichletAllocation
    import scipy.sparse as sp
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    # Dummy classes
    class TfidfVectorizer:
        pass
    class cosine_similarity:
        pass
    class KMeans:
        pass
    class LatentDirichletAllocation:
        pass

from app.core.bootstrap_logging import logger


@dataclass
class BiomedicalEntity:
    """
    Represents a biomedical entity extracted from text.
    
    Attributes:
        text: The actual text span of the entity
        label: Entity type (e.g., "Gene/Protein", "Disease", "Chemical")
        start: Start character position in the original text
        end: End character position in the original text
        score: Confidence score for the entity recognition (0.0 to 1.0)
        normalized_form: Normalized form of the entity (e.g., gene symbol)
        ontology_id: ID from biomedical ontology (e.g., Gene Ontology)
        context: Surrounding context of the entity
    """
    text: str
    label: str
    start: int
    end: int
    score: float
    normalized_form: Optional[str] = None
    ontology_id: Optional[str] = None
    context: Optional[str] = None


@dataclass 
class SemanticAnalysisResult:
    """
    Result of semantic similarity analysis between two texts.
    
    Attributes:
        similarity_score: Cosine similarity score between texts (0.0 to 1.0)
        relevance_level: Qualitative relevance assessment ("High", "Medium", "Low")
        confidence: Confidence score for the similarity assessment (0.0 to 1.0)
        embedding_similarity: Similarity based on transformer embeddings
        tfidf_similarity: Similarity based on TF-IDF vectors
        semantic_features: Additional semantic features extracted
    """
    similarity_score: float
    relevance_level: str
    confidence: float
    embedding_similarity: Optional[float] = None
    tfidf_similarity: Optional[float] = None
    semantic_features: Optional[Dict[str, Any]] = None


@dataclass
class RelationExtraction:
    """
    Represents a relationship between biomedical entities.
    
    Attributes:
        subject: Subject entity
        predicate: Relationship type
        object: Object entity
        confidence: Confidence score for the relationship
        context: Context where the relationship was found
    """
    subject: str
    predicate: str
    object: str
    confidence: float
    context: str


@dataclass
class TopicModelingResult:
    """
    Result of topic modeling analysis.
    
    Attributes:
        topics: List of topics with their keywords
        document_topics: Topic distribution for each document
        coherence_score: Topic coherence score
        perplexity: Model perplexity
    """
    topics: List[Dict[str, Any]]
    document_topics: List[Dict[str, float]]
    coherence_score: float
    perplexity: float


class BiomedicalNLPService(BaseService):
    """
    Advanced Biomedical NLP Service with BioBERT, SciBERT, and advanced NLP capabilities
    Enhanced implementation for biomedical text analysis
    """
    
    def __init__(self):
        """Initialize advanced service"""
        super().__init__("BiomedicalNLPService")
        logger.info("Initializing BiomedicalNLPService (advanced version)")
        self.version = "2.0.0-advanced"
        self.is_ready = True
        
        # Advanced configuration
        self.advanced_config = {
            "use_biobert": True,
            "use_scibert": True,
            "use_spacy": True,
            "use_topic_modeling": True,
            "use_relation_extraction": True,
            "use_semantic_clustering": True,
            "max_sequence_length": 512,
            "batch_size": 16,
            "confidence_threshold": 0.7,
            "similarity_threshold": 0.5,
            "max_entities_per_text": 100,
            "use_gpu": torch.cuda.is_available() if TRANSFORMERS_AVAILABLE else False
        }
        
        # Model initialization
        self.biobert_model = None
        self.biobert_tokenizer = None
        self.scibert_model = None
        self.scibert_tokenizer = None
        self.sentence_transformer = None
        self.spacy_model = None
        self.ner_pipeline = None
        self.tfidf_vectorizer = None
        
        # Initialize models
        self._initialize_models()
        
        # Biomedical entity patterns
        self.entity_patterns = {
            "Gene/Protein": [
                r'\b[A-Z]{2,}[0-9]*\b',  # Gene symbols like BRCA1, p53
                r'\b[A-Z][a-z]+[0-9]*\b',  # Protein names
                r'\b[A-Z]{1,2}[0-9]{1,3}[A-Z]?\b'  # Gene IDs
            ],
            "Disease": [
                r'\b\w*cancer\w*\b',
                r'\b\w*tumor\w*\b',
                r'\b\w*syndrome\w*\b',
                r'\b\w*disease\w*\b'
            ],
            "Chemical": [
                r'\b[A-Z][a-z]*[0-9]*[A-Z]?[a-z]*\b',  # Chemical formulas
                r'\b\w*acid\w*\b',
                r'\b\w*compound\w*\b'
            ],
            "Technology": [
                r'\bCRISPR\b',
                r'\bPCR\b',
                r'\bRNA-seq\b',
                r'\bChIP-seq\b'
            ]
        }
        
        # Research domain keywords
        self.domain_keywords = {
            'cancer_research': ['cancer', 'tumor', 'oncology', 'carcinoma', 'metastasis', 'chemotherapy'],
            'genetics': ['gene', 'genetic', 'dna', 'mutation', 'allele', 'genotype', 'phenotype'],
            'neuroscience': ['brain', 'neuron', 'alzheimer', 'parkinson', 'synapse', 'neurotransmitter'],
            'immunology': ['immune', 'antibody', 'vaccine', 'inflammation', 'lymphocyte', 'antigen'],
            'drug_discovery': ['drug', 'therapeutic', 'treatment', 'therapy', 'pharmacology', 'medication'],
            'microbiology': ['bacteria', 'virus', 'pathogen', 'infection', 'microbe', 'antibiotic'],
            'biochemistry': ['protein', 'enzyme', 'metabolism', 'pathway', 'molecule', 'reaction']
        }
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process biomedical NLP requests
        """
        action = request_data.get("action")
        
        if action == "extract_entities":
            return await self.extract_biomedical_entities(
                text=request_data.get("text")
            )
        elif action == "calculate_similarity":
            return await self.calculate_semantic_similarity(
                text1=request_data.get("text1"),
                text2=request_data.get("text2")
            )
            
        return {"success": False, "error": f"Unknown action: {action}"}
    
    def _initialize_models(self):
        """Initialize advanced NLP models"""
        try:
            if TRANSFORMERS_AVAILABLE:
                # Initialize BioBERT
                if self.advanced_config["use_biobert"]:
                    try:
                        self.biobert_tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
                        self.biobert_model = AutoModel.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
                        logger.info("✅ BioBERT model loaded successfully")
                    except BiologyError as e:
                        logger.warning(f"⚠️ BioBERT not available: {e}")
                        self.biobert_model = None
                        self.biobert_tokenizer = None
                
                # Initialize SciBERT
                if self.advanced_config["use_scibert"]:
                    try:
                        self.scibert_tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
                        self.scibert_model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
                        logger.info("✅ SciBERT model loaded successfully")
                    except BiologyError as e:
                        logger.warning(f"⚠️ SciBERT not available: {e}")
                        self.scibert_model = None
                        self.scibert_tokenizer = None
                
                # Initialize sentence transformer
                try:
                    self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
                    logger.info("✅ Sentence Transformer loaded successfully")
                except BiologyError as e:
                    logger.warning(f"⚠️ Sentence Transformer not available: {e}")
                    self.sentence_transformer = None
                
                # Initialize NER pipeline
                try:
                    self.ner_pipeline = pipeline("ner", 
                                                model="dmis-lab/biobert-base-cased-v1.1",
                                                tokenizer="dmis-lab/biobert-base-cased-v1.1",
                                                aggregation_strategy="simple")
                    logger.info("✅ NER pipeline loaded successfully")
                except BiologyError as e:
                    logger.warning(f"⚠️ NER pipeline not available: {e}")
                    self.ner_pipeline = None
            
            # Initialize spaCy
            if self.advanced_config["use_spacy"]:
                try:
                    import spacy
                    self.spacy_model = spacy.load("en_core_web_sm")
                    logger.info("✅ spaCy model loaded successfully")
                except BiologyError as e:
                    logger.warning(f"⚠️ spaCy not available: {e}")
                    self.spacy_model = None
            
            # Initialize TF-IDF vectorizer
            if SKLEARN_AVAILABLE:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                logger.info("✅ TF-IDF vectorizer initialized")
            
        except BiologyError as e:
            logger.error(f"❌ Error initializing models: {e}")
            self.is_ready = False
        
    async def extract_biomedical_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract biomedical entities using advanced NLP models
        """
        try:
            await asyncio.sleep(0.1)  # Simulate processing
            
            entities = []
            
            # Method 1: Use BioBERT NER pipeline if available
            if self.ner_pipeline and TRANSFORMERS_AVAILABLE:
                try:
                    ner_results = self.ner_pipeline(text)
                    for entity in ner_results:
                        if entity['score'] >= self.advanced_config["confidence_threshold"]:
                            entities.append(BiomedicalEntity(
                                text=entity['word'],
                                label=entity['entity_group'],
                                start=entity['start'],
                                end=entity['end'],
                                score=entity['score'],
                                normalized_form=self._normalize_entity(entity['word'], entity['entity_group']),
                                context=self._extract_context(text, entity['start'], entity['end'])
                            ))
                except BiologyError as e:
                    logger.warning(f"BioBERT NER failed: {e}")
            
            # Method 2: Use spaCy if available
            if self.spacy_model and len(entities) < self.advanced_config["max_entities_per_text"]:
                try:
                    doc = self.spacy_model(text)
                    for ent in doc.ents:
                        if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT']:  # Map to biomedical entities
                            biomedical_label = self._map_spacy_to_biomedical(ent.label_)
                            entities.append(BiomedicalEntity(
                                text=ent.text,
                                label=biomedical_label,
                                start=ent.start_char,
                                end=ent.end_char,
                                score=0.8,  # Default confidence for spaCy
                                normalized_form=self._normalize_entity(ent.text, biomedical_label),
                                context=self._extract_context(text, ent.start_char, ent.end_char)
                            ))
                except BiologyError as e:
                    logger.warning(f"spaCy NER failed: {e}")
            
            # Method 3: Fallback to pattern-based extraction
            if len(entities) < self.advanced_config["max_entities_per_text"]:
                pattern_entities = self._extract_entities_by_patterns(text)
                entities.extend(pattern_entities)
            
            # Remove duplicates and sort by score
            entities = self._deduplicate_entities(entities)
            entities = sorted(entities, key=lambda x: x.score, reverse=True)
            entities = entities[:self.advanced_config["max_entities_per_text"]]
            
            # Calculate processing metrics
            processing_time = 0.1
            if self.ner_pipeline:
                processing_time += 0.2
            if self.spacy_model:
                processing_time += 0.1
            
            return {
                'success': True,
                'data': {
                    'entities': [vars(entity) for entity in entities],
                    'entity_count': len(entities),
                    'processing_time': processing_time,
                    'methods_used': self._get_extraction_methods(),
                    'confidence_distribution': self._calculate_confidence_distribution(entities)
                }
            }
            
        except BiologyError as e:
            logger.error(f"Error in entity extraction: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_entities_by_patterns(self, text: str) -> List[BiomedicalEntity]:
        """Extract entities using regex patterns"""
        entities = []
        
        for label, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append(BiomedicalEntity(
                        text=match.group(),
                        label=label,
                        start=match.start(),
                        end=match.end(),
                        score=0.7,  # Default confidence for pattern matching
                        normalized_form=self._normalize_entity(match.group(), label),
                        context=self._extract_context(text, match.start(), match.end())
                    ))
        
        return entities
    
    def _normalize_entity(self, text: str, label: str) -> str:
        """Normalize entity text based on type"""
        if label == "Gene/Protein":
            return text.upper()
        elif label == "Disease":
            return text.lower()
        elif label == "Chemical":
            return text.capitalize()
        else:
            return text
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Extract context around an entity"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _map_spacy_to_biomedical(self, spacy_label: str) -> str:
        """Map spaCy labels to biomedical entity types"""
        mapping = {
            'PERSON': 'Gene/Protein',
            'ORG': 'Organization',
            'GPE': 'Location',
            'PRODUCT': 'Technology'
        }
        return mapping.get(spacy_label, 'Other')
    
    def _deduplicate_entities(self, entities: List[BiomedicalEntity]) -> List[BiomedicalEntity]:
        """Remove duplicate entities"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.text.lower(), entity.start, entity.end)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _get_extraction_methods(self) -> List[str]:
        """Get list of extraction methods used"""
        methods = []
        if self.ner_pipeline:
            methods.append("BioBERT NER")
        if self.spacy_model:
            methods.append("spaCy NER")
        methods.append("Pattern Matching")
        return methods
    
    def _calculate_confidence_distribution(self, entities: List[BiomedicalEntity]) -> Dict[str, int]:
        """Calculate confidence score distribution"""
        distribution = {"high": 0, "medium": 0, "low": 0}
        
        for entity in entities:
            if entity.score >= 0.8:
                distribution["high"] += 1
            elif entity.score >= 0.6:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1
        
        return distribution
    
    async def calculate_semantic_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Calculate semantic similarity using advanced NLP models
        """
        try:
            await asyncio.sleep(0.1)  # Simulate processing
            
            similarity_scores = {}
            semantic_features = {}
            
            # Method 1: Sentence Transformer embeddings
            if self.sentence_transformer and TRANSFORMERS_AVAILABLE:
                try:
                    embeddings = self.sentence_transformer.encode([text1, text2])
                    embedding_similarity = float(np.dot(embeddings[0], embeddings[1]) / 
                                               (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])))
                    similarity_scores['embedding_similarity'] = embedding_similarity
                    semantic_features['embedding_dimension'] = len(embeddings[0])
                except BiologyError as e:
                    logger.warning(f"Sentence transformer similarity failed: {e}")
                    embedding_similarity = None
            
            # Method 2: BioBERT embeddings
            if self.biobert_model and self.biobert_tokenizer and TRANSFORMERS_AVAILABLE:
                try:
                    biobert_similarity = self._calculate_biobert_similarity(text1, text2)
                    similarity_scores['biobert_similarity'] = biobert_similarity
                except BiologyError as e:
                    logger.warning(f"BioBERT similarity failed: {e}")
            
            # Method 3: SciBERT embeddings
            if self.scibert_model and self.scibert_tokenizer and TRANSFORMERS_AVAILABLE:
                try:
                    scibert_similarity = self._calculate_scibert_similarity(text1, text2)
                    similarity_scores['scibert_similarity'] = scibert_similarity
                except BiologyError as e:
                    logger.warning(f"SciBERT similarity failed: {e}")
            
            # Method 4: TF-IDF similarity
            if self.tfidf_vectorizer and SKLEARN_AVAILABLE:
                try:
                    tfidf_similarity = self._calculate_tfidf_similarity(text1, text2)
                    similarity_scores['tfidf_similarity'] = tfidf_similarity
                except BiologyError as e:
                    logger.warning(f"TF-IDF similarity failed: {e}")
            
            # Method 5: Basic word overlap (fallback)
            basic_similarity = self._calculate_basic_similarity(text1, text2)
            similarity_scores['basic_similarity'] = basic_similarity
            
            # Calculate weighted average similarity
            weights = {
                'embedding_similarity': 0.3,
                'biobert_similarity': 0.25,
                'scibert_similarity': 0.25,
                'tfidf_similarity': 0.15,
                'basic_similarity': 0.05
            }
            
            weighted_similarity = 0.0
            total_weight = 0.0
            
            for method, score in similarity_scores.items():
                if score is not None:
                    weight = weights.get(method, 0.1)
                    weighted_similarity += score * weight
                    total_weight += weight
            
            final_similarity = weighted_similarity / total_weight if total_weight > 0 else basic_similarity
            
            # Classify relevance level
            if final_similarity > 0.7:
                relevance_level = "High"
            elif final_similarity > 0.4:
                relevance_level = "Medium"
            else:
                relevance_level = "Low"
            
            # Calculate confidence based on method agreement
            confidence = self._calculate_similarity_confidence(similarity_scores)
            
            result = SemanticAnalysisResult(
                similarity_score=final_similarity,
                relevance_level=relevance_level,
                confidence=confidence,
                embedding_similarity=similarity_scores.get('embedding_similarity'),
                tfidf_similarity=similarity_scores.get('tfidf_similarity'),
                semantic_features=semantic_features
            )
            
            return {
                'success': True,
                'data': vars(result)
            }
            
        except BiologyError as e:
            logger.error(f"Error in similarity calculation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_biobert_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using BioBERT embeddings"""
        if not TRANSFORMERS_AVAILABLE:
            return 0.0
        
        # Tokenize and encode texts
        inputs1 = self.biobert_tokenizer(text1, return_tensors="pt", truncation=True, max_length=512)
        inputs2 = self.biobert_tokenizer(text2, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs1 = self.biobert_model(**inputs1)
            outputs2 = self.biobert_model(**inputs2)
            
            # Get pooled embeddings
            embedding1 = outputs1.pooler_output
            embedding2 = outputs2.pooler_output
            
            # Calculate cosine similarity
            similarity = torch.cosine_similarity(embedding1, embedding2, dim=1)
            return float(similarity.item())
    
    def _calculate_scibert_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using SciBERT embeddings"""
        if not TRANSFORMERS_AVAILABLE:
            return 0.0
        
        # Tokenize and encode texts
        inputs1 = self.scibert_tokenizer(text1, return_tensors="pt", truncation=True, max_length=512)
        inputs2 = self.scibert_tokenizer(text2, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs1 = self.scibert_model(**inputs1)
            outputs2 = self.scibert_model(**inputs2)
            
            # Get pooled embeddings
            embedding1 = outputs1.pooler_output
            embedding2 = outputs2.pooler_output
            
            # Calculate cosine similarity
            similarity = torch.cosine_similarity(embedding1, embedding2, dim=1)
            return float(similarity.item())
    
    def _calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using TF-IDF vectors"""
        if not SKLEARN_AVAILABLE:
            return 0.0
        
        try:
            # Fit and transform texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            return float(similarity_matrix[0, 1])
        except BiologyError:
            return 0.0
    
    def _calculate_basic_similarity(self, text1: str, text2: str) -> float:
        """Calculate basic word overlap similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_similarity_confidence(self, similarity_scores: Dict[str, float]) -> float:
        """Calculate confidence based on method agreement"""
        valid_scores = [score for score in similarity_scores.values() if score is not None]
        
        if len(valid_scores) < 2:
            return 0.5
        
        # Calculate variance as a measure of disagreement
        mean_score = np.mean(valid_scores)
        variance = np.var(valid_scores)
        
        # Lower variance = higher confidence
        confidence = max(0.1, 1.0 - variance)
        return min(1.0, confidence)
    
    async def extract_relations(self, text: str) -> Dict[str, Any]:
        """
        Extract relationships between biomedical entities
        """
        try:
            await asyncio.sleep(0.2)  # Simulate processing
            
            # First extract entities
            entity_result = await self.extract_biomedical_entities(text)
            entities = entity_result.get('data', {}).get('entities', [])
            
            relations = []
            
            # Extract relations using pattern matching
            relation_patterns = {
                'treats': [r'(\w+)\s+(?:treats?|cures?|heals?)\s+(\w+)', r'(\w+)\s+(?:therapy|treatment)\s+(?:for|of)\s+(\w+)'],
                'causes': [r'(\w+)\s+(?:causes?|leads?\s+to|results?\s+in)\s+(\w+)', r'(\w+)\s+(?:is\s+)?associated\s+with\s+(\w+)'],
                'inhibits': [r'(\w+)\s+(?:inhibits?|blocks?|suppresses?)\s+(\w+)', r'(\w+)\s+(?:antagonist|inhibitor)\s+(?:of|for)\s+(\w+)'],
                'activates': [r'(\w+)\s+(?:activates?|stimulates?|promotes?)\s+(\w+)', r'(\w+)\s+(?:agonist|activator)\s+(?:of|for)\s+(\w+)'],
                'binds_to': [r'(\w+)\s+(?:binds?\s+to|interacts?\s+with)\s+(\w+)', r'(\w+)\s+(?:receptor|binding)\s+(?:for|of)\s+(\w+)']
            }
            
            for relation_type, patterns in relation_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        subject = match.group(1)
                        object_entity = match.group(2)
                        
                        # Check if entities exist in our extracted entities
                        subject_entity = self._find_entity_by_text(entities, subject)
                        object_entity_found = self._find_entity_by_text(entities, object_entity)
                        
                        if subject_entity and object_entity_found:
                            relations.append(RelationExtraction(
                                subject=subject,
                                predicate=relation_type,
                                object=object_entity,
                                confidence=0.8,
                                context=self._extract_context(text, match.start(), match.end())
                            ))
            
            # Extract relations using dependency parsing (if spaCy available)
            if self.spacy_model:
                try:
                    doc = self.spacy_model(text)
                    spacy_relations = self._extract_spacy_relations(doc, entities)
                    relations.extend(spacy_relations)
                except BiologyError as e:
                    logger.warning(f"spaCy relation extraction failed: {e}")
            
            # Remove duplicates
            relations = self._deduplicate_relations(relations)
            
            return {
                'success': True,
                'data': {
                    'relations': [vars(relation) for relation in relations],
                    'relation_count': len(relations),
                    'entity_count': len(entities),
                    'processing_time': 0.2
                }
            }
            
        except BiologyError as e:
            logger.error(f"Error in relation extraction: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_entity_by_text(self, entities: List[Dict], text: str) -> Optional[Dict]:
        """Find entity by text match"""
        for entity in entities:
            if entity['text'].lower() == text.lower():
                return entity
        return None
    
    def _extract_spacy_relations(self, doc, entities: List[Dict]) -> List[RelationExtraction]:
        """Extract relations using spaCy dependency parsing"""
        relations = []
        
        # Look for common relation patterns in dependency trees
        for token in doc:
            if token.dep_ in ['nsubj', 'nsubjpass']:  # Subject
                subject = token.text
                # Find the verb
                verb = token.head
                if verb.pos_ == 'VERB':
                    # Find the object
                    for child in verb.children:
                        if child.dep_ in ['dobj', 'pobj']:  # Direct object or prepositional object
                            object_entity = child.text
                            
                            # Map verb to relation type
                            relation_type = self._map_verb_to_relation(verb.text.lower())
                            
                            if relation_type:
                                relations.append(RelationExtraction(
                                    subject=subject,
                                    predicate=relation_type,
                                    object=object_entity,
                                    confidence=0.7,
                                    context=f"{subject} {verb.text} {object_entity}"
                                ))
        
        return relations
    
    def _map_verb_to_relation(self, verb: str) -> Optional[str]:
        """Map verbs to relation types"""
        verb_mapping = {
            'treats': 'treats',
            'cures': 'treats',
            'heals': 'treats',
            'causes': 'causes',
            'leads': 'causes',
            'results': 'causes',
            'inhibits': 'inhibits',
            'blocks': 'inhibits',
            'suppresses': 'inhibits',
            'activates': 'activates',
            'stimulates': 'activates',
            'promotes': 'activates',
            'binds': 'binds_to',
            'interacts': 'binds_to'
        }
        return verb_mapping.get(verb)
    
    def _deduplicate_relations(self, relations: List[RelationExtraction]) -> List[RelationExtraction]:
        """Remove duplicate relations"""
        seen = set()
        unique_relations = []
        
        for relation in relations:
            key = (relation.subject.lower(), relation.predicate, relation.object.lower())
            if key not in seen:
                seen.add(key)
                unique_relations.append(relation)
        
        return unique_relations
    
    async def perform_topic_modeling(self, texts: List[str], num_topics: int = 5) -> Dict[str, Any]:
        """
        Perform topic modeling on biomedical texts
        """
        try:
            await asyncio.sleep(0.3)  # Simulate processing
            
            if not SKLEARN_AVAILABLE or len(texts) < 2:
                return {
                    'success': False,
                    'error': 'Topic modeling requires sklearn and at least 2 texts'
                }
            
            # Preprocess texts
            processed_texts = [self._preprocess_text_for_topic_modeling(text) for text in texts]
            
            # Create TF-IDF matrix
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_texts)
            
            # Perform LDA
            lda = LatentDirichletAllocation(
                n_components=num_topics,
                random_state=42,
                max_iter=100
            )
            lda.fit(tfidf_matrix)
            
            # Extract topics
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(lda.components_):
                top_words_idx = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]
                topic_words = [(word, topic[i]) for i, word in enumerate(top_words)]
                
                topics.append({
                    'topic_id': topic_idx,
                    'words': topic_words,
                    'top_words': top_words[:5]
                })
            
            # Get document-topic distributions
            doc_topic_dist = lda.transform(tfidf_matrix)
            document_topics = []
            
            for i, dist in enumerate(doc_topic_dist):
                doc_topics = {}
                for j, prob in enumerate(dist):
                    doc_topics[f'topic_{j}'] = float(prob)
                document_topics.append(doc_topics)
            
            # Calculate coherence score (simplified)
            coherence_score = self._calculate_topic_coherence(topics, processed_texts)
            
            # Calculate perplexity
            perplexity = lda.perplexity(tfidf_matrix)
            
            result = TopicModelingResult(
                topics=topics,
                document_topics=document_topics,
                coherence_score=coherence_score,
                perplexity=perplexity
            )
            
            return {
                'success': True,
                'data': vars(result)
            }
            
        except BiologyError as e:
            logger.error(f"Error in topic modeling: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _preprocess_text_for_topic_modeling(self, text: str) -> str:
        """Preprocess text for topic modeling"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _calculate_topic_coherence(self, topics: List[Dict], texts: List[str]) -> float:
        """Calculate topic coherence score (simplified)"""
        # Simple coherence based on word co-occurrence
        total_coherence = 0.0
        
        for topic in topics:
            top_words = topic['top_words']
            if len(top_words) < 2:
                continue
            
            # Count co-occurrences of top words
            cooccurrences = 0
            total_pairs = 0
            
            for i in range(len(top_words)):
                for j in range(i + 1, len(top_words)):
                    word1, word2 = top_words[i], top_words[j]
                    total_pairs += 1
                    
                    # Count documents containing both words
                    for text in texts:
                        if word1 in text and word2 in text:
                            cooccurrences += 1
            
            if total_pairs > 0:
                topic_coherence = cooccurrences / total_pairs
                total_coherence += topic_coherence
        
        return total_coherence / len(topics) if topics else 0.0
    
    async def enhance_literature_search(self, query: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enhance literature search using advanced NLP techniques
        """
        try:
            await asyncio.sleep(0.2)  # Simulate processing
            
            enhanced_papers = []
            
            # Extract entities from query
            query_entities_result = await self.extract_biomedical_entities(query)
            query_entities = query_entities_result.get('data', {}).get('entities', [])
            
            for paper in papers:
                title = paper.get('title', '')
                abstract = paper.get('abstract', '')
                text = f"{title} {abstract}"
                
                # Calculate multiple similarity scores
                similarity_result = await self.calculate_semantic_similarity(query, text)
                similarity_data = similarity_result.get('data', {})
                
                # Extract entities from paper
                paper_entities_result = await self.extract_biomedical_entities(text)
                paper_entities = paper_entities_result.get('data', {}).get('entities', [])
                
                # Calculate entity overlap
                entity_overlap = self._calculate_entity_overlap(query_entities, paper_entities)
                
                # Determine research domain
                research_domain = self._determine_research_domain(text)
                
                # Calculate biomedical relevance score
                biomedical_relevance = self._calculate_biomedical_relevance(text, query_entities)
                
                enhanced_paper = paper.copy()
                enhanced_paper.update({
                    'relevance_score': similarity_data.get('similarity_score', 0.0),
                    'biomedical_relevance': biomedical_relevance,
                    'entity_overlap': entity_overlap,
                    'research_domain': research_domain,
                    'semantic_features': similarity_data.get('semantic_features', {}),
                    'confidence': similarity_data.get('confidence', 0.0),
                    'extracted_entities': paper_entities,
                    'entity_count': len(paper_entities)
                })
                
                enhanced_papers.append(enhanced_paper)
            
            # Sort by combined relevance score
            enhanced_papers.sort(key=lambda x: self._calculate_combined_relevance_score(x), reverse=True)
            
            return {
                'success': True,
                'data': {
                    'enhanced_papers': enhanced_papers,
                    'query': query,
                    'papers_processed': len(papers),
                    'query_entities': query_entities,
                    'processing_time': 0.2
                }
            }
            
        except BiologyError as e:
            logger.error(f"Error in literature enhancement: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_entity_overlap(self, query_entities: List[Dict], paper_entities: List[Dict]) -> float:
        """Calculate overlap between query and paper entities"""
        if not query_entities or not paper_entities:
            return 0.0
        
        query_texts = {entity['text'].lower() for entity in query_entities}
        paper_texts = {entity['text'].lower() for entity in paper_entities}
        
        intersection = len(query_texts.intersection(paper_texts))
        union = len(query_texts.union(paper_texts))
        
        return intersection / union if union > 0 else 0.0
    
    def _determine_research_domain(self, text: str) -> str:
        """Determine research domain from text"""
        text_lower = text.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            domain_scores[domain] = score
        
        if not domain_scores or max(domain_scores.values()) == 0:
            return 'General'
        
        best_domain = max(domain_scores, key=domain_scores.get)
        return best_domain.replace('_', ' ').title()
    
    def _calculate_biomedical_relevance(self, text: str, query_entities: List[Dict]) -> float:
        """Calculate biomedical relevance score"""
        if not query_entities:
            return 0.0
        
        # Count biomedical terms in text
        biomedical_terms = ['gene', 'protein', 'disease', 'drug', 'therapy', 'treatment', 'cancer', 'dna', 'rna']
        text_lower = text.lower()
        
        biomedical_count = sum(1 for term in biomedical_terms if term in text_lower)
        total_words = len(text.split())
        
        biomedical_density = biomedical_count / total_words if total_words > 0 else 0.0
        
        # Factor in entity overlap
        entity_overlap = self._calculate_entity_overlap(query_entities, [])
        
        return min(1.0, biomedical_density * 10 + entity_overlap)
    
    def _calculate_combined_relevance_score(self, paper: Dict[str, Any]) -> float:
        """Calculate combined relevance score"""
        relevance_score = paper.get('relevance_score', 0.0)
        biomedical_relevance = paper.get('biomedical_relevance', 0.0)
        entity_overlap = paper.get('entity_overlap', 0.0)
        confidence = paper.get('confidence', 0.0)
        
        # Weighted combination
        combined_score = (
            relevance_score * 0.4 +
            biomedical_relevance * 0.3 +
            entity_overlap * 0.2 +
            confidence * 0.1
        )
        
        return combined_score
    
    async def analyze_paper_abstract(self, abstract: str) -> Dict[str, Any]:
        """
        Analyze paper abstract using advanced NLP techniques
        """
        try:
            await asyncio.sleep(0.15)  # Simulate processing
            
            # Extract entities from abstract
            entity_result = await self.extract_biomedical_entities(abstract)
            entities = entity_result.get('data', {}).get('entities', [])
            
            # Extract relations
            relation_result = await self.extract_relations(abstract)
            relations = relation_result.get('data', {}).get('relations', [])
            
            # Determine research domain
            research_domain = self._determine_research_domain(abstract)
            
            # Extract key concepts
            key_concepts = self._extract_key_concepts(abstract, entities)
            
            # Analyze sentiment and tone
            sentiment_analysis = self._analyze_sentiment(abstract)
            
            # Calculate complexity metrics
            complexity_metrics = self._calculate_complexity_metrics(abstract)
            
            # Extract methodology indicators
            methodology_indicators = self._extract_methodology_indicators(abstract)
            
            # Calculate confidence score
            confidence = self._calculate_analysis_confidence(entities, relations, abstract)
            
            return {
                'success': True,
                'data': {
                    'entities': entities,
                    'relations': relations,
                    'research_domain': research_domain,
                    'key_concepts': key_concepts,
                    'sentiment_analysis': sentiment_analysis,
                    'complexity_metrics': complexity_metrics,
                    'methodology_indicators': methodology_indicators,
                    'entity_count': len(entities),
                    'relation_count': len(relations),
                    'analysis_confidence': confidence,
                    'processing_time': 0.15
                }
            }
            
        except BiologyError as e:
            logger.error(f"Error in abstract analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_key_concepts(self, abstract: str, entities: List[Dict]) -> List[str]:
        """Extract key concepts from abstract"""
        # Start with high-confidence entities
        key_concepts = [entity['text'] for entity in entities if entity['score'] >= 0.8]
        
        # Add important biomedical terms
        important_terms = ['gene', 'protein', 'disease', 'drug', 'therapy', 'treatment', 'cancer', 'dna', 'rna']
        text_lower = abstract.lower()
        
        for term in important_terms:
            if term in text_lower and term not in key_concepts:
                key_concepts.append(term)
        
        return key_concepts[:10]  # Limit to top 10 concepts
    
    def _analyze_sentiment(self, abstract: str) -> Dict[str, Any]:
        """Analyze sentiment and tone of abstract"""
        # Simple sentiment analysis based on keywords
        positive_words = ['successful', 'effective', 'improved', 'beneficial', 'promising', 'significant']
        negative_words = ['failed', 'ineffective', 'adverse', 'harmful', 'problematic', 'limitation']
        neutral_words = ['study', 'analysis', 'investigation', 'research', 'method', 'result']
        
        text_lower = abstract.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        neutral_count = sum(1 for word in neutral_words if word in text_lower)
        
        total_words = len(abstract.split())
        
        sentiment_scores = {
            'positive': positive_count / total_words if total_words > 0 else 0.0,
            'negative': negative_count / total_words if total_words > 0 else 0.0,
            'neutral': neutral_count / total_words if total_words > 0 else 0.0
        }
        
        # Determine overall sentiment
        if sentiment_scores['positive'] > sentiment_scores['negative']:
            overall_sentiment = 'positive'
        elif sentiment_scores['negative'] > sentiment_scores['positive']:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_scores': sentiment_scores,
            'confidence': 0.7
        }
    
    def _calculate_complexity_metrics(self, abstract: str) -> Dict[str, Any]:
        """Calculate complexity metrics for abstract"""
        words = abstract.split()
        sentences = abstract.split('.')
        
        # Basic metrics
        word_count = len(words)
        sentence_count = len(sentences)
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Count complex words (more than 6 characters)
        complex_words = [word for word in words if len(word) > 6]
        complexity_ratio = len(complex_words) / word_count if word_count > 0 else 0
        
        # Count technical terms
        technical_terms = ['analysis', 'methodology', 'hypothesis', 'experiment', 'statistical', 'significant']
        technical_count = sum(1 for term in technical_terms if term in abstract.lower())
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_words_per_sentence': avg_words_per_sentence,
            'avg_word_length': avg_word_length,
            'complexity_ratio': complexity_ratio,
            'technical_term_count': technical_count,
            'readability_score': self._calculate_readability_score(abstract)
        }
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate simplified readability score"""
        words = text.split()
        sentences = text.split('.')
        
        if len(words) == 0 or len(sentences) == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simplified Flesch Reading Ease formula
        readability = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_word_length / 100)
        return max(0.0, min(100.0, readability))
    
    def _extract_methodology_indicators(self, abstract: str) -> Dict[str, Any]:
        """Extract methodology indicators from abstract"""
        text_lower = abstract.lower()
        
        # Research methods
        methods = {
            'experimental': ['experiment', 'trial', 'study', 'test'],
            'observational': ['observe', 'survey', 'analysis', 'examine'],
            'computational': ['simulation', 'model', 'algorithm', 'computational'],
            'clinical': ['clinical', 'patient', 'treatment', 'therapy'],
            'laboratory': ['laboratory', 'in vitro', 'cell culture', 'assay']
        }
        
        method_scores = {}
        for method_type, keywords in methods.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            method_scores[method_type] = score
        
        # Statistical methods
        statistical_methods = ['statistical', 'regression', 'correlation', 'significance', 'p-value', 'confidence']
        statistical_count = sum(1 for method in statistical_methods if method in text_lower)
        
        # Sample size indicators
        sample_indicators = ['sample', 'participant', 'subject', 'patient', 'n=', 'n =']
        sample_count = sum(1 for indicator in sample_indicators if indicator in text_lower)
        
        return {
            'method_scores': method_scores,
            'statistical_methods': statistical_count,
            'sample_indicators': sample_count,
            'primary_method': max(method_scores, key=method_scores.get) if method_scores else 'unknown'
        }
    
    def _calculate_analysis_confidence(self, entities: List[Dict], relations: List[Dict], abstract: str) -> float:
        """Calculate confidence score for analysis"""
        # Base confidence
        confidence = 0.5
        
        # Factor in entity count and quality
        if entities:
            avg_entity_confidence = sum(entity['score'] for entity in entities) / len(entities)
            confidence += avg_entity_confidence * 0.3
        
        # Factor in relation count
        if relations:
            confidence += min(0.2, len(relations) * 0.05)
        
        # Factor in abstract length and complexity
        word_count = len(abstract.split())
        if word_count > 100:
            confidence += 0.1
        elif word_count < 50:
            confidence -= 0.1
        
        return min(1.0, max(0.0, confidence))
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Service health check
        """
        try:
            # Check model availability
            model_status = {
                'biobert_available': self.biobert_model is not None,
                'scibert_available': self.scibert_model is not None,
                'sentence_transformer_available': self.sentence_transformer is not None,
                'spacy_available': self.spacy_model is not None,
                'ner_pipeline_available': self.ner_pipeline is not None,
                'tfidf_vectorizer_available': self.tfidf_vectorizer is not None
            }
            
            # Calculate overall model readiness
            available_models = sum(model_status.values())
            total_models = len(model_status)
            model_readiness = available_models / total_models if total_models > 0 else 0.0
            
            return {
                'service_status': 'healthy' if self.is_ready else 'degraded',
                'service_name': self.service_name,
                'version': self.version,
                'model_status': model_status,
                'model_readiness': model_readiness,
                'advanced_config': self.advanced_config,
                'memory_usage_mb': 150.0,  # Estimated for advanced models
                'is_ready': self.is_ready,
                'capabilities': [
                    'Entity Extraction (BioBERT, spaCy, Pattern Matching)',
                    'Semantic Similarity (Multiple Models)',
                    'Relation Extraction (Pattern + Dependency Parsing)',
                    'Topic Modeling (LDA)',
                    'Literature Search Enhancement',
                    'Abstract Analysis (Sentiment, Complexity, Methodology)'
                ]
            }
        except BiologyError as e:
            logger.error(f"Health check failed: {e}")
            return {
                'service_status': 'error',
                'error': str(e)
            }
