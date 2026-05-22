#!/bin/bash
# Stop Grafana for ATLAS Security Dashboard

set -e

echo "🛑 Stopping ATLAS Security Dashboard (Grafana)..."
echo "================================================"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed"
    exit 1
fi

# Stop Grafana
cd grafana
docker-compose down

echo ""
echo "✅ Grafana stopped successfully!"
echo "================================================"
