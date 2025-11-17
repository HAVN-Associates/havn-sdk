# HAVN Python SDK

SDK resmi untuk menghubungkan SaaS Anda ke HAVN (Hierarchical Associate Voucher Network) API dengan autentikasi aman, model data terstruktur, serta helper untuk seluruh rangkaian webhook HAVN.

## Nilai Utama

- Integrasi cepat: client, konfigurasi, dan helper siap pakai untuk auth, transaksi, user sync, dan voucher.
- Aman & resilien: HMAC signature, retry bawaan, dan pengecualian khusus untuk memudahkan observabilitas.
- Konsisten: seluruh payload, response, dan error memiliki model serta dokumentasi terstandarisasi.

## Quick Start

1. Siapkan lingkungan Python 3.8+ (disarankan menggunakan virtual environment).
2. Instal paket melalui `pip install havn-sdk`.
3. Konfigurasikan API key & webhook secret via environment variables atau parameter client.
4. Buka folder `docs/` untuk panduan metode, contoh skenario, dan best practices sebelum menghubungkan endpoint produksi.

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
