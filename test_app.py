#!/usr/bin/env python3
"""
Tests for the ASL Monitoring System
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import SlackNotifier, ASLMonitor


class TestSlackNotifier(unittest.TestCase):
    """Test cases for SlackNotifier class."""
    
    def test_init_with_valid_url(self):
        """Test initialization with valid webhook URL."""
        url = "https://hooks.slack.com/services/T00/B00/XXX"
        notifier = SlackNotifier(url)
        self.assertEqual(notifier.webhook_url, url)
    
    def test_init_with_empty_url(self):
        """Test initialization with empty URL raises ValueError."""
        with self.assertRaises(ValueError):
            SlackNotifier("")
    
    def test_init_with_invalid_url(self):
        """Test initialization with invalid URL raises ValueError."""
        with self.assertRaises(ValueError):
            SlackNotifier("https://invalid.com/webhook")
    
    @patch('app.requests.post')
    def test_send_notification_success(self, mock_post):
        """Test successful notification sending."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        url = "https://hooks.slack.com/services/T00/B00/XXX"
        notifier = SlackNotifier(url)
        
        result = notifier.send_notification("Test message", "info")
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('app.requests.post')
    def test_send_notification_failure(self, mock_post):
        """Test notification sending failure."""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        url = "https://hooks.slack.com/services/T00/B00/XXX"
        notifier = SlackNotifier(url)
        
        result = notifier.send_notification("Test message", "error")
        self.assertFalse(result)


class TestASLMonitor(unittest.TestCase):
    """Test cases for ASLMonitor class."""
    
    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/services/T00/B00/XXX'})
    def test_init_with_valid_config(self):
        """Test initialization with valid configuration."""
        monitor = ASLMonitor()
        self.assertIsNotNone(monitor.notifier)
        self.assertFalse(monitor.is_running)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_webhook_url(self):
        """Test initialization without webhook URL raises ValueError."""
        with self.assertRaises(ValueError):
            ASLMonitor()
    
    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/services/T00/B00/XXX'})
    def test_get_health_status(self):
        """Test health status retrieval."""
        monitor = ASLMonitor()
        status = monitor.get_health_status()
        
        self.assertIn('status', status)
        self.assertIn('metrics', status)
        self.assertIn('timestamp', status)
        self.assertEqual(status['status'], 'stopped')
    
    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/services/T00/B00/XXX'})
    def test_check_asl_system(self):
        """Test ASL system health check."""
        monitor = ASLMonitor()
        result = monitor.check_asl_system()
        
        # Default implementation should return True
        self.assertTrue(result)
        self.assertEqual(monitor.metrics['total_checks'], 1)
        self.assertEqual(monitor.metrics['successful_checks'], 1)
    
    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/services/T00/B00/XXX'})
    def test_stop_monitoring(self):
        """Test stopping monitoring."""
        with patch('app.requests.post'):
            monitor = ASLMonitor()
            monitor.is_running = True
            monitor.stop_monitoring()
            self.assertFalse(monitor.is_running)


if __name__ == '__main__':
    unittest.main()
