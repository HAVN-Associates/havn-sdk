# HAVN Python SDK

SDK Python resmi untuk integrasi dengan HAVN (Hierarchical Associate Voucher Network) API.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Fitur

- ✅ **API Sederhana & Intuitif** - Mudah digunakan dengan interface Pythonic
- ✅ **Autentikasi Otomatis** - HMAC-SHA256 signature generation otomatis
- ✅ **Type Hints** - Dukungan penuh untuk type annotation
- ✅ **Retry Logic** - Built-in retry dengan exponential backoff
- ✅ **Model Lengkap** - Model dengan validasi otomatis
- ✅ **Error Handling** - Custom exception dengan rate limit support
- ✅ **Test Mode** - Mode dry-run untuk testing tanpa side effects
- ✅ **Login Webhook** - User login dari SaaS company ke HAVN
- ✅ **Bulk Operations** - Bulk user sync untuk efisiensi tinggi
- ✅ **Role Management** - Support untuk owner dan partner role
- ✅ **Rate Limiting** - Automatic rate limit handling dengan retry
- ✅ **Currency Conversion** - Multi-currency support dengan auto-conversion
- ✅ **Voucher Management** - Get, validate, dan combine vouchers
- ✅ **Dokumentasi Lengkap** - Dokumentasi ekstensif dengan contoh kode

## Instalasi

```bash
pip install havn-sdk
```

Atau install dari source:

```bash
git clone https://github.com/havn/havn-python-sdk.git
cd havn-python-sdk
pip install -e .
```

## Quick Start

```python
from havn import HAVNClient

# Inisialisasi client
client = HAVNClient(
    api_key="your_api_key_here",
    webhook_secret="your_webhook_secret_here",
    base_url="https://api.havn.com"  # Opsional, default ke production
)

# Kirim transaksi
result = client.transactions.send(
    amount=10000,  # $100.00 dalam cents
    referral_code="HAVN-MJ-001",
    currency="USD",
    customer_type="NEW_CUSTOMER"
)

print(f"Transaction ID: {result.transaction.transaction_id}")
print(f"Komisi: {len(result.commissions)} level terdistribusi")
```

## Contoh Penggunaan

### 1. Login User

```python
# Login user dari SaaS company ke HAVN (via webhook)
redirect_url = client.auth.login(email="user@example.com")

# Integrasi dengan Flask
from flask import redirect
return redirect(redirect_url)

# Integrasi dengan Django
from django.http import HttpResponseRedirect
return HttpResponseRedirect(redirect_url)

# Integrasi dengan FastAPI
from fastapi.responses import RedirectResponse
return RedirectResponse(url=redirect_url)

# User akan di-redirect ke HAVN frontend dan otomatis login
```

### 2. Kirim Transaksi

```python
# Transaksi sederhana
result = client.transactions.send(
    amount=10000,
    referral_code="HAVN-MJ-001"
)

# Transaksi dengan voucher
result = client.transactions.send(
    amount=8000,  # Setelah diskon
    subtotal_transaction=10000,  # Sebelum diskon
    promo_code="VOUCHER123",
    referral_code="HAVN-MJ-001",
    currency="USD",
    customer_type="NEW_CUSTOMER"
)

# Transaksi dengan custom fields
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

### 3. Sync User

```python
# Sync user dari Google OAuth
result = client.users.sync(
    email="user@example.com",
    name="John Doe",
    google_id="google123",
    picture="https://example.com/photo.jpg",
    create_associate=True,
    upline_code="HAVN-MJ-001",
    is_owner=False  # Default: false (role: "partner")
)

# Sync project owner dengan role "owner"
result = client.users.sync(
    email="owner@shopeasy.com",
    name="John Doe",
    is_owner=True,  # Set role sebagai "owner"
    upline_code="HAVN-MJ-001"
)

print(f"User created: {result.user_created}")
print(f"Associate created: {result.associate_created}")
```

### 4. Bulk User Sync

```python
# Bulk sync beberapa users sekaligus dalam satu request
result = client.users.sync_bulk(
    users=[
        {"email": "owner@shopeasy.com", "name": "John Doe", "is_owner": True},
        {"email": "admin@shopeasy.com", "name": "Jane Smith"},
        {"email": "manager@shopeasy.com", "name": "Bob Johnson"},
    ],
    upline_code="HAVN-MJ-001"
)

