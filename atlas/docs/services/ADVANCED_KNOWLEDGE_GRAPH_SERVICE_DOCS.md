# Advanced Knowledge Graph Service

## Alcance
- Servicio: `AdvancedKnowledgeGraphService` (`app/services/advanced/advanced_knowledge_graph_service.py`).
- Propósito: Gestión inteligente y optimización de grafos de conocimiento científicos a gran escala.
- Implementación: Extensión de `KnowledgeGraphService` con algoritmos avanzados de teoría de grafos, clustering y pruning automático.

## Capacidades
- **Control de Crecimiento**: Monitoreo de la salud del grafo y prevención de la explosión combinatoria de nodos.
- **Pruning Inteligente**: Eliminación automática de nodos y aristas de baja relevancia o redundantes basada en métricas de centralidad.
- **Detección de Comunidades**: Identificación de clusters conceptuales y temas emergentes usando algoritmos como Louvain o Leiden.
- **Análisis de Calidad**: Evaluación de la densidad, conectividad y entropía de la distribución de grados.
- **Evolución Temporal**: Seguimiento de cómo cambia el conocimiento y las relaciones a lo largo del tiempo.

## Algoritmos y Métricas
- **Centralidad**: PageRank, Betweenness y Closeness para identificar nodos críticos.
- **Clustering**: K-Means y DBSCAN sobre embeddings semánticos de los nodos.
- **Information Theory**: Compresión del grafo minimizando la pérdida de información.

## Acciones Principales

### `monitor_growth_health`
Analiza el estado actual del grafo y detecta anomalías estructurales.
- **Salida**:
  - `metrics` (GraphQualityMetrics): Densidad, coeficiente de clustering, etc.
  - `recommendations` (List[str]): Acciones sugeridas (ej. "ejecutar pruning").

### `perform_intelligent_pruning`
Reduce el tamaño del grafo manteniendo los conceptos nucleares.
- **Entrada**:
  - `config` (PruningConfig): Criterios de eliminación.
- **Salida**:
  - `nodes_removed` (int).
  - `information_retention` (float): Porcentaje de conocimiento preservado.

### `detect_emerging_topics`
Identifica nuevas áreas de investigación basadas en la topología del grafo.
- **Salida**:
  - `topics` (List[Dict]): Descripción de comunidades densamente conectadas.

## Ejemplo de Uso
```python
from app.services.advanced.advanced_knowledge_graph_service import AdvancedKnowledgeGraphService

service = AdvancedKnowledgeGraphService()
health = service.monitor_growth_health()

if health.density > 0.05:
    service.perform_intelligent_pruning(max_nodes=5000)
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_advanced_knowledge_graph_service.py`
