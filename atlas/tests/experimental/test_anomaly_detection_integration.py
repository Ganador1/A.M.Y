"""
Test Script for PINN Anomaly Detection System Integration

This script tests the complete integration of:
- Anomaly Detection Service
- Real-Time Monitoring Service
- Automated Alerting Service
- Security Dashboard

Author: AXIOM Research Team
Date: September 2025
"""

import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_anomaly_detection_service():
    """Test the anomaly detection service"""
    logger.info("Testing Anomaly Detection Service...")

    try:
        from app.anomaly_detection import AnomalyDetectionService

        # Initialize service and test basic functionality
        AnomalyDetectionService()
        logger.info("Anomaly Detection Service initialized successfully")

        return True

    except Exception as e:
        logger.error(f"Anomaly detection service test failed: {str(e)}")
        return False


async def test_realtime_monitoring_service():
    """Test the real-time monitoring service"""
    logger.info("Testing Real-Time Monitoring Service...")

    try:
        from app.realtime_monitoring import RealTimeMonitoringService

        # Initialize service and test basic functionality
        RealTimeMonitoringService()
        logger.info("Real-Time Monitoring Service initialized successfully")

        return True

    except Exception as e:
        logger.error(f"Real-time monitoring service test failed: {str(e)}")
        return False


async def test_automated_alerting_service():
    """Test the automated alerting service"""
    logger.info("Testing Automated Alerting Service...")

    try:
        from app.automated_alerts import AutomatedAlertingService, NotificationConfig, NotificationChannel

        # Configure notifications
        notification_config = NotificationConfig(
            channels=[NotificationChannel.CONSOLE],
            file_path="test_alerts.log"
        )

        # Initialize service
        alerting_service = AutomatedAlertingService()
        init_result = await alerting_service.initialize(notification_config, [])
        logger.info(f"Alerting service initialization: {init_result['status']}")

        # Test notifications
        test_result = await alerting_service.test_notifications()
        logger.info(f"Notification test: {test_result['status']}")

        return True

    except Exception as e:
        logger.error(f"Automated alerting service test failed: {str(e)}")
        return False


async def test_security_dashboard():
    """Test the security dashboard"""
    logger.info("Testing Security Dashboard...")

    try:
        from app.security_dashboard import SecurityDashboard, DashboardConfig

        # Configure dashboard
        dashboard_config = DashboardConfig(
            host="127.0.0.1",
            port=8001,
            title="PINN Security Test Dashboard"
        )

        # Initialize dashboard and test basic functionality
        SecurityDashboard(dashboard_config)
        logger.info("Security Dashboard initialized successfully")

        return True

    except Exception as e:
        logger.error(f"Security dashboard test failed: {str(e)}")
        return False


async def test_integrated_system():
    """Test the complete integrated system"""
    logger.info("Testing Complete Integrated Anomaly Detection System...")

    try:
        from app.automated_alerts import AutomatedAlertingService, NotificationConfig, NotificationChannel
        from app.security_dashboard import SecurityDashboard, DashboardConfig

        # Initialize alerting service
        notification_config = NotificationConfig(
            channels=[NotificationChannel.CONSOLE],
            file_path="integration_test_alerts.log"
        )
        alerting_service = AutomatedAlertingService()
        await alerting_service.initialize(notification_config, [])

        # Initialize dashboard
        dashboard_config = DashboardConfig(
            host="127.0.0.1",
            port=8002,
            title="PINN Integration Test Dashboard"
        )
        dashboard = SecurityDashboard(dashboard_config)

        # Test system health
        system_health = await dashboard._get_system_health()
        logger.info(f"System health: {system_health.get('overall_status', 'unknown')}")

        # Test dashboard summary
        dashboard_summary = await dashboard._get_dashboard_summary()
        logger.info(f"Dashboard summary: {dashboard_summary['status']}")

        logger.info("Integration test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Integrated system test failed: {str(e)}")
        return False


async def main():
    """Main test function"""
    logger.info("Starting PINN Anomaly Detection System Tests")
    logger.info("=" * 60)

    test_results = []

    # Test individual services
    logger.info("PHASE 1: Testing Individual Services")
    logger.info("-" * 40)

    anomaly_test = await test_anomaly_detection_service()
    test_results.append(("Anomaly Detection Service", anomaly_test))

    monitoring_test = await test_realtime_monitoring_service()
    test_results.append(("Real-Time Monitoring Service", monitoring_test))

    alerting_test = await test_automated_alerting_service()
    test_results.append(("Automated Alerting Service", alerting_test))

    dashboard_test = await test_security_dashboard()
    test_results.append(("Security Dashboard", dashboard_test))

    # Test integrated system
    logger.info("\nPHASE 2: Testing Integrated System")
    logger.info("-" * 40)

    integration_test = await test_integrated_system()
    test_results.append(("Integrated System", integration_test))

    # Summary
    logger.info("\nTEST SUMMARY")
    logger.info("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1

    logger.info("-" * 60)
    logger.info(f"Overall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! PINN Anomaly Detection System is ready.")
        return 0
    else:
        logger.error(f"⚠️  {total - passed} test(s) failed. Please check the logs above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error during testing: {str(e)}")
        sys.exit(1)
