# Screenshot Guide for ASL Monitoring System

This guide helps you capture screenshots of the monitoring dashboard for documentation purposes.

## Dashboard Screenshots

### Main Dashboard View

To capture the main dashboard:

1. Start the monitoring system:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Wait a few seconds for metrics to populate

4. Take a screenshot showing:
   - Header with system name and status
   - All metric cards (CPU, Memory, Disk, Network, etc.)
   - Progress bars with current values
   - Alert section

### Dashboard Features to Highlight

**Recommended screenshots:**

1. **Full Dashboard** - Shows all metrics in one view
2. **CPU & Memory Cards** - Close-up of system metrics with progress bars
3. **Disk Usage** - Shows multiple partitions
4. **Alerts Panel** - When alerts are triggered (use high load)
5. **Mobile View** - Responsive design on smaller screens

### Testing Alert Notifications

To generate alerts for screenshots:

```python
# Create a script to simulate high load
import requests

# This will trigger alerts if thresholds are set correctly
metrics = {
    'cpu_usage_percent': 95,
    'memory_usage_percent': 92,
}

requests.post('http://localhost:5000/api/metrics/submit', json=metrics)
```

### Slack Alert Screenshot

If you have Slack configured:

1. Trigger an alert (high CPU/memory usage)
2. Check your Slack channel
3. Capture the alert notification showing:
   - Alert emoji and title
   - Severity level
   - Current value vs threshold
   - Timestamp

## Screenshot Locations

Suggested file structure:
```
screenshots/
  ├── dashboard-main.png
  ├── metrics-cpu-memory.png
  ├── metrics-disk.png
  ├── alerts-panel.png
  ├── slack-notification.png
  └── mobile-view.png
```

## Tools for Screenshots

### Browser Developer Tools
- Press F12 in most browsers
- Toggle device toolbar (Ctrl+Shift+M)
- Select different screen sizes
- Take screenshots of responsive views

### Screenshot Tools
- **Windows**: Snipping Tool or Snip & Sketch
- **macOS**: Cmd+Shift+4 for selection
- **Linux**: Flameshot, GNOME Screenshot

## Embedding in Documentation

Add screenshots to README.md:

```markdown
## Dashboard Preview

![Main Dashboard](screenshots/dashboard-main.png)

### Features

![CPU and Memory Metrics](screenshots/metrics-cpu-memory.png)
```

## Tips for Good Screenshots

1. Use a clean browser window (close unnecessary tabs)
2. Ensure metrics are showing realistic values
3. Capture when status indicators show different states (green/yellow/red)
4. Include the browser address bar to show the URL
5. Use good lighting if capturing on mobile devices
6. Crop unnecessary whitespace
7. Ensure text is readable at the resolution you're sharing
