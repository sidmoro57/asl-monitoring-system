# ASL Monitoring System

A real-time monitoring system for ASL (American Sign Language) applications with live dashboard, metrics collection, and Slack integration.

![ASL Monitoring Dashboard](https://github.com/user-attachments/assets/2852b99d-b38f-4a94-94ac-3f5c822f0215)

## 🚀 Features

### Real-time Monitoring Dashboard
- **Live Metrics**: CPU, Memory, Disk, and Network monitoring
- **Interactive UI**: Web-based dashboard with real-time updates
- **Visual Alerts**: Color-coded status indicators and progress bars
- **Historical Data**: Track metrics over time with data persistence

### Intelligent Alerting
- **Slack Integration**: Instant notifications when thresholds are exceeded
- **Configurable Thresholds**: Customize alert levels for all metrics
- **Alert Management**: Cooldown periods to prevent notification spam
- **Alert History**: Track all alerts in the dashboard

### RESTful API
- Submit custom metrics from your applications
- Retrieve current and historical data
- Configure alert thresholds programmatically
- Health check endpoints

## 🚨 PUSH BLOQUÉ? → [START_HERE.md](START_HERE.md) 🚨

Si votre push a été bloqué par GitHub à cause de secrets détectés, **lisez immédiatement [START_HERE.md](START_HERE.md)** pour la solution rapide!

---

## 🚨 Important: Secret Management

**This repository uses GitHub push protection to prevent accidental exposure of secrets.**

If your push was blocked due to detected secrets:
1. ❌ **DO NOT** bypass the protection
2. ✅ **DO** follow the guide in `SECURITY.md` to properly handle secrets
3. ✅ **DO** use environment variables instead of hardcoded values
4. ✅ **DO** clean your git history if secrets were committed

See **[SECURITY.md](SECURITY.md)** for detailed instructions.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/sidmoro57/asl-monitoring-system.git
cd asl-monitoring-system
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your actual credentials
# Never commit this file - it's gitignored
nano .env
```

### 4. Start the Monitoring System

```bash
python app.py
```

### 5. Access the Dashboard

Open your browser and navigate to:
```
http://localhost:5000
```

You should see the real-time monitoring dashboard with live metrics!

## Files in This Repository

### Application Files
- **`app.py`** - Main Flask application and API server
- **`requirements.txt`** - Python dependencies
- **`modules/`** - Core monitoring modules
  - `metrics_collector.py` - System metrics collection
  - `alert_manager.py` - Alert management and Slack notifications
  - `data_store.py` - Metrics data storage and persistence
- **`templates/`** - HTML templates for the web dashboard
- **`static/`** - CSS and JavaScript for the dashboard UI

### Configuration & Documentation
- **`.env.example`** - Template for environment variables (safe to commit)
- **`.env`** - Your actual secrets (never commit this - it's gitignored)
- **`docs/MONITORING_GUIDE.md`** - Complete monitoring system documentation
- **`docs/API.md`** - API documentation with integration examples
- **`SECURITY.md`** - Security best practices and secret handling guide
- **`GIT_CLEANUP_GUIDE.md`** - How to remove secrets from git history

### Utility Scripts
- **`fix_and_push.ps1`** - PowerShell script for git operations with Slack notifications
- **`check_secrets.ps1`** / **`check_secrets.sh`** - Scripts to detect secrets in your repo

## Using the Monitoring System

### Web Dashboard

Access the real-time dashboard at `http://localhost:5000`:

- **Live Metrics**: View CPU, memory, disk, and network statistics
- **Visual Indicators**: Color-coded status badges and progress bars
- **Alert History**: See recent alerts and notifications
- **Controls**: Pause/resume monitoring, manual refresh, auto-refresh toggle

### API Endpoints

```bash
# Get current metrics
curl http://localhost:5000/api/metrics/current

# Get metrics history
curl http://localhost:5000/api/metrics/history?limit=100

# Submit custom metrics
curl -X POST http://localhost:5000/api/metrics/submit \
  -H "Content-Type: application/json" \
  -d '{"custom_metric": "value"}'

# Health check
curl http://localhost:5000/api/health
```

### Slack Alerts

Configure Slack integration in your `.env` file:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

The system will automatically send alerts to Slack when metrics exceed thresholds:
- CPU usage > 80%
- Memory usage > 85%
- Disk usage > 90%
- Swap usage > 75%

Thresholds are configurable via environment variables.

### PowerShell Push Script

```powershell
# Make sure your .env file is set up first
./fix_and_push.ps1
```

This script will:
- Load environment variables from `.env`
- Add and commit changes
- Push to GitHub
- Send a Slack notification on success

## If Your Push Was Blocked

GitHub detected secrets in your code. Here's what to do:

### Option 1: Fix Current Files (Quick Fix)

1. Edit files to use environment variables instead of hardcoded secrets
2. Follow examples in `docs/API.md`
3. Update your `.env` file with actual values
4. Commit the changes

### Option 2: Clean Git History (Required if secrets in history)

If secrets exist in previous commits:

1. Read **`GIT_CLEANUP_GUIDE.md`** carefully
2. Use `git filter-repo` or BFG Repo-Cleaner to remove secrets
3. Force push the cleaned history
4. **Immediately rotate the exposed secrets**

See the full guide: **[GIT_CLEANUP_GUIDE.md](GIT_CLEANUP_GUIDE.md)**

## Documentation

- **[Monitoring System Guide](docs/MONITORING_GUIDE.md)** - Complete documentation for the real-time monitoring system
- **[API Documentation](docs/API.md)** - Integration examples and API reference
- **[Security Guide](SECURITY.md)** - Best practices for handling secrets
- **[Git Cleanup Guide](GIT_CLEANUP_GUIDE.md)** - Remove secrets from history

## Security Best Practices

✅ **DO:**
- Use environment variables for all secrets
- Keep `.env` file local (it's gitignored)
- Review code before committing: `git diff`
- Use the provided templates in this repository
- Rotate secrets if they were ever exposed

❌ **DON'T:**
- Hardcode secrets in code files
- Commit `.env` files
- Share secrets in chat or email
- Bypass GitHub push protection
- Ignore secret scanning alerts

## Common Issues

### "Push declined due to repository rule violations"

**Cause:** GitHub detected secrets in your commits

**Solution:**
1. See [SECURITY.md](SECURITY.md) - Section "Quick Fix for Blocked Pushes"
2. Remove hardcoded secrets from files
3. Use environment variables instead
4. Clean git history if needed
5. Rotate exposed secrets

### "Large file detected"

**Cause:** File exceeds GitHub's 50MB recommendation

**Solution:**
1. Use Git LFS for large files: `git lfs track "*.msi"`
2. Or remove large files: `git rm --cached large-file.msi`

## Getting Help

1. Read the documentation files in this repository
2. Check [SECURITY.md](SECURITY.md) for security issues
3. Create an issue on GitHub for other problems

## Contributing

Before contributing:
1. Set up your `.env` file with your own credentials
2. Never commit `.env` or files with secrets
3. Run pre-commit hooks if configured
4. Test your changes locally

## License

[Add your license here]

## Support

For security issues, see [SECURITY.md](SECURITY.md).

---

**Remember:** Protecting secrets is critical. Always use environment variables and never commit sensitive data.

