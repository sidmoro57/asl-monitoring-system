#!/usr/bin/env python3
"""
ASL Monitoring System - Main Application

This application monitors ASL (American Sign Language) application metrics
and sends notifications to Slack when issues are detected.
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('asl_monitoring.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SlackNotifier:
    """Handles Slack notifications using webhook."""
    
    def __init__(self, webhook_url: str):
        """
        Initialize Slack notifier.
        
        Args:
            webhook_url: Slack webhook URL from environment variable
        """
        if not webhook_url:
            raise ValueError("Slack webhook URL is required")
        
        if not webhook_url.startswith('https://hooks.slack.com/services/'):
            raise ValueError("Invalid Slack webhook URL format")
        
        self.webhook_url = webhook_url
    
    def send_notification(self, message: str, level: str = "info") -> bool:
        """
        Send a notification to Slack.
        
        Args:
            message: The message to send
            level: Message level (info, warning, error, success)
        
        Returns:
            True if successful, False otherwise
        """
        emoji_map = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }
        
        emoji = emoji_map.get(level, "ℹ️")
        formatted_message = f"{emoji} {message}"
        
        payload = {
            'text': formatted_message,
            'username': 'ASL Monitoring Bot',
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Slack notification sent successfully: {message}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False


class ASLMonitor:
    """Main ASL monitoring system."""
    
    def __init__(self):
        """Initialize the monitoring system."""
        # Load environment variables
        load_dotenv()
        
        # Get configuration from environment
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        if not self.webhook_url:
            logger.error("SLACK_WEBHOOK_URL environment variable is not set")
            logger.error("Please create a .env file based on .env.example")
            raise ValueError("SLACK_WEBHOOK_URL is required")
        
        # Initialize Slack notifier
        try:
            self.notifier = SlackNotifier(self.webhook_url)
        except ValueError as e:
            logger.error(f"Failed to initialize Slack notifier: {e}")
            raise
        
        # Monitoring state
        self.is_running = False
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds
        self.metrics = {
            'last_check': None,
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
        }
    
    def get_health_status(self) -> Dict[str, any]:
        """
        Get current health status of the monitoring system.
        
        Returns:
            Dictionary containing health status information
        """
        return {
            'status': 'healthy' if self.is_running else 'stopped',
            'uptime': self.metrics['total_checks'] * self.check_interval,
            'metrics': self.metrics,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_asl_system(self) -> bool:
        """
        Perform a health check on the ASL system.
        
        This is a placeholder that should be customized based on
        actual ASL application monitoring needs.
        
        Returns:
            True if system is healthy, False otherwise
        """
        try:
            # Placeholder for actual monitoring logic
            # In a real implementation, this would:
            # - Check ASL application endpoints
            # - Verify database connections
            # - Monitor resource usage
            # - Check for error rates
            
            logger.debug("Performing ASL system health check...")
            
            # Simulate a health check (replace with actual logic)
            current_time = datetime.now()
            self.metrics['last_check'] = current_time.isoformat()
            self.metrics['total_checks'] += 1
            
            # Example: Simple check that always passes
            # Replace with actual monitoring logic
            is_healthy = True
            
            if is_healthy:
                self.metrics['successful_checks'] += 1
                logger.debug("ASL system health check passed")
            else:
                self.metrics['failed_checks'] += 1
                logger.warning("ASL system health check failed")
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            self.metrics['failed_checks'] += 1
            return False
    
    def start_monitoring(self):
        """Start the monitoring loop."""
        logger.info("Starting ASL monitoring system...")
        self.is_running = True
        
        # Send startup notification
        startup_message = (
            f"ASL Monitoring System started\n"
            f"Check interval: {self.check_interval} seconds\n"
            f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.notifier.send_notification(startup_message, level="success")
        
        try:
            while self.is_running:
                # Perform health check
                is_healthy = self.check_asl_system()
                
                # Send notification if check failed
                if not is_healthy:
                    error_message = (
                        f"ASL System Health Check Failed!\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Total checks: {self.metrics['total_checks']}\n"
                        f"Failed checks: {self.metrics['failed_checks']}"
                    )
                    self.notifier.send_notification(error_message, level="error")
                
                # Log periodic status
                if self.metrics['total_checks'] % 10 == 0:
                    logger.info(
                        f"Monitoring active - "
                        f"Total checks: {self.metrics['total_checks']}, "
                        f"Success: {self.metrics['successful_checks']}, "
                        f"Failed: {self.metrics['failed_checks']}"
                    )
                
                # Wait for next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            error_message = f"ASL Monitoring System encountered an error: {str(e)}"
            self.notifier.send_notification(error_message, level="error")
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        logger.info("Stopping ASL monitoring system...")
        self.is_running = False
        
        # Send shutdown notification
        shutdown_message = (
            f"ASL Monitoring System stopped\n"
            f"Total checks performed: {self.metrics['total_checks']}\n"
            f"Successful: {self.metrics['successful_checks']}\n"
            f"Failed: {self.metrics['failed_checks']}\n"
            f"Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.notifier.send_notification(shutdown_message, level="info")


def main():
    """Main entry point for the application."""
    logger.info("=== ASL Monitoring System ===")
    
    try:
        # Initialize monitor
        monitor = ASLMonitor()
        
        # Start monitoring
        monitor.start_monitoring()
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
