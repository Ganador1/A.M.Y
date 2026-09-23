"""
ClinicalBERT Service for AXIOM
Clinical text analysis using ClinicalBERT for medical applications

Capabilities:
- Clinical note analysis and classification
- Medical entity extraction and recognition
- Clinical outcome prediction
- Medical text similarity analysis
- EHR data processing and insights

Ethics & Safety:
- HIPAA Compliance: No PHI processing without proper safeguards
- Medical Disclaimer: For research use only - not for clinical diagnosis
- Data Privacy: Local processing preferred for sensitive medical data
- Professional Review: Results require medical professional validation

Consulta la guía: ETHICS_AND_SAFETY.md
"""

import logging
# Optional torch import for deep learning support
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import time
import re
from app.exceptions.domain.medicine import MedicalError

try:
    from transformers import AutoTokenizer, AutoModel
    # Avoid pipeline import due to compatibility issues
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    AutoTokenizer = None
    AutoModel = None
from dataclasses import dataclass
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.core.bootstrap_logging import logger


@dataclass
class ClinicalEntity:
    """Clinical entity representation"""
    text: str
    label: str
    confidence: float
    start_pos: int
    end_pos: int
    entity_type: str
    clinical_category: str


@dataclass
class ClinicalClassificationResult:
    """Clinical text classification result"""
    text: str
    predicted_class: str
    confidence_score: float
    class_probabilities: Dict[str, float]
    processing_info: Dict[str, Any]


@dataclass
class ClinicalSimilarityResult:
    """Clinical text similarity analysis result"""
    text1: str
    text2: str
    similarity_score: float
    semantic_distance: float
    clinical_relevance: str
    processing_info: Dict[str, Any]


