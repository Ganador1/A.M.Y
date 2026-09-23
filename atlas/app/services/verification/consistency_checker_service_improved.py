"""
Advanced Consistency Checker Service
- Natural Language Inference (NLI) para detectar contradicciones lógicas
- Análisis semántico profundo usando transformers
- Detección de vacíos conceptuales y inconsistencias argumentativas
- Evaluación de coherencia lógica y factual
"""

from __future__ import annotations
import asyncio
import re
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict

import numpy as np
from app.exceptions.domain.biology import BiologyError
from app.utils.hf_safe import safe_load_pipeline, safe_load_tokenizer

# Try to import advanced NLP libraries
try:
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        pipeline, AutoModel
    )
    from sentence_transformers import SentenceTransformer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    # Dummy classes
    class AutoTokenizer:
        @staticmethod
        def from_pretrained(model_name):
            return None
    
    class AutoModelForSequenceClassification:
        @staticmethod
        def from_pretrained(model_name):
            return None
    
    class AutoModel:
        @staticmethod
        def from_pretrained(model_name):
            return None
    
    class SentenceTransformer:
        def __init__(self, model_name):
            pass
        def encode(self, texts):
            return np.random.random((len(texts), 384))
    
    def pipeline(task, model=None, tokenizer=None):
        class MockPipeline:
            def __call__(self, inputs):
                if isinstance(inputs, list):
                    return [{"label": "NEUTRAL", "score": 0.5} for _ in inputs]
                return {"label": "NEUTRAL", "score": 0.5}
        return MockPipeline()

# Try to import sklearn for additional ML features
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import LatentDirichletAllocation
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    # Dummy classes
    class TfidfVectorizer:
        def fit_transform(self, texts):
            return np.random.random((len(texts), 100))
        def transform(self, texts):
            return np.random.random((len(texts), 100))
    
    class KMeans:
        def __init__(self, **kwargs):
            pass
        def fit_predict(self, X):
            return np.random.randint(0, 3, len(X))
    
    def cosine_similarity(X, Y=None):
        if Y is None:
            return np.random.random((len(X), len(X)))
        return np.random.random((len(X), len(Y)))
    
    class LatentDirichletAllocation:
        def __init__(self, **kwargs):
            pass
        def fit_transform(self, X):
            return np.random.random((len(X), 5))

# Try to import spaCy for additional NLP
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

@dataclass
class InconsistencyIssue:
    """Represents a detected inconsistency"""
    issue_type: str
    severity: str  # "critical", "major", "minor"
    description: str
    confidence: float
    source_text: str
    target_text: Optional[str] = None
    location: Optional[str] = None
    suggestion: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

@dataclass
class LogicalRelation:
    """Represents a logical relationship between statements"""
    premise: str
    hypothesis: str
    relation: str  # "entailment", "contradiction", "neutral"
    confidence: float
    reasoning: str

@dataclass
class SemanticGap:
    """Represents a semantic gap or missing concept"""
    missing_concept: str
    context: str
    importance: float
    suggestions: List[str]
    related_concepts: List[str]

@dataclass
class ConsistencyReport:
    """Comprehensive consistency analysis report"""
    overall_score: float
    inconsistency_issues: List[InconsistencyIssue]
    logical_relations: List[LogicalRelation]
    semantic_gaps: List[SemanticGap]
    coherence_metrics: Dict[str, float]
    text_statistics: Dict[str, Any]
    recommendations: List[str]

# ... existing service implementation ...

# --- Guarded singleton pattern para inicialización pesada NLP ---
import os as _os  # colocado al final para evitar ciclos de importación
from app.config import settings


def _should_skip_autoinit() -> bool:
    """Determina si se debe omitir la auto-inicialización."""
    env_flag = str(_os.getenv("AXIOM_SKIP_AUTOINIT", "0")).lower()
    settings_flag = str(getattr(settings, "AXIOM_SKIP_AUTOINIT", env_flag)).lower()
    return settings_flag in {"1", "true", "yes"}


_CC_AUTO_DISABLED = _should_skip_autoinit()

