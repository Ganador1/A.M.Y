# Results

## Primary Findings

{{ primary_findings }}

{% if validation_results %}
## Validation Results

{{ validation_results.summary }}

**Cross-Validation Score**: {{ validation_results.aggregate_score }}
**Confidence Level**: {{ validation_results.confidence }}
**Uncertainty Bounds**: ± {{ validation_results.uncertainty }}

{% if validation_results.individual_scores %}
### Domain-Specific Validation

| Domain | Score | Confidence | Uncertainty |
|--------|-------|------------|-------------|
{% for score in validation_results.individual_scores %}
| {{ score.domain }} | {{ "%.3f" | format(score.score|default(0.0)) }} | {{ "%.3f" | format(score.confidence|default(0.0)) }} | {{ "%.3f" | format(score.uncertainty|default(0.0)) }} |
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

