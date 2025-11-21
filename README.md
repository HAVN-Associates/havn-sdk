# HAVN Python SDK

SDK resmi untuk menghubungkan SaaS Anda ke HAVN (Hierarchical Associate Voucher Network) API dengan autentikasi aman, model data terstruktur, serta helper untuk seluruh rangkaian webhook HAVN.

## Nilai Utama

- Integrasi cepat: client, konfigurasi, dan helper siap pakai untuk auth, transaksi, dan voucher.
- Aman & resilien: HMAC signature, retry bawaan, dan pengecualian khusus untuk memudahkan observabilitas.
- Konsisten: seluruh payload, response, dan error memiliki model serta dokumentasi terstandarisasi.
- Server-side currency conversion: SDK meneruskan amount/currency mentah dan HAVN backend menjadi single source of truth (aktifkan `server_side_conversion=True` pada transaksi non-USD; voucher validation/listing selalu mengikuti backend).
- **Public Referral Links**: Stateless referral system dengan query parameters - no Redis, no session storage needed!

## Quick Start

1. Siapkan lingkungan Python 3.8+ (disarankan menggunakan virtual environment).
2. Instal paket melalui `pip install havn-sdk`.
3. Konfigurasikan API key & webhook secret via environment variables atau parameter client.
4. Buka folder `docs/` untuk panduan metode, contoh skenario, dan best practices sebelum menghubungkan endpoint produksi.

## 🎯 Public Referral Links (NEW!)

**Stateless referral system** - no Redis, no session storage, just query params!

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# Step 1: Capture referral params in your login page
# URL: https://yourcompany.com/login?ref=HAVN-MJ-001&vc=DISC50

# Step 2: Validate voucher on first transaction
validation = client.vouchers.validate(
    code="DISC50",
    amount=10000,
    currency="USD"
)

# Step 3: Send transaction with referral + voucher
result = client.transactions.send(
    customer_email="user@example.com",
    amount=10000,
    currency="USD",
    referral_code="HAVN-MJ-001",  # From query param
    promo_code="DISC50",           # From query param
    payment_gateway_transaction_id="txn_123"
)
```

**See [docs/REFERRAL_PUBLIC_LINK.md](docs/REFERRAL_PUBLIC_LINK.md) for complete integration guide!**

### Pembaruan Penting v1.1.5

- **Server-Side FX Conversion**: Semua konversi resmi kini dilakukan di backend HAVN. SDK cukup meneruskan `amount` dalam smallest unit currency asal dan set `server_side_conversion=True` ketika bukan USD.
- **Voucher Flow Disederhanakan**: `client.vouchers.validate()`, `get_all()`, dan `get_combined()` tidak lagi melakukan konversi lokal; gunakan `display_currency` untuk meminta tampilan tertentu dari backend.
- **Utilitas Konversi Didepresiasi**: `convert_to_usd_cents()` dan `convert_from_usd_cents()` masih tersedia untuk debugging/tampilan, namun akan dihapus pada rilis mendatang. Gunakan backend sebagai sumber kebenaran.

### Pembaruan Penting v2.0.0

- **Public Referral Links**: Sistem referral baru yang stateless, menggunakan query parameters (no Redis/session storage).
- **User Sync Deprecated**: `client.users.sync()` tidak lagi digunakan. User management sekarang di-handle di SaaS company side.
- **Simplified Integration**: Lebih mudah integrate dengan existing login flow Anda (Google OAuth, Email, Magic Link, etc.).
- **Voucher Payload Enrichment**: Response `VoucherData` menyertakan `configured_currency` dan `display_currency`.
- **Raw Payload Snapshot**: Setiap voucher membawa `raw_response` untuk debugging.

### Migration from v1.x to v2.0

**Breaking Changes:**
- ❌ `client.users.sync()` - Removed (deprecated)
- ❌ `client.users.sync_bulk()` - Removed (deprecated)

**Migration Steps:**
1. Remove all `client.users.sync()` calls
2. Implement referral param capture in your login page
3. See `docs/REFERRAL_PUBLIC_LINK.md` for complete guide

## Navigasi Dokumentasi

| File | Fokus Utama | Manfaat Membacanya |
| --- | --- | --- |
| `docs/README.md` | Indeks dokumentasi dan tautan cepat per use case | Peta awal untuk memilih webhook atau topik yang relevan |
| `docs/INTEGRATION_FLOW.md` | Urutan integrasi end-to-end (sync user → login → transaksi → voucher) | Gambaran holistik alur produksi beserta dependensi antar langkah |
| `docs/API_REFERENCE.md` | Referensi method/mode sdk, parameter, response, dan error resmi | Detail lengkap tiap fungsi publik sehingga implementasi lebih presisi |
| `docs/AUTH_WEBHOOK.md` | Login user via webhook dengan token sementara dan redirect | Panduan membangun pengalaman single sign-on dari SaaS Anda ke HAVN |
| `docs/TRANSACTION_WEBHOOK.md` | Pengiriman transaksi, komisi multi-level, dan penggunaan voucher | Cara memastikan transaksi tervalidasi, tercatat, dan terdistribusi dengan benar |
| `docs/REFERRAL_PUBLIC_LINK.md` | **Public referral link integration (NEW!)** | Sistem referral stateless dengan query params - recommended approach! |
| ~~`docs/USER_SYNC_WEBHOOK.md`~~ | ~~Sinkronisasi user~~ | **DEPRECATED** - User management now on SaaS side |
| `docs/VOUCHER_WEBHOOK.md` | Validasi, listing, dan kombinasi voucher HAVN + lokal | Langkah membuat pengalaman diskon terkurasi dan konsisten lintas channel |
| `docs/EXAMPLES.md` | Kumpulan skenario praktis lintas framework & workflow | Contoh konkret untuk mengadaptasi SDK ke kode basis Anda |

Gunakan daftar di atas untuk langsung menuju materi yang menjawab kebutuhan integrasi Anda; seluruh file saling melengkapi sehingga Anda dapat memilih detail teknis, panduan alur, maupun referensi contoh sesuai konteks tim.
