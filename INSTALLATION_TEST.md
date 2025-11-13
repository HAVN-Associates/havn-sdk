# Installation Test Guide

## ✅ GitHub Push Successful!

Repository: https://github.com/HAVN-Associates/havn-sdk

---

## 🎯 Installation Methods (Now Available!)

### Method 1: Install from GitHub (Available NOW!)

```bash
# Install latest from main branch
pip install git+https://github.com/HAVN-Associates/havn-sdk.git

# Or install specific version
pip install git+https://github.com/HAVN-Associates/havn-sdk.git@v1.0.0
```

**Verification:**
```bash
python -c "from havn import HAVNClient; print('✅ Installation successful!')"
python -c "import havn; print(f'Version: {havn.__version__}')"
```

---

### Method 2: Install from PyPI (After Publishing)

**First time setup (do once):**

```bash
# 1. Install tools
pip install twine wheel

# 2. Build packages
cd /home/baguse/Documents/HAVN/havn-python-sdk
python setup.py sdist bdist_wheel

# 3. Upload to PyPI (requires PyPI account)
twine upload dist/*
# Username: __token__
# Password: (your PyPI API token from https://pypi.org/manage/account/token/)
```

**After PyPI publishing, users can:**

```bash
# Install from PyPI (simplest!)
pip install havn-sdk

# Install specific version
pip install havn-sdk==1.0.0

# Upgrade to latest
pip install --upgrade havn-sdk
```

---

## 🧪 Test Installation

### Create Test Environment

```bash
# Create fresh virtual environment
python -m venv test-sdk-env
source test-sdk-env/bin/activate  # On Windows: test-sdk-env\Scripts\activate

# Install from GitHub
pip install git+https://github.com/HAVN-Associates/havn-sdk.git

# Test import
python << EOF
from havn import HAVNClient
print("✅ Import successful!")
print(f"Version: {__import__('havn').__version__}")
print(f"Available: HAVNClient, exceptions, models")
EOF

# Deactivate
deactivate
```

---

## 📦 Test Usage

Create test file:

```python
# test_sdk.py
from havn import HAVNClient

# Initialize (will fail without credentials, but tests import)
try:
    client = HAVNClient(
        api_key="test_key",
        webhook_secret="test_secret",
        test_mode=True  # Test mode
    )
    print("✅ Client initialized")
    print(f"Base URL: {client.base_url}")
    print(f"Test mode: {client.test_mode}")
    
    # Check methods are available
    assert hasattr(client, 'transactions')
    assert hasattr(client, 'users')
    assert hasattr(client, 'vouchers')
    print("✅ All webhook handlers available")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

Run test:
```bash
python test_sdk.py
```

---

## 🔍 Verify Package Contents

```bash
# After installation, check what's installed
pip show havn-sdk

# List installed files
pip show -f havn-sdk

# Check version
python -c "import havn; print(havn.__version__)"

# Check available imports
python -c "from havn import *; print(dir())"
```

---

## 📊 Installation Comparison

### From GitHub (Available NOW!)

```bash
pip install git+https://github.com/HAVN-Associates/havn-sdk.git
```

| Aspect | Status |
|--------|--------|
| Available | ✅ Now |
| Requires | Git installed |
| Command | Complex |
| Updates | Manual (`pip install --upgrade git+...`) |
| Professional | ⭐⭐⭐ |

---

### From PyPI (After Publishing)

```bash
pip install havn-sdk
```

| Aspect | Status |
|--------|--------|
| Available | After twine upload |
| Requires | Only pip |
| Command | Simple ✨ |
| Updates | Easy (`pip install --upgrade havn-sdk`) |
| Professional | ⭐⭐⭐⭐⭐ |

---

## 🎉 Success Criteria

After installation, these should work:

```python
# 1. Import SDK
from havn import HAVNClient
from havn.exceptions import HAVNAPIError

# 2. Check version
import havn
print(havn.__version__)  # Should print: 1.0.0

# 3. Initialize client
client = HAVNClient(
    api_key="test_key",
    webhook_secret="test_secret"
)

# 4. Check methods exist
assert hasattr(client.transactions, 'send')
assert hasattr(client.users, 'sync')
assert hasattr(client.vouchers, 'validate')

print("✅ All tests passed!")
```

---

## 🚀 Next: Publish to PyPI

To make installation even easier, publish to PyPI:

```bash
cd /home/baguse/Documents/HAVN/havn-python-sdk

# Build
python setup.py sdist bdist_wheel

# Check packages
ls -lh dist/
# You should see:
# - havn_sdk-1.0.0-py3-none-any.whl
# - havn-sdk-1.0.0.tar.gz

# Upload
twine upload dist/*
```

After that, everyone can simply:
```bash
pip install havn-sdk
```

---

## 📝 Summary

**Current Status:**
- ✅ Pushed to GitHub: https://github.com/HAVN-Associates/havn-sdk
- ✅ Tagged as v1.0.0
- ✅ Can install via: `pip install git+https://github.com/HAVN-Associates/havn-sdk.git`
- ⏳ PyPI publishing: Pending (optional but recommended)

**Installation works!** ✨
