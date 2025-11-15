# API Reference

Dokumentasi lengkap API Reference untuk HAVN Python SDK.

## Daftar Isi

- [Client](#client)
- [Webhooks](#webhooks)
  - [TransactionWebhook](#transactionwebhook)
  - [UserSyncWebhook](#usersyncwebhook)
  - [VoucherWebhook](#voucherwebhook)
- [Models](#models)
  - [Transaction Models](#transaction-models)
  - [User Sync Models](#user-sync-models)
  - [Voucher Models](#voucher-models)
- [Exceptions](#exceptions)
- [Utilities](#utilities)

---

## Client

### HAVNClient

Main client class untuk berinteraksi dengan HAVN API.

#### Constructor

```python
class HAVNClient(
    api_key: Optional[str] = None,
    webhook_secret: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
    backoff_factor: Optional[float] = None,
    test_mode: bool = False,
)
```

#### Parameters

| Parameter        | Type    | Required | Default                | Description                                                                                         |
| ---------------- | ------- | -------- | ---------------------- | --------------------------------------------------------------------------------------------------- |
| `api_key`        | `str`   | No\*     | -                      | API key untuk authentication. Dibaca dari `HAVN_API_KEY` env var jika tidak disediakan.             |
| `webhook_secret` | `str`   | No\*     | -                      | Webhook secret untuk HMAC signing. Dibaca dari `HAVN_WEBHOOK_SECRET` env var jika tidak disediakan. |
| `base_url`       | `str`   | No       | `https://api.havn.com` | Base URL untuk HAVN API                                                                             |
| `timeout`        | `int`   | No       | `30`                   | Request timeout dalam seconds                                                                       |
| `max_retries`    | `int`   | No       | `3`                    | Maximum retry attempts                                                                              |
| `backoff_factor` | `float` | No       | `0.5`                  | Exponential backoff multiplier                                                                      |
| `test_mode`      | `bool`  | No       | `False`                | Enable dry-run mode (tidak save data)                                                               |

\* **Required**: `api_key` dan `webhook_secret` harus disediakan (baik via parameter atau environment variables)

#### Properties

| Property         | Type                 | Description                        |
| ---------------- | -------------------- | ---------------------------------- |
| `transactions`   | `TransactionWebhook` | Transaction webhook handler        |
| `users`          | `UserSyncWebhook`    | User sync webhook handler          |
| `vouchers`       | `VoucherWebhook`     | Voucher validation webhook handler |
| `api_key`        | `str`                | API key yang digunakan             |
| `webhook_secret` | `str`                | Webhook secret yang digunakan      |
| `base_url`       | `str`                | Base URL untuk API                 |
| `timeout`        | `int`                | Request timeout                    |
| `max_retries`    | `int`                | Maximum retry attempts             |
| `backoff_factor` | `float`              | Backoff factor                     |
| `test_mode`      | `bool`               | Test mode status                   |

#### Methods

##### `close()`

Close HTTP session.

```python
client.close()
```

**Returns:** `None`

**Example:**

```python
client = HAVNClient(api_key="...", webhook_secret="...")
result = client.transactions.send(...)
client.close()  # Close session manually
```

##### Context Manager Support

Client mendukung context manager untuk auto-close session:

```python
with HAVNClient(api_key="...", webhook_secret="...") as client:
    result = client.transactions.send(...)
# Session ditutup otomatis
```

#### Examples

**Basic Initialization:**

```python
from havn import HAVNClient

# Initialize dengan explicit parameters
client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret"
)
```

**Using Environment Variables:**

```python
# Set environment variables:
# export HAVN_API_KEY="your_api_key"
# export HAVN_WEBHOOK_SECRET="your_webhook_secret"

from havn import HAVNClient

# Initialize dari environment
client = HAVNClient()
```

**Custom Configuration:**

```python
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    base_url="https://staging-api.havn.com",
    timeout=60,
    max_retries=5,
    backoff_factor=1.0,
    test_mode=True
)
```

**With Context Manager:**

```python
with HAVNClient(api_key="...", webhook_secret="...") as client:
    result = client.transactions.send(amount=10000, referral_code="HAVN-MJ-001")
    print(result.transaction.transaction_id)
```

---

## Webhooks

### TransactionWebhook

Handler untuk transaction webhooks. Diakses via `client.transactions`.

#### `send()`

Send transaction ke HAVN API.

```python
client.transactions.send(
    amount: int,
    referral_code: Optional[str] = None,
    promo_code: Optional[str] = None,
    currency: str = "USD",
    customer_type: str = "NEW_CUSTOMER",
    subtotal_transaction: Optional[int] = None,
    acquisition_method: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    invoice_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    customer_email: Optional[str] = None,
    transaction_type: Optional[str] = None,
    description: Optional[str] = None,
    payment_gateway_transaction_id: Optional[str] = None,
    is_recurring: Optional[bool] = None,
) -> TransactionResponse
```

#### Parameters

| Parameter                        | Type   | Required | Default          | Description                                                   |
| -------------------------------- | ------ | -------- | ---------------- | ------------------------------------------------------------- |
| `amount`                         | `int`  | ✅ Yes   | -                | Final transaction amount dalam cents                          |
| `referral_code`                  | `str`  | No       | `None`           | Associate referral code                                       |
| `promo_code`                     | `str`  | No       | `None`           | Voucher code                                                  |
| `currency`                       | `str`  | No       | `"USD"`          | Currency code (ISO 4217, 3 uppercase letters)                 |
| `customer_type`                  | `str`  | No       | `"NEW_CUSTOMER"` | `"NEW_CUSTOMER"` atau `"RECURRING"`                           |
| `subtotal_transaction`           | `int`  | No       | `None`           | Original amount sebelum discount (dalam cents)                |
| `acquisition_method`             | `str`  | No       | `None`           | `"VOUCHER"`, `"REFERRAL"`, atau `"REFERRAL_VOUCHER"`          |
| `custom_fields`                  | `dict` | No       | `None`           | Custom metadata (max 3 entries, string/number/boolean values) |
| `invoice_id`                     | `str`  | No       | `None`           | External invoice ID                                           |
| `customer_id`                    | `str`  | No       | `None`           | External customer ID                                          |
| `customer_email`                 | `str`  | No       | `None`           | Customer email                                                |
| `transaction_type`               | `str`  | No       | `None`           | Transaction type                                              |
| `description`                    | `str`  | No       | `None`           | Transaction description                                       |
| `payment_gateway_transaction_id` | `str`  | No       | `None`           | Payment gateway transaction ID                                |
| `is_recurring`                   | `bool` | No       | `None`           | Apakah transaction adalah recurring                           |

#### Returns

`TransactionResponse` - Response object dengan transaction dan commission data.

#### Raises

- `HAVNValidationError`: Jika payload validation gagal
- `HAVNAPIError`: Jika API request gagal
- `HAVNAuthError`: Jika authentication gagal
- `HAVNNetworkError`: Jika network error terjadi

#### Examples

**Simple Transaction:**

```python
result = client.transactions.send(
    amount=10000,  # $100.00 in cents
    referral_code="HAVN-MJ-001",
    currency="USD"
)

print(f"Transaction ID: {result.transaction.transaction_id}")
print(f"Amount: ${result.transaction.amount / 100:.2f}")
print(f"Commissions: {len(result.commissions)} levels")
```

**Transaction dengan Voucher:**

```python
result = client.transactions.send(
    amount=8000,  # $80.00 (after discount)
    subtotal_transaction=10000,  # $100.00 (before discount)
    promo_code="VOUCHER123",
    referral_code="HAVN-MJ-001",
    currency="USD",
    customer_type="NEW_CUSTOMER"
)

print(f"Discount: ${result.transaction.subtotal_discount / 100:.2f}")
```

**Transaction dengan Custom Fields:**

```python
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
```

**Recurring Transaction:**

```python
result = client.transactions.send(
    amount=5000,  # $50.00 monthly
    referral_code="HAVN-MJ-001",
    currency="USD",
    customer_type="RECURRING",
    is_recurring=True,
    description="Monthly subscription"
)
```

---

### UserSyncWebhook

Handler untuk user synchronization webhooks. Diakses via `client.users`.

#### `sync()`

Sync user data ke HAVN API.

```python
client.users.sync(
    email: str,
    name: str,
    google_id: Optional[str] = None,
    picture: Optional[str] = None,
    avatar: Optional[str] = None,
    upline_code: Optional[str] = None,
    referral_code: Optional[str] = None,
    country_code: Optional[str] = None,
    create_associate: bool = True,
) -> UserSyncResponse
```

#### Parameters

| Parameter          | Type   | Required | Default | Description                                            |
| ------------------ | ------ | -------- | ------- | ------------------------------------------------------ |
| `email`            | `str`  | ✅ Yes   | -       | User email                                             |
| `name`             | `str`  | ✅ Yes   | -       | User full name (max 200 characters)                    |
| `google_id`        | `str`  | No       | `None`  | Google OAuth ID                                        |
| `picture`          | `str`  | No       | `None`  | Profile picture URL                                    |
| `avatar`           | `str`  | No       | `None`  | Avatar URL                                             |
| `upline_code`      | `str`  | No       | `None`  | Upline associate referral code                         |
| `referral_code`    | `str`  | No       | `None`  | Referral code untuk associate creation                 |
| `country_code`     | `str`  | No       | `None`  | Country code (2 uppercase letters, ISO 3166-1 alpha-2) |
| `create_associate` | `bool` | No       | `True`  | Apakah akan membuat associate                          |

#### Returns

`UserSyncResponse` - Response object dengan user dan associate data.

#### Raises

- `HAVNValidationError`: Jika payload validation gagal
- `HAVNAPIError`: Jika API request gagal
- `HAVNAuthError`: Jika authentication gagal
- `HAVNNetworkError`: Jika network error terjadi

#### Examples

**Basic User Sync:**

```python
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
```

**User Sync dengan Upline:**

```python
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
    print(f"Upline ID: {result.associate.upline_id}")
```

**User Sync tanpa Associate:**

```python
result = client.users.sync(
    email="existing@example.com",
    name="Existing User",
    create_associate=False  # Hanya update user
)

print(f"User created: {result.user_created}")  # False jika sudah ada
print(f"Associate created: {result.associate_created}")  # False
```

**User Sync dengan Referral Code (Link ke Associate yang sudah ada):**

```python
# Link user ke associate yang sudah ada
result = client.users.sync(
    email="newuser@example.com",
    name="New User",
    referral_code="HAVN-SE-002",  # Referral code dari associate yang sudah ada
    create_associate=False  # Tidak create associate baru, link ke yang sudah ada
)

if result.associate:
    print(f"User linked to associate: {result.associate.referral_code}")
```

#### `sync_bulk()`

Sync multiple users ke HAVN API dalam satu request (bulk sync).

```python
client.users.sync_bulk(
    users: List[Dict[str, Any]],
    upline_code: Optional[str] = None,
    referral_code: Optional[str] = None,
    create_associate: Optional[bool] = None,
) -> BulkUserSyncResponse
```

#### Parameters

| Parameter          | Type                   | Required | Default | Description                                                                 |
| ------------------ | ---------------------- | -------- | ------- | --------------------------------------------------------------------------- |
| `users`            | `List[Dict[str, Any]]` | ✅ Yes   | -       | List user data (max 50 users per batch)                                     |
| `upline_code`      | `str`                  | No       | `None`  | Shared upline referral code untuk semua users                               |
| `referral_code`    | `str`                  | No       | `None`  | Shared referral code untuk link semua users ke associate yang sudah ada     |
| `create_associate` | `bool`                 | No       | `None`  | Shared flag untuk associate creation (jika None, akan auto-detect per user) |

**User Dictionary Fields:**

Setiap user dalam `users` list harus memiliki:

- `email` (`str`, required): User email
- `name` (`str`, required): User full name (max 200 characters)
- `google_id` (`str`, optional): Google OAuth ID
- `picture` (`str`, optional): Profile picture URL
- `avatar` (`str`, optional): Avatar URL
- `upline_code` (`str`, optional): Per-user upline code (override shared upline_code)
- `referral_code` (`str`, optional): Per-user referral code (override shared referral_code)
- `country_code` (`str`, optional): Country code (2 uppercase letters)
- `create_associate` (`bool`, optional): Per-user flag (override shared create_associate)

#### Returns

`BulkUserSyncResponse` - Response object dengan:

- `results`: List of `UserSyncResponse` untuk setiap user yang berhasil
- `summary`: Summary statistics (total, success, errors)
- `referral_code`: Referral code dari user pertama yang berhasil (untuk batch berikutnya)
- `errors`: List errors untuk users yang gagal (jika ada)

#### Raises

- `HAVNValidationError`: Jika payload validation gagal (users empty, max size exceeded, invalid fields)
- `HAVNAPIError`: Jika API request gagal
- `HAVNAuthError`: Jika authentication gagal
- `HAVNNetworkError`: Jika network error terjadi

#### Examples

**Basic Bulk Sync:**

```python
result = client.users.sync_bulk(
    users=[
        {"email": "user1@example.com", "name": "John Doe"},
        {"email": "user2@example.com", "name": "Jane Smith"},
        {"email": "user3@example.com", "name": "Bob Johnson"},
    ],
    upline_code="HAVN-MJ-001",
    create_associate=True
)

print(f"Total: {result.summary.total}")
print(f"Success: {result.summary.success}")
print(f"Errors: {result.summary.errors}")

# Access results
for user_result in result.results:
    print(f"{user_result.user.email}: {user_result.user_created}")

# Get referral_code for next batch
if result.referral_code:
    print(f"Referral code: {result.referral_code}")
```

**Bulk Sync dengan Shared Parameters:**

```python
# Semua users akan share upline_code dan create_associate
result = client.users.sync_bulk(
    users=[
        {"email": "user1@example.com", "name": "John Doe"},
        {"email": "user2@example.com", "name": "Jane Smith"},
    ],
    upline_code="HAVN-MJ-001",  # Shared untuk semua
    create_associate=True  # Shared untuk semua
)
```

**Bulk Sync dengan Per-User Override:**

```python
# Shared upline_code, tapi user2 punya upline_code sendiri
result = client.users.sync_bulk(
    users=[
        {"email": "user1@example.com", "name": "John Doe"},
        {"email": "user2@example.com", "name": "Jane Smith", "upline_code": "HAVN-OTHER-001"},
    ],
    upline_code="HAVN-MJ-001",  # Default untuk user1
    create_associate=True
)
```

**Bulk Sync untuk Link ke Associate yang sudah ada:**

```python
# Link semua users ke associate yang sama
result = client.users.sync_bulk(
    users=[
        {"email": "user4@example.com", "name": "Alice Brown"},
        {"email": "user5@example.com", "name": "Charlie Wilson"},
    ],
    referral_code="HAVN-SE-002"  # Dari batch sebelumnya
)

# Semua users akan di-link ke associate dengan referral_code ini
for user_result in result.results:
    if user_result.associate:
        print(f"{user_result.user.email} -> {user_result.associate.referral_code}")
```

**Batch Processing dengan Referral Code:**

```python
# Batch pertama - create associates baru
batch1_result = client.users.sync_bulk(
    users=[
        {"email": "user1@example.com", "name": "John Doe"},
        {"email": "user2@example.com", "name": "Jane Smith"},
    ],
    upline_code="HAVN-MJ-001"
)

referral_code = batch1_result.referral_code  # "HAVN-SE-002"

# Batch kedua - link ke associate dari batch pertama
batch2_result = client.users.sync_bulk(
    users=[
        {"email": "user3@example.com", "name": "Bob Johnson"},
        {"email": "user4@example.com", "name": "Alice Brown"},
    ],
    referral_code=referral_code  # Semua di-link ke associate yang sama
)
```

**Error Handling dalam Bulk Sync:**

```python
try:
    result = client.users.sync_bulk(
        users=[
            {"email": "user1@example.com", "name": "John Doe"},
            {"email": "invalid-email", "name": "Invalid User"},  # Will fail
            {"email": "user3@example.com", "name": "Valid User"},
        ]
    )

    # Partial success - check errors
    if result.errors:
        print(f"Errors occurred: {len(result.errors)}")
        for error in result.errors:
            print(f"Index {error['index']}: {error['error']}")

    # Process successful results
    for user_result in result.results:
        print(f"✅ {user_result.user.email}: Success")

except HAVNValidationError as e:
    print(f"Validation error: {e}")
except HAVNAPIError as e:
    print(f"API error: {e}")
```

---

### VoucherWebhook

Handler untuk voucher validation. Diakses via `client.vouchers`.

#### `validate()`

Validate voucher code.

```python
client.vouchers.validate(
    voucher_code: str,
    amount: Optional[int] = None,
    currency: Optional[str] = None,
) -> bool
```

#### Parameters

| Parameter      | Type  | Required | Default | Description                    |
| -------------- | ----- | -------- | ------- | ------------------------------ |
| `voucher_code` | `str` | ✅ Yes   | -       | Voucher code untuk di-validate |
| `amount`       | `int` | No       | `None`  | Transaction amount dalam cents |
| `currency`     | `str` | No       | `None`  | Currency code                  |

#### Returns

`bool` - `True` jika voucher valid.

#### Raises

- `HAVNValidationError`: Jika payload validation gagal
- `HAVNAPIError`: Jika voucher invalid (404, 400, 422) atau API request gagal
- `HAVNAuthError`: Jika authentication gagal
- `HAVNNetworkError`: Jika network error terjadi

#### Status Codes

- `200 OK`: Voucher valid
- `400 Bad Request`: Voucher invalid (expired, used up, or inactive)
- `404 Not Found`: Voucher tidak ditemukan
- `422 Unprocessable Entity`: Amount tidak memenuhi voucher requirements

#### Examples

**Basic Validation:**

```python
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
```

**Validation sebelum Transaction:**

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
```

---

## Models

### Transaction Models

#### TransactionPayload

Payload untuk transaction webhook.

**Attributes:**

- `amount` (`int`): Final transaction amount dalam cents
- `referral_code` (`Optional[str]`): Associate referral code
- `promo_code` (`Optional[str]`): Voucher code
- `currency` (`str`): Currency code (default: "USD")
- `customer_type` (`str`): "NEW_CUSTOMER" atau "RECURRING" (default: "NEW_CUSTOMER")
- `subtotal_transaction` (`Optional[int]`): Original amount sebelum discount
- `acquisition_method` (`Optional[str]`): "VOUCHER", "REFERRAL", atau "REFERRAL_VOUCHER"
- `custom_fields` (`Optional[Dict[str, Any]]`): Custom metadata (max 3 entries)
- `invoice_id` (`Optional[str]`): External invoice ID
- `customer_id` (`Optional[str]`): External customer ID
- `customer_email` (`Optional[str]`): Customer email
- `transaction_type` (`Optional[str]`): Transaction type
- `description` (`Optional[str]`): Transaction description
- `payment_gateway_transaction_id` (`Optional[str]`): Payment gateway transaction ID
- `is_recurring` (`Optional[bool]`): Apakah transaction adalah recurring

#### TransactionData

Transaction data dari response.

**Attributes:**

- `transaction_id` (`str`): Transaction ID
- `amount` (`int`): Transaction amount dalam cents
- `currency` (`str`): Currency code
- `status` (`str`): Transaction status
- `customer_type` (`str`): Customer type
- `acquisition_method` (`Optional[str]`): Acquisition method
- `subtotal_transaction` (`Optional[int]`): Subtotal sebelum discount
- `subtotal_discount` (`Optional[int]`): Discount amount
- `created_at` (`Optional[str]`): Created timestamp

#### CommissionData

Commission data dari response.

**Attributes:**

- `commission_id` (`str`): Commission ID
- `associate_id` (`str`): Associate ID
- `level` (`int`): Commission level
- `amount` (`int`): Commission amount dalam cents
- `percentage` (`float`): Commission percentage
- `type` (`str`): Commission type
- `direction` (`str`): Commission direction
- `status` (`str`): Commission status

#### TransactionResponse

Response dari transaction webhook.

**Attributes:**

- `success` (`bool`): Apakah request berhasil
- `message` (`str`): Response message
- `transaction` (`TransactionData`): Transaction data
- `commissions` (`List[CommissionData]`): List commission data
- `raw_response` (`Dict[str, Any]`): Raw response dictionary

**Example:**

```python
result = client.transactions.send(amount=10000, referral_code="HAVN-MJ-001")

# Access transaction data
print(f"Transaction ID: {result.transaction.transaction_id}")
print(f"Amount: ${result.transaction.amount / 100:.2f}")

# Access commissions
for commission in result.commissions:
    print(f"Level {commission.level}: ${commission.amount / 100:.2f} ({commission.percentage}%)")

# Access raw response
print(f"Raw response: {result.raw_response}")
```

---

### User Sync Models

#### UserSyncPayload

Payload untuk user sync webhook.

**Attributes:**

- `email` (`str`): User email (required)
- `name` (`str`): User full name (required, max 200 chars)
- `google_id` (`Optional[str]`): Google OAuth ID
- `picture` (`Optional[str]`): Profile picture URL
- `avatar` (`Optional[str]`): Avatar URL
- `upline_code` (`Optional[str]`): Upline associate referral code
- `referral_code` (`Optional[str]`): Referral code untuk associate creation
- `country_code` (`Optional[str]`): Country code (2 uppercase letters)
- `create_associate` (`bool`): Apakah akan membuat associate (default: True)

#### UserData

User data dari response.

**Attributes:**

- `id` (`str`): User ID
- `email` (`str`): User email
- `name` (`str`): User name
- `is_active` (`bool`): Apakah user aktif
- `google_id` (`Optional[str]`): Google OAuth ID
- `avatar` (`Optional[str]`): Avatar URL

#### AssociateData

Associate data dari response.

**Attributes:**

- `associate_id` (`str`): Associate ID
- `associate_name` (`str`): Associate name
- `referral_code` (`str`): Referral code
- `type` (`str`): Associate type
- `is_active` (`bool`): Apakah associate aktif
- `upline_id` (`Optional[str]`): Upline associate ID

#### UserSyncResponse

Response dari user sync webhook.

**Attributes:**

- `success` (`bool`): Apakah request berhasil
- `message` (`str`): Response message
- `user_created` (`bool`): Apakah user dibuat (vs updated)
- `associate_created` (`bool`): Apakah associate dibuat
- `user` (`UserData`): User data
- `associate` (`Optional[AssociateData]`): Associate data (jika dibuat)
- `raw_response` (`Dict[str, Any]`): Raw response dictionary

**Example:**

```python
result = client.users.sync(
    email="user@example.com",
    name="John Doe",
    create_associate=True
)

# Access user data
print(f"User ID: {result.user.id}")
print(f"User email: {result.user.email}")
print(f"User created: {result.user_created}")

# Access associate data
if result.associate:
    print(f"Associate ID: {result.associate.associate_id}")
    print(f"Referral code: {result.associate.referral_code}")
    print(f"Associate created: {result.associate_created}")
```

#### BulkUserSyncPayload

Payload untuk bulk user sync webhook.

**Attributes:**

- `users` (`List[Dict[str, Any]]`): List user data (required, max 50)
- `upline_code` (`Optional[str]`): Shared upline referral code
- `referral_code` (`Optional[str]`): Shared referral code untuk linking
- `create_associate` (`Optional[bool]`): Shared flag untuk associate creation

#### BulkSyncSummary

Summary statistics dari bulk sync.

**Attributes:**

- `total` (`int`): Total users dalam request
- `success` (`int`): Jumlah users yang berhasil di-sync
- `errors` (`int`): Jumlah users yang gagal di-sync

#### BulkUserSyncResponse

Response dari bulk user sync webhook.

**Attributes:**

- `success` (`bool`): Apakah request berhasil (True jika ada minimal 1 success)
- `message` (`str`): Response message
- `results` (`List[UserSyncResponse]`): List hasil sync untuk setiap user yang berhasil
- `summary` (`BulkSyncSummary`): Summary statistics
- `referral_code` (`Optional[str]`): Referral code dari user pertama yang berhasil (untuk next batch)
- `errors` (`Optional[List[Dict[str, Any]]]`): List errors untuk users yang gagal
- `raw_response` (`Dict[str, Any]`): Raw response dictionary

**Example:**

```python
result = client.users.sync_bulk(
    users=[
        {"email": "user1@example.com", "name": "John Doe"},
        {"email": "user2@example.com", "name": "Jane Smith"},
    ]
)

# Access summary
print(f"Total: {result.summary.total}")
print(f"Success: {result.summary.success}")
print(f"Errors: {result.summary.errors}")

# Access results
for user_result in result.results:
    print(f"✅ {user_result.user.email}")
    if user_result.associate:
        print(f"   Referral code: {user_result.associate.referral_code}")

# Access errors (if any)
if result.errors:
    for error in result.errors:
        print(f"❌ Index {error['index']}: {error['error']}")

# Get referral_code for next batch
if result.referral_code:
    print(f"Referral code for next batch: {result.referral_code}")
```

---

### Voucher Models

#### VoucherValidationPayload

Payload untuk voucher validation.

**Attributes:**

- `voucher_code` (`str`): Voucher code untuk di-validate (required)
- `amount` (`Optional[int]`): Transaction amount dalam cents
- `currency` (`Optional[str]`): Currency code

**Note**: Voucher validation tidak mengembalikan response body, hanya HTTP status code:

- `200 OK`: Voucher valid
- `400/404/422`: Voucher invalid

---

## Exceptions

### HAVNError

Base exception untuk semua HAVN SDK errors.

```python
class HAVNError(Exception):
    """Base exception for all HAVN SDK errors"""
    pass
```

### HAVNAPIError

Exception untuk API errors (4xx, 5xx).

```python
class HAVNAPIError(HAVNError):
    def __init__(self, message: str, status_code: int = None, response: dict = None)
```

**Attributes:**

- `message` (`str`): Error message
- `status_code` (`int`, optional): HTTP status code
- `response` (`dict`, optional): Response data

**Example:**

```python
try:
    result = client.transactions.send(...)
except HAVNAPIError as e:
    print(f"API error ({e.status_code}): {e.message}")
    if e.response:
        print(f"Details: {e.response}")
```

### HAVNAuthError

Exception untuk authentication errors (401).

```python
class HAVNAuthError(HAVNError):
    def __init__(self, message: str = "Authentication failed")
```

**Attributes:**

- `message` (`str`): Error message

**Example:**

```python
try:
    result = client.transactions.send(...)
except HAVNAuthError as e:
    print(f"Authentication failed: {e.message}")
```

### HAVNValidationError

Exception untuk validation errors (sebelum request ke API).

```python
class HAVNValidationError(HAVNError):
    def __init__(self, message: str, errors: dict = None)
```

**Attributes:**

- `message` (`str`): Error message
- `errors` (`dict`): Validation errors

**Example:**

```python
try:
    result = client.transactions.send(amount=-100)  # Invalid amount
except HAVNValidationError as e:
    print(f"Validation error: {e.message}")
    if e.errors:
        for field, error in e.errors.items():
            print(f"  {field}: {error}")
```

### HAVNNetworkError

Exception untuk network-related errors (timeout, connection).

```python
class HAVNNetworkError(HAVNError):
    def __init__(self, message: str, original_error: Exception = None)
```

**Attributes:**

- `message` (`str`): Error message
- `original_error` (`Exception`, optional): Original exception

**Example:**

```python
try:
    result = client.transactions.send(...)
except HAVNNetworkError as e:
    print(f"Network error: {e.message}")
    if e.original_error:
        print(f"Original: {e.original_error}")
```

---

## Utilities

### Validation Functions

#### `validate_amount()`

Validate transaction amount.

```python
from havn.utils.validators import validate_amount

validate_amount(10000)  # OK
validate_amount(-100)   # Raises ValueError: Amount must be greater than 0
```

**Raises:** `ValueError` jika amount invalid

---

#### `validate_email()`

Validate email format.

```python
from havn.utils.validators import validate_email

validate_email("user@example.com")  # OK
validate_email("invalid")           # Raises ValueError: Invalid email format
```

**Raises:** `ValueError` jika email format invalid

---

#### `validate_currency()`

Validate currency code.

```python
from havn.utils.validators import validate_currency

validate_currency("USD")  # OK
validate_currency("xyz")  # Raises ValueError: Unsupported currency code
```

**Raises:** `ValueError` jika currency code invalid

**Supported Currencies:** USD, EUR, GBP, JPY, CNY, AUD, CAD, CHF, HKD, SGD, SEK, NOK, DKK, INR, IDR, MYR, PHP, THB, VND, KRW, TWD, BRL, MXN, ZAR, TRY, RUB

---

#### `validate_custom_fields()`

Validate custom fields dictionary.

```python
from havn.utils.validators import validate_custom_fields

validate_custom_fields({"key": "value"})  # OK
validate_custom_fields({"k1": "v1", "k2": "v2", "k3": "v3", "k4": "v4"})  # Raises ValueError: exceeds 3 entries
```

**Raises:** `ValueError` jika custom fields invalid

---

#### `validate_referral_code()`

Validate referral code format.

```python
from havn.utils.validators import validate_referral_code

validate_referral_code("HAVN-MJ-001")  # OK
validate_referral_code("")             # Raises ValueError: Referral code cannot be empty
```

**Raises:** `ValueError` jika referral code format invalid

---

### Authentication Functions

#### `calculate_hmac_signature()`

Calculate HMAC-SHA256 signature untuk request authentication.

```python
from havn.utils.auth import calculate_hmac_signature

payload = {"amount": 10000, "referral_code": "HAVN-MJ-001"}
signature = calculate_hmac_signature(payload, webhook_secret)
```

**Note**: SDK menangani ini otomatis, Anda tidak perlu memanggil fungsi ini secara manual.

---

## Next Steps

- Baca [Quick Start Guide](QUICKSTART.md) untuk mulai menggunakan SDK
- Lihat [Examples](EXAMPLES.md) untuk contoh penggunaan lengkap
- Check [Concepts Guide](CONCEPTS.md) untuk memahami konsep dasar
- Review [Troubleshooting Guide](TROUBLESHOOTING.md) jika ada masalah