print(f"Sukses: {result.summary.success}/{result.summary.total}")
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

### 5. Validasi Voucher

```python
# Validasi kode voucher
try:
    is_valid = client.vouchers.validate(
        voucher_code="VOUCHER123",
        amount=10000,
        currency="USD"
    )
    print("✅ Voucher valid")
except Exception as e:
    print(f"❌ Voucher tidak valid: {str(e)}")
```

### 6. Get Vouchers

```python
# Get semua vouchers dengan filtering dan pagination
result = client.vouchers.get_all(
    active=True,
    is_valid=True,
    page=1,
    per_page=20,
    display_currency="IDR"  # Convert amount ke IDR untuk display
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

### 7. Error Handling & Rate Limiting

```python
from havn import HAVNClient, HAVNRateLimitError, HAVNAPIError
import time

try:
    result = client.transactions.send(
        amount=10000,
        referral_code="HAVN-MJ-001"
    )
except HAVNRateLimitError as e:
    print(f"Rate limit terlampaui. Retry setelah {e.retry_after} detik")
    print(f"Limit: {e.limit}, Remaining: {e.remaining}")
    # Tunggu dan retry
    time.sleep(e.retry_after)
    result = client.transactions.send(
        amount=10000,
        referral_code="HAVN-MJ-001"
    )
except HAVNAPIError as e:
    print(f"API Error: {e.message} (status: {e.status_code})")
```

### 8. Test Mode (Dry-Run)

```python
# Aktifkan test mode - tidak ada data yang disimpan
client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret",
    test_mode=True  # Mode dry-run
)

result = client.transactions.send(
    amount=10000,
    referral_code="HAVN-MJ-001"
)
# Request akan sukses tapi tidak menyimpan data ke database
```

## Konfigurasi

### Environment Variables

```bash
export HAVN_API_KEY="your_api_key"
export HAVN_WEBHOOK_SECRET="your_webhook_secret"
export HAVN_BASE_URL="https://api.havn.com"  # Opsional
export HAVN_TIMEOUT=30  # Opsional, default 30 detik
export HAVN_MAX_RETRIES=3  # Opsional, default 3
```

Kemudian inisialisasi client tanpa parameter:

```python
from havn import HAVNClient

client = HAVNClient()  # Baca dari environment variables
```

### Konfigurasi Custom

```python
client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret",
    base_url="https://api.havn.com",
    timeout=30,  # Request timeout dalam detik
    max_retries=3,  # Jumlah retry attempts
    backoff_factor=0.5,  # Exponential backoff multiplier
    test_mode=False  # Aktifkan mode dry-run
)
```

## Error Handling

```python
from havn import HAVNClient
from havn.exceptions import (
    HAVNAPIError,
    HAVNAuthError,
    HAVNValidationError,
    HAVNNetworkError,
    HAVNRateLimitError
)

client = HAVNClient(api_key="...", webhook_secret="...")

try:
    result = client.transactions.send(
        amount=10000,
        referral_code="HAVN-MJ-001"
    )
except HAVNAuthError as e:
    print(f"Autentikasi gagal: {e}")
except HAVNValidationError as e:
    print(f"Error validasi: {e}")
except HAVNRateLimitError as e:
    print(f"Rate limit terlampaui: retry setelah {e.retry_after} detik")
except HAVNNetworkError as e:
    print(f"Error network: {e}")
except HAVNAPIError as e:
    print(f"API error: {e}")
