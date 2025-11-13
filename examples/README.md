# HAVN SDK Examples

This directory contains comprehensive examples for using HAVN Python SDK.

## Examples Overview

### 01. Simple Transaction
**File:** `01_simple_transaction.py`

Basic transaction sending with error handling.

```bash
python examples/01_simple_transaction.py
```

### 02. Transaction with Voucher
**File:** `02_transaction_with_voucher.py`

Send transaction with voucher discount and validation.

```bash
python examples/02_transaction_with_voucher.py
```

### 03. User Synchronization
**File:** `03_user_sync.py`

Sync users from Google OAuth and create associates.

```bash
python examples/03_user_sync.py
```

### 04. Error Handling
**File:** `04_error_handling.py`

Comprehensive error handling examples.

```bash
python examples/04_error_handling.py
```

### 05. Test Mode (Dry-Run)
**File:** `05_test_mode.py`

Use test mode for testing without saving data.

```bash
python examples/05_test_mode.py
```

### 06. Advanced Usage
**File:** `06_advanced_usage.py`

Advanced features like context managers, custom config, and batch operations.

```bash
python examples/06_advanced_usage.py
```

## Running Examples

### Prerequisites

1. Install the SDK:
```bash
pip install havn-sdk
# Or install from source:
pip install -e .
```

2. Set up credentials:
```bash
export HAVN_API_KEY="your_api_key"
export HAVN_WEBHOOK_SECRET="your_webhook_secret"
```

Or create `.env` file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Run All Examples

```bash
for example in examples/*.py; do
    echo "Running $example..."
    python "$example"
    echo "---"
done
```

## Need Help?

- 📖 [Full Documentation](../README.md)
- 🐛 [Error Handling Guide](04_error_handling.py)
- 🧪 [Test Mode Guide](05_test_mode.py)
