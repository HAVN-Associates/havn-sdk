# Voucher Webhook

Dokumentasi untuk VoucherWebhook - Validasi dan manajemen voucher/promo code.

## Daftar Isi

- [Overview](#overview)
- [Method: validate()](#method-validate)
- [Method: get_all()](#method-get_all)
- [Method: get_combined()](#method-get_combined)
- [Contoh Penggunaan](#contoh-penggunaan)

---

## Overview

`VoucherWebhook` menyediakan method untuk:
- Validasi voucher code
- Get voucher list dengan filtering & pagination
- Combine HAVN vouchers dengan local vouchers

**Key Features:**
- ✅ Voucher validation dengan amount & currency
- ✅ Multi-currency support
- ✅ Pagination & filtering
- ✅ Search by code
- ✅ Combine HAVN + local vouchers
- ✅ Display currency diproses langsung oleh backend HAVN

---

## Method: validate()

Validasi voucher code dengan amount dan currency.

### Signature

```python
def validate(
    voucher_code: str,
    amount: Optional[int] = None,
    currency: Optional[str] = None,
) -> bool
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `voucher_code` | `str` | Yes | - | Kode voucher yang akan divalidasi |
| `amount` | `int` | No | `None` | Transaction amount dalam smallest unit currency Anda. Jika tidak dikirim, backend hanya mengecek status voucher. |
| `currency` | `str` | No | `None` | Currency asal dari amount. Jika tidak diisi, backend mengasumsikan amount sudah berada pada currency voucher. |

### Returns

`bool` - `True` jika voucher valid, raise exception jika invalid

### Raises

| Exception | Condition |
|-----------|-----------|
| `HAVNAPIError` | Voucher tidak ditemukan, expired, inactive, dll |

### Validation Rules

Voucher dianggap **valid** jika:
- ✅ Voucher exists
- ✅ Status active
- ✅ Belum expired (valid_until > now)
- ✅ Amount >= min_purchase
- ✅ Usage belum mencapai max_usage
- ✅ Currency supported

### Currency Handling

- Backend HAVN adalah satu-satunya pihak yang melakukan konversi FX untuk voucher validation.
- Kirim saja amount/currency mentah Anda; SDK tidak lagi melakukan auto-conversion.
- Jika Anda hanya butuh mengecek status voucher, Anda dapat memanggil `validate()` tanpa `amount`.

---

## Method: get_all()

Get semua vouchers dengan filtering, pagination, dan search.

### Signature

```python
def get_all(
    page: int = 1,
    per_page: int = 20,
    active: Optional[bool] = None,
    is_valid: Optional[bool] = None,
    search: Optional[str] = None,
    display_currency: Optional[str] = None
) -> VoucherListResponse
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | `int` | No | 1 | Page number (1-based) |
| `per_page` | `int` | No | 20 | Items per page (max 100) |
| `active` | `bool` | No | None | Filter by active status |
| `is_valid` | `bool` | No | None | Filter by validity (not expired) |
| `search` | `str` | No | None | Search by code (partial match) |
| `display_currency` | `str` | No | None | Minta backend HAVN mengembalikan HAVN vouchers dalam currency tertentu untuk display. |

### Returns

```python
@dataclass
class VoucherListResponse:
    data: List[Voucher]
    pagination: Pagination
    filters: Dict[str, Any]
```

### Pagination Object

```python
@dataclass
class Pagination:
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
```

---

## Method: get_combined()

Combine HAVN vouchers dengan local vouchers dari SaaS company.

### Signature

```python
def get_combined(
    local_vouchers_callback: Optional[Callable[[], List[Dict]]] = None,
    active: Optional[bool] = None,
    is_valid: Optional[bool] = None,
    search: Optional[str] = None,
    display_currency: Optional[str] = None
) -> VoucherListResponse
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `local_vouchers_callback` | `Callable` | No | None | Function yang return list local vouchers |
| `active` | `bool` | No | None | Filter by active |
| `is_valid` | `bool` | No | None | Filter by validity |
| `search` | `str` | No | None | Search by code |
| `display_currency` | `str` | No | None | Currency tujuan untuk display; backend akan mengkonversi HAVN vouchers ke currency ini. |

### Local Voucher Format

```python
{
    "code": "LOCAL123",
    "type": "DISCOUNT_PERCENTAGE",  # or "DISCOUNT_FIXED"
    "value": 10,  # 10% or $10
    "currency": "USD",
    "min_purchase": 5000,
    "max_discount": 10000,
    "valid_from": "2024-01-01T00:00:00Z",
    "valid_until": "2024-12-31T23:59:59Z",
    "is_active": True,
    "usage_count": 0,
    "max_usage": 100
}
```


## Field Notes (v1.1.6+)

- `currency`: Audit currency yang disimpan HAVN (biasanya USD untuk HAVN vouchers). Nilai numeric pada field seperti `value`/`min_purchase` selalu dinyatakan dalam currency ini ketika `display_currency` tidak digunakan.
- `configured_currency`: Currency default SaaS yang dikonfigurasi di HAVN. Gunakan untuk mengetahui preferensi tenant tanpa melihat request Anda.
- `display_currency`: Currency yang dipakai HAVN backend ketika Anda memanggil `display_currency` di request. Nilai numeric untuk HAVN vouchers sudah dikonversi ke currency ini, sementara local vouchers tetap memakai currency masing-masing.
- `raw_response`: Snapshot payload asli dari backend. Sangat berguna untuk debugging ketika Anda butuh memeriksa field tambahan tanpa menunggu rilis SDK.

Gunakan kombinasi field tersebut untuk membedakan: currency asal (audit), currency konfigurasi tenant, dan currency yang sedang ditampilkan ke end-user.

---
---

## Contoh Penggunaan

### 1. Validate Voucher

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# Validasi voucher
try:
    is_valid = client.vouchers.validate(
        voucher_code="VOUCHER123",
        amount=10000,  # $100.00
        currency="USD"
    )
    print("✅ Voucher valid")
    
except Exception as e:
    print(f"❌ Voucher tidak valid: {e}")
```

### 2. Get All Vouchers

```python
# Get semua vouchers dengan pagination
result = client.vouchers.get_all(
    page=1,
    per_page=20
)

print(f"Total vouchers: {result.pagination.total}")
print(f"Page {result.pagination.page} of {result.pagination.total_pages}")

for voucher in result.data:
    print(
        f"{voucher.code}: {voucher.value} {voucher.display_currency or voucher.currency}"
    )
```

### 3. Filter Active Vouchers

```python
# Filter vouchers yang active dan belum expired
result = client.vouchers.get_all(
    active=True,
    is_valid=True,
    per_page=50
)

print(f"Active vouchers: {len(result.data)}")
```

### 4. Search Vouchers

```python
# Search voucher by code
result = client.vouchers.get_all(
    search="BLACK",  # Partial match
    active=True
)

for voucher in result.data:
    print(f"Found: {voucher.code}")
```

### 5. Currency Conversion

```python
# Minta backend mengembalikan nilai HAVN voucher dalam IDR untuk display
result = client.vouchers.get_all(
    active=True,
    display_currency="IDR"
)

for voucher in result.data:
    source = "HAVN" if voucher.is_havn_voucher else "Local"
    audit_currency = voucher.currency
    display_currency = voucher.display_currency or voucher.currency
    print(
        f"{source} {voucher.code}: {voucher.value} {display_currency} (audit: {audit_currency})"
    )
    if voucher.configured_currency:
        print(f"Configured currency: {voucher.configured_currency}")
    print(f"Raw payload currency: {voucher.raw_response.get('currency')}")
```

### 6. Combine dengan Local Vouchers

```python
# Function untuk get local vouchers
def get_local_vouchers():
    return [
        {
            "code": "LOCAL10",
            "type": "DISCOUNT_PERCENTAGE",
            "value": 10,
            "currency": "USD",
            "min_purchase": 5000,
            "is_active": True
        },
        {
            "code": "LOCAL20",
            "type": "DISCOUNT_FIXED",
            "value": 2000,
            "currency": "USD",
            "min_purchase": 10000,
            "is_active": True
        }
    ]

# Combine HAVN + local vouchers
result = client.vouchers.get_combined(
    local_vouchers_callback=get_local_vouchers,
    active=True,
    display_currency="IDR"
)

havn_vouchers = [v for v in result.data if v.is_havn_voucher]
local_vouchers = [v for v in result.data if not v.is_havn_voucher]

print(f"HAVN vouchers: {len(havn_vouchers)}")
print(f"Local vouchers: {len(local_vouchers)}")
```

### 7. Pagination Loop

```python
# Loop semua pages
page = 1
all_vouchers = []

while True:
    result = client.vouchers.get_all(page=page, per_page=50)
    all_vouchers.extend(result.data)
    
    if not result.pagination.has_next:
        break
    
    page += 1

print(f"Total vouchers loaded: {len(all_vouchers)}")
```

### 8. Display Vouchers di UI

```python
# Get vouchers untuk display di checkout page
result = client.vouchers.get_all(
    active=True,
    is_valid=True,
    display_currency="IDR",
    per_page=10
)

# Format untuk display
vouchers_display = []
for v in result.data:
    display_currency = v.display_currency or v.currency
    if v.type == "DISCOUNT_PERCENTAGE":
        discount_text = f"{v.value}%"
    else:
        discount_text = f"{display_currency} {v.value:,}"

    vouchers_display.append({
        "code": v.code,
        "description": f"Diskon {discount_text}",
        "min_purchase": f"Min. {display_currency} {v.min_purchase:,}",
        "expires": v.valid_until
    })

print(vouchers_display)
```

### 9. Apply Voucher di Transaction

```python
# Step 1: Validate voucher
voucher_code = "BLACKFRIDAY50"
subtotal = 10000

try:
    is_valid = client.vouchers.validate(
        voucher_code=voucher_code,
        amount=subtotal,
        currency="USD"
    )
    
    # Step 2: Get voucher details untuk calculate discount
    vouchers = client.vouchers.get_all(search=voucher_code)
    voucher = vouchers.data[0]
    
    # Step 3: Calculate discount
    if voucher.type == "DISCOUNT_PERCENTAGE":
        discount = int(subtotal * voucher.value / 100)
        if voucher.max_discount:
            discount = min(discount, voucher.max_discount)
    else:
        discount = voucher.value
    
    final_amount = subtotal - discount
    
    # Step 4: Send transaction
    result = client.transactions.send(
        amount=final_amount,
        subtotal_transaction=subtotal,
        promo_code=voucher_code,
        referral_code="HAVN-MJ-001"
    )
    
    print(f"Transaction ID: {result.transaction.transaction_id}")
    print(f"Discount: ${discount/100:.2f}")
    
except Exception as e:
    print(f"Error: {e}")
```

---

## Best Practices

### 1. Cache Vouchers

```python
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=1)
def get_vouchers_cached(ttl_hash: int):
    """Cache vouchers dengan TTL"""
    return client.vouchers.get_all(active=True, is_valid=True)

# TTL 5 minutes
import time
ttl_hash = int(time.time() / 300)
vouchers = get_vouchers_cached(ttl_hash)
```

### 2. Error Handling

```python
def validate_voucher_safe(code: str, amount: int, currency: str) -> bool:
    """Validate dengan error handling"""
    try:
        return client.vouchers.validate(
            voucher_code=code,
            amount=amount,
            currency=currency
        )
    except HAVNAPIError as e:
        if "expired" in str(e).lower():
            print("Voucher sudah expired")
        elif "minimum purchase" in str(e).lower():
            print("Belum memenuhi minimum purchase")
        else:
            print(f"Voucher invalid: {e}")
        return False
```

### 3. Display Currency

```python
# Selalu gunakan display_currency untuk UI
user_currency = "IDR"  # Derived from user profile

result = client.vouchers.get_all(
    active=True,
    is_valid=True,
    display_currency=user_currency
)

for voucher in result.data:
    print(f"{voucher.code}: {voucher.value} {voucher.currency}")
```

### 4. Combine Vouchers

```python
class VoucherService:
    def __init__(self, client: HAVNClient):
        self.client = client
    
    def get_all_vouchers(self):
        """Get HAVN + local vouchers"""
        return self.client.vouchers.get_combined(
            local_vouchers_callback=self._get_local_vouchers,
            active=True,
            is_valid=True,
            display_currency="IDR"
        )
    
    def _get_local_vouchers(self):
        """Load dari database lokal"""
        # Query dari DB
        return LocalVoucher.objects.filter(is_active=True).values()
```

---

## Voucher Types

### DISCOUNT_PERCENTAGE

```python
{
    "code": "SAVE10",
    "type": "DISCOUNT_PERCENTAGE",
    "value": 10,  # 10%
    "max_discount": 10000  # Max $100
}
```

**Calculation:**
```python
discount = min(amount * 0.10, max_discount)
final = amount - discount
```

### DISCOUNT_FIXED

```python
{
    "code": "FLAT20",
    "type": "DISCOUNT_FIXED",
    "value": 2000,  # $20
    "currency": "USD"
}
```

**Calculation:**
```python
discount = value
final = amount - discount
```

---

## Lihat Juga

- [Auth Webhook](AUTH_WEBHOOK.md)
- [Transaction Webhook](TRANSACTION_WEBHOOK.md)
- [User Sync Webhook](USER_SYNC_WEBHOOK.md)
- [Models](MODELS.md)
