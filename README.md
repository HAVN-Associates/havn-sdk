# HAVN Python SDK

Official Python SDK for integrating with HAVN (Hierarchical Associate Voucher Network) API.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Features

- ✅ **Simple & Intuitive API** - Easy to use, Pythonic interface
- ✅ **Automatic Authentication** - HMAC-SHA256 signature generation
- ✅ **Type Hints** - Full type annotation support
- ✅ **Retry Logic** - Built-in retry with exponential backoff
- ✅ **Comprehensive Models** - Pydantic models with validation
- ✅ **Error Handling** - Descriptive custom exceptions
- ✅ **Test Mode** - Dry-run mode for testing without side effects
- ✅ **Well Documented** - Extensive documentation and examples

## Installation

```bash
pip install havn-sdk
```

Or install from source:

```bash
git clone https://github.com/havn/havn-python-sdk.git
cd havn-python-sdk
pip install -e .
```

## Quick Start

```python
from havn import HAVNClient

# Initialize client
client = HAVNClient(
    api_key="your_api_key_here",
    webhook_secret="your_webhook_secret_here",
    base_url="https://api.havn.com"  # Optional, defaults to production
)

# Send a transaction
result = client.transactions.send(
    amount=10000,  # $100.00 in cents
    referral_code="HAVN-MJ-001",
    currency="USD",
    customer_type="NEW_CUSTOMER"
)

print(f"Transaction ID: {result.transaction.transaction_id}")
print(f"Commissions: {len(result.commissions)} levels distributed")
```

## Usage Examples

### Send Transaction

```python
# Simple transaction
result = client.transactions.send(
    amount=10000,
    referral_code="HAVN-MJ-001"
)

# Transaction with voucher
result = client.transactions.send(
    amount=8000,  # After discount
    subtotal_transaction=10000,  # Before discount
    promo_code="VOUCHER123",
    referral_code="HAVN-MJ-001",
    currency="USD",
    customer_type="NEW_CUSTOMER"
)

# Transaction with custom fields
result = client.transactions.send(
    amount=10000,
    referral_code="HAVN-MJ-001",
    custom_fields={
        "order_id": "ORD123456",
        "payment_method": "credit_card",
        "customer_segment": "premium"
    }
)
```

### Sync User

```python
# Sync user from Google OAuth
result = client.users.sync(
    email="user@example.com",
    name="John Doe",
    google_id="google123",
    picture="https://example.com/photo.jpg",
    create_associate=True,
    upline_code="HAVN-MJ-001"
)

print(f"User created: {result.user_created}")
print(f"Associate created: {result.associate_created}")
```

### Validate Voucher

```python
# Validate voucher code
try:
    is_valid = client.vouchers.validate(
        voucher_code="VOUCHER123",
        amount=10000,
        currency="USD"
    )
    print("✅ Voucher is valid")
except Exception as e:
    print(f"❌ Voucher invalid: {str(e)}")
```

### Test Mode (Dry-Run)

```python
# Enable test mode - no data will be saved
client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret",
    test_mode=True  # Dry-run mode
)

result = client.transactions.send(
    amount=10000,
    referral_code="HAVN-MJ-001"
)
# This will return success but not save to database
```

## Configuration

### Environment Variables

```bash
export HAVN_API_KEY="your_api_key"
export HAVN_WEBHOOK_SECRET="your_webhook_secret"
export HAVN_BASE_URL="https://api.havn.com"  # Optional
export HAVN_TIMEOUT=30  # Optional, default 30 seconds
export HAVN_MAX_RETRIES=3  # Optional, default 3
```

Then initialize client without parameters:

```python
from havn import HAVNClient

client = HAVNClient()  # Reads from environment variables
```

### Custom Configuration

```python
client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret",
    base_url="https://api.havn.com",
    timeout=30,  # Request timeout in seconds
    max_retries=3,  # Number of retry attempts
    backoff_factor=0.5,  # Exponential backoff multiplier
    test_mode=False  # Enable dry-run mode
)
```

## Error Handling

```python
from havn import HAVNClient
from havn.exceptions import (
    HAVNAPIError,
    HAVNAuthError,
    HAVNValidationError,
    HAVNNetworkError
)

client = HAVNClient(api_key="...", webhook_secret="...")

try:
    result = client.transactions.send(
        amount=10000,
        referral_code="HAVN-MJ-001"
    )
except HAVNAuthError as e:
    print(f"Authentication failed: {e}")
except HAVNValidationError as e:
    print(f"Validation error: {e}")
except HAVNNetworkError as e:
    print(f"Network error: {e}")
except HAVNAPIError as e:
    print(f"API error: {e}")
```

