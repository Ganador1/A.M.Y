# ATLAS Security Monitoring with Grafana

Grafana dashboards for real-time security monitoring and analysis.

## Quick Start

```bash
# Start Grafana
./scripts/start_grafana.sh

# Access dashboard
# URL: http://localhost:3000
# User: admin
# Pass: admin

# Stop Grafana
./scripts/stop_grafana.sh
```

## Dashboards

- **ATLAS Security Dashboard**: Main overview with events, metrics, and alerts
- **ATLAS Security Alerts**: Detailed alert monitoring and analysis

## Requirements

- Docker
- Docker Compose

## Structure

```
grafana/
├── docker-compose.yml          # Docker Compose configuration
├── grafana.ini                 # Grafana server configuration
├── provisioning/
│   ├── datasources/
│   │   └── atlas_security.yml  # SQLite datasource config
│   └── dashboards/
│       └── atlas_dashboards.yml # Dashboard provisioning config
└── dashboards/
    ├── atlas_security_dashboard.json  # Main dashboard
    └── atlas_alerts_dashboard.json    # Alerts dashboard
```

## Documentation

See [R3.9_GRAFANA_DASHBOARDS.md](../docs/R3.9_GRAFANA_DASHBOARDS.md) for complete documentation.
