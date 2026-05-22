"""
Multimodal Scientific Reasoning Service

Este servicio proporciona capacidades avanzadas de razonamiento multimodal
para análisis científico, integrando Claude 3.5 Sonnet y GPT-4V para
procesamiento de texto, imágenes, gráficos y datos científicos.
"""

import asyncio
import base64
import io
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import json
import aiofiles

import openai
import anthropic
from PIL import Image
try:
    import cv2
    CV2_AVAILABLE = True
except Exception:
    cv2 = None
    CV2_AVAILABLE = False
import numpy as np
# Optional torch import for deep learning support
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore
from app.exceptions.domain.biology import BiologyError
from app.types.multimodal_reasoning_service_types import (
    AnalyzeWithClaudeResult,
    AnalyzeWithGpt4Result,
    AnalyzeWithLocalModelsResult,
    AnalyzeImageLocallyResult,
    HealthCheckResult,
)
from app.utils.hf_safe import safe_load_pipeline, safe_load_tokenizer

logger = logging.getLogger(__name__)

class MultimodalReasoningService:
    """
    Servicio de Razonamiento Multimodal Científico
    
    Integra múltiples modelos de IA para análisis científico multimodal:
    - Claude 3.5 Sonnet para razonamiento científico avanzado
    - GPT-4V para análisis visual y comprensión de imágenes
    - Modelos locales para procesamiento especializado
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Configuración de APIs
        self.anthropic_client = None
        self.openai_client = None
        
        # Modelos locales
        self.local_models = {}
        
        # Configuración de límites
        self.max_image_size = self.config.get("max_image_size", (1024, 1024))
        self.max_text_length = self.config.get("max_text_length", 100000)
        
        self._initialize_clients()
        self._initialize_local_models()
    
    def _initialize_clients(self):
        """Inicializa los clientes de API"""
        try:
            # Claude 3.5 Sonnet
            anthropic_key = self.config.get("anthropic_api_key")
            if anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("Cliente Anthropic inicializado")
            
            # GPT-4V
            openai_key = self.config.get("openai_api_key")
            if openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                logger.info("Cliente OpenAI inicializado")
                
        except BiologyError as e:
            logger.warning(f"Error inicializando clientes API: {e}")
    
    def _initialize_local_models(self):
        """Inicializa modelos locales para procesamiento especializado"""
        # Modelo para análisis de sentimientos científicos
        if self.config.get("enable_sentiment_analysis", True):
            model = safe_load_pipeline(
                "sentiment-analysis",
                "cardiffnlp/twitter-roberta-base-sentiment-latest",
            )
            if model is not None:
                self.local_models["sentiment"] = model
            else:
                logger.warning("Pipeline HF sentiment-analysis no disponible; se usará heurística simple.")
        
        # Modelo para clasificación de texto científico
        if self.config.get("enable_text_classification", True):
            model = safe_load_pipeline(
                "text-classification",
                "microsoft/DialoGPT-medium",
            )
            if model is not None:
                self.local_models["classification"] = model
            else:
                logger.warning("Pipeline HF text-classification no disponible; se usará clasificación heurística.")
        
        if self.local_models:
            logger.info("Modelos locales inicializados (total=%d)", len(self.local_models))
    
    async def analyze_scientific_document(
        self,
        text: str,
        images: Optional[List[Union[str, bytes, Image.Image]]] = None,
        analysis_type: str = "comprehensive",
        model_preference: str = "claude"
    ) -> Dict[str, Any]:
        """
        Analiza un documento científico multimodal
        
        Args:
            text: Texto del documento
            images: Lista de imágenes (rutas, bytes o objetos PIL)
            analysis_type: Tipo de análisis (comprehensive, summary, critique)
            model_preference: Modelo preferido (claude, gpt4v, hybrid)
        
        Returns:
            Diccionario con el análisis completo
        """
        try:
            results = {
                "text_analysis": {},
                "image_analysis": {},
                "multimodal_synthesis": {},
                "scientific_insights": {},
                "metadata": {
                    "analysis_type": analysis_type,
                    "model_used": model_preference,
                    "timestamp": asyncio.get_event_loop().time()
                }
            }
            
            # Análisis de texto
            if text:
                results["text_analysis"] = await self._analyze_text(
                    text, analysis_type, model_preference
                )
            
            # Análisis de imágenes
            if images:
                results["image_analysis"] = await self._analyze_images(
                    images, analysis_type, model_preference
                )
            
            # Síntesis multimodal
            if text and images:
                results["multimodal_synthesis"] = await self._synthesize_multimodal(
                    text, images, results["text_analysis"], results["image_analysis"]
                )
            
            # Insights científicos
            results["scientific_insights"] = await self._generate_scientific_insights(
                results, analysis_type
            )
            
            return results
            
        except BiologyError as e:
            logger.error(f"Error en análisis de documento científico: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _analyze_text(
        self,
        text: str,
        analysis_type: str,
        model_preference: str
    ) -> Dict[str, Any]:
        """Analiza el texto usando el modelo especificado"""
        try:
            results = {}
            
            # Análisis con Claude 3.5
            if model_preference in ["claude", "hybrid"] and self.anthropic_client:
                results["claude_analysis"] = await self._analyze_with_claude(
                    text, analysis_type
                )
            
            # Análisis con GPT-4
            if model_preference in ["gpt4", "hybrid"] and self.openai_client:
                results["gpt4_analysis"] = await self._analyze_with_gpt4(
                    text, analysis_type
                )
            
            # Análisis local
            results["local_analysis"] = await self._analyze_with_local_models(text)
            
            return results
            
        except BiologyError as e:
            logger.error(f"Error en análisis de texto: {e}")
            return {"error": str(e)}
    
    async def _analyze_with_claude(self, text: str, analysis_type: str) -> AnalyzeWithClaudeResult:
        """Analiza texto con Claude 3.5 Sonnet"""
        try:
            prompt = self._build_claude_prompt(text, analysis_type)
            
            message = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "content": message.content[0].text,
                "model": "claude-3-5-sonnet",
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
            
        except BiologyError as e:
            logger.error(f"Error con Claude: {e}")
            return {"error": str(e)}
    
    async def _analyze_with_gpt4(self, text: str, analysis_type: str) -> AnalyzeWithGpt4Result:
        """Analiza texto con GPT-4"""
        try:
            prompt = self._build_gpt4_prompt(text, analysis_type)
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": "gpt-4-turbo",
                "tokens_used": response.usage.total_tokens
            }
            
        except BiologyError as e:
            logger.error(f"Error con GPT-4: {e}")
            return {"error": str(e)}
    
    async def _analyze_images(
        self,
        images: List[Union[str, bytes, Image.Image]],
        analysis_type: str,
        model_preference: str
    ) -> Dict[str, Any]:
        """Analiza imágenes usando modelos de visión"""
        try:
            results = {"images": []}
            
            for i, image in enumerate(images):
                image_result = {
                    "index": i,
                    "analysis": {}
                }
                
                # Procesar imagen
                processed_image = await self._process_image(image)
                
                # Análisis con GPT-4V
                if model_preference in ["gpt4v", "hybrid"] and self.openai_client:
                    image_result["analysis"]["gpt4v"] = await self._analyze_image_with_gpt4v(
                        processed_image, analysis_type
                    )
                
                # Análisis con Claude (si soporta imágenes)
                if model_preference in ["claude", "hybrid"] and self.anthropic_client:
                    image_result["analysis"]["claude"] = await self._analyze_image_with_claude(
                        processed_image, analysis_type
                    )
                
                # Análisis local
                image_result["analysis"]["local"] = await self._analyze_image_locally(
                    processed_image
                )
                
                results["images"].append(image_result)
            
            return results
            
        except BiologyError as e:
            logger.error(f"Error en análisis de imágenes: {e}")
            return {"error": str(e)}
    
    async def _process_image(self, image: Union[str, bytes, Image.Image]) -> Image.Image:
        """Procesa y normaliza una imagen"""
        try:
            if isinstance(image, str):
                # Ruta de archivo
                pil_image = Image.aiofiles.aiofiles.open(image)
            elif isinstance(image, bytes):
                # Datos binarios
                pil_image = Image.aiofiles.aiofiles.open(io.BytesIO(image))
            elif isinstance(image, Image.Image):
                # Ya es una imagen PIL
                pil_image = image
            else:
                raise ValueError(f"Tipo de imagen no soportado: {type(image)}")
            
            # Redimensionar si es necesario
            if pil_image.size[0] > self.max_image_size[0] or pil_image.size[1] > self.max_image_size[1]:
                pil_image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
            
            # Convertir a RGB si es necesario
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")
            
            return pil_image
            
        except BiologyError as e:
            logger.error(f"Error procesando imagen: {e}")
            raise
    
    async def _analyze_image_with_gpt4v(
        self,
        image: Image.Image,
        analysis_type: str
    ) -> Dict[str, Any]:
        """Analiza imagen con GPT-4V"""
        try:
            # Convertir imagen a base64
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            prompt = self._build_image_analysis_prompt(analysis_type)
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": "gpt-4-vision",
                "tokens_used": response.usage.total_tokens
            }
            
        except BiologyError as e:
            logger.error(f"Error con GPT-4V: {e}")
            return {"error": str(e)}
    
    async def _analyze_image_with_claude(
        self,
        image: Image.Image,
        analysis_type: str
    ) -> Dict[str, Any]:
        """Analiza imagen con Claude (si soporta imágenes)"""
        try:
            # Convertir imagen a base64
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            prompt = self._build_image_analysis_prompt(analysis_type)
            
            message = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_b64
                                }
                            }
                        ]
                    }
                ]
            )
            
            return {
                "content": message.content[0].text,
                "model": "claude-3-5-sonnet",
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
            
        except BiologyError as e:
            logger.error(f"Error con Claude Vision: {e}")
            return {"error": str(e)}
    
    def _build_claude_prompt(self, text: str, analysis_type: str) -> str:
        """Construye prompt para Claude"""
        base_prompt = f"""
        Eres un asistente científico experto. Analiza el siguiente texto científico con un enfoque de {analysis_type}.
        
        Proporciona:
        1. Resumen ejecutivo
        2. Conceptos clave identificados
        3. Metodología utilizada (si aplica)
        4. Resultados principales
        5. Limitaciones y sesgos potenciales
        6. Implicaciones científicas
        7. Recomendaciones para investigación futura
        
        Texto a analizar:
        {text[:self.max_text_length]}
        """
        return base_prompt
    
    def _build_gpt4_prompt(self, text: str, analysis_type: str) -> str:
        """Construye prompt para GPT-4"""
        base_prompt = f"""
        Como experto en análisis científico, realiza un análisis {analysis_type} del siguiente texto.
        
        Incluye:
        - Análisis crítico de la metodología
        - Evaluación de la validez de los resultados
        - Identificación de fortalezas y debilidades
        - Contexto dentro del campo científico
        - Sugerencias de mejora
        
        Texto:
        {text[:self.max_text_length]}
        """
        return base_prompt
    
    def _build_image_analysis_prompt(self, analysis_type: str) -> str:
        """Construye prompt para análisis de imágenes"""
        return f"""
        Analiza esta imagen científica con un enfoque {analysis_type}.
        
        Describe:
        1. Tipo de visualización (gráfico, diagrama, fotografía, etc.)
        2. Elementos clave visibles
        3. Datos o información presentada
        4. Calidad y claridad de la presentación
        5. Interpretación científica
        6. Posibles mejoras en la visualización
        """
    
    async def _analyze_with_local_models(self, text: str) -> AnalyzeWithLocalModelsResult:
        """Análisis con modelos locales"""
        try:
            results = {}
            
            # Análisis de sentimientos
            if "sentiment" in self.local_models:
                sentiment = await asyncio.to_thread(
                    self.local_models["sentiment"],
                    text[:512]  # Límite del modelo
                )
                results["sentiment"] = sentiment
            
            # Estadísticas básicas del texto
            results["text_stats"] = {
                "length": len(text),
                "words": len(text.split()),
                "sentences": text.count('.') + text.count('!') + text.count('?'),
                "paragraphs": text.count('\n\n') + 1
            }
            
            return results
            
        except BiologyError as e:
            logger.error(f"Error en análisis local: {e}")
            return {"error": str(e)}
    
    async def _analyze_image_locally(self, image: Image.Image) -> AnalyzeImageLocallyResult:
        """Análisis local de imágenes"""
        try:
            # Convertir a array numpy
            img_array = np.array(image)
            
            # Estadísticas básicas
            stats = {
                "dimensions": image.size,
                "mode": image.mode,
                "mean_brightness": np.mean(img_array),
                "std_brightness": np.std(img_array)
            }
            
            # Detección de bordes (como proxy para complejidad) usando OpenCV si está disponible
            try:
                import cv2
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                edges = cv2.Canny(gray, 100, 200)
                stats["edge_density"] = np.sum(edges > 0) / edges.size
            except (ImportError, AttributeError):
                # Fallback: usar gradiente simple con numpy si OpenCV no funciona
                if len(img_array.shape) == 3:
                    gray = np.mean(img_array, axis=2)
                else:
                    gray = img_array
                
                # Gradiente simple como proxy para detección de bordes
                grad_x = np.gradient(gray, axis=1)
                grad_y = np.gradient(gray, axis=0)
                gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
                stats["edge_density"] = np.mean(gradient_magnitude > np.std(gradient_magnitude))
            
            return {"stats": stats}
            
        except BiologyError as e:
            logger.error(f"Error en análisis local de imagen: {e}")
            return {"error": str(e)}
    
    async def _synthesize_multimodal(
        self,
        text: str,
        images: List,
        text_analysis: Dict,
        image_analysis: Dict
    ) -> Dict[str, Any]:
        """Síntesis multimodal de texto e imágenes"""
        try:
            synthesis_prompt = f"""
            Basándote en el análisis de texto e imágenes proporcionado, 
            crea una síntesis coherente que integre ambos tipos de información.
            
            Análisis de texto: {json.dumps(text_analysis, indent=2)[:2000]}
            Análisis de imágenes: {json.dumps(image_analysis, indent=2)[:2000]}
            
            Proporciona:
            1. Coherencia entre texto e imágenes
            2. Complementariedad de la información
            3. Discrepancias identificadas
            4. Síntesis integrada
            """
            
            # Usar el modelo preferido para síntesis
            if self.anthropic_client:
                result = await self._analyze_with_claude(synthesis_prompt, "synthesis")
            elif self.openai_client:
                result = await self._analyze_with_gpt4(synthesis_prompt, "synthesis")
            else:
                result = {"content": "Síntesis no disponible - no hay modelos configurados"}
            
            return result
            
        except BiologyError as e:
            logger.error(f"Error en síntesis multimodal: {e}")
            return {"error": str(e)}
    
    async def _generate_scientific_insights(
        self,
        analysis_results: Dict,
        analysis_type: str
    ) -> Dict[str, Any]:
        """Genera insights científicos basados en el análisis completo"""
        try:
            insights = {
                "key_findings": [],
                "methodological_assessment": {},
                "reproducibility_score": 0.0,
                "innovation_level": "medium",
                "research_gaps": [],
                "future_directions": []
            }
            
            # Extraer hallazgos clave del análisis
            if "text_analysis" in analysis_results:
                text_content = str(analysis_results["text_analysis"])
                if "novel" in text_content.lower() or "innovative" in text_content.lower():
                    insights["innovation_level"] = "high"
                elif "standard" in text_content.lower() or "conventional" in text_content.lower():
                    insights["innovation_level"] = "low"
            
            # Calcular puntuación de reproducibilidad
            reproducibility_factors = []
            if "methodology" in str(analysis_results).lower():
                reproducibility_factors.append(0.3)
            if "data" in str(analysis_results).lower():
                reproducibility_factors.append(0.2)
            if "code" in str(analysis_results).lower():
                reproducibility_factors.append(0.3)
            if "statistical" in str(analysis_results).lower():
                reproducibility_factors.append(0.2)
            
            insights["reproducibility_score"] = sum(reproducibility_factors)
            
            return insights
            
        except BiologyError as e:
            logger.error(f"Error generando insights científicos: {e}")
            return {"error": str(e)}
    
    async def compare_scientific_approaches(
        self,
        documents: List[Dict[str, Any]],
        comparison_criteria: List[str] = None
    ) -> Dict[str, Any]:
        """Compara múltiples enfoques científicos"""
        try:
            if not comparison_criteria:
                comparison_criteria = [
                    "methodology",
                    "sample_size",
                    "statistical_power",
                    "reproducibility",
                    "innovation"
                ]
            
            comparison_results = {
                "documents_analyzed": len(documents),
                "criteria": comparison_criteria,
                "comparative_analysis": {},
                "ranking": [],
                "recommendations": []
            }
            
            # Analizar cada documento
            document_analyses = []
            for i, doc in enumerate(documents):
                analysis = await self.analyze_scientific_document(
                    doc.get("text", ""),
                    doc.get("images", []),
                    "comparative"
                )
                document_analyses.append({
                    "index": i,
                    "title": doc.get("title", f"Document {i+1}"),
                    "analysis": analysis
                })
            
            # Realizar comparación
            for criterion in comparison_criteria:
                comparison_results["comparative_analysis"][criterion] = await self._compare_by_criterion(
                    document_analyses, criterion
                )
            
            return comparison_results
            
        except BiologyError as e:
            logger.error(f"Error en comparación de enfoques científicos: {e}")
            return {"error": str(e)}
    
    async def _compare_by_criterion(
        self,
        document_analyses: List[Dict],
        criterion: str
    ) -> Dict[str, Any]:
        """Compara documentos por un criterio específico"""
        try:
            comparison = {
                "criterion": criterion,
                "scores": {},
                "analysis": "",
                "best_performer": None
            }
            
            # Asignar puntuaciones basadas en el análisis
            for doc in document_analyses:
                analysis_text = str(doc["analysis"]).lower()
                score = 0.5  # Puntuación base
                
                # Criterios específicos
                if criterion == "methodology":
                    if "rigorous" in analysis_text or "systematic" in analysis_text:
                        score += 0.3
                    if "controlled" in analysis_text:
                        score += 0.2
                elif criterion == "reproducibility":
                    score = doc["analysis"].get("scientific_insights", {}).get("reproducibility_score", 0.5)
                elif criterion == "innovation":
                    innovation_level = doc["analysis"].get("scientific_insights", {}).get("innovation_level", "medium")
                    score = {"low": 0.3, "medium": 0.6, "high": 0.9}.get(innovation_level, 0.5)
                
                comparison["scores"][doc["title"]] = min(1.0, score)
            
            # Identificar mejor desempeño
            if comparison["scores"]:
                comparison["best_performer"] = max(
                    comparison["scores"].items(),
                    key=lambda x: x[1]
                )[0]
            
            return comparison
            
        except BiologyError as e:
            logger.error(f"Error comparando por criterio {criterion}: {e}")
            return {"error": str(e)}
    
    async def generate_research_hypothesis(
        self,
        research_context: str,
        existing_literature: List[str] = None,
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Genera hipótesis de investigación basadas en contexto y literatura"""
        try:
            hypothesis_prompt = f"""
            Basándote en el siguiente contexto de investigación, genera hipótesis científicas innovadoras y testables.
            
            Contexto: {research_context}
            
            Literatura existente: {existing_literature or 'No proporcionada'}
            
            Restricciones: {constraints or 'Ninguna'}
            
            Genera:
            1. 3-5 hipótesis principales
            2. Hipótesis nulas correspondientes
            3. Variables independientes y dependientes
            4. Metodología sugerida para cada hipótesis
            5. Predicciones específicas
            6. Métricas de evaluación
            """
            
            # Usar el mejor modelo disponible
            if self.anthropic_client:
                result = await self._analyze_with_claude(hypothesis_prompt, "hypothesis_generation")
            elif self.openai_client:
                result = await self._analyze_with_gpt4(hypothesis_prompt, "hypothesis_generation")
            else:
                result = {"content": "Generación de hipótesis no disponible - no hay modelos configurados"}
            
            return {
                "research_context": research_context,
                "generated_hypotheses": result,
                "methodology_suggestions": {},
                "testability_assessment": {},
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except BiologyError as e:
            logger.error(f"Error generando hipótesis de investigación: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> HealthCheckResult:
        """Verifica el estado del servicio"""
        try:
            status = {
                "service": "MultimodalReasoningService",
                "status": "healthy",
                "components": {
                    "anthropic_client": bool(self.anthropic_client),
                    "openai_client": bool(self.openai_client),
                    "local_models": len(self.local_models)
                },
                "capabilities": [
                    "scientific_document_analysis",
                    "multimodal_synthesis",
                    "image_analysis",
                    "comparative_analysis",
                    "hypothesis_generation"
                ]
            }
            
            # Test básico de conectividad
            if self.anthropic_client:
                try:
                    await asyncio.to_thread(
                        self.anthropic_client.messages.create,
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "Test"}]
                    )
                    status["components"]["anthropic_connectivity"] = True
                except BiologyError as e:
                    logger.debug(f"Anthropic connectivity test failed: {e}")
                    status["components"]["anthropic_connectivity"] = False
            
            return status
            
        except BiologyError as e:
            return {
                "service": "MultimodalReasoningService",
                "status": "unhealthy",
                "error": str(e)
            }
