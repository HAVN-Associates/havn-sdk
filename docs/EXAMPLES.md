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
    customer_id="CUST-123",
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
    is_recurring=True,
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

### 4. User Sync dengan Custom Referral Code

```python
# User sync dengan custom referral code
result = client.users.sync(
    email="vip@example.com",
    name="VIP User",
    referral_code="VIP-001",  # Custom referral code
    create_associate=True,
    avatar="https://example.com/avatar.jpg"
)

if result.associate:
    print(f"Custom referral code: {result.associate.referral_code}")
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

---

## Error Handling Examples

### 1. Comprehensive Error Handling

```python
from havn import HAVNClient
from havn.exceptions import (
    HAVNAuthError,
    HAVNValidationError,
    HAVNAPIError,
    HAVNNetworkError
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
        
except HAVNNetworkError as e:
    # Network error (timeout, connection)
    print(f"❌ Network error: {e.message}")
    if e.original_error:
        print(f"   Original: {e.original_error}")
    print("   Check your internet connection or HAVN API status")
```

### 2. Retry on Network Error

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

### 3. Validation sebelum Request

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
- Lihat [Concepts Guide](CONCEPTS.md) untuk memahami konsep dasar
- Check [Configuration Guide](CONFIGURATION.md) untuk konfigurasi lanjutan
- Review [Troubleshooting Guide](TROUBLESHOOTING.md) jika ada masalah

