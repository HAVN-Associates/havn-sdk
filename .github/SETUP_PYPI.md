# PyPI Setup Guide for GitHub Actions

## 🔐 Setup PyPI Token in GitHub Secrets

To enable automatic publishing to PyPI via GitHub Actions, follow these steps:

### Step 1: Create PyPI API Token

1. **Login to PyPI:**
   - Go to: https://pypi.org/

2. **Navigate to API tokens:**
   - Go to: https://pypi.org/manage/account/token/

3. **Create new token:**
   - Click "Add API token"
   - Token name: `github-actions-havn-sdk`
   - Scope: 
     - First time: `Entire account`
     - After first publish: `Project: havn-sdk` (more secure)
   
4. **Copy the token:**
   - Format: `pypi-AgE...`
   - ⚠️ Save it immediately! Won't be shown again.

---

### Step 2: Add Token to GitHub Secrets

1. **Go to repository settings:**
   - https://github.com/HAVN-Associates/havn-sdk/settings/secrets/actions

2. **Click "New repository secret"**

3. **Add secret:**
   - Name: `PYPI_API_TOKEN`
   - Value: (paste your PyPI token)

4. **Click "Add secret"**

---

## 🚀 How Auto-Publish Works

### Workflow: publish.yml

**Triggers:**
- ✅ When you create a GitHub Release
- ✅ Manual trigger via Actions tab

**What it does:**
1. Checks out code
2. Builds Python packages (wheel + source)
3. Validates packages with `twine check`
4. Uploads to PyPI automatically
5. Creates deployment summary

**Example usage:**

```bash
# Create version tag
git tag v1.0.1
git push origin v1.0.1

# GitHub will automatically:
# 1. Create GitHub Release (release.yml)
# 2. Publish to PyPI (publish.yml)
```

---

### Workflow: release.yml

**Triggers:**
- ✅ When you push a version tag (e.g., `v1.0.1`)

**What it does:**
1. Extracts version from tag
2. Reads CHANGELOG.md for release notes
3. Creates GitHub Release automatically
4. Triggers publish.yml workflow

---

### Workflow: test.yml

**Triggers:**
- ✅ Push to main or dev branch
- ✅ Pull requests to main
- ✅ Manual trigger

**What it does:**
1. Runs tests on Python 3.8-3.12
2. Checks code coverage
3. Lints code with flake8
4. Checks formatting with black
5. Checks imports with isort

---

### Workflow: security.yml

**Triggers:**
- ✅ Push to main branch
- ✅ Pull requests
- ✅ Weekly on Sunday (scheduled)
- ✅ Manual trigger

**What it does:**
1. Scans dependencies for vulnerabilities (safety)
2. Scans code for security issues (bandit)
3. Uploads security reports

---

## 📋 Release Process (Best Practice)

### Option 1: Automated Release (Recommended)

```bash
# 1. Update version
# Edit: havn/__init__.py
__version__ = "1.0.1"

# Edit: setup.py
version="1.0.1"

# 2. Update CHANGELOG.md
## [1.0.1] - 2024-11-14

### Added
- New feature X

### Fixed
- Bug Y

# 3. Commit changes
git add .
git commit -m "chore: Release v1.0.1"
git push origin main

# 4. Create and push tag
git tag v1.0.1
git push origin v1.0.1

# 5. GitHub Actions will automatically:
#    - Create GitHub Release (with changelog)
#    - Publish to PyPI
#    - Run all tests
```

---

### Option 2: Manual Release

```bash
# 1. Go to GitHub repository
# 2. Click "Releases" → "Draft a new release"
# 3. Choose tag: v1.0.1 (create new tag)
# 4. Title: Release v1.0.1
# 5. Description: (copy from CHANGELOG.md)
# 6. Click "Publish release"

# GitHub Actions will automatically publish to PyPI
```

---

## 🔍 Verify Deployment

### Check GitHub Actions

1. Go to: https://github.com/HAVN-Associates/havn-sdk/actions
2. Look for "Publish to PyPI" workflow
3. Check status: ✅ Success

### Check PyPI

1. Go to: https://pypi.org/project/havn-sdk/
2. Verify version is updated
3. Test installation:
   ```bash
   pip install --upgrade havn-sdk
   python -c "import havn; print(havn.__version__)"
   ```

---

## 🛡️ Security Best Practices

### PyPI Token Security

- ✅ Use project-scoped tokens (after first publish)
- ✅ Store in GitHub Secrets (never in code)
- ✅ Rotate tokens periodically
- ✅ Use environment protection for sensitive deployments

### Code Security

- ✅ Security scanning enabled (Bandit)
- ✅ Dependency scanning enabled (Safety)
- ✅ Code review required before merge
- ✅ Automated tests before publish

---

## 🐛 Troubleshooting

### Error: 403 Forbidden (PyPI)

**Cause:** Invalid or expired token

**Solution:**
1. Generate new token at https://pypi.org/manage/account/token/
2. Update GitHub secret: `PYPI_API_TOKEN`

---

### Error: Package already exists

**Cause:** Version number already published

**Solution:**
1. Update version in `havn/__init__.py` and `setup.py`
2. Commit and create new tag
3. Push tag to trigger re-publish

---

### Error: Workflow not running

**Cause:** Missing permissions or secrets

**Solution:**
1. Check `PYPI_API_TOKEN` secret exists
2. Check workflow file permissions
3. Check branch protection rules

---

## 📊 Workflow Summary

```
Tag Push (v1.0.1)
    ↓
┌─────────────────────────────────────┐
│  release.yml (Auto-create release)  │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│  publish.yml (Auto-publish to PyPI) │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│  PyPI (havn-sdk v1.0.1 live!)      │
└─────────────────────────────────────┘

Users can now:
  pip install havn-sdk==1.0.1
```

---

## ✅ Checklist

Before first auto-publish:

- [ ] PyPI account created
- [ ] PyPI API token generated
- [ ] Token added to GitHub Secrets (`PYPI_API_TOKEN`)
- [ ] Workflows committed to repository
- [ ] Test release created (optional)
- [ ] CHANGELOG.md updated

After first publish:

- [ ] Create project-scoped PyPI token
- [ ] Update GitHub Secret with project token
- [ ] Enable branch protection on `main`
- [ ] Configure required reviewers
- [ ] Test auto-release workflow

---

## 🎉 Benefits of Auto-Publish

- ⚡ **Fast:** Release in seconds, not minutes
- 🔒 **Secure:** No manual token handling
- 📝 **Consistent:** Same process every time
- 🤖 **Automated:** Less human error
- 📊 **Trackable:** Full audit log in GitHub Actions
- ✅ **Tested:** Only publishes if tests pass

---

Generated: 2024-11-13  
Repository: HAVN-Associates/havn-sdk
