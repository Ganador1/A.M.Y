"""
ClinicalBERT Service for AXIOM — Real clinical text analysis using BioClinicalBERT,
scispaCy NER, and HuggingFace transformers.
"""

import logging
import os
from typing import Dict, Any, List, Optional
import json
import re
import asyncio

import numpy as np

# Optional torch import for deep learning support
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore

try:
    from transformers import AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
    logging.info("Transformers available - using real models")
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    logging.warning(f"Transformers not available: {e}. Using keyword fallback.")

# Optional scispaCy for real clinical NER
try:
    import spacy
    scispacy_models = []
    for model_name in ("en_ner_bc5cdr_md", "en_core_sci_scibert", "en_core_sci_sm"):
        try:
            spacy.load(model_name)
            scispacy_models.append(model_name)
        except Exception:
            pass
    HAS_SCISPACY = len(scispacy_models) > 0
    if HAS_SCISPACY:
        logging.info("scispaCy available with models: %s", scispacy_models)
except Exception:
    HAS_SCISPACY = False

# Optional HF pipeline for NER fallback
try:
    from transformers import pipeline
    HF_PIPELINE_AVAILABLE = True
except Exception:
    HF_PIPELINE_AVAILABLE = False

from app.exceptions.domain.medicine import MedicalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClinicalBERTService:
    """
    ClinicalBERT service for clinical text analysis using real models when available.
    """

    def __init__(self):
        self.primary_model = "emilyalsentzer/Bio_ClinicalBERT"
        self.fallback_model = "bert-base-uncased"
        self.device = self._get_device()
        self.tokenizer = None
        self.model = None
        self.is_loaded = False
        self._ner_pipeline = None
        self._scispacy_nlp = None
        self._specialty_embeddings: Optional[Dict[str, Any]] = None

        # Clinical entity keyword fallback
        self.clinical_entities = {
            'medication': ['aspirin', 'ibuprofen', 'acetaminophen', 'insulin', 'warfarin', 'metformin',
                           'atorvastatin', 'lisinopril', 'amlodipine', 'omeprazole'],
            'procedure': ['surgery', 'biopsy', 'catheterization', 'endoscopy', 'dialysis', 'chemotherapy',
                          'radiation', 'mri', 'ct scan', 'x-ray', 'ultrasound'],
            'symptom': ['pain', 'fever', 'nausea', 'fatigue', 'headache', 'shortness of breath',
                        'cough', 'dizziness', 'vomiting', 'diarrhea'],
            'condition': ['diabetes', 'hypertension', 'cancer', 'pneumonia', 'asthma', 'depression',
                          'arthritis', 'stroke', 'myocardial infarction', 'copd'],
            'anatomy': ['heart', 'liver', 'kidney', 'lung', 'brain', 'stomach',
                        'intestine', 'pancreas', 'spleen', 'colon']
        }

        # Medical specialty descriptions for zero-shot classification via embeddings
        self.medical_specialty_descriptions = {
            'cardiology': 'heart disease cardiac cardiovascular ECG chest pain myocardial infarction',
            'neurology': 'brain neurological seizure stroke headache memory dementia nervous system',
            'oncology': 'cancer tumor chemotherapy radiation metastasis biopsy malignancy oncology',
            'pulmonology': 'lung respiratory breathing cough pneumonia asthma copd bronchitis',
            'gastroenterology': 'stomach digestive abdomen nausea liver intestinal colon endoscopy',
            'endocrinology': 'diabetes thyroid hormone insulin glucose metabolism pituitary adrenal',
            'nephrology': 'kidney renal dialysis transplantation proteinuria chronic kidney disease',
            'hematology': 'blood anemia leukemia lymphoma coagulation transfusion bone marrow',
            'infectious_disease': 'infection bacteria virus antibiotic fever sepsis immunization hiv',
            'rheumatology': 'arthritis autoimmune lupus joint inflammation connective tissue vasculitis',
        }

        logger.info("ClinicalBERT service initialized")

    def _get_device(self) -> str:
        if not HAS_TORCH:
            return "cpu"
        if torch.cuda.is_available():
            return "cuda"
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    async def _load_model(self) -> bool:
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
                # Pre-compute specialty embeddings
                await asyncio.to_thread(self._precompute_specialty_embeddings)
            else:
                logger.warning("Transformers not available; using keyword fallback for all tasks.")
                self.is_loaded = True

            # Load scispaCy if available
            if HAS_SCISPACY and self._scispacy_nlp is None:
                for model_name in scispacy_models:
                    try:
                        self._scispacy_nlp = spacy.load(model_name)
                        logger.info("Loaded scispaCy model: %s", model_name)
                        break
                    except Exception:
                        pass

            # Load HF NER pipeline if available and scispaCy not loaded
            if HF_PIPELINE_AVAILABLE and self._ner_pipeline is None and self._scispacy_nlp is None:
                try:
                    self._ner_pipeline = pipeline(
                        "ner",
                        model="samrawal/bert-base-uncased_clinical-ner",
                        aggregation_strategy="simple",
                        device=0 if self.device != "cpu" else -1,
                    )
                    logger.info("Loaded HF clinical NER pipeline")
                except Exception as e:
                    logger.warning("Could not load HF clinical NER pipeline: %s", e)

            return True
        except Exception as e:
            logger.error(f"Failed to load ClinicalBERT: {e}")
            self.is_loaded = True
            return True

    def _precompute_specialty_embeddings(self):
        if not TRANSFORMERS_AVAILABLE or self.model is None or self.tokenizer is None:
            return
        self._specialty_embeddings = {}
        with torch.no_grad():
            for specialty, desc in self.medical_specialty_descriptions.items():
                inputs = self.tokenizer(desc, return_tensors="pt", truncation=True, max_length=128)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                outputs = self.model(**inputs)
                vec = outputs.last_hidden_state[:, 0, :].cpu().numpy().squeeze()
                self._specialty_embeddings[specialty] = vec / (np.linalg.norm(vec) + 1e-9)

    def _embed_text(self, text: str) -> Optional[np.ndarray]:
        if not TRANSFORMERS_AVAILABLE or self.model is None or self.tokenizer is None:
            return None
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            outputs = self.model(**inputs)
            vec = outputs.last_hidden_state[:, 0, :].cpu().numpy().squeeze()
            return vec / (np.linalg.norm(vec) + 1e-9)

    def _extract_entities_mock(self, text: str) -> Dict[str, List[str]]:
        entities = {entity_type: [] for entity_type in self.clinical_entities}
        text_lower = text.lower()
        for entity_type, keywords in self.clinical_entities.items():
            found = []
            for keyword in keywords:
                if keyword in text_lower:
                    found.append(keyword.title())
            entities[entity_type] = list(set(found))
        return entities

    def _extract_entities_scispacy(self, text: str) -> Dict[str, List[str]]:
        entities = {entity_type: [] for entity_type in self.clinical_entities}
        if self._scispacy_nlp is None:
            return entities
        doc = self._scispacy_nlp(text)
        # scispaCy labels: CHEMICAL, DISEASE, etc.
        label_map = {
            "CHEMICAL": "medication",
            "DISEASE": "condition",
            "SYMPTOM": "symptom",
        }
        for ent in doc.ents:
            mapped = label_map.get(ent.label_, None)
            if mapped:
                entities[mapped].append(ent.text)
        # Deduplicate
        for k in entities:
            entities[k] = list(set(entities[k]))
        return entities

    def _extract_entities_hf(self, text: str) -> Dict[str, List[str]]:
        entities = {entity_type: [] for entity_type in self.clinical_entities}
        if self._ner_pipeline is None:
            return entities
        try:
            results = self._ner_pipeline(text)
            label_map = {
                "B-problem": "condition",
                "I-problem": "condition",
                "B-treatment": "medication",
                "I-treatment": "medication",
                "B-test": "procedure",
                "I-test": "procedure",
            }
            for r in results:
                label = label_map.get(r.get("entity_group", r.get("entity")), None)
                if label:
                    entities[label].append(r.get("word", "").strip())
            for k in entities:
                entities[k] = list(set(entities[k]))
        except Exception as e:
            logger.warning("HF NER failed: %s", e)
        return entities

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        if self._scispacy_nlp is not None:
            return self._extract_entities_scispacy(text)
        if self._ner_pipeline is not None:
            return self._extract_entities_hf(text)
        return self._extract_entities_mock(text)

    async def extract_clinical_entities(self, text: str) -> Dict[str, Any]:
        try:
            await self._load_model()
            if not text or not text.strip():
                return {'success': False, 'error': 'Empty text provided', 'data': {}}

            entities = self._extract_entities(text)
            total_entities = sum(len(v) for v in entities.values())
            entity_types_found = sum(1 for v in entities.values() if v)

            method = 'scispaCy' if self._scispacy_nlp else ('hf_ner' if self._ner_pipeline else 'keyword_fallback')
            return {
                'success': True,
                'data': {
                    'entities': entities,
                    'total_entities': total_entities,
                    'entity_types_found': entity_types_found,
                    'text_length': len(text),
                    'analysis_method': method,
                }
            }
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {'success': False, 'error': str(e), 'data': {}}

    async def classify_clinical_text(self, text: str, classification_type: str = "specialty") -> Dict[str, Any]:
        try:
            await self._load_model()
            if not text or not text.strip():
                return {'success': False, 'error': 'Empty text provided', 'data': {}}

            if classification_type == "specialty":
                scores: Dict[str, float] = {}
                predicted_specialty = "general_medicine"
                confidence = 0.0

                if self._specialty_embeddings is not None:
                    text_vec = self._embed_text(text)
                    if text_vec is not None:
                        for specialty, spec_vec in self._specialty_embeddings.items():
                            sim = float(np.dot(text_vec, spec_vec))
                            scores[specialty] = max(0.0, sim)
                        if scores:
                            predicted_specialty = max(scores, key=scores.get)
                            confidence = scores[predicted_specialty]
                        method = 'clinicalbert_embeddings'
                    else:
                        method = 'keyword_fallback'
                        scores = self._classify_specialty_mock(text)
                        predicted_specialty = max(scores, key=scores.get)
                        confidence = scores[predicted_specialty]
                else:
                    method = 'keyword_fallback'
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
                        'analysis_method': method,
                    }
                }
            else:
                return {'success': False, 'error': f'Unsupported classification type: {classification_type}', 'data': {}}
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {'success': False, 'error': str(e), 'data': {}}

    def _classify_specialty_mock(self, text: str) -> Dict[str, float]:
        scores = {}
        text_lower = text.lower()
        for specialty, keywords in {
            'cardiology': ['heart', 'cardiac', 'cardiovascular', 'ecg', 'ekg', 'chest pain'],
            'neurology': ['brain', 'neurological', 'seizure', 'stroke', 'headache', 'memory'],
            'oncology': ['cancer', 'tumor', 'chemotherapy', 'radiation', 'metastasis', 'biopsy'],
            'pulmonology': ['lung', 'respiratory', 'breathing', 'cough', 'pneumonia', 'asthma'],
            'gastroenterology': ['stomach', 'digestive', 'abdomen', 'nausea', 'liver', 'intestinal'],
            'endocrinology': ['diabetes', 'thyroid', 'hormone', 'insulin', 'glucose', 'metabolism']
        }.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[specialty] = score / len(keywords)
        return scores

    async def analyze_clinical_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        try:
            await self._load_model()
            if not text1 or not text2 or not text1.strip() or not text2.strip():
                return {'success': False, 'error': 'Empty texts provided', 'data': {}}

            if self.model is not None and self.tokenizer is not None:
                vec1 = self._embed_text(text1)
                vec2 = self._embed_text(text2)
                if vec1 is not None and vec2 is not None:
                    similarity_score = float(np.dot(vec1, vec2))
                    method = 'clinicalbert_embeddings'
                else:
                    similarity_score = self._calculate_similarity_mock(text1, text2)
                    method = 'keyword_fallback'
            else:
                similarity_score = self._calculate_similarity_mock(text1, text2)
                method = 'keyword_fallback'

            if similarity_score >= 0.8:
                category = "very_high"
            elif similarity_score >= 0.6:
                category = "high"
            elif similarity_score >= 0.4:
                category = "moderate"
            elif similarity_score >= 0.2:
                category = "low"
            else:
                category = "very_low"

            return {
                'success': True,
                'data': {
                    'similarity_score': similarity_score,
                    'similarity_category': category,
                    'text1_length': len(text1),
                    'text2_length': len(text2),
                    'analysis_method': method,
                }
            }
        except Exception as e:
            logger.error(f"Similarity analysis failed: {e}")
            return {'success': False, 'error': str(e), 'data': {}}

    def _calculate_similarity_mock(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0

    async def analyze_clinical_notes(self, notes: List[str]) -> Dict[str, Any]:
        try:
            await self._load_model()
            if not notes:
                return {'success': False, 'error': 'No notes provided', 'data': {}}

            all_entities = {entity_type: [] for entity_type in self.clinical_entities}
            specialty_scores: Dict[str, float] = {specialty: 0.0 for specialty in self.medical_specialty_descriptions}

            for note in notes:
                if note and note.strip():
                    entities = self._extract_entities(note)
                    for entity_type, entity_list in entities.items():
                        all_entities[entity_type].extend(entity_list)

                    # Specialty scoring
                    spec_result = await self.classify_clinical_text(note, classification_type="specialty")
                    if spec_result.get("success"):
                        for specialty, score in spec_result["data"]["all_scores"].items():
                            if specialty in specialty_scores:
                                specialty_scores[specialty] += float(score)

            # Most common entities
            common_entities = {}
            for entity_type, entity_list in all_entities.items():
                if entity_list:
                    counts = {}
                    for entity in entity_list:
                        counts[entity] = counts.get(entity, 0) + 1
                    common_entities[entity_type] = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]

            dominant_specialty = max(specialty_scores, key=specialty_scores.get) if specialty_scores else "general_medicine"
            method = 'scispaCy' if self._scispacy_nlp else ('hf_ner' if self._ner_pipeline else 'keyword_fallback')

            return {
                'success': True,
                'data': {
                    'notes_analyzed': len(notes),
                    'total_entities': sum(len(v) for v in all_entities.values()),
                    'common_entities': common_entities,
                    'dominant_specialty': dominant_specialty,
                    'specialty_scores': specialty_scores,
                    'analysis_method': method,
                }
            }
        except Exception as e:
            logger.error(f"Clinical notes analysis failed: {e}")
            return {'success': False, 'error': str(e), 'data': {}}

    async def get_service_health(self) -> Dict[str, Any]:
        try:
            await self._load_model()
            return {
                'service': 'ClinicalBERT',
                'status': 'healthy',
                'model_loaded': self.is_loaded,
                'device': self.device,
                'transformers_available': TRANSFORMERS_AVAILABLE,
                'scispaCy_available': HAS_SCISPACY,
                'scispaCy_model': scispacy_models[0] if HAS_SCISPACY else None,
                'hf_ner_available': self._ner_pipeline is not None,
                'primary_model': self.primary_model,
                'fallback_model': self.fallback_model,
            }
        except Exception as e:
            return {
                'service': 'ClinicalBERT',
                'status': 'unhealthy',
                'error': str(e)
            }


# Global service instance
_clinical_bert_service = None


def get_clinical_bert_service() -> ClinicalBERTService:
    global _clinical_bert_service
    if _clinical_bert_service is None:
        _clinical_bert_service = ClinicalBERTService()
    return _clinical_bert_service
