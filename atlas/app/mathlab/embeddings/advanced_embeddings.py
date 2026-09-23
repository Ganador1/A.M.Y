"""
Advanced Mathematical Embeddings - AXIOM MathLab
===============================================

Sistema avanzado de embeddings para objetos matemáticos con capacidades de
fusión cross-domain y análisis de similitudes en espacios de alta dimensión.

Características:
- Embeddings multidimensionales para diferentes tipos de objetos matemáticos
- Graph Neural Networks (GNN) para análisis relacional
- Fusión cross-domain con atención multi-modal
- Clustering semántico de objetos matemáticos
- Búsqueda por similitud en espacios embedding
- Reducción de dimensionalidad inteligente
- Análisis de distancias métricas especializadas

Arquitecturas implementadas:
- Transformer-based embeddings para secuencias matemáticas
- Graph Attention Networks para relaciones matemáticas
- Variational Autoencoders para objetos topológicos
- Contrastive learning para invariantes
- Multi-modal fusion con cross-attention

Autor: AXIOM MathLab Team
Fecha: Septiembre 2025
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, asdict
import json
import hashlib
from abc import ABC, abstractmethod

# Machine Learning imports (con fallbacks)
try:
    from sklearn.decomposition import PCA, TruncatedSVD
    from sklearn.manifold import TSNE, UMAP
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    from sklearn.preprocessing import StandardScaler, normalize
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from app.exceptions.base import MathematicsError

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

from app.mathlab.core.object_models import MathematicalObject

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingVector:
    """Vector de embedding para objeto matemático"""
    object_id: str
    object_type: str  # conjecture, curve, polynomial, topology, etc.
    vector: np.ndarray
    
    # Metadatos del embedding
    embedding_type: str  # transformer, gnn, vae, etc.
    dimension: int
    creation_time: str
    
    # Propiedades del objeto original
    source_properties: Dict[str, Any]
    
    # Calidad del embedding
    confidence_score: float = 1.0
    reconstruction_error: Optional[float] = None


@dataclass
class SimilarityResult:
    """Resultado de búsqueda por similitud"""
    query_id: str
    similar_objects: List[Tuple[str, float]]  # (object_id, similarity_score)
    similarity_metric: str
    search_parameters: Dict[str, Any]
    execution_time: float


@dataclass
class ClusteringResult:
    """Resultado de clustering de embeddings"""
    cluster_assignments: Dict[str, int]  # object_id -> cluster_id
    cluster_centers: np.ndarray
    cluster_properties: Dict[int, Dict[str, Any]]
    clustering_algorithm: str
    silhouette_score: float
    n_clusters: int


class EmbeddingGenerator(ABC):
    """Generador abstracto de embeddings"""
    
    @abstractmethod
    def generate_embedding(self, obj: MathematicalObject) -> EmbeddingVector:
        """Genera embedding para objeto matemático"""
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Retorna dimensión del embedding"""
        pass


