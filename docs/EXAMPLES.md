# Contoh Penggunaan HAVN SDK

Dokumen ini berisi contoh-contoh lengkap penggunaan HAVN Python SDK dalam berbagai skenario.

## Daftar Isi

- [Setup Dasar](#setup-dasar)
- [Transaction Examples](#transaction-examples)
- [User Sync Examples](#user-sync-examples)
- [Voucher Validation Examples](#voucher-validation-examples)
- [Error Handling Examples](#error-handling-examples)
- [Advanced Examples](#advanced-examples)

---

## Setup Dasar

### Basic Initialization

```python
from havn import HAVNClient

# Initialize dengan explicit credentials
client = HAVNClient(
    api_key="your_api_key_here",
    webhook_secret="your_webhook_secret_here",
    base_url="https://api.havn.com"
)
```

### Environment Variables

```python
# Set environment variables
# export HAVN_API_KEY="your_api_key"
# export HAVN_WEBHOOK_SECRET="your_webhook_secret"

from havn import HAVNClient

# Initialize dari environment
client = HAVNClient()
```

### Context Manager

```python
# Gunakan context manager untuk auto-close session
with HAVNClient(api_key="...", webhook_secret="...") as client:
    result = client.transactions.send(amount=10000, referral_code="HAVN-MJ-001")
    print(result.transaction.transaction_id)
# Session ditutup otomatis
```

---

## Transaction Examples

### 1. Simple Transaction

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# Transaction sederhana
result = client.transactions.send(
    amount=10000,  # $100.00 in cents
    referral_code="HAVN-MJ-001",
    currency="USD"
)

print(f"Transaction ID: {result.transaction.transaction_id}")
print(f"Status: {result.transaction.status}")
print(f"Commissions: {len(result.commissions)} levels")

# Access commission details
for commission in result.commissions:
    print(f"Level {commission.level}: ${commission.amount / 100:.2f} ({commission.percentage}%)")
```

### 2. Transaction dengan Voucher

```python
# Transaction dengan kode voucher
result = client.transactions.send(
    amount=8000,  # $80.00 (setelah diskon)
    subtotal_transaction=10000,  # $100.00 (sebelum diskon)
    promo_code="VOUCHER123",
    referral_code="HAVN-MJ-001",
    currency="USD",
    customer_type="NEW_CUSTOMER"
)

print(f"Subtotal: ${result.transaction.subtotal_transaction / 100:.2f}")
print(f"Discount: ${result.transaction.subtotal_discount / 100:.2f}")
print(f"Final Amount: ${result.transaction.amount / 100:.2f}")
```

### 3. Transaction dengan Custom Fields

```python
# Transaction dengan custom metadata
result = client.transactions.send(
    amount=15000,
    referral_code="HAVN-MJ-001",
    currency="USD",
    custom_fields={
        "order_id": "ORD-12345",
        "payment_method": "credit_card",
        "customer_segment": "premium"
    },
    invoice_id="INV-2024-001",
    customer_email="customer@example.com"
)

print(f"Invoice ID: {result.transaction.transaction_id}")
```

### 4. Recurring Transaction

```python
# Transaction recurring (subscription)
result = client.transactions.send(
    amount=5000,  # $50.00 monthly
    referral_code="HAVN-MJ-001",
    currency="USD",
    customer_type="RECURRING",
    description="Monthly subscription"
)

print(f"Recurring transaction: {result.transaction.transaction_id}")
```

### 5. Transaction dengan Payment Gateway

```python
# Transaction dengan payment gateway info
result = client.transactions.send(
    amount=20000,
    referral_code="HAVN-MJ-001",
    currency="USD",
    payment_gateway_transaction_id="PGW-123456",
    transaction_type="sale"
)

print(f"Payment Gateway TX: {result.transaction.transaction_id}")
```

---

## User Sync Examples

### 1. Basic User Sync

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# Sync user dari Google OAuth
result = client.users.sync(
    email="user@example.com",
    name="John Doe",
    google_id="google_oauth_id_123",
    picture="https://example.com/photo.jpg",
    create_associate=True
)

print(f"User created: {result.user_created}")
print(f"Associate created: {result.associate_created}")
print(f"User ID: {result.user.id}")
print(f"User email: {result.user.email}")
```

### 2. User Sync dengan Upline

```python
# Sync user dengan upline associate
result = client.users.sync(
    email="newuser@example.com",
    name="Jane Smith",
    google_id="google_oauth_id_456",
    upline_code="HAVN-MJ-001",  # Upline referral code
    create_associate=True,
    country_code="ID"  # Indonesia
)

if result.associate:
    print(f"Associate created: {result.associate.referral_code}")
    print(f"Associate type: {result.associate.type}")
    print(f"Upline ID: {result.associate.upline_id}")
```

### 3. User Sync tanpa Associate

```python
# Sync user tanpa membuat associate
result = client.users.sync(
    email="existing@example.com",
    name="Existing User",
    create_associate=False  # Hanya update user
)

print(f"User created: {result.user_created}")  # False jika user sudah ada
print(f"Associate created: {result.associate_created}")  # False
```

### 4. User Sync dengan Referral Code (Link ke Associate yang sudah ada)

```python
# Link user ke associate yang sudah ada menggunakan referral_code
result = client.users.sync(
    email="newuser@example.com",
    name="New User",
    referral_code="HAVN-SE-002",  # Referral code dari associate yang sudah ada
    create_associate=False  # Tidak create associate baru, link ke yang sudah ada
)

if result.associate:
    print(f"User linked to associate: {result.associate.referral_code}")
```

### 4a. User Sync dengan is_owner (Set Role Owner)

```python
# Sync project owner dengan role "owner"
result = client.users.sync(
    email="owner@shopeasy.com",
    name="John Doe",
    is_owner=True,  # Set role sebagai "owner" instead of "partner"
    upline_code="HAVN-MJ-001",
    create_associate=True
)

if result.associate:
    print(f"Owner created: {result.associate.referral_code}")
    # User akan punya role "owner" di associate
```

### 5. Bulk User Sync (Basic)

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# Sync multiple users dalam satu request
result = client.users.sync_bulk(
    users=[
        {"email": "user1@example.com", "name": "John Doe"},
        {"email": "user2@example.com", "name": "Jane Smith"},
        {"email": "user3@example.com", "name": "Bob Johnson"},
    ],
    upline_code="HAVN-MJ-001",
    create_associate=True
)

# Check summary
print(f"Total: {result.summary.total}")
print(f"Success: {result.summary.success}")
print(f"Errors: {result.summary.errors}")

# Access results
for user_result in result.results:
    print(f"✅ {user_result.user.email}: Created={user_result.user_created}")
    if user_result.associate:
        print(f"   Associate: {user_result.associate.referral_code}")
```

### 6. Bulk User Sync dengan Shared Parameters

```python
# Semua users akan share upline_code dan create_associate
result = client.users.sync_bulk(
    users=[
        {"email": "user1@example.com", "name": "John Doe"},
        {"email": "user2@example.com", "name": "Jane Smith"},
        {"email": "user3@example.com", "name": "Bob Johnson"},
    ],
    upline_code="HAVN-MJ-001",  # Shared untuk semua
    create_associate=True  # Shared untuk semua
)

# Semua users akan punya upline yang sama
for user_result in result.results:
    if user_result.associate:
        print(f"{user_result.user.email} -> Upline: HAVN-MJ-001")
```

### 7. Bulk User Sync dengan Per-User Override

```python
# Shared upline_code, tapi user2 punya upline_code sendiri
result = client.users.sync_bulk(
    users=[
        {"email": "user1@example.com", "name": "John Doe"},
        {"email": "user2@example.com", "name": "Jane Smith", "upline_code": "HAVN-OTHER-001"},
        {"email": "user3@example.com", "name": "Bob Johnson"},
    ],
    upline_code="HAVN-MJ-001",  # Default untuk user1 dan user3
    create_associate=True
)

# user1 dan user3 akan punya upline HAVN-MJ-001
# user2 akan punya upline HAVN-OTHER-001
```

### 8. Bulk User Sync untuk Link ke Associate yang sudah ada

```python
# Link semua users ke associate yang sama menggunakan referral_code
result = client.users.sync_bulk(
    users=[
        {"email": "user4@example.com", "name": "Alice Brown"},
        {"email": "user5@example.com", "name": "Charlie Wilson"},
        {"email": "user6@example.com", "name": "David Lee"},
    ],
    referral_code="HAVN-SE-002"  # Dari associate yang sudah ada
)

# Semua users akan di-link ke associate dengan referral_code ini
for user_result in result.results:
    if user_result.associate:
        print(f"{user_result.user.email} -> {user_result.associate.referral_code}")
        # Semua akan punya referral_code yang sama: HAVN-SE-002
```

### 9. Batch Processing dengan Referral Code

```python
# Batch pertama - create associates baru
batch1_result = client.users.sync_bulk(
    users=[
        {"email": "user1@example.com", "name": "John Doe"},
        {"email": "user2@example.com", "name": "Jane Smith"},
    ],
    upline_code="HAVN-MJ-001"
)

# Get referral_code dari user pertama untuk batch berikutnya
referral_code = batch1_result.referral_code  # "HAVN-SE-002"
print(f"Batch 1 referral_code: {referral_code}")

# Batch kedua - link ke associate dari batch pertama
batch2_result = client.users.sync_bulk(
    users=[
        {"email": "user3@example.com", "name": "Bob Johnson"},
        {"email": "user4@example.com", "name": "Alice Brown"},
    ],
    referral_code=referral_code  # Semua di-link ke associate yang sama dari batch1
)

print(f"Batch 2: {batch2_result.summary.success} users linked to {referral_code}")
```

### 10. Bulk User Sync dengan Error Handling

```python
from havn import HAVNClient
from havn.exceptions import HAVNValidationError, HAVNAPIError

client = HAVNClient(api_key="...", webhook_secret="...")

try:
    result = client.users.sync_bulk(
        users=[
            {"email": "user1@example.com", "name": "John Doe"},  # Valid
            {"email": "invalid-email", "name": "Invalid User"},  # Will fail validation
            {"email": "user3@example.com", "name": "Valid User"},  # Valid
            {"email": "", "name": "Empty Email"},  # Will fail
        ]
    )

    # Partial success - check errors
    if result.errors:
        print(f"⚠️ Errors occurred: {len(result.errors)}")
        for error in result.errors:
            print(f"   Index {error['index']}: {error['email']} - {error['error']}")

    # Process successful results
    if result.summary.success > 0:
        print(f"✅ Successfully synced {result.summary.success} users:")
        for user_result in result.results:
            print(f"   - {user_result.user.email}")

except HAVNValidationError as e:
    print(f"❌ Validation error: {e}")
    # Handle validation errors (empty users list, max size exceeded, etc.)
except HAVNAPIError as e:
    print(f"❌ API error: {e}")
    # Handle API errors
```

### 11. Bulk User Sync untuk Project Integration

```python
# Scenario: Sync semua users dalam project ke associate yang sama

# Step 1: Sync project owner (create associate baru dengan role "owner")
owner_result = client.users.sync(
    email="owner@shopeasy.com",
    name="John Doe",
    is_owner=True,  # Set role sebagai "owner"
    upline_code="HAVN-MJ-001",
    create_associate=True
)

project_referral_code = owner_result.associate.referral_code if owner_result.associate else None
print(f"Project referral_code: {project_referral_code}")

# Step 2: Sync team members ke associate yang sama (dengan role "partner")
team_members = [
    {"email": "admin@shopeasy.com", "name": "Jane Smith"},
    {"email": "manager@shopeasy.com", "name": "Bob Johnson"},
    {"email": "support@shopeasy.com", "name": "Alice Brown"},
]

if project_referral_code:
    team_result = client.users.sync_bulk(
        users=team_members,
        referral_code=project_referral_code,  # Link semua ke associate project
        is_owner=False  # Semua team members jadi "partner" (default)
    )

    print(f"Team members synced: {team_result.summary.success}")
    print(f"All members linked to: {project_referral_code}")
    # Owner punya role "owner", team members punya role "partner"
```

---

## Voucher Validation Examples

### 1. Basic Voucher Validation

```python
from havn import HAVNClient
from havn.exceptions import HAVNAPIError

client = HAVNClient(api_key="...", webhook_secret="...")

# Validate voucher code
try:
    is_valid = client.vouchers.validate(
        voucher_code="VOUCHER123",
        amount=10000,  # $100.00
        currency="USD"
    )
    print("✅ Voucher is valid!")
except HAVNAPIError as e:
    if e.status_code == 404:
        print("❌ Voucher not found")
    elif e.status_code == 400:
        print("❌ Voucher invalid (expired, used up, or inactive)")
    elif e.status_code == 422:
        print("❌ Amount does not meet voucher requirements")
    else:
        print(f"❌ Error: {e}")
```

### 2. Voucher Validation dalam Flow Checkout

```python
def validate_voucher_before_checkout(voucher_code: str, amount: int):
    """Validate voucher sebelum checkout"""
    try:
        client.vouchers.validate(
            voucher_code=voucher_code,
            amount=amount,
            currency="USD"
        )
        return True, "Voucher valid"
    except HAVNAPIError as e:
        if e.status_code == 404:
            return False, "Voucher tidak ditemukan"
        elif e.status_code == 400:
            return False, "Voucher sudah tidak aktif"
        elif e.status_code == 422:
            return False, "Minimum purchase tidak terpenuhi"
        else:
            return False, f"Error: {e.message}"

# Usage
valid, message = validate_voucher_before_checkout("VOUCHER123", 10000)
if valid:
    print(f"✅ {message}")
    # Proceed with checkout
else:
    print(f"❌ {message}")
    # Show error to user
```

### 3. Validate Voucher tanpa Amount

```python
# Validasi voucher tanpa amount (untuk info saja)
try:
    is_valid = client.vouchers.validate(voucher_code="VOUCHER123")
    print("✅ Voucher exists and is active")
except HAVNAPIError:
    print("❌ Voucher invalid")
```

### 4. Validate Voucher dengan Auto-Conversion (Currency)

Validate voucher dengan amount dalam currency berbeda dari voucher currency.

```python
from havn import HAVNClient
from havn.exceptions import HAVNAPIError

client = HAVNClient(api_key="...", webhook_secret="...")

# Validate dengan amount dalam IDR, tapi voucher currency USD
# SDK akan auto-convert amount ke voucher currency (convenience)
# Backend akan convert ulang server-side untuk security
try:
    is_valid = client.vouchers.validate(
        voucher_code="HAVN-123",
        amount=150000,  # IDR rupiah (150.000 IDR)
        currency="IDR",  # SDK converts to voucher currency (USD) for convenience
        auto_convert=True  # Default (backend tetap convert server-side)
    )
    print("✅ Voucher is valid!")
except HAVNAPIError as e:
    if e.status_code == 404:
        print("❌ Voucher not found")
    elif e.status_code == 400:
        print("❌ Voucher invalid or currency conversion failed")
    elif e.status_code == 422:
        print("❌ Amount does not meet voucher requirements")
# Note: Backend always converts server-side (security requirement)
```

### 5. Get Voucher dengan Currency Conversion

Get vouchers dengan amounts di-convert ke currency lokal untuk display.

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# Get vouchers dengan amounts dalam IDR (untuk display)
result = client.vouchers.get_all(display_currency="IDR")

for voucher in result.data:
    print(f"Code: {voucher.code}")
    print(f"Value: {voucher.value} IDR")  # Converted from USD
    print(f"Min Purchase: {voucher.min_purchase} IDR")  # Converted
    print(f"Currency: {voucher.currency}")  # "IDR"
    # Hanya HAVN vouchers yang di-convert, local vouchers keep original currency
```

### 6. Get Combined Vouchers dengan Currency Conversion

Get combined vouchers (HAVN + local) dengan HAVN vouchers di-convert ke currency lokal.

```python
def get_local_vouchers():
    return [
        {
            "code": "LOCAL123",
            "type": "DISCOUNT_PERCENTAGE",
            "value": 2000,
            "min_purchase": 5000,
            "currency": "IDR",  # Local voucher dalam IDR
            # ... other fields
        }
    ]

# Get combined dengan display currency IDR
result = client.vouchers.get_combined(
    local_vouchers_callback=get_local_vouchers,
    display_currency="IDR"  # Convert HAVN vouchers to IDR
)

for voucher in result.data:
    if voucher.is_havn_voucher:
        print(f"HAVN: {voucher.code} - {voucher.currency} IDR")  # Converted
    else:
        print(f"Local: {voucher.code} - {voucher.currency} IDR")  # Original
```

---

## Currency Conversion Examples

### Auto-Conversion (Recommended)

SDK dapat auto-convert non-USD amounts ke USD cents sebelum kirim ke HAVN.

**Security Note:** Backend selalu verify conversion dengan recalculate server-side. Amount harus match exact (no tolerance). Jika mismatch, transaction akan di-mark sebagai `FAILED`.

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# Transaction dengan IDR - SDK auto-convert ke USD cents
result = client.transactions.send(
    amount=150000,  # IDR rupiah (150.000 IDR)
    currency="IDR",  # SDK auto-convert ke USD cents
    referral_code="HAVN-MJ-001"
)

print(f"Transaction ID: {result.transaction.transaction_id}")
print(f"Amount: ${result.transaction.amount / 100:.2f}")  # USD cents
# Original amount & exchange rate tersimpan di custom_fields untuk audit
# ⚠️ Security: Backend verifies conversion dengan exact match (no tolerance)
#    Jika mismatch → transaction FAILED
```

### Manual Conversion

Gunakan helper function untuk convert manual sebelum kirim.

```python
from havn import HAVNClient
from havn.utils.currency import convert_to_usd_cents

client = HAVNClient(api_key="...", webhook_secret="...")

# Convert manual
conversion_result = convert_to_usd_cents(150000, "IDR")
usd_cents = conversion_result["amount_cents"]

print(f"Original: 150000 IDR")
print(f"Converted: {usd_cents} USD cents")
print(f"Exchange Rate: {conversion_result['exchange_rate']}")

# Kirim dengan USD
result = client.transactions.send(
    amount=usd_cents,
    currency="USD",
    referral_code="HAVN-MJ-001"
)
```

### Convert Response untuk Display

Convert response dari USD cents ke currency lokal untuk display di frontend.

```python
from havn import HAVNClient
from havn.utils.currency import convert_from_usd_cents

client = HAVNClient(api_key="...", webhook_secret="...")

result = client.transactions.send(
    amount=10000,
    currency="USD",
    referral_code="HAVN-MJ-001"
)

# Convert response untuk display
idr_result = convert_from_usd_cents(
    result.transaction.amount,  # USD cents
    "IDR"
)

print(f"Amount: {idr_result['amount_formatted']}")  # "Rp 150.000"
print(f"Original: ${result.transaction.amount / 100:.2f}")  # "$10.00"
```

### Disable Auto-Conversion

Jika ingin backend handle conversion, disable auto-conversion di SDK.

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# Kirim amount sudah dalam USD cents, tapi info currency tetap ada
result = client.transactions.send(
    amount=10000,  # Sudah dalam USD cents
    currency="IDR",  # Info saja, backend akan handle conversion
    auto_convert=False,  # Disable auto-conversion
    referral_code="HAVN-MJ-001"
)
```

### Multiple Currency Support

SDK mendukung berbagai currency dengan auto-conversion.

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# EUR
result = client.transactions.send(
    amount=8500,  # EUR cents (85.00 EUR)
    currency="EUR",
    referral_code="HAVN-MJ-001"
)

# GBP
result = client.transactions.send(
    amount=7500,  # GBP pence (75.00 GBP)
    currency="GBP",
    referral_code="HAVN-MJ-001"
)

# IDR
result = client.transactions.send(
    amount=150000,  # IDR rupiah (150.000 IDR)
    currency="IDR",
    referral_code="HAVN-MJ-001"
)
```

### Get Exchange Rate

Check exchange rate sebelum convert.

```python
from havn.utils.currency import get_exchange_rate

# Get exchange rate
rate = get_exchange_rate("IDR", "USD")  # 1 USD = X IDR
print(f"Exchange Rate: {rate}")

if rate:
    # Calculate expected conversion
    idr_amount = 150000
    usd_amount = idr_amount * rate
    print(f"{idr_amount} IDR = {usd_amount:.2f} USD")
```

### Currency Converter Configuration

Configure currency converter dengan custom settings.

```python
from havn.utils.currency import CurrencyConverter

# Custom converter dengan custom cache duration
converter = CurrencyConverter(
    exchange_rate_api_url="https://api.exchangerate-api.com/v4/latest/USD",
    cache_duration_hours=12,  # Cache untuk 12 jam
    api_timeout=10  # Timeout 10 detik
)

result = converter.convert_to_usd_cents(150000, "IDR")
print(result["amount_cents"])
```

---

## Error Handling Examples

### 1. Comprehensive Error Handling

```python
from havn import HAVNClient
from havn.exceptions import (
    HAVNAuthError,
    HAVNValidationError,
    HAVNAPIError,
    HAVNNetworkError,
    HAVNRateLimitError,
)

client = HAVNClient(api_key="...", webhook_secret="...")

try:
    result = client.transactions.send(
        amount=10000,
        referral_code="HAVN-MJ-001"
    )
    print(f"✅ Success: {result.transaction.transaction_id}")

except HAVNValidationError as e:
    # Input validation error (sebelum request ke API)
    print(f"❌ Validation error: {e.message}")
    if e.errors:
        for field, error in e.errors.items():
            print(f"  - {field}: {error}")

except HAVNAuthError as e:
    # Authentication error (401)
    print(f"❌ Authentication failed: {e.message}")
    print("   Check your API key and webhook secret")

except HAVNAPIError as e:
    # API error (4xx, 5xx)
    print(f"❌ API error ({e.status_code}): {e.message}")
    if e.response:
        print(f"   Details: {e.response}")

except HAVNRateLimitError as e:
    # Rate limit exceeded (429)
    print(f"❌ Rate limit exceeded. Retry after {e.retry_after} seconds")
    print(f"   Limit: {e.limit}, Remaining: {e.remaining}")
    if e.retry_after:
        time.sleep(e.retry_after)
        # Retry request here
except HAVNNetworkError as e:
    # Network error (timeout, connection)
    print(f"❌ Network error: {e.message}")
    if e.original_error:
        print(f"   Original: {e.original_error}")
    print("   Check your internet connection or HAVN API status")
```

### 2. Rate Limit Handling

```python
import time
from havn.exceptions import HAVNRateLimitError

def send_transaction_with_rate_limit_handling(client, max_retries=3):
    """Send transaction dengan rate limit handling"""
    for attempt in range(max_retries):
        try:
            result = client.transactions.send(
                amount=10000,
                referral_code="HAVN-MJ-001"
            )
            return result
        except HAVNRateLimitError as e:
            # Rate limit exceeded dengan detailed info
            wait_time = e.retry_after or (2 ** attempt)  # Use retry_after or exponential backoff
            print(f"⚠️ Rate limit exceeded. Retry after {wait_time}s... ({attempt + 1}/{max_retries})")
            print(f"   Limit: {e.limit}, Remaining: {e.remaining}")
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                raise  # Re-raise on last attempt
```

### 3. Retry on Network Error

```python
import time
from havn.exceptions import HAVNNetworkError

def send_transaction_with_retry(client, max_retries=3):
    """Send transaction dengan manual retry"""
    for attempt in range(max_retries):
        try:
            result = client.transactions.send(
                amount=10000,
                referral_code="HAVN-MJ-001"
            )
            return result
        except HAVNNetworkError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"⚠️ Network error, retrying in {wait_time}s... ({attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise  # Re-raise on last attempt
```

### 4. Validation sebelum Request

```python
from havn.utils.validators import validate_amount, validate_currency

# Validate input sebelum request
def safe_send_transaction(client, amount: int, currency: str = "USD"):
    """Send transaction dengan pre-validation"""
    try:
        validate_amount(amount)
        validate_currency(currency)
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        return None

    try:
        return client.transactions.send(amount=amount, currency=currency)
    except HAVNAPIError as e:
        print(f"❌ API error: {e}")
        return None

# Usage
result = safe_send_transaction(client, amount=10000, currency="USD")
if result:
    print(f"✅ Transaction ID: {result.transaction.transaction_id}")
```

---

## Advanced Examples

### 1. Batch Transaction Processing

```python
def process_batch_transactions(client, transactions: list):
    """Process multiple transactions dengan error handling"""
    results = []
    errors = []

    for tx in transactions:
        try:
            result = client.transactions.send(**tx)
            results.append({
                "success": True,
                "transaction_id": result.transaction.transaction_id,
                "amount": result.transaction.amount
            })
        except Exception as e:
            errors.append({
                "error": str(e),
                "transaction": tx
            })

    return {"results": results, "errors": errors}

# Usage
transactions = [
    {"amount": 10000, "referral_code": "HAVN-MJ-001"},
    {"amount": 20000, "referral_code": "HAVN-MJ-002"},
    {"amount": 15000, "referral_code": "HAVN-MJ-003"},
]

batch_result = process_batch_transactions(client, transactions)
print(f"✅ Success: {len(batch_result['results'])}")
print(f"❌ Errors: {len(batch_result['errors'])}")
```

### 2. Transaction dengan Conditional Logic

```python
def send_transaction_with_voucher(client, amount: int, referral_code: str, voucher_code: str = None):
    """Send transaction dengan optional voucher"""

    # Validate voucher jika ada
    if voucher_code:
        try:
            client.vouchers.validate(voucher_code=voucher_code, amount=amount)
            print(f"✅ Voucher {voucher_code} is valid")
        except HAVNAPIError:
            print(f"❌ Voucher {voucher_code} is invalid, proceeding without voucher")
            voucher_code = None

    # Send transaction
    if voucher_code:
        # Calculate discount (assuming 20% discount for example)
        discounted_amount = int(amount * 0.8)
        return client.transactions.send(
            amount=discounted_amount,
            subtotal_transaction=amount,
            promo_code=voucher_code,
            referral_code=referral_code
        )
    else:
        return client.transactions.send(
            amount=amount,
            referral_code=referral_code
        )

# Usage
result = send_transaction_with_voucher(
    client=client,
    amount=10000,
    referral_code="HAVN-MJ-001",
    voucher_code="VOUCHER123"
)
```

### 3. User Sync dengan Transaction

```python
def complete_user_signup_flow(client, user_data: dict, first_transaction: dict):
    """Complete user signup dan first transaction"""

    # Step 1: Sync user
    try:
        user_result = client.users.sync(**user_data)
        print(f"✅ User synced: {user_result.user.email}")

        # Step 2: Send first transaction jika associate dibuat
        if user_result.associate_created and user_result.associate:
            tx_result = client.transactions.send(**first_transaction)
            print(f"✅ First transaction: {tx_result.transaction.transaction_id}")
            return {
                "user": user_result.user,
                "associate": user_result.associate,
                "transaction": tx_result.transaction
            }
        else:
            print("⚠️ Associate not created, skipping transaction")
            return {
                "user": user_result.user,
                "associate": None,
                "transaction": None
            }

    except Exception as e:
        print(f"❌ Error in signup flow: {e}")
        raise

# Usage
user_data = {
    "email": "newuser@example.com",
    "name": "New User",
    "google_id": "google123",
    "create_associate": True
}

first_transaction = {
    "amount": 5000,
    "referral_code": "HAVN-MJ-001",
    "customer_type": "NEW_CUSTOMER"
}

result = complete_user_signup_flow(client, user_data, first_transaction)
```

### 4. Test Mode untuk Development

```python
# Development: Gunakan test mode
dev_client = HAVNClient(
    api_key="dev_api_key",
    webhook_secret="dev_webhook_secret",
    test_mode=True  # Dry-run mode
)

# Production: Normal mode
prod_client = HAVNClient(
    api_key=os.getenv("HAVN_API_KEY"),
    webhook_secret=os.getenv("HAVN_WEBHOOK_SECRET"),
    test_mode=False
)

# Switch berdasarkan environment
import os
is_production = os.getenv("ENVIRONMENT") == "production"
client = prod_client if is_production else dev_client
```

### 5. Custom Configuration

```python
# Custom timeout dan retry untuk slow network
slow_client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    timeout=60,  # 60 seconds timeout
    max_retries=5,  # 5 retry attempts
    backoff_factor=1.0  # 1 second backoff
)

# Fast client untuk high-frequency requests
fast_client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    timeout=10,  # 10 seconds timeout
    max_retries=2,  # 2 retry attempts
    backoff_factor=0.3  # 0.3 second backoff
)
```

---

## Next Steps

- Baca [API Reference](API_REFERENCE.md) untuk dokumentasi lengkap semua methods
- Lihat [API Reference](API_REFERENCE.md) untuk dokumentasi lengkap
- Lihat [Integration Flow](INTEGRATION_FLOW.md) untuk panduan integrasi
- Review [README](../README.md) untuk quick start dan common issues
