# Quick Start Guide

Panduan cepat untuk memulai menggunakan HAVN Python SDK dalam 5 menit.

## Installation

### Install dari PyPI

```bash
pip install havn-sdk
```

### Install dari Source

```bash
pip install git+https://github.com/HAVN-Associates/havn-sdk.git
```

### Install untuk Development

```bash
git clone https://github.com/HAVN-Associates/havn-sdk.git
cd havn-sdk
pip install -e ".[dev]"
```

## Basic Setup

### Step 1: Dapatkan Credentials

Anda memerlukan 2 credentials dari HAVN Dashboard:

1. **API Key** - Untuk autentikasi aplikasi Anda
2. **Webhook Secret** - Untuk generate HMAC signature

**Cara Mendapatkan**:

1. Login ke HAVN Dashboard
2. Navigate ke Settings > API Keys
3. Create new API key atau copy existing key
4. Simpan **API Key** dan **Webhook Secret** dengan aman

### Step 2: Setup Environment Variables (Recommended)

**Linux/Mac**:

```bash
export HAVN_API_KEY="your_api_key_here"
export HAVN_WEBHOOK_SECRET="your_webhook_secret_here"
```

**Windows (CMD)**:

```cmd
set HAVN_API_KEY=your_api_key_here
set HAVN_WEBHOOK_SECRET=your_webhook_secret_here
```

**Windows (PowerShell)**:

```powershell
$env:HAVN_API_KEY="your_api_key_here"
$env:HAVN_WEBHOOK_SECRET="your_webhook_secret_here"
```

**Python (.env file)**:

```bash
# .env file
HAVN_API_KEY=your_api_key_here
HAVN_WEBHOOK_SECRET=your_webhook_secret_here
```

```python
from dotenv import load_dotenv
load_dotenv()
```

### Step 3: Initialize Client

**Menggunakan Environment Variables** (Recommended):

```python
from havn import HAVNClient

# Otomatis membaca dari environment variables
client = HAVNClient()
```

**Menggunakan Explicit Parameters**:

```python
from havn import HAVNClient

client = HAVNClient(
    api_key="your_api_key_here",
    webhook_secret="your_webhook_secret_here"
)
```

## Your First Transaction

### Contoh Sederhana

```python
from havn import HAVNClient

# Initialize client
client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret"
)

# Kirim transaksi
result = client.transactions.send(
    amount=10000,  # $100.00 dalam cents
    referral_code="HAVN-MJ-001",
    currency="USD"
)

# Access hasil
print(f"✅ Transaction berhasil!")
print(f"Transaction ID: {result.transaction.transaction_id}")
print(f"Amount: ${result.transaction.amount / 100:.2f}")
print(f"Status: {result.transaction.status}")
print(f"Commissions: {len(result.commissions)} levels")

# Print detail komisi
for commission in result.commissions:
    print(f"  Level {commission.level}: ${commission.amount / 100:.2f} ({commission.percentage}%)")
```

### Error Handling

```python
from havn import HAVNClient
from havn.exceptions import (
    HAVNAuthError,
    HAVNValidationError,
    HAVNAPIError
)

client = HAVNClient(api_key="...", webhook_secret="...")

try:
    result = client.transactions.send(
        amount=10000,
        referral_code="HAVN-MJ-001"
    )
    print(f"✅ Success: {result.transaction.transaction_id}")

except HAVNValidationError as e:
    print(f"❌ Validation error: {e}")
except HAVNAuthError as e:
    print(f"❌ Authentication failed: {e}")
except HAVNAPIError as e:
    print(f"❌ API error: {e}")
```

## Contoh Lainnya

### Transaction dengan Voucher

```python
result = client.transactions.send(
    amount=8000,  # $80.00 (setelah diskon)
    subtotal_transaction=10000,  # $100.00 (sebelum diskon)
    promo_code="VOUCHER123",
    referral_code="HAVN-MJ-001",
    currency="USD"
)
```

### User Sync

```python
result = client.users.sync(
    email="user@example.com",
    name="John Doe",
    google_id="google_oauth_id",
    create_associate=True,
    upline_code="HAVN-MJ-001"
)

print(f"User created: {result.user_created}")
print(f"Associate created: {result.associate_created}")
```

### Voucher Validation

```python
try:
    is_valid = client.vouchers.validate(
        voucher_code="VOUCHER123",
        amount=10000
    )
    print("✅ Voucher valid")
except HAVNAPIError:
    print("❌ Voucher invalid")
```

## Test Mode

Gunakan test mode untuk testing tanpa menyimpan data:

```python
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    test_mode=True  # Dry-run mode
)

# Request akan return success tapi tidak save data
result = client.transactions.send(amount=10000, referral_code="HAVN-MJ-001")
```

## Context Manager

Gunakan context manager untuk auto-close session:

```python
with HAVNClient(api_key="...", webhook_secret="...") as client:
    result = client.transactions.send(amount=10000, referral_code="HAVN-MJ-001")
    print(result.transaction.transaction_id)
# Session ditutup otomatis
```

## Bulk User Sync

Sync multiple users dalam satu request menggunakan `sync_bulk()`:

```python
# Sync multiple users
result = client.users.sync_bulk(
    users=[
        {"email": "user1@example.com", "name": "John Doe"},
        {"email": "user2@example.com", "name": "Jane Smith"},
    ],
    upline_code="HAVN-MJ-001"
)

print(f"Success: {result.summary.success}/{result.summary.total}")
print(f"Referral code: {result.referral_code}")
```

Untuk batch processing dan link multiple users ke associate yang sama, lihat [Examples](EXAMPLES.md) dan [Integration Flow](INTEGRATION_FLOW.md).

## Next Steps

Setelah menguasai dasar-dasar:

1. **📖 Baca Dokumentasi Lengkap**:

   - [Concepts Guide](CONCEPTS.md) - Memahami konsep dasar SDK
   - [API Reference](API_REFERENCE.md) - Dokumentasi lengkap semua methods termasuk bulk sync
   - [Configuration Guide](CONFIGURATION.md) - Panduan konfigurasi lanjutan

2. **💻 Lihat Contoh Penggunaan**:

   - [Examples](EXAMPLES.md) - Contoh lengkap berbagai skenario termasuk bulk sync
   - [Integration Flow](INTEGRATION_FLOW.md) - Panduan integrasi lengkap dengan bulk sync
   - [Examples Directory](../examples/) - Contoh code yang bisa di-run

3. **🔧 Advanced Topics**:

   - [Troubleshooting Guide](TROUBLESHOOTING.md) - Menyelesaikan masalah umum
   - Error handling patterns
   - Best practices

4. **🚀 Production Ready**:
   - Setup environment variables
   - Configure retry logic
   - Implement logging
   - Set up monitoring

## Support

Jika ada pertanyaan:

- 📧 Email: bagus@intelove.com
- 📖 Docs: https://docs.havn.com
- 🐛 Issues: https://github.com/havn/havn-python-sdk/issues