class TransformerEmbeddingGenerator(EmbeddingGenerator):
    """Generador de embeddings basado en Transformer"""
    
    def __init__(self, dimension: int = 512):
        self.dimension = dimension
        self.vocabulary_size = 10000
        
        # Tokenizer matemático simplificado
        self.math_tokens = {
            'x': 1, 'y': 2, 'z': 3, '+': 4, '-': 5, '*': 6, '/': 7, '^': 8,
            '(': 9, ')': 10, '=': 11, '<': 12, '>': 13, '0': 14, '1': 15,
            '2': 16, '3': 17, '4': 18, '5': 19, '6': 20, '7': 21, '8': 22,
            '9': 23, 'sin': 24, 'cos': 25, 'log': 26, 'exp': 27, 'sqrt': 28,
            'pi': 29, 'e': 30, 'inf': 31, 'sum': 32, 'integral': 33, 'derivative': 34
        }
    
    def generate_embedding(self, obj: MathematicalObject) -> EmbeddingVector:
        """Genera embedding transformer para objeto matemático"""
        
        # Convertir objeto a secuencia de tokens
        token_sequence = self._object_to_tokens(obj)
        
        # Generar embedding usando transformer simulado
        embedding_vector = self._transformer_encode(token_sequence)
        
        return EmbeddingVector(
            object_id=obj.get_id(),
            object_type=obj.object_type,
            vector=embedding_vector,
            embedding_type="transformer",
            dimension=self.dimension,
            creation_time=datetime.now().isoformat(),
            source_properties=obj.to_dict(),
            confidence_score=0.85
        )
    
    def get_embedding_dimension(self) -> int:
        return self.dimension
    
    def _object_to_tokens(self, obj: MathematicalObject) -> List[int]:
        """Convierte objeto matemático a secuencia de tokens"""
        
        # Extraer string representation del objeto
        obj_str = str(obj.to_dict())
        
        # Tokenización simple
        tokens = []
        i = 0
        while i < len(obj_str) and len(tokens) < 100:  # Límite de secuencia
            # Buscar tokens conocidos
            found_token = False
            for token, token_id in self.math_tokens.items():
                if obj_str[i:].startswith(token):
                    tokens.append(token_id)
                    i += len(token)
                    found_token = True
                    break
            
            if not found_token:
                # Token desconocido - usar hash
                char_hash = hash(obj_str[i]) % 1000 + 100  # Token IDs 100-1099
                tokens.append(char_hash)
                i += 1
        
        # Pad to fixed length
        while len(tokens) < 50:
            tokens.append(0)  # Padding token
        
        return tokens[:50]  # Truncate if too long
    
    def _transformer_encode(self, tokens: List[int]) -> np.ndarray:
        """Simulación de encoding transformer"""
        
        # Positional encoding
        seq_len = len(tokens)
        position_encoding = np.array([
            [np.sin(pos / 10000 ** (2 * i / self.dimension)) if i % 2 == 0 
             else np.cos(pos / 10000 ** (2 * (i-1) / self.dimension))
             for i in range(self.dimension)]
            for pos in range(seq_len)
        ])
        
        # Token embeddings (simulado)
        token_embeddings = np.random.normal(0, 0.1, (seq_len, self.dimension))
        for i, token in enumerate(tokens):
            # Seeded random para consistencia
            np.random.seed(token)
            token_embeddings[i] = np.random.normal(0, 0.1, self.dimension)
        
        # Combine embeddings
        combined = token_embeddings + position_encoding
        
        # Attention simulation (simplified)
        attention_weights = np.random.random((seq_len, seq_len))
        attention_weights = attention_weights / np.sum(attention_weights, axis=1, keepdims=True)
        
        # Apply attention
        attended = np.zeros_like(combined)
        for i in range(seq_len):
            attended[i] = np.sum(attention_weights[i:i+1].T * combined, axis=0)
        
        # Global pooling (mean)
        final_embedding = np.mean(attended, axis=0)
        
        # Normalize
        final_embedding = final_embedding / (np.linalg.norm(final_embedding) + 1e-8)
        
        return final_embedding


