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
- ✅ **Error Handling** - Descriptive custom exceptions with rate limit support
- ✅ **Test Mode** - Dry-run mode for testing without side effects
- ✅ **Bulk Operations** - Bulk user sync untuk efficiency
- ✅ **Role Management** - Support untuk owner role assignment
- ✅ **Rate Limiting** - Automatic rate limit handling with retry logic
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
    upline_code="HAVN-MJ-001",
    is_owner=False  # Default: false (role: "partner")
)

# Sync project owner with "owner" role
result = client.users.sync(
    email="owner@shopeasy.com",
    name="John Doe",
    is_owner=True,  # Set role sebagai "owner"
    upline_code="HAVN-MJ-001"
)

print(f"User created: {result.user_created}")
print(f"Associate created: {result.associate_created}")
```

### Bulk User Sync

```python
# Bulk sync multiple users dalam satu request
result = client.users.sync_bulk(
    users=[
        {"email": "owner@shopeasy.com", "name": "John Doe", "is_owner": True},
        {"email": "admin@shopeasy.com", "name": "Jane Smith"},
        {"email": "manager@shopeasy.com", "name": "Bob Johnson"},
    ],
    upline_code="HAVN-MJ-001"
)

print(f"Success: {result.summary.success}/{result.summary.total}")
print(f"Referral code: {result.referral_code}")

# Link semua users ke associate yang sama
result = client.users.sync_bulk(
    users=[
        {"email": "admin@shopeasy.com", "name": "Jane Smith"},
        {"email": "manager@shopeasy.com", "name": "Bob Johnson"},
    ],
    referral_code="HAVN-SE-001"  # Dari batch sebelumnya
)
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

### Get Vouchers

```python
# Get all vouchers dengan filtering dan pagination
result = client.vouchers.get_all(
    active=True,
    is_valid=True,
    page=1,
    per_page=20,
    display_currency="IDR"  # Convert amounts to IDR for display
)

for voucher in result.data:
    print(f"{voucher.code}: {voucher.value} {voucher.currency}")
    print(f"Is HAVN: {voucher.is_havn_voucher}")

# Get combined vouchers (HAVN + local)
def get_local_vouchers():
    return [{"code": "LOCAL123", "type": "DISCOUNT_PERCENTAGE", ...}]

result = client.vouchers.get_combined(
    local_vouchers_callback=get_local_vouchers,
    active=True,
    display_currency="IDR"
)
```

### Error Handling & Rate Limiting

