# ASL Real-time Monitoring System - User Guide

## Overview

The ASL Monitoring System provides real-time monitoring of system and application health with an interactive web dashboard and Slack alerting capabilities.

## Features

### 📊 Real-time Metrics Collection
- **CPU Monitoring**: Usage percentage, core count, frequency
- **Memory Monitoring**: RAM usage, available memory, swap usage
- **Disk Monitoring**: Usage per partition, I/O statistics
- **Network Monitoring**: Bytes sent/received, packet statistics
- **System Information**: Uptime, boot time

### 🎯 Interactive Dashboard
- Live metrics updated every 5 seconds (configurable)
- Visual progress bars and status indicators
- Color-coded alerts (green/yellow/red)
- Responsive design for desktop and mobile

### ⚠️ Intelligent Alerting
- Configurable thresholds for all metrics
- Slack integration for instant notifications
- Alert cooldown to prevent notification spam
- Alert history tracking

### 💾 Data Persistence
- In-memory storage for fast access
- Optional file-based persistence (JSONL format)
- Historical data retrieval via API

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/sidmoro57/asl-monitoring-system.git
cd asl-monitoring-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

4. **Run the monitoring system**
```bash
python app.py
```

5. **Access the dashboard**
Open your browser and navigate to:
```
http://localhost:5000
```

## Configuration

### Environment Variables

Edit the `.env` file to configure the monitoring system:

```bash
# Application Settings
PORT=5000                    # Web server port
DEBUG=False                  # Enable debug mode (True/False)
MONITORING_INTERVAL=5        # Metrics collection interval (seconds)

# Slack Integration (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_API_TOKEN=xoxb-your-slack-api-token-here

# Alert Thresholds (percentage)
ALERT_CPU_THRESHOLD=80       # CPU usage alert threshold
ALERT_MEMORY_THRESHOLD=85    # Memory usage alert threshold
ALERT_DISK_THRESHOLD=90      # Disk usage alert threshold
ALERT_SWAP_THRESHOLD=75      # Swap usage alert threshold
ALERT_COOLDOWN_SECONDS=300   # Time between duplicate alerts

# Data Storage
METRICS_DATA_FILE=data/metrics.jsonl  # Metrics storage file
```

### Slack Integration Setup

1. **Create a Slack App**
   - Go to https://api.slack.com/apps
   - Click "Create New App"
   - Choose "From scratch"
   - Give it a name (e.g., "ASL Monitor")

2. **Enable Incoming Webhooks**
   - Navigate to "Incoming Webhooks"
   - Activate incoming webhooks
   - Click "Add New Webhook to Workspace"
   - Select the channel for alerts
   - Copy the webhook URL

3. **Add to .env file**
   ```bash
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000/B00000/XXXXX
   ```

## Usage

### Web Dashboard

#### Main Features
- **Live Metrics**: View real-time system statistics
- **Refresh Control**: Manual refresh or auto-refresh toggle
- **Status Indicators**: Color-coded badges showing system health
- **Alert History**: View recent alerts in the dashboard

#### Dashboard Controls
- **🔄 Refresh Now**: Manually update all metrics
- **⏸️ Pause Monitoring**: Temporarily pause background monitoring
- **Auto-refresh Toggle**: Enable/disable automatic updates

### API Endpoints

The monitoring system provides a RESTful API for integration:

#### Get Current Metrics
```bash
GET /api/metrics/current

Response:
{
  "success": true,
  "data": {
    "timestamp": "2024-01-15T10:30:00",
    "cpu": { "usage_percent": 45.2, ... },
    "memory": { "usage_percent": 62.5, ... },
    ...
  }
}
```

#### Get Metrics History
```bash
GET /api/metrics/history?limit=100

Response:
{
  "success": true,
  "data": [...]
}
```

#### Submit Custom Metrics
```bash
POST /api/metrics/submit
Content-Type: application/json

{
  "custom_metric": "value",
  "response_time_ms": 250
}
```

#### Configure Alert Thresholds
```bash
POST /api/alerts/configure
Content-Type: application/json

{
  "cpu_usage_percent": 85,
  "memory_usage_percent": 90
}
```