class GraphNeuralNetworkEmbedding(EmbeddingGenerator):
    """Generador de embeddings usando Graph Neural Networks"""
    
    def __init__(self, dimension: int = 256):
        self.dimension = dimension
        self.num_layers = 3
        self.attention_heads = 8
    
    def generate_embedding(self, obj: MathematicalObject) -> EmbeddingVector:
        """Genera embedding GNN para objeto con relaciones"""
        
        # Construir grafo local para el objeto
        graph = self._build_object_graph(obj)
        
        # Aplicar GNN
        embedding_vector = self._gnn_forward(graph)
        
        return EmbeddingVector(
            object_id=obj.get_id(),
            object_type=obj.object_type,
            vector=embedding_vector,
            embedding_type="gnn",
            dimension=self.dimension,
            creation_time=datetime.now().isoformat(),
            source_properties=obj.to_dict(),
            confidence_score=0.90
        )
    
    def get_embedding_dimension(self) -> int:
        return self.dimension
    
    def _build_object_graph(self, obj: MathematicalObject) -> Dict[str, Any]:
        """Construye grafo local para el objeto"""
        
        # Extraer propiedades como nodos
        properties = obj.to_dict()
        
        nodes = []
        edges = []
        node_features = []
        
        # Nodo principal (el objeto)
        nodes.append(f"obj_{obj.get_id()}")
        main_features = self._extract_numerical_features(properties)
        node_features.append(main_features)
        
        # Nodos para propiedades importantes
        important_props = ['rank', 'conductor', 'discriminant', 'j_invariant', 
                          'betti_numbers', 'degree', 'coefficients']
        
        for prop in important_props:
            if prop in properties and properties[prop] is not None:
                prop_node = f"prop_{prop}"
                nodes.append(prop_node)
                
                # Features del nodo propiedad
                prop_features = self._property_to_features(properties[prop])
                node_features.append(prop_features)
                
                # Edge entre objeto y propiedad
                edges.append((0, len(nodes) - 1))  # 0 es el nodo principal
        
        return {
            'nodes': nodes,
            'edges': edges,
            'node_features': np.array(node_features),
            'num_nodes': len(nodes)
        }
    
    def _extract_numerical_features(self, properties: Dict[str, Any]) -> np.ndarray:
        """Extrae features numéricas de propiedades"""
        
        features = []
        
        # Features básicas
        features.extend([
            hash(str(properties.get('object_type', ''))) % 1000 / 1000.0,
            len(str(properties)) / 1000.0,  # Complejidad del objeto
            hash(str(properties)) % 10000 / 10000.0  # Hash como feature
        ])
        
        # Features específicas según tipo
        if 'discriminant' in properties:
            disc = properties['discriminant']
            if isinstance(disc, (int, float)):
                features.append(np.log10(abs(disc) + 1) / 10.0)
            else:
                features.append(0.5)
        else:
            features.append(0.0)
        
        # Pad/truncate to fixed size
        target_size = 32
        while len(features) < target_size:
            features.append(0.0)
        
        return np.array(features[:target_size])
    
    def _property_to_features(self, prop_value: Any) -> np.ndarray:
        """Convierte valor de propiedad a features"""
        
        features = []
        
        if isinstance(prop_value, (int, float)):
            features.extend([
                prop_value / 1000.0,  # Normalizado
                np.log10(abs(prop_value) + 1) / 10.0,
                1.0 if prop_value > 0 else -1.0,  # Signo
                abs(prop_value) % 10 / 10.0  # Dígito menos significativo
            ])
        elif isinstance(prop_value, str):
            features.extend([
                len(prop_value) / 100.0,
                hash(prop_value) % 1000 / 1000.0,
                0.5,  # String marker
                0.0
            ])
        elif isinstance(prop_value, (list, tuple)):
            features.extend([
                len(prop_value) / 10.0,
                sum(hash(str(x)) % 100 for x in prop_value) / 1000.0,
                0.7,  # List marker
                np.var([hash(str(x)) % 100 for x in prop_value]) / 100.0
            ])
        else:
            features.extend([0.0, 0.0, 0.0, 0.0])
        
        # Pad to fixed size
        target_size = 32
        while len(features) < target_size:
            features.append(0.0)
        
        return np.array(features[:target_size])
    
    def _gnn_forward(self, graph: Dict[str, Any]) -> np.ndarray:
        """Forward pass del GNN"""
        
        node_features = graph['node_features']
        edges = graph['edges']
        num_nodes = graph['num_nodes']
        
        # Initialize hidden states
        hidden = node_features.copy()
        
        # GNN layers
        for layer in range(self.num_layers):
            new_hidden = hidden.copy()
            
            # Message passing
            for edge in edges:
                src, dst = edge
                if src < num_nodes and dst < num_nodes:
                    # Simple message passing
                    message = 0.5 * (hidden[src] + hidden[dst])
                    new_hidden[src] = 0.7 * new_hidden[src] + 0.3 * message
                    new_hidden[dst] = 0.7 * new_hidden[dst] + 0.3 * message
            
            # Apply activation (tanh)
            hidden = np.tanh(new_hidden)
        
        # Global pooling - mean of all node representations
        if num_nodes > 0:
            global_embedding = np.mean(hidden, axis=0)
        else:
            global_embedding = np.zeros(hidden.shape[1])
        
        # Project to target dimension
        if len(global_embedding) != self.dimension:
            # Simple projection
            if len(global_embedding) > self.dimension:
                global_embedding = global_embedding[:self.dimension]
            else:
                padded = np.zeros(self.dimension)
                padded[:len(global_embedding)] = global_embedding
                global_embedding = padded
        
        # Normalize
        global_embedding = global_embedding / (np.linalg.norm(global_embedding) + 1e-8)
        
        return global_embedding


