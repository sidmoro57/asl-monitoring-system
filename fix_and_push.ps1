# PowerShell script to fix and push changes
# This script demonstrates proper secret handling using environment variables

# Load environment variables from .env file if it exists
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# Get Slack webhook URL from environment variable
$webhookUrl = $env:SLACK_WEBHOOK_URL

# Validate that the webhook URL is set
if (-not $webhookUrl) {
    Write-Host "❌ Error: SLACK_WEBHOOK_URL environment variable is not set" -ForegroundColor Red
    Write-Host "Please set the SLACK_WEBHOOK_URL environment variable or create a .env file" -ForegroundColor Yellow
    Write-Host "See .env.example for template" -ForegroundColor Yellow
    exit 1
}

# Validate webhook URL format (basic check)
if ($webhookUrl -notmatch '^https://hooks\.slack\.com/services/') {
    Write-Host "❌ Error: Invalid Slack webhook URL format" -ForegroundColor Red
    exit 1
}

Write-Host "Starting git operations..." -ForegroundColor Cyan

# Check git status
git status

# Add all changes
Write-Host "Adding changes..." -ForegroundColor Cyan
git add .

# Commit changes
$commitMessage = Read-Host "Enter commit message"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

git commit -m $commitMessage

# Push to remote
Write-Host "Pushing to remote..." -ForegroundColor Cyan
git push origin main

# Check if push was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Push successful! Your changes are now on GitHub" -ForegroundColor Green
    
    # Send Slack notification (optional)
    $slackMessage = @{
        text = "✅ Code pushed successfully to repository`nCommit: $commitMessage`nTime: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri $webhookUrl -Method Post -Body $slackMessage -ContentType 'application/json'
        Write-Host "✅ Slack notification sent" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Warning: Could not send Slack notification: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Push failed. Please check the error message above." -ForegroundColor Red
    Write-Host "" -ForegroundColor Red
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  1. Secret detected: Remove hardcoded secrets from your code" -ForegroundColor Yellow
    Write-Host "  2. Large files: Use Git LFS for files over 50MB" -ForegroundColor Yellow
    Write-Host "  3. Merge conflicts: Pull latest changes first" -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Write-Host "See SECURITY.md for help with secret scanning issues" -ForegroundColor Cyan
    exit 1
}
