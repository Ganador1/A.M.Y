# 🏭 Autonomous Generators

Generators are the creative engines of the Autonomous System. They use advanced AI models to propose novel concepts, mathematical structures, and experimental designs.

## Types of Generators

### Hypothesis Generators
Produce scientifically plausible hypotheses based on literature and current knowledge graph state.

### Experiment Generators
Design experiments to test specific hypotheses, optimizing for cost and information gain.

### Data Generators
Create synthetic datasets for training and validation when real-world data is scarce.

## Usage

Generators are typically invoked by Pipelines but can be used standalone for exploratory analysis.

```python
from app.autonomous.generators import HypothesisGenerator

generator = HypothesisGenerator()
hypothesis = generator.generate(domain="physics", constraints={"energy": "high"})
print(hypothesis)
```
