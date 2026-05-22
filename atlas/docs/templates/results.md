# Results

## Primary Findings

{{ primary_findings }}

{% if validation_results %}
## Validation Results

{{ validation_results.summary if validation_results.summary else "Cross-validation analysis completed." }}

**Cross-Validation Score**: {{ "%.3f" | format(validation_results.aggregate_score) if validation_results.aggregate_score is not none else "N/A" }}
**Confidence Level**: {{ "%.3f" | format(validation_results.confidence) if validation_results.confidence is not none else "N/A" }}
**Uncertainty Bounds**: {{ ("± %.3f" | format(validation_results.uncertainty)) if validation_results.uncertainty is not none else "N/A" }}

{% if validation_results.individual_scores %}
### Domain-Specific Validation

| Domain | Score | Confidence | Uncertainty |
|--------|-------|------------|-------------|
{% for score in validation_results.individual_scores %}
| {{ score.domain }} | {{ ("%.3f" | format(score.score)) if score.score is not none else "N/A" }} | {{ ("%.3f" | format(score.confidence)) if score.confidence is not none else "N/A" }} | {{ ("%.3f" | format(score.uncertainty)) if score.uncertainty is not none else "N/A" }} |
{% endfor %}
{% endif %}
{% endif %}

{% if experimental_data %}
## Experimental Data

{{ experimental_data.summary }}

{% for dataset in experimental_data.datasets %}
### {{ dataset.name }}
- **Type**: {{ dataset.type }}
- **Size**: {{ dataset.size }}
- **Hash**: `{{ dataset.hash }}`
- **Validation**: {{ dataset.validation_status }}
{% endfor %}
{% endif %}

{% if figures %}
## Figures

{% for figure in figures %}
### Figure {{ loop.index }}: {{ figure.caption }}

![{{ figure.caption }}]({{ figure.filename }})

{{ figure.description }}

{% endfor %}
{% endif %}

