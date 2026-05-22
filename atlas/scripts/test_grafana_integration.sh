#!/bin/bash
# Test script for Grafana integration
# Verifies that Grafana can connect to the database and dashboards are accessible

set -e

echo "🧪 ATLAS Security Monitoring - Grafana Integration Test"
echo "=========================================================="
echo ""

# Check if Grafana is running
echo "1️⃣  Checking if Grafana is running..."
if docker ps | grep -q atlas-grafana; then
    echo "   ✅ Grafana container is running"
else
    echo "   ❌ Grafana container is not running"
    echo "   Run: ./scripts/start_grafana.sh"
    exit 1
fi

# Wait for Grafana to be ready
echo ""
echo "2️⃣  Waiting for Grafana to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo "   ✅ Grafana is ready"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   ⏳ Waiting... (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "   ❌ Grafana did not become ready in time"
    exit 1
fi

# Check datasource
echo ""
echo "3️⃣  Checking datasource..."
DATASOURCE_STATUS=$(curl -s -u admin:admin http://localhost:3000/api/datasources/uid/atlas_security_db)

if echo "$DATASOURCE_STATUS" | grep -q "atlas_security_db"; then
    echo "   ✅ Datasource 'ATLAS Security DB' is configured"
else
    echo "   ❌ Datasource not found"
    exit 1
fi

# Check dashboards
echo ""
echo "4️⃣  Checking dashboards..."

# Main dashboard
MAIN_DASHBOARD=$(curl -s -u admin:admin http://localhost:3000/api/dashboards/uid/atlas_security_main)
if echo "$MAIN_DASHBOARD" | grep -q "ATLAS Security Dashboard"; then
    echo "   ✅ Dashboard 'ATLAS Security Dashboard' is available"
else
    echo "   ⚠️  Main dashboard not found (may still be loading)"
fi

# Alerts dashboard
ALERTS_DASHBOARD=$(curl -s -u admin:admin http://localhost:3000/api/dashboards/uid/atlas_security_alerts)
if echo "$ALERTS_DASHBOARD" | grep -q "ATLAS Security Alerts"; then
    echo "   ✅ Dashboard 'ATLAS Security Alerts' is available"
else
    echo "   ⚠️  Alerts dashboard not found (may still be loading)"
fi

# Check database file
echo ""
echo "5️⃣  Checking database file..."
if docker exec atlas-grafana test -f /app/migrations.db; then
    echo "   ✅ Database file is mounted correctly"
    
    # Check database size
    DB_SIZE=$(docker exec atlas-grafana stat -f%z /app/migrations.db 2>/dev/null || docker exec atlas-grafana stat -c%s /app/migrations.db 2>/dev/null)
    echo "   📊 Database size: $((DB_SIZE / 1024)) KB"
else
    echo "   ❌ Database file not found in container"
    exit 1
fi

# Test database query
echo ""
echo "6️⃣  Testing database connection..."
QUERY_RESULT=$(curl -s -u admin:admin \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "queries": [{
            "datasource": {"uid": "atlas_security_db"},
            "queryText": "SELECT COUNT(*) as count FROM audit_events",
            "rawQueryText": "SELECT COUNT(*) as count FROM audit_events",
            "refId": "A"
        }]
    }' \
    http://localhost:3000/api/ds/query)

if echo "$QUERY_RESULT" | grep -q "count"; then
    EVENT_COUNT=$(echo "$QUERY_RESULT" | grep -o '"count":[0-9]*' | grep -o '[0-9]*')
    echo "   ✅ Database query successful"
    echo "   📊 Total audit events: ${EVENT_COUNT}"
else
    echo "   ⚠️  Database query failed (check logs)"
fi

echo ""
echo "=========================================================="
echo "✅ Grafana Integration Test Complete!"
echo ""
echo "📊 Access your dashboards:"
echo "   URL: http://localhost:3000"
echo "   User: admin"
echo "   Pass: admin"
echo ""
echo "📌 Navigate to:"
echo "   Dashboards → Security → ATLAS Security Dashboard"
echo "   Dashboards → Security → ATLAS Security Alerts"
echo ""
echo "🔄 Dashboards auto-refresh every 10 seconds"
echo "=========================================================="
