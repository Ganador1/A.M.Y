# Multimodal Scientific Reasoning Service

## Alcance
- Servicio: `MultimodalReasoningService` (`app/services/scientific_ai/multimodal_reasoning_service.py`).
- Propósito: Análisis avanzado de datos científicos que combinan texto, imágenes (microscopía, gráficos, diagramas) y datos estructurados.
- Integración: Conecta con modelos de lenguaje de última generación (SOTA) como Claude 3.5 Sonnet y GPT-4V.

## Capacidades
- **Análisis de Imágenes Científicas**: Interpretación de resultados visuales de experimentos (ej. placas de Petri, espectrogramas).
- **Extracción de Datos de Gráficos**: Conversión de representaciones visuales de datos en valores numéricos estructurados.
- **Razonamiento Interdisciplinario**: Correlación de hallazgos visuales con literatura científica y bases de datos.
- **Generación de Hipótesis Visuales**: Propuesta de explicaciones para fenómenos observados en imágenes.

## Modelos y Proveedores
- **Anthropic**: Claude 3.5 Sonnet (Optimizado para razonamiento técnico y visión).
- **OpenAI**: GPT-4o / GPT-4V.
- **Local (Ollama)**: Soporte experimental para modelos multimodales locales como LLaVA.

## Acciones Principales

### `analyze_scientific_image`
Analiza una imagen con un contexto de investigación específico.
- **Entrada**:
  - `image_path` (str): Ruta al archivo de imagen.
  - `prompt` (str): Pregunta o instrucción específica.
  - `domain` (str): Dominio científico (biology, physics, etc.).
- **Salida**:
  - `analysis` (str): Descripción técnica detallada.
  - `detected_entities` (List): Elementos científicos identificados.

### `reason_over_multimodal_context`
Combina múltiples imágenes y documentos para un razonamiento complejo.
- **Entrada**:
  - `images` (List[str]): Lista de rutas de imágenes.
  - `documents` (List[str]): Textos o papers relacionados.
- **Salida**:
  - `synthesis` (str): Conclusión integrada.

## Ejemplo de Uso
```python
service = MultimodalReasoningService(provider="anthropic")
result = await service.analyze_scientific_image(
    image_path="data/microscopy/cell_sample_01.png",
    prompt="Identifica anomalías en la morfología celular y sugiere posibles causas.",
    domain="biology"
)
print(result['analysis'])
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_multimodal_reasoning_service.py`
