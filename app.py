"""
ASL Monitoring System - Real-time Application Monitoring
Main application entry point
"""

import os
import json
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from datetime import datetime
import threading
import time

from modules.metrics_collector import MetricsCollector
from modules.alert_manager import AlertManager
from modules.data_store import DataStore

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize components
data_store = DataStore()
metrics_collector = MetricsCollector(data_store)
alert_manager = AlertManager(
    slack_webhook_url=os.getenv('SLACK_WEBHOOK_URL'),
    data_store=data_store
)

# Global flag for background monitoring
monitoring_active = False
monitoring_thread = None


def background_monitoring():
    """Background thread for continuous monitoring"""
    global monitoring_active
    while monitoring_active:
        try:
            # Collect metrics
            metrics = metrics_collector.collect()
            
            # Check for alerts
            alert_manager.check_thresholds(metrics)
            
            # Wait before next collection (configurable interval)
            interval = int(os.getenv('MONITORING_INTERVAL', '5'))
            time.sleep(interval)
        except Exception as e:
            print(f"Error in background monitoring: {e}")
            time.sleep(5)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/metrics/current')
def get_current_metrics():
    """Get current system metrics"""
    try:
        metrics = metrics_collector.collect()
        return jsonify({
            'success': True,
            'data': metrics,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        # Log the error internally
        print(f"Error collecting metrics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to collect metrics'
        }), 500


@app.route('/api/metrics/history')
def get_metrics_history():
    """Get historical metrics data"""
    try:
        limit = request.args.get('limit', 100, type=int)
        history = data_store.get_history(limit)
        return jsonify({
            'success': True,
            'data': history
        })
    except Exception as e:
        # Log the error internally
        print(f"Error retrieving metrics history: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve metrics history'
        }), 500


@app.route('/api/metrics/submit', methods=['POST'])
def submit_metrics():
    """Endpoint for external applications to submit custom metrics"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Add timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        # Store the metrics
        data_store.store(data)
        
        # Check for alerts on custom metrics
        alert_manager.check_thresholds(data)
        
        return jsonify({
            'success': True,
            'message': 'Metrics submitted successfully'
        })
    except Exception as e:
        # Log the error internally
        print(f"Error submitting metrics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to submit metrics'
        }), 500


@app.route('/api/alerts/configure', methods=['POST'])
def configure_alerts():
    """Configure alert thresholds"""
    try:
        data = request.get_json()
        alert_manager.update_thresholds(data)
        return jsonify({
            'success': True,
            'message': 'Alert thresholds updated'
        })
    except Exception as e:
        # Log the error internally
        print(f"Error configuring alerts: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to configure alert thresholds'
        }), 500


@app.route('/api/alerts/history')
def get_alert_history():
    """Get alert history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        alerts = alert_manager.get_alert_history(limit)
        return jsonify({
            'success': True,
            'data': alerts
        })
    except Exception as e:
        # Log the error internally
        print(f"Error retrieving alert history: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve alert history'
        }), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'monitoring_active': monitoring_active,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start background monitoring"""
    global monitoring_active, monitoring_thread
    
    if monitoring_active:
        return jsonify({
            'success': False,
            'message': 'Monitoring is already active'
        })
    
    monitoring_active = True
    monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitoring_thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Monitoring started'
    })


@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop background monitoring"""
    global monitoring_active
    
    if not monitoring_active:
        return jsonify({
            'success': False,
            'message': 'Monitoring is not active'
        })
    
    monitoring_active = False
    
    return jsonify({
        'success': True,
        'message': 'Monitoring stopped'
    })


if __name__ == '__main__':
    # Start background monitoring on startup
    monitoring_active = True
    monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitoring_thread.start()
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print("=" * 50)
    print("ASL Monitoring System - Real-time Dashboard")
    print("=" * 50)
    print(f"Dashboard URL: http://localhost:{port}")
    print(f"Monitoring interval: {os.getenv('MONITORING_INTERVAL', '5')} seconds")
    print(f"Slack alerts: {'Enabled' if os.getenv('SLACK_WEBHOOK_URL') else 'Disabled'}")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
