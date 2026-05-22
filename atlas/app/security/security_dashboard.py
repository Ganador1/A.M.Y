"""
Security Monitoring Dashboard for PINN Anomaly Detection

This module provides a comprehensive web-based dashboard for visualizing
security metrics, anomaly detection results, and real-time monitoring data.

Key Features:
- Real-time metric visualization
- Anomaly detection results display
- Alert history and trends
- Interactive charts and graphs
- System health monitoring
- Customizable dashboards

Author: AXIOM Research Team
Date: September 2025
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import aiofiles

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from app.realtime_monitoring import RealTimeMonitoringService, MetricType
from app.algorithms.anomaly_detection import AnomalyDetectionService

# Conditional import for AutomatedAlertingService
try:
    from app.automated_alerts import AutomatedAlertingService
    AUTOMATED_ALERTS_AVAILABLE = True
except ImportError:
    AUTOMATED_ALERTS_AVAILABLE = False
    # Create a dummy class for when the service is not available
    class AutomatedAlertingService:
        async def get_alert_history(self, hours: int) -> dict:
            return {
                'status': 'error',
                'error': 'AutomatedAlertingService not available',
                'recent_alerts': []
            }


@dataclass
class DashboardConfig:
    """Configuration for the dashboard"""
    host: str = "0.0.0.0"
    port: int = 8000
    title: str = "PINN Security Monitoring Dashboard"
    refresh_interval: int = 30  # seconds
    max_history_points: int = 1000
    enable_websockets: bool = True


@dataclass
class ChartData:
    """Data structure for chart visualization"""
    labels: List[str]
    datasets: List[Dict[str, Any]]
    title: str
    chart_type: str = "line"


class SecurityDashboard:
    """Main dashboard service for security monitoring"""

    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or DashboardConfig()
        self.app = FastAPI(title=self.config.title)
        self.monitoring_service = None
        self.anomaly_service = None
        self.alerting_service = None
        self.templates = None
        self.metric_history = {}
        self.alert_history = []
        self.logger = logging.getLogger(__name__)

        # Initialize metric history for each type
        for metric_type in MetricType:
            self.metric_history[metric_type.value] = []

    async def initialize(self, monitoring_service: RealTimeMonitoringService,
                        anomaly_service: AnomalyDetectionService,
                        alerting_service: AutomatedAlertingService) -> Dict[str, Any]:
        """Initialize the dashboard with required services"""
        try:
            self.monitoring_service = monitoring_service
            self.anomaly_service = anomaly_service
            self.alerting_service = alerting_service

            # Setup FastAPI routes
            await self._setup_routes()

            # Setup static files and templates
            await self._setup_static_files()

            self.logger.info("Security dashboard initialized")
            return {
                'status': 'success',
                'message': 'Dashboard initialized successfully',
                'url': f"http://{self.config.host}:{self.config.port}"
            }

        except Exception as e:
            self.logger.error(f"Failed to initialize dashboard: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def _setup_routes(self) -> None:
        """Setup FastAPI routes"""
        try:
            @self.app.get("/", response_class=HTMLResponse)
            async def dashboard_home(request: Request):
                return await self._render_dashboard(request)

            @self.app.get("/api/metrics/current")
            async def get_current_metrics():
                return await self._get_current_metrics()

            @self.app.get("/api/metrics/history")
            async def get_metrics_history(hours: int = 24):
                return await self._get_metrics_history(hours)

            @self.app.get("/api/anomalies/recent")
            async def get_recent_anomalies(limit: int = 50):
                return await self._get_recent_anomalies(limit)

            @self.app.get("/api/alerts/history")
            async def get_alerts_history(hours: int = 24):
                return await self._get_alerts_history(hours)

            @self.app.get("/api/system/health")
            async def get_system_health():
                return await self._get_system_health()

            @self.app.get("/api/dashboard/summary")
            async def get_dashboard_summary():
                return await self._get_dashboard_summary()

            @self.app.post("/api/dashboard/refresh")
            async def refresh_dashboard():
                return await self._refresh_dashboard_data()

        except Exception as e:
            self.logger.error(f"Failed to setup routes: {str(e)}")

    async def _setup_static_files(self) -> None:
        """Setup static files and templates"""
        try:
            # Create static directory if it doesn't exist
            static_dir = os.path.join(os.path.dirname(__file__), "static")
            os.makedirs(static_dir, exist_ok=True)

            # Create templates directory if it doesn't exist
            templates_dir = os.path.join(os.path.dirname(__file__), "templates")
            os.makedirs(templates_dir, exist_ok=True)

            # Mount static files
            self.app.mount("/static", StaticFiles(directory=static_dir), name="static")

            # Setup Jinja2 templates
            self.templates = Jinja2Templates(directory=templates_dir)

            # Create basic template if it doesn't exist
            await self._create_dashboard_template()

        except Exception as e:
            self.logger.error(f"Failed to setup static files: {str(e)}")

    async def _create_dashboard_template(self) -> None:
        """Create the main dashboard HTML template"""
        try:
            template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ config.title }}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/luxon@3.0.1/build/global/luxon.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .metric-card {
            border-left: 4px solid #667eea;
        }
        .alert-card {
            border-left: 4px solid #e74c3c;
        }
        .anomaly-card {
            border-left: 4px solid #f39c12;
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-healthy { background-color: #27ae60; }
        .status-warning { background-color: #f39c12; }
        .status-critical { background-color: #e74c3c; }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px 0;
        }
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        .alert-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .alert-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            margin-bottom: 5px;
        }
        .alert-info { border-left: 4px solid #3498db; }
        .alert-warning { border-left: 4px solid #f39c12; }
        .alert-error { border-left: 4px solid #e74c3c; }
        .alert-critical { border-left: 4px solid #c0392b; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ config.title }}</h1>
        <p>Real-time Security Monitoring & Anomaly Detection</p>
        <button class="refresh-btn" onclick="refreshDashboard()">Refresh Data</button>
        <span id="last-update">Last updated: <span id="update-time">Never</span></span>
    </div>

    <div class="dashboard-grid">
        <!-- System Health -->
        <div class="card metric-card">
            <h3>System Health</h3>
            <div id="system-health">
                <p>Loading system health...</p>
            </div>
        </div>

        <!-- Current Metrics -->
        <div class="card metric-card">
            <h3>Current Metrics</h3>
            <div id="current-metrics">
                <p>Loading metrics...</p>
            </div>
        </div>

        <!-- Recent Alerts -->
        <div class="card alert-card">
            <h3>Recent Alerts</h3>
            <div id="recent-alerts" class="alert-list">
                <p>Loading alerts...</p>
            </div>
        </div>

        <!-- Anomaly Detection -->
        <div class="card anomaly-card">
            <h3>Anomaly Detection</h3>
            <div id="anomaly-stats">
                <p>Loading anomaly data...</p>
            </div>
        </div>
    </div>

    <!-- Charts Section -->
    <div class="dashboard-grid">
        <div class="card">
            <h3>Security Metrics Over Time</h3>
            <div class="chart-container">
                <canvas id="securityChart"></canvas>
            </div>
        </div>

        <div class="card">
            <h3>Alert Trends</h3>
            <div class="chart-container">
                <canvas id="alertChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        let securityChart = null;
        let alertChart = null;
        const refreshInterval = {{ config.refresh_interval }} * 1000;

        async function loadDashboardData() {
            try {
                const [metrics, alerts, anomalies, health] = await Promise.all([
                    fetch('/api/metrics/current').then(r => r.json()),
                    fetch('/api/alerts/history?hours=1').then(r => r.json()),
                    fetch('/api/anomalies/recent?limit=10').then(r => r.json()),
                    fetch('/api/system/health').then(r => r.json())
                ]);

                updateSystemHealth(health);
                updateCurrentMetrics(metrics);
                updateRecentAlerts(alerts);
                updateAnomalyStats(anomalies);
                updateCharts(metrics, alerts);

                document.getElementById('update-time').textContent = new Date().toLocaleTimeString();
            } catch (error) {
                console.error('Failed to load dashboard data:', error);
            }
        }

        function updateSystemHealth(health) {
            const container = document.getElementById('system-health');
            if (health.status === 'success') {
                const statusClass = health.overall_status === 'healthy' ? 'status-healthy' :
                                  health.overall_status === 'warning' ? 'status-warning' : 'status-critical';
                container.innerHTML = `
                    <div>
                        <span class="status-indicator ${statusClass}"></span>
                        <strong>${health.overall_status.toUpperCase()}</strong>
                    </div>
                    <div style="margin-top: 10px;">
                        <div>CPU: ${health.cpu_usage.toFixed(1)}%</div>
                        <div>Memory: ${health.memory_usage.toFixed(1)}%</div>
                        <div>Disk: ${health.disk_usage.toFixed(1)}%</div>
                    </div>
                `;
            } else {
                container.innerHTML = '<p>Error loading system health</p>';
            }
        }

        function updateCurrentMetrics(metrics) {
            const container = document.getElementById('current-metrics');
            if (metrics.status === 'success') {
                let html = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">';
                Object.entries(metrics.metrics).forEach(([type, data]) => {
                    html += `
                        <div>
                            <strong>${type}:</strong>
                            <div style="margin-left: 10px;">
                                ${Object.entries(data).map(([key, value]) =>
                                    `<div>${key}: ${typeof value === 'number' ? value.toFixed(3) : value}</div>`
                                ).join('')}
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p>Error loading metrics</p>';
            }
        }

        function updateRecentAlerts(alerts) {
            const container = document.getElementById('recent-alerts');
            if (alerts.status === 'success' && alerts.recent_alerts.length > 0) {
                const html = alerts.recent_alerts.map(alert => {
                    const levelClass = `alert-${alert.level.toLowerCase()}`;
                    return `
                        <div class="alert-item ${levelClass}">
                            <strong>${alert.title}</strong>
                            <div style="font-size: 0.9em; color: #666;">
                                ${new Date(alert.timestamp).toLocaleTimeString()}
                            </div>
                            <div>${alert.description}</div>
                        </div>
                    `;
                }).join('');
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p>No recent alerts</p>';
            }
        }

        function updateAnomalyStats(anomalies) {
            const container = document.getElementById('anomaly-stats');
            if (anomalies.status === 'success') {
                container.innerHTML = `
                    <div>
                        <div>Total Anomalies: <strong>${anomalies.total_anomalies}</strong></div>
                        <div>Recent Anomalies: <strong>${anomalies.recent_count}</strong></div>
                        <div>Average Confidence: <strong>${anomalies.avg_confidence.toFixed(2)}</strong></div>
                    </div>
                `;
            } else {
                container.innerHTML = '<p>Error loading anomaly data</p>';
            }
        }

        function updateCharts(metrics, alerts) {
            // Update security metrics chart
            if (securityChart) {
                securityChart.destroy();
            }

            const ctx = document.getElementById('securityChart').getContext('2d');
            securityChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Now'],
                    datasets: [{
                        label: 'Security Score',
                        data: [95.5], // Placeholder
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });

            // Update alerts chart
            if (alertChart) {
                alertChart.destroy();
            }

            const alertCtx = document.getElementById('alertChart').getContext('2d');
            alertChart = new Chart(alertCtx, {
                type: 'bar',
                data: {
                    labels: ['INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                    datasets: [{
                        label: 'Alert Count',
                        data: [5, 3, 1, 0], // Placeholder
                        backgroundColor: [
                            '#3498db',
                            '#f39c12',
                            '#e74c3c',
                            '#c0392b'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        async function refreshDashboard() {
            await loadDashboardData();
        }

        // Auto-refresh
        setInterval(loadDashboardData, refreshInterval);

        // Initial load
        loadDashboardData();
    </script>
</body>
</html>"""

            template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
            with aiofiles.open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)

        except Exception as e:
            self.logger.error(f"Failed to create dashboard template: {str(e)}")

    async def _render_dashboard(self, request: Request) -> Any:
        """Render the main dashboard page"""
        try:
            if not self.templates:
                return HTMLResponse("<h1>Dashboard not initialized</h1>", status_code=500)

            return self.templates.TemplateResponse(
                "dashboard.html",
                {
                    "request": request,
                    "config": self.config
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to render dashboard: {str(e)}")
            return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)

    async def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics from monitoring service"""
        try:
            if not self.monitoring_service:
                return {'status': 'error', 'error': 'Monitoring service not available'}

            # Get latest metrics from service
            current_metrics = {}
            for metric_type in MetricType:
                # This would integrate with the actual monitoring service
                current_metrics[metric_type.value] = {
                    'value': 0.95,  # Placeholder
                    'timestamp': datetime.now().isoformat()
                }

            return {
                'status': 'success',
                'metrics': current_metrics,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to get current metrics: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def _get_metrics_history(self, hours: int) -> Dict[str, Any]:
        """Get metrics history"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Filter history data
            history_data = {}
            for metric_type, data in self.metric_history.items():
                filtered_data = [d for d in data if d['timestamp'] > cutoff_time]
                history_data[metric_type] = filtered_data[-self.config.max_history_points:]

            return {
                'status': 'success',
                'history': history_data,
                'hours': hours
            }

        except Exception as e:
            self.logger.error(f"Failed to get metrics history: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def _get_recent_anomalies(self, limit: int) -> Dict[str, Any]:
        """Get recent anomaly detection results"""
        try:
            if not self.anomaly_service:
                return {'status': 'error', 'error': 'Anomaly service not available'}

            # This would integrate with the actual anomaly service
            # For now, return placeholder data
            return {
                'status': 'success',
                'total_anomalies': 15,
                'recent_count': min(limit, 15),
                'avg_confidence': 0.87,
                'anomalies': []  # Would contain actual anomaly data
            }

        except Exception as e:
            self.logger.error(f"Failed to get recent anomalies: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def _get_alerts_history(self, hours: int) -> Dict[str, Any]:
        """Get alerts history"""
        try:
            if not self.alerting_service:
                return {'status': 'error', 'error': 'Alerting service not available'}

            # Get alert history from alerting service
            history_result = await self.alerting_service.get_alert_history(hours)

            if history_result['status'] == 'success':
                return history_result
            else:
                return {'status': 'error', 'error': 'Failed to get alert history'}

        except Exception as e:
            self.logger.error(f"Failed to get alerts history: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health information"""
        try:
            import psutil

            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Determine overall status
            if cpu_usage > 90 or memory.percent > 90 or disk.percent > 95:
                overall_status = 'critical'
            elif cpu_usage > 70 or memory.percent > 80 or disk.percent > 85:
                overall_status = 'warning'
            else:
                overall_status = 'healthy'

            return {
                'status': 'success',
                'overall_status': overall_status,
                'cpu_usage': cpu_usage,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'memory_total': memory.total,
                'memory_available': memory.available,
                'disk_total': disk.total,
                'disk_free': disk.free
            }

        except ImportError:
            return {
                'status': 'success',
                'overall_status': 'unknown',
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'disk_usage': 0.0,
                'note': 'psutil not available'
            }
        except Exception as e:
            self.logger.error(f"Failed to get system health: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def _get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        try:
            # Get all dashboard data in parallel
            tasks = [
                self._get_current_metrics(),
                self._get_alerts_history(24),
                self._get_recent_anomalies(20),
                self._get_system_health()
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            summary = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'metrics': results[0] if not isinstance(results[0], Exception) else {'status': 'error'},
                'alerts': results[1] if not isinstance(results[1], Exception) else {'status': 'error'},
                'anomalies': results[2] if not isinstance(results[2], Exception) else {'status': 'error'},
                'system_health': results[3] if not isinstance(results[3], Exception) else {'status': 'error'}
            }

            return summary

        except Exception as e:
            self.logger.error(f"Failed to get dashboard summary: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def _refresh_dashboard_data(self) -> Dict[str, Any]:
        """Refresh all dashboard data"""
        try:
            summary = await self._get_dashboard_summary()
            return {
                'status': 'success',
                'message': 'Dashboard data refreshed',
                'data': summary
            }

        except Exception as e:
            self.logger.error(f"Failed to refresh dashboard data: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def start_dashboard(self) -> None:
        """Start the dashboard server"""
        try:
            self.logger.info(f"Starting dashboard server on {self.config.host}:{self.config.port}")
            uvicorn.run(
                self.app,
                host=self.config.host,
                port=self.config.port,
                log_level="info"
            )

        except Exception as e:
            self.logger.error(f"Failed to start dashboard server: {str(e)}")
            raise

    def update_metric_history(self, metric_type: MetricType, value: float,
                            timestamp: Optional[datetime] = None) -> None:
        """Update metric history for visualization"""
        try:
            if timestamp is None:
                timestamp = datetime.now()

            history_key = metric_type.value
            if history_key not in self.metric_history:
                self.metric_history[history_key] = []

            # Add new data point
            self.metric_history[history_key].append({
                'value': value,
                'timestamp': timestamp
            })

            # Keep only recent history
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.metric_history[history_key] = [
                d for d in self.metric_history[history_key]
                if d['timestamp'] > cutoff_time
            ]

            # Limit history size
            if len(self.metric_history[history_key]) > self.config.max_history_points:
                self.metric_history[history_key] = self.metric_history[history_key][-self.config.max_history_points:]

        except Exception as e:
            self.logger.error(f"Failed to update metric history: {str(e)}")

    def add_alert_to_history(self, alert_data: Dict[str, Any]) -> None:
        """Add alert to history for visualization"""
        try:
            self.alert_history.append({
                'timestamp': datetime.now(),
                **alert_data
            })

            # Keep only recent alerts
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.alert_history = [
                a for a in self.alert_history
                if a['timestamp'] > cutoff_time
            ]

        except Exception as e:
            self.logger.error(f"Failed to add alert to history: {str(e)}")


# Export main service
__all__ = ['SecurityDashboard', 'DashboardConfig', 'ChartData']
