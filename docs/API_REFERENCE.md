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
  - [Validation Functions](#validation-functions)
  - [Currency Utilities](#currency-utilities)
  - [Authentication Functions](#authentication-functions)

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
    payment_gateway_transaction_id: str,
    payment_gateway: str,
    customer_email: str,
    referral_code: str,
    promo_code: Optional[str] = None,
    currency: str = "USD",
    customer_type: Optional[str] = None,
    subtotal_transaction: Optional[int] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    invoice_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    description: Optional[str] = None,
    server_side_conversion: bool = False,
) -> TransactionResponse
```

> **Keyword-only:** Semua parameter setelah `payment_gateway_transaction_id` harus dipanggil menggunakan keyword argument agar kompatibel ketika SDK menambah parameter baru.

#### Parameters

| Parameter                        | Type   | Required | Default          | Description                                                                                                                                                                                                                                                                                                  |
| -------------------------------- | ------ | -------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `amount`                         | `int`  | ✅ Yes   | -                | Final transaction amount dalam smallest unit currency yang dikirimkan.<br>- Jika mengirim USD: isi dalam USD cents.<br>- Jika mengirim currency lain, kirim nilai mentahnya dan set `server_side_conversion=True` agar backend HAVN melakukan konversi resmi.                                         |
| `payment_gateway_transaction_id` | `str`  | ✅ Yes   | -                | Payment gateway transaction ID (required, non-empty, max 200 characters)                                                                                                                                                                                                                                     |
| `payment_gateway`                | `str`  | ✅ Yes   | -                | Payment gateway identifier/name (mis. `MIDTRANS`, `STRIPE`). Wajib diisi dan akan divalidasi terhadap konfigurasi SaaS company.                                                                                                                                                                              |
| `customer_email`                 | `str`  | ✅ Yes   | -                | Customer email (required, valid email format)                                                                                                                                                                                                                                                                |
| `referral_code`                  | `str`  | ✅ Yes   | -                | Associate referral code (wajib). HAVN menggunakan kode ini untuk identitas komisi.                                                                                                                                                                                                                            |
| `promo_code`                     | `str`  | No       | `None`           | Voucher code (HAVN atau local)                                                                                                                                                                                                                                                                               |
| `currency`                       | `str`  | No       | `"USD"`          | Currency code (ISO 4217, 3 uppercase letters)                                                                                                                                                                                                                                                                |
| `customer_type`                  | `str`  | No       | `None`           | Opsional manual override. HAVN backend otomatis menandai transaksi pertama per (SaaS company + email) sebagai `NEW_CUSTOMER`, dan transaksi berikutnya sebagai `RECURRING`. Isi hanya jika Anda butuh overriding sementara — backend tetap menjadi single source of truth.                                    |
| `subtotal_transaction`           | `int`  | No       | `None`           | Original amount sebelum discount (mengikuti aturan currency yang sama dengan `amount`)                                                                                                                                                                                                                       |
| `custom_fields`                  | `dict` | No       | `None`           | Custom metadata (maks 3 entries, string/number/boolean values)                                                                                                                                                                                                                                               |
| `invoice_id`                     | `str`  | No       | `None`           | External invoice ID (opsional, maks 100 karakter). Jika tidak ada nomor invoice, biarkan kosong agar tidak terisi dengan payment gateway transaction ID.                                                                                                                                                     |
| `transaction_type`               | `str`  | No       | `None`           | Transaction type (untuk logging)                                                                                                                                                                                                                                                                             |
| `description`                    | `str`  | No       | `None`           | Transaction description                                                                                                                                                                                                                                                                                      |
| `server_side_conversion`         | `bool` | No       | `False`          | Flag untuk meminta backend melakukan konversi currency resmi.<br>- `True`: SDK mengirim amount/currency apa adanya; backend menghitung ulang dengan kurs internal.<br>- `False`: Gunakan hanya jika amount sudah dalam USD cents dan tidak perlu konversi backend.                                         |

#### Returns

`TransactionResponse` - Response object dengan transaction dan commission data.

#### Raises

- `HAVNValidationError`: Jika payload validation gagal
- `HAVNAPIError`: Jika API request gagal atau backend verification gagal (mismatch conversion)
- `HAVNAuthError`: Jika authentication gagal
- `HAVNNetworkError`: Jika network error terjadi

#### Security Notes

**Currency Conversion (Server-Side Authority):**

- ✅ **Gunakan `server_side_conversion=True`** untuk transaksi non-USD agar backend resmi melakukan konversi berdasarkan kurs internal HAVN.
- ✅ **Exact Match Required** - Backend menghitung ulang dan akan menolak jumlah yang tidak konsisten dengan kurs terkini.
- ✅ **Audit Trail** - Amount awal dan metadata kurs disimpan oleh backend untuk kebutuhan audit/komisi.

**Important:** SDK tidak lagi melakukan auto-conversion. Selalu kirim nilai asli Anda; backend adalah satu-satunya sumber kebenaran untuk FX.

#### Examples

**Simple Transaction:**

```python
result = client.transactions.send(
    amount=10000,  # $100.00 in cents
    referral_code="HAVN-MJ-001",
    currency="USD",
    payment_gateway_transaction_id="stripe_txn_001",
    payment_gateway="STRIPE",
    customer_email="customer@example.com",
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
    payment_gateway_transaction_id="stripe_txn_002",
    payment_gateway="STRIPE",
    customer_email="customer@example.com",
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
    payment_gateway_transaction_id="stripe_txn_003",
    payment_gateway="STRIPE",
    customer_email="customer@example.com"
)
```

**Transaction dengan Server-Side Conversion (IDR):**

```python
# Kirim amount mentah dalam IDR dan biarkan backend HAVN yang mengkonversi
result = client.transactions.send(
    amount=150000,  # 150.000 IDR (smallest unit)
    currency="IDR",
    referral_code="HAVN-MJ-001",
    payment_gateway_transaction_id="stripe_111222333",
    payment_gateway="MIDTRANS",
    customer_email="customer@example.com",
    server_side_conversion=True,
)
# Backend menggunakan kurs internal resmi → memastikan komisi & audit konsisten
```

**Transaction dengan Amount Sudah USD:**

```python
# Jika payment processor Anda sudah mengekspresikan amount dalam USD cents
result = client.transactions.send(
    amount=10000,  # $100.00 USD cents
    currency="USD",
    referral_code="HAVN-MJ-001",
    payment_gateway_transaction_id="stripe_444555666",
    payment_gateway="STRIPE",
    customer_email="customer@example.com",
    server_side_conversion=False,  # default
)
```

**Recurring Transaction:**

```python
result = client.transactions.send(
    amount=5000,  # $50.00 monthly
    referral_code="HAVN-MJ-001",
    currency="USD",
    payment_gateway_transaction_id="stripe_sub_001",
    payment_gateway="STRIPE",
    customer_email="customer@example.com",
    description="Monthly subscription",
    customer_type="RECURRING",  # Optional override; HAVN auto-detects based on history
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
| `is_owner`         | `bool` | No       | `False` | Set role sebagai "owner" instead of "partner"          |

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

**User Sync dengan is_owner (Set Role Owner):**

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
| `is_owner`         | `bool`                 | No       | `None`  | Shared flag untuk set role sebagai "owner" (default: False = "partner")     |

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
- `is_owner` (`bool`, optional): Per-user flag untuk set role sebagai "owner" (override shared is_owner)

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

**Bulk Sync dengan is_owner (Mix Owner dan Partner):**

```python
# Owner dengan role "owner", lainnya "partner"
result = client.users.sync_bulk(
    users=[
        {"email": "owner@shopeasy.com", "name": "John Doe", "is_owner": True},
        {"email": "admin@shopeasy.com", "name": "Jane Smith"},  # Default: partner
        {"email": "manager@shopeasy.com", "name": "Bob Johnson"},
    ],
    upline_code="HAVN-MJ-001"
)

# Owner akan punya role "owner", lainnya "partner"
for user_result in result.results:
    print(f"{user_result.user.email}: {user_result.associate.referral_code}")
```

**Bulk Sync dengan Shared is_owner (All Owners):**

```python
# Semua users jadi owner
result = client.users.sync_bulk(
    users=[
        {"email": "user1@shopeasy.com", "name": "User 1"},
        {"email": "user2@shopeasy.com", "name": "User 2"},
    ],
    is_owner=True  # Shared: semua jadi owner
)

# Semua users akan punya role "owner"
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

Validate voucher code dengan optional currency conversion.

```python
client.vouchers.validate(
    voucher_code: str,
    amount: Optional[int] = None,
    currency: Optional[str] = None,
) -> bool
```

#### Parameters

| Parameter      | Type   | Required | Default | Description                                                                                                                                                                                                           |
| -------------- | ------ | -------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `voucher_code` | `str`  | ✅ Yes   | -       | Voucher code untuk di-validate                                                                                                                                                                                        |
| `amount`       | `int`  | No       | `None`  | Transaction amount dalam smallest unit currency yang sama dengan parameter `currency`. Backend HAVN akan melakukan konversi resmi terhadap currency voucher secara otomatis.                                         |
| `currency`     | `str`  | No       | `None`  | Currency asal dari amount (contoh: `"IDR"`, `"EUR"`). Jika tidak diisi, backend menganggap amount sudah berada pada currency voucher.                                                                              |

#### Returns

`bool` - `True` jika voucher valid.

#### Raises

- `HAVNValidationError`: Jika payload validation gagal
- `HAVNAPIError`: Jika voucher invalid (404, 400, 422) atau API request gagal atau currency conversion failed
- `HAVNAuthError`: Jika authentication gagal
- `HAVNNetworkError`: Jika network error terjadi

#### Security Notes

**Currency Conversion (Server-Side Only):**

- ✅ **Backend Always Converts** - Backend selalu melakukan conversion server-side (security requirement)
- ✅ **No Client Trust** - Backend tidak trust client conversion untuk security
- ✅ **Exact Match** - Amount harus match voucher currency setelah backend conversion
- ✅ **Conversion via USD** - Backend convert via USD: `source_currency -> USD -> voucher_currency`

**Important:** Tidak ada konversi di sisi SDK. Selalu kirim amount/currency asli Anda; backend melakukan konversi dan validasi penuh.

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

**Validation dengan Amount Non-USD (Backend Convert):**

```python
# Kirim nilai mentah IDR; backend HAVN mengkonversi ke currency voucher
is_valid = client.vouchers.validate(
    voucher_code="HAVN-123",
    amount=150000,  # Rp 150.000
    currency="IDR",
)
```

**Validation dengan Amount Sudah Sesuai Currency Voucher:**

```python
is_valid = client.vouchers.validate(
    voucher_code="HAVN-123",
    amount=10000,  # USD cents
    currency="USD",
)
```

#### `get_all()`

Get semua vouchers untuk SaaS company dengan pagination, filtering, dan search.

```python
def get_all(
    self,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    active: Optional[bool] = None,
    type: Optional[str] = None,
    client_type: Optional[str] = None,
    currency: Optional[str] = None,
    search: Optional[str] = None,
    start_date_from: Optional[str] = None,
    start_date_to: Optional[str] = None,
    end_date_from: Optional[str] = None,
    end_date_to: Optional[str] = None,
    created_from: Optional[str] = None,
    created_to: Optional[str] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    min_purchase_from: Optional[int] = None,
    min_purchase_to: Optional[int] = None,
    usage_limit_from: Optional[int] = None,
    usage_limit_to: Optional[int] = None,
    is_valid: Optional[bool] = None,
    is_expired: Optional[bool] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    display_currency: Optional[str] = None,
) -> VoucherListResponse
```

**Important:** Method ini selalu fetch fresh data dari HAVN backend. No client-side caching. Single source of truth adalah backend.

##### Parameters

| Parameter           | Type   | Required | Default | Description                                                                                                                                                                                                                                                                       |
| ------------------- | ------ | -------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `page`              | `int`  | No       | `1`     | Page number                                                                                                                                                                                                                                                                       |
| `per_page`          | `int`  | No       | `10`    | Items per page (max: 100)                                                                                                                                                                                                                                                         |
| `active`            | `bool` | No       | `None`  | Filter by active status                                                                                                                                                                                                                                                           |
| `type`              | `str`  | No       | `None`  | Voucher type (DISCOUNT_PERCENTAGE, DISCOUNT_FIXED)                                                                                                                                                                                                                                |
| `client_type`       | `str`  | No       | `None`  | Client type (NEW_CUSTOMER, RECURRING)                                                                                                                                                                                                                                             |
| `currency`          | `str`  | No       | `None`  | Currency code (USD, IDR, etc.)                                                                                                                                                                                                                                                    |
| `search`            | `str`  | No       | `None`  | Search dalam voucher code dan description                                                                                                                                                                                                                                         |
| `start_date_from`   | `str`  | No       | `None`  | Filter start_date >= (YYYY-MM-DD)                                                                                                                                                                                                                                                 |
| `start_date_to`     | `str`  | No       | `None`  | Filter start_date <= (YYYY-MM-DD)                                                                                                                                                                                                                                                 |
| `end_date_from`     | `str`  | No       | `None`  | Filter end_date >= (YYYY-MM-DD)                                                                                                                                                                                                                                                   |
| `end_date_to`       | `str`  | No       | `None`  | Filter end_date <= (YYYY-MM-DD)                                                                                                                                                                                                                                                   |
| `created_from`      | `str`  | No       | `None`  | Filter created_date >= (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)                                                                                                                                                                                                                        |
| `created_to`        | `str`  | No       | `None`  | Filter created_date <= (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)                                                                                                                                                                                                                        |
| `min_value`         | `int`  | No       | `None`  | Filter value >= (cents/basis points)                                                                                                                                                                                                                                              |
| `max_value`         | `int`  | No       | `None`  | Filter value <= (cents/basis points)                                                                                                                                                                                                                                              |
| `min_purchase_from` | `int`  | No       | `None`  | Filter min_purchase >= (cents)                                                                                                                                                                                                                                                    |
| `min_purchase_to`   | `int`  | No       | `None`  | Filter min_purchase <= (cents)                                                                                                                                                                                                                                                    |
| `usage_limit_from`  | `int`  | No       | `None`  | Filter usage_limit >=                                                                                                                                                                                                                                                             |
| `usage_limit_to`    | `int`  | No       | `None`  | Filter usage_limit <=                                                                                                                                                                                                                                                             |
| `is_valid`          | `bool` | No       | `None`  | Filter by validity (checks active, dates, usage)                                                                                                                                                                                                                                  |
| `is_expired`        | `bool` | No       | `None`  | Filter by expired status                                                                                                                                                                                                                                                          |
| `sort_by`           | `str`  | No       | `None`  | Sort field (code, type, value, start_date, end_date, created_date, current_usage)                                                                                                                                                                                                 |
| `sort_order`        | `str`  | No       | `desc`  | Sort direction (asc, desc)                                                                                                                                                                                                                                                        |
| `display_currency`  | `str`  | No       | `None`  | Target currency untuk display.<br>- Backend HAVN mengisi `VoucherData.display_currency` saat mengkonversi HAVN voucher amounts ke currency ini (sementara `currency` tetap menjadi audit currency, umumnya USD).<br>- Local vouchers tidak terpengaruh dan mempertahankan currency masing-masing. |

##### Returns

`VoucherListResponse` - Response dengan paginated voucher data.

##### Raises

- `HAVNValidationError`: Jika filters validation gagal
- `HAVNAPIError`: Jika API request gagal

##### Examples

**Get All Active Vouchers:**

```python
result = client.vouchers.get_all(active=True, page=1, per_page=20)
print(f"Total: {result.pagination.total}")
for voucher in result.data:
    print(f"{voucher.code}: {voucher.is_valid}")
```

**Search dan Filter:**

```python
result = client.vouchers.get_all(
    search="DISCOUNT",
    type="DISCOUNT_PERCENTAGE",
    is_valid=True,
    sort_by="created_date",
    sort_order="desc"
)
```

**Filter by Date Range:**

```python
result = client.vouchers.get_all(
    start_date_from="2024-01-01",
    end_date_to="2024-12-31",
    active=True
)
```

**Get Vouchers dengan Currency Conversion:**

```python
# Get vouchers dengan amounts dalam IDR (untuk display)
result = client.vouchers.get_all(display_currency="IDR")

for voucher in result.data:
    print(f"Code: {voucher.code}")
    print(f"Value: {voucher.value} {voucher.currency}")  # Converted to IDR
    print(f"Min Purchase: {voucher.min_purchase} {voucher.currency}")
    # Hanya HAVN vouchers yang di-convert, local vouchers keep original currency
```

#### `get_combined()`

Get combined vouchers (HAVN + local) dengan filtering, sorting, dan pagination.

```python
def get_combined(
    self,
    local_vouchers_callback: Callable[[], List[Dict[str, Any]]],
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    active: Optional[bool] = None,
    type: Optional[str] = None,
    client_type: Optional[str] = None,
    currency: Optional[str] = None,
    search: Optional[str] = None,
    start_date_from: Optional[str] = None,
    start_date_to: Optional[str] = None,
    end_date_from: Optional[str] = None,
    end_date_to: Optional[str] = None,
    created_from: Optional[str] = None,
    created_to: Optional[str] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    min_purchase_from: Optional[int] = None,
    min_purchase_to: Optional[int] = None,
    usage_limit_from: Optional[int] = None,
    usage_limit_to: Optional[int] = None,
    is_valid: Optional[bool] = None,
    is_expired: Optional[bool] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    display_currency: Optional[str] = None,
) -> VoucherListResponse
```

**Important:** Method ini mengkombinasikan HAVN vouchers (dari API) dengan local vouchers (dari callback). Filtering dan sorting dilakukan setelah kombinasi untuk consistency.

##### Parameters

| Parameter                 | Type                                 | Required | Default | Description                                                                                                                                                                                                                           |
| ------------------------- | ------------------------------------ | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `local_vouchers_callback` | `Callable[[], List[Dict[str, Any]]]` | ✅ Yes   | -       | Callback function yang return list local vouchers<br>- Function harus return list dict dengan format voucher<br>- Local vouchers akan di-mark sebagai `is_havn_voucher=False`                                                         |
| `page`                    | `int`                                | No       | `1`     | Page number                                                                                                                                                                                                                           |
| `per_page`                | `int`                                | No       | `10`    | Items per page (max: 100)                                                                                                                                                                                                             |
| `active`                  | `bool`                               | No       | `None`  | Filter by active status                                                                                                                                                                                                               |
| `type`                    | `str`                                | No       | `None`  | Voucher type (DISCOUNT_PERCENTAGE, DISCOUNT_FIXED)                                                                                                                                                                                    |
| `client_type`             | `str`                                | No       | `None`  | Client type (NEW_CUSTOMER, RECURRING)                                                                                                                                                                                                 |
| `currency`                | `str`                                | No       | `None`  | Currency code (USD, IDR, etc.)                                                                                                                                                                                                        |
| `search`                  | `str`                                | No       | `None`  | Search dalam voucher code dan description                                                                                                                                                                                             |
| `start_date_from`         | `str`                                | No       | `None`  | Filter start_date >= (YYYY-MM-DD)                                                                                                                                                                                                     |
| `start_date_to`           | `str`                                | No       | `None`  | Filter start_date <= (YYYY-MM-DD)                                                                                                                                                                                                     |
| `end_date_from`           | `str`                                | No       | `None`  | Filter end_date >= (YYYY-MM-DD)                                                                                                                                                                                                       |
| `end_date_to`             | `str`                                | No       | `None`  | Filter end_date <= (YYYY-MM-DD)                                                                                                                                                                                                       |
| `created_from`            | `str`                                | No       | `None`  | Filter created_date >= (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)                                                                                                                                                                            |
| `created_to`              | `str`                                | No       | `None`  | Filter created_date <= (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)                                                                                                                                                                            |
| `min_value`               | `int`                                | No       | `None`  | Filter value >= (cents/basis points)                                                                                                                                                                                                  |
| `max_value`               | `int`                                | No       | `None`  | Filter value <= (cents/basis points)                                                                                                                                                                                                  |
| `min_purchase_from`       | `int`                                | No       | `None`  | Filter min_purchase >= (cents)                                                                                                                                                                                                        |
| `min_purchase_to`         | `int`                                | No       | `None`  | Filter min_purchase <= (cents)                                                                                                                                                                                                        |
| `usage_limit_from`        | `int`                                | No       | `None`  | Filter usage_limit >=                                                                                                                                                                                                                 |
| `usage_limit_to`          | `int`                                | No       | `None`  | Filter usage_limit <=                                                                                                                                                                                                                 |
| `is_valid`                | `bool`                               | No       | `None`  | Filter by validity (checks active, dates, usage)                                                                                                                                                                                      |
| `is_expired`              | `bool`                               | No       | `None`  | Filter by expired status                                                                                                                                                                                                              |
| `sort_by`                 | `str`                                | No       | `None`  | Sort field (code, type, value, start_date, end_date, created_date, current_usage)                                                                                                                                                     |
| `sort_order`              | `str`                                | No       | `desc`  | Sort direction (asc, desc)                                                                                                                                                                                                            |
| `display_currency`        | `str`                                | No       | `None`  | Target currency untuk display HAVN vouchers.<br>- Backend akan menyetel `VoucherData.display_currency` dan mengembalikan nilai yang sudah dikonversi, sementara `currency` tetap menunjuk ke currency asli (biasanya USD).<br>- Local vouchers tetap memakai currency masing-masing. |

##### Returns

`VoucherListResponse` - Response dengan paginated combined voucher data (HAVN + local).

##### Raises

- `HAVNValidationError`: Jika filters validation gagal
- `HAVNAPIError`: Jika API request gagal

##### Examples

**Get Combined Vouchers:**

```python
def get_local_vouchers():
    return [
        {
            "code": "LOCAL123",
            "type": "DISCOUNT_PERCENTAGE",
            "value": 2000,  # 20%
            "min_purchase": 5000,
            "currency": "IDR",
            "active": True,
            # ... other fields
        }
    ]

# Get combined dengan filtering
result = client.vouchers.get_combined(
    local_vouchers_callback=get_local_vouchers,
    active=True,
    is_valid=True,
    sort_by="created_date",
    sort_order="desc"
)

for voucher in result.data:
    if voucher.is_havn_voucher:
        print(f"HAVN: {voucher.code} - {voucher.currency}")
    else:
        print(f"Local: {voucher.code} - {voucher.currency}")
```

**Get Combined dengan Currency Conversion:**

```python
# Get combined dengan HAVN vouchers di-convert ke IDR
result = client.vouchers.get_combined(
    local_vouchers_callback=get_local_vouchers,
    display_currency="IDR"  # Convert HAVN vouchers to IDR
)

for voucher in result.data:
    if voucher.is_havn_voucher:
        print(f"HAVN: {voucher.code} - {voucher.value} IDR")  # Converted
    else:
        print(f"Local: {voucher.code} - {voucher.value} IDR")  # Original
```

**Important Notes:**

- ✅ **HAVN Vouchers** - Hanya voucher dengan code yang dimulai dengan "HAVN-" yang dikirim ke transaction API
- ✅ **Local Vouchers** - Local vouchers tidak dikirim ke transaction API, hanya `referral_code` yang dikirim
- ✅ **Combined List** - `get_combined()` menggabungkan HAVN dan local vouchers untuk display ke user
- ✅ **Filtering** - Filtering dilakukan setelah kombinasi untuk consistency
- ✅ **Currency Conversion** - Hanya HAVN vouchers yang di-convert, local vouchers keep original currency

---

## Models

### Transaction Models

#### TransactionPayload

Payload untuk transaction webhook.

**Attributes:**

- `amount` (`int`): Final transaction amount dalam cents
- `payment_gateway_transaction_id` (`str`): Payment gateway transaction ID (required, non-empty, max 200 characters)
- `payment_gateway` (`str`): Payment gateway name/identifier (required, max 100 characters)
- `customer_email` (`str`): Customer email (required, valid email format)
- `referral_code` (`str`): Associate referral code (required)
- `promo_code` (`Optional[str]`): Voucher code
- `currency` (`str`): Currency code (default: "USD")
- `customer_type` (`Optional[str]`): Manual override (HAVN otomatis menentukan berdasarkan histori)
- `subtotal_transaction` (`Optional[int]`): Original amount sebelum discount
- `acquisition_method` (`Optional[str]`): Diisi oleh backend untuk kebutuhan audit (REFERRAL vs REFERRAL_VOUCHER). Tidak perlu dikirim dari SDK.
- `custom_fields` (`Optional[Dict[str, Any]]`): Custom metadata (max 3 entries)
- `invoice_id` (`Optional[str]`): External invoice ID
- `transaction_type` (`Optional[str]`): Transaction type (untuk logging)
- `description` (`Optional[str]`): Transaction description

#### TransactionData

Transaction data dari response.

**Attributes:**

- `transaction_id` (`str`): Transaction ID
- `amount` (`int`): Transaction amount dalam cents
- `currency` (`str`): Currency code
- `status` (`str`): Transaction status
- `customer_type` (`str`): Customer type
- `acquisition_method` (`Optional[str]`): Acquisition method yang diisi oleh backend (REFERRAL / REFERRAL_VOUCHER)
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
- `is_owner` (`bool`): Apakah set role sebagai "owner" (default: False, role: "partner")
  - `True`: Set role sebagai "owner"
  - `False`: Set role sebagai "partner" (default)

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
- `is_owner` (`Optional[bool]`): Shared flag untuk set role sebagai "owner" (default: False, role: "partner")
  - `True`: Set role sebagai "owner"
  - `False` atau `None`: Set role sebagai "partner" (default)

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

#### VoucherListFilters

Filters untuk voucher list query.

**Attributes:**

- Semua filter parameters dari `get_all()` dan `get_combined()` methods
- Lihat method documentation untuk detail parameters

#### VoucherData

Voucher data dari list response.

**Attributes:**

- `code` (`str`): Voucher code
- `type` (`str`): Voucher type (DISCOUNT_PERCENTAGE, DISCOUNT_FIXED)
- `value` (`int`): Voucher value (cents atau basis points)
- `min_purchase` (`Optional[int]`): Minimum purchase requirement (cents)
- `max_purchase` (`Optional[int]`): Maximum purchase limit (cents)
- `currency` (`str`): Currency code asli (audit currency, biasanya USD untuk HAVN vouchers)
- `configured_currency` (`Optional[str]`): Currency default SaaS/company jika berbeda dari currency voucher
- `display_currency` (`Optional[str]`): Currency yang digunakan HAVN backend ketika Anda meminta `display_currency` pada request (nilai numeric sudah dikonversi ke currency ini)
- `active` (`bool`): Apakah voucher aktif
- `start_date` (`Optional[str]`): Start date (YYYY-MM-DD)
- `end_date` (`Optional[str]`): End date (YYYY-MM-DD)
- `usage_limit` (`Optional[int]`): Maximum usage limit
- `current_usage` (`int`): Current usage count
- `is_valid` (`bool`): Apakah voucher valid (active, within dates, not exceeded usage)
- `is_expired` (`bool`): Apakah voucher expired
- `is_havn_voucher` (`bool`): Apakah HAVN voucher (code starts with "HAVN-")
- `description` (`Optional[str]`): Voucher description
- `client_type` (`Optional[str]`): Client type (NEW_CUSTOMER, RECURRING)
- `created_date` (`Optional[str]`): Created timestamp
- `creation_cost` (`Optional[int]`): Creation cost (selalu mengikuti currency pada field `currency` / `display_currency` sesuai respons backend)
- `raw_response` (`Dict[str, Any]`): Snapshot payload asli dari backend (berguna untuk debugging/observability)

**Example:**

```python
result = client.vouchers.get_all(active=True)
for voucher in result.data:
    print(f"Code: {voucher.code}")
    print(f"Type: {voucher.type}")
    print(f"Value: {voucher.value}")
    print(f"Currency (audit): {voucher.currency}")
    print(f"Display currency: {voucher.display_currency or voucher.currency}")
    print(f"Is HAVN: {voucher.is_havn_voucher}")
    print(f"Is Valid: {voucher.is_valid}")
    print(f"Configured currency: {voucher.configured_currency}")
    print(f"Raw payload currency: {voucher.raw_response.get('currency')}")
```

#### VoucherListPagination

Pagination metadata dari voucher list response.

**Attributes:**

- `page` (`int`): Current page number
- `per_page` (`int`): Items per page
- `total` (`int`): Total items
- `total_pages` (`int`): Total pages
- `has_next` (`bool`): Apakah ada next page
- `has_prev` (`bool`): Apakah ada previous page

#### VoucherListResponse

Response dari voucher list (get_all atau get_combined).

**Attributes:**

- `success` (`bool`): Apakah request berhasil
- `message` (`str`): Response message
- `data` (`List[VoucherData]`): List voucher data
- `pagination` (`VoucherListPagination`): Pagination metadata
- `raw_response` (`Dict[str, Any]`): Raw response dictionary

**Example:**

```python
result = client.vouchers.get_all(active=True, page=1, per_page=20)

# Access pagination
print(f"Page: {result.pagination.page}")
print(f"Total: {result.pagination.total}")
print(f"Total Pages: {result.pagination.total_pages}")

# Access vouchers
for voucher in result.data:
    print(f"{voucher.code}: {voucher.is_valid}")

# Access raw response
print(f"Raw: {result.raw_response}")
```

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

### HAVNRateLimitError

Exception untuk rate limit exceeded errors (429).

```python
class HAVNRateLimitError(HAVNError):
    def __init__(self, message: str, retry_after: int = None, limit: int = None, remaining: int = None)
```

**Attributes:**

- `message` (`str`): Error message
- `retry_after` (`int`, optional): Seconds until rate limit resets
- `limit` (`int`, optional): Total requests allowed per window
- `remaining` (`int`, optional): Remaining requests in current window

**Example:**

```python
import time
from havn import HAVNRateLimitError

try:
    result = client.transactions.send(...)
except HAVNRateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
    print(f"Limit: {e.limit}, Remaining: {e.remaining}")

    # Wait and retry
    if e.retry_after:
        time.sleep(e.retry_after)
        result = client.transactions.send(...)
```

**Note:** Rate limiting aktif untuk semua webhook endpoints dengan per-endpoint limits. Lihat [Examples](EXAMPLES.md#rate-limit-handling) untuk detail lengkap.

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

### Currency Utilities

Utilities untuk currency conversion dengan exchange rate caching dan backend verification support.

#### CurrencyConverter

Main class untuk currency conversion dengan exchange rate caching.

**Location:** `havn.utils.currency.CurrencyConverter`

**Example:**

```python
from havn.utils.currency import CurrencyConverter

# Create converter instance
converter = CurrencyConverter(
    exchange_rate_api_url="https://api.exchangerate-api.com/v4/latest/USD",
    cache_duration_hours=24,
    api_timeout=30
)

# Convert IDR to USD cents
result = converter.convert_to_usd_cents(150000, "IDR")
print(f"USD cents: {result['amount_cents']}")
print(f"Exchange rate: {result['exchange_rate']}")
```

**Methods:**

- `convert_to_usd_cents(amount: int, from_currency: str) -> Dict[str, Any]` - Convert to USD cents
- `convert_from_usd_cents(amount_cents: int, to_currency: str) -> Dict[str, Any]` - Convert from USD cents
- `get_exchange_rate(to_currency: str, from_currency: str = "USD") -> Optional[Decimal]` - Get exchange rate

**Configuration:**

Currency converter dapat dikonfigurasi via environment variables:

- `HAVN_EXCHANGE_RATE_API_URL` - Exchange rate API URL (default: exchangerate-api.com)
- `HAVN_EXCHANGE_RATE_CACHE_DURATION_HOURS` - Cache duration dalam hours (default: 24)
- `HAVN_CURRENCY_API_TIMEOUT` - API timeout dalam seconds (default: 30)

#### `convert_to_usd_cents()`

Convert amount dari source currency ke USD cents (convenience function).

**Location:** `havn.utils.currency.convert_to_usd_cents`

```python
from havn.utils.currency import convert_to_usd_cents

result = convert_to_usd_cents(150000, "IDR")
print(f"USD cents: {result['amount_cents']}")
print(f"Exchange rate: {result['exchange_rate']}")
```

**Parameters:**

- `amount` (`int`): Amount dalam source currency's smallest unit
- `currency` (`str`): Source currency code (e.g., "IDR", "EUR")

**Returns:**

- `Dict[str, Any]` dengan:
  - `amount_cents` (`int`): Amount dalam USD cents
  - `amount_decimal` (`float`): Amount dalam USD dollars
  - `amount_formatted` (`str`): Formatted string (e.g., "$10.00")
  - `currency` (`str`): "USD"
  - `exchange_rate` (`float`): Exchange rate used
  - `original_amount` (`int`): Original amount
  - `original_currency` (`str`): Source currency code

#### `convert_from_usd_cents()`

Convert amount dari USD cents ke target currency (convenience function).

**Location:** `havn.utils.currency.convert_from_usd_cents`

```python
from havn.utils.currency import convert_from_usd_cents

result = convert_from_usd_cents(1000, "IDR")  # 1000 USD cents = ~150000 IDR
print(f"IDR: {result['amount']}")
print(f"Formatted: {result['amount_formatted']}")  # "Rp 150.000"
```

**Parameters:**

- `amount_cents` (`int`): Amount dalam USD cents
- `currency` (`str`): Target currency code (e.g., "IDR", "EUR")

**Returns:**

- `Dict[str, Any]` dengan:
  - `amount` (`int`): Amount dalam target currency's smallest unit
  - `amount_decimal` (`float`): Amount dalam target currency
  - `amount_formatted` (`str`): Formatted string (e.g., "Rp 150.000")
  - `currency` (`str`): Target currency code
  - `exchange_rate` (`float`): Exchange rate used
  - `original_amount_cents` (`int`): Original USD cents
  - `original_currency` (`str`): "USD"

#### `get_exchange_rate()`

Get exchange rate antara currencies (convenience function).

**Location:** `havn.utils.currency.get_exchange_rate`

```python
from havn.utils.currency import get_exchange_rate

# Get exchange rate: 1 USD = X IDR
rate = get_exchange_rate("IDR", "USD")
if rate:
    print(f"1 USD = {rate} IDR")
```

**Parameters:**

- `to_currency` (`str`): Target currency code
- `from_currency` (`str`): Source currency code (default: "USD")

**Returns:**

- `Optional[Decimal]`: Exchange rate (1 from_currency = X to_currency), atau `None` jika not available

#### `get_currency_converter()`

Get singleton CurrencyConverter instance (convenience function).

**Location:** `havn.utils.currency.get_currency_converter`

```python
from havn.utils.currency import get_currency_converter

converter = get_currency_converter()
result = converter.convert_to_usd_cents(150000, "IDR")
```

**Returns:**

- `CurrencyConverter`: Singleton converter instance dengan default settings

**Important Notes:**

- ✅ **Backend Verification** - Backend selalu verify conversion dengan exact match (no tolerance)
- ✅ **Server Authoritative** - Server exchange rate digunakan untuk final calculation
- ✅ **Exchange Rate Caching** - Exchange rates di-cache untuk reduce API calls
- ✅ **Audit Trail** - Original amounts dan exchange rates disimpan di `custom_fields` untuk audit
- ✅ **Transaction Failed** - Jika conversion mismatch, transaction akan di-mark sebagai `FAILED`

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

- Lihat [Examples](EXAMPLES.md) untuk contoh penggunaan lengkap
- Lihat [Integration Flow](INTEGRATION_FLOW.md) untuk panduan integrasi
- Review [README](../README.md) untuk quick start dan common issues
