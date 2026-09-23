"""
MatSciBERT Service for AXIOM
Materials science text analysis using MatSciBERT for advanced materials research

Capabilities:
- Materials property extraction and analysis
- Chemical composition understanding
- Materials synthesis route analysis
- Scientific literature analysis for materials research
- Materials discovery and design insights

Ethics & Safety:
- Environmental Impact: Consider environmental implications of materials research
- Safety Protocols: Ensure safe handling recommendations for chemical compounds
- Research Ethics: Results for research purposes, not direct industrial application without validation
- Data Quality: Verify materials data through established databases and peer review

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
from app.types.matscibert_service_types import (
    AnalyzeMaterialsTextResult,
    ExtractSynthesisInfoResult,
    GenerateMaterialsSummaryResult,
    FallbackMaterialsAnalysisResult,
    SimpleMaterialsSimilarityResult,
    GetServiceInfoResult,
)


@dataclass
class MaterialEntity:
    """Materials science entity representation"""
    text: str
    entity_type: str
    confidence: float
    properties: Dict[str, Any]
    chemical_formula: Optional[str]
    material_class: str


@dataclass 
class MaterialsAnalysisResult:
    """Materials analysis result"""
    text: str
    entities: List[MaterialEntity]
    material_properties: Dict[str, Any]
    synthesis_info: Dict[str, Any]
    research_context: str
    processing_info: Dict[str, Any]


@dataclass
class MaterialsSimilarityResult:
    """Materials similarity analysis result"""
    text1: str
    text2: str
    similarity_score: float
    common_materials: List[str]
    property_overlap: Dict[str, Any]
    research_relevance: str


from app.services.base_service import BaseService

class MatSciBERTService(BaseService):
    """Advanced materials science text analysis using MatSciBERT"""
    
    def __init__(self):
        """Initialize MatSciBERT Service"""
        super().__init__("MatSciBERTService")
        
        # Model initialization
        self.tokenizer: Optional[Any] = None
        self.model: Optional[Any] = None
        self.device = "cuda" if HAS_TORCH and torch.cuda.is_available() else "cpu"
        
        # Materials entity types
        self.material_entity_types = {
            'MATERIAL': 'Material/Compound',
            'PROPERTY': 'Material Property',
            'SYNTHESIS': 'Synthesis Method',
            'CHARACTERIZATION': 'Characterization Technique',
            'APPLICATION': 'Material Application',
            'STRUCTURE': 'Crystal Structure'
        }
        
        # Material classes
        self.material_classes = [
            'metals', 'ceramics', 'polymers', 'composites', 
            'semiconductors', 'superconductors', 'biomaterials',
            'nanomaterials', '2d_materials', 'energy_materials'
        ]
        
        # Common material properties
        self.material_properties = [
            'conductivity', 'strength', 'hardness', 'density',
            'melting_point', 'elastic_modulus', 'thermal_conductivity',
            'bandgap', 'magnetism', 'corrosion_resistance'
        ]
        
        self._initialize_model()
        logger.info(f"✅ MatSciBERTService initialized on {self.device}")
    
    def _initialize_model(self):
        """Initialize MatSciBERT model with fallback handling"""
        if not HAS_TORCH:
            logger.warning("Torch not available, running in fallback mode")
            return

        try:
            from transformers import AutoTokenizer, AutoModel
            # Primary model: MatSciBERT
            model_name = "m3rg-iitd/matscibert"
            logger.info(f"Loading MatSciBERT model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("✅ MatSciBERT model loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to load MatSciBERT model: {e}")
            logger.info("Using fallback: SciBERT for materials analysis")
            
            # Fallback to SciBERT
            try:
                from transformers import AutoTokenizer, AutoModel
                fallback_model = "allenai/scibert_scivocab_uncased"
                self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
                self.model = AutoModel.from_pretrained(fallback_model)
                self.model.to(self.device)
                self.model.eval()
                logger.info("✅ Fallback SciBERT model loaded")
            except Exception as fallback_e:
                logger.warning(f"Failed to load SciBERT fallback: {fallback_e}")
                # Final fallback to BERT
                try:
                    from transformers import AutoTokenizer, AutoModel
                    final_fallback = "bert-base-uncased"
                    self.tokenizer = AutoTokenizer.from_pretrained(final_fallback)
                    self.model = AutoModel.from_pretrained(final_fallback)
                    self.model.to(self.device)
                    self.model.eval()
                    logger.info("✅ Final fallback BERT model loaded")
                except BiologyError as final_e:
                    logger.error(f"All model loading attempts failed: {final_e}")
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
                result = await self.analyze_materials_text(text)
                return {"success": True, "data": result}
            elif operation == "extract_synthesis":
                text = request_data.get("text")
                if not text:
                    return {"success": False, "error": "Text is required"}
                result = await self.extract_synthesis_info(text)
                return {"success": True, "data": result}
            elif operation == "generate_summary":
                text = request_data.get("text")
                if not text:
                    return {"success": False, "error": "Text is required"}
                result = await self.generate_materials_summary(text)
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
        except Exception as e:
            return self.handle_error(e, "process_request")

    async def analyze_materials_text(self, text: str) -> AnalyzeMaterialsTextResult:
        """Comprehensive materials science text analysis"""
        try:
            if len(text.strip()) < 20:
                raise ValueError("Text too short for materials analysis")
            
            # Extract materials entities
            entities = await self._extract_materials_entities(text)
            
            # Analyze material properties
            properties = await self._analyze_material_properties(text, entities)
            
            # Extract synthesis information
            synthesis_info = await self._extract_synthesis_info(text)
            
            # Determine research context
            research_context = self._determine_research_context(text, entities)
            
            result = MaterialsAnalysisResult(
                text=text[:500] + "..." if len(text) > 500 else text,
                entities=entities,
                material_properties=properties,
                synthesis_info=synthesis_info,
                research_context=research_context,
                processing_info={
                    "model": "MatSciBERT" if "matscibert" in str(self.model) else "SciBERT/BERT",
                    "device": self.device,
                    "text_length": len(text),
                    "entities_found": len(entities)
                }
            )
            
            return {
                "success": True,
                "message": "Materials text analyzed successfully",
                "data": {
                    "entities": [
                        {
                            "text": e.text,
                            "type": e.entity_type,
                            "material_class": e.material_class,
                            "confidence": e.confidence,
                            "chemical_formula": e.chemical_formula
                        } for e in result.entities
                    ],
                    "material_properties": result.material_properties,
                    "synthesis_info": result.synthesis_info,
                    "research_context": result.research_context,
                    "materials_summary": self._generate_materials_summary(result),
                    "processing_info": result.processing_info
                }
            }
            
        except BiologyError as e:
            logger.error(f"Materials text analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_analysis": await self._fallback_materials_analysis(text)
            }
    
    async def calculate_materials_similarity(
        self, 
        text1: str, 
        text2: str
    ) -> Dict[str, Any]:
        """Calculate similarity between materials research texts"""
        try:
            if not self.model or not self.tokenizer:
                return {
                    "success": False,
                    "error": "MatSciBERT model not available",
                    "fallback_similarity": self._simple_materials_similarity(text1, text2)
                }
            
            # Get embeddings for both texts
            embedding1 = await self._get_materials_embedding(text1)
            embedding2 = await self._get_materials_embedding(text2)
            
            if embedding1 is None or embedding2 is None:
                raise ValueError("Failed to generate materials text embeddings")
            
            # Calculate similarity
            similarity_score = cosine_similarity(
                embedding1.reshape(1, -1),
                embedding2.reshape(1, -1)
            )[0][0]
            
            # Find common materials
            materials1 = await self._extract_materials_entities(text1)
            materials2 = await self._extract_materials_entities(text2)
            
            common_materials = self._find_common_materials(materials1, materials2)
            
            # Analyze property overlap
            properties1 = await self._analyze_material_properties(text1, materials1)
            properties2 = await self._analyze_material_properties(text2, materials2)
            property_overlap = self._calculate_property_overlap(properties1, properties2)
            
            # Determine research relevance
            research_relevance = self._interpret_materials_similarity(
                similarity_score, 
                len(common_materials),
                property_overlap
            )
            
            result = MaterialsSimilarityResult(
                text1=text1[:100] + "..." if len(text1) > 100 else text1,
                text2=text2[:100] + "..." if len(text2) > 100 else text2,
                similarity_score=float(similarity_score),
                common_materials=common_materials,
                property_overlap=property_overlap,
                research_relevance=research_relevance
            )
            
            return {
                "success": True,
                "message": "Materials similarity calculated successfully",
                "data": {
                    "similarity_score": result.similarity_score,
                    "common_materials": result.common_materials,
                    "property_overlap": result.property_overlap,
                    "research_relevance": result.research_relevance,
                    "similarity_interpretation": self._interpret_similarity_score(result.similarity_score),
                    "materials_overlap_count": len(result.common_materials)
                }
            }
            
        except BiologyError as e:
            logger.error(f"Materials similarity calculation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_similarity": self._simple_materials_similarity(text1, text2)
            }
    
    async def predict_material_properties(
        self, 
        material_description: str
    ) -> Dict[str, Any]:
        """Predict material properties from description using MatSciBERT"""
        try:
            if not self.model or not self.tokenizer:
                return {
                    "success": False,
                    "error": "MatSciBERT model not available",
                    "fallback_prediction": self._rule_based_property_prediction(material_description)
                }
            
            # Extract entities and analyze
            entities = await self._extract_materials_entities(material_description)
            properties = await self._analyze_material_properties(material_description, entities)
            
            # Generate embedding for property prediction
            embedding = await self._get_materials_embedding(material_description)
            
            # Rule-based property prediction (can be enhanced with trained models)
            predicted_properties = self._predict_properties_from_description(
                material_description, entities, embedding
            )
            
            return {
                "success": True,
                "message": "Material properties predicted successfully",
                "data": {
                    "material_entities": [e.text for e in entities],
                    "predicted_properties": predicted_properties,
                    "confidence_scores": {prop: 0.7 for prop in predicted_properties.keys()},
                    "prediction_method": "MatSciBERT + rule-based",
                    "recommendations": self._generate_property_recommendations(predicted_properties)
                }
            }
            
        except BiologyError as e:
            logger.error(f"Material property prediction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_prediction": self._rule_based_property_prediction(material_description)
            }
    
    async def _get_materials_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate MatSciBERT embedding for materials text"""
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
            logger.error(f"Materials embedding generation error: {e}")
            return None
    
    async def _extract_materials_entities(self, text: str) -> List[MaterialEntity]:
        """Extract materials-related entities from text"""
        entities = []
        text_lower = text.lower()
        
        # Define materials keywords by category
        materials_keywords = {
            'metals': ['iron', 'steel', 'aluminum', 'copper', 'titanium', 'gold', 'silver', 'zinc'],
            'ceramics': ['alumina', 'zirconia', 'silicon carbide', 'boron nitride', 'silicon nitride'],
            'polymers': ['polyethylene', 'polystyrene', 'pvdf', 'peek', 'pvc', 'polymer'],
            'semiconductors': ['silicon', 'germanium', 'gallium arsenide', 'indium phosphide'],
            'nanomaterials': ['graphene', 'carbon nanotube', 'quantum dot', 'nanoparticle', 'fullerene'],
            '2d_materials': ['graphene', 'mos2', 'ws2', 'borophene', 'phosphorene'],
            'energy_materials': ['lithium', 'battery', 'solar cell', 'fuel cell', 'electrode']
        }
        
        for material_class, keywords in materials_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Try to extract chemical formula if present
                    formula = self._extract_chemical_formula(text, keyword)
                    
                    entity = MaterialEntity(
                        text=keyword,
                        entity_type='MATERIAL',
                        confidence=0.8,
                        properties={},
                        chemical_formula=formula,
                        material_class=material_class
                    )
                    entities.append(entity)
        
        return entities
    
    async def _analyze_material_properties(
        self, 
        text: str, 
        entities: List[MaterialEntity]
    ) -> Dict[str, Any]:
        """Analyze material properties mentioned in text"""
        properties = {}
        text_lower = text.lower()
        
        # Property keywords with units
        property_patterns = {
            'conductivity': r'conductivity|conductive|electrical conductivity',
            'strength': r'strength|tensile|yield strength|ultimate strength',
            'hardness': r'hardness|vickers|rockwell|brinell',
            'density': r'density|specific gravity',
            'melting_point': r'melting point|melting temperature|mp',
            'elastic_modulus': r'elastic modulus|young.s modulus|modulus',
            'thermal_conductivity': r'thermal conductivity|heat transfer',
            'bandgap': r'bandgap|band gap|energy gap'
        }
        
        for prop_name, pattern in property_patterns.items():
            if re.search(pattern, text_lower):
                properties[prop_name] = {
                    'mentioned': True,
                    'confidence': 0.7,
                    'context': self._extract_property_context(text, prop_name)
                }
        
        return properties
    
    async def _extract_synthesis_info(self, text: str) -> ExtractSynthesisInfoResult:
        """Extract synthesis and processing information"""
        synthesis_info = {
            'methods': [],
            'conditions': {},
            'equipment': []
        }
        
        text_lower = text.lower()
        
        # Synthesis methods
        synthesis_methods = [
            'sol-gel', 'cvd', 'pvd', 'sputtering', 'epitaxy',
            'chemical vapor deposition', 'physical vapor deposition',
            'hydrothermal', 'sintering', 'annealing'
        ]
        
        for method in synthesis_methods:
            if method in text_lower:
                synthesis_info['methods'].append(method)
        
        # Processing conditions
        temp_match = re.search(r'(\d+)\s*°?c|(\d+)\s*celsius|(\d+)\s*kelvin', text_lower)
        if temp_match:
            temp = temp_match.group(1) or temp_match.group(2) or temp_match.group(3)
            synthesis_info['conditions']['temperature'] = f"{temp}°C"
        
        pressure_match = re.search(r'(\d+\.?\d*)\s*(pa|bar|atm|torr|psi)', text_lower)
        if pressure_match:
            synthesis_info['conditions']['pressure'] = f"{pressure_match.group(1)} {pressure_match.group(2)}"
        
        return synthesis_info
    
    def _determine_research_context(self, text: str, entities: List[MaterialEntity]) -> str:
        """Determine the research context/application area"""
        text_lower = text.lower()
        
        context_keywords = {
            'energy_storage': ['battery', 'supercapacitor', 'energy storage', 'electrode'],
            'electronics': ['semiconductor', 'transistor', 'circuit', 'electronic'],
            'biomedical': ['biocompatible', 'implant', 'medical', 'biomedical'],
            'aerospace': ['aerospace', 'aircraft', 'space', 'lightweight'],
            'automotive': ['automotive', 'vehicle', 'engine', 'brake'],
            'construction': ['construction', 'building', 'concrete', 'structural']
        }
        
        for context, keywords in context_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return context
        
        return 'general_materials_research'
    
    def _extract_chemical_formula(self, text: str, material_name: str) -> Optional[str]:
        """Extract chemical formula near material name"""
        # Simple pattern matching for chemical formulas
        formula_pattern = r'[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*'
        
        # Look for formula near the material name
        material_pos = text.lower().find(material_name.lower())
        if material_pos != -1:
            # Search in a window around the material name
            window_start = max(0, material_pos - 50)
            window_end = min(len(text), material_pos + len(material_name) + 50)
            window_text = text[window_start:window_end]
            
            formulas = re.findall(formula_pattern, window_text)
            if formulas:
                return formulas[0]  # Return first found formula
        
        return None
    
    def _extract_property_context(self, text: str, property_name: str) -> str:
        """Extract context around property mention"""
        prop_pos = text.lower().find(property_name.lower())
        if prop_pos != -1:
            # Extract surrounding context
            start = max(0, prop_pos - 100)
            end = min(len(text), prop_pos + 100)
            return text[start:end].strip()
        return ""
    
    def _find_common_materials(
        self, 
        materials1: List[MaterialEntity], 
        materials2: List[MaterialEntity]
    ) -> List[str]:
        """Find common materials between two lists"""
        materials1_names = {m.text.lower() for m in materials1}
        materials2_names = {m.text.lower() for m in materials2}
        
        return list(materials1_names.intersection(materials2_names))
    
    def _calculate_property_overlap(
        self, 
        props1: Dict[str, Any], 
        props2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overlap in material properties"""
        common_properties = set(props1.keys()).intersection(set(props2.keys()))
        
        overlap_info = {
            'common_properties': list(common_properties),
            'overlap_ratio': len(common_properties) / max(len(props1), len(props2), 1),
            'total_unique_properties': len(set(props1.keys()).union(set(props2.keys())))
        }
        
        return overlap_info
    
    def _interpret_materials_similarity(
        self, 
        similarity_score: float, 
        common_materials_count: int,
        property_overlap: Dict[str, Any]
    ) -> str:
        """Interpret materials similarity with multiple factors"""
        if similarity_score >= 0.8 and common_materials_count >= 2:
            return "highly_similar_materials_research"
        elif similarity_score >= 0.6 or common_materials_count >= 1:
            return "moderately_similar_materials_research"
        elif similarity_score >= 0.4 or property_overlap['overlap_ratio'] > 0.3:
            return "somewhat_related_materials_research"
        else:
            return "different_materials_research_areas"
    
    def _predict_properties_from_description(
        self, 
        description: str, 
        entities: List[MaterialEntity], 
        embedding: Optional[np.ndarray]
    ) -> Dict[str, Any]:
        """Rule-based property prediction from material description"""
        predicted_props = {}
        desc_lower = description.lower()
        
        # Predict properties based on material class
        for entity in entities:
            if entity.material_class == 'metals':
                predicted_props.update({
                    'electrical_conductivity': 'high',
                    'thermal_conductivity': 'high',
                    'ductility': 'high'
                })
            elif entity.material_class == 'ceramics':
                predicted_props.update({
                    'hardness': 'high',
                    'electrical_conductivity': 'low',
                    'thermal_stability': 'high'
                })
            elif entity.material_class == 'polymers':
                predicted_props.update({
                    'flexibility': 'high',
                    'density': 'low',
                    'chemical_resistance': 'variable'
                })
            elif entity.material_class == 'semiconductors':
                predicted_props.update({
                    'bandgap': 'tunable',
                    'electrical_conductivity': 'moderate',
                    'doping_capability': 'high'
                })
        
        return predicted_props
    
    def _generate_property_recommendations(self, predicted_properties: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on predicted properties"""
        recommendations = []
        
        if 'electrical_conductivity' in predicted_properties:
            if predicted_properties['electrical_conductivity'] == 'high':
                recommendations.append("Suitable for electrical applications and conductive pathways")
            elif predicted_properties['electrical_conductivity'] == 'low':
                recommendations.append("Good insulator, suitable for dielectric applications")
        
        if 'hardness' in predicted_properties:
            if predicted_properties['hardness'] == 'high':
                recommendations.append("Excellent for wear-resistant applications")
        
        if 'flexibility' in predicted_properties:
            if predicted_properties['flexibility'] == 'high':
                recommendations.append("Good for applications requiring deformation tolerance")
        
        return recommendations
    
    def _generate_materials_summary(self, result: MaterialsAnalysisResult) -> GenerateMaterialsSummaryResult:
        """Generate summary of materials analysis"""
        summary = {
            "total_materials": len(result.entities),
            "primary_material_classes": list(set(e.material_class for e in result.entities)),
            "key_properties": list(result.material_properties.keys()),
            "synthesis_methods": result.synthesis_info.get('methods', []),
            "research_focus": result.research_context,
            "complexity_level": "high" if len(result.entities) > 5 else "moderate"
        }
        
        return summary
    
    def _interpret_similarity_score(self, score: float) -> str:
        """Provide human-readable similarity interpretation"""
        if score >= 0.8:
            return "Very similar materials research - likely same material system or properties"
        elif score >= 0.6:
            return "Moderately similar - may share material classes or applications"
        elif score >= 0.4:
            return "Some similarity - possibly related synthesis methods or characterization"
        else:
            return "Different materials research areas - distinct material systems"
    
    async def _fallback_materials_analysis(self, text: str) -> FallbackMaterialsAnalysisResult:
        """Fallback analysis using keyword matching"""
        entities = await self._extract_materials_entities(text)
        
        return {
            "entities": [e.text for e in entities],
            "material_classes": list(set(e.material_class for e in entities)),
            "method": "keyword_based_fallback",
            "note": "MatSciBERT not available - using rule-based analysis"
        }
    
    def _rule_based_property_prediction(self, description: str) -> Dict[str, str]:
        """Fallback rule-based property prediction"""
        return {
            "predicted_properties": {"general": "properties depend on specific material composition"},
            "method": "rule_based_fallback",
            "note": "MatSciBERT not available"
        }
    
    def _simple_materials_similarity(self, text1: str, text2: str) -> SimpleMaterialsSimilarityResult:
        """Fallback simple materials similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        jaccard_score = intersection / union if union > 0 else 0.0
        
        return {
            "similarity_score": jaccard_score,
            "method": "jaccard_similarity",
            "note": "MatSciBERT not available - using word overlap"
        }
    
    def get_service_info(self) -> GetServiceInfoResult:
        """Get MatSciBERT service information"""
        return {
            "service_name": "MatSciBERT Service",
            "model_loaded": self.model is not None,
            "device": self.device,
            "capabilities": [
                "Materials entity extraction",
                "Property analysis and prediction",
                "Synthesis route analysis",
                "Materials similarity comparison",
                "Research context determination"
            ],
            "material_classes": self.material_classes,
            "supported_properties": self.material_properties,
            "model_info": "m3rg-iitd/matscibert" if self.model else "Not loaded"
        }
