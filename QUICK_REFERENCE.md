# Quick Reference - Publishing Flow

## 🔄 Simple Publishing Flow

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Step 1: DEVELOP                                        │
│  ✅ Code SDK                                            │
│  ✅ Write tests                                         │
│  ✅ Write docs                                          │
│                                                         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Step 2: GITHUB (Version Control)                      │
│                                                         │
│  git init                                               │
│  git add .                                              │
│  git commit -m "feat: Initial release v1.0.0"          │
│  git remote add origin https://github.com/USER/REPO    │
│  git push -u origin main                               │
│                                                         │
│  ➡️  Users CAN install from GitHub:                     │
│      pip install git+https://github.com/USER/REPO.git  │
│                                                         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Step 3: PyPI (Package Index) ⭐ RECOMMENDED            │
│                                                         │
│  # Build packages                                       │
│  python setup.py sdist bdist_wheel                     │
│                                                         │
│  # Upload to PyPI                                       │
│  twine upload dist/*                                   │
│                                                         │
│  ➡️  Users install EASILY:                              │
│      pip install havn-sdk  ✨                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Two Options for Distribution

### Option 1: GitHub Only (Free, Simple)

**Pros:**
- ✅ Free
- ✅ No PyPI account needed
- ✅ Good for private/internal packages
- ✅ Immediate availability

**Cons:**
- ❌ Complex installation command
- ❌ Harder for users to discover
- ❌ No automatic dependency resolution
- ❌ Less professional

**Installation:**
```bash
pip install git+https://github.com/YOUR_USERNAME/havn-python-sdk.git
```

---

### Option 2: GitHub + PyPI (Recommended) ⭐

**Pros:**
- ✅ Simple installation: `pip install havn-sdk`
- ✅ Easy to discover on pypi.org
- ✅ Automatic dependency resolution
- ✅ Professional appearance
- ✅ Version management built-in
- ✅ pip freeze works properly

**Cons:**
- ⚠️ Requires PyPI account (free)
- ⚠️ Need to upload on every release
- ⚠️ Public by default

**Installation:**
```bash
pip install havn-sdk  # ✨ Simple!
```

---

## 📋 Quick Commands

### GitHub Setup (One-time)

```bash
# Navigate to SDK folder
cd /home/baguse/Documents/HAVN/havn-python-sdk

# Initialize git
git init
git add .
git commit -m "feat: Initial release v1.0.0"

# Add GitHub remote (create repo on GitHub first!)
git remote add origin https://github.com/YOUR_USERNAME/havn-python-sdk.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### PyPI Setup (One-time)

```bash
# Install tools
pip install twine wheel

# Register at https://pypi.org/account/register/
# Get API token from https://pypi.org/manage/account/token/
```

### Publishing (Every Release)

```bash
# Clean old builds
rm -rf build/ dist/ *.egg-info

# Build packages
python setup.py sdist bdist_wheel

# Upload to PyPI
twine upload dist/*
# Username: __token__
# Password: pypi-YOUR_TOKEN_HERE
```

---

## 🔑 Installation Methods (for End Users)

### 1. From PyPI (After you publish)
```bash
pip install havn-sdk
```

### 2. From GitHub (Available now)
```bash
# Latest from main branch
pip install git+https://github.com/YOUR_USERNAME/havn-python-sdk.git

# Specific version
pip install git+https://github.com/YOUR_USERNAME/havn-python-sdk.git@v1.0.0
```

### 3. From Local Source (Development)
```bash
cd /path/to/havn-python-sdk
pip install -e .
```

---

## 🎭 What Happens Behind the Scenes

### When you `git push` to GitHub:

```
Your Computer  →  GitHub Servers
    SDK Code   →  Stored in Git Repository
               →  ✅ Available for cloning
               →  ✅ Can install via: pip install git+https://...
               →  ❌ NOT on PyPI (yet)
```

### When you `twine upload` to PyPI:

```
Your Computer  →  PyPI Servers
    dist/*.whl →  Processed & Indexed
               →  ✅ Available on pypi.org
               →  ✅ Searchable
               →  ✅ Can install via: pip install havn-sdk
               →  ✅ Automatic dependency resolution
```

---

## 💡 Recommended Workflow

### For Production SDK (Your Case):

```bash
# 1. Push to GitHub (for source code, issues, collaboration)
git push origin main

# 2. Publish to PyPI (for easy installation)
python setup.py sdist bdist_wheel
twine upload dist/*

# 3. Create GitHub Release (optional but nice)
git tag v1.0.0
git push origin v1.0.0
# Then create release on GitHub UI
```

**Result:**
- ✅ Source code on GitHub (for developers, contributors)
- ✅ Package on PyPI (for end users)
- ✅ Professional and discoverable
- ✅ Easy to install: `pip install havn-sdk`

---

## 🚫 Common Misconceptions

### ❌ WRONG:
> "If I push to GitHub, it automatically becomes available on PyPI"

### ✅ CORRECT:
> "GitHub and PyPI are separate. I need to:"
> 1. Push to GitHub (for source code)
> 2. Build packages (`python setup.py sdist bdist_wheel`)
> 3. Upload to PyPI (`twine upload dist/*`)

---

### ❌ WRONG:
> "I need to upload every commit to PyPI"

### ✅ CORRECT:
> "Only upload to PyPI when releasing a new version (e.g., v1.0.0, v1.1.0)"

---

### ❌ WRONG:
> "PyPI will automatically track my GitHub repository"

### ✅ CORRECT:
> "PyPI and GitHub are independent. I manually upload to PyPI, but can link to GitHub in setup.py"

---

## 📊 Version Management

### Update Version for New Release:

1. **havn/__init__.py**
   ```python
   __version__ = "1.1.0"  # ← Change here
   ```

2. **setup.py**
   ```python
   setup(
       version="1.1.0",  # ← Change here
   )
   ```

3. **CHANGELOG.md**
   ```markdown
   ## [1.1.0] - 2024-11-15
   ### Added
   - New features...
   ```

4. **Git tag**
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

5. **Upload to PyPI**
   ```bash
   python setup.py sdist bdist_wheel
   twine upload dist/*
   ```

---

## 🎉 Summary

**SIMPLE ANSWER TO YOUR QUESTION:**

1. **Upload to GitHub** (for source code):
   ```bash
   git push origin main
   ```
   ➡️ Users CAN install but it's complex:
   ```bash
   pip install git+https://github.com/USER/REPO.git
   ```

2. **Publish to PyPI** (recommended):
   ```bash
   python setup.py sdist bdist_wheel
   twine upload dist/*
   ```
   ➡️ Users install EASILY:
   ```bash
   pip install havn-sdk  ✨
   ```

**Tidak otomatis!** Anda perlu:
- Push ke GitHub manually
- Build & upload ke PyPI manually
- (Or automate with GitHub Actions)

**Setelah di PyPI:**
- ✅ Users tinggal: `pip install havn-sdk`
- ✅ Automatic updates when you publish new version
- ✅ Professional and discoverable
