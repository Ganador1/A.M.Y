"""
Automated Alerting System for PINN Security Monitoring

This module provides comprehensive alerting capabilities for the PINN security
monitoring system, including automated notifications, alert escalation, and
integration with external systems.

Key Features:
- Multi-channel alert notifications (console, file, email)
- Alert escalation based on severity and duration
- Alert correlation and deduplication
- Integration with external monitoring systems
- Alert history and trend analysis

Author: AXIOM Research Team
Date: September 2025
"""

import asyncio
import logging
import smtplib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiofiles

from app.realtime_monitoring import Alert, AlertLevel, MetricType


class NotificationChannel(Enum):
    """Available notification channels"""
    CONSOLE = "console"
    FILE = "file"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TELEGRAM = "telegram"


class EscalationLevel(Enum):
    """Alert escalation levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NotificationConfig:
    """Configuration for notifications"""
    channels: List[NotificationChannel]
    email_config: Optional[Dict[str, Any]] = None
    webhook_config: Optional[Dict[str, Any]] = None
    slack_config: Optional[Dict[str, Any]] = None
    telegram_config: Optional[Dict[str, Any]] = None
    file_path: str = "alerts.log"


@dataclass
class EscalationRule:
    """Rule for alert escalation"""
    alert_level: AlertLevel
    duration_minutes: int
    escalation_level: EscalationLevel
    additional_channels: List[NotificationChannel]
    repeat_interval_minutes: int = 60


@dataclass
class AlertTemplate:
    """Template for alert messages"""
    subject_template: str
    body_template: str
    channel: NotificationChannel


class NotificationManager:
    """Manages notifications across multiple channels"""

    def __init__(self, config: NotificationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def send_notification(self, alert: Alert, channel: NotificationChannel,
                              template: Optional[AlertTemplate] = None) -> bool:
        """Send notification through specified channel"""
        try:
            if channel == NotificationChannel.CONSOLE:
                return await self._send_console_notification(alert)
            elif channel == NotificationChannel.FILE:
                return await self._send_file_notification(alert)
            elif channel == NotificationChannel.EMAIL:
                return await self._send_email_notification(alert, template)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook_notification(alert)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack_notification(alert)
            elif channel == NotificationChannel.TELEGRAM:
                return await self._send_telegram_notification(alert)
            else:
                self.logger.warning(f"Unsupported notification channel: {channel}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to send {channel.value} notification: {str(e)}")
            return False

    async def _send_console_notification(self, alert: Alert) -> bool:
        """Send notification to console"""
        try:
            timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            message = f"[{timestamp}] {alert.level.value.upper()} ALERT: {alert.title}\n"
            message += f"Description: {alert.description}\n"
            message += f"Metric: {alert.metric_type.value}/{alert.metric_name}\n"
            message += f"Value: {alert.actual_value:.3f} (Threshold: {alert.threshold_value:.3f})\n"

            if alert.recommendations:
                message += "Recommendations:\n"
                for rec in alert.recommendations:
                    message += f"  • {rec}\n"

            print(message)
            return True

        except Exception as e:
            self.logger.error(f"Console notification failed: {str(e)}")
            return False

    async def _send_file_notification(self, alert: Alert) -> bool:
        """Send notification to file"""
        try:
            timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            message = f"[{timestamp}] {alert.level.value.upper()} ALERT: {alert.title} - {alert.description}\n"

            with aiofiles.aiofiles.open(self.config.file_path, 'a', encoding='utf-8') as f:
                f.write(message)

            return True

        except Exception as e:
            self.logger.error(f"File notification failed: {str(e)}")
            return False

    async def _send_email_notification(self, alert: Alert, template: Optional[AlertTemplate]) -> bool:
        """Send email notification"""
        try:
            if not self.config.email_config:
                self.logger.warning("Email configuration not provided")
                return False

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.email_config['from_email']
            msg['To'] = self.config.email_config['to_email']

            if template:
                msg['Subject'] = template.subject_template.format(
                    level=alert.level.value.upper(),
                    title=alert.title
                )
                body = template.body_template.format(
                    timestamp=alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    level=alert.level.value.upper(),
                    title=alert.title,
                    description=alert.description,
                    metric_type=alert.metric_type.value,
                    metric_name=alert.metric_name,
                    actual_value=alert.actual_value,
                    threshold_value=alert.threshold_value,
                    recommendations="\n".join(f"• {rec}" for rec in alert.recommendations)
                )
            else:
                msg['Subject'] = f"PINN Security Alert: {alert.level.value.upper()} - {alert.title}"
                body = f"""
