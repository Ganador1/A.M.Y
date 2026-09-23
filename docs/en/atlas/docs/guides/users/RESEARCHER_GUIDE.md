> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="guía-para-investigadores-en-axiom"></a>
# Guide for Researchers in AXIOM

This guide is designed for researchers who use AXIOM to advance their scientific projects. AXIOM offers powerful tools for hypothesis generation, experiment design, and more.

<a id="generación-de-hipótesis"></a>
## Hypothesis Generation

AXIOM can help you generate hypotheses based on existing data. Use the hypothesis service to input data and receive suggestions.

- **Step 1:** Access the endpoint `/hypothesis/generate`.
- **Step 2:** Provide your input data.
- **Example:** Use Python to call the API.

```python
import requests
response = requests.post('http://localhost:8000/hypothesis/generate', json={'data': 'tus datos'})
print(response.json())
```

<a id="workflows-para-diseño-de-experimentos"></a>
## Workflows for Experiment Design

Create custom workflows to design experiments.

- Integrate with tools such as Jupyter Notebooks.
- Use simulation services to predict results.

<a id="integración-con-lab-notebooks"></a>
## Integration with Lab Notebooks

AXIOM integrates with electronic notebooks to record experiments.

- Export results directly to your notebook.

<a id="mejores-prácticas"></a>
## Best Practices

- Always validate the generated hypotheses with empirical data.
- Use ML capabilities for predictive analysis.

For more details, consult the main documentation.
