"""
Alert Manager Module
Manages alert thresholds and sends notifications
"""

import os
import requests
from datetime import datetime


class AlertManager:
    """Manages monitoring alerts and notifications"""
    
    def __init__(self, slack_webhook_url=None, data_store=None):
        self.slack_webhook_url = slack_webhook_url
        self.data_store = data_store
        self.alert_history = []
        
        # Default alert thresholds
        self.thresholds = {
            'cpu_usage_percent': float(os.getenv('ALERT_CPU_THRESHOLD', '80')),
            'memory_usage_percent': float(os.getenv('ALERT_MEMORY_THRESHOLD', '85')),
            'disk_usage_percent': float(os.getenv('ALERT_DISK_THRESHOLD', '90')),
            'swap_usage_percent': float(os.getenv('ALERT_SWAP_THRESHOLD', '75'))
        }
        
        # Track last alert time to avoid spam
        self.last_alert_time = {}
        self.alert_cooldown = int(os.getenv('ALERT_COOLDOWN_SECONDS', '300'))  # 5 minutes
    
    def update_thresholds(self, new_thresholds):
        """Update alert thresholds"""
        self.thresholds.update(new_thresholds)
    
    def check_thresholds(self, metrics):
        """Check if any metrics exceed thresholds"""
        alerts = []
        
        # Check CPU usage
        if 'cpu' in metrics and 'usage_percent' in metrics['cpu']:
            cpu_usage = metrics['cpu']['usage_percent']
            if cpu_usage > self.thresholds['cpu_usage_percent']:
                if self._should_send_alert('cpu'):
                    alert = {
                        'type': 'cpu',
                        'severity': 'warning',
                        'metric': 'CPU Usage',
                        'current_value': cpu_usage,
                        'threshold': self.thresholds['cpu_usage_percent'],
                        'message': f"CPU usage is at {cpu_usage}% (threshold: {self.thresholds['cpu_usage_percent']}%)"
                    }
                    alerts.append(alert)
        
        # Check memory usage
        if 'memory' in metrics and 'usage_percent' in metrics['memory']:
            memory_usage = metrics['memory']['usage_percent']
            if memory_usage > self.thresholds['memory_usage_percent']:
                if self._should_send_alert('memory'):
                    alert = {
                        'type': 'memory',
                        'severity': 'warning',
                        'metric': 'Memory Usage',
                        'current_value': memory_usage,
                        'threshold': self.thresholds['memory_usage_percent'],
                        'message': f"Memory usage is at {memory_usage}% (threshold: {self.thresholds['memory_usage_percent']}%)"
                    }
                    alerts.append(alert)
        
        # Check swap usage
        if 'memory' in metrics and 'swap_percent' in metrics['memory']:
            swap_usage = metrics['memory']['swap_percent']
            if swap_usage > self.thresholds['swap_usage_percent']:
                if self._should_send_alert('swap'):
                    alert = {
                        'type': 'swap',
                        'severity': 'warning',
                        'metric': 'Swap Usage',
                        'current_value': swap_usage,
                        'threshold': self.thresholds['swap_usage_percent'],
                        'message': f"Swap usage is at {swap_usage}% (threshold: {self.thresholds['swap_usage_percent']}%)"
                    }
                    alerts.append(alert)
        
        # Check disk usage
        if 'disk' in metrics and 'partitions' in metrics['disk']:
            for partition in metrics['disk']['partitions']:
                if partition['usage_percent'] > self.thresholds['disk_usage_percent']:
                    alert_key = f"disk_{partition['mountpoint']}"
                    if self._should_send_alert(alert_key):
                        alert = {
                            'type': 'disk',
                            'severity': 'warning',
                            'metric': f"Disk Usage ({partition['mountpoint']})",
                            'current_value': partition['usage_percent'],
                            'threshold': self.thresholds['disk_usage_percent'],
                            'message': f"Disk usage on {partition['mountpoint']} is at {partition['usage_percent']}% (threshold: {self.thresholds['disk_usage_percent']}%)"
                        }
                        alerts.append(alert)
        
        # Send alerts if any were triggered
        for alert in alerts:
            self._send_alert(alert)
        
        return alerts
    
    def _should_send_alert(self, alert_key):
        """Check if enough time has passed since last alert"""
        now = datetime.now().timestamp()
        last_time = self.last_alert_time.get(alert_key, 0)
        
        if now - last_time >= self.alert_cooldown:
            self.last_alert_time[alert_key] = now
            return True
        return False
    
    def _send_alert(self, alert):
        """Send alert notification"""
        alert['timestamp'] = datetime.now().isoformat()
        self.alert_history.append(alert)
        
        # Keep only last 1000 alerts in memory
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        # Send to Slack if configured
        if self.slack_webhook_url:
            self._send_slack_notification(alert)
        
        # Log alert
        print(f"[ALERT] {alert['severity'].upper()}: {alert['message']}")
    
    def _send_slack_notification(self, alert):
        """Send alert to Slack"""
        try:
            # Determine emoji based on severity
            emoji = {
                'critical': '🔴',
                'warning': '⚠️',
                'info': 'ℹ️'
            }.get(alert['severity'], '⚠️')
            
            message = {
                'text': f"{emoji} *ASL Monitoring Alert*",
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': f"{emoji} Monitoring Alert: {alert['metric']}"
                        }
                    },
                    {
                        'type': 'section',
                        'fields': [
                            {
                                'type': 'mrkdwn',
                                'text': f"*Severity:*\n{alert['severity'].upper()}"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*Current Value:*\n{alert['current_value']}%"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*Threshold:*\n{alert['threshold']}%"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*Time:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f"*Message:*\n{alert['message']}"
                        }
                    }
                ]
            }
            
            response = requests.post(
                self.slack_webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to send Slack notification: {e}")
        except Exception as e:
            print(f"Error sending Slack notification: {e}")
    
    def get_alert_history(self, limit=50):
        """Get recent alert history"""
        return self.alert_history[-limit:]
    
    def clear_alert_history(self):
        """Clear alert history"""
        self.alert_history = []