## Documentation

Dokumentasi lengkap tersedia di folder `docs/`:

### 📚 Panduan Lengkap

- **[Quick Start Guide](docs/QUICKSTART.md)** - Mulai menggunakan SDK dalam 5 menit
- **[API Reference](docs/API_REFERENCE.md)** - Dokumentasi lengkap semua methods dan parameters
- **[Concepts Guide](docs/CONCEPTS.md)** - Memahami konsep dasar dan arsitektur SDK
- **[Examples](docs/EXAMPLES.md)** - Contoh penggunaan lengkap berbagai skenario
- **[Configuration Guide](docs/CONFIGURATION.md)** - Panduan konfigurasi lanjutan
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Menyelesaikan masalah umum

### 📖 Quick Links

**Getting Started:**
- [Installation & Setup](docs/QUICKSTART.md#installation)
- [Basic Setup](docs/QUICKSTART.md#basic-setup)
- [Your First Transaction](docs/QUICKSTART.md#your-first-transaction)

**Core Concepts:**
- [Authentication](docs/CONCEPTS.md#authentication)
- [Webhooks vs API](docs/CONCEPTS.md#webhooks-vs-api)
- [Error Handling](docs/CONCEPTS.md#error-handling)
- [Test Mode](docs/CONCEPTS.md#test-mode)

**Examples:**
- [Transaction Examples](docs/EXAMPLES.md#transaction-examples)
- [User Sync Examples](docs/EXAMPLES.md#user-sync-examples)
- [Voucher Validation Examples](docs/EXAMPLES.md#voucher-validation-examples)
- [Error Handling Examples](docs/EXAMPLES.md#error-handling-examples)

**API Reference:**
- [HAVNClient](docs/API_REFERENCE.md#havnclient)
- [TransactionWebhook](docs/API_REFERENCE.md#transactionwebhook)
- [UserSyncWebhook](docs/API_REFERENCE.md#usersyncwebhook)
- [VoucherWebhook](docs/API_REFERENCE.md#voucherwebhook)
- [Models](docs/API_REFERENCE.md#models)
- [Exceptions](docs/API_REFERENCE.md#exceptions)

**Configuration:**
- [Environment Variables](docs/CONFIGURATION.md#environment-variables)
- [Custom Configuration](docs/CONFIGURATION.md#programmatic-configuration)
- [Multi-Environment Setup](docs/CONFIGURATION.md#multi-environment-setup)

**Troubleshooting:**
- [Common Errors](docs/TROUBLESHOOTING.md#common-errors)
- [Authentication Issues](docs/TROUBLESHOOTING.md#authentication-issues)
- [Network Issues](docs/TROUBLESHOOTING.md#network-issues)
- [Debugging Tips](docs/TROUBLESHOOTING.md#debugging-tips)

### 🚀 Quick Reference

**Client Methods:**
- `client.transactions.send(**kwargs)` - Send transaction
- `client.users.sync(**kwargs)` - Sync user data
- `client.vouchers.validate(**kwargs)` - Validate voucher

**Response Models:**
- `TransactionResponse` - Transaction webhook response dengan commissions
- `UserSyncResponse` - User sync webhook response dengan user dan associate data
- Voucher validation mengembalikan `bool` (True jika valid)

Lihat [API Reference](docs/API_REFERENCE.md) untuk dokumentasi lengkap.

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/havn/havn-python-sdk.git
cd havn-python-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checker
mypy havn

# Run linter
flake8 havn
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=havn --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support & Resources

### 📚 Documentation

- **Local Documentation**: Check folder `docs/` untuk dokumentasi lengkap
- **Quick Start**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **API Reference**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **Examples**: [docs/EXAMPLES.md](docs/EXAMPLES.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

### 💬 Get Help

- 📧 **Email**: bagus@intelove.com
- 📖 **Documentation**: https://docs.havn.com
- 🐛 **GitHub Issues**: https://github.com/havn/havn-python-sdk/issues
- 💻 **Examples**: Check folder `examples/` untuk contoh code yang bisa di-run

### 🆘 Common Issues

Jika mengalami masalah, lihat [Troubleshooting Guide](docs/TROUBLESHOOTING.md) untuk:
- Authentication errors
- Network issues
- Validation errors
- API errors
- Debugging tips

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Related Projects

- [HAVN Backend](https://github.com/havn/backend) - HAVN API server
- [HAVN Frontend](https://github.com/havn/frontend) - HAVN admin/user dashboard
- [HAVN JS SDK](https://github.com/havn/havn-js-sdk) - JavaScript/TypeScript SDK
