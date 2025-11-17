# HAVN SDK - Dokumentasi

Dokumentasi lengkap untuk HAVN Python SDK, terpisah per fitur webhook.

## 📚 Daftar Dokumentasi

### Webhook Features

| Dokumen | Deskripsi | Key Features |
|---------|-----------|--------------|
| **[Auth Webhook](AUTH_WEBHOOK.md)** | User login via webhook | Email validation, temporary token, auto-redirect |
| **[Transaction Webhook](TRANSACTION_WEBHOOK.md)** | Kirim transaksi & distribusi komisi | Multi-currency, voucher support, custom fields |
| **[User Sync Webhook](USER_SYNC_WEBHOOK.md)** | Sync user data ke HAVN | Single/bulk sync, role management, upline hierarchy |
| **[Voucher Webhook](VOUCHER_WEBHOOK.md)** | Validasi & manajemen voucher | Validation, filtering, pagination, combine local |

---

## 🚀 Quick Links

### Berdasarkan Use Case

**Saya ingin...**

- **Login user ke HAVN dari SaaS saya**  
  → [Auth Webhook](AUTH_WEBHOOK.md)

- **Kirim transaksi dan hitung komisi**  
  → [Transaction Webhook](TRANSACTION_WEBHOOK.md)

- **Sync user dari Google OAuth**  
  → [User Sync Webhook - sync()](USER_SYNC_WEBHOOK.md#method-sync)

- **Sync banyak users sekaligus**  
  → [User Sync Webhook - sync_bulk()](USER_SYNC_WEBHOOK.md#method-sync_bulk)

- **Validasi kode voucher**  
  → [Voucher Webhook - validate()](VOUCHER_WEBHOOK.md#method-validate)

- **Get list vouchers dengan filter**  
  → [Voucher Webhook - get_all()](VOUCHER_WEBHOOK.md#method-get_all)

- **Combine HAVN voucher dengan voucher lokal**  
  → [Voucher Webhook - get_combined()](VOUCHER_WEBHOOK.md#method-get_combined)

---

## 📖 Struktur Dokumentasi

Setiap dokumen webhook memiliki struktur:

### 1. Overview
- Deskripsi fitur
- Key features
- Use cases

### 2. Methods
- Signature lengkap
- Parameter details
- Return types
- Error handling

### 3. Response Models
- Structure detail
- Field descriptions
- Example responses

### 4. Contoh Penggunaan
- Basic usage
- Framework integration (Flask, Django, FastAPI)
- Error handling
- Advanced scenarios

### 5. Best Practices
- Recommended patterns
- Performance tips
- Security notes
- Common pitfalls

---

## 🎯 Integration Flow

### Complete Integration Steps

```
1. Setup & Initialize
   ↓
2. Sync Users (User Sync Webhook)
   ↓
3. Login Users (Auth Webhook)
   ↓
4. Send Transactions (Transaction Webhook)
   ↓
5. Apply Vouchers (Voucher Webhook)
```

### Step-by-Step

#### 1. Initialize Client

```python
from havn import HAVNClient

client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret"
)
```

#### 2. Sync Project Owner

```python
# Sync owner dengan role "owner"
owner_result = client.users.sync(
    email="owner@company.com",
    name="Company Owner",
    is_owner=True,
    upline_code="HAVN-MJ-001"
)

owner_code = owner_result.referral_code
```

#### 3. Sync Team Members

```python
# Bulk sync team members
team_result = client.users.sync_bulk(
    users=[
        {"email": "member1@company.com", "name": "Member 1"},
        {"email": "member2@company.com", "name": "Member 2"}
    ],
    referral_code=owner_code  # Link ke owner
)
```

#### 4. Login User

```python
# User login ke HAVN
redirect_url = client.auth.login(email="owner@company.com")
# Redirect browser ke: redirect_url
```

#### 5. Validate & Send Transaction

```python
# Validate voucher
voucher_valid = client.vouchers.validate(
    voucher_code="SAVE10",
    amount=10000,
    currency="USD"
)

# Send transaction dengan voucher
result = client.transactions.send(
    amount=9000,  # After discount
    subtotal_transaction=10000,  # Before discount
    promo_code="SAVE10",
    referral_code=owner_code,
    currency="USD"
)

print(f"Commission distributed: ${result.total_commission/100:.2f}")
```

---

## 🔧 Framework Integration

### Flask

```python
from flask import Flask, redirect, request
from havn import HAVNClient

app = Flask(__name__)
client = HAVNClient(api_key="...", webhook_secret="...")

@app.route('/login')
def login():
    redirect_url = client.auth.login(email=request.args.get('email'))
    return redirect(redirect_url)

@app.route('/transaction', methods=['POST'])
def transaction():
    data = request.json
    result = client.transactions.send(
        amount=data['amount'],
        referral_code=data['referral_code']
    )
    return {"transaction_id": result.transaction.transaction_id}
```

### Django

```python
from django.http import HttpResponseRedirect, JsonResponse
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

def login_view(request):
    redirect_url = client.auth.login(email=request.GET['email'])
    return HttpResponseRedirect(redirect_url)

def transaction_view(request):
    result = client.transactions.send(
        amount=int(request.POST['amount']),
        referral_code=request.POST['referral_code']
    )
    return JsonResponse({"transaction_id": result.transaction.transaction_id})
```

### FastAPI

```python
from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from havn import HAVNClient

app = FastAPI()
client = HAVNClient(api_key="...", webhook_secret="...")

@app.get("/login")
async def login(email: str = Query(...)):
    redirect_url = client.auth.login(email=email)
    return RedirectResponse(url=redirect_url)

@app.post("/transaction")
async def transaction(amount: int, referral_code: str):
    result = client.transactions.send(
        amount=amount,
        referral_code=referral_code
    )
    return {"transaction_id": result.transaction.transaction_id}
```

---

## 🛡️ Error Handling

### Common Exceptions

```python
from havn import (
    HAVNAPIError,
    HAVNAuthError,
    HAVNValidationError,
    HAVNNetworkError,
    HAVNRateLimitError
)

try:
    result = client.transactions.send(amount=10000, referral_code="HAVN-MJ-001")
    
except HAVNAuthError as e:
    # API key/signature invalid
    print(f"Authentication failed: {e}")
    
except HAVNValidationError as e:
    # Parameter validation failed
    print(f"Validation error: {e}")
    
except HAVNRateLimitError as e:
    # Rate limit exceeded
    print(f"Rate limit: retry after {e.retry_after} seconds")
    
except HAVNNetworkError as e:
    # Network connection error
    print(f"Network error: {e}")
    
except HAVNAPIError as e:
    # General API error
    print(f"API error [{e.status_code}]: {e.message}")
```

---

## 📊 Response Models

### Common Patterns

Semua response menggunakan dataclass untuk type safety:

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TransactionResponse:
    transaction: Transaction
    commissions: List[Commission]
    total_commission: float
    currency: str

@dataclass
class UserSyncResponse:
    user: User
    associate: Optional[Associate]
    user_created: bool
    associate_created: bool
    referral_code: Optional[str]
```

Detail lengkap ada di masing-masing webhook documentation.

---

## ⚡ Performance Tips

### 1. Use Bulk Operations

```python
# ❌ SLOW: Multiple single requests
for user in users:
    client.users.sync(email=user['email'], name=user['name'])

# ✅ FAST: Single bulk request
client.users.sync_bulk(users=users)
```

### 2. Enable Test Mode untuk Development

```python
# Dry-run mode - tidak save data
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    test_mode=True
)
```

### 3. Cache Vouchers

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_active_vouchers():
    return client.vouchers.get_all(active=True, is_valid=True)
```

### 4. Implement Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def send_transaction_with_retry(amount, referral_code):
    return client.transactions.send(amount=amount, referral_code=referral_code)
```

---

## 🔐 Security Best Practices

1. **Never expose API keys** - Simpan di environment variables
2. **Use HTTPS** - Semua requests otomatis via HTTPS
3. **HMAC validation** - Otomatis di-handle oleh SDK
4. **Rate limiting** - Respect rate limits (20 req/min)
5. **Input validation** - Validate data sebelum kirim ke API

---

## 📞 Support

**Dokumentasi:**
- [Main README](../README.md)
- [Changelog](../CHANGELOG.md)

**Contact:**
- Email: bagus@intelove.com
- GitHub Issues: https://github.com/havn/havn-python-sdk/issues

**Examples:**
- Lihat folder `examples/` di root repository
- File: `05_auth_login.py`, `01_simple_transaction.py`, dll

---

## 📝 Notes

- Semua amount dalam **cents** atau **smallest unit** currency
- Semua datetime dalam **ISO 8601 format** dengan UTC timezone
- Referral code format: **HAVN-XX-XXX** (2 huruf + 3 digit)
- Semua responses menggunakan **dataclass** untuk type safety

---

**Happy Coding! 🚀**
