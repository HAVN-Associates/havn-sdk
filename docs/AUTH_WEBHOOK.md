# Auth Webhook

Dokumentasi untuk AuthWebhook - User login dari SaaS company ke HAVN.

## Daftar Isi

- [Overview](#overview)
- [Method: login()](#method-login)
- [Response](#response)
- [Error Handling](#error-handling)
- [Contoh Penggunaan](#contoh-penggunaan)

---

## Overview

`AuthWebhook` menyediakan method untuk login user dari SaaS company ke HAVN via webhook dengan temporary token generation dan auto-redirect ke HAVN frontend.

**Key Features:**
- ✅ Email validation otomatis
- ✅ HMAC signature authentication
- ✅ Temporary token generation
- ✅ Auto-redirect ke HAVN frontend
- ✅ Rate limiting: 20 requests/minute
- ✅ Support Flask, Django, FastAPI

---

## Method: login()

Login user dari SaaS company ke HAVN.

### Signature

```python
def login(email: str) -> str
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | `str` | Yes | Email address user yang akan login |

### Returns

`str` - Redirect URL ke HAVN frontend dengan temporary token

### Raises

| Exception | Condition |
|-----------|-----------|
| `HAVNValidationError` | Email tidak valid |
| `HAVNAuthError` | API key/signature validation gagal |
| `HAVNAPIError` | User tidak ditemukan atau inactive |
| `HAVNRateLimitError` | Rate limit terlampaui (20 req/min) |

### Flow

```
1. SaaS company calls client.auth.login(email)
   ↓
2. SDK sends request ke HAVN backend
   ↓
3. Backend validates:
   - API key valid?
   - HMAC signature valid?
   - User exists?
   - User active?
   ↓
4. Backend generates temporary token
   ↓
5. Backend returns redirect URL
   ↓
6. SaaS redirects user browser ke URL
   ↓
7. HAVN frontend auto-login user dengan token
```

---

## Response

**Success Response:**

```python
redirect_url: str
# Example: "https://app.havn.com/login?token=eyJhbGc..."
```

**Response Structure (Backend):**

```json
{
  "success": true,
  "data": {
    "redirect_url": "https://app.havn.com/login?token=...",
    "token": "eyJhbGc..."
  },
  "message": "Login successful - redirect user to provided URL"
}
```

---

## Error Handling

### Common Errors

**1. Invalid Email (HAVNValidationError)**

```python
try:
    client.auth.login(email="invalid-email")
except HAVNValidationError as e:
    print(f"Email tidak valid: {e}")
```

**2. User Not Found (HAVNAPIError - 404)**

```python
try:
    client.auth.login(email="notfound@example.com")
except HAVNAPIError as e:
    if e.status_code == 404:
        print("User tidak ditemukan. Sync user terlebih dahulu.")
```

**3. User Inactive (HAVNAPIError - 400)**

```python
try:
    client.auth.login(email="inactive@example.com")
except HAVNAPIError as e:
    if e.status_code == 400:
        print("User inactive. Hubungi HAVN admin.")
```

**4. Rate Limit (HAVNRateLimitError)**

```python
import time

try:
    client.auth.login(email="user@example.com")
except HAVNRateLimitError as e:
    print(f"Rate limit. Retry setelah {e.retry_after} detik")
    time.sleep(e.retry_after)
    # Retry
    client.auth.login(email="user@example.com")
```

---

## Contoh Penggunaan

### 1. Basic Usage

```python
from havn import HAVNClient

client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret"
)

# Login user
redirect_url = client.auth.login(email="user@example.com")
print(f"Redirect user ke: {redirect_url}")
```

### 2. Flask Integration

```python
from flask import Flask, redirect, request
from havn import HAVNClient

app = Flask(__name__)
client = HAVNClient(api_key="...", webhook_secret="...")

@app.route('/login-to-havn')
def login_to_havn():
    """Redirect user ke HAVN"""
    user_email = request.args.get('email')
    
    try:
        redirect_url = client.auth.login(email=user_email)
        return redirect(redirect_url)
    except Exception as e:
        return f"Login failed: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)
```

### 3. Django Integration

```python
from django.http import HttpResponseRedirect
from django.shortcuts import render
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

def login_to_havn(request):
    """Redirect user ke HAVN"""
    user_email = request.GET.get('email')
    
    try:
        redirect_url = client.auth.login(email=user_email)
        return HttpResponseRedirect(redirect_url)
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})
```

### 4. FastAPI Integration

```python
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import RedirectResponse
from havn import HAVNClient

app = FastAPI()
client = HAVNClient(api_key="...", webhook_secret="...")

@app.get("/login-to-havn")
async def login_to_havn(email: str = Query(...)):
    """Redirect user ke HAVN"""
    try:
        redirect_url = client.auth.login(email=email)
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 5. Dengan Error Handling Lengkap

```python
from havn import HAVNClient, HAVNAPIError, HAVNValidationError, HAVNAuthError
import logging

logger = logging.getLogger(__name__)
client = HAVNClient(api_key="...", webhook_secret="...")

def login_user_to_havn(email: str) -> str:
    """
    Login user ke HAVN dengan error handling lengkap
    
    Returns:
        Redirect URL atau None jika gagal
    """
    try:
        redirect_url = client.auth.login(email=email)
        logger.info(f"Login successful for {email}")
        return redirect_url
        
    except HAVNValidationError as e:
        logger.error(f"Validation error: {e}")
        return None
        
    except HAVNAuthError as e:
        logger.error(f"Authentication failed: {e}")
        return None
        
    except HAVNAPIError as e:
        if e.status_code == 404:
            logger.error(f"User not found: {email}")
            # Optionally: Sync user first
            # client.users.sync(email=email, name="...")
        elif e.status_code == 400:
            logger.error(f"User inactive: {email}")
        else:
            logger.error(f"API error: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
```

---

## Best Practices

### 1. Sync User Sebelum Login

Pastikan user sudah di-sync ke HAVN sebelum login:

```python
# Step 1: Sync user
client.users.sync(
    email="user@example.com",
    name="John Doe",
    google_id="google123"
)

# Step 2: Login user
redirect_url = client.auth.login(email="user@example.com")
```

### 2. Handle Rate Limiting

```python
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def login_with_retry(email: str):
    return client.auth.login(email=email)
```

### 3. Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redirect_url = client.auth.login(email="user@example.com")
logger.info(f"User logged in: {email} -> {redirect_url}")
```

### 4. Validation

```python
import re

def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Validate before calling API
if is_valid_email(email):
    redirect_url = client.auth.login(email=email)
else:
    print("Email format tidak valid")
```

---

## Security Notes

1. **HMAC Signature**: Otomatis digenerate oleh SDK
2. **API Key**: Dijaga kerahasiaannya, jangan expose di frontend
3. **Temporary Token**: Single-use, expired setelah digunakan
4. **Rate Limiting**: 20 requests per minute per SaaS company

---

## Lihat Juga

- [Transaction Webhook](TRANSACTION_WEBHOOK.md)
- [User Sync Webhook](USER_SYNC_WEBHOOK.md)
- [Voucher Webhook](VOUCHER_WEBHOOK.md)
- [Models](MODELS.md)
- [Exceptions](EXCEPTIONS.md)
