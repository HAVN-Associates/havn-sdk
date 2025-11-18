# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-13

### Added

- Initial release of HAVN Python SDK
- Transaction webhook support
- User sync webhook support
- Voucher validation support
- HMAC-SHA256 authentication
- Automatic retry logic with exponential backoff
- Test mode (dry-run) support
- Comprehensive error handling
- Full type hints support
- Pydantic-style model validation
- Context manager support
- Environment variable configuration
- Complete documentation and examples

### Features

- ✅ Simple & Intuitive API
- ✅ Automatic Authentication
- ✅ Type Hints
- ✅ Retry Logic
- ✅ Comprehensive Models
- ✅ Error Handling
- ✅ Test Mode
- ✅ Well Documented

### Examples Included

- 01_simple_transaction.py - Basic transaction sending
- 02_transaction_with_voucher.py - Transaction with voucher discount
- 03_user_sync.py - User synchronization from OAuth
- 04_error_handling.py - Comprehensive error handling
- 05_test_mode.py - Test mode (dry-run) usage
- 06_advanced_usage.py - Advanced features

### Documentation

- README.md - Complete usage guide
- API documentation for all endpoints
- Type hints for IDE autocomplete
- Comprehensive examples

## [Unreleased]
## [1.2.0] - 2025-11-18

### Changed
- Auto-bumped version to 1.2.0

## [1.1.10] - 2025-11-18

### Changed
- Auto-bumped version to 1.1.10

## [1.1.8] - 2025-11-18

### Changed
- Auto-bumped version to 1.1.8

## [1.1.7] - 2025-11-18

### Changed
- Auto-bumped version to 1.1.7

## [1.1.6] - 2025-11-18

### Changed
- Auto-bumped version to 1.1.6


## [1.1.5] - 2025-11-18

### Changed
- Transaction webhook kini menggunakan flag `server_side_conversion` untuk seluruh transaksi non-USD; SDK hanya meneruskan amount/currency mentah dan HAVN backend menjadi sumber kebenaran tunggal.
- Voucher webhook (`validate`, `get_all`, `get_combined`) tidak lagi melakukan konversi lokal dan sepenuhnya mengandalkan parameter `display_currency` yang diproses backend.
- Docstring serta contoh diperbarui agar sesuai dengan arsitektur server-side FX.

### Deprecated
- Helper `convert_to_usd_cents()` dan `convert_from_usd_cents()` hanya dipertahankan untuk kebutuhan tampilan/debugging dan akan dihapus pada rilis mayor berikutnya.
- Parameter `auto_convert` pada voucher validation masih diterima namun menampilkan `DeprecationWarning`; tidak lagi mempengaruhi perilaku.

### Documentation
- README, API reference, dan seluruh dokumen terkait transaksi/voucher diperbarui untuk menekankan server-side conversion dan flag baru.
- Contoh penggunaan non-USD kini menampilkan `server_side_conversion=True` serta menghapus referensi `auto_convert`.

## [1.1.4] - 2025-11-17

### Changed
- Auto-bumped version to 1.1.4
## [1.1.2] - 2025-11-17

### Changed
- Auto-bumped version to 1.1.2

## [1.1.1] - 2025-11-17

### Changed
- Auto-bumped version to 1.1.1

## [1.1.0] - 2025-11-17

### Changed
- Auto-bumped version to 1.1.0

## [1.0.10] - 2025-11-17

### Changed
- Auto-bumped version to 1.0.10

## [1.0.9] - 2025-11-17

### Changed
- Auto-bumped version to 1.0.9

## [1.0.8] - 2025-11-16

### Changed
- Auto-bumped version to 1.0.8

## [1.0.7] - 2025-11-15

### Changed
- Auto-bumped version to 1.0.7

## [1.0.6] - 2025-11-15

### Changed
- Auto-bumped version to 1.0.6

## [1.0.5] - 2025-11-15

### Changed
- Auto-bumped version to 1.0.5


### Planned

- Async client support (asyncio)
- Webhook signature verification utilities
- CLI tool for testing
- More comprehensive integration tests

## [1.1.0] - 2025-01-15

### Added

