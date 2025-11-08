# API Documentation

## ASL Monitoring System API

This document provides information about the API endpoints and integrations used in the ASL Monitoring System.

## Table of Contents

1. [Authentication](#authentication)
2. [Environment Setup](#environment-setup)
3. [Slack Integration](#slack-integration)
4. [API Endpoints](#api-endpoints)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

## Authentication

All API requests require proper authentication. Never hardcode credentials in your code.

### Using Environment Variables

Set up your environment variables before running the application:

```bash
export SLACK_WEBHOOK_URL="your-webhook-url"
export SLACK_API_TOKEN="your-api-token"
export API_KEY="your-api-key"
```

### Using Configuration Files

Create a `.env` file in the project root (this file is gitignored):

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

## Environment Setup

### Required Environment Variables

The following environment variables must be set:

| Variable | Description | Example |
|----------|-------------|---------|
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL | `https://hooks.slack.com/services/T00/B00/XXX` |
| `SLACK_API_TOKEN` | Slack API token for bot integration | `xoxb-000-000-XXX` |
| `API_KEY` | Application API key | `your-api-key-here` |

### Development Setup

```bash
# Copy environment template
cp .env.example .env

# Install dependencies
npm install  # or pip install -r requirements.txt

# Run application
npm start    # or python app.py
```

## Slack Integration

### Webhook Configuration

Slack webhooks allow sending messages to Slack channels.

#### Creating a Slack Webhook

1. Go to https://api.slack.com/apps
2. Create a new app or select an existing one
3. Navigate to "Incoming Webhooks"
4. Activate incoming webhooks
5. Add new webhook to workspace
6. Copy the webhook URL to your `.env` file

**Important:** Never commit the actual webhook URL to version control!

#### Using Webhooks in Code

**Python Example:**
```python
import os
import requests

def send_slack_notification(message):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL environment variable is not set")
    
    payload = {
        'text': message
    }
    
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()
    return response

# Usage
send_slack_notification("✅ Monitoring alert: System is healthy")
```

**JavaScript Example:**
```javascript
const axios = require('axios');

async function sendSlackNotification(message) {
    const webhookUrl = process.env.SLACK_WEBHOOK_URL;
    
    if (!webhookUrl) {
        throw new Error('SLACK_WEBHOOK_URL environment variable is not set');
    }
    
    const payload = {
        text: message
    };
    
    const response = await axios.post(webhookUrl, payload);
    return response.data;
}

// Usage
await sendSlackNotification('✅ Monitoring alert: System is healthy');
```

**PowerShell Example:**
```powershell
function Send-SlackNotification {
    param([string]$Message)
    
    $webhookUrl = $env:SLACK_WEBHOOK_URL
    
    if (-not $webhookUrl) {
        throw "SLACK_WEBHOOK_URL environment variable is not set"
    }
    
    $payload = @{ text = $Message } | ConvertTo-Json
    
    Invoke-RestMethod -Uri $webhookUrl -Method Post -Body $payload -ContentType 'application/json'
}

# Usage
Send-SlackNotification "✅ Monitoring alert: System is healthy"
```

### Slack Bot API

For more advanced integrations, use the Slack Bot API.

#### Setting Up Bot Token

1. Go to https://api.slack.com/apps
2. Select your app
3. Navigate to "OAuth & Permissions"
4. Install app to workspace
5. Copy the "Bot User OAuth Token" (starts with `xoxb-`)
6. Add to your `.env` file as `SLACK_API_TOKEN`

#### Using Bot API in Code

**Python Example:**
```python
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def post_message_to_channel(channel, message):
    token = os.environ.get('SLACK_API_TOKEN')
    
    if not token:
        raise ValueError("SLACK_API_TOKEN environment variable is not set")
    
    client = WebClient(token=token)
    
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=message
        )
        return response
    except SlackApiError as e:
        print(f"Error posting message: {e}")
        raise

# Usage
post_message_to_channel('#monitoring', 'System status: OK')
```

## API Endpoints

### Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API is running

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### Monitoring Data

**Endpoint:** `GET /api/v1/monitoring/data`

**Headers:**
```
Authorization: Bearer ${API_KEY}
Content-Type: application/json
```

**Response:**
```json
{
    "data": [
        {
            "timestamp": "2024-01-01T12:00:00Z",
            "metric": "cpu_usage",
            "value": 45.2
        }
    ]
}
```

### Send Alert

**Endpoint:** `POST /api/v1/alerts`

**Headers:**
```
Authorization: Bearer ${API_KEY}
Content-Type: application/json
```

**Request Body:**
```json
{
    "severity": "warning",
    "message": "CPU usage exceeds threshold",
    "metric": "cpu_usage",
    "value": 85.5
}
```

**Response:**
```json
{
    "alert_id": "alert-123",
    "status": "sent",
    "notification_channels": ["slack"]
}
```

## Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 401 | Unauthorized | Check API key or token |
| 403 | Forbidden | Verify permissions |
| 404 | Not Found | Check endpoint URL |
| 429 | Rate Limited | Implement backoff strategy |
| 500 | Server Error | Check logs and retry |

### Example Error Response

```json
{
    "error": {
        "code": 401,
        "message": "Invalid API token",
        "details": "The provided SLACK_API_TOKEN is invalid or expired"
    }
}
```

## Examples

### Complete Integration Example

**Python:**
```python
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MonitoringSystem:
    def __init__(self):
        self.slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
        self.api_key = os.environ.get('API_KEY')
        
        if not self.slack_webhook:
            raise ValueError("SLACK_WEBHOOK_URL not set")
        if not self.api_key:
            raise ValueError("API_KEY not set")
    
    def check_system_health(self):
        # Your monitoring logic here
        cpu_usage = get_cpu_usage()
        memory_usage = get_memory_usage()
        
        if cpu_usage > 80:
            self.send_alert(f"⚠️ High CPU usage: {cpu_usage}%")
        
        return {
            'cpu': cpu_usage,
            'memory': memory_usage
        }
    
    def send_alert(self, message):
        payload = {'text': message}
        response = requests.post(self.slack_webhook, json=payload)
        response.raise_for_status()
        return response

# Usage
if __name__ == '__main__':
    monitor = MonitoringSystem()
    health = monitor.check_system_health()
    print(f"System health: {health}")
```

### Testing Your Integration

```bash
# Test webhook (replace with your actual webhook URL from .env)
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test message from ASL Monitoring System"}' \
  $SLACK_WEBHOOK_URL

# Expected response: "ok"
```

## Security Best Practices

1. ✅ **Always use environment variables** for sensitive data
2. ✅ **Never commit** `.env` files to version control
3. ✅ **Rotate credentials** regularly
4. ✅ **Use HTTPS** for all API calls
5. ✅ **Implement rate limiting** to prevent abuse
6. ✅ **Log security events** for auditing
7. ❌ **Never hardcode** API tokens or webhook URLs
8. ❌ **Never share** credentials in chat, email, or documentation

### Example of What NOT to Do

```python
# ❌ BAD - Never do this!
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T00000000/B00000000/XXXXX"
SLACK_API_TOKEN = "xoxb-your-token-here"

# ✅ GOOD - Do this instead!
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
```

## Additional Resources

- [Slack API Documentation](https://api.slack.com/)
- [Webhook Security Best Practices](https://api.slack.com/messaging/webhooks)
- [Environment Variables Guide](https://12factor.net/config)
- See `SECURITY.md` for handling secrets safely

## Support

For issues or questions:
- Create an issue on GitHub
- Check the `SECURITY.md` file for security-related concerns
- Review error logs in the application

---

**Remember:** This is a template. Replace all placeholder values with your actual configuration from `.env` file.
