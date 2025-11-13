# Publishing Guide - HAVN Python SDK

Panduan lengkap untuk publish SDK ke GitHub dan PyPI.

## 📋 Checklist Sebelum Publish

- [ ] Semua tests pass (`pytest`)
- [ ] Documentation lengkap
- [ ] Examples tested
- [ ] Version number di `setup.py` dan `__init__.py` sesuai
- [ ] CHANGELOG.md updated
- [ ] LICENSE file ada

## 🔄 Alur Publishing

```
1. Git Repository (GitHub/GitLab)
   ↓
2. PyPI (Python Package Index)
   ↓
3. Users Install: pip install havn-sdk
```

---

## 📚 Step 1: Upload ke GitHub

### 1.1 Create GitHub Repository

1. **Buat repository baru di GitHub:**
   - Go to: https://github.com/new
   - Repository name: `havn-python-sdk`
   - Description: `Official Python SDK for HAVN API`
   - Visibility: **Public** (agar bisa di-install via pip)
   - ✅ Add README (skip, kita sudah punya)
   - ✅ Add .gitignore (skip, kita sudah punya)
   - ✅ Choose license: MIT (skip, kita sudah punya)

2. **Copy Git URL:**
   ```
   https://github.com/YOUR_USERNAME/havn-python-sdk.git
   ```

### 1.2 Initialize Git dan Push

```bash
cd /home/baguse/Documents/HAVN/havn-python-sdk

# Initialize git (jika belum)
git init

# Add all files
git add .

# First commit
git commit -m "feat: Initial release v1.0.0

- Core HAVNClient implementation
- Transaction, User Sync, Voucher webhooks
- HMAC authentication
- Retry logic with exponential backoff
- Test mode support
- Comprehensive examples (6 files)
- Unit tests
- Complete documentation
"

# Add remote (ganti YOUR_USERNAME dengan username GitHub Anda)
git remote add origin https://github.com/YOUR_USERNAME/havn-python-sdk.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 1.3 Create GitHub Release (Optional tapi Recommended)

1. Go to: `https://github.com/YOUR_USERNAME/havn-python-sdk/releases/new`
2. Tag version: `v1.0.0`
3. Release title: `HAVN Python SDK v1.0.0`
4. Description: Copy dari CHANGELOG.md
5. Click "Publish release"

---

## 📦 Step 2: Publish ke PyPI

### 2.1 Register di PyPI

1. **Create account:**
   - Go to: https://pypi.org/account/register/
   - Username: your_username
   - Email: your@email.com
   - Password: secure_password

2. **Verify email**

3. **Enable 2FA (Recommended)**

### 2.2 Install Publishing Tools

```bash
# Install twine (tool untuk upload ke PyPI)
pip install twine wheel

# Verify installation
twine --version
```

### 2.3 Build Distribution Packages

```bash
cd /home/baguse/Documents/HAVN/havn-python-sdk

# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build source distribution and wheel
python setup.py sdist bdist_wheel

# You should see:
# dist/
#   ├── havn-sdk-1.0.0.tar.gz        (source distribution)
#   └── havn_sdk-1.0.0-py3-none-any.whl  (wheel)
```

### 2.4 Test Upload ke TestPyPI (Recommended)

TestPyPI adalah server testing untuk practice sebelum upload ke real PyPI.

```bash
# Register di TestPyPI
# https://test.pypi.org/account/register/

# Upload ke TestPyPI
twine upload --repository testpypi dist/*

# Enter credentials:
# Username: __token__
# Password: your-testpypi-api-token
```

**Test installation dari TestPyPI:**

```bash
# Create test environment
python -m venv test-env
source test-env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ havn-sdk

# Test import
python -c "from havn import HAVNClient; print('✅ Import successful!')"

# Deactivate
deactivate
```

### 2.5 Upload ke PyPI (Production)

```bash
# Upload ke real PyPI
twine upload dist/*

# Enter credentials:
# Username: __token__
# Password: your-pypi-api-token
```

**Generate API Token:**
1. Go to: https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Token name: `havn-sdk-upload`
4. Scope: `Project: havn-sdk` (atau "Entire account")
5. Click "Add token"
6. **Copy token** (starts with `pypi-...`)
7. Save token securely

---

## ✅ Step 3: Verify Publication

### 3.1 Check PyPI Page

Visit: https://pypi.org/project/havn-sdk/

You should see:
- ✅ Project name and version
- ✅ Description from README.md
- ✅ Installation instructions
- ✅ Project links (GitHub, docs)

### 3.2 Test Installation

