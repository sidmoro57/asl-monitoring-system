# ASL Monitoring System - Usage Examples

## Basic Usage

### 1. Set up environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Slack webhook URL:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
CHECK_INTERVAL=60
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the monitoring system

```bash
python3 app.py
```

Expected output:
```
2025-11-08 07:00:00,000 - __main__ - INFO - === ASL Monitoring System ===
2025-11-08 07:00:00,001 - __main__ - INFO - Starting ASL monitoring system...
2025-11-08 07:00:00,002 - app - INFO - Slack notification sent successfully: ASL Monitoring System started
Check interval: 60 seconds
Started at: 2025-11-08 07:00:00
```

### 4. Stop the monitoring system

Press `Ctrl+C` to gracefully stop the monitoring system.

## Running Tests

```bash
# Run all unit tests
python3 test_app.py -v

# Expected output:
# test_check_asl_system ... ok
# test_get_health_status ... ok
# test_init_with_valid_config ... ok
# test_init_without_webhook_url ... ok
# test_stop_monitoring ... ok
# test_init_with_empty_url ... ok
# test_init_with_invalid_url ... ok
# test_init_with_valid_url ... ok
# test_send_notification_failure ... ok
# test_send_notification_success ... ok
# 
# Ran 10 tests in 0.XXXs
# OK
```

## Customizing the Monitoring System

The `check_asl_system()` method in `app.py` is a placeholder that can be customized based on your specific monitoring needs. For example:

```python
def check_asl_system(self) -> bool:
    """
    Perform a health check on the ASL system.
    """
    try:
        # Example: Check if ASL application endpoint is responding
        response = requests.get('http://localhost:8080/health', timeout=5)
        is_healthy = response.status_code == 200
        
        # Example: Check database connection
        # db_healthy = check_database_connection()
        
        # Example: Check resource usage
        # cpu_ok = get_cpu_usage() < 80
        # memory_ok = get_memory_usage() < 90
        
        return is_healthy
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SLACK_WEBHOOK_URL` | Yes | - | Slack incoming webhook URL for notifications |
| `CHECK_INTERVAL` | No | 60 | Health check interval in seconds |

## Slack Notifications

The monitoring system sends Slack notifications for:

1. **Startup**: When the monitoring system starts
2. **Health Check Failures**: When a health check fails
3. **Shutdown**: When the monitoring system stops
4. **Errors**: When unexpected errors occur

Example notification format:
```
✅ ASL Monitoring System started
Check interval: 60 seconds
Started at: 2025-11-08 07:00:00
```

## Logging

All activity is logged to:
- **File**: `asl_monitoring.log` (in the project directory)
- **Console**: Standard output

Log levels:
- `INFO`: Normal operations
- `WARNING`: Potential issues
- `ERROR`: Errors and failures
- `DEBUG`: Detailed debug information

## Security Best Practices

1. ✅ Never commit your `.env` file
2. ✅ Use environment variables for all secrets
3. ✅ Rotate Slack webhooks if accidentally exposed
4. ✅ Keep dependencies up to date
5. ✅ Review logs regularly for security issues

## Troubleshooting

### Error: "SLACK_WEBHOOK_URL environment variable is not set"

**Solution**: Create a `.env` file with your Slack webhook URL:
```bash
cp .env.example .env
# Edit .env and add your webhook URL
```

### Error: "Invalid Slack webhook URL format"

**Solution**: Ensure your webhook URL starts with `https://hooks.slack.com/services/`

### Tests failing

**Solution**: Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```
