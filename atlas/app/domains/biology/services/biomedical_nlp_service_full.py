"""
Biomedical NLP Service for AXIOM
Enhanced semantic analysis using BioBERT for scientific literature

Capabilities:
- Biomedical entity extraction (genes, proteins, diseases, chemicals)
- Semantic similarity analysis for scientific texts
- Literature enhancement with domain-specific understanding
- Integration with existing LiteratureSearchService

Ethics & Safety:
- Uso responsable: resultados para investigación, no diagnóstico médico
- Datos sensibles: no procesar información personal de salud
- Limitaciones: complementa pero no sustituye revisión experta
- Privacidad: no enviar datos confidenciales a APIs externas

Consulta la guía: ETHICS_AND_SAFETY.md
"""

# Optional torch import for deep learning support
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore
from transformers import AutoTokenizer, AutoModel
from transformers.pipelines import pipeline
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.utils.hf_safe import safe_load_pipeline


@dataclass
class BiomedicalEntity:
    """Biomedical entity representation"""
    text: str
    label: str
    confidence: float
    start_pos: int
    end_pos: int
    entity_type: str


@dataclass
class SemanticAnalysisResult:
    """Result of semantic analysis"""
    similarity_score: float
    key_concepts: List[str]
    biomedical_relevance: float
    extracted_entities: List[BiomedicalEntity]


