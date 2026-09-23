> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="multimodal-scientific-reasoning-service"></a>
# Multimodal Scientific Reasoning Service

<a id="alcance"></a>
## Scope
- Service: `MultimodalReasoningService` (`app/services/scientific_ai/multimodal_reasoning_service.py`).
- Purpose: Advanced analysis of scientific data combining text, images (microscopy, graphs, diagrams), and structured data.
- Integration: Connects with state-of-the-art (SOTA) language models such as Claude 3.5 Sonnet and GPT-4V.

<a id="capacidades"></a>
## Capabilities
- **Scientific Image Analysis**: Interpretation of visual results from experiments (e.g., Petri dishes, spectrograms).
- **Data Extraction from Graphs**: Conversion of visual data representations into structured numerical values.
- **Interdisciplinary Reasoning**: Correlation of visual findings with scientific literature and databases.
- **Visual Hypothesis Generation**: Proposal of explanations for phenomena observed in images.

<a id="modelos-y-proveedores"></a>
## Models and Providers
- **Anthropic**: Claude 3.5 Sonnet (Optimized for technical reasoning and vision).
- **OpenAI**: GPT-4o / GPT-4V.
- **Local (Ollama)**: Experimental support for local multimodal models such as LLaVA.

<a id="acciones-principales"></a>
## Main Actions

<a id="analyze_scientific_image"></a>
### `analyze_scientific_image`
Analyzes an image with a specific research context.
- **Input**:
  - `image_path` (str): Path to the image file.
  - `prompt` (str): Specific question or instruction.
  - `domain` (str): Scientific domain (biology, physics, etc.).
- **Output**:
  - `analysis` (str): Detailed technical description.
  - `detected_entities` (List): Identified scientific elements.

<a id="reason_over_multimodal_context"></a>
### `reason_over_multimodal_context`
Combines multiple images and documents for complex reasoning.
- **Input**:
  - `images` (List[str]): List of image paths.
  - `documents` (List[str]): Related texts or papers.
- **Output**:
  - `synthesis` (str): Integrated conclusion.

<a id="ejemplo-de-uso"></a>
## Usage Example
```python
service = MultimodalReasoningService(provider="anthropic")
result = await service.analyze_scientific_image(
    image_path="data/microscopy/cell_sample_01.png",
    prompt="Identifica anomalías en la morfología celular y sugiere posibles causas.",
    domain="biology"
)
print(result['analysis'])
```

<a id="pruebas"></a>
## Tests
- Run unit tests:
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_multimodal_reasoning_service.py`