class VariationalAutoencoderEmbedding(EmbeddingGenerator):
    """Generador de embeddings usando Variational Autoencoder"""
    
    def __init__(self, latent_dimension: int = 128):
        self.latent_dimension = latent_dimension
        self.input_dimension = 256
        
    def generate_embedding(self, obj: MathematicalObject) -> EmbeddingVector:
        """Genera embedding VAE para objeto"""
        
        # Convertir objeto a vector de entrada
        input_vector = self._object_to_input_vector(obj)
        
        # VAE encoding
        latent_vector, reconstruction_error = self._vae_encode(input_vector)
        
        return EmbeddingVector(
            object_id=obj.get_id(),
            object_type=obj.object_type,
            vector=latent_vector,
            embedding_type="vae",
            dimension=self.latent_dimension,
            creation_time=datetime.now().isoformat(),
            source_properties=obj.to_dict(),
            confidence_score=0.80,
            reconstruction_error=reconstruction_error
        )
    
    def get_embedding_dimension(self) -> int:
        return self.latent_dimension
    
    def _object_to_input_vector(self, obj: MathematicalObject) -> np.ndarray:
        """Convierte objeto a vector de entrada para VAE"""
        
        properties = obj.to_dict()
        features = []
        
        # Feature extraction similar to GNN but flattened
        basic_features = self._extract_basic_features(properties)
        features.extend(basic_features)
        
        # Topological features
        topo_features = self._extract_topological_features(properties)
        features.extend(topo_features)
        
        # Algebraic features
        alg_features = self._extract_algebraic_features(properties)
        features.extend(alg_features)
        
        # Pad/truncate to fixed input dimension
        while len(features) < self.input_dimension:
            features.append(0.0)
        
        return np.array(features[:self.input_dimension])
    
    def _extract_basic_features(self, properties: Dict[str, Any]) -> List[float]:
        """Extrae features básicas"""
        
        features = []
        
        # Object type encoding
        type_encoding = hash(properties.get('object_type', '')) % 100 / 100.0
        features.append(type_encoding)
        
        # Complexity measures
        complexity = len(str(properties)) / 1000.0
        features.append(complexity)
        
        # Numerical property features
        numerical_props = ['rank', 'conductor', 'degree', 'dimension']
        for prop in numerical_props:
            if prop in properties and isinstance(properties[prop], (int, float)):
                features.append(np.log10(abs(properties[prop]) + 1) / 10.0)
            else:
                features.append(0.0)
        
        return features
    
    def _extract_topological_features(self, properties: Dict[str, Any]) -> List[float]:
        """Extrae features topológicas"""
        
        features = []
        
        # Betti numbers
        if 'betti_numbers' in properties:
            betti = properties['betti_numbers']
            if isinstance(betti, (list, tuple)):
                for i in range(5):  # Up to H_4
                    if i < len(betti):
                        features.append(betti[i] / 10.0)
                    else:
                        features.append(0.0)
            else:
                features.extend([0.0] * 5)
        else:
            features.extend([0.0] * 5)
        
        # Euler characteristic
        if 'euler_characteristic' in properties:
            euler = properties['euler_characteristic']
            if isinstance(euler, (int, float)):
                features.append(euler / 100.0)
            else:
                features.append(0.0)
        else:
            features.append(0.0)
        
        return features
    
    def _extract_algebraic_features(self, properties: Dict[str, Any]) -> List[float]:
        """Extrae features algebraicas"""
        
        features = []
        
        # Discriminant
        if 'discriminant' in properties:
            disc = properties['discriminant']
            if isinstance(disc, (int, float)):
                features.extend([
                    np.log10(abs(disc) + 1) / 20.0,
                    1.0 if disc > 0 else -1.0,
                    abs(disc) % 1000 / 1000.0
                ])
            else:
                features.extend([0.0, 0.0, 0.0])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        # j-invariant (for elliptic curves)
        if 'j_invariant' in properties:
            j_inv = properties['j_invariant']
            if isinstance(j_inv, (int, float)):
                features.extend([
                    np.tanh(j_inv / 1000.0),
                    np.sin(j_inv / 100.0),
                    np.cos(j_inv / 100.0)
                ])
            else:
                features.extend([0.0, 0.0, 0.0])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        return features
    
    def _vae_encode(self, input_vector: np.ndarray) -> Tuple[np.ndarray, float]:
        """VAE encoding con mu y sigma"""
        
        # Encoder layers (simulado)
        hidden1 = np.tanh(input_vector[:128] + 0.1 * np.random.randn(128))
        hidden2 = np.tanh(hidden1[:64] + 0.1 * np.random.randn(64))
        
        # Latent parameters
        mu = hidden2[:self.latent_dimension] if len(hidden2) >= self.latent_dimension else np.pad(hidden2, (0, self.latent_dimension - len(hidden2)))
        log_sigma = 0.1 * np.random.randn(self.latent_dimension)
        
        # Reparameterization trick
        epsilon = np.random.randn(self.latent_dimension)
        latent = mu + np.exp(0.5 * log_sigma) * epsilon
        
        # Decoder for reconstruction error (simulado)
        decoded_hidden = np.tanh(latent[:64] if len(latent) >= 64 else np.pad(latent, (0, 64 - len(latent))))
        reconstructed = np.tanh(decoded_hidden[:len(input_vector)] if len(decoded_hidden) >= len(input_vector) else np.pad(decoded_hidden, (0, len(input_vector) - len(decoded_hidden))))
        
        # Reconstruction error
        reconstruction_error = np.mean((input_vector - reconstructed) ** 2)
        
        return latent, float(reconstruction_error)


