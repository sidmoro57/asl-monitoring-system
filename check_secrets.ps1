# Quick script to check for secrets and guide the user
# check_secrets.ps1

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   ASL Monitoring System - Secret Detection & Fix Helper       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a git repository
try {
    git rev-parse --git-dir 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error: Not a git repository" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: Not a git repository" -ForegroundColor Red
    exit 1
}

Write-Host "🔍 Scanning git history for secrets..." -ForegroundColor Yellow
Write-Host ""

# Flag to track if secrets are found
$secretsFound = $false

# Check for Slack webhooks
Write-Host "Checking for Slack webhook URLs..." -ForegroundColor Cyan
$webhookCommits = git log --all --full-history -S "hooks.slack.com" --oneline -- . 2>$null
if ($webhookCommits) {
    Write-Host "❌ FOUND: Slack webhook URLs in commits:" -ForegroundColor Red
    git log --all --full-history -S "hooks.slack.com" --pretty=format:"   %h - %s" -- . 2>$null
    Write-Host ""
    $secretsFound = $true
} else {
    Write-Host "✅ No Slack webhooks found in history" -ForegroundColor Green
}
Write-Host ""

# Check for Slack tokens
Write-Host "Checking for Slack API tokens..." -ForegroundColor Cyan
$tokenCommits = git log --all --full-history -S "xoxb-" --oneline -- . 2>$null
if ($tokenCommits) {
    Write-Host "❌ FOUND: Slack API tokens in commits:" -ForegroundColor Red
    git log --all --full-history -S "xoxb-" --pretty=format:"   %h - %s" -- . 2>$null
    Write-Host ""
    $secretsFound = $true
} else {
    Write-Host "✅ No Slack tokens found in history" -ForegroundColor Green
}
Write-Host ""

# Check for AWS keys
Write-Host "Checking for AWS access keys..." -ForegroundColor Cyan
$awsCommits = git log --all --full-history -S "AKIA" --oneline -- . 2>$null
if ($awsCommits) {
    Write-Host "⚠️  Possible AWS keys found in commits:" -ForegroundColor Yellow
    git log --all --full-history -S "AKIA" --pretty=format:"   %h - %s" -- . 2>$null
    Write-Host ""
    $secretsFound = $true
} else {
    Write-Host "✅ No AWS keys found in history" -ForegroundColor Green
}
Write-Host ""

# Check current working directory for secrets
Write-Host "Checking current files for hardcoded secrets..." -ForegroundColor Cyan
# Look for actual webhook URLs (not just the domain name in search patterns)
$currentWebhooks = Select-String -Path . -Pattern "https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[a-zA-Z0-9]+" -Recurse 2>$null | 
    Where-Object { 
        $_.Path -notmatch "\.git" -and 
        $_.Path -notmatch "node_modules" -and 
        $_.Path -notmatch "\.md$" -and
        $_.Path -notmatch "check_secrets" -and
        $_.Line -notmatch "example" -and
        $_.Line -notmatch "template"
    }
if ($currentWebhooks) {
    Write-Host "❌ FOUND: Hardcoded webhooks in current files:" -ForegroundColor Red
    $currentWebhooks | ForEach-Object { Write-Host "   $($_.Path):$($_.LineNumber)" -ForegroundColor Red }
    Write-Host ""
    $secretsFound = $true
}

# Look for actual Slack tokens (not just the prefix in search patterns)
$currentTokens = Select-String -Path . -Pattern "xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]{24,}" -Recurse 2>$null | 
    Where-Object { 
        $_.Path -notmatch "\.git" -and 
        $_.Path -notmatch "node_modules" -and 
        $_.Path -notmatch "\.md$" -and
        $_.Path -notmatch "check_secrets" -and
        $_.Line -notmatch "example" -and
        $_.Line -notmatch "template"
    }
if ($currentTokens) {
    Write-Host "❌ FOUND: Hardcoded tokens in current files:" -ForegroundColor Red
    $currentTokens | ForEach-Object { Write-Host "   $($_.Path):$($_.LineNumber)" -ForegroundColor Red }
    Write-Host ""
    $secretsFound = $true
}

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($secretsFound) {
    Write-Host "❌ SECRETS DETECTED!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Your repository contains secrets that will block your push." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Read the resolution guide:" -ForegroundColor White
    Write-Host "   - French: RESOLUTION_PUSH_BLOQUE.md" -ForegroundColor Gray
    Write-Host "   - English: GIT_CLEANUP_GUIDE.md" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Quick fix for recent commits:" -ForegroundColor White
    Write-Host "   - Edit files to use environment variables" -ForegroundColor Gray
    Write-Host "   - Run: git commit --amend --all" -ForegroundColor Gray
    Write-Host "   - Run: git push" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. For older commits:" -ForegroundColor White
    Write-Host "   - Run: git rebase -i <commit-id>~1" -ForegroundColor Gray
    Write-Host "   - Edit each commit to remove secrets" -ForegroundColor Gray
    Write-Host "   - See RESOLUTION_PUSH_BLOQUE.md for details" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Set up your environment:" -ForegroundColor White
    Write-Host "   - Copy: cp .env.example .env" -ForegroundColor Gray
    Write-Host "   - Edit .env with your actual secrets" -ForegroundColor Gray
    Write-Host "   - Use templates: fix_and_push.ps1 and docs/API.md" -ForegroundColor Gray
    Write-Host ""
    Write-Host "5. IMPORTANT: Rotate all exposed secrets!" -ForegroundColor Red
    Write-Host "   - Regenerate Slack webhooks" -ForegroundColor Yellow
    Write-Host "   - Regenerate API tokens" -ForegroundColor Yellow
    Write-Host ""
    exit 1
} else {
    Write-Host "✅ SUCCESS! No secrets detected in your repository." -ForegroundColor Green
    Write-Host ""
    Write-Host "Your code is safe to push to GitHub." -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Recommendations:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Make sure you have a .env file for local secrets:" -ForegroundColor White
    Write-Host "   cp .env.example .env" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Install pre-commit hooks to prevent future issues:" -ForegroundColor White
    Write-Host "   pip install pre-commit detect-secrets" -ForegroundColor Gray
    Write-Host "   pre-commit install" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Review your changes before pushing:" -ForegroundColor White
    Write-Host "   git diff HEAD~1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "You can now safely run:" -ForegroundColor Green
    Write-Host "   git push origin main" -ForegroundColor Cyan
    Write-Host ""
    exit 0
}