#### Get Alert History
```bash
GET /api/alerts/history?limit=50
```

#### Health Check
```bash
GET /api/health
```

#### Start/Stop Monitoring
```bash
POST /api/monitoring/start
POST /api/monitoring/stop
```

### Python API Usage

You can also use the monitoring system programmatically:

```python
from modules.metrics_collector import MetricsCollector
from modules.data_store import DataStore

# Initialize
data_store = DataStore()
collector = MetricsCollector(data_store)

# Collect metrics
metrics = collector.collect()
print(f"CPU Usage: {metrics['cpu']['usage_percent']}%")
```

## Alert Notifications

### Alert Severity Levels
- **Normal** (Green): Metrics within acceptable range
- **Warning** (Yellow): Metrics approaching threshold (75-89%)
- **Critical** (Red): Metrics exceeding threshold (90%+)

### Slack Alert Format
Alerts sent to Slack include:
- Severity level with emoji indicator
- Metric name and description
- Current value vs. threshold
- Timestamp

### Alert Cooldown
To prevent alert spam, each alert type has a cooldown period (default: 5 minutes). During this time, duplicate alerts for the same metric are suppressed.

## Advanced Usage

### Custom Metrics Integration

Send custom application metrics to the monitoring system:

```python
import requests

# Submit custom metrics
data = {
    "application": "my-app",
    "response_time_ms": 250,
    "requests_per_second": 1500,
    "error_rate": 0.02
}

response = requests.post(
    'http://localhost:5000/api/metrics/submit',
    json=data
)
```

### Data Persistence

By default, metrics are stored both in memory and in a JSONL file:
- **In-memory**: Last 1000 metrics (fast access)
- **File storage**: `data/metrics.jsonl` (persistent)

To load historical data:
```python
from modules.data_store import DataStore

store = DataStore()
history = store.load_from_file(limit=1000)
```

### Cleanup Old Data

Remove metrics older than specified days:
```python
from modules.data_store import DataStore

store = DataStore()
store.clear_old_data(days=7)  # Keep only last 7 days
```

## Deployment

### Production Deployment

For production use, consider:

1. **Use a production WSGI server**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **Set up as a system service** (Linux)
```bash
# Create /etc/systemd/system/asl-monitoring.service
[Unit]
Description=ASL Monitoring System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/asl-monitoring-system
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. **Enable and start the service**
```bash
sudo systemctl enable asl-monitoring
sudo systemctl start asl-monitoring
```

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t asl-monitoring .
docker run -d -p 5000:5000 --env-file .env asl-monitoring
```

## Troubleshooting

### Common Issues

**Problem**: Dashboard not updating
- **Solution**: Check browser console for errors, verify the API endpoints are accessible

**Problem**: Alerts not sending to Slack
- **Solution**: Verify `SLACK_WEBHOOK_URL` is correctly set in `.env` file

**Problem**: High memory usage
- **Solution**: Reduce `max_memory_items` in DataStore or enable file-only persistence

**Problem**: Permission errors reading disk metrics
- **Solution**: Run with appropriate permissions or ignore specific partitions

### Debug Mode

Enable debug mode for detailed logging:
```bash
# In .env file
DEBUG=True
```

## Security Best Practices

1. ✅ Never commit `.env` files to version control
2. ✅ Use environment variables for all sensitive data
3. ✅ Rotate Slack webhook URLs if exposed
4. ✅ Run the application with minimal required permissions
5. ✅ Use HTTPS in production (reverse proxy with nginx/Apache)
6. ✅ Implement authentication for production deployments

## Performance Considerations

- **Monitoring Interval**: Lower intervals provide more granular data but use more resources
- **Data Retention**: Limit historical data storage based on your needs
- **Alert Cooldown**: Adjust to balance between timely notifications and alert fatigue

## Support

For issues, questions, or contributions:
- Create an issue on GitHub: https://github.com/sidmoro57/asl-monitoring-system/issues
- Check existing documentation in the `docs/` folder
- Review the API documentation: `docs/API.md`

## License

[Add your license information here]

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-08
