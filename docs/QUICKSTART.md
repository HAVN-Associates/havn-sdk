# Quick Start Guide

Get started with HAVN Python SDK in 5 minutes.

## Installation

```bash
pip install havn-sdk
```

## Basic Setup

### 1. Get Your Credentials

You'll need two credentials from HAVN dashboard:
- **API Key** - For authentication
- **Webhook Secret** - For signing requests

### 2. Initialize Client

```python
from havn import HAVNClient

client = HAVNClient(
    api_key="your_api_key_here",
    webhook_secret="your_webhook_secret_here"
)
```

Or use environment variables:

```bash
export HAVN_API_KEY="your_api_key"
export HAVN_WEBHOOK_SECRET="your_webhook_secret"
```

```python
client = HAVNClient()  # Reads from environment
```

## Your First Transaction

```python
# Send a transaction
result = client.transactions.send(
    amount=10000,  # $100.00 in cents
    referral_code="HAVN-MJ-001",
    currency="USD"
)

print(f"Transaction ID: {result.transaction.transaction_id}")
print(f"Commissions: {len(result.commissions)} levels")
```

## Next Steps

- 📖 Read the [Full Documentation](README.md)
- 💻 Check [Examples](../examples/)
- 🧪 Try [Test Mode](../examples/05_test_mode.py)
- 🐛 Review [Error Handling](../examples/04_error_handling.py)