```python
from havn import HAVNClient, HAVNRateLimitError, HAVNAPIError
import time

try:
    result = client.transactions.send(
        amount=10000,
        referral_code="HAVN-MJ-001"
    )
except HAVNRateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
    print(f"Limit: {e.limit}, Remaining: {e.remaining}")
    # Wait and retry
    time.sleep(e.retry_after)
    result = client.transactions.send(
        amount=10000,
        referral_code="HAVN-MJ-001"
    )
except HAVNAPIError as e:
    print(f"API Error: {e.message} (status: {e.status_code})")
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

### 📚 Dokumentasi Utama

- **[API Reference](docs/API_REFERENCE.md)** - Dokumentasi lengkap semua methods, parameters, dan models
- **[Integration Flow](docs/INTEGRATION_FLOW.md)** - Panduan lengkap flow integrasi (project creation, user sync, transaction)
- **[Examples](docs/EXAMPLES.md)** - Contoh penggunaan lengkap berbagai skenario

### 📖 Quick Links

**Getting Started:**

- Lihat bagian [Quick Start](#quick-start) di atas
- Atau lihat [Integration Flow](docs/INTEGRATION_FLOW.md) untuk panduan lengkap

**Examples:**

- [Transaction Examples](docs/EXAMPLES.md#transaction-examples)
- [User Sync Examples](docs/EXAMPLES.md#user-sync-examples)
- [Bulk User Sync Examples](docs/EXAMPLES.md#bulk-user-sync-basic)
- [Voucher Validation Examples](docs/EXAMPLES.md#voucher-validation-examples)
- [Error Handling Examples](docs/EXAMPLES.md#error-handling-examples)

**Integration Flow:**

- [Complete Integration Flow](docs/INTEGRATION_FLOW.md#complete-integration-flow)
- [Project Creation](docs/INTEGRATION_FLOW.md#1-project-creation)
- [User Sync ke HAVN](docs/INTEGRATION_FLOW.md#2-user-sync-ke-havn)
- [Bulk User Sync](docs/INTEGRATION_FLOW.md#bulk-user-sync-sync-multiple-users-dalam-project)
- [Payment/Transaction](docs/INTEGRATION_FLOW.md#3-paymenttransaction)

**API Reference:**

- [HAVNClient](docs/API_REFERENCE.md#havnclient)
- [TransactionWebhook](docs/API_REFERENCE.md#transactionwebhook)
  - [send()](docs/API_REFERENCE.md#send) - Send transaction dengan currency conversion support
- [UserSyncWebhook](docs/API_REFERENCE.md#usersyncwebhook)
  - [sync()](docs/API_REFERENCE.md#sync) - Sync single user dengan is_owner support
  - [sync_bulk()](docs/API_REFERENCE.md#sync_bulk) - Bulk user sync dengan is_owner support
- [VoucherWebhook](docs/API_REFERENCE.md#voucherwebhook)
  - [validate()](docs/API_REFERENCE.md#validate) - Validate voucher dengan currency conversion
  - [get_all()](docs/API_REFERENCE.md#get_all) - Get all vouchers dengan pagination, filtering, search
  - [get_combined()](docs/API_REFERENCE.md#get_combined) - Get combined vouchers (HAVN + local)
- [Models](docs/API_REFERENCE.md#models)
- [Exceptions](docs/API_REFERENCE.md#exceptions)
- [Currency Utilities](docs/API_REFERENCE.md#currency-utilities)

### 🚀 Quick Reference

**Client Methods:**

- `client.transactions.send(**kwargs)` - Send transaction
- `client.users.sync(**kwargs)` - Sync user data
- `client.users.sync_bulk(**kwargs)` - Bulk sync multiple users
- `client.vouchers.validate(**kwargs)` - Validate voucher
- `client.vouchers.get_all(**kwargs)` - Get all vouchers dengan filtering, pagination, search
- `client.vouchers.get_combined(**kwargs)` - Get combined vouchers (HAVN + local)

**Response Models:**

- `TransactionResponse` - Transaction webhook response dengan commissions
- `UserSyncResponse` - User sync webhook response dengan user dan associate data
- `BulkUserSyncResponse` - Bulk user sync response dengan summary statistics
- `VoucherListResponse` - Voucher list response dengan pagination dan filtering
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

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support & Resources

### 📚 Documentation

- **API Reference**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md) - Lengkap semua methods dan parameters
- **Integration Flow**: [docs/INTEGRATION_FLOW.md](docs/INTEGRATION_FLOW.md) - Panduan integrasi lengkap
- **Examples**: [docs/EXAMPLES.md](docs/EXAMPLES.md) - Contoh penggunaan berbagai skenario

### 💬 Get Help

- 📧 **Email**: bagus@intelove.com
- 📖 **Documentation**: https://docs.havn.com
- 🐛 **GitHub Issues**: https://github.com/havn/havn-python-sdk/issues
- 💻 **Examples**: Check folder `examples/` untuk contoh code yang bisa di-run

### 🆘 Common Issues

**Authentication Error (401):**

- Pastikan API key dan webhook secret benar
- Check environment variables jika menggunakan env vars

**Rate Limit Error (429):**

- Gunakan `HAVNRateLimitError` untuk proper handling
- Implement exponential backoff
- Gunakan bulk sync untuk mengurangi jumlah requests

**Network Error:**

- Check koneksi internet
- Check HAVN API status
- Implement retry logic

Lihat [Examples](docs/EXAMPLES.md#error-handling-examples) untuk error handling patterns lengkap.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Related Projects

- [HAVN Backend](https://github.com/havn/backend) - HAVN API server
- [HAVN Frontend](https://github.com/havn/frontend) - HAVN admin/user dashboard
- [HAVN JS SDK](https://github.com/havn/havn-js-sdk) - JavaScript/TypeScript SDK
