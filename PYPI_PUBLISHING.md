# PyPI Publishing Guide

## ✅ Build Successful!

Distribution packages have been created in `dist/` directory.

---

## 📦 Built Packages

```
dist/
├── havn_sdk-1.0.0-py3-none-any.whl  (Binary distribution)
└── havn_sdk-1.0.0.tar.gz            (Source distribution)
```

---

## 🚀 Publishing to PyPI

### Step 1: Create PyPI Account

1. **Register at PyPI:**
   - Go to: https://pypi.org/account/register/
   - Username: (choose your username)
   - Email: (your email)
   - Password: (secure password)

2. **Verify email** (check inbox)

3. **Enable 2FA** (recommended):
   - Go to: https://pypi.org/manage/account/
   - Click "Add 2FA with authentication application"
   - Use Google Authenticator or Authy

---

### Step 2: Generate API Token

1. **Go to API token page:**
   - https://pypi.org/manage/account/token/

2. **Click "Add API token"**

3. **Configure token:**
   - Token name: `havn-sdk-upload`
   - Scope: `Entire account` (for first upload)
     - After first upload, can create project-specific token

4. **Copy token** (important!)
   ```
   pypi-AgEIcHlwaS5vcmcCJDExMTExMTExLTExMTEtMTExMS0xMTExLTExMTExMTExMTExMQA...
   ```
   **⚠️ Save this token securely! It won't be shown again.**

---

### Step 3: Upload to PyPI

#### Option A: Manual Upload (Recommended for first time)

```bash
cd /home/baguse/Documents/HAVN/havn-python-sdk

# Upload to PyPI
twine upload dist/*

# You'll be prompted:
# Username: __token__
# Password: (paste your PyPI token here - starts with pypi-)
```

#### Option B: Using .pypirc (For convenience)

```bash
# Create .pypirc file (one-time setup)
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
EOF

# Secure the file
chmod 600 ~/.pypirc

# Upload (no prompt needed)
twine upload dist/*
```

---

### Step 4: Verify Upload

1. **Check PyPI page:**
   - https://pypi.org/project/havn-sdk/
   
   You should see:
   - ✅ Version 1.0.0
   - ✅ README rendered
   - ✅ Project description
   - ✅ Installation instructions

2. **Test installation:**
   ```bash
   # Create test environment
   python3 -m venv /tmp/test-pypi-install
   source /tmp/test-pypi-install/bin/activate
   
   # Install from PyPI
   pip install havn-sdk
   
   # Test import
   python -c "from havn import HAVNClient; print('✅ Works!')"
   
   # Deactivate
   deactivate
   ```

---

## 📊 After Publishing

### Installation Methods

Users can now install in 3 ways:

#### 1. From PyPI (Simplest) ⭐
```bash
pip install havn-sdk
```

#### 2. From GitHub
```bash
pip install git+https://github.com/HAVN-Associates/havn-sdk.git
```

#### 3. From Source
```bash
git clone https://github.com/HAVN-Associates/havn-sdk.git
cd havn-sdk
pip install -e .
```

---

## 🔄 Future Updates

When you release a new version:

### 1. Update version number

**havn/__init__.py:**
```python
__version__ = "1.1.0"  # Update
```

**setup.py:**
```python
setup(
    version="1.1.0",  # Update
    ...
)
```

**CHANGELOG.md:**
```markdown
## [1.1.0] - 2024-11-14

### Added
- New feature X

### Fixed
- Bug fix Y
```

### 2. Commit and tag

```bash
git add .
git commit -m "chore: Release v1.1.0"
git tag v1.1.0
git push origin main --tags
```

### 3. Build and upload

```bash
# Clean old builds
rm -rf build/ dist/ *.egg-info

# Build new packages
python3 setup.py sdist bdist_wheel

# Upload to PyPI
twine upload dist/*
```

### 4. Verify

```bash
pip install --upgrade havn-sdk
python -c "import havn; print(havn.__version__)"  # Should show 1.1.0
```

---

## 🐛 Troubleshooting

### Error: Package already exists

```
HTTPError: 403 Forbidden
```

**Solution:** You can't overwrite existing versions on PyPI. Update version number in `setup.py` and `havn/__init__.py`.

---

### Error: Invalid credentials

```
HTTPError: 403 Forbidden
```

**Solution:** 
- Username must be exactly: `__token__`
- Password must be your API token starting with `pypi-`

---

### Error: README rendering issues

```bash
# Check README before upload
twine check dist/*
```

If issues found, fix README.md and rebuild.

---

## 🎯 Quick Commands Reference

```bash
# Build packages
python3 setup.py sdist bdist_wheel

# Check packages (recommended before upload)
twine check dist/*

# Upload to PyPI
twine upload dist/*

# Upload to Test PyPI (for testing first)
twine upload --repository testpypi dist/*

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ havn-sdk
```

---

## ✅ Success Criteria

After successful publishing:

- ✅ Package visible at: https://pypi.org/project/havn-sdk/
- ✅ Installation works: `pip install havn-sdk`
- ✅ Import works: `from havn import HAVNClient`
- ✅ Version correct: `havn.__version__ == "1.0.0"`
- ✅ Dependencies installed automatically
- ✅ README rendered on PyPI page

---

## 🎉 Ready to Publish!

**Current status:**
- ✅ Packages built in `dist/`
- ✅ README ready
- ✅ setup.py configured
- ✅ License included
- ⏳ Waiting for PyPI credentials

**Next step:** Create PyPI account and upload!

```bash
twine upload dist/*
```

After upload, anyone can:
```bash
pip install havn-sdk  # ✨ That's it!
```
