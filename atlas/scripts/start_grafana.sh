#!/bin/bash
# Start Grafana for ATLAS Security Dashboard
# This script starts Grafana using Docker Compose

set -e

echo "🚀 Starting ATLAS Security Dashboard (Grafana)..."
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "   Please start Docker and try again"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed"
    echo "   Please install docker-compose and try again"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p grafana/data
mkdir -p grafana/logs

# Set permissions for Grafana data directory
chmod 777 grafana/data
chmod 777 grafana/logs

# Start Grafana
cd grafana
docker-compose up -d

echo ""
echo "✅ Grafana started successfully!"
echo ""
echo "📊 Access the dashboard:"
echo "   URL: http://localhost:3000"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "📌 Dashboard location:"
echo "   Security > ATLAS Security Dashboard"
echo ""
echo "🔄 Auto-refresh: Every 10 seconds"
echo ""
echo "📝 To view logs:"
echo "   docker-compose logs -f grafana"
echo ""
echo "🛑 To stop Grafana:"
echo "   ./scripts/stop_grafana.sh"
echo "================================================"