```

## Dokumentasi

Dokumentasi lengkap tersedia di folder `docs/`:

### 📚 Dokumentasi Utama

- **[Dokumentasi Lengkap](docs/README.md)** - Index semua dokumentasi webhook
- **[Auth Webhook](docs/AUTH_WEBHOOK.md)** - Login user via webhook
- **[Transaction Webhook](docs/TRANSACTION_WEBHOOK.md)** - Kirim transaksi & komisi
- **[User Sync Webhook](docs/USER_SYNC_WEBHOOK.md)** - Sync user data
- **[Voucher Webhook](docs/VOUCHER_WEBHOOK.md)** - Validasi & manajemen voucher

### 📖 Quick Links

**Getting Started:**

- Lihat bagian [Quick Start](#quick-start) di atas
- Atau lihat [Docs README](docs/README.md) untuk panduan lengkap

**Webhook Documentation:**

- [Auth Webhook](docs/AUTH_WEBHOOK.md) - Login user
  - `client.auth.login(email)` - Login via webhook
- [Transaction Webhook](docs/TRANSACTION_WEBHOOK.md) - Kirim transaksi
  - `client.transactions.send(**kwargs)` - Send transaction
- [User Sync Webhook](docs/USER_SYNC_WEBHOOK.md) - Sync users
  - `client.users.sync(**kwargs)` - Sync single user
  - `client.users.sync_bulk(**kwargs)` - Bulk sync
- [Voucher Webhook](docs/VOUCHER_WEBHOOK.md) - Manage vouchers
  - `client.vouchers.validate(**kwargs)` - Validate voucher
  - `client.vouchers.get_all(**kwargs)` - Get vouchers
  - `client.vouchers.get_combined(**kwargs)` - Combine HAVN + local

### 🚀 Quick Reference

**Client Methods:**

- `client.auth.login(email)` - Login user ke HAVN via webhook
- `client.transactions.send(**kwargs)` - Kirim transaksi
- `client.users.sync(**kwargs)` - Sync data user
- `client.users.sync_bulk(**kwargs)` - Bulk sync beberapa users sekaligus
- `client.vouchers.validate(**kwargs)` - Validasi voucher
- `client.vouchers.get_all(**kwargs)` - Get semua vouchers dengan filtering, pagination, search
- `client.vouchers.get_combined(**kwargs)` - Get combined vouchers (HAVN + local)

**Response Models:**

- `TransactionResponse` - Response transaksi dengan data commissions
- `UserSyncResponse` - Response user sync dengan data user dan associate
- `BulkUserSyncResponse` - Response bulk sync dengan summary statistics
- `VoucherListResponse` - Response voucher list dengan pagination dan filtering
- Voucher validation mengembalikan `bool` (True jika valid)
- Auth login mengembalikan `str` (redirect URL)

Lihat [Dokumentasi Lengkap](docs/README.md) untuk detail setiap webhook.

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/havn/havn-python-sdk.git
cd havn-python-sdk

# Buat virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

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
# Run semua tests
pytest

# Run dengan coverage
pytest --cov=havn --cov-report=html

# Run test file tertentu
pytest tests/test_client.py

# Run dengan output verbose
pytest -v
```

## Contributing

Kontribusi sangat diterima! Silakan buka issue atau submit pull request di GitHub.

## License

Project ini menggunakan MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## Support & Resources

### 📚 Documentation

- **[Docs Index](docs/README.md)** - Index lengkap semua dokumentasi
- **[Auth Webhook](docs/AUTH_WEBHOOK.md)** - Login user documentation
- **[Transaction Webhook](docs/TRANSACTION_WEBHOOK.md)** - Transaction documentation
- **[User Sync Webhook](docs/USER_SYNC_WEBHOOK.md)** - User sync documentation
- **[Voucher Webhook](docs/VOUCHER_WEBHOOK.md)** - Voucher documentation

### 💬 Get Help

- 📧 **Email**: bagus@intelove.com
- 📖 **Documentation**: https://docs.havn.com
- 🐛 **GitHub Issues**: https://github.com/havn/havn-python-sdk/issues
- 💻 **Examples**: Check folder `examples/` untuk contoh code yang bisa di-run

### 🆘 Common Issues

**Authentication Error (401):**

- Pastikan API key dan webhook secret benar
- Cek environment variables jika menggunakan env vars

**Rate Limit Error (429):**

- Gunakan `HAVNRateLimitError` untuk proper handling
- Implement exponential backoff
- Gunakan bulk sync untuk mengurangi jumlah requests

**Network Error:**

- Cek koneksi internet
- Cek HAVN API status
- Implement retry logic

**Login Webhook Error:**

- Pastikan user sudah di-sync ke HAVN dengan `client.users.sync()`
- Pastikan user status active
- Cek format email valid

Lihat [Dokumentasi](docs/README.md) untuk error handling patterns lengkap.

## Changelog

Lihat [CHANGELOG.md](CHANGELOG.md) untuk riwayat versi.

## Related Projects

- [HAVN Backend](https://github.com/havn/backend) - HAVN API server
- [HAVN Frontend](https://github.com/havn/frontend) - HAVN admin/user dashboard
- [HAVN JS SDK](https://github.com/havn/havn-js-sdk) - JavaScript/TypeScript SDK
