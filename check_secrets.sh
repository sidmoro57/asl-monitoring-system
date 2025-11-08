#!/bin/bash
# Quick script to check for secrets and guide the user

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   ASL Monitoring System - Secret Detection & Fix Helper       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not a git repository"
    exit 1
fi

echo "🔍 Scanning git history for secrets..."
echo ""

# Flag to track if secrets are found
SECRETS_FOUND=0

# Check for Slack webhooks
echo "Checking for Slack webhook URLs..."
if git log --all --full-history -S "hooks.slack.com" --oneline -- . 2>/dev/null | grep -q .; then
    echo "❌ FOUND: Slack webhook URLs in commits:"
    git log --all --full-history -S "hooks.slack.com" --pretty=format:"   %h - %s" -- .
    echo ""
    SECRETS_FOUND=1
else
    echo "✅ No Slack webhooks found in history"
fi
echo ""

# Check for Slack tokens
echo "Checking for Slack API tokens..."
if git log --all --full-history -S "xoxb-" --oneline -- . 2>/dev/null | grep -q .; then
    echo "❌ FOUND: Slack API tokens in commits:"
    git log --all --full-history -S "xoxb-" --pretty=format:"   %h - %s" -- .
    echo ""
    SECRETS_FOUND=1
else
    echo "✅ No Slack tokens found in history"
fi
echo ""

# Check for AWS keys
echo "Checking for AWS access keys..."
if git log --all --full-history -S "AKIA" --oneline -- . 2>/dev/null | grep -q .; then
    echo "⚠️  Possible AWS keys found in commits:"
    git log --all --full-history -S "AKIA" --pretty=format:"   %h - %s" -- .
    echo ""
    SECRETS_FOUND=1
else
    echo "✅ No AWS keys found in history"
fi
echo ""

# Check current working directory for secrets
echo "Checking current files for hardcoded secrets..."
# Look for actual webhook URLs (not just the domain name in search patterns)
if grep -rE "https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[a-zA-Z0-9]+" . --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md" --exclude="check_secrets.*" 2>/dev/null | grep -v "example" | grep -v "template" | grep -q .; then
    echo "❌ FOUND: Hardcoded webhooks in current files:"
    grep -rnE "https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[a-zA-Z0-9]+" . --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md" --exclude="check_secrets.*" 2>/dev/null | grep -v "example" | grep -v "template"
    echo ""
    SECRETS_FOUND=1
fi

# Look for actual Slack tokens (not just the prefix in search patterns)
if grep -rE "xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]{24,}" . --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md" --exclude="check_secrets.*" 2>/dev/null | grep -v "example" | grep -v "template" | grep -q .; then
    echo "❌ FOUND: Hardcoded tokens in current files:"
    grep -rnE "xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]{24,}" . --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md" --exclude="check_secrets.*" 2>/dev/null | grep -v "example" | grep -v "template"
    echo ""
    SECRETS_FOUND=1
fi

echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ $SECRETS_FOUND -eq 1 ]; then
    echo "❌ SECRETS DETECTED!"
    echo ""
    echo "Your repository contains secrets that will block your push."
    echo ""
    echo "📋 Next Steps:"
    echo ""
    echo "1. Read the resolution guide:"
    echo "   - French: RESOLUTION_PUSH_BLOQUE.md"
    echo "   - English: GIT_CLEANUP_GUIDE.md"
    echo ""
    echo "2. Quick fix for recent commits:"
    echo "   - Edit files to use environment variables"
    echo "   - Run: git commit --amend --all"
    echo "   - Run: git push"
    echo ""
    echo "3. For older commits:"
    echo "   - Run: git rebase -i <commit-id>~1"
    echo "   - Edit each commit to remove secrets"
    echo "   - See RESOLUTION_PUSH_BLOQUE.md for details"
    echo ""
    echo "4. Set up your environment:"
    echo "   - Copy: cp .env.example .env"
    echo "   - Edit .env with your actual secrets"
    echo "   - Use templates: fix_and_push.ps1 and docs/API.md"
    echo ""
    echo "5. IMPORTANT: Rotate all exposed secrets!"
    echo "   - Regenerate Slack webhooks"
    echo "   - Regenerate API tokens"
    echo ""
    exit 1
else
    echo "✅ SUCCESS! No secrets detected in your repository."
    echo ""
    echo "Your code is safe to push to GitHub."
    echo ""
    echo "📋 Recommendations:"
    echo ""
    echo "1. Make sure you have a .env file for local secrets:"
    echo "   cp .env.example .env"
    echo ""
    echo "2. Install pre-commit hooks to prevent future issues:"
    echo "   pip install pre-commit detect-secrets"
    echo "   pre-commit install"
    echo ""
    echo "3. Review your changes before pushing:"
    echo "   git diff HEAD~1"
    echo ""
    echo "You can now safely run:"
    echo "   git push origin main"
    echo ""
    exit 0
fi
