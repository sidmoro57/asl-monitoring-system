# Security Policy

## Handling Secrets and Sensitive Information

This repository uses GitHub's push protection to prevent accidental exposure of secrets. If you encounter a blocked push due to secret detection, follow these steps:

### Quick Fix for Blocked Pushes

If your push is blocked due to detected secrets:

1. **DO NOT** use `--force` or `--force-with-lease` to bypass the protection
2. **DO NOT** click the "Allow secret" link in the error message
3. Follow the steps below to properly remove secrets from your commits

### Step 1: Remove Secrets from Files

Replace hardcoded secrets with environment variables:

**Bad (Don't do this):**
```powershell
$webhookUrl = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
```

**Good (Do this instead):**
```powershell
$webhookUrl = $env:SLACK_WEBHOOK_URL
if (-not $webhookUrl) {
    Write-Error "SLACK_WEBHOOK_URL environment variable is not set"
    exit 1
}
```

### Step 2: Create Environment Variables Template

Copy `.env.example` to `.env` and fill in your actual values:
```bash
cp .env.example .env
```

The `.env` file is gitignored and will not be committed.

### Step 3: Clean Git History

If you've already committed secrets, you need to remove them from git history:

#### Option A: Using git filter-repo (Recommended)

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove specific file from history
git filter-repo --path fix_and_push.ps1 --invert-paths

# Or remove specific lines containing secrets
git filter-repo --replace-text <(echo "regex:https://hooks\.slack\.com/services/[A-Z0-9/]+==>SLACK_WEBHOOK_URL_PLACEHOLDER")
```

#### Option B: Using BFG Repo-Cleaner

```bash
# Download BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

# Remove file from history
java -jar bfg.jar --delete-files fix_and_push.ps1

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

#### Option C: Interactive Rebase (for recent commits)

```bash
# For the last N commits
git rebase -i HEAD~N

# Mark commits to edit, then amend them
git commit --amend
git rebase --continue
```

### Step 4: Force Push (After Cleaning History)

**WARNING:** Only do this after removing secrets from history:

```bash
# Verify secrets are removed
git log --all --full-history -S "hooks.slack.com" -- .

# Force push with lease (safer than --force)
git push origin main --force-with-lease
```

### Step 5: Revoke Exposed Secrets

**CRITICAL:** If secrets were pushed to GitHub (even if removed later), they are compromised:

1. **Slack Webhooks:** Regenerate the webhook URL in Slack workspace settings
2. **API Tokens:** Revoke and regenerate tokens in the respective service
3. **AWS Keys:** Rotate credentials immediately via AWS IAM
4. **Database Passwords:** Change passwords immediately

### Prevention Best Practices

1. ✅ Use environment variables for all secrets
2. ✅ Use `.env` files (gitignored) for local development
3. ✅ Use secret management services (AWS Secrets Manager, Azure Key Vault, etc.) for production
4. ✅ Review commits before pushing: `git diff HEAD~1`
5. ✅ Enable pre-commit hooks to scan for secrets locally
6. ❌ Never commit files with names like `secrets.txt`, `credentials.json`, `config.production.js`
7. ❌ Never disable push protection or ignore secret scanning warnings

### Installing Pre-commit Secret Scanning

Detect secrets before committing:

```bash
# Install pre-commit
pip install pre-commit

# Install detect-secrets
pip install detect-secrets

# Run scan on repository
detect-secrets scan --baseline .secrets.baseline

# Add to pre-commit hook
detect-secrets-hook --baseline .secrets.baseline
```

## Reporting Security Issues

If you discover a security vulnerability, please email security@example.com instead of creating a public issue.