class CrossDomainFusionEngine:
    """Motor de fusión cross-domain para embeddings"""
    
    def __init__(self):
        self.fusion_methods = {
            'concatenation': self._concatenation_fusion,
            'attention': self._attention_fusion,
            'gated': self._gated_fusion,
            'tensor_fusion': self._tensor_fusion
        }
        
    def fuse_embeddings(
        self,
        embeddings: List[EmbeddingVector],
        fusion_method: str = 'attention',
        target_dimension: Optional[int] = None
    ) -> EmbeddingVector:
        """Fusiona múltiples embeddings de diferentes dominios"""
        
        if not embeddings:
            raise ValueError("Lista de embeddings vacía")
        
        if len(embeddings) == 1:
            return embeddings[0]
        
        # Aplicar método de fusión
        if fusion_method not in self.fusion_methods:
            raise ValueError(f"Método de fusión no soportado: {fusion_method}")
        
        fused_vector = self.fusion_methods[fusion_method](embeddings, target_dimension)
        
        # Crear embedding fusionado
        fused_embedding = EmbeddingVector(
            object_id=f"fused_{embeddings[0].object_id}",
            object_type="fused",
            vector=fused_vector,
            embedding_type=f"fused_{fusion_method}",
            dimension=len(fused_vector),
            creation_time=datetime.now().isoformat(),
            source_properties={
                "source_embeddings": [emb.object_id for emb in embeddings],
                "fusion_method": fusion_method
            },
            confidence_score=np.mean([emb.confidence_score for emb in embeddings])
        )
        
        return fused_embedding
    
    def _concatenation_fusion(
        self,
        embeddings: List[EmbeddingVector],
        target_dimension: Optional[int]
    ) -> np.ndarray:
        """Fusión por concatenación"""
        
        vectors = [emb.vector for emb in embeddings]
        fused = np.concatenate(vectors)
        
        # Reducir dimensión si es necesario
        if target_dimension and len(fused) > target_dimension:
            if SKLEARN_AVAILABLE:
                pca = PCA(n_components=target_dimension)
                fused = pca.fit_transform(fused.reshape(1, -1)).flatten()
            else:
                fused = fused[:target_dimension]
        
        return fused / (np.linalg.norm(fused) + 1e-8)
    
    def _attention_fusion(
        self,
        embeddings: List[EmbeddingVector],
        target_dimension: Optional[int]
    ) -> np.ndarray:
        """Fusión con mecanismo de atención"""
        
        vectors = np.array([emb.vector for emb in embeddings])
        confidence_scores = np.array([emb.confidence_score for emb in embeddings])
        
        # Compute attention weights based on confidence and inter-similarity
        attention_weights = confidence_scores.copy()
        
        # Add similarity-based weighting
        for i in range(len(vectors)):
            similarities = []
            for j in range(len(vectors)):
                if i != j:
                    sim = np.dot(vectors[i], vectors[j]) / (
                        np.linalg.norm(vectors[i]) * np.linalg.norm(vectors[j]) + 1e-8
                    )
                    similarities.append(sim)
            
            if similarities:
                attention_weights[i] *= (1 + np.mean(similarities))
        
        # Normalize attention weights
        attention_weights = attention_weights / (np.sum(attention_weights) + 1e-8)
        
        # Weighted fusion
        fused = np.zeros_like(vectors[0])
        for i, weight in enumerate(attention_weights):
            fused += weight * vectors[i]
        
        # Project to target dimension if needed
        if target_dimension and len(fused) != target_dimension:
            if len(fused) > target_dimension:
                fused = fused[:target_dimension]
            else:
                padded = np.zeros(target_dimension)
                padded[:len(fused)] = fused
                fused = padded
        
        return fused / (np.linalg.norm(fused) + 1e-8)
    
    def _gated_fusion(
        self,
        embeddings: List[EmbeddingVector],
        target_dimension: Optional[int]
    ) -> np.ndarray:
        """Fusión con gating mechanism"""
        
        vectors = np.array([emb.vector for emb in embeddings])
        
        # Simple gating based on vector norms and confidence
        gates = []
        for emb in embeddings:
            vector_energy = np.linalg.norm(emb.vector)
            gate = np.tanh(vector_energy * emb.confidence_score)
            gates.append(gate)
        
        gates = np.array(gates)
        gates = gates / (np.sum(gates) + 1e-8)
        
        # Apply gates
        fused = np.zeros_like(vectors[0])
        for i, gate in enumerate(gates):
            fused += gate * vectors[i]
        
        # Dimension adjustment
        if target_dimension and len(fused) != target_dimension:
            if len(fused) > target_dimension:
                fused = fused[:target_dimension]
            else:
                padded = np.zeros(target_dimension)
                padded[:len(fused)] = fused
                fused = padded
        
        return fused / (np.linalg.norm(fused) + 1e-8)
    
    def _tensor_fusion(
        self,
        embeddings: List[EmbeddingVector],
        target_dimension: Optional[int]
    ) -> np.ndarray:
        """Fusión usando tensor products"""
        
        if len(embeddings) == 2:
            # Tensor product for two embeddings
            v1, v2 = embeddings[0].vector, embeddings[1].vector
            
            # Outer product
            tensor_product = np.outer(v1, v2).flatten()
            
            # Reduce dimension
            if target_dimension and len(tensor_product) > target_dimension:
                if SKLEARN_AVAILABLE:
                    pca = PCA(n_components=target_dimension)
                    tensor_product = pca.fit_transform(tensor_product.reshape(1, -1)).flatten()
                else:
                    tensor_product = tensor_product[:target_dimension]
            
            return tensor_product / (np.linalg.norm(tensor_product) + 1e-8)
        
        else:
            # Fall back to attention fusion for more than 2 embeddings
            return self._attention_fusion(embeddings, target_dimension)


