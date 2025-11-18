# Transaction Webhook

Dokumentasi untuk TransactionWebhook - Kirim transaksi dan distribusi komisi.

## Daftar Isi

- [Overview](#overview)
- [Method: send()](#method-send)
- [Parameters](#parameters)
- [Response](#response)
- [Contoh Penggunaan](#contoh-penggunaan)

---

## Overview

`TransactionWebhook` menyediakan method untuk mengirim transaksi ke HAVN dengan automatic commission distribution.

**Key Features:**
- ✅ Multi-currency support (USD, EUR, GBP, IDR, dll)
- ✅ Server-side currency conversion (aktifkan `server_side_conversion` untuk amount non-USD)
- ✅ Voucher/promo code support
- ✅ Custom fields untuk metadata
- ✅ Automatic commission calculation & distribution
- ✅ Test mode (dry-run) support

---

## Method: send()

Kirim transaksi ke HAVN untuk commission processing.

### Signature

```python
def send(
    amount: int,
    payment_gateway_transaction_id: str,
    customer_email: str,
    referral_code: Optional[str] = None,
    promo_code: Optional[str] = None,
    subtotal_transaction: Optional[int] = None,
    currency: str = "USD",
    customer_type: str = "NEW_CUSTOMER",
    custom_fields: Optional[Dict[str, Any]] = None
    invoice_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    description: Optional[str] = None,
    server_side_conversion: bool = False,
) -> TransactionResponse
```

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `amount` | `int` | Yes | - | Jumlah transaksi final dalam smallest unit currency yang dikirimkan. Kirim USD cents jika `currency="USD"`; untuk currency lain kirim nilai mentahnya dan aktifkan `server_side_conversion`. |
| `payment_gateway_transaction_id` | `str` | Yes | - | ID transaksi dari payment gateway (maks 200 karakter). |
| `customer_email` | `str` | Yes | - | Email customer yang valid. |
| `referral_code` | `str` | No | None | Referral code associate (HAVN-XX-XXX). |
| `promo_code` | `str` | No | None | Voucher/promo code untuk diskon (hanya HAVN voucher yang akan dikirim ke backend). |
| `subtotal_transaction` | `int` | No | None | Subtotal sebelum diskon (mengikuti aturan currency yang sama dengan `amount`). |
| `currency` | `str` | No | "USD" | Currency code (USD, EUR, GBP, IDR, dll). Backend akan mengkonversi ke USD jika `server_side_conversion=True`. |
| `customer_type` | `str` | No | "NEW_CUSTOMER" | "NEW_CUSTOMER" atau "RETURNING_CUSTOMER". |
| `custom_fields` | `dict` | No | None | Custom metadata (max 10 fields). |
| `server_side_conversion` | `bool` | No | `False` | Aktifkan untuk meminta backend HAVN melakukan konversi currency resmi terhadap amount mentah Anda. |

### Parameter Details

#### amount
- **Type**: `int`
- **Required**: Yes
- **Format**: Dalam smallest unit currency sesuai parameter `currency`
- **Example**: `10000` = $100.00 USD (cents) atau Rp 10.000 IDR
- **Non-USD**: Kirim nilai mentahnya (mis. rupiah) dan set `server_side_conversion=True` agar backend melakukan konversi resmi.

#### referral_code
- **Type**: `str`
- **Format**: `HAVN-XX-XXX` (2 huruf + 3 digit)
- **Example**: `"HAVN-MJ-001"`, `"HAVN-SE-123"`
- **Note**: Akan di-uppercase otomatis

#### promo_code
- **Type**: `str`
- **Example**: `"VOUCHER123"`, `"DISCOUNT50"`
- **Note**: Voucher harus valid dan active

#### currency
- **Type**: `str`
- **Supported**: USD, EUR, GBP, IDR, SGD, MYR, THB, PHP, VND
- **Default**: "USD"
- **Note**: HAVN backend akan mengkonversi ke USD ketika `server_side_conversion=True`. Jika Anda sudah mengirim USD cents, biarkan flag tersebut `False`.

#### customer_type
- **Type**: `str`
- **Options**: 
  - `"NEW_CUSTOMER"` - First-time buyer
  - `"RETURNING_CUSTOMER"` - Repeat buyer
- **Impact**: Affects commission rate

#### custom_fields
- **Type**: `dict`
- **Max fields**: 10
- **Example**:
  ```python
  {
      "order_id": "ORD123456",
      "payment_method": "credit_card",
      "customer_segment": "premium"
  }
  ```

#### server_side_conversion
- **Type**: `bool`
- **Default**: `False`
- **When to use**: Set `True` jika Anda mengirim `amount` dalam currency selain USD. SDK akan meneruskan nilai asli dan backend HAVN akan mengkonversi menggunakan kurs internal resmi.

---

## Response

### TransactionResponse

```python
@dataclass
class TransactionResponse:
    transaction: Transaction
    commissions: List[Commission]
    total_commission: float
    currency: str
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `transaction` | `Transaction` | Data transaksi yang dibuat |
| `commissions` | `List[Commission]` | List komisi per level |
| `total_commission` | `float` | Total komisi terdistribusi |
| `currency` | `str` | Currency transaksi |

### Transaction Object

```python
@dataclass
class Transaction:
    transaction_id: str
    amount: float
    currency: str
    referral_code: Optional[str]
    promo_code: Optional[str]
    customer_type: str
    status: str
    created_at: str
    custom_fields: Optional[Dict]
```

### Commission Object

```python
@dataclass
class Commission:
    commission_id: str
    associate_id: str
    level: int
    rate: float
    amount: float
    currency: str
    status: str
```

---

## Contoh Penggunaan

### 1. Transaksi Sederhana

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# Transaksi basic
result = client.transactions.send(
    amount=10000,  # $100.00
    referral_code="HAVN-MJ-001",
    payment_gateway_transaction_id="stripe_txn_001",
    customer_email="customer@example.com",
)

print(f"Transaction ID: {result.transaction.transaction_id}")
print(f"Total Commission: ${result.total_commission/100:.2f}")
print(f"Distributed to {len(result.commissions)} levels")
```

### 2. Transaksi dengan Voucher

```python
# Transaksi dengan diskon
result = client.transactions.send(
    amount=8000,  # $80.00 (setelah diskon)
    subtotal_transaction=10000,  # $100.00 (sebelum diskon)
    promo_code="VOUCHER123",
    referral_code="HAVN-MJ-001",
    currency="USD",
    customer_type="NEW_CUSTOMER",
    payment_gateway_transaction_id="stripe_txn_002",
    customer_email="customer@example.com",
)

discount = result.transaction.subtotal_transaction - result.transaction.amount
print(f"Discount: ${discount/100:.2f}")
```

### 3. Multi-Currency

```python
# Transaksi dalam IDR
result = client.transactions.send(
    amount=1000000,  # Rp 1.000.000
    referral_code="HAVN-MJ-001",
    currency="IDR",
    payment_gateway_transaction_id="midtrans_txn_003",
    customer_email="customer@example.com",
    server_side_conversion=True,
)

# Backend akan mengkonversi ke USD secara resmi untuk perhitungan komisi
print(f"Amount (raw): Rp {result.transaction.amount:,}")
print(f"Commission (USD): ${result.total_commission/100:.2f}")
```

### 4. Custom Fields

```python
# Transaksi dengan metadata
result = client.transactions.send(
    amount=10000,
    referral_code="HAVN-MJ-001",
    payment_gateway_transaction_id="stripe_txn_004",
    customer_email="customer@example.com",
    custom_fields={
        "order_id": "ORD123456",
        "payment_method": "credit_card",
        "customer_segment": "premium",
        "campaign": "black_friday_2024"
    }
)

print(f"Order ID: {result.transaction.custom_fields['order_id']}")
```

### 5. Error Handling

```python
from havn import HAVNClient, HAVNAPIError, HAVNValidationError

client = HAVNClient(api_key="...", webhook_secret="...")

try:
    result = client.transactions.send(
        amount=10000,
        referral_code="HAVN-MJ-001",
        promo_code="INVALID_CODE",
        payment_gateway_transaction_id="stripe_txn_005",
        customer_email="customer@example.com",
    )
except HAVNValidationError as e:
    print(f"Validation error: {e}")
except HAVNAPIError as e:
    if e.status_code == 404:
        print("Referral code atau voucher tidak ditemukan")
    elif e.status_code == 400:
        print(f"Bad request: {e.message}")
    else:
        print(f"API error: {e}")
```

### 6. Bulk Transactions

```python
# Loop multiple transactions
transactions = [
    {
        "amount": 10000,
        "referral_code": "HAVN-MJ-001",
        "payment_gateway_transaction_id": "stripe_txn_006",
        "customer_email": "user1@example.com",
    },
    {
        "amount": 20000,
        "referral_code": "HAVN-SE-002",
        "payment_gateway_transaction_id": "stripe_txn_007",
        "customer_email": "user2@example.com",
    },
    {
        "amount": 15000,
        "referral_code": "HAVN-MJ-001",
        "payment_gateway_transaction_id": "stripe_txn_008",
        "customer_email": "user3@example.com",
    },
]

results = []
for txn in transactions:
    result = client.transactions.send(**txn)
    results.append(result)

total_sales = sum(r.transaction.amount for r in results)
total_commissions = sum(r.total_commission for r in results)

print(f"Total Sales: ${total_sales/100:.2f}")
print(f"Total Commissions: ${total_commissions/100:.2f}")
```

### 7. Test Mode

```python
# Dry-run mode - tidak save ke database
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    test_mode=True
)

result = client.transactions.send(
    amount=10000,
    referral_code="HAVN-MJ-001",
    payment_gateway_transaction_id="stripe_txn_009",
    customer_email="customer@example.com",
)

# Response sukses tapi tidak tersimpan
print(f"Test transaction: {result.transaction.transaction_id}")
```

---

## Best Practices

### 1. Amount Handling

```python
# ✅ BENAR: Gunakan cents
amount_dollars = 99.99
amount_cents = int(amount_dollars * 100)  # 9999
result = client.transactions.send(amount=amount_cents)

# ❌ SALAH: Jangan gunakan float decimal
result = client.transactions.send(amount=99.99)  # Bisa error rounding
```

### 2. Referral Code Validation

```python
import re

def is_valid_referral_code(code: str) -> bool:
    pattern = r'^HAVN-[A-Z]{2}-\d{3}$'
    return bool(re.match(pattern, code.upper()))

code = "havn-mj-001"
if is_valid_referral_code(code):
    result = client.transactions.send(
        amount=10000,
        referral_code=code.upper()
    )
```

### 3. Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def send_transaction_with_retry(amount, referral_code):
    return client.transactions.send(
        amount=amount,
        referral_code=referral_code
    )

result = send_transaction_with_retry(10000, "HAVN-MJ-001")
```

### 4. Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

result = client.transactions.send(amount=10000, referral_code="HAVN-MJ-001")

logger.info(
    "Transaction created",
    extra={
        "transaction_id": result.transaction.transaction_id,
        "amount": result.transaction.amount,
        "commission": result.total_commission,
        "levels": len(result.commissions)
    }
)
```

### 5. Persist Promo Code / Voucher Reference

- **Simpan kode voucher HAVN** di sisi SaaS (mis. kolom `havn_voucher_code` pada tabel `payments` / `subscription_payments` dengan panjang 64 karakter) segera setelah user memvalidasi voucher.
- **Gunakan nilai yang tersimpan** tersebut setiap kali memanggil `transactions.send()` agar `promo_code` tetap ada pada retry, manual sync, atau settlement ulang tanpa bergantung pada payload Midtrans/custom_field.
- **Alasan utama**: webhook Midtrans tidak menjamin pengiriman kembali kode voucher, sementara HAVN mewajibkan `promo_code` ketika `subtotal_transaction > amount`. Menyimpan sendiri memastikan tracking komisi dan limit voucher selalu konsisten.
- Jika belum siap menambah kolom permanen, minimal simpan di storage sementara (session/cache) sampai transaksi benar-benar diverifikasi dan dikirim ke HAVN.

---

## Commission Calculation

### Multi-Level Structure

```
Level 1: 5%  → Direct referrer
Level 2: 3%  → Referrer's upline
Level 3: 2%  → Level 2's upline
Level 4: 1%  → Level 3's upline
Level 5: 1%  → Level 4's upline
```

### Example

```python
result = client.transactions.send(
    amount=10000,  # $100.00
    referral_code="HAVN-MJ-001"
)

for commission in result.commissions:
    print(f"Level {commission.level}: ${commission.amount/100:.2f} ({commission.rate*100}%)")

# Output:
# Level 1: $5.00 (5%)
# Level 2: $3.00 (3%)
# Level 3: $2.00 (2%)
# Level 4: $1.00 (1%)
# Level 5: $1.00 (1%)
```

---

## Lihat Juga

- [Auth Webhook](AUTH_WEBHOOK.md)
- [User Sync Webhook](USER_SYNC_WEBHOOK.md)
- [Voucher Webhook](VOUCHER_WEBHOOK.md)
- [Models](MODELS.md)
