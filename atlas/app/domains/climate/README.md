# Climate Domain in AXIOM Atlas

## Overview
The Climate domain provides tools for climate data analysis, focusing on evidence from datasets like GISTEMP for temperature anomalies and climate change indicators.

## Available Services
- **ClimateEvidenceService**: Analyzes climate data for evidence of changes, computing support scores and statistics.

## Installation
Requires: numpy, statistics.
Data: GISTEMP dataset in real_data_tests/.

## Quick Start
### Python SDK
```python
from app.domains.climate.services import ClimateEvidenceService

service = ClimateEvidenceService()
result = await service.process_request({"action": "climate_evidence"})
```

## Scientific Background
Based on NASA GISTEMP dataset for global temperature analysis.

## Performance Considerations
Efficient for time-series data.

## Limitations
Relies on provided dataset; update for latest data.

## Testing
`pytest tests/climate/`

## Related Services
- Observability for monitoring

## Contributing
See CONTRIBUTING.md.

## License
MIT.

## Support
support@axiom-meta.com.