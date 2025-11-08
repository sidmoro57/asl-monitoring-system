# Git History Cleanup Guide

This guide helps you remove secrets that were accidentally committed to your git repository.

## ⚠️ Important Warning

**Before you start:**
- Cleaning git history rewrites commits
- This will require a force push
- Coordinate with your team before doing this
- All collaborators will need to re-clone or reset their local repositories
- Any secrets that were pushed to GitHub are considered compromised and must be rotated

## Prerequisites

Make sure you have:
1. A backup of your repository: `git clone --mirror <repo-url> backup.git`
2. All local changes committed or stashed
3. Coordination with team members (they'll need to re-clone)

## Method 1: Using git filter-repo (Recommended)

`git filter-repo` is the modern, fast, and safe way to rewrite git history.

### Installation

```bash
# macOS
brew install git-filter-repo

# Linux (Debian/Ubuntu)
sudo apt-get install git-filter-repo

# Using pip
pip install git-filter-repo

# Windows (with Python)
pip install git-filter-repo
```

### Remove Specific Files

If you want to completely remove files from history:

```bash
# Remove a single file
git filter-repo --path fix_and_push.ps1 --invert-paths

# Remove multiple files
git filter-repo --path fix_and_push.ps1 --path secrets.txt --invert-paths

# Remove an entire directory
git filter-repo --path secrets/ --invert-paths
```

### Replace Secrets with Placeholders

If you want to keep the files but replace secret values:

```bash
# Create a replacements file
cat > replacements.txt << 'EOF'
regex:https://hooks\.slack\.com/services/[A-Z0-9/]+==><SLACK_WEBHOOK_URL>
regex:xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]+==><SLACK_API_TOKEN>
regex:AKIA[0-9A-Z]{16}==><AWS_ACCESS_KEY>
EOF

# Apply replacements
git filter-repo --replace-text replacements.txt
```

### Remove Specific Lines from Files

```bash
# This removes lines containing specific patterns
git filter-repo --replace-text <(cat << 'EOF'
$webhookUrl = "https://hooks.slack.com===>${webhookUrl = $env:SLACK_WEBHOOK_URL
EOF
)
```

## Method 2: Using BFG Repo-Cleaner

BFG is faster than git-filter-branch but less flexible than git-filter-repo.

### Installation

```bash
# Download BFG
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar
# or
curl -L https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar -o bfg.jar
```

### Remove Files

```bash
# Remove specific file from history
java -jar bfg.jar --delete-files fix_and_push.ps1

# Remove files by pattern
java -jar bfg.jar --delete-files "*.key"

# Remove folders
java -jar bfg.jar --delete-folders secrets
```

### Replace Text

```bash
# Create replacement file
cat > passwords.txt << 'EOF'
https://hooks.slack.com/services/T00000000/B00000000/XXXXX
xoxb-YOUR-SLACK-TOKEN-HERE
EOF

# Replace with placeholder
java -jar bfg.jar --replace-text passwords.txt
```

## Method 3: Interactive Rebase (For Recent Commits)

Use this only if the secret was committed recently (last few commits).

### Step-by-Step

```bash
# Start interactive rebase for last N commits
git rebase -i HEAD~5

# In the editor, mark commits to edit:
# Change 'pick' to 'edit' for commits with secrets
# Save and close

# For each commit marked as 'edit':
# 1. Remove the secret from the file
nano fix_and_push.ps1  # or your editor

# 2. Stage the changes
git add fix_and_push.ps1

# 3. Amend the commit
git commit --amend --no-edit

# 4. Continue rebase
git rebase --continue

# Repeat for each commit
```

## Method 4: Reset and Recommit (Nuclear Option)

If you want to start fresh and the repository is new:

```bash
# Save current files
cp -r /path/to/repo /path/to/backup

# Remove git history
rm -rf .git

# Initialize new repository
git init

# Remove secrets from files
# Edit files to use environment variables

# Make initial commit
git add .
git commit -m "Initial commit with secrets removed"

# Force push to remote
git remote add origin <repo-url>
git push -u origin main --force
```

## After Cleaning History

### Step 1: Verify Secrets are Removed

```bash
# Search for webhook patterns
git log --all --full-history -S "hooks.slack.com" -- .

# Search for token patterns  
git log --all --full-history -S "xoxb-" -- .

# Search in all files
git grep -i "hooks.slack.com" $(git rev-list --all)

# If these return nothing, secrets are removed
```

### Step 2: Clean Up Local Repository

```bash
# Remove reflog
git reflog expire --expire=now --all

# Garbage collect
git gc --prune=now --aggressive

# Verify repository size decreased
du -sh .git
```

### Step 3: Force Push to Remote

⚠️ **This will overwrite remote history**

```bash
# Push with force-with-lease (safer than --force)
git push origin main --force-with-lease

# If you have multiple branches
git push origin --force-with-lease --all

# Push tags if needed
git push origin --force-with-lease --tags
```

### Step 4: Notify Team Members

Send this message to collaborators:

```
⚠️ Git history has been rewritten to remove secrets.

Please follow these steps:

1. Backup any local work:
   git stash
   
2. Fetch new history:
   git fetch origin
   
3. Reset your branch:
   git reset --hard origin/main
   
4. Apply your stashed work:
   git stash pop

Alternatively, re-clone the repository:
   cd ..
   rm -rf asl-monitoring-system
   git clone <repo-url>
```

## Step 5: Rotate Compromised Secrets

🔑 **CRITICAL:** Any secret that was pushed to GitHub must be considered compromised:

### Slack Webhooks
1. Go to https://api.slack.com/apps
2. Select your app
3. Navigate to "Incoming Webhooks"
4. Delete the old webhook
5. Create a new webhook
6. Update your `.env` file with new URL

### Slack API Tokens
1. Go to https://api.slack.com/apps
2. Select your app  
3. Navigate to "OAuth & Permissions"
4. Revoke the old token
5. Reinstall app to workspace to get new token
6. Update your `.env` file

### AWS Keys
```bash
# Deactivate old key
aws iam delete-access-key --access-key-id <OLD_KEY>

# Create new key
aws iam create-access-key --user-name <USERNAME>

# Update .env file
```

### Database Passwords
```sql
-- MySQL/MariaDB
ALTER USER 'username'@'host' IDENTIFIED BY 'new_password';

-- PostgreSQL
ALTER USER username WITH PASSWORD 'new_password';
```

## Preventing Future Issues

### 1. Set Up Pre-commit Hooks

```bash
# Install detect-secrets
pip install detect-secrets

# Scan repository
detect-secrets scan > .secrets.baseline

# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF

# Install hook
pre-commit install
```

### 2. Use Git Secrets by AWS Labs

```bash
# Install git-secrets
brew install git-secrets  # macOS
# or download from: https://github.com/awslabs/git-secrets

# Initialize in repository
git secrets --install
git secrets --register-aws

# Add custom patterns
git secrets --add 'hooks\.slack\.com/services/[A-Z0-9/]+'
git secrets --add 'xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]+'
```

### 3. Configure .gitignore

Ensure these patterns are in `.gitignore`:
```
.env
.env.local
.env.*.local
secrets/
*.key
*.pem
credentials.json
config.production.*
```

### 4. Use GitHub Secret Scanning

- Enable push protection in repository settings
- Review security alerts regularly
- Never bypass push protection warnings

## Troubleshooting

### "Cannot force push" Error

```bash
# Your branch protection rules may prevent force push
# Temporarily disable protection or contact admin

# Alternative: Create new branch
git checkout -b main-cleaned
git push origin main-cleaned
# Then update default branch in GitHub settings
```

### "Working directory dirty" Error

```bash
# Commit or stash changes first
git status
git stash
# Then retry cleanup
```

### Filter-repo: "not a fresh clone"

```bash
# git filter-repo requires a fresh clone
cd ..
git clone repo-url repo-clean
cd repo-clean
# Now run filter-repo
```

## Additional Resources

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [git-filter-repo documentation](https://github.com/newren/git-filter-repo)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [detect-secrets](https://github.com/Yelp/detect-secrets)

## Summary Checklist

- [ ] Backup repository
- [ ] Remove secrets from files (use environment variables)
- [ ] Clean git history with filter-repo/BFG
- [ ] Verify secrets are removed
- [ ] Clean up local repository (reflog, gc)
- [ ] Force push to remote
- [ ] Notify team members
- [ ] Rotate all exposed secrets
- [ ] Set up pre-commit hooks
- [ ] Update documentation
- [ ] Monitor for any security alerts

---

Need help? See `SECURITY.md` or create an issue on GitHub.