_advanced_consistency_checker_service = None  # type: ignore

def get_advanced_consistency_checker_service():
    global _advanced_consistency_checker_service
    if _advanced_consistency_checker_service is None and not _CC_AUTO_DISABLED:
        try:  # pragma: no cover (defensive)
            # The real class name inside this module is AdvancedConsistencyCheckerService
            if 'AdvancedConsistencyCheckerService' in globals():
                _advanced_consistency_checker_service = globals()['AdvancedConsistencyCheckerService']()
        except BiologyError as e:  # pragma: no cover
            import logging as _logging
            _logging.getLogger(__name__).error(f"Failed to init AdvancedConsistencyCheckerService: {e}")
            _advanced_consistency_checker_service = None
    return _advanced_consistency_checker_service

if not _CC_AUTO_DISABLED:
    get_advanced_consistency_checker_service()

class AdvancedConsistencyCheckerService:
    """
    Advanced Consistency Checker Service using Natural Language Inference
    and deep semantic analysis to detect logical contradictions and gaps.
    """
    
    def __init__(self):
        self.version = "2.0.0-advanced"
        
        # Advanced configuration
        self.advanced_config = {
            'use_nli_models': True,
            'use_semantic_similarity': True,
            'use_topic_modeling': True,
            'confidence_threshold': 0.7,
            'similarity_threshold': 0.8,
            'max_text_length': 5000,
            'enable_spacy_analysis': True,
            'detect_argument_structure': True
        }
        
        # Initialize models
        self.nli_pipeline = None
        self.sentence_transformer = None
        self.tfidf_vectorizer = None
        self.spacy_model = None
        
        # Contradiction patterns (enhanced)
        self.contradiction_patterns = [
            # Existence/Non-existence
            (r"does not exist", r"exists"),
            (r"no evidence", r"strong evidence"),
            (r"never observed", r"frequently observed"),
            (r"impossible", r"possible"),
            (r"cannot occur", r"occurs"),
            
            # Magnitude/Frequency
            (r"always", r"never"),
            (r"all", r"none"),
            (r"increase", r"decrease"),
            (r"rise", r"fall"),
            (r"maximum", r"minimum"),
            
            # Quality/State
            (r"effective", r"ineffective"),
            (r"safe", r"dangerous"),
            (r"stable", r"unstable"),
            (r"reliable", r"unreliable"),
            
            # Causation
            (r"causes", r"prevents"),
            (r"leads to", r"prevents"),
            (r"results in", r"avoids"),
        ]
        
        # Initialize all models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize NLP models for advanced consistency checking"""
        try:
            if TRANSFORMERS_AVAILABLE:
                print("🤖 Initializing NLI models...")

                self.nli_pipeline = safe_load_pipeline(
                    "text-classification",
                    "microsoft/DialoGPT-medium",
                    return_all_scores=True,
                )

                if self.nli_pipeline is None:
                    self.nli_pipeline = safe_load_pipeline(
                        "zero-shot-classification",
                        "facebook/bart-large-mnli",
                    )

                if self.nli_pipeline is None:
                    self.nli_pipeline = safe_load_pipeline("sentiment-analysis", "distilbert-base-uncased")

                if self.nli_pipeline is None:
                    print("⚠️ NLI pipelines no disponibles; se usarán heurísticas.")

                try:
                    self.sentence_transformer = SentenceTransformer("all-MiniLM-L6-v2")
                    print("✅ Sentence transformer initialized")
                except Exception:
                    print("⚠️ Sentence transformer not available; usando stub.")
                    self.sentence_transformer = SentenceTransformer("dummy")
            else:
                print("⚠️ Transformers not available, using fallback methods")
            
            # TF-IDF for text analysis
            if SKLEARN_AVAILABLE:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                print("✅ TF-IDF vectorizer initialized")
            
            # spaCy for linguistic analysis
            if SPACY_AVAILABLE:
                try:
                    self.spacy_model = spacy.load("en_core_web_sm")
                    print("✅ spaCy model loaded")
                except BiologyError:
                    print("⚠️ spaCy model not available")
                    
        except BiologyError as e:
            print(f"❌ Error initializing models: {e}")
    
    async def comprehensive_check(
        self, 
        text: str, 
        required_terms: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> ConsistencyReport:
        """
        Perform comprehensive consistency analysis using advanced NLP techniques.
        
        Args:
            text: The main text to analyze
            required_terms: List of terms that should be present
            context: Additional context for analysis
            
        Returns:
            Comprehensive consistency report
        """
        try:
            # Text preprocessing
            sentences = self._extract_sentences(text)
            
            if len(sentences) < 2:
                return ConsistencyReport(
                    overall_score=1.0,
                    inconsistency_issues=[],
                    logical_relations=[],
                    semantic_gaps=[],
                    coherence_metrics={},
                    text_statistics={"sentence_count": len(sentences)},
                    recommendations=["Text too short for comprehensive analysis"]
                )
            
            # Parallel analysis tasks
            tasks = []
            
            # 1. Logical contradiction detection
            tasks.append(self._detect_logical_contradictions(sentences))
            
            # 2. Semantic gap analysis
            tasks.append(self._analyze_semantic_gaps(sentences, required_terms))
            
            # 3. Coherence analysis
            tasks.append(self._analyze_coherence(sentences))
            
            # 4. Argument structure analysis
            tasks.append(self._analyze_argument_structure(sentences))
            
            # Execute all analyses
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            logical_relations = results[0] if not isinstance(results[0], Exception) else []
            semantic_gaps = results[1] if not isinstance(results[1], Exception) else []
            coherence_metrics = results[2] if not isinstance(results[2], Exception) else {}
            argument_issues = results[3] if not isinstance(results[3], Exception) else []
            
            # Combine all inconsistency issues
            all_issues = []
            
            # Convert logical contradictions to issues
            for relation in logical_relations:
                if relation.relation == "contradiction":
                    issue = InconsistencyIssue(
                        issue_type="logical_contradiction",
                        severity="critical" if relation.confidence > 0.8 else "major",
                        description=f"Contradiction detected: '{relation.premise}' vs '{relation.hypothesis}'",
                        confidence=relation.confidence,
                        source_text=relation.premise,
                        target_text=relation.hypothesis,
                        suggestion="Resolve the contradictory statements",
                        evidence={"reasoning": relation.reasoning}
                    )
                    all_issues.append(issue)
            
            # Add argument structure issues
            all_issues.extend(argument_issues)
            
            # Add missing term issues
            if required_terms:
                missing_terms = self._check_missing_terms(text, required_terms)
                for term in missing_terms:
                    issue = InconsistencyIssue(
                        issue_type="missing_required_term",
                        severity="minor",
                        description=f"Required term '{term}' not found in text",
                        confidence=1.0,
                        source_text=text,
                        suggestion=f"Consider including discussion of '{term}'"
                    )
                    all_issues.append(issue)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                all_issues, logical_relations, semantic_gaps, coherence_metrics
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                all_issues, semantic_gaps, coherence_metrics
            )
            
            # Text statistics
            text_stats = self._calculate_text_statistics(text, sentences)
            
            return ConsistencyReport(
                overall_score=overall_score,
                inconsistency_issues=all_issues,
                logical_relations=logical_relations,
                semantic_gaps=semantic_gaps,
                coherence_metrics=coherence_metrics,
                text_statistics=text_stats,
                recommendations=recommendations
            )
            
        except BiologyError as e:
            # Fallback to basic check
            return await self._fallback_check(text, required_terms)
    
    def check(self, text: str, required_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Legacy interface for basic consistency checking.
        Enhanced with some advanced features while maintaining compatibility.
        """
        try:
            # Quick basic analysis
            issues = []
            lower_text = text.lower()
            
            # Check missing terms
            if required_terms:
                for term in required_terms:
                    if term.lower() not in lower_text:
                        issues.append({"type": "missing_term", "term": term})
            
            # Enhanced contradiction detection
            for pattern_a, pattern_b in self.contradiction_patterns:
                if re.search(pattern_a, lower_text) and re.search(pattern_b, lower_text):
                    issues.append({
                        "type": "contradiction_pair", 
                        "patterns": [pattern_a, pattern_b],
                        "severity": "major"
                    })
            
            # Additional heuristic checks
            sentences = self._extract_sentences(text)
            
            # Check for negation confusion
            negation_issues = self._detect_negation_issues(sentences)
            issues.extend(negation_issues)
            
            # Check for temporal inconsistencies
            temporal_issues = self._detect_temporal_inconsistencies(sentences)
            issues.extend(temporal_issues)
            
            # Calculate enhanced score
            score = self._calculate_basic_score(issues, len(sentences))
            
            return {
                "score": round(score, 3),
                "issues": issues,
                "issue_count": len(issues),
                "version": self.version,
                "analysis_type": "enhanced_basic"
            }
            
        except BiologyError as e:
            # Ultimate fallback
            return {
                "score": 0.5,
                "issues": [{"type": "analysis_error", "error": str(e)}],
                "issue_count": 1,
                "version": self.version
            }
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text using multiple methods"""
        try:
            if self.spacy_model:
                # Use spaCy for better sentence segmentation
                doc = self.spacy_model(text)
                return [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
            else:
                # Fallback to regex-based sentence splitting
                sentences = re.split(r'[.!?]+', text)
                return [s.strip() for s in sentences if len(s.strip()) > 10]
        except BiologyError:
            # Ultimate fallback
            return [text]
    
    async def _detect_logical_contradictions(self, sentences: List[str]) -> List[LogicalRelation]:
        """Detect logical contradictions using NLI models"""
        try:
            relations = []
            
            # Compare each pair of sentences
            for i in range(len(sentences)):
                for j in range(i + 1, len(sentences)):
                    premise = sentences[i]
                    hypothesis = sentences[j]
                    
                    # Skip if sentences are too similar (likely not contradictory)
                    if self._are_sentences_too_similar(premise, hypothesis):
                        continue
                    
                    # Use NLI to determine relationship
                    relation = await self._analyze_nli_relationship(premise, hypothesis)
                    
                    if relation:
                        relations.append(relation)
                    
                    # Limit number of comparisons for performance
                    if len(relations) >= 10:
                        break
                
                if len(relations) >= 10:
                    break
            
            return relations
            
        except BiologyError as e:
            return []
    
    async def _analyze_nli_relationship(self, premise: str, hypothesis: str) -> Optional[LogicalRelation]:
        """Analyze Natural Language Inference relationship between two sentences"""
        try:
            if not self.nli_pipeline:
                # Fallback to pattern-based analysis
                return self._pattern_based_nli(premise, hypothesis)
            
            # Use NLI model
            if hasattr(self.nli_pipeline, '__call__'):
                # Try different NLI formats
                try:
                    # Format for MNLI models
                    input_text = f"{premise} [SEP] {hypothesis}"
                    result = self.nli_pipeline(input_text)
                    
                    if isinstance(result, list) and len(result) > 0:
                        result = result[0]
                    
                    label = result.get('label', 'NEUTRAL').upper()
                    confidence = result.get('score', 0.5)
                    
                    # Map labels to our format
                    if 'CONTRADICT' in label or 'CONFLICT' in label:
                        relation_type = "contradiction"
                    elif 'ENTAIL' in label or 'SUPPORT' in label:
                        relation_type = "entailment"
                    else:
                        relation_type = "neutral"
                    
                    return LogicalRelation(
                        premise=premise,
                        hypothesis=hypothesis,
                        relation=relation_type,
                        confidence=confidence,
                        reasoning=f"NLI model prediction: {label}"
                    )
                    
                except BiologyError:
                    # Fallback to pattern-based analysis
                    return self._pattern_based_nli(premise, hypothesis)
            
            return None
            
        except BiologyError:
            return self._pattern_based_nli(premise, hypothesis)
    
    def _pattern_based_nli(self, premise: str, hypothesis: str) -> Optional[LogicalRelation]:
        """Pattern-based NLI analysis as fallback"""
        try:
            premise_lower = premise.lower()
            hypothesis_lower = hypothesis.lower()
            
            # Check for explicit contradictions
            for pattern_a, pattern_b in self.contradiction_patterns:
                if (re.search(pattern_a, premise_lower) and re.search(pattern_b, hypothesis_lower)) or \
                   (re.search(pattern_b, premise_lower) and re.search(pattern_a, hypothesis_lower)):
                    return LogicalRelation(
                        premise=premise,
                        hypothesis=hypothesis,
                        relation="contradiction",
                        confidence=0.7,
                        reasoning=f"Pattern-based contradiction: {pattern_a} vs {pattern_b}"
                    )
            
            # Check for semantic similarity (potential entailment)
            if self.sentence_transformer:
                try:
                    embeddings = self.sentence_transformer.encode([premise, hypothesis])
                    similarity = np.dot(embeddings[0], embeddings[1]) / (
                        np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                    )
                    
                    if similarity > 0.8:
                        return LogicalRelation(
                            premise=premise,
                            hypothesis=hypothesis,
                            relation="entailment",
                            confidence=float(similarity),
                            reasoning="High semantic similarity suggests entailment"
                        )
                except BiologyError:
                    pass
            
            return LogicalRelation(
                premise=premise,
                hypothesis=hypothesis,
                relation="neutral",
                confidence=0.5,
                reasoning="No clear logical relationship detected"
            )
            
        except BiologyError:
            return None
    
    def _are_sentences_too_similar(self, sent1: str, sent2: str) -> bool:
        """Check if sentences are too similar to be meaningfully compared"""
        # Simple word overlap check
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return True
        
        overlap = len(words1.intersection(words2))
        min_length = min(len(words1), len(words2))
        
        return overlap / min_length > 0.8
    
    async def _analyze_semantic_gaps(self, sentences: List[str], required_terms: Optional[List[str]]) -> List[SemanticGap]:
        """Analyze semantic gaps and missing concepts"""
        try:
            gaps = []
            
            # If we have required terms, check for missing concepts
            if required_terms:
                text_combined = " ".join(sentences).lower()
                
                for term in required_terms:
                    if term.lower() not in text_combined:
                        # Try to find related concepts
                        related_concepts = self._find_related_concepts(term, sentences)
                        
                        gap = SemanticGap(
                            missing_concept=term,
                            context=f"Term '{term}' not found in text",
                            importance=0.8,
                            suggestions=[f"Consider including discussion of {term}"],
                            related_concepts=related_concepts
                        )
                        gaps.append(gap)
            
            # Topic modeling to identify potential gaps
            if len(sentences) >= 5 and SKLEARN_AVAILABLE:
                try:
                    # Create document-term matrix
                    tfidf_matrix = self.tfidf_vectorizer.fit_transform(sentences)
                    
                    # Simple topic modeling
                    n_topics = min(5, len(sentences) // 2)
                    if n_topics >= 2:
                        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
                        doc_topic_matrix = lda.fit_transform(tfidf_matrix)
                        
                        # Identify sentences with low topic coherence
                        for i, topic_dist in enumerate(doc_topic_matrix):
                            max_topic_prob = np.max(topic_dist)
                            if max_topic_prob < 0.3:  # Low coherence
                                gap = SemanticGap(
                                    missing_concept="topic_coherence",
                                    context=sentences[i],
                                    importance=0.6,
                                    suggestions=["Consider improving topical coherence of this statement"],
                                    related_concepts=[]
                                )
                                gaps.append(gap)
                
                except BiologyError:
                    pass
            
            return gaps
            
        except BiologyError:
            return []
    
    def _find_related_concepts(self, term: str, sentences: List[str]) -> List[str]:
        """Find concepts related to a missing term"""
        try:
            related = []
            term_words = set(term.lower().split())
            
            for sentence in sentences:
                sentence_words = set(sentence.lower().split())
                
                # Look for partial matches or related words
                overlap = term_words.intersection(sentence_words)
                if overlap:
                    # Extract nearby words as potential related concepts
                    words = sentence.split()
                    for word in overlap:
                        try:
                            word_idx = [w.lower() for w in words].index(word)
                            # Get surrounding words
                            start = max(0, word_idx - 2)
                            end = min(len(words), word_idx + 3)
                            context_words = words[start:end]
                            related.extend(context_words)
                        except ValueError:
                            continue
            
            # Remove duplicates and the original term
            related = list(set(related))
            related = [w for w in related if w.lower() not in term.lower()]
            
            return related[:5]  # Return top 5 related concepts
            
        except BiologyError:
            return []
    
    async def _analyze_coherence(self, sentences: List[str]) -> Dict[str, float]:
        """Analyze text coherence using various metrics"""
        try:
            metrics = {}
            
            # Lexical coherence (word overlap between adjacent sentences)
            if len(sentences) > 1:
                overlaps = []
                for i in range(len(sentences) - 1):
                    words1 = set(sentences[i].lower().split())
                    words2 = set(sentences[i + 1].lower().split())
                    
                    if len(words1) > 0 and len(words2) > 0:
                        overlap = len(words1.intersection(words2))
                        union = len(words1.union(words2))
                        overlaps.append(overlap / union if union > 0 else 0)
                
                metrics['lexical_coherence'] = np.mean(overlaps) if overlaps else 0.0
            else:
                metrics['lexical_coherence'] = 1.0
            
            # Semantic coherence (if sentence transformer available)
            if self.sentence_transformer and len(sentences) > 1:
                try:
                    embeddings = self.sentence_transformer.encode(sentences)
                    similarities = []
                    
                    for i in range(len(embeddings) - 1):
                        sim = np.dot(embeddings[i], embeddings[i + 1]) / (
                            np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1])
                        )
                        similarities.append(sim)
                    
                    metrics['semantic_coherence'] = float(np.mean(similarities))
                except BiologyError:
                    metrics['semantic_coherence'] = 0.5
            else:
                metrics['semantic_coherence'] = 0.5
            
            # Syntactic diversity
            if self.spacy_model:
                try:
                    pos_patterns = []
                    for sentence in sentences[:10]:  # Limit for performance
                        doc = self.spacy_model(sentence)
                        pos_pattern = [token.pos_ for token in doc]
                        pos_patterns.append(tuple(pos_pattern))
                    
                    unique_patterns = len(set(pos_patterns))
                    metrics['syntactic_diversity'] = unique_patterns / len(pos_patterns) if pos_patterns else 0
                except BiologyError:
                    metrics['syntactic_diversity'] = 0.5
            else:
                metrics['syntactic_diversity'] = 0.5
            
            return metrics
            
        except BiologyError:
            return {'lexical_coherence': 0.5, 'semantic_coherence': 0.5, 'syntactic_diversity': 0.5}
    
    async def _analyze_argument_structure(self, sentences: List[str]) -> List[InconsistencyIssue]:
        """Analyze argument structure for logical consistency"""
        try:
            issues = []
            
            # Look for argument indicators
            claim_indicators = ['claim', 'argue', 'assert', 'maintain', 'propose']
            evidence_indicators = ['evidence', 'data', 'study', 'research', 'shows', 'demonstrates']
            conclusion_indicators = ['therefore', 'thus', 'consequently', 'in conclusion', 'hence']
            
            claim_sentences = []
            evidence_sentences = []
            conclusion_sentences = []
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                
                if any(indicator in sentence_lower for indicator in claim_indicators):
                    claim_sentences.append(sentence)
                elif any(indicator in sentence_lower for indicator in evidence_indicators):
                    evidence_sentences.append(sentence)
                elif any(indicator in sentence_lower for indicator in conclusion_indicators):
                    conclusion_sentences.append(sentence)
            
            # Check for argument structure issues
            if len(claim_sentences) > 0 and len(evidence_sentences) == 0:
                issue = InconsistencyIssue(
                    issue_type="weak_argument_structure",
                    severity="minor",
                    description="Claims made without supporting evidence",
                    confidence=0.7,
                    source_text=claim_sentences[0],
                    suggestion="Provide evidence to support claims"
                )
                issues.append(issue)
            
            if len(conclusion_sentences) > 0 and len(evidence_sentences) == 0:
                issue = InconsistencyIssue(
                    issue_type="unsupported_conclusion",
                    severity="major",
                    description="Conclusions drawn without evidence",
                    confidence=0.8,
                    source_text=conclusion_sentences[0],
                    suggestion="Provide evidence before drawing conclusions"
                )
                issues.append(issue)
            
            return issues
            
        except BiologyError:
            return []
    
    def _check_missing_terms(self, text: str, required_terms: List[str]) -> List[str]:
        """Check for missing required terms"""
        text_lower = text.lower()
        missing = []
        
        for term in required_terms:
            if term.lower() not in text_lower:
                missing.append(term)
        
        return missing
    
    def _detect_negation_issues(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """Detect potential negation-related inconsistencies"""
        issues = []
        
        # Look for double negatives or confusing negations
        for sentence in sentences:
            # Count negation words
            negation_words = ['not', 'no', 'never', 'none', 'nothing', 'nowhere', 'nobody']
            negation_count = sum(1 for word in negation_words if word in sentence.lower())
            
            if negation_count >= 2:
                issues.append({
                    "type": "complex_negation",
                    "sentence": sentence,
                    "negation_count": negation_count,
                    "severity": "minor"
                })
        
        return issues
    
    def _detect_temporal_inconsistencies(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """Detect temporal inconsistencies"""
        issues = []
        
        # Look for conflicting temporal expressions
        temporal_patterns = {
            'past': ['was', 'were', 'had', 'did', 'before', 'previously', 'earlier'],
            'present': ['is', 'are', 'has', 'does', 'now', 'currently', 'today'],
            'future': ['will', 'shall', 'going to', 'later', 'tomorrow', 'next']
        }
        
        sentence_tenses = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            tense_scores = {}
            
            for tense, patterns in temporal_patterns.items():
                score = sum(1 for pattern in patterns if pattern in sentence_lower)
                tense_scores[tense] = score
            
            dominant_tense = max(tense_scores, key=tense_scores.get)
            sentence_tenses.append((sentence, dominant_tense, tense_scores[dominant_tense]))
        
        # Check for abrupt tense changes without clear reason
        for i in range(len(sentence_tenses) - 1):
            current_tense = sentence_tenses[i][1]
            next_tense = sentence_tenses[i + 1][1]
            
            if current_tense != next_tense and sentence_tenses[i][2] > 0 and sentence_tenses[i + 1][2] > 0:
                # Check if there's a clear temporal transition
                transition_words = ['then', 'later', 'previously', 'now', 'currently']
                has_transition = any(word in sentence_tenses[i + 1][0].lower() for word in transition_words)
                
                if not has_transition:
                    issues.append({
                        "type": "temporal_inconsistency",
                        "current_sentence": sentence_tenses[i][0],
                        "next_sentence": sentence_tenses[i + 1][0],
                        "tense_change": f"{current_tense} -> {next_tense}",
                        "severity": "minor"
                    })
        
        return issues
    
    def _calculate_basic_score(self, issues: List[Dict[str, Any]], sentence_count: int) -> float:
        """Calculate basic consistency score"""
        if sentence_count == 0:
            return 0.0
        
        # Weight issues by severity
        penalty = 0.0
        for issue in issues:
            severity = issue.get('severity', 'minor')
            if severity == 'critical':
                penalty += 0.3
            elif severity == 'major':
                penalty += 0.2
            else:  # minor
                penalty += 0.1
        
        # Normalize by sentence count
        penalty = penalty / max(1, sentence_count / 5)
        
        return max(0.0, 1.0 - penalty)
    
    def _calculate_overall_score(
        self, 
        issues: List[InconsistencyIssue], 
        relations: List[LogicalRelation], 
        gaps: List[SemanticGap],
        coherence_metrics: Dict[str, float]
    ) -> float:
        """Calculate comprehensive consistency score"""
        try:
            # Base score from coherence metrics
            base_score = np.mean(list(coherence_metrics.values())) if coherence_metrics else 0.5
            
            # Penalty for issues
            issue_penalty = 0.0
            for issue in issues:
                if issue.severity == "critical":
                    issue_penalty += 0.3 * issue.confidence
                elif issue.severity == "major":
                    issue_penalty += 0.2 * issue.confidence
                else:  # minor
                    issue_penalty += 0.1 * issue.confidence
            
            # Penalty for contradictions
            contradiction_penalty = 0.0
            for relation in relations:
                if relation.relation == "contradiction":
                    contradiction_penalty += 0.25 * relation.confidence
            
            # Penalty for semantic gaps
            gap_penalty = min(0.2, len(gaps) * 0.05)
            
            # Calculate final score
            final_score = base_score - issue_penalty - contradiction_penalty - gap_penalty
            
            return max(0.0, min(1.0, final_score))
            
        except BiologyError:
            return 0.5
    
    def _generate_recommendations(
        self, 
        issues: List[InconsistencyIssue], 
        gaps: List[SemanticGap],
        coherence_metrics: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations for improving consistency"""
        recommendations = []
        
        # Recommendations based on issues
        critical_issues = [i for i in issues if i.severity == "critical"]
        if critical_issues:
            recommendations.append("🚨 Address critical logical contradictions immediately")
        
        major_issues = [i for i in issues if i.severity == "major"]
        if major_issues:
            recommendations.append("⚠️ Resolve major inconsistencies in argument structure")
        
        # Recommendations based on coherence
        if coherence_metrics.get('lexical_coherence', 0.5) < 0.3:
            recommendations.append("📝 Improve lexical coherence between sentences")
        
        if coherence_metrics.get('semantic_coherence', 0.5) < 0.3:
            recommendations.append("🔗 Enhance semantic connections between ideas")
        
        # Recommendations based on gaps
        if len(gaps) > 3:
            recommendations.append("🔍 Address semantic gaps and missing concepts")
        
        # Generic recommendations
        if len(recommendations) == 0:
            recommendations.append("✅ Text shows good consistency overall")
        
        return recommendations
    
    def _calculate_text_statistics(self, text: str, sentences: List[str]) -> Dict[str, Any]:
        """Calculate text statistics"""
        try:
            words = text.split()
            
            return {
                "character_count": len(text),
                "word_count": len(words),
                "sentence_count": len(sentences),
                "average_sentence_length": len(words) / len(sentences) if sentences else 0,
                "average_word_length": np.mean([len(word) for word in words]) if words else 0,
                "unique_word_ratio": len(set(words)) / len(words) if words else 0
            }
        except BiologyError:
            return {"error": "Failed to calculate statistics"}
    
    async def _fallback_check(self, text: str, required_terms: Optional[List[str]]) -> ConsistencyReport:
        """Fallback consistency check when advanced methods fail"""
        try:
            # Use basic check method
            basic_result = self.check(text, required_terms)
            
            # Convert to ConsistencyReport format
            issues = []
            for issue_dict in basic_result.get('issues', []):
                issue = InconsistencyIssue(
                    issue_type=issue_dict.get('type', 'unknown'),
                    severity=issue_dict.get('severity', 'minor'),
                    description=str(issue_dict),
                    confidence=0.5,
                    source_text=text
                )
                issues.append(issue)
            
            return ConsistencyReport(
                overall_score=basic_result.get('score', 0.5),
                inconsistency_issues=issues,
                logical_relations=[],
                semantic_gaps=[],
                coherence_metrics={},
                text_statistics={"analysis_type": "fallback"},
                recommendations=["Analysis completed with basic methods due to errors"]
            )
            
        except BiologyError:
            return ConsistencyReport(
                overall_score=0.0,
                inconsistency_issues=[],
                logical_relations=[],
                semantic_gaps=[],
                coherence_metrics={},
                text_statistics={},
                recommendations=["Analysis failed - please check input text"]
            )

# Create service instance
advanced_consistency_checker_service = AdvancedConsistencyCheckerService()
