# Methods

## Experimental Design

{{ experimental_design }}

{% if computational_methods %}
## Computational Methods

{{ computational_methods }}

{% for method in computational_details %}
### {{ method.name }}
- **Service**: {{ method.service_name }}
- **Parameters**: {{ method.parameters }}
- **Validation**: {{ method.validation_method }}
{% endfor %}
{% endif %}

{% if cross_validation %}
## Cross-Validation Protocol

{{ cross_validation.protocol }}

**Domains Tested**: {{ cross_validation.domains | join(", ") }}
**Validation Score**: {{ cross_validation.aggregate_score }}
**Uncertainty Metrics**: {{ cross_validation.uncertainty_metrics }}
{% endif %}

## Quality Assurance

All results were validated using the AXIOM blockchain validation system with cryptographic integrity verification.

