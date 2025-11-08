# ASL Monitoring System - Examples

This directory contains example scripts demonstrating how to integrate with the ASL Monitoring System.

## Available Examples

### custom_metrics.py
Demonstrates how to submit custom application metrics to the monitoring system.

**Usage:**
```bash
# Make sure the monitoring system is running first
python app.py

# In another terminal, run the example
python examples/custom_metrics.py
```

**What it does:**
- Simulates an application generating various metrics
- Submits metrics to the monitoring API
- Shows how to structure metrics data
- Includes performance, business, and custom metrics

**Sample Metrics Submitted:**
- Response time (ms)
- Requests per second
- Error rate
- Active users
- Transactions completed
- Revenue
- Cache hit rate
- Database pool usage
- Queue length

## Creating Your Own Integration

### Basic Example

```python
import requests

# Your application metrics
metrics = {
    'application': 'my-app',
    'response_time_ms': 250,
    'error_rate': 0.01,
    'active_users': 42
}

# Submit to monitoring system
response = requests.post(
    'http://localhost:5000/api/metrics/submit',
    json=metrics
)

print(response.json())
```

### With Error Handling

```python
import requests

def submit_metrics(metrics):
    try:
        response = requests.post(
            'http://localhost:5000/api/metrics/submit',
            json=metrics,
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to submit metrics: {e}")
        return None

# Use it
result = submit_metrics({
    'metric_name': 'value'
})
```

## Best Practices

1. **Include timestamps**: Add `'timestamp'` field in ISO format
2. **Use consistent naming**: Use snake_case for metric names
3. **Handle errors**: Always handle connection errors gracefully
4. **Don't block**: Submit metrics asynchronously in production
5. **Batch when possible**: Submit multiple metrics together

## Next Steps

- Check the [API Documentation](../docs/API.md) for all available endpoints
- Read the [Monitoring Guide](../docs/MONITORING_GUIDE.md) for setup instructions
- Visit the dashboard at http://localhost:5000 to see your metrics
