# API Reference

Complete API reference for HAVN Python SDK.

## Client

### HAVNClient

Main client class for interacting with HAVN API.

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

**Parameters:**
- `api_key` (str, optional): API key for authentication. Reads from `HAVN_API_KEY` env var if not provided.
- `webhook_secret` (str, optional): Webhook secret for HMAC signing. Reads from `HAVN_WEBHOOK_SECRET` env var if not provided.
- `base_url` (str, optional): Base URL for API (default: https://api.havn.com)
- `timeout` (int, optional): Request timeout in seconds (default: 30)
- `max_retries` (int, optional): Maximum retry attempts (default: 3)
- `backoff_factor` (float, optional): Exponential backoff multiplier (default: 0.5)
- `test_mode` (bool, optional): Enable dry-run mode (default: False)

**Properties:**
- `transactions` (TransactionWebhook): Transaction webhook handler
- `users` (UserSyncWebhook): User sync webhook handler
- `vouchers` (VoucherWebhook): Voucher webhook handler

**Methods:**
- `close()`: Close HTTP session
- `__enter__()`: Context manager entry
- `__exit__()`: Context manager exit

---

## Webhooks

### TransactionWebhook

Handler for transaction webhooks.

#### send()

Send transaction to HAVN API.

```python
client.transactions.send(
    amount: int,
    referral_code: Optional[str] = None,
    promo_code: Optional[str] = None,
    currency: str = "USD",
    customer_type: str = "NEW_CUSTOMER",
    **kwargs
) -> TransactionResponse
```

**Parameters:**
- `amount` (int): Transaction amount in cents (required)
- `referral_code` (str, optional): Associate referral code
- `promo_code` (str, optional): Voucher code
- `currency` (str): Currency code (default: USD)
- `customer_type` (str): NEW_CUSTOMER or RECURRING (default: NEW_CUSTOMER)
- `subtotal_transaction` (int, optional): Original amount before discount
- `acquisition_method` (str, optional): VOUCHER, REFERRAL, or REFERRAL_VOUCHER
- `custom_fields` (dict, optional): Custom metadata (max 3 entries)
- `invoice_id` (str, optional): External invoice ID
- `customer_id` (str, optional): External customer ID
- `customer_email` (str, optional): Customer email
- `transaction_type` (str, optional): Transaction type
- `description` (str, optional): Transaction description
- `payment_gateway_transaction_id` (str, optional): Payment gateway transaction ID
- `is_recurring` (bool, optional): Whether transaction is recurring

**Returns:** `TransactionResponse`

**Raises:**
- `HAVNValidationError`: If validation fails
- `HAVNAPIError`: If API request fails

---

### UserSyncWebhook

Handler for user synchronization webhooks.

#### sync()

Sync user data to HAVN API.

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

**Parameters:**
- `email` (str): User email (required)
- `name` (str): User full name (required)
- `google_id` (str, optional): Google OAuth ID
- `picture` (str, optional): Profile picture URL
- `avatar` (str, optional): Avatar URL
- `upline_code` (str, optional): Upline associate referral code
- `referral_code` (str, optional): Referral code for associate creation
- `country_code` (str, optional): Country code (2 letters, ISO 3166-1 alpha-2)
- `create_associate` (bool): Whether to create associate (default: True)

**Returns:** `UserSyncResponse`

**Raises:**
- `HAVNValidationError`: If validation fails
- `HAVNAPIError`: If API request fails

---

### VoucherWebhook

Handler for voucher validation.

#### validate()

Validate voucher code.

```python
client.vouchers.validate(
    voucher_code: str,
    amount: Optional[int] = None,
    currency: Optional[str] = None,
) -> bool
```

**Parameters:**
- `voucher_code` (str): Voucher code to validate (required)
- `amount` (int, optional): Transaction amount in cents
- `currency` (str, optional): Currency code

**Returns:** `bool` - True if voucher is valid

**Raises:**
- `HAVNValidationError`: If validation fails
- `HAVNAPIError`: If voucher is invalid (404, 400, 422)

---

## Models

### TransactionResponse

Response from transaction webhook.

**Attributes:**
- `success` (bool): Whether request was successful
- `message` (str): Response message
- `transaction` (TransactionData): Transaction data
- `commissions` (List[CommissionData]): Commission data
- `raw_response` (dict): Raw response dictionary

### UserSyncResponse

Response from user sync webhook.

**Attributes:**
- `success` (bool): Whether request was successful
- `message` (str): Response message
- `user_created` (bool): Whether user was created (vs updated)
- `associate_created` (bool): Whether associate was created
- `user` (UserData): User data
- `associate` (AssociateData, optional): Associate data
- `raw_response` (dict): Raw response dictionary

---

## Exceptions

### HAVNError

Base exception for all HAVN SDK errors.

### HAVNAPIError

Exception raised for API errors.

**Attributes:**
- `message` (str): Error message
- `status_code` (int, optional): HTTP status code
- `response` (dict, optional): Response data

### HAVNAuthError

Exception raised for authentication errors.

### HAVNValidationError

Exception raised for validation errors.

**Attributes:**
- `message` (str): Error message
- `errors` (dict): Validation errors

### HAVNNetworkError

Exception raised for network errors.

**Attributes:**
- `message` (str): Error message
- `original_error` (Exception, optional): Original exception

---

## Utilities

### calculate_hmac_signature()

Calculate HMAC-SHA256 signature.

```python
from havn.utils import calculate_hmac_signature

signature = calculate_hmac_signature(payload, secret)
```

### validate_amount()

Validate transaction amount.

```python
from havn.utils import validate_amount

validate_amount(10000)  # OK
validate_amount(-100)   # Raises ValueError
```

### validate_email()

Validate email format.

```python
from havn.utils import validate_email

validate_email("user@example.com")  # OK
validate_email("invalid")           # Raises ValueError
```

### validate_currency()

Validate currency code.

```python
from havn.utils import validate_currency

validate_currency("USD")  # OK
validate_currency("XYZ")  # Raises ValueError
```
