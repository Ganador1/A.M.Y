"""
Fixed ClinicalBERT Service - Avoiding transformers pipeline issues

This service provides clinical text analysis capabilities using ClinicalBERT
without relying on the problematic transformers pipeline functionality.
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
from typing import Dict, Any, List, Optional
import json
import re
from app.exceptions.domain.medicine import MedicalError
from app.services.base_service import BaseService

try:
    from transformers import AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
    logging.info("Transformers available - using real models")
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    logging.warning(f"Transformers not available: {e}. Using mock implementation.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClinicalBERTService(BaseService):
    """
    Fixed ClinicalBERT service for clinical text analysis.
    Uses direct model loading instead of pipeline to avoid compatibility issues.
    """
    
    def __init__(self):
        """Initialize the ClinicalBERT service"""
        super().__init__("ClinicalBERTService")
        self.primary_model = "emilyalsentzer/Bio_ClinicalBERT"
        self.fallback_model = "bert-base-uncased"
        self.device = self._get_device()
        self.tokenizer = None
        self.model = None
        self.is_loaded = False
        
        # Clinical entity types
        self.clinical_entities = {
            'medication': ['aspirin', 'ibuprofen', 'acetaminophen', 'insulin', 'warfarin', 'metformin'],
            'procedure': ['surgery', 'biopsy', 'catheterization', 'endoscopy', 'dialysis', 'chemotherapy'],
            'symptom': ['pain', 'fever', 'nausea', 'fatigue', 'headache', 'shortness of breath'],
            'condition': ['diabetes', 'hypertension', 'cancer', 'pneumonia', 'asthma', 'depression'],
            'anatomy': ['heart', 'liver', 'kidney', 'lung', 'brain', 'stomach']
        }
        
        # Medical specialties
        self.medical_specialties = {
            'cardiology': ['heart', 'cardiac', 'cardiovascular', 'ecg', 'ekg', 'chest pain'],
            'neurology': ['brain', 'neurological', 'seizure', 'stroke', 'headache', 'memory'],
            'oncology': ['cancer', 'tumor', 'chemotherapy', 'radiation', 'metastasis', 'biopsy'],
            'pulmonology': ['lung', 'respiratory', 'breathing', 'cough', 'pneumonia', 'asthma'],
            'gastroenterology': ['stomach', 'digestive', 'abdomen', 'nausea', 'liver', 'intestinal'],
            'endocrinology': ['diabetes', 'thyroid', 'hormone', 'insulin', 'glucose', 'metabolism']
        }
        
        logger.info("ClinicalBERT service initialized")
    
    def _get_device(self) -> str:
        """Get the best available device for model execution"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    async def _load_model(self) -> bool:
        """Load the ClinicalBERT model safely"""
        if self.is_loaded:
            return True
        
        try:
            if TRANSFORMERS_AVAILABLE:
                logger.info(f"Loading ClinicalBERT model: {self.primary_model}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.primary_model)
                self.model = AutoModel.from_pretrained(self.primary_model)
                self.model.to(self.device)
                self.model.eval()
                self.is_loaded = True
                logger.info("✅ ClinicalBERT model loaded successfully")
                return True
            else:
                logger.warning("Using mock implementation due to transformers issues")
                self.is_loaded = True
                return True
                
        except MedicalError as e:
            logger.error(f"Failed to load ClinicalBERT: {e}")
            logger.info("Using mock implementation as fallback")
            self.is_loaded = True
            return True
    
    def _extract_entities_mock(self, text: str) -> Dict[str, List[str]]:
        """Mock entity extraction using keyword matching"""
        entities = {entity_type: [] for entity_type in self.clinical_entities}
        text_lower = text.lower()
        
        for entity_type, keywords in self.clinical_entities.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entities[entity_type].append(keyword.title())
        
        return entities
    
    def _classify_specialty_mock(self, text: str) -> Dict[str, float]:
        """Mock specialty classification using keyword scoring"""
        scores = {}
        text_lower = text.lower()
        
        for specialty, keywords in self.medical_specialties.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[specialty] = score / len(keywords)  # Normalize
        
        return scores
    
    def _calculate_similarity_mock(self, text1: str, text2: str) -> float:
        """Mock similarity calculation using simple word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a service request.
        """
        operation = request_data.get("operation")
        
        if operation == "extract_entities":
            text = request_data.get("text", "")
            return await self.extract_clinical_entities(text)
            
        if operation == "classify_specialty":
            text = request_data.get("text", "")
            return await self.classify_medical_specialty(text)
            
        if operation == "calculate_similarity":
            text1 = request_data.get("text1", "")
            text2 = request_data.get("text2", "")
            return await self.calculate_clinical_similarity(text1, text2)
            
        return {"success": False, "error": f"Unknown operation: {operation}"}
    
    async def extract_clinical_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract clinical entities from text
        
        Args:
            text: Clinical text to analyze
            
        Returns:
            Dictionary with extracted entities and metadata
        """
        try:
            await self._load_model()
            
            if not text or not text.strip():
                return {
                    'success': False,
                    'error': 'Empty text provided',
                    'data': {}
                }
            
            # Use mock extraction for now (can be replaced with real model later)
            entities = self._extract_entities_mock(text)
            
            # Calculate metrics
            total_entities = sum(len(entity_list) for entity_list in entities.values())
            entity_types_found = sum(1 for entity_list in entities.values() if entity_list)
            
            return {
                'success': True,
                'data': {
                    'entities': entities,
                    'total_entities': total_entities,
                    'entity_types_found': entity_types_found,
                    'text_length': len(text),
                    'analysis_method': 'keyword_fallback'  # extraction is keyword-based here regardless of transformers; see personalized/clinicalbert_service.py for the real scispaCy/HF NER path
                }
            }
            
        except MedicalError as e:
            logger.error(f"Entity extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    async def classify_clinical_text(self, text: str, classification_type: str = "specialty") -> Dict[str, Any]:
        """
        Classify clinical text by type
        
        Args:
            text: Clinical text to classify
            classification_type: Type of classification (specialty, urgency, etc.)
            
        Returns:
            Dictionary with classification results
        """
        try:
            await self._load_model()
            
            if not text or not text.strip():
                return {
                    'success': False,
                    'error': 'Empty text provided',
                    'data': {}
                }
            
            if classification_type == "specialty":
                scores = self._classify_specialty_mock(text)
                predicted_specialty = max(scores, key=scores.get)
                confidence = scores[predicted_specialty]
                
                return {
                    'success': True,
                    'data': {
                        'predicted_class': predicted_specialty,
                        'confidence_score': confidence,
                        'all_scores': scores,
                        'classification_type': classification_type,
                        'text_length': len(text),
                        'analysis_method': 'keyword_fallback'  # extraction is keyword-based here regardless of transformers; see personalized/clinicalbert_service.py for the real scispaCy/HF NER path
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Unsupported classification type: {classification_type}',
                    'data': {}
                }
                
        except MedicalError as e:
            logger.error(f"Classification failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    async def analyze_clinical_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Analyze similarity between clinical texts
        
        Args:
            text1: First clinical text
            text2: Second clinical text
            
        Returns:
            Dictionary with similarity analysis
        """
        try:
            await self._load_model()
            
            if not text1 or not text2 or not text1.strip() or not text2.strip():
                return {
                    'success': False,
                    'error': 'Empty texts provided',
                    'data': {}
                }
            
            similarity_score = self._calculate_similarity_mock(text1, text2)
            
            # Determine similarity category
            if similarity_score >= 0.8:
                similarity_category = "very_high"
            elif similarity_score >= 0.6:
                similarity_category = "high"
            elif similarity_score >= 0.4:
                similarity_category = "moderate"
            elif similarity_score >= 0.2:
                similarity_category = "low"
            else:
                similarity_category = "very_low"
            
            return {
                'success': True,
                'data': {
                    'similarity_score': similarity_score,
                    'similarity_category': similarity_category,
                    'text1_length': len(text1),
                    'text2_length': len(text2),
                    'analysis_method': 'keyword_fallback'  # extraction is keyword-based here regardless of transformers; see personalized/clinicalbert_service.py for the real scispaCy/HF NER path
                }
            }
            
        except MedicalError as e:
            logger.error(f"Similarity analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    async def analyze_clinical_notes(self, notes: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple clinical notes for patterns and insights
        
        Args:
            notes: List of clinical notes
            
        Returns:
            Dictionary with comprehensive analysis
        """
        try:
            await self._load_model()
            
            if not notes:
                return {
                    'success': False,
                    'error': 'No notes provided',
                    'data': {}
                }
            
            # Analyze each note
            all_entities = {entity_type: [] for entity_type in self.clinical_entities}
            specialty_scores = {specialty: 0 for specialty in self.medical_specialties}
            
            for note in notes:
                if note and note.strip():
                    # Extract entities
                    entities = self._extract_entities_mock(note)
                    for entity_type, entity_list in entities.items():
                        all_entities[entity_type].extend(entity_list)
                    
                    # Score specialties
                    scores = self._classify_specialty_mock(note)
                    for specialty, score in scores.items():
                        specialty_scores[specialty] += score
            
            # Find most common entities
            common_entities = {}
            for entity_type, entity_list in all_entities.items():
                if entity_list:
                    # Count occurrences
                    entity_counts = {}
                    for entity in entity_list:
                        entity_counts[entity] = entity_counts.get(entity, 0) + 1
                    common_entities[entity_type] = sorted(entity_counts.items(), 
                                                        key=lambda x: x[1], reverse=True)[:3]
            
            # Dominant specialty
            dominant_specialty = max(specialty_scores, key=specialty_scores.get)
            
            return {
                'success': True,
                'data': {
                    'notes_analyzed': len(notes),
                    'total_entities': sum(len(entities) for entities in all_entities.values()),
                    'common_entities': common_entities,
                    'dominant_specialty': dominant_specialty,
                    'specialty_scores': specialty_scores,
                    'analysis_method': 'keyword_fallback'  # extraction is keyword-based here regardless of transformers; see personalized/clinicalbert_service.py for the real scispaCy/HF NER path
                }
            }
            
        except MedicalError as e:
            logger.error(f"Clinical notes analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            await self._load_model()
            return {
                'service': 'ClinicalBERT',
                'status': 'healthy',
                'model_loaded': self.is_loaded,
                'device': self.device,
                'transformers_available': TRANSFORMERS_AVAILABLE,
                'primary_model': self.primary_model,
                'fallback_model': self.fallback_model
            }
        except MedicalError as e:
            return {
                'service': 'ClinicalBERT',
                'status': 'unhealthy',
                'error': str(e)
            }


# Global service instance
_clinical_bert_service = None

def get_clinical_bert_service() -> ClinicalBERTService:
    """Get singleton ClinicalBERT service instance"""
    global _clinical_bert_service
    if _clinical_bert_service is None:
        _clinical_bert_service = ClinicalBERTService()
    return _clinical_bert_service