- **Bulk User Sync** - Support untuk sync multiple users dalam satu request
  - `UserSyncWebhook.sync_bulk()` method untuk bulk operations
  - `BulkUserSyncPayload` dan `BulkUserSyncResponse` models
  - `BulkSyncSummary` model untuk statistics
  - Shared parameters untuk efficiency (upline_code, referral_code, create_associate, is_owner)
  - Per-user override parameters
  - Batch processing dengan referral_code dari batch sebelumnya
  - Partial success support dengan detailed error reporting
- **is_owner Flag** - Support untuk set role "owner" vs "partner"
  - `is_owner` parameter di `UserSyncPayload` dan `BulkUserSyncPayload`
  - Per-user atau shared flag untuk bulk sync
  - Validation untuk is_owner flag (boolean check)
- **Rate Limiting Support** - Automatic rate limit handling
  - `HAVNRateLimitError` exception dengan retry_after, limit, remaining
  - Automatic extraction dari X-RateLimit-\* headers
  - Proper error handling dan retry logic
- **Enhanced Error Handling** - Better rate limit error handling dengan detailed info
- **Voucher Management** - Comprehensive voucher features
  - `VoucherWebhook.get_all()` - Get all vouchers dengan pagination, filtering, dan search
  - `VoucherWebhook.get_combined()` - Get combined vouchers (HAVN + local) dengan filtering dan sorting
  - `VoucherListFilters`, `VoucherData`, `VoucherListPagination`, `VoucherListResponse` models
  - `is_havn_voucher_code()` helper function untuk identify HAVN vouchers
  - Support untuk local voucher integration via callback
  - Currency conversion untuk voucher display (`display_currency` parameter)
- **Currency Conversion** - Comprehensive currency conversion support
  - `CurrencyConverter` class dengan exchange rate caching
  - `convert_to_usd_cents()`, `convert_from_usd_cents()`, `get_exchange_rate()` helper functions
  - `auto_convert` parameter untuk transaction dan voucher validation
  - `display_currency` parameter untuk voucher list conversion
  - Exchange rate caching dengan configurable duration
  - Backend verification dengan exact match requirement (security)
  - Original amounts dan exchange rates stored di `custom_fields` untuk audit
- **Local vs HAVN Voucher Handling** - Intelligent voucher processing
  - Automatic detection HAVN vouchers (code starts with "HAVN-")
  - HAVN vouchers sent ke transaction API (referral_code + promo_code)
  - Local vouchers NOT sent ke transaction API (only referral_code sent)
  - Combined voucher list support untuk display

### Changed

- Updated `UserSyncPayload` untuk include `is_owner` field
- Updated `BulkUserSyncPayload` untuk include `is_owner` field
- Enhanced validation untuk bulk sync dengan is_owner checks
- Updated client untuk handle 429 rate limit responses
- Updated `TransactionWebhook.send()` untuk support currency conversion dan local voucher handling
- Updated `VoucherWebhook.validate()` untuk support currency conversion dengan backend verification
- Updated `VoucherWebhook.get_all()` dan `get_combined()` untuk support currency conversion
- Export `HAVNRateLimitError`, `VoucherListFilters`, `VoucherData`, `VoucherListPagination`, `VoucherListResponse`, `is_havn_voucher_code`, dan currency utilities di `__init__.py`

### Security

- **Currency Conversion Verification** - Backend selalu verify conversion dengan exact match (no tolerance)
- **Server-Side Authoritative** - Server exchange rate digunakan untuk final calculation
- **Audit Trail** - Original amounts dan exchange rates disimpan di `custom_fields` untuk audit
- **Transaction Failed** - Jika conversion mismatch, transaction di-mark sebagai `FAILED`

### Documentation

- Updated API_REFERENCE.md dengan bulk sync, is_owner, rate limiting, voucher features, dan currency conversion documentation
- Updated EXAMPLES.md dengan bulk sync, is_owner, currency conversion, dan voucher examples (get_all, get_combined)
- Updated INTEGRATION_FLOW.md dengan bulk sync workflow, currency conversion, security notes, dan voucher handling
- Updated README.md dengan rate limiting, bulk sync, voucher features (get_all, get_combined), dan currency conversion

## [1.0.4] - 2025-11-15

### Changed

- Auto-bumped version to 1.0.4

## [1.0.3] - 2025-11-14

### Changed

- Auto-bumped version to 1.0.3

## [1.0.2] - 2025-11-14

### Changed

- Auto-bumped version to 1.0.2

## [1.0.1] - 2025-11-14

### Changed

- Auto-bumped version to 1.0.1