PINN Security Alert

Timestamp: {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
Level: {alert.level.value.upper()}
Title: {alert.title}
Description: {alert.description}

Metric: {alert.metric_type.value}/{alert.metric_name}
Actual Value: {alert.actual_value:.3f}
Threshold: {alert.threshold_value:.3f}

Recommendations:
{chr(10).join(f"• {rec}" for rec in alert.recommendations)}
"""

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            server = smtplib.SMTP(self.config.email_config['smtp_server'],
                                self.config.email_config['smtp_port'])
            if self.config.email_config.get('use_tls', True):
                server.starttls()
            server.login(self.config.email_config['username'],
                        self.config.email_config['password'])
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            self.logger.error(f"Email notification failed: {str(e)}")
            return False

    async def _send_webhook_notification(self, alert: Alert) -> bool:
        """Send webhook notification"""
        try:
            if not self.config.webhook_config:
                self.logger.warning("Webhook configuration not provided")
                return False

            import aiohttp

            payload = {
                'timestamp': alert.timestamp.isoformat(),
                'level': alert.level.value,
                'title': alert.title,
                'description': alert.description,
                'metric_type': alert.metric_type.value,
                'metric_name': alert.metric_name,
                'actual_value': alert.actual_value,
                'threshold_value': alert.threshold_value,
                'recommendations': alert.recommendations
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.webhook_config['url'],
                    json=payload,
                    headers=self.config.webhook_config.get('headers', {})
                ) as response:
                    return response.status == 200

        except ImportError:
            self.logger.warning("aiohttp not available for webhook notifications")
            return False
        except Exception as e:
            self.logger.error(f"Webhook notification failed: {str(e)}")
            return False

    async def _send_slack_notification(self, alert: Alert) -> bool:
        """Send Slack notification"""
        try:
            if not self.config.slack_config:
                self.logger.warning("Slack configuration not provided")
                return False

            import aiohttp

            # Create Slack message
            color = {
                AlertLevel.INFO: "good",
                AlertLevel.WARNING: "warning",
                AlertLevel.ERROR: "danger",
                AlertLevel.CRITICAL: "danger"
            }.get(alert.level, "warning")

            payload = {
                'attachments': [{
                    'color': color,
                    'title': f"PINN Security Alert: {alert.title}",
                    'text': alert.description,
                    'fields': [
                        {
                            'title': 'Metric',
                            'value': f"{alert.metric_type.value}/{alert.metric_name}",
                            'short': True
                        },
                        {
                            'title': 'Value',
                            'value': f"{alert.actual_value:.3f} (Threshold: {alert.threshold_value:.3f})",
                            'short': True
                        }
                    ],
                    'footer': f"PINN Security Monitor | {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                }]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.slack_config['webhook_url'],
                    json=payload
                ) as response:
                    return response.status == 200

        except ImportError:
            self.logger.warning("aiohttp not available for Slack notifications")
            return False
        except Exception as e:
            self.logger.error(f"Slack notification failed: {str(e)}")
            return False

    async def _send_telegram_notification(self, alert: Alert) -> bool:
        """Send Telegram notification"""
        try:
            if not self.config.telegram_config:
                self.logger.warning("Telegram configuration not provided")
                return False

            import aiohttp

            # Create Telegram message
            emoji = {
                AlertLevel.INFO: "ℹ️",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.ERROR: "❌",
                AlertLevel.CRITICAL: "🚨"
            }.get(alert.level, "⚠️")

            message = f"{emoji} *PINN Security Alert*\n\n"
            message += f"*{alert.title}*\n"
            message += f"{alert.description}\n\n"
            message += f"📊 Metric: `{alert.metric_type.value}/{alert.metric_name}`\n"
            message += f"📈 Value: `{alert.actual_value:.3f}` (Threshold: `{alert.threshold_value:.3f}`)\n\n"

            if alert.recommendations:
                message += "💡 *Recommendations:*\n"
                for rec in alert.recommendations:
                    message += f"• {rec}\n"

            payload = {
                'chat_id': self.config.telegram_config['chat_id'],
                'text': message,
                'parse_mode': 'Markdown'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://api.telegram.org/bot{self.config.telegram_config['bot_token']}/sendMessage",
                    json=payload
                ) as response:
                    return response.status == 200

        except ImportError:
            self.logger.warning("aiohttp not available for Telegram notifications")
            return False
        except Exception as e:
            self.logger.error(f"Telegram notification failed: {str(e)}")
            return False


class AlertEscalationManager:
    """Manages alert escalation based on rules"""

    def __init__(self, escalation_rules: List[EscalationRule],
                 notification_manager: NotificationManager):
        self.escalation_rules = escalation_rules
        self.notification_manager = notification_manager
        self.active_escalations = {}
        self.logger = logging.getLogger(__name__)

    async def check_escalation(self, alert: Optional[Alert]) -> None:
        """Check if alert needs escalation"""
        try:
            if alert is None:
                # Check all active escalations for repeat notifications
                await self.check_repeat_notifications()
                return

            alert_key = f"{alert.metric_type.value}_{alert.metric_name}_{alert.level.value}"

            # Find applicable escalation rule
            applicable_rule = None
            for rule in self.escalation_rules:
                if (rule.alert_level == alert.level and
                    alert_key not in self.active_escalations):
                    applicable_rule = rule
                    break

            if applicable_rule:
                # Check if alert duration exceeds threshold
                alert_age = (datetime.now() - alert.timestamp).total_seconds() / 60

                if alert_age >= applicable_rule.duration_minutes:
                    await self._escalate_alert(alert, applicable_rule)

        except Exception as e:
            self.logger.error(f"Escalation check failed: {str(e)}")

    async def _escalate_alert(self, alert: Alert, rule: EscalationRule) -> None:
        """Escalate an alert"""
        try:
            alert_key = f"{alert.metric_type.value}_{alert.metric_name}_{alert.level.value}"

            # Mark as escalated
            self.active_escalations[alert_key] = {
                'escalation_time': datetime.now(),
                'rule': rule,
                'last_notification': datetime.now()
            }

            # Send escalated notifications
            escalation_message = f"🚨 ESCALATED ALERT: {alert.title}\n"
            escalation_message += f"This alert has been active for {rule.duration_minutes} minutes "
            escalation_message += f"and has been escalated to {rule.escalation_level.value.upper()} level."

            escalated_alert = Alert(
                id=f"escalated_{alert.id}",
                timestamp=datetime.now(),
                level=AlertLevel.CRITICAL if rule.escalation_level == EscalationLevel.CRITICAL else alert.level,
                title=f"ESCALATED: {alert.title}",
                description=escalation_message,
                metric_type=alert.metric_type,
                metric_name=alert.metric_name,
                threshold_value=alert.threshold_value,
                actual_value=alert.actual_value,
                recommendations=alert.recommendations + ["Alert has been escalated due to prolonged duration"]
            )

            # Send to additional channels
            for channel in rule.additional_channels:
                await self.notification_manager.send_notification(escalated_alert, channel)

            self.logger.warning(f"Alert escalated: {alert.title}")

        except Exception as e:
            self.logger.error(f"Alert escalation failed: {str(e)}")

    async def check_repeat_notifications(self) -> None:
        """Check for repeat notifications on escalated alerts"""
        try:
            current_time = datetime.now()

            for alert_key, escalation_info in self.active_escalations.items():
                rule = escalation_info['rule']
                last_notification = escalation_info['last_notification']

                # Check if it's time for repeat notification
                time_since_last = (current_time - last_notification).total_seconds() / 60

                if time_since_last >= rule.repeat_interval_minutes:
                    # Send repeat notification
                    repeat_message = "🔄 REPEAT ALERT: This escalated alert is still active"

                    # Create repeat alert (simplified)
                    repeat_alert = Alert(
                        id=f"repeat_{alert_key}_{int(current_time.timestamp())}",
                        timestamp=current_time,
                        level=AlertLevel.WARNING,
                        title="Repeat Escalated Alert",
                        description=repeat_message,
                        metric_type=MetricType.SECURITY,  # Placeholder
                        metric_name="escalated_alert",
                        threshold_value=0.0,
                        actual_value=0.0,
                        recommendations=["Check the original escalated alert"]
                    )

                    # Send to escalation channels
                    for channel in rule.additional_channels:
                        await self.notification_manager.send_notification(repeat_alert, channel)

                    # Update last notification time
                    escalation_info['last_notification'] = current_time

        except Exception as e:
            self.logger.error(f"Repeat notification check failed: {str(e)}")


class AutomatedAlertingService:
    """Main service for automated alerting"""

    def __init__(self):
        self.notification_manager = None
        self.escalation_manager = None
        self.alert_templates = {}
        self.alert_history = []
        self.monitoring_active = False
        self.logger = logging.getLogger(__name__)

    async def initialize(self, notification_config: NotificationConfig,
                        escalation_rules: List[EscalationRule]) -> Dict[str, Any]:
        """Initialize the alerting service"""
        try:
            self.notification_manager = NotificationManager(notification_config)
            self.escalation_manager = AlertEscalationManager(
                escalation_rules, self.notification_manager
            )

            # Set up default alert templates
            self._setup_default_templates()

            self.logger.info("Automated alerting service initialized")
            return {
                'status': 'success',
                'message': 'Alerting service initialized',
                'channels': [c.value for c in notification_config.channels]
            }

        except Exception as e:
            self.logger.error(f"Failed to initialize alerting service: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def _setup_default_templates(self) -> None:
        """Set up default alert templates"""
        try:
            # Email template
            self.alert_templates[NotificationChannel.EMAIL] = AlertTemplate(
                subject_template="PINN Security Alert: {level} - {title}",
                body_template="""PINN Security Alert

Timestamp: {timestamp}
Severity Level: {level}
Alert Title: {title}

Description:
{description}

Affected Metric: {metric_type}/{metric_name}
Current Value: {actual_value:.3f}
Threshold Value: {threshold_value:.3f}

Recommended Actions:
{recommendations}

This is an automated notification from the PINN Security Monitoring System.
""",
                channel=NotificationChannel.EMAIL
            )

            # Slack template (would be used for rich formatting)
            self.alert_templates[NotificationChannel.SLACK] = AlertTemplate(
                subject_template="",  # Not used for Slack
                body_template="",    # Not used for Slack
                channel=NotificationChannel.SLACK
            )

        except Exception as e:
            self.logger.error(f"Failed to setup default templates: {str(e)}")

    async def process_alert(self, alert: Alert) -> Dict[str, Any]:
        """Process an incoming alert"""
        try:
            # Store alert in history
            self.alert_history.append(alert)

            # Keep only recent history
            cutoff_time = datetime.now() - timedelta(days=7)
            self.alert_history = [a for a in self.alert_history if a.timestamp > cutoff_time]

            # Send notifications
            if not self.notification_manager:
                return {'status': 'error', 'error': 'Notification manager not initialized'}

            notification_results = []
            for channel in self.notification_manager.config.channels:
                template = self.alert_templates.get(channel)
                success = await self.notification_manager.send_notification(
                    alert, channel, template
                )
                notification_results.append({
                    'channel': channel.value,
                    'success': success
                })

            # Check for escalation
            if self.escalation_manager:
                await self.escalation_manager.check_escalation(alert)

            successful_notifications = sum(1 for r in notification_results if r['success'])

            return {
                'status': 'success',
                'alert_id': alert.id,
                'notifications_sent': successful_notifications,
                'total_channels': len(notification_results),
                'notification_results': notification_results
            }

        except Exception as e:
            self.logger.error(f"Failed to process alert: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def start_monitoring(self) -> Dict[str, Any]:
        """Start the alerting monitoring service"""
        try:
            if self.monitoring_active:
                return {'status': 'error', 'message': 'Monitoring already active'}

            self.monitoring_active = True

            # Start escalation monitoring
            asyncio.create_task(self._escalation_monitoring_loop())

            self.logger.info("Alerting monitoring started")
            return {'status': 'success', 'message': 'Alerting monitoring started'}

        except Exception as e:
            self.logger.error(f"Failed to start alerting monitoring: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop the alerting monitoring service"""
        try:
            self.monitoring_active = False
            self.logger.info("Alerting monitoring stopped")
            return {'status': 'success', 'message': 'Alerting monitoring stopped'}

        except Exception as e:
            self.logger.error(f"Failed to stop alerting monitoring: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def _escalation_monitoring_loop(self) -> None:
        """Main loop for escalation monitoring"""
        try:
            while self.monitoring_active:
                # Check for escalations
                if self.escalation_manager:
                    await self.escalation_manager.check_escalation(None)  # Check all active alerts

                    # Check for repeat notifications
                    await self.escalation_manager.check_repeat_notifications()

                # Wait before next check
                await asyncio.sleep(60)  # Check every minute

        except asyncio.CancelledError:
            self.logger.info("Escalation monitoring cancelled")
        except Exception as e:
            self.logger.error(f"Escalation monitoring failed: {str(e)}")
            self.monitoring_active = False

    async def get_alert_history(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert history"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Filter alerts by time
            filtered_alerts = [a for a in self.alert_history if a.timestamp > cutoff_time]

            # Group by level
            alerts_by_level = {}
            for level in AlertLevel:
                level_alerts = [a for a in filtered_alerts if a.level == level]
                alerts_by_level[level.value] = len(level_alerts)

            # Group by metric type
            alerts_by_type = {}
            for alert in filtered_alerts:
                metric_type = alert.metric_type.value
                if metric_type not in alerts_by_type:
                    alerts_by_type[metric_type] = 0
                alerts_by_type[metric_type] += 1

            return {
                'status': 'success',
                'total_alerts': len(filtered_alerts),
                'alerts_by_level': alerts_by_level,
                'alerts_by_type': alerts_by_type,
                'time_range': f"{hours} hours",
                'recent_alerts': [
                    {
                        'id': alert.id,
                        'timestamp': alert.timestamp.isoformat(),
                        'level': alert.level.value,
                        'title': alert.title,
                        'description': alert.description[:100] + "..." if len(alert.description) > 100 else alert.description
                    }
                    for alert in filtered_alerts[-10:]  # Last 10 alerts
                ]
            }

        except Exception as e:
            self.logger.error(f"Failed to get alert history: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def test_notifications(self) -> Dict[str, Any]:
        """Test notification channels"""
        try:
            if not self.notification_manager:
                return {'status': 'error', 'error': 'Notification manager not initialized'}

            # Create test alert
            test_alert = Alert(
                id="test_alert",
                timestamp=datetime.now(),
                level=AlertLevel.INFO,
                title="Test Alert",
                description="This is a test notification from the PINN Security Alerting System",
                metric_type=MetricType.SECURITY,
                metric_name="test_metric",
                threshold_value=1.0,
                actual_value=0.5,
                recommendations=["This is a test notification", "No action required"]
            )

            # Test each configured channel
            test_results = []
            for channel in self.notification_manager.config.channels:
                template = self.alert_templates.get(channel)
                success = await self.notification_manager.send_notification(
                    test_alert, channel, template
                )
                test_results.append({
                    'channel': channel.value,
                    'success': success
                })

            successful_tests = sum(1 for r in test_results if r['success'])

            return {
                'status': 'success',
                'message': f"Notification test completed: {successful_tests}/{len(test_results)} channels successful",
                'test_results': test_results
            }

        except Exception as e:
            self.logger.error(f"Notification test failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}


# Export main service
__all__ = ['AutomatedAlertingService', 'NotificationConfig', 'EscalationRule', 'AlertTemplate']