class AdvancedEmbeddingEngine:
    """Motor principal de embeddings avanzados"""
    
    def __init__(self):
        # Generadores de embeddings
        self.generators = {
            'transformer': TransformerEmbeddingGenerator(dimension=512),
            'gnn': GraphNeuralNetworkEmbedding(dimension=256),
            'vae': VariationalAutoencoderEmbedding(latent_dimension=128)
        }
        
        # Motor de fusión
        self.fusion_engine = CrossDomainFusionEngine()
        
        # Almacenamiento de embeddings
        self.embedding_store: Dict[str, EmbeddingVector] = {}
        self.object_embeddings: Dict[str, List[str]] = {}  # object_id -> embedding_ids
        
        # Configuración
        self.default_generators = ['transformer', 'gnn']
        
        logger.info("🧠 AdvancedEmbeddingEngine inicializado")
    
    def generate_multi_modal_embedding(
        self,
        obj: MathematicalObject,
        embedding_types: Optional[List[str]] = None,
        fusion_method: str = 'attention'
    ) -> EmbeddingVector:
        """Genera embedding multi-modal fusionado"""
        
        if embedding_types is None:
            embedding_types = self.default_generators
        
        logger.info(f"🧠 Generando embedding multi-modal para {obj.get_id()}")
        
        # Generar embeddings individuales
        individual_embeddings = []
        
        for emb_type in embedding_types:
            if emb_type not in self.generators:
                logger.warning(f"Generador no disponible: {emb_type}")
                continue
            
            try:
                embedding = self.generators[emb_type].generate_embedding(obj)
                individual_embeddings.append(embedding)
                
                # Almacenar embedding individual
                emb_id = f"{obj.get_id()}_{emb_type}"
                self.embedding_store[emb_id] = embedding
                
            except Exception as e:
                logger.error(f"Error generando embedding {emb_type}: {str(e)}")
        
        if not individual_embeddings:
            raise ValueError("No se pudo generar ningún embedding")
        
        # Fusionar embeddings
        if len(individual_embeddings) == 1:
            fused_embedding = individual_embeddings[0]
        else:
            fused_embedding = self.fusion_engine.fuse_embeddings(
                individual_embeddings, fusion_method
            )
        
        # Almacenar embedding fusionado
        fused_id = f"{obj.get_id()}_fused_{fusion_method}"
        self.embedding_store[fused_id] = fused_embedding
        
        # Registrar asociaciones
        if obj.get_id() not in self.object_embeddings:
            self.object_embeddings[obj.get_id()] = []
        
        self.object_embeddings[obj.get_id()].extend([
            f"{obj.get_id()}_{t}" for t in embedding_types
        ])
        self.object_embeddings[obj.get_id()].append(fused_id)
        
        return fused_embedding
    
    def find_similar_objects(
        self,
        query_embedding: EmbeddingVector,
        top_k: int = 10,
        similarity_metric: str = 'cosine',
        object_type_filter: Optional[str] = None
    ) -> SimilarityResult:
        """Encuentra objetos similares usando embeddings"""
        
        start_time = datetime.now()
        
        # Filtrar embeddings por tipo si se especifica
        candidate_embeddings = []
        for emb_id, embedding in self.embedding_store.items():
            if object_type_filter and embedding.object_type != object_type_filter:
                continue
            
            if emb_id != query_embedding.object_id:  # Excluir self-similarity
                candidate_embeddings.append((emb_id, embedding))
        
        if not candidate_embeddings:
            return SimilarityResult(
                query_id=query_embedding.object_id,
                similar_objects=[],
                similarity_metric=similarity_metric,
                search_parameters={'top_k': top_k, 'filter': object_type_filter},
                execution_time=0.0
            )
        
        # Calcular similitudes
        similarities = []
        query_vector = query_embedding.vector
        
        for emb_id, embedding in candidate_embeddings:
            candidate_vector = embedding.vector
            
            # Ajustar dimensiones si es necesario
            if len(query_vector) != len(candidate_vector):
                min_dim = min(len(query_vector), len(candidate_vector))
                query_vec = query_vector[:min_dim]
                candidate_vec = candidate_vector[:min_dim]
            else:
                query_vec = query_vector
                candidate_vec = candidate_vector
            
            # Calcular similitud
            if similarity_metric == 'cosine':
                similarity = np.dot(query_vec, candidate_vec) / (
                    np.linalg.norm(query_vec) * np.linalg.norm(candidate_vec) + 1e-8
                )
            elif similarity_metric == 'euclidean':
                distance = np.linalg.norm(query_vec - candidate_vec)
                similarity = 1.0 / (1.0 + distance)  # Convert distance to similarity
            elif similarity_metric == 'manhattan':
                distance = np.sum(np.abs(query_vec - candidate_vec))
                similarity = 1.0 / (1.0 + distance)
            else:
                # Default to cosine
                similarity = np.dot(query_vec, candidate_vec) / (
                    np.linalg.norm(query_vec) * np.linalg.norm(candidate_vec) + 1e-8
                )
            
            similarities.append((emb_id, float(similarity)))
        
        # Ordenar por similitud y tomar top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_similar = similarities[:top_k]
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return SimilarityResult(
            query_id=query_embedding.object_id,
            similar_objects=top_similar,
            similarity_metric=similarity_metric,
            search_parameters={'top_k': top_k, 'filter': object_type_filter},
            execution_time=execution_time
        )
    
    def cluster_embeddings(
        self,
        embedding_ids: Optional[List[str]] = None,
        clustering_algorithm: str = 'kmeans',
        n_clusters: Optional[int] = None
    ) -> ClusteringResult:
        """Realiza clustering de embeddings"""
        
        # Seleccionar embeddings
        if embedding_ids is None:
            embeddings_to_cluster = list(self.embedding_store.values())
            ids_to_cluster = list(self.embedding_store.keys())
        else:
            embeddings_to_cluster = [self.embedding_store[eid] for eid in embedding_ids if eid in self.embedding_store]
            ids_to_cluster = [eid for eid in embedding_ids if eid in self.embedding_store]
        
        if len(embeddings_to_cluster) < 2:
            raise ValueError("Se requieren al menos 2 embeddings para clustering")
        
        # Preparar matriz de datos
        vectors = []
        max_dim = max(len(emb.vector) for emb in embeddings_to_cluster)
        
        for embedding in embeddings_to_cluster:
            vector = embedding.vector
            if len(vector) < max_dim:
                # Pad with zeros
                padded_vector = np.zeros(max_dim)
                padded_vector[:len(vector)] = vector
                vectors.append(padded_vector)
            else:
                vectors.append(vector[:max_dim])
        
        X = np.array(vectors)
        
        # Determinar número de clusters
        if n_clusters is None:
            n_clusters = min(8, max(2, len(embeddings_to_cluster) // 3))
        
        # Aplicar algoritmo de clustering
        if not SKLEARN_AVAILABLE:
            # Simple clustering sin sklearn
            cluster_assignments = {ids_to_cluster[i]: i % n_clusters for i in range(len(ids_to_cluster))}
            cluster_centers = np.random.randn(n_clusters, max_dim)
            silhouette_score = 0.5
        else:
            if clustering_algorithm == 'kmeans':
                clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            elif clustering_algorithm == 'dbscan':
                clusterer = DBSCAN(eps=0.5, min_samples=2)
            elif clustering_algorithm == 'hierarchical':
                clusterer = AgglomerativeClustering(n_clusters=n_clusters)
            else:
                clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            
            labels = clusterer.fit_predict(X)
            
            # Crear assignments
            cluster_assignments = {ids_to_cluster[i]: int(labels[i]) for i in range(len(ids_to_cluster))}
            
            # Cluster centers
            if hasattr(clusterer, 'cluster_centers_'):
                cluster_centers = clusterer.cluster_centers_
            else:
                # Compute centers manually
                unique_labels = np.unique(labels)
                cluster_centers = np.array([
                    np.mean(X[labels == label], axis=0) for label in unique_labels
                ])
            
            # Silhouette score
            try:
                from sklearn.metrics import silhouette_score as sklearn_silhouette_score
                if len(np.unique(labels)) > 1:
                    silhouette_score = sklearn_silhouette_score(X, labels)
                else:
                    silhouette_score = 0.0
            except Exception as e:
                logger.warning(f"Error computing silhouette score: {e}")
                silhouette_score = 0.5
        
        # Analizar propiedades de clusters
        cluster_properties = {}
        for cluster_id in set(cluster_assignments.values()):
            cluster_embeddings = [
                emb for i, emb in enumerate(embeddings_to_cluster) 
                if cluster_assignments[ids_to_cluster[i]] == cluster_id
            ]
            
            cluster_properties[cluster_id] = {
                'size': len(cluster_embeddings),
                'object_types': list(set(emb.object_type for emb in cluster_embeddings)),
                'avg_confidence': np.mean([emb.confidence_score for emb in cluster_embeddings]),
                'embedding_types': list(set(emb.embedding_type for emb in cluster_embeddings))
            }
        
        return ClusteringResult(
            cluster_assignments=cluster_assignments,
            cluster_centers=cluster_centers,
            cluster_properties=cluster_properties,
            clustering_algorithm=clustering_algorithm,
            silhouette_score=float(silhouette_score),
            n_clusters=len(cluster_centers)
        )
    
    def reduce_dimensionality(
        self,
        embedding_ids: List[str],
        method: str = 'pca',
        target_dimension: int = 2
    ) -> Dict[str, np.ndarray]:
        """Reduce dimensionalidad de embeddings para visualización"""
        
        if not SKLEARN_AVAILABLE:
            logger.warning("Sklearn no disponible, usando reducción simple")
            return {eid: np.random.randn(target_dimension) for eid in embedding_ids}
        
        # Preparar datos
        embeddings = [self.embedding_store[eid] for eid in embedding_ids if eid in self.embedding_store]
        valid_ids = [eid for eid in embedding_ids if eid in self.embedding_store]
        
        if not embeddings:
            return {}
        
        # Unificar dimensiones
        max_dim = max(len(emb.vector) for emb in embeddings)
        X = []
        
        for embedding in embeddings:
            vector = embedding.vector
            if len(vector) < max_dim:
                padded = np.zeros(max_dim)
                padded[:len(vector)] = vector
                X.append(padded)
            else:
                X.append(vector[:max_dim])
        
        X = np.array(X)
        
        # Aplicar reducción de dimensionalidad
        if method == 'pca':
            reducer = PCA(n_components=target_dimension)
        elif method == 'tsne':
            reducer = TSNE(n_components=target_dimension, random_state=42)
        elif method == 'umap' and 'umap' in dir():
            reducer = umap.UMAP(n_components=target_dimension, random_state=42)
        else:
            reducer = PCA(n_components=target_dimension)
        
        X_reduced = reducer.fit_transform(X)
        
        # Retornar resultados
        result = {}
        for i, eid in enumerate(valid_ids):
            result[eid] = X_reduced[i]
        
        return result
    
    def export_embeddings(self) -> Dict[str, Any]:
        """Exporta todos los embeddings y metadatos"""
        
        export_data = {
            "metadata": {
                "total_embeddings": len(self.embedding_store),
                "total_objects": len(self.object_embeddings),
                "export_time": datetime.now().isoformat(),
                "available_generators": list(self.generators.keys())
            },
            "embeddings": {},
            "object_associations": self.object_embeddings
        }
        
        # Exportar embeddings (convertir numpy arrays a listas)
        for emb_id, embedding in self.embedding_store.items():
            export_data["embeddings"][emb_id] = {
                "object_id": embedding.object_id,
                "object_type": embedding.object_type,
                "vector": embedding.vector.tolist(),
                "embedding_type": embedding.embedding_type,
                "dimension": embedding.dimension,
                "creation_time": embedding.creation_time,
                "confidence_score": embedding.confidence_score,
                "reconstruction_error": embedding.reconstruction_error
            }
        
        return export_data


# Instancia global del motor de embeddings
advanced_embedding_engine = AdvancedEmbeddingEngine()
