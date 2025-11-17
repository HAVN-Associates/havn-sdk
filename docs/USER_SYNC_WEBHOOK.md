# User Sync Webhook

Dokumentasi untuk UserSyncWebhook - Sync user data dari SaaS company ke HAVN.

## Daftar Isi

- [Overview](#overview)
- [Method: sync()](#method-sync)
- [Method: sync_bulk()](#method-sync_bulk)
- [Parameters](#parameters)
- [Response](#response)
- [Contoh Penggunaan](#contoh-penggunaan)

---

## Overview

`UserSyncWebhook` menyediakan method untuk sync user data dari SaaS company (via Google OAuth atau source lain) ke HAVN dengan automatic associate creation.

**Key Features:**
- ✅ Single user sync
- ✅ Bulk user sync (multiple users)
- ✅ Automatic associate creation dengan referral code
- ✅ Role management (owner vs partner)
- ✅ Upline hierarchy management
- ✅ Avatar/picture sync dari Google OAuth
- ✅ Country code support

---

## Method: sync()

Sync single user ke HAVN.

### Signature

```python
def sync(
    email: str,
    name: str,
    google_id: Optional[str] = None,
    picture: Optional[str] = None,
    avatar: Optional[str] = None,
    upline_code: Optional[str] = None,
    referral_code: Optional[str] = None,
    country_code: Optional[str] = None,
    create_associate: bool = True,
    is_owner: bool = False
) -> UserSyncResponse
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `email` | `str` | Yes | - | Email address user |
| `name` | `str` | Yes | - | Nama lengkap user |
| `google_id` | `str` | No | None | Google OAuth ID |
| `picture` | `str` | No | None | URL foto profil (Google) |
| `avatar` | `str` | No | None | URL avatar (custom) |
| `upline_code` | `str` | No | None | Referral code upline (HAVN-XX-XXX) |
| `referral_code` | `str` | No | None | Referral code untuk user ini (custom) |
| `country_code` | `str` | No | None | Country code (ISO 3166-1 alpha-2) |
| `create_associate` | `bool` | No | True | Create associate dengan referral code |
| `is_owner` | `bool` | No | False | True = owner role, False = partner role |

### Parameter Details

#### is_owner
- **Type**: `bool`
- **Default**: `False`
- **Impact**:
  - `True` → Role: "owner" (project owner)
  - `False` → Role: "partner" (regular associate)

#### create_associate
- **Type**: `bool`
- **Default**: `True`
- **Impact**:
  - `True` → Create associate dengan referral code auto-generated
  - `False` → Hanya create user, tidak create associate

### Response

```python
@dataclass
class UserSyncResponse:
    user: User
    associate: Optional[Associate]
    user_created: bool
    associate_created: bool
    referral_code: Optional[str]
```

---

## Method: sync_bulk()

Sync multiple users sekaligus dalam satu request.

### Signature

```python
def sync_bulk(
    users: List[Dict[str, Any]],
    upline_code: Optional[str] = None,
    referral_code: Optional[str] = None,
    create_associate: bool = True
) -> BulkUserSyncResponse
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `users` | `List[Dict]` | Yes | - | List of user data |
| `upline_code` | `str` | No | None | Upline code untuk semua users |
| `referral_code` | `str` | No | None | Link semua users ke associate ini |
| `create_associate` | `bool` | No | True | Create associate untuk user pertama |

### User Dict Structure

```python
{
    "email": "user@example.com",  # Required
    "name": "John Doe",           # Required
    "google_id": "google123",     # Optional
    "picture": "https://...",     # Optional
    "is_owner": False             # Optional
}
```

### Response

```python
@dataclass
class BulkUserSyncResponse:
    results: List[UserSyncResult]
    summary: BulkSummary
    referral_code: Optional[str]
```

```python
@dataclass
class BulkSummary:
    total: int
    success: int
    failed: int
```

---

## Contoh Penggunaan

### 1. Sync User Basic

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# Sync user dengan minimal data
result = client.users.sync(
    email="user@example.com",
    name="John Doe"
)

print(f"User created: {result.user_created}")
print(f"Associate created: {result.associate_created}")
print(f"Referral code: {result.referral_code}")
```

### 2. Sync dari Google OAuth

```python
# Sync user dengan Google OAuth data
result = client.users.sync(
    email="user@gmail.com",
    name="John Doe",
    google_id="google_oauth_id_123",
    picture="https://lh3.googleusercontent.com/...",
    country_code="US"
)

print(f"Google ID: {result.user.google_id}")
print(f"Picture: {result.user.picture}")
```

### 3. Sync dengan Upline

```python
# Sync user dan link ke upline
result = client.users.sync(
    email="newuser@example.com",
    name="Jane Smith",
    upline_code="HAVN-MJ-001",  # Upline referral code
    create_associate=True
)

print(f"User: {result.user.email}")
print(f"Upline: HAVN-MJ-001")
print(f"Referral code: {result.referral_code}")
```

### 4. Sync Project Owner

```python
# Sync owner dengan role "owner"
result = client.users.sync(
    email="owner@shopeasy.com",
    name="John Doe",
    is_owner=True,  # Set as owner
    upline_code="HAVN-MJ-001"
)

print(f"Role: {result.associate.role}")  # Output: "owner"
```

### 5. Sync User Only (Tanpa Associate)

```python
# Sync user tanpa create associate
result = client.users.sync(
    email="user@example.com",
    name="John Doe",
    create_associate=False  # Tidak create associate
)

print(f"User created: {result.user_created}")
print(f"Associate: {result.associate}")  # Output: None
```

### 6. Bulk User Sync

```python
# Sync multiple users sekaligus
users_data = [
    {
        "email": "owner@shopeasy.com",
        "name": "John Doe",
        "is_owner": True
    },
    {
        "email": "admin@shopeasy.com",
        "name": "Jane Smith"
    },
    {
        "email": "manager@shopeasy.com",
        "name": "Bob Johnson"
    }
]

result = client.users.sync_bulk(
    users=users_data,
    upline_code="HAVN-MJ-001"
)

print(f"Total: {result.summary.total}")
print(f"Success: {result.summary.success}")
print(f"Failed: {result.summary.failed}")
print(f"Referral code: {result.referral_code}")
```

### 7. Bulk Link ke Associate yang Sama

```python
# Step 1: Sync owner dan dapatkan referral code
result1 = client.users.sync_bulk(
    users=[{"email": "owner@example.com", "name": "Owner", "is_owner": True}],
    upline_code="HAVN-MJ-001"
)

owner_code = result1.referral_code
print(f"Owner referral code: {owner_code}")

# Step 2: Link users lain ke owner
result2 = client.users.sync_bulk(
    users=[
        {"email": "user1@example.com", "name": "User 1"},
        {"email": "user2@example.com", "name": "User 2"}
    ],
    referral_code=owner_code  # Link ke owner
)

print(f"Linked {result2.summary.success} users ke {owner_code}")
```

### 8. Error Handling

```python
from havn import HAVNClient, HAVNAPIError, HAVNValidationError

client = HAVNClient(api_key="...", webhook_secret="...")

try:
    result = client.users.sync(
        email="invalid-email",
        name="John Doe"
    )
except HAVNValidationError as e:
    print(f"Validation error: {e}")
except HAVNAPIError as e:
    print(f"API error: {e.message}")
```

### 9. Update Existing User

```python
# Sync akan update jika user sudah ada
result = client.users.sync(
    email="existing@example.com",
    name="Updated Name",
    picture="https://new-picture.jpg",
    country_code="ID"
)

if result.user_created:
    print("User baru dibuat")
else:
    print("User sudah ada, diupdate")
```

---

## Best Practices

### 1. Sync Owner First

```python
# Step 1: Sync owner
owner_result = client.users.sync(
    email="owner@company.com",
    name="Owner Name",
    is_owner=True,
    upline_code="HAVN-MJ-001"
)

owner_code = owner_result.referral_code

# Step 2: Sync team members dengan owner sebagai upline
for member in team_members:
    client.users.sync(
        email=member['email'],
        name=member['name'],
        upline_code=owner_code
    )
```

### 2. Batch Processing

```python
from typing import List, Dict
import time

def sync_users_batch(users: List[Dict], batch_size: int = 50):
    """Sync users dalam batches"""
    results = []
    
    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]
        
        try:
            result = client.users.sync_bulk(
                users=batch,
                upline_code="HAVN-MJ-001"
            )
            results.append(result)
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Batch {i//batch_size + 1} failed: {e}")
    
    return results
```

### 3. Idempotency

```python
# Sync adalah idempotent - aman untuk retry
def sync_with_retry(email: str, name: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return client.users.sync(email=email, name=name)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

### 4. Validation

```python
def validate_user_data(email: str, name: str) -> bool:
    """Validate before syncing"""
    if not email or '@' not in email:
        return False
    if not name or len(name) < 2:
        return False
    return True

if validate_user_data(email, name):
    result = client.users.sync(email=email, name=name)
```

---

## Role Management

### Owner vs Partner

| Aspect | Owner | Partner |
|--------|-------|---------|
| **is_owner** | `True` | `False` |
| **Role** | "owner" | "partner" |
| **Use Case** | Project owner | Team member |
| **Permissions** | Full project access | Limited access |

### Example

```python
# Owner
owner = client.users.sync(
    email="owner@company.com",
    name="Company Owner",
    is_owner=True
)
print(f"Role: {owner.associate.role}")  # "owner"

# Partner
partner = client.users.sync(
    email="partner@company.com",
    name="Team Member",
    is_owner=False  # or omit (default)
)
print(f"Role: {partner.associate.role}")  # "partner"
```

---

## Lihat Juga

- [Auth Webhook](AUTH_WEBHOOK.md)
- [Transaction Webhook](TRANSACTION_WEBHOOK.md)
- [Voucher Webhook](VOUCHER_WEBHOOK.md)
- [Models](MODELS.md)