class BiomedicalNLPService:
    """Advanced biomedical NLP service using BioBERT"""
    
    def __init__(self):
        """Initialize Biomedical NLP Service with BioBERT"""
        
        # Model initialization with error handling
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model: Optional[AutoModel] = None
        self.ner_pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Entity types mapping
        self.entity_types = {
            'GENE': 'Gene/Protein',
            'DISEASE': 'Disease/Disorder', 
            'CHEMICAL': 'Chemical/Drug',
            'SPECIES': 'Species/Organism',
            'CELL_TYPE': 'Cell Type',
            'TISSUE': 'Tissue/Organ'
        }
        
        self._initialize_models()
        logger.info(f"✅ BiomedicalNLPService initialized on {self.device}")
    
    def _initialize_models(self):
        """Initialize BioBERT models with fallback handling"""
        try:
            # Primary model: BioBERT for embeddings
            model_name = "dmis-lab/biobert-base-cased-v1.2"
            logger.info(f"Loading BioBERT model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # NER pipeline for entity extraction
            ner_model = "d4data/biomedical-ner-all"
            self.ner_pipeline = safe_load_pipeline(
                "ner",
                ner_model,
                tokenizer=ner_model,
                aggregation_strategy="simple",
            )

            if self.ner_pipeline is not None:
                logger.info("✅ BioBERT models loaded successfully")
            else:
                raise BiologyError("NER pipeline unavailable (safe loader returned None)")

        except BiologyError as e:
            logger.warning(f"Failed to load BioBERT models: {e}")
            logger.info("Using fallback: general transformers model")
            
            # Fallback to a smaller, more reliable model
            try:
                fallback_model = "bert-base-uncased"
                self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
                self.model = AutoModel.from_pretrained(fallback_model)
                self.model.to(self.device)
                self.model.eval()
                logger.info("✅ Fallback model loaded")
            except BiologyError as fallback_e:
                logger.error(f"Failed to load fallback model: {fallback_e}")
                self.model = None
                self.tokenizer = None
    
    async def extract_biomedical_entities(self, text: str) -> Dict[str, Any]:
        """Extract biomedical entities from scientific text"""
        try:
            if not self.ner_pipeline:
                return {
                    "success": False,
                    "error": "NER model not available",
                    "fallback_entities": await self._extract_simple_entities(text)
                }
            
            # Use BioBERT NER pipeline
            entities_raw = self.ner_pipeline(text)
            
            entities = []
            for ent in entities_raw:
                biomedical_entity = BiomedicalEntity(
                    text=ent['word'],
                    label=ent['entity_group'],
                    confidence=float(ent['score']),
                    start_pos=int(ent['start']),
                    end_pos=int(ent['end']),
                    entity_type=self.entity_types.get(ent['entity_group'], 'Unknown')
                )
                entities.append(biomedical_entity)
            
            # Group entities by type
            entities_by_type = {}
            for entity in entities:
                entity_type = entity.entity_type
                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []
                entities_by_type[entity_type].append({
                    'text': entity.text,
                    'confidence': entity.confidence,
                    'position': (entity.start_pos, entity.end_pos)
                })
            
            return {
                "success": True,
                "message": "Biomedical entities extracted successfully",
                "data": {
                    "total_entities": len(entities),
                    "entities_by_type": entities_by_type,
                    "raw_entities": [
                        {
                            "text": e.text,
                            "label": e.label,
                            "confidence": e.confidence,
                            "type": e.entity_type
                        } for e in entities
                    ],
                    "processing_info": {
                        "model": "BioBERT NER",
                        "device": self.device,
                        "text_length": len(text)
                    }
                }
            }
            
        except BiologyError as e:
            logger.error(f"Error in entity extraction: {e}")
            return {
                "success": False,
                "error": f"Entity extraction failed: {str(e)}",
                "fallback_entities": await self._extract_simple_entities(text)
            }
    
    async def _extract_simple_entities(self, text: str) -> Dict[str, List[str]]:
        """Fallback simple entity extraction using keyword matching"""
        biomedical_keywords = {
            'Gene/Protein': ['protein', 'gene', 'enzyme', 'receptor', 'kinase'],
            'Disease/Disorder': ['cancer', 'tumor', 'disease', 'disorder', 'syndrome'],
            'Chemical/Drug': ['drug', 'compound', 'molecule', 'inhibitor', 'treatment'],
            'Species/Organism': ['human', 'mouse', 'rat', 'cell', 'tissue']
        }
        
        text_lower = text.lower()
        found_entities = {}
        
        for entity_type, keywords in biomedical_keywords.items():
            found = [kw for kw in keywords if kw in text_lower]
            if found:
                found_entities[entity_type] = found
        
        return found_entities
    
    async def calculate_semantic_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """Calculate semantic similarity between two scientific texts"""
        try:
            if not self.model or not self.tokenizer:
                return {
                    "success": False,
                    "error": "BioBERT model not available",
                    "similarity_score": 0.0
                }
            
            # Get embeddings for both texts
            embedding1 = await self._get_text_embedding(text1)
            embedding2 = await self._get_text_embedding(text2)
            
            if embedding1 is None or embedding2 is None:
                return {
                    "success": False,
                    "error": "Failed to generate embeddings",
                    "similarity_score": 0.0
                }
            
            # Calculate cosine similarity
            similarity = torch.cosine_similarity(embedding1, embedding2, dim=0)
            similarity_score = float(similarity.item())
            
            # Determine relevance level
            if similarity_score > 0.8:
                relevance = "High"
            elif similarity_score > 0.6:
                relevance = "Medium" 
            elif similarity_score > 0.4:
                relevance = "Low"
            else:
                relevance = "Very Low"
            
            return {
                "success": True,
                "message": "Semantic similarity calculated successfully",
                "data": {
                    "similarity_score": similarity_score,
                    "relevance_level": relevance,
                    "text1_length": len(text1),
                    "text2_length": len(text2),
                    "model_info": {
                        "model": "BioBERT",
                        "device": self.device
                    }
                }
            }
            
        except BiologyError as e:
            logger.error(f"Error calculating similarity: {e}")
            return {
                "success": False,
                "error": f"Similarity calculation failed: {str(e)}",
                "similarity_score": 0.0
            }
    
    async def _get_text_embedding(self, text: str) -> Optional[torch.Tensor]:
        """Generate BioBERT embedding for text"""
        try:
            # Tokenize and encode
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use [CLS] token embedding
                embedding = outputs.last_hidden_state[:, 0, :].squeeze()
            
            return embedding
            
        except BiologyError as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    async def enhance_literature_search(self, query: str, papers: List[Dict]) -> Dict[str, Any]:
        """Enhance literature search results with biomedical understanding"""
        try:
            enhanced_papers = []
            
            for paper in papers:
                title = paper.get('title', '')
                abstract = paper.get('abstract', '')
                
                # Extract entities from title + abstract
                text = f"{title} {abstract}"
                entities_result = await self.extract_biomedical_entities(text)
                
                # Calculate relevance to query
                similarity_result = await self.calculate_semantic_similarity(query, text)
                
                enhanced_paper = paper.copy()
                enhanced_paper.update({
                    'biomedical_entities': entities_result.get('data', {}),
                    'semantic_relevance': similarity_result.get('data', {}),
                    'biomedical_score': self._calculate_biomedical_score(entities_result, similarity_result)
                })
                
                enhanced_papers.append(enhanced_paper)
            
            # Sort by biomedical relevance
            enhanced_papers.sort(key=lambda x: x['biomedical_score'], reverse=True)
            
            return {
                "success": True,
                "message": "Literature search enhanced with biomedical analysis",
                "data": {
                    "enhanced_papers": enhanced_papers,
                    "total_papers": len(enhanced_papers),
                    "enhancement_info": {
                        "query": query,
                        "biomedical_analysis": True,
                        "semantic_similarity": True
                    }
                }
            }
            
        except BiologyError as e:
            logger.error(f"Error enhancing literature search: {e}")
            return {
                "success": False,
                "error": f"Literature enhancement failed: {str(e)}",
                "data": {"enhanced_papers": papers}  # Return original papers
            }
    
    def _calculate_biomedical_score(self, entities_result: Dict, similarity_result: Dict) -> float:
        """Calculate composite biomedical relevance score"""
        try:
            # Entity score (0-1)
            entity_score = 0.0
            if entities_result.get('success') and 'data' in entities_result:
                total_entities = entities_result['data'].get('total_entities', 0)
                entity_score = min(total_entities / 10.0, 1.0)  # Normalize to 0-1
            
            # Semantic score (0-1)  
            semantic_score = 0.0
            if similarity_result.get('success') and 'data' in similarity_result:
                semantic_score = similarity_result['data'].get('similarity_score', 0.0)
            
            # Weighted combination
            biomedical_score = (0.6 * semantic_score) + (0.4 * entity_score)
            return float(biomedical_score)
            
        except BiologyError:
            return 0.0
    
    async def analyze_paper_abstract(self, abstract: str) -> Dict[str, Any]:
        """Comprehensive analysis of a scientific paper abstract"""
        try:
            # Extract entities
            entities_result = await self.extract_biomedical_entities(abstract)
            
            # Analyze key concepts (simplified)
            key_concepts = await self._extract_key_concepts(abstract)
            
            # Determine research domain
            research_domain = await self._classify_research_domain(abstract, entities_result)
            
            return {
                "success": True,
                "message": "Paper abstract analyzed successfully",
                "data": {
                    "abstract_length": len(abstract),
                    "biomedical_entities": entities_result.get('data', {}),
                    "key_concepts": key_concepts,
                    "research_domain": research_domain,
                    "analysis_timestamp": datetime.now().isoformat()
                }
            }
            
        except BiologyError as e:
            logger.error(f"Error analyzing abstract: {e}")
            return {
                "success": False,
                "error": f"Abstract analysis failed: {str(e)}"
            }
    
    async def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key scientific concepts (simplified implementation)"""
        # This is a simplified version - in production, you might use more sophisticated methods
        scientific_terms = [
            'mechanism', 'pathway', 'expression', 'regulation', 'interaction',
            'inhibition', 'activation', 'binding', 'structure', 'function',
            'mutation', 'variant', 'treatment', 'therapy', 'diagnosis'
        ]
        
        text_lower = text.lower()
        found_concepts = [term for term in scientific_terms if term in text_lower]
        return found_concepts[:10]  # Return top 10
    
    async def _classify_research_domain(self, text: str, entities_result: Dict) -> str:
        """Classify the research domain based on content"""
        domain_keywords = {
            'Drug Discovery': ['drug', 'compound', 'molecule', 'inhibitor', 'therapeutic'],
            'Genomics': ['gene', 'genome', 'dna', 'rna', 'sequencing'],
            'Proteomics': ['protein', 'enzyme', 'receptor', 'structure'],
            'Cancer Research': ['cancer', 'tumor', 'oncology', 'metastasis'],
            'Neuroscience': ['brain', 'neuron', 'neural', 'cognitive'],
            'Immunology': ['immune', 'antibody', 'vaccine', 'inflammation']
        }
        
        text_lower = text.lower()
        domain_scores = {}
        
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        else:
            return "General Biomedical"

    # Health check and status methods
    async def health_check(self) -> Dict[str, Any]:
        """Check service health and model availability"""
        return {
            "service": "BiomedicalNLPService",
            "status": "healthy" if self.model is not None else "degraded",
            "models_loaded": {
                "biobert_embeddings": self.model is not None,
                "ner_pipeline": self.ner_pipeline is not None
            },
            "device": self.device,
            "capabilities": [
                "biomedical_entity_extraction",
                "semantic_similarity", 
                "literature_enhancement",
                "abstract_analysis"
            ]
        }
