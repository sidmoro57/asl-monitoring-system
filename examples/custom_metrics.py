"""
Example: Submitting Custom Metrics to ASL Monitoring System

This example demonstrates how to send custom application metrics
to the monitoring system for tracking and alerting.
"""

import requests
import time
import random
from datetime import datetime


def submit_metrics(metrics_data):
    """Submit metrics to the monitoring system"""
    try:
        response = requests.post(
            'http://localhost:5000/api/metrics/submit',
            json=metrics_data,
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        if result['success']:
            print(f"✓ Metrics submitted: {metrics_data}")
        else:
            print(f"✗ Failed to submit metrics: {result.get('error')}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"✗ Error submitting metrics: {e}")
        return None


def simulate_application_metrics():
    """Simulate an application generating metrics"""
    print("=" * 60)
    print("Custom Metrics Example - Simulating Application Metrics")
    print("=" * 60)
    print()
    
    # Simulate metrics collection for 5 iterations
    for i in range(5):
        # Generate sample application metrics
        metrics = {
            'application': 'sample-app',
            'timestamp': datetime.now().isoformat(),
            
            # Performance metrics
            'response_time_ms': random.randint(50, 500),
            'requests_per_second': random.randint(100, 1000),
            'error_rate': round(random.uniform(0, 0.05), 4),
            
            # Business metrics
            'active_users': random.randint(10, 100),
            'transactions_completed': random.randint(50, 500),
            'revenue_usd': round(random.uniform(100, 10000), 2),
            
            # Custom application metrics
            'cache_hit_rate': round(random.uniform(0.7, 0.99), 3),
            'database_connection_pool_usage': random.randint(5, 50),
            'queue_length': random.randint(0, 100)
        }
        
        # Submit metrics
        submit_metrics(metrics)
        
        # Wait before next submission
        if i < 4:
            time.sleep(2)
    
    print()
    print("=" * 60)
    print("Example completed! Check the monitoring dashboard at:")
    print("http://localhost:5000")
    print("=" * 60)


def submit_alert_worthy_metrics():
    """Submit metrics that should trigger alerts"""
    print()
    print("Submitting high-threshold metrics to test alerting...")
    
    # Create metrics that would trigger alerts
    critical_metrics = {
        'application': 'test-app',
        'cpu_usage_percent': 95,  # Should trigger CPU alert
        'memory_usage_percent': 92,  # Should trigger memory alert
        'error_rate': 0.25  # High error rate
    }
    
    submit_metrics(critical_metrics)
    print("Check Slack for alert notifications (if configured)")


if __name__ == '__main__':
    # Check if monitoring system is running
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=2)
        if response.status_code == 200:
            print("✓ Monitoring system is running")
            print()
            
            # Run the example
            simulate_application_metrics()
            
            # Optionally test alerts
            # Uncomment to test alert triggering:
            # submit_alert_worthy_metrics()
        else:
            print("✗ Monitoring system returned unexpected status")
    except requests.exceptions.RequestException:
        print("✗ Error: Monitoring system is not running")
        print()
        print("Please start the monitoring system first:")
        print("  python app.py")
        print()
        print("Or use the start scripts:")
        print("  ./start.sh (Linux/Mac)")
        print("  .\\start.ps1 (Windows)")
