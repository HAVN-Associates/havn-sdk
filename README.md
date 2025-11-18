# HAVN Python SDK

SDK resmi untuk menghubungkan SaaS Anda ke HAVN (Hierarchical Associate Voucher Network) API dengan autentikasi aman, model data terstruktur, serta helper untuk seluruh rangkaian webhook HAVN.

## Nilai Utama

- Integrasi cepat: client, konfigurasi, dan helper siap pakai untuk auth, transaksi, user sync, dan voucher.
- Aman & resilien: HMAC signature, retry bawaan, dan pengecualian khusus untuk memudahkan observabilitas.
- Konsisten: seluruh payload, response, dan error memiliki model serta dokumentasi terstandarisasi.
- Server-side currency conversion: SDK meneruskan amount/currency mentah dan HAVN backend menjadi single source of truth (aktifkan `server_side_conversion=True` pada transaksi non-USD; voucher validation/listing selalu mengikuti backend).

## Quick Start

1. Siapkan lingkungan Python 3.8+ (disarankan menggunakan virtual environment).
2. Instal paket melalui `pip install havn-sdk`.
3. Konfigurasikan API key & webhook secret via environment variables atau parameter client.
4. Buka folder `docs/` untuk panduan metode, contoh skenario, dan best practices sebelum menghubungkan endpoint produksi.

### Pembaruan Penting v1.1.5

- **Server-Side FX Conversion**: Semua konversi resmi kini dilakukan di backend HAVN. SDK cukup meneruskan `amount` dalam smallest unit currency asal dan set `server_side_conversion=True` ketika bukan USD.
- **Voucher Flow Disederhanakan**: `client.vouchers.validate()`, `get_all()`, dan `get_combined()` tidak lagi melakukan konversi lokal; gunakan `display_currency` untuk meminta tampilan tertentu dari backend.
- **Utilitas Konversi Didepresiasi**: `convert_to_usd_cents()` dan `convert_from_usd_cents()` masih tersedia untuk debugging/tampilan, namun akan dihapus pada rilis mendatang. Gunakan backend sebagai sumber kebenaran.

### Pembaruan Penting v1.1.6

- **Voucher Payload Enrichment**: Response `VoucherData` kini menyertakan `configured_currency` (currency default SaaS) dan `display_currency` (currency hasil konversi backend) sehingga frontend dapat membedakan nilai audit vs tampilan.
- **Raw Payload Snapshot**: Setiap voucher juga membawa `raw_response` untuk debugging/observability sehingga Anda bisa melihat struktur asli dari HAVN backend tanpa perlu logging terpisah.
- **Dokumentasi Diperbarui**: Lihat `docs/VOUCHER_WEBHOOK.md` dan `docs/EXAMPLES.md` untuk contoh cara memanfaatkan field baru tersebut pada checkout flow.

## Navigasi Dokumentasi

| File | Fokus Utama | Manfaat Membacanya |
| --- | --- | --- |
| `docs/README.md` | Indeks dokumentasi dan tautan cepat per use case | Peta awal untuk memilih webhook atau topik yang relevan |
| `docs/INTEGRATION_FLOW.md` | Urutan integrasi end-to-end (sync user → login → transaksi → voucher) | Gambaran holistik alur produksi beserta dependensi antar langkah |
| `docs/API_REFERENCE.md` | Referensi method/mode sdk, parameter, response, dan error resmi | Detail lengkap tiap fungsi publik sehingga implementasi lebih presisi |
| `docs/AUTH_WEBHOOK.md` | Login user via webhook dengan token sementara dan redirect | Panduan membangun pengalaman single sign-on dari SaaS Anda ke HAVN |
| `docs/TRANSACTION_WEBHOOK.md` | Pengiriman transaksi, komisi multi-level, dan penggunaan voucher | Cara memastikan transaksi tervalidasi, tercatat, dan terdistribusi dengan benar |
| `docs/USER_SYNC_WEBHOOK.md` | Sinkronisasi user single maupun bulk serta manajemen role/upline | Strategi provisioning pengguna, owner, dan partner sebelum mengakses HAVN |
| `docs/VOUCHER_WEBHOOK.md` | Validasi, listing, dan kombinasi voucher HAVN + lokal | Langkah membuat pengalaman diskon terkurasi dan konsisten lintas channel |
| `docs/EXAMPLES.md` | Kumpulan skenario praktis lintas framework & workflow | Contoh konkret untuk mengadaptasi SDK ke kode basis Anda |

Gunakan daftar di atas untuk langsung menuju materi yang menjawab kebutuhan integrasi Anda; seluruh file saling melengkapi sehingga Anda dapat memilih detail teknis, panduan alur, maupun referensi contoh sesuai konteks tim.