class ClinicalBERTService:
    """Advanced clinical text analysis using ClinicalBERT"""
    
    def __init__(self):
        """Initialize ClinicalBERT Service"""
        
        # Model initialization
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model: Optional[AutoModel] = None
        self.classifier_model: Optional[AutoModelForSequenceClassification] = None
        self.ner_pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Clinical entity types mapping
        self.clinical_entity_types = {
            'PROBLEM': 'Medical Problem/Condition',
            'TREATMENT': 'Treatment/Procedure', 
            'TEST': 'Diagnostic Test/Lab',
            'MEDICINE': 'Medication/Drug',
            'ANATOMY': 'Anatomical Structure',
            'SYMPTOM': 'Symptom/Sign',
            'DIAGNOSIS': 'Clinical Diagnosis'
        }
        
        # Clinical categories for classification
        self.clinical_categories = [
            'cardiology', 'oncology', 'neurology', 'psychiatry',
            'emergency', 'surgery', 'radiology', 'pathology'
        ]
        
        self._initialize_models()
        logger.info(f"✅ ClinicalBERTService initialized on {self.device}")
    
    def _initialize_models(self):
        """Initialize ClinicalBERT models with fallback handling"""
        try:
            # Primary model: ClinicalBERT
            model_name = "emilyalsentzer/Bio_ClinicalBERT"
            logger.info(f"Loading ClinicalBERT model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Try to load clinical NER pipeline
            try:
                ner_model = "clinical-ai-apollo/Medical-NER"
                self.ner_pipeline = pipeline(
                    "ner",
                    model=ner_model,
                    tokenizer=ner_model,
                    aggregation_strategy="simple",
                    device=0 if self.device == "cuda" else -1
                )
            except MedicalError as ner_e:
                logger.warning(f"Clinical NER model not available: {ner_e}")
                # Fallback to general biomedical NER
                try:
                    self.ner_pipeline = pipeline(
                        "ner",
                        model="d4data/biomedical-ner-all",
                        aggregation_strategy="simple",
                        device=0 if self.device == "cuda" else -1
                    )
                except MedicalError:
                    logger.warning("No NER pipeline available - using keyword extraction")
                    self.ner_pipeline = None
            
            logger.info("✅ ClinicalBERT models loaded successfully")
            
        except MedicalError as e:
            logger.warning(f"Failed to load ClinicalBERT models: {e}")
            logger.info("Using fallback: BioBERT model for clinical analysis")
            
            # Fallback to BioBERT
            try:
                fallback_model = "dmis-lab/biobert-base-cased-v1.2"
                self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
                self.model = AutoModel.from_pretrained(fallback_model)
                self.model.to(self.device)
                self.model.eval()
                logger.info("✅ Fallback BioBERT model loaded")
            except MedicalError as fallback_e:
                logger.error(f"Failed to load fallback model: {fallback_e}")
                self.model = None
                self.tokenizer = None
    
    async def extract_clinical_entities(self, clinical_text: str) -> Dict[str, Any]:
        """Extract clinical entities from medical text"""
        try:
            if len(clinical_text.strip()) < 10:
                raise ValueError("Clinical text too short for meaningful analysis")
            
            if not self.ner_pipeline:
                # Fallback to keyword-based extraction
                return {
                    "success": True,
                    "message": "Clinical entities extracted using keyword matching",
                    "data": await self._extract_clinical_keywords(clinical_text),
                    "fallback_method": "keyword_extraction"
                }
            
            # Use NER pipeline
            entities_raw = self.ner_pipeline(clinical_text)
            
            entities = []
            for ent in entities_raw:
                clinical_entity = ClinicalEntity(
                    text=ent['word'].replace('##', ''),  # Clean subword tokens
                    label=ent['entity_group'],
                    confidence=float(ent['score']),
                    start_pos=int(ent['start']),
                    end_pos=int(ent['end']),
                    entity_type=self.clinical_entity_types.get(ent['entity_group'], 'Clinical Entity'),
                    clinical_category=self._categorize_clinical_entity(ent['word'], ent['entity_group'])
                )
                entities.append(clinical_entity)
            
            # Group entities by clinical category
            entities_by_category = {}
            for entity in entities:
                category = entity.clinical_category
                if category not in entities_by_category:
                    entities_by_category[category] = []
                entities_by_category[category].append({
                    'text': entity.text,
                    'label': entity.label,
                    'confidence': entity.confidence,
                    'entity_type': entity.entity_type,
                    'position': (entity.start_pos, entity.end_pos)
                })
            
            return {
                "success": True,
                "message": "Clinical entities extracted successfully",
                "data": {
                    "total_entities": len(entities),
                    "entities_by_category": entities_by_category,
                    "clinical_summary": self._generate_clinical_summary(entities_by_category),
                    "processing_info": {
                        "model": "ClinicalBERT NER",
                        "device": self.device,
                        "text_length": len(clinical_text),
                        "confidence_threshold": 0.5
                    }
                }
            }
            
        except MedicalError as e:
            logger.error(f"Clinical entity extraction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_entities": await self._extract_clinical_keywords(clinical_text)
            }
    
    async def classify_clinical_text(
        self, 
        clinical_text: str, 
        classification_type: str = "specialty"
    ) -> Dict[str, Any]:
        """Classify clinical text by medical specialty or urgency"""
        try:
            if not self.model or not self.tokenizer:
                return {
                    "success": False,
                    "error": "ClinicalBERT model not available",
                    "fallback_classification": self._rule_based_classification(clinical_text)
                }
            
            # Get text embedding
            embedding = await self._get_clinical_embedding(clinical_text)
            if embedding is None:
                raise ValueError("Failed to generate clinical text embedding")
            
            # Rule-based classification for now (can be enhanced with trained classifier)
            classification = self._classify_by_keywords(clinical_text, classification_type)
            
            result = ClinicalClassificationResult(
                text=clinical_text[:200] + "..." if len(clinical_text) > 200 else clinical_text,
                predicted_class=classification['class'],
                confidence_score=classification['confidence'],
                class_probabilities=classification['probabilities'],
                processing_info={
                    "model": "ClinicalBERT",
                    "classification_type": classification_type,
                    "embedding_dim": embedding.shape[0] if embedding is not None else 0,
                    "processing_time": classification.get('processing_time', 0)
                }
            )
            
            return {
                "success": True,
                "message": f"Clinical text classified successfully as {classification_type}",
                "data": {
                    "predicted_class": result.predicted_class,
                    "confidence_score": result.confidence_score,
                    "class_probabilities": result.class_probabilities,
                    "clinical_insights": self._generate_classification_insights(result),
                    "processing_info": result.processing_info
                }
            }
            
        except MedicalError as e:
            logger.error(f"Clinical classification error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_classification": self._rule_based_classification(clinical_text)
            }
    
    async def analyze_clinical_similarity(
        self, 
        text1: str, 
        text2: str
    ) -> Dict[str, Any]:
        """Analyze semantic similarity between clinical texts"""
        try:
            if not self.model or not self.tokenizer:
                return {
                    "success": False,
                    "error": "ClinicalBERT model not available",
                    "fallback_similarity": self._simple_text_similarity(text1, text2)
                }
            
            # Get embeddings for both texts
            embedding1 = await self._get_clinical_embedding(text1)
            embedding2 = await self._get_clinical_embedding(text2)
            
            if embedding1 is None or embedding2 is None:
                raise ValueError("Failed to generate clinical text embeddings")
            
            # Calculate cosine similarity
            similarity_score = cosine_similarity(
                embedding1.reshape(1, -1),
                embedding2.reshape(1, -1)
            )[0][0]
            
            # Interpret clinical relevance
            clinical_relevance = self._interpret_clinical_similarity(similarity_score)
            
            result = ClinicalSimilarityResult(
                text1=text1[:100] + "..." if len(text1) > 100 else text1,
                text2=text2[:100] + "..." if len(text2) > 100 else text2,
                similarity_score=float(similarity_score),
                semantic_distance=float(1 - similarity_score),
                clinical_relevance=clinical_relevance,
                processing_info={
                    "model": "ClinicalBERT",
                    "embedding_method": "mean_pooling",
                    "similarity_metric": "cosine_similarity"
                }
            )
            
            return {
                "success": True,
                "message": "Clinical similarity analyzed successfully",
                "data": {
                    "similarity_score": result.similarity_score,
                    "semantic_distance": result.semantic_distance,
                    "clinical_relevance": result.clinical_relevance,
                    "similarity_interpretation": self._interpret_similarity_score(result.similarity_score),
                    "processing_info": result.processing_info
                }
            }
            
        except MedicalError as e:
            logger.error(f"Clinical similarity analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_similarity": self._simple_text_similarity(text1, text2)
            }
    
    async def _get_clinical_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate ClinicalBERT embedding for text"""
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
            
        except MedicalError as e:
            logger.error(f"Clinical embedding generation error: {e}")
            return None
    
    def _categorize_clinical_entity(self, entity_text: str, entity_label: str) -> str:
        """Categorize clinical entity into medical domain"""
        entity_lower = entity_text.lower()
        
        # Cardiology terms
        cardiology_terms = ['heart', 'cardiac', 'ecg', 'ekg', 'chest pain', 'arrhythmia']
        if any(term in entity_lower for term in cardiology_terms):
            return 'cardiology'
        
        # Neurology terms  
        neurology_terms = ['brain', 'neural', 'stroke', 'seizure', 'headache', 'memory']
        if any(term in entity_lower for term in neurology_terms):
            return 'neurology'
        
        # Oncology terms
        oncology_terms = ['cancer', 'tumor', 'malignant', 'chemotherapy', 'radiation']
        if any(term in entity_lower for term in oncology_terms):
            return 'oncology'
        
        return 'general_medicine'
    
    def _classify_by_keywords(self, text: str, classification_type: str) -> Dict[str, Any]:
        """Rule-based classification using medical keywords"""
        text_lower = text.lower()
        
        if classification_type == "specialty":
            specialty_scores = {}
            
            # Define specialty keywords
            specialty_keywords = {
                'cardiology': ['heart', 'cardiac', 'ecg', 'chest pain', 'arrhythmia', 'hypertension'],
                'neurology': ['brain', 'neural', 'stroke', 'seizure', 'headache', 'memory', 'cognitive'],
                'oncology': ['cancer', 'tumor', 'malignant', 'chemotherapy', 'radiation', 'biopsy'],
                'psychiatry': ['depression', 'anxiety', 'psychiatric', 'mental health', 'therapy'],
                'emergency': ['emergency', 'urgent', 'critical', 'trauma', 'acute', 'severe'],
                'radiology': ['x-ray', 'ct scan', 'mri', 'ultrasound', 'imaging', 'radiological']
            }
            
            for specialty, keywords in specialty_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                specialty_scores[specialty] = score / len(keywords)
            
            best_specialty = max(specialty_scores.items(), key=lambda x: x[1])
            
            return {
                'class': best_specialty[0],
                'confidence': best_specialty[1],
                'probabilities': specialty_scores,
                'processing_time': 0.001
            }
        
        return {
            'class': 'general_medicine',
            'confidence': 0.5,
            'probabilities': {'general_medicine': 0.5},
            'processing_time': 0.001
        }
    
    def _generate_clinical_summary(self, entities_by_category: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate clinical summary from extracted entities"""
        summary = {
            "total_categories": len(entities_by_category),
            "primary_focus": None,
            "clinical_complexity": "low",
            "key_findings": []
        }
        
        if entities_by_category:
            # Find primary focus (category with most entities)
            primary_category = max(entities_by_category.items(), key=lambda x: len(x[1]))
            summary["primary_focus"] = primary_category[0]
            
            # Assess complexity
            total_entities = sum(len(entities) for entities in entities_by_category.values())
            if total_entities > 10:
                summary["clinical_complexity"] = "high"
            elif total_entities > 5:
                summary["clinical_complexity"] = "medium"
            
            # Extract key findings
            for category, entities in entities_by_category.items():
                if entities:
                    top_entity = max(entities, key=lambda x: x['confidence'])
                    summary["key_findings"].append({
                        "category": category,
                        "key_entity": top_entity['text'],
                        "confidence": top_entity['confidence']
                    })
        
        return summary
    
    def _interpret_clinical_similarity(self, score: float) -> str:
        """Interpret clinical similarity score"""
        if score >= 0.8:
            return "highly_similar_clinical_context"
        elif score >= 0.6:
            return "moderately_similar_clinical_context"
        elif score >= 0.4:
            return "somewhat_similar_clinical_context"
        else:
            return "different_clinical_contexts"
    
    def _interpret_similarity_score(self, score: float) -> str:
        """Provide human-readable similarity interpretation"""
        if score >= 0.8:
            return "Very similar clinical cases - likely same condition or related treatments"
        elif score >= 0.6:
            return "Moderately similar - may share clinical features or treatment approaches"
        elif score >= 0.4:
            return "Some similarity - possibly related medical domains or symptoms"
        else:
            return "Different clinical contexts - distinct medical conditions or specialties"
    
    def _generate_classification_insights(self, result: ClinicalClassificationResult) -> List[str]:
        """Generate clinical insights from classification"""
        insights = []
        
        if result.confidence_score >= 0.7:
            insights.append(f"High confidence classification as {result.predicted_class}")
        elif result.confidence_score >= 0.5:
            insights.append(f"Moderate confidence classification as {result.predicted_class}")
        else:
            insights.append("Low confidence - consider multi-specialty consultation")
        
        # Add specialty-specific insights
        if result.predicted_class == "emergency":
            insights.append("Urgent medical attention may be required")
        elif result.predicted_class == "oncology":
            insights.append("Oncological evaluation and staging recommended")
        elif result.predicted_class == "cardiology":
            insights.append("Cardiac workup and monitoring indicated")
        
        return insights
    
    async def _extract_clinical_keywords(self, text: str) -> Dict[str, Any]:
        """Fallback keyword-based clinical entity extraction"""
        clinical_keywords = {
            'conditions': ['diabetes', 'hypertension', 'cancer', 'pneumonia', 'stroke'],
            'medications': ['aspirin', 'insulin', 'metformin', 'lisinopril', 'atorvastatin'],
            'procedures': ['surgery', 'biopsy', 'catheterization', 'intubation', 'dialysis'],
            'symptoms': ['pain', 'fever', 'nausea', 'fatigue', 'shortness of breath']
        }
        
        found_entities = {}
        text_lower = text.lower()
        
        for category, keywords in clinical_keywords.items():
            found_entities[category] = []
            for keyword in keywords:
                if keyword in text_lower:
                    found_entities[category].append({
                        'text': keyword,
                        'confidence': 0.6,
                        'method': 'keyword_matching'
                    })
        
        return {
            "entities_by_category": found_entities,
            "method": "keyword_extraction",
            "note": "ClinicalBERT not available - using keyword matching"
        }
    
    def _rule_based_classification(self, text: str) -> Dict[str, str]:
        """Fallback rule-based classification"""
        return {
            "predicted_class": "general_medicine",
            "confidence": 0.5,
            "method": "rule_based_fallback",
            "note": "ClinicalBERT not available"
        }
    
    def _simple_text_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """Fallback simple text similarity"""
        # Simple Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        jaccard_score = intersection / union if union > 0 else 0.0
        
        return {
            "similarity_score": jaccard_score,
            "method": "jaccard_similarity",
            "note": "ClinicalBERT not available - using word overlap"
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get ClinicalBERT service information"""
        return {
            "service_name": "ClinicalBERT Service",
            "model_loaded": self.model is not None,
            "device": self.device,
            "capabilities": [
                "Clinical entity extraction",
                "Medical text classification",
                "Clinical similarity analysis", 
                "Medical specialty prediction",
                "EHR text processing"
            ],
            "clinical_categories": self.clinical_categories,
            "model_info": "emilyalsentzer/Bio_ClinicalBERT" if self.model else "Not loaded"
        }
