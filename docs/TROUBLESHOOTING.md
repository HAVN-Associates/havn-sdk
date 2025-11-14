# Troubleshooting Guide - HAVN SDK

Panduan ini membantu menyelesaikan masalah umum yang mungkin terjadi saat menggunakan HAVN Python SDK.

## Daftar Isi

- [Common Errors](#common-errors)
- [Authentication Issues](#authentication-issues)
- [Network Issues](#network-issues)
- [Validation Errors](#validation-errors)
- [API Errors](#api-errors)
- [Debugging Tips](#debugging-tips)

---

## Common Errors

### 1. Missing Credentials

**Error**:
```
ValueError: API key is required. Provide api_key parameter or set HAVN_API_KEY environment variable.
```

**Cause**: API key tidak disediakan

**Solution**:
```python
# Option 1: Set environment variable
import os
os.environ["HAVN_API_KEY"] = "your_api_key"
os.environ["HAVN_WEBHOOK_SECRET"] = "your_webhook_secret"

client = HAVNClient()

# Option 2: Pass explicitly
client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret"
)
```

---

### 2. Invalid Credentials

**Error**:
```
HAVNAuthError: Authentication failed
```

**Cause**: API key atau webhook secret salah

**Solution**:
1. Verify credentials di HAVN Dashboard
2. Check apakah credentials tidak expired
3. Pastikan tidak ada whitespace di environment variables:
   ```bash
   # ❌ Bad
   export HAVN_API_KEY=" your_api_key "
   
   # ✅ Good
   export HAVN_API_KEY="your_api_key"
   ```

---

### 3. Connection Error

**Error**:
```
HAVNNetworkError: Connection error
```

**Cause**: Tidak bisa connect ke HAVN API

**Solution**:
1. Check internet connection
2. Verify `base_url` configuration:
   ```python
   client = HAVNClient(
       api_key="...",
       webhook_secret="...",
       base_url="https://api.havn.com"  # Verify this URL
   )
   ```
3. Check firewall/proxy settings
4. Verify HAVN API status

---

### 4. Timeout Error

**Error**:
```
HAVNNetworkError: Request timeout after 30 seconds
```

**Cause**: Request terlalu lama, tidak ada response dari API

**Solution**:
```python
# Increase timeout
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    timeout=60  # Increase to 60 seconds
)
```

---

## Authentication Issues

### Invalid HMAC Signature

**Error**:
```
HAVNAuthError: Authentication failed (401)
```

**Cause**: Webhook secret salah, signature tidak match

**Solution**:
1. Verify `webhook_secret` di HAVN Dashboard
2. Pastikan `webhook_secret` sama dengan yang di-set di dashboard
3. Jangan gunakan `api_key` sebagai `webhook_secret`

---

### API Key vs Webhook Secret

**Confusion**: Banyak yang bingung antara API key dan Webhook secret

**Clarification**:
- **API Key**: Di-set di header `X-API-Key`, untuk identifikasi aplikasi
- **Webhook Secret**: Digunakan untuk generate HMAC signature, untuk keamanan

**Both are required!**

---

## Network Issues

### Slow Network / High Latency

**Symptoms**: Request timeout, frequent connection errors

**Solution**:
```python
# Increase timeout dan retry
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    timeout=60,
    max_retries=5,
    backoff_factor=1.0
)
```

---

### Intermittent Connection

**Symptoms**: Kadang berhasil, kadang gagal

**Solution**:
```python
# Enable automatic retry
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    max_retries=5,  # Increase retries
    backoff_factor=0.5
)

# SDK akan otomatis retry pada error: 429, 500, 502, 503, 504
```

---

### Proxy / VPN Issues

**Symptoms**: Connection error meskipun internet OK

**Solution**:
```python
import requests
from havn import HAVNClient

# Configure proxy di requests session
# (SDK tidak support proxy langsung, tapi bisa di-extend)

# Atau gunakan environment variables
# export HTTP_PROXY="http://proxy.example.com:8080"
# export HTTPS_PROXY="http://proxy.example.com:8080"
```

---

## Validation Errors

### Invalid Amount

**Error**:
```
HAVNValidationError: Amount must be greater than 0
```

**Cause**: Amount <= 0 atau bukan integer

**Solution**:
```python
# ❌ Wrong
amount = 100.00  # Float, wrong!
amount = -100    # Negative, wrong!

# ✅ Correct
amount = 10000  # Integer, in cents ($100.00)
```

---

### Invalid Currency

**Error**:
```
HAVNValidationError: Unsupported currency code: XYZ
```

**Cause**: Currency code tidak didukung

**Solution**:
```python
# Check supported currencies
from havn.utils.validators import validate_currency

# Supported: USD, EUR, GBP, JPY, CNY, AUD, CAD, CHF, HKD, SGD, 
#            SEK, NOK, DKK, INR, IDR, MYR, PHP, THB, VND, KRW, 
#            TWD, BRL, MXN, ZAR, TRY, RUB

# ✅ Correct
currency = "USD"
currency = "IDR"

# ❌ Wrong
currency = "xyz"
currency = "usd"  # Must be uppercase!
```

---

### Invalid Email

**Error**:
```
HAVNValidationError: Invalid email format: invalid-email
```

**Cause**: Format email salah

**Solution**:
```python
# ✅ Correct
email = "user@example.com"

# ❌ Wrong
email = "invalid-email"
email = "user@"
email = "@example.com"
```

---

### Custom Fields Limit

**Error**:
```
HAVNValidationError: custom_fields cannot exceed 3 entries
```

**Cause**: Terlalu banyak custom fields

**Solution**:
```python
# ✅ Correct (max 3 entries)
custom_fields = {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3"
}

# ❌ Wrong (more than 3)
custom_fields = {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3",
    "key4": "value4"  # Too many!
}
```

---

## API Errors

### 400 Bad Request

**Error**:
```
HAVNAPIError (status 400): Bad request
```

**Cause**: Request payload invalid (meskipun sudah pass validation)

**Solution**:
1. Check payload structure
2. Verify required fields
3. Check field types (string, int, etc.)
4. Review API documentation

---

### 404 Not Found

**Error**:
```
HAVNAPIError (status 404): Not found
```

**Cause**: Endpoint tidak ditemukan atau resource tidak ada

**Possible Causes**:
1. **Wrong endpoint**: Check `base_url`
2. **Voucher not found**: Voucher code tidak valid
3. **Referral code not found**: Referral code tidak ada

**Solution**:
```python
# Voucher validation
try:
    client.vouchers.validate(voucher_code="VOUCHER123")
except HAVNAPIError as e:
    if e.status_code == 404:
        print("Voucher not found")
```

---

### 422 Unprocessable Entity

**Error**:
```
HAVNAPIError (status 422): Validation failed
```

**Cause**: Data valid tapi tidak memenuhi business rules

**Examples**:
- Voucher minimum purchase tidak terpenuhi
- Referral code tidak aktif
- Transaction amount terlalu kecil

**Solution**:
```python
try:
    result = client.transactions.send(amount=100, referral_code="HAVN-MJ-001")
except HAVNAPIError as e:
    if e.status_code == 422:
        print(f"Business rule violation: {e.message}")
        if e.response:
            print(f"Details: {e.response}")
```

---

### 429 Too Many Requests

**Error**:
```
HAVNAPIError (status 429): Too many requests
```

**Cause**: Rate limit exceeded

**Solution**:
1. SDK akan otomatis retry dengan exponential backoff
2. Implement rate limiting di application:
   ```python
   import time
   
   def send_with_rate_limit(client, transactions):
       for tx in transactions:
           try:
               client.transactions.send(**tx)
           except HAVNAPIError as e:
               if e.status_code == 429:
                   print("Rate limited, waiting...")
                   time.sleep(60)  # Wait 1 minute
                   continue
           time.sleep(1)  # Wait 1 second between requests
   ```

---

### 500 Internal Server Error

**Error**:
```
HAVNAPIError (status 500): Internal server error
```

**Cause**: Server error di HAVN API

**Solution**:
1. SDK akan otomatis retry (3x default)
2. Jika masih gagal, contact HAVN support
3. Check HAVN API status page

---

## Debugging Tips

### 1. Enable Debug Logging

```python
import logging

# Enable debug logging untuk requests
logging.basicConfig(level=logging.DEBUG)

# HAVN SDK akan log semua request/response
client = HAVNClient(api_key="...", webhook_secret="...")
```

---

### 2. Check Raw Response

```python
try:
    result = client.transactions.send(amount=10000, referral_code="HAVN-MJ-001")
    print("Raw response:", result.raw_response)
except HAVNAPIError as e:
    print("Error response:", e.response)
    print("Status code:", e.status_code)
```

---

### 3. Validate Input Sebelum Request

```python
from havn.utils.validators import (
    validate_amount,
    validate_currency,
    validate_email
)

# Validate sebelum request
try:
    validate_amount(10000)
    validate_currency("USD")
    validate_email("user@example.com")
    
    # Safe to send request
    result = client.transactions.send(...)
except ValueError as e:
    print(f"Validation error: {e}")
    # Fix input before retrying
```

---

### 4. Test Mode untuk Debugging

```python
# Gunakan test mode untuk debug tanpa save data
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    test_mode=True  # Dry-run mode
)

# Request akan diproses tapi tidak save data
result = client.transactions.send(...)
print("Test mode response:", result)
```

---

### 5. Check Configuration

```python
client = HAVNClient(api_key="...", webhook_secret="...")

# Print configuration
print(f"Base URL: {client.base_url}")
print(f"Timeout: {client.timeout}")
print(f"Max Retries: {client.max_retries}")
print(f"Test Mode: {client.test_mode}")
print(f"API Key: {client.api_key[:10]}...")  # Partial key for security
```

---

### 6. Network Debugging

```python
import requests

# Enable requests debug logging
import logging
logging.basicConfig()
logging.getLogger("requests.packages.urllib3").setLevel(logging.DEBUG)

# Now all HTTP requests will be logged
client = HAVNClient(api_key="...", webhook_secret="...")
```

---

## Common Scenarios

### Scenario 1: Voucher Validation Always Fails

**Problem**: Voucher validation selalu return 404

**Debugging**:
```python
# Check voucher code format
voucher_code = "VOUCHER123"
print(f"Voucher code: '{voucher_code}'")
print(f"Length: {len(voucher_code)}")
print(f"Has spaces: {' ' in voucher_code}")

# Try without amount
try:
    client.vouchers.validate(voucher_code=voucher_code)
    print("Voucher exists (without amount check)")
except HAVNAPIError as e:
    print(f"Error: {e.status_code} - {e.message}")
```

---

### Scenario 2: Commission Not Distributed

**Problem**: Transaction berhasil tapi tidak ada commission

**Debugging**:
```python
result = client.transactions.send(
    amount=10000,
    referral_code="HAVN-MJ-001"
)

print(f"Commissions: {len(result.commissions)}")
if len(result.commissions) == 0:
    # Check referral code
    print("⚠️ No commissions - check referral code validity")
    print(f"Referral code used: HAVN-MJ-001")
```

---

### Scenario 3: User Sync Tidak Membuat Associate

**Problem**: User sync berhasil tapi associate tidak dibuat

**Debugging**:
```python
result = client.users.sync(
    email="user@example.com",
    name="John Doe",
    create_associate=True
)

print(f"User created: {result.user_created}")
print(f"Associate created: {result.associate_created}")

if not result.associate_created:
    print("⚠️ Associate not created - possible reasons:")
    print("  - Associate already exists")
    print("  - Upline code invalid")
    print("  - Permission issue")
```

---

## Getting Help

Jika masalah masih berlanjut:

1. **Check Documentation**: 
   - [API Reference](API_REFERENCE.md)
   - [Examples](EXAMPLES.md)
   - [Configuration Guide](CONFIGURATION.md)

2. **Check Error Details**:
   ```python
   try:
       result = client.transactions.send(...)
   except Exception as e:
       print(f"Error type: {type(e).__name__}")
       print(f"Error message: {str(e)}")
       if hasattr(e, 'status_code'):
           print(f"Status code: {e.status_code}")
       if hasattr(e, 'response'):
           print(f"Response: {e.response}")
   ```

3. **Contact Support**:
   - Email: bagus@intelove.com
   - Issues: https://github.com/havn/havn-python-sdk/issues

---

## Next Steps

- Baca [Concepts Guide](CONCEPTS.md) untuk memahami dasar SDK
- Lihat [Examples](EXAMPLES.md) untuk contoh penggunaan
- Check [API Reference](API_REFERENCE.md) untuk dokumentasi lengkap