```bash
# Create fresh environment
python -m venv verify-env
source verify-env/bin/activate

# Install from PyPI
pip install havn-sdk

# Verify version
python -c "import havn; print(havn.__version__)"
# Output: 1.0.0

# Test import
python -c "from havn import HAVNClient; print('✅ Installation successful!')"

# Deactivate
deactivate
```

---

## 🔄 Updating the Package (Future Releases)

### Update Version

1. **Update version number in 3 places:**

   a. `havn/__init__.py`:
   ```python
   __version__ = "1.1.0"  # Update this
   ```

   b. `setup.py`:
   ```python
   setup(
       name="havn-sdk",
       version="1.1.0",  # Update this
       ...
   )
   ```

   c. `CHANGELOG.md`:
   ```markdown
   ## [1.1.0] - 2024-11-15
   
   ### Added
   - New feature X
   
   ### Fixed
   - Bug fix Y
   ```

2. **Commit changes:**
   ```bash
   git add .
   git commit -m "chore: Bump version to 1.1.0"
   git tag v1.1.0
   git push origin main --tags
   ```

3. **Build and upload:**
   ```bash
   rm -rf build/ dist/ *.egg-info
   python setup.py sdist bdist_wheel
   twine upload dist/*
   ```

---

## 🚀 Alternative: GitHub Installation (Without PyPI)

Users can install directly from GitHub:

```bash
# Install from GitHub main branch
pip install git+https://github.com/YOUR_USERNAME/havn-python-sdk.git

# Install specific version (tag)
pip install git+https://github.com/YOUR_USERNAME/havn-python-sdk.git@v1.0.0

# Install from local source (for development)
cd /path/to/havn-python-sdk
pip install -e .
```

---

## 📊 Comparison: GitHub vs PyPI

| Feature | GitHub Only | PyPI |
|---------|-------------|------|
| Installation | `pip install git+https://...` | `pip install havn-sdk` |
| Ease of use | ⚠️ Complex URL | ✅ Simple |
| Version pinning | ✅ Via tags | ✅ Via version |
| Dependency resolution | ⚠️ Manual | ✅ Automatic |
| Discovery | ❌ Hard to find | ✅ Easy (pypi.org) |
| CI/CD friendly | ⚠️ Needs token | ✅ No auth |
| Professional | ⚠️ Less | ✅ More |

**Recommendation:** Publish to both GitHub AND PyPI untuk best experience.

---

## 🔐 Security Best Practices

### API Tokens

```bash
# Store PyPI token securely
# Option 1: Use keyring
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__

# Option 2: Use .pypirc file
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-your-api-token-here
EOF
chmod 600 ~/.pypirc
```

### GitHub Secrets (for CI/CD)

If using GitHub Actions:

1. Go to: `Settings > Secrets and variables > Actions`
2. Add secret: `PYPI_API_TOKEN`
3. Value: your PyPI API token

---

## 🤖 Automation with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      
      - name: Install dependencies
        run: |
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

**Benefits:**
- ✅ Automatic publish when you create GitHub release
- ✅ No manual upload needed
- ✅ Consistent process

---

## 📝 Post-Publication Checklist

- [ ] PyPI page looks correct
- [ ] Installation works: `pip install havn-sdk`
- [ ] Import works: `from havn import HAVNClient`
- [ ] Examples run without errors
- [ ] Documentation links work
- [ ] Update HAVN main docs to link to SDK
- [ ] Announce on social media / blog
- [ ] Add badge to README:
  ```markdown
  [![PyPI](https://img.shields.io/pypi/v/havn-sdk)](https://pypi.org/project/havn-sdk/)
  [![Downloads](https://pepy.tech/badge/havn-sdk)](https://pepy.tech/project/havn-sdk)
  ```

---

## 🐛 Troubleshooting

### Error: Package already exists

```bash
# Solution: Update version number in setup.py and __init__.py
# PyPI doesn't allow overwriting existing versions
```

### Error: Invalid credentials

```bash
# Solution: Use API token instead of password
# Username: __token__
# Password: pypi-...your-token...
```

### Error: README rendering issues

```bash
# Solution: Validate README
pip install readme-renderer
python setup.py check --restructuredtext --strict
```

### Error: Missing dependencies

```bash
# Solution: Add to requirements.txt and setup.py install_requires
```

---

## 📞 Support

- PyPI Help: https://pypi.org/help/
- Twine Docs: https://twine.readthedocs.io/
- GitHub Docs: https://docs.github.com/

---

## 🎉 Success!

Once published:

```bash
# Anyone can install with:
pip install havn-sdk

# And use immediately:
from havn import HAVNClient
client = HAVNClient(api_key="...", webhook_secret="...")
```

**Your SDK is now available to millions of Python developers worldwide!** 🚀
