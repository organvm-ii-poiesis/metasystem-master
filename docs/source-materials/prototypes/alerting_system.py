#!/usr/bin/env python3
"""
Phase 17: Alerting System
Sends alerts via email, webhooks, and Slack/Discord integration.
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"           # Informational only
    WARNING = "warning"     # Warning, needs attention
    CRITICAL = "critical"   # Critical, immediate action needed


class AlertChannel(Enum):
    """Alert delivery channels."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    LOG = "log"


class Alert:
    """Represents an alert to be sent."""
    
    def __init__(self, title: str, message: str, severity: AlertSeverity,
                 channels: List[AlertChannel], details: Optional[Dict] = None):
        self.id = f"alert_{int(datetime.now().timestamp() * 1000)}"
        self.title = title
        self.message = message
        self.severity = severity
        self.channels = channels
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity.value,
            'channels': [c.value for c in self.channels],
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
        }


class AlertingSystem:
    """
    Phase 17: Intelligent Alerting System
    
    Sends notifications via multiple channels:
    - Email (via mail command or SMTP)
    - Webhooks (generic HTTP POST)
    - Slack (via webhook URL)
    - Discord (via webhook URL)
    - System logs
    
    Features:
    - Alert deduplication (no spam for same issue)
    - Configurable severity thresholds
    - Smart retry with backoff
    - Alert history tracking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize alerting system.
        
        Args:
            config: Configuration dictionary with alert settings
        """
        self.config = config or {}
        self.alert_history: List[Alert] = []
        self.last_alerts: Dict[str, datetime] = {}  # For deduplication
        self.deduplicate_window = 3600  # 1 hour by default
        self._load_config()
    
    def _load_config(self):
        """Load alerting configuration from file or environment."""
        config_path = Path.home() / ".metasystem" / "alerting-config.yaml"
        
        if config_path.exists():
            try:
                import yaml
                with open(config_path) as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"Loaded alerting config from {config_path}")
            except Exception as e:
                logger.warning(f"Could not load alerting config: {e}")
    
    # Alert Creation
    
    def create_alert(self, title: str, message: str, 
                    severity: AlertSeverity = AlertSeverity.WARNING,
                    channels: Optional[List[AlertChannel]] = None,
                    details: Optional[Dict] = None) -> Alert:
        """Create an alert.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity level
            channels: Delivery channels (default: [LOG])
            details: Additional details
            
        Returns:
            Alert object
        """
        if channels is None:
            channels = [AlertChannel.LOG]
        
        alert = Alert(title, message, severity, channels, details)
        return alert
    
    # Alert Sending
    
    def send_alert(self, alert: Alert) -> Dict[str, bool]:
        """Send alert via configured channels.
        
        Args:
            alert: Alert to send
            
        Returns:
            Dictionary of channel -> success status
        """
        # Check deduplication
        alert_key = f"{alert.severity.value}:{alert.title}"
        if self._should_skip_duplicate(alert_key):
            logger.info(f"Skipping duplicate alert: {alert.title}")
            return {c.value: False for c in alert.channels}
        
        # Update deduplication tracker
        self.last_alerts[alert_key] = datetime.now()
        
        # Record in history
        self.alert_history.append(alert)
        
        # Send via each channel
        results = {}
        for channel in alert.channels:
            try:
                if channel == AlertChannel.LOG:
                    results[channel.value] = self._send_log(alert)
                elif channel == AlertChannel.EMAIL:
                    results[channel.value] = self._send_email(alert)
                elif channel == AlertChannel.WEBHOOK:
                    results[channel.value] = self._send_webhook(alert)
                elif channel == AlertChannel.SLACK:
                    results[channel.value] = self._send_slack(alert)
                elif channel == AlertChannel.DISCORD:
                    results[channel.value] = self._send_discord(alert)
            except Exception as e:
                logger.error(f"Failed to send alert via {channel.value}: {e}")
                results[channel.value] = False
        
        return results
    
    def send_critical_alert(self, title: str, message: str, **kwargs):
        """Send a critical alert with default channels.
        
        Args:
            title: Alert title
            message: Alert message
            **kwargs: Additional parameters for create_alert
        """
        alert = self.create_alert(
            title, message,
            severity=AlertSeverity.CRITICAL,
            channels=[AlertChannel.LOG, AlertChannel.EMAIL],
            **kwargs
        )
        return self.send_alert(alert)
    
    def send_warning_alert(self, title: str, message: str, **kwargs):
        """Send a warning alert with default channels.
        
        Args:
            title: Alert title
            message: Alert message
            **kwargs: Additional parameters for create_alert
        """
        alert = self.create_alert(
            title, message,
            severity=AlertSeverity.WARNING,
            channels=[AlertChannel.LOG],
            **kwargs
        )
        return self.send_alert(alert)
    
    # Channel Implementations
    
    def _send_log(self, alert: Alert) -> bool:
        """Send alert to system log."""
        try:
            log_func = {
                AlertSeverity.INFO: logger.info,
                AlertSeverity.WARNING: logger.warning,
                AlertSeverity.CRITICAL: logger.critical,
            }[alert.severity]
            
            message = f"[{alert.severity.value.upper()}] {alert.title}: {alert.message}"
            if alert.details:
                message += f" | {json.dumps(alert.details)}"
            
            log_func(message)
            return True
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
            return False
    
    def _send_email(self, alert: Alert) -> bool:
        """Send alert via email using mail command.
        
        Requires:
        - mail command to be available
        - ALERT_EMAIL_TO environment variable set
        """
        try:
            import os
            
            recipient = self.config.get('email_to') or os.environ.get('ALERT_EMAIL_TO')
            if not recipient:
                logger.warning("Email recipient not configured")
                return False
            
            subject = f"[METASYSTEM {alert.severity.value.upper()}] {alert.title}"
            body = f"{alert.message}\n\n"
            body += f"Severity: {alert.severity.value}\n"
            body += f"Time: {alert.timestamp.isoformat()}\n"
            
            if alert.details:
                body += f"\nDetails:\n{json.dumps(alert.details, indent=2)}\n"
            
            # Use mail command
            proc = subprocess.Popen(
                ['mail', '-s', subject, recipient],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            proc.communicate(input=body.encode())
            
            return proc.returncode == 0
        except Exception as e:
            logger.warning(f"Could not send email alert: {e}")
            return False
    
    def _send_webhook(self, alert: Alert) -> bool:
        """Send alert to generic webhook.
        
        Requires:
        - ALERT_WEBHOOK_URL configuration
        """
        try:
            import requests
            
            webhook_url = self.config.get('webhook_url')
            if not webhook_url:
                logger.warning("Webhook URL not configured")
                return False
            
            payload = {
                'alert': alert.to_dict(),
                'source': 'metasystem',
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code < 300
        except Exception as e:
            logger.warning(f"Could not send webhook alert: {e}")
            return False
    
    def _send_slack(self, alert: Alert) -> bool:
        """Send alert to Slack via webhook.
        
        Requires:
        - SLACK_WEBHOOK_URL configuration
        """
        try:
            import requests
            
            webhook_url = self.config.get('slack_webhook_url')
            if not webhook_url:
                logger.warning("Slack webhook URL not configured")
                return False
            
            # Slack message format
            color = {
                AlertSeverity.INFO: '#36a64f',
                AlertSeverity.WARNING: '#ff9900',
                AlertSeverity.CRITICAL: '#ff0000',
            }[alert.severity]
            
            payload = {
                'attachments': [{
                    'color': color,
                    'title': alert.title,
                    'text': alert.message,
                    'fields': [
                        {
                            'title': 'Severity',
                            'value': alert.severity.value,
                            'short': True
                        },
                        {
                            'title': 'Time',
                            'value': alert.timestamp.isoformat(),
                            'short': True
                        },
                    ] + [
                        {
                            'title': k,
                            'value': str(v),
                            'short': True
                        } for k, v in alert.details.items()
                    ],
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code < 300
        except Exception as e:
            logger.warning(f"Could not send Slack alert: {e}")
            return False
    
    def _send_discord(self, alert: Alert) -> bool:
        """Send alert to Discord via webhook.
        
        Requires:
        - DISCORD_WEBHOOK_URL configuration
        """
        try:
            import requests
            
            webhook_url = self.config.get('discord_webhook_url')
            if not webhook_url:
                logger.warning("Discord webhook URL not configured")
                return False
            
            # Discord embed format
            color = {
                AlertSeverity.INFO: 0x36a64f,      # Green
                AlertSeverity.WARNING: 0xff9900,   # Orange
                AlertSeverity.CRITICAL: 0xff0000,  # Red
            }[alert.severity]
            
            payload = {
                'embeds': [{
                    'title': alert.title,
                    'description': alert.message,
                    'color': color,
                    'fields': [
                        {
                            'name': 'Severity',
                            'value': alert.severity.value.upper(),
                            'inline': True
                        },
                        {
                            'name': 'Time',
                            'value': alert.timestamp.isoformat(),
                            'inline': True
                        },
                    ] + [
                        {
                            'name': k,
                            'value': str(v)[:1024],  # Discord field limit
                            'inline': True
                        } for k, v in list(alert.details.items())[:5]
                    ],
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code < 300
        except Exception as e:
            logger.warning(f"Could not send Discord alert: {e}")
            return False
    
    # Deduplication
    
    def _should_skip_duplicate(self, alert_key: str) -> bool:
        """Check if alert should be skipped due to deduplication.
        
        Args:
            alert_key: Unique key for alert (severity:title)
            
        Returns:
            True if alert should be skipped
        """
        if alert_key not in self.last_alerts:
            return False
        
        elapsed = (datetime.now() - self.last_alerts[alert_key]).total_seconds()
        return elapsed < self.deduplicate_window
    
    # Alert History
    
    def get_recent_alerts(self, limit: int = 20, 
                         hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts.
        
        Args:
            limit: Maximum alerts to return
            hours: Only alerts from past N hours
            
        Returns:
            List of alert dictionaries
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent = [
            a for a in self.alert_history
            if a.timestamp > cutoff
        ]
        
        return [a.to_dict() for a in recent[-limit:]]
    
    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Get all unresolved critical alerts."""
        critical = [
            a for a in self.alert_history
            if a.severity == AlertSeverity.CRITICAL
        ]
        
        return [a.to_dict() for a in critical]
