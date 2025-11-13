# HAVN SDK - Installation Instructions

## 📦 Two Ways to Install

### ✅ Method 1: From GitHub (Available NOW!)

```bash
pip install git+https://github.com/HAVN-Associates/havn-sdk.git
```

**Or specific version:**
```bash
pip install git+https://github.com/HAVN-Associates/havn-sdk.git@v1.0.0
```

---

### ✅ Method 2: From PyPI (After Publishing - SIMPLER!)

**Once you publish to PyPI:**

```bash
pip install havn-sdk
```

**To publish to PyPI (one-time):**
```bash
cd /home/baguse/Documents/HAVN/havn-python-sdk
pip install twine wheel
python setup.py sdist bdist_wheel
twine upload dist/*
```

---

## 🧪 Verify Installation

```bash
# Check if installed
pip show havn-sdk

# Test import
python -c "from havn import HAVNClient; print('✅ Works!')"

# Check version
python -c "import havn; print(f'Version: {havn.__version__}')"
```

---

## 💻 Quick Usage

```python
from havn import HAVNClient

# Initialize
client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret"
)

# Send transaction
result = client.transactions.send(
    amount=10000,
    referral_code="HAVN-MJ-001"
)

print(f"Transaction: {result.transaction.transaction_id}")
```

---

## 🎯 For SaaS Companies

Add to your requirements.txt:
```
havn-sdk>=1.0.0
```

Or for GitHub install:
```
havn-sdk @ git+https://github.com/HAVN-Associates/havn-sdk.git@v1.0.0
```

Then: `pip install -r requirements.txt`
