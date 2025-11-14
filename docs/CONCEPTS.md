# Konsep Dasar HAVN SDK

Dokumen ini menjelaskan konsep-konsep inti dalam HAVN Python SDK untuk membantu Anda memahami cara kerja SDK sebelum menggunakannya.

## Daftar Isi

- [Overview](#overview)
- [Arsitektur SDK](#arsitektur-sdk)
- [Authentication](#authentication)
- [Webhooks vs API](#webhooks-vs-api)
- [Model dan Response](#model-dan-response)
- [Error Handling](#error-handling)
- [Test Mode](#test-mode)

---

## Overview

HAVN SDK adalah pustaka Python yang memungkinkan aplikasi SaaS Anda berintegrasi dengan HAVN API untuk mengelola:
- **Transaksi dan Komisi**: Mencatat transaksi dan mendistribusikan komisi ke network associate
- **User Synchronization**: Menyinkronkan data user dari Google OAuth atau sumber lain
- **Voucher Validation**: Memvalidasi kode voucher sebelum digunakan

---

## Arsitektur SDK

### Struktur Modul

```
havn/
├── client.py           # HAVNClient - main client class
├── config.py           # Configuration management
├── exceptions.py       # Custom exceptions
├── models/            # Data models (Pydantic/dataclass)
│   ├── transaction.py
│   ├── user_sync.py
│   └── voucher.py
├── webhooks/          # Webhook handlers
│   ├── transaction.py
│   ├── user_sync.py
│   └── voucher.py
└── utils/             # Utility functions
    ├── auth.py        # HMAC signature generation
    └── validators.py  # Input validation
```

### Flow Request

```
1. User Code
   ↓
2. Webhook Handler (transactions/users/vouchers)
   ↓
3. Payload Validation (models)
   ↓
4. HAVNClient._make_request()
   ↓
5. Authentication Headers (HMAC signature)
   ↓
6. HTTP Request (with retry logic)
   ↓
7. Response Parsing (models)
   ↓
8. Return Typed Response
```

---

## Authentication

### HMAC-SHA256 Signature

Semua request ke HAVN API menggunakan **HMAC-SHA256 signature** untuk keamanan:

1. **API Key**: Di-set di header `X-API-Key`
2. **Signature**: Di-generate dari payload menggunakan `webhook_secret`
3. **Timestamp**: Di-generate otomatis oleh SDK

### Contoh Signature Generation

```python
import hmac
import hashlib
import json

payload = {"amount": 10000, "referral_code": "HAVN-MJ-001"}
payload_str = json.dumps(payload, sort_keys=True)
signature = hmac.new(
    webhook_secret.encode(),
    payload_str.encode(),
    hashlib.sha256
).hexdigest()
```

**Catatan**: SDK menangani ini otomatis, Anda tidak perlu membuat signature manual.

### Credentials

Anda memerlukan 2 kredensial dari HAVN Dashboard:

1. **API Key**: Untuk identifikasi aplikasi Anda
2. **Webhook Secret**: Untuk generate HMAC signature

**Jangan pernah** commit credentials ke repository! Gunakan environment variables.

---

## Webhooks vs API

### Mengapa "Webhook"?

HAVN SDK menggunakan terminologi "webhook" meskipun sebenarnya ini adalah **outbound webhook calls** dari aplikasi Anda ke HAVN API. Ini berarti:

- **Outbound**: Aplikasi Anda **mengirim** data ke HAVN (bukan menerima)
- **Synchronous**: Request menunggu response dari HAVN API
- **Idempotent**: Request dapat di-retry dengan aman

### Tiga Jenis Webhook

1. **Transaction Webhook** (`/api/v1/webhook/transaction`)
   - Mengirim data transaksi
   - Mendapat response dengan komisi yang didistribusikan

2. **User Sync Webhook** (`/api/v1/webhook/user-sync`)
   - Menyinkronkan data user (dari Google OAuth, dll)
   - Membuat atau update user dan associate

3. **Voucher Validation Webhook** (`/api/v1/webhook/voucher/validate`)
   - Memvalidasi kode voucher
   - Tidak mengembalikan body response (hanya status code)

---

## Model dan Response

### Payload Models

Semua input menggunakan **dataclass models** dengan validasi:

- `TransactionPayload`: Data untuk transaction webhook
- `UserSyncPayload`: Data untuk user sync webhook
- `VoucherValidationPayload`: Data untuk voucher validation

**Keuntungan**:
- Type safety dengan type hints
- Automatic validation
- Easy serialization ke dictionary

### Response Models

Semua response di-parse menjadi **typed dataclass models**:

- `TransactionResponse`: Response dari transaction webhook
  - `transaction`: `TransactionData`
  - `commissions`: `List[CommissionData]`
  
- `UserSyncResponse`: Response dari user sync webhook
  - `user`: `UserData`
  - `associate`: `AssociateData` (optional)

**Keuntungan**:
- Type-safe access ke response data
- Autocomplete di IDE
- Built-in validation

### Contoh Response

```python
result = client.transactions.send(amount=10000, referral_code="HAVN-MJ-001")

# Typed access
print(result.transaction.transaction_id)  # String
print(result.transaction.amount)          # Integer (cents)
print(len(result.commissions))            # Integer

# Access raw response if needed
raw_data = result.raw_response
```

---

## Error Handling

### Exception Hierarchy

```
HAVNError (base)
├── HAVNAPIError       # API errors (4xx, 5xx)
├── HAVNAuthError      # Authentication errors (401)
├── HAVNValidationError # Validation errors (before request)
└── HAVNNetworkError   # Network errors (timeout, connection)
```

### Error Handling Best Practice

```python
from havn import HAVNClient
from havn.exceptions import (
    HAVNAuthError,
    HAVNValidationError,
    HAVNAPIError,
    HAVNNetworkError
)

try:
    result = client.transactions.send(amount=10000, referral_code="HAVN-MJ-001")
except HAVNValidationError as e:
    # Input validation error (sebelum request)
    print(f"Invalid input: {e}")
except HAVNAuthError as e:
    # Authentication error (401)
    print(f"Authentication failed: {e}")
except HAVNAPIError as e:
    # API error (4xx, 5xx)
    print(f"API error ({e.status_code}): {e.message}")
    if e.response:
        print(f"Details: {e.response}")
except HAVNNetworkError as e:
    # Network error (timeout, connection)
    print(f"Network error: {e}")
    if e.original_error:
        print(f"Original error: {e.original_error}")
```

---

## Test Mode

### Apa itu Test Mode?

**Test Mode** adalah mode **dry-run** yang memungkinkan Anda menguji integrasi tanpa menyimpan data ke database HAVN.

### Cara Kerja

1. Request dikirim ke HAVN API dengan header `X-Test-Mode: true`
2. HAVN API memproses request dan validasi
3. Response dikembalikan seperti normal
4. **Tapi data tidak disimpan** ke database

### Penggunaan

```python
# Enable test mode
client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret",
    test_mode=True  # Enable dry-run mode
)

# Request akan return success tapi tidak save data
result = client.transactions.send(amount=10000, referral_code="HAVN-MJ-001")
# ✅ Response OK, tapi transaksi tidak tersimpan
```

### Kapan Menggunakan

- **Development**: Testing integrasi di local environment
- **Staging**: Testing di staging environment tanpa mengganggu production data
- **Debugging**: Memverifikasi request format dan validation

**⚠️ Catatan**: Test mode tidak mengembalikan komisi real, hanya simulasi.

---

## Retry Logic

### Automatic Retry

SDK secara otomatis melakukan retry pada request yang gagal:

- **Status codes**: 429, 500, 502, 503, 504
- **Max retries**: 3 (default, dapat diubah)
- **Backoff**: Exponential backoff (default: 0.5x multiplier)

### Retry Strategy

```
Attempt 1: Immediate
Attempt 2: Wait 0.5s
Attempt 3: Wait 1.0s
Attempt 4: Wait 2.0s
```

### Konfigurasi

```python
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    max_retries=5,      # Increase retry attempts
    backoff_factor=1.0  # Increase backoff delay
)
```

---

## Amount Format

### Cent-based System

Semua amount di HAVN SDK menggunakan **cents** (bukan decimal):

```python
# ✅ Correct
amount = 10000  # $100.00

# ❌ Wrong
amount = 100.00  # Jangan gunakan float!
```

### Konversi

```python
# Dollar ke cents
dollars = 100.00
cents = int(dollars * 100)  # 10000

# Cents ke dollar
cents = 10000
dollars = cents / 100  # 100.00
```

### Validasi

- Minimum: 1 cent
- Maximum: $10,000,000 (1,000,000,000 cents)

---

## Best Practices

### 1. Always Use Environment Variables

```python
# ❌ Don't hardcode
client = HAVNClient(api_key="hardcoded-key", webhook_secret="hardcoded-secret")

# ✅ Use environment variables
import os
client = HAVNClient(
    api_key=os.getenv("HAVN_API_KEY"),
    webhook_secret=os.getenv("HAVN_WEBHOOK_SECRET")
)
```

### 2. Handle Errors Properly

```python
# ❌ Don't catch all exceptions
try:
    result = client.transactions.send(...)
except Exception as e:
    print(e)  # Too generic!

# ✅ Catch specific exceptions
try:
    result = client.transactions.send(...)
except HAVNValidationError as e:
    # Handle validation errors
    pass
except HAVNAPIError as e:
    # Handle API errors
    pass
```

### 3. Use Context Manager

```python
# ✅ Close session properly
with HAVNClient(api_key="...", webhook_secret="...") as client:
    result = client.transactions.send(...)
# Session closed automatically
```

### 4. Validate Input Early

```python
# ✅ SDK validates automatically, but you can validate early
from havn.utils.validators import validate_amount, validate_email

amount = 10000
validate_amount(amount)  # Raises ValueError if invalid

email = "user@example.com"
validate_email(email)  # Raises ValueError if invalid
```

---

## Next Steps

- Baca [Quick Start Guide](QUICKSTART.md) untuk mulai menggunakan SDK
- Lihat [API Reference](API_REFERENCE.md) untuk dokumentasi lengkap
- Check [Examples](../examples/) untuk contoh penggunaan
- Baca [Configuration Guide](CONFIGURATION.md) untuk konfigurasi lanjutan

