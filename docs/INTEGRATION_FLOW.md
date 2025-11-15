# Integration Flow Guide - Using HAVN SDK

Panduan lengkap untuk mengintegrasikan aplikasi SaaS Anda dengan HAVN menggunakan Python SDK, mulai dari project creation hingga transaction processing.

## Daftar Isi

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Complete Integration Flow](#complete-integration-flow)
  - [1. Project Creation](#1-project-creation)
  - [2. User Sync ke HAVN](#2-user-sync-ke-havn)
  - [3. Payment/Transaction](#3-paymenttransaction)
  - [4. Referral Project Lain](#4-referral-project-lain)
- [Complete Code Examples](#complete-code-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

Integration Flow adalah alur lengkap bagaimana aplikasi SaaS Anda terintegrasi dengan HAVN platform menggunakan Python SDK. Flow ini mencakup:

1. **Project Creation** - Membuat project dengan optional upline referral code
2. **User Sync** - Sinkronisasi user ke HAVN untuk mendapatkan referral code
3. **Transaction Processing** - Mengirim transaksi ke HAVN untuk commission distribution
4. **Referral Management** - Mengelola referral relationship antar project

### Flow Diagram

```
┌─────────────────┐
│ 1. Project      │
│ Creation        │
│ (optional       │
│  upline_code)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. User Sync    │
│ (SDK returns    │
│  referral_code) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Save         │
│ referral_code   │
│ ke Database     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Payment/     │
│ Transaction     │
│ (use upline_    │
│  referral_code) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. Commission   │
│ Distributed     │
└─────────────────┘
```

---

## Prerequisites

### Installation

```bash
pip install havn-sdk
```

### Credentials

Anda memerlukan credentials dari HAVN Dashboard:

1. **API Key** - Untuk autentikasi
2. **Webhook Secret** - Untuk HMAC signature

**Cara Mendapatkan**:

1. Login ke HAVN Dashboard
2. Navigate ke Settings > API Keys
3. Create new API key atau copy existing key
4. Simpan **API Key** dan **Webhook Secret**

### Setup Client

```python
from havn import HAVNClient
import os

# Initialize SDK client
client = HAVNClient(
    api_key=os.getenv('HAVN_API_KEY'),
    webhook_secret=os.getenv('HAVN_WEBHOOK_SECRET')
)
```

**Atau menggunakan environment variables**:

```bash
# .env file
HAVN_API_KEY=your_api_key_here
HAVN_WEBHOOK_SECRET=your_webhook_secret_here
```

```python
from havn import HAVNClient
from dotenv import load_dotenv

load_dotenv()

# Otomatis membaca dari environment
client = HAVNClient()
```

---

## Complete Integration Flow

### 1. Project Creation

**Deskripsi:**
Admin membuat project baru dengan optional `upline_referral_code`. Pada tahap ini, project belum memiliki `referral_code` sendiri (akan di-generate oleh HAVN setelah user sync).

**Langkah-langkah:**

1. Buat project di database Anda
2. Jika project ini direferensikan oleh project lain, simpan `upline_referral_code`
3. Project dibuat **tanpa** `referral_code` (akan di-generate di step 2)

**Contoh Implementasi:**

```python
# 1. Project Creation (Internal Database)
# Ini adalah contoh untuk database/models Anda sendiri
class Project:
    def __init__(self, project_name, upline_referral_code=None):
        self.project_name = project_name
        self.upline_referral_code = upline_referral_code
        self.referral_code = None  # Belum ada, akan di-generate di step 2

# Admin membuat project baru
project = Project(
    project_name="ShopEasy Platform",
    upline_referral_code="HAVN-MJ-001"  # Optional: jika ada upline
)

# Simpan ke database (contoh)
# project.save()
```

**Catatan Penting:**

- ✅ `upline_referral_code` adalah **optional**
- ✅ Project bisa dibuat tanpa upline (direct project)
- ❌ `referral_code` belum ada di tahap ini
- ✅ `referral_code` akan di-generate oleh HAVN setelah user sync

---

### 2. User Sync ke HAVN

**Deskripsi:**
Sync user (project owner) ke HAVN menggunakan SDK. HAVN akan mengembalikan `referral_code` untuk project ini yang kemudian disimpan ke database.

**Langkah-langkah:**

1. Gunakan SDK untuk sync user ke HAVN
2. HAVN akan return `referral_code` unik
3. Simpan `referral_code` ke project database

**Contoh Implementasi:**

```python
from havn import HAVNClient
import os

# Initialize SDK client
client = HAVNClient(
    api_key=os.getenv('HAVN_API_KEY'),
    webhook_secret=os.getenv('HAVN_WEBHOOK_SECRET')
)

# Sync user ke HAVN dengan role "owner"
result = client.users.sync(
    email="owner@shopeasy.com",
    name="John Doe",
    is_owner=True,  # Set role sebagai "owner"
    upline_code=project.upline_referral_code  # "HAVN-MJ-001" jika ada
)

# HAVN return referral_code
referral_code = result.referral_code  # Contoh: "HAVN-SE-002"
print(f"Project referral_code: {referral_code}")

# Simpan referral_code ke project
project.referral_code = referral_code
# project.save()
```

**Response dari SDK:**

```python
# result object structure
print(result.referral_code)  # "HAVN-SE-002"
print(result.user_id)        # "usr_456"
print(result.success)        # True
print(result.message)        # "User synced successfully"
```

**Error Handling:**

```python
from havn import HAVNClient, HAVNError

try:
    result = client.users.sync(
        email="owner@shopeasy.com",
        name="John Doe",
        is_owner=True,  # Set role sebagai "owner"
        upline_code=project.upline_referral_code
    )
    project.referral_code = result.referral_code
    project.save()

except HAVNError as e:
    print(f"HAVN API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    # Handle error: retry, log, notify admin, etc.

except Exception as e:
    print(f"Unexpected error: {e}")
```

**Bulk User Sync (Sync Multiple Users dalam Project):**

Jika project memiliki multiple users yang perlu di-sync ke associate yang sama:

```python
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

# Step 1: Sync project owner (create associate baru dengan role "owner")
owner_result = client.users.sync(
    email="owner@shopeasy.com",
    name="John Doe",
    is_owner=True,  # Set role sebagai "owner"
    upline_code=project.upline_referral_code,
    create_associate=True
)

# Simpan referral_code project
project.referral_code = owner_result.associate.referral_code if owner_result.associate else None
project.save()

# Step 2: Sync team members ke associate yang sama (bulk) dengan role "partner"
if project.referral_code:
    team_members = [
        {"email": "admin@shopeasy.com", "name": "Jane Smith"},
        {"email": "manager@shopeasy.com", "name": "Bob Johnson"},
        {"email": "support@shopeasy.com", "name": "Alice Brown"},
    ]

    team_result = client.users.sync_bulk(
        users=team_members,
        referral_code=project.referral_code,  # Link semua ke associate project
        is_owner=False  # Semua team members jadi "partner" (default)
    )

    print(f"Team members synced: {team_result.summary.success}/{team_result.summary.total}")
    # Owner punya role "owner", team members punya role "partner"
    if team_result.errors:
        print(f"Errors: {len(team_result.errors)}")
        for error in team_result.errors:
            print(f"  - {error['email']}: {error['error']}")
```

**Batch Processing untuk Large Projects:**

Untuk project dengan banyak users (>50), gunakan batch processing:

```python
# Batch pertama - sync owner dan initial team
batch1_users = [
    {"email": "owner@shopeasy.com", "name": "John Doe", "is_owner": True},  # Owner
    {"email": "admin@shopeasy.com", "name": "Jane Smith"},  # Partner
    # ... max 50 users
]

batch1_result = client.users.sync_bulk(
    users=batch1_users,
    upline_code=project.upline_referral_code
)

# Simpan referral_code untuk batch berikutnya
project.referral_code = batch1_result.referral_code
project.save()

# Batch kedua - link users ke associate yang sama
if project.referral_code:
    batch2_users = [
        {"email": "user51@shopeasy.com", "name": "User 51"},
        {"email": "user52@shopeasy.com", "name": "User 52"},
        # ... max 50 users
    ]

    batch2_result = client.users.sync_bulk(
        users=batch2_users,
        referral_code=project.referral_code  # Link ke associate dari batch 1
    )

    print(f"Batch 2: {batch2_result.summary.success} users linked")
```

**Catatan Penting:**

- ✅ `upline_code` harus dikirim jika project memiliki upline
- ✅ HAVN akan generate `referral_code` unik untuk project ini
- ✅ `referral_code` harus disimpan ke database untuk digunakan di tahap selanjutnya
- ✅ `referral_code` digunakan sebagai identifier project di HAVN
- ✅ **Multiple users bisa di-link ke associate yang sama** menggunakan `referral_code`
- ✅ **Bulk sync** mendukung max 50 users per batch (configurable via `USER_SYNC_BULK_MAX_SIZE`)
- ✅ **Batch processing** bisa digunakan untuk sync banyak users dengan referral_code dari batch sebelumnya
- ✅ **`is_owner` flag** untuk set role "owner" (default: "partner") - berguna untuk project owner
- ✅ **Rate limiting** aktif untuk semua endpoints dengan per-endpoint limits (lihat Troubleshooting section)
- ✅ **`HAVNRateLimitError`** exception untuk proper rate limit handling dengan detailed info (retry_after, limit, remaining)

---

### 3. Payment/Transaction

**Deskripsi:**
Saat payment/subscription berhasil, gunakan SDK untuk mengirim transaction ke HAVN dengan `referral_code=upline_referral_code`. Commission akan didistribusikan ke upline yang mereferensikan project ini.

**Langkah-langkah:**

1. Customer melakukan payment/subscription
2. Payment berhasil (confirmed)
3. Gunakan SDK untuk kirim transaction ke HAVN dengan `upline_referral_code`
4. HAVN memproses transaction dan distribusikan commission ke upline

**Contoh Implementasi:**

```python
from havn import HAVNClient, HAVNError

# Initialize SDK client
client = HAVNClient(
    api_key=os.getenv('HAVN_API_KEY'),
    webhook_secret=os.getenv('HAVN_WEBHOOK_SECRET')
)

# Saat customer melakukan payment berhasil
def process_payment(payment):
    if payment.status == 'completed':
        try:
            # Ambil upline_referral_code dari project
            upline_code = payment.project.upline_referral_code

            # Kirim transaction ke HAVN menggunakan SDK
            result = client.transactions.send(
                amount=payment.amount_cents,  # $1000.00 = 100000 cents
                currency=payment.currency,     # "USD"
                invoice_id=payment.invoice_number,
                customer_id=str(payment.customer_id),
                referral_code=upline_code,  # Gunakan upline_referral_code!
                transaction_type="NEW_CUSTOMER",  # atau "RECURRING"
                promo_code=payment.voucher_code,  # Optional
                custom_fields={
                    'order_id': str(payment.order_id),
                    'payment_method': payment.payment_method,
                }
            )

            # Simpan transaction ID untuk reference
            payment.havn_transaction_id = result.transaction.transaction_id
            payment.havn_synced = True
            payment.save()

            print(f"Transaction sent: {result.transaction.transaction_id}")
            print(f"Commission distributed: {result.commission_distributed}")

            return result

        except HAVNError as e:
            # Log error but don't block payment
            print(f"HAVN integration error: {e.message}")
            # Retry mechanism bisa ditambahkan di sini
            return None
```

**Response dari SDK:**

```python
# Access transaction details
print(result.transaction.transaction_id)  # "txn_abc123"
print(result.transaction.amount)          # 100000 (cents)
print(result.transaction.status)          # "success"
print(result.commission_distributed)      # True

# Access commission breakdown (if available)
for commission in result.commissions:
    print(f"Level {commission.level}: ${commission.amount / 100:.2f} ({commission.percentage}%)")
```

**Catatan Penting:**

- ✅ **Currency Conversion** - SDK dapat auto-convert non-USD amounts ke USD cents (backend akan verify dengan exact match)
- ✅ **Backend Verification** - Backend selalu verify conversion dengan recalculate server-side (security requirement)
- ✅ **Exact Match Required** - Amount harus match exact (no tolerance) dengan backend calculation
- ✅ **Transaction Failed** - Jika conversion mismatch, transaction akan di-mark sebagai `FAILED`
- ✅ **Server Authoritative** - Server exchange rate digunakan untuk final calculation
- ✅ **Audit Trail** - Original amounts dan exchange rates disimpan di `custom_fields` untuk audit
- ✅ **HAVN vs Local Vouchers** - Hanya HAVN vouchers (code starts with "HAVN-") yang dikirim ke transaction API
- ✅ **Local Vouchers** - Local vouchers tidak dikirim ke transaction API, hanya `referral_code` yang dikirim

**Transaction dengan Voucher:**

```python
# Transaction dengan HAVN voucher (both referral_code dan promo_code sent)
result = client.transactions.send(
    amount=80000,  # $800.00 (setelah diskon)
    referral_code="HAVN-MJ-001",
    promo_code="HAVN-AQNEO-S08-ABC123",  # HAVN voucher - akan dikirim
    currency="USD"
)

# Transaction dengan local voucher (hanya referral_code sent)
result = client.transactions.send(
    amount=80000,  # $800.00 (setelah diskon)
    subtotal_transaction=100000,  # $1000.00 (sebelum diskon)
    currency="USD",
    referral_code=upline_code,
    promo_code="SUMMER2024",  # Voucher code
    transaction_type="NEW_CUSTOMER"
)
```

**Recurring Transaction:**

```python
# Subscription/recurring transaction
result = client.transactions.send(
    amount=50000,  # $500.00 monthly
    currency="USD",
    referral_code=upline_code,
    transaction_type="RECURRING",
    is_recurring=True,
    description="Monthly subscription"
)
```

**Catatan Penting:**

- ⚠️ **PENTING:** Gunakan `upline_referral_code` sebagai `referral_code` di transaction, **BUKAN** `referral_code` project sendiri!
- ✅ Commission akan masuk ke upline yang mereferensikan project ini
- ✅ Jika tidak ada upline (`upline_referral_code` null), commission masuk ke platform revenue
- ✅ Transaction harus dikirim setelah payment confirmed/success
- ✅ SDK akan handle HMAC signature dan retry logic secara otomatis
- ✅ **Currency Conversion** - SDK dapat auto-convert non-USD amounts ke USD cents (backend akan verify dengan exact match)
- ✅ **Backend Verification** - Backend selalu verify conversion dengan recalculate server-side (security requirement)
- ✅ **Exact Match Required** - Amount harus match exact (no tolerance) dengan backend calculation
- ✅ **Transaction Failed** - Jika conversion mismatch, transaction akan di-mark sebagai `FAILED`
- ✅ **Server Authoritative** - Server exchange rate digunakan untuk final calculation
- ✅ **Audit Trail** - Original amounts dan exchange rates disimpan di `custom_fields` untuk audit
- ✅ **HAVN vs Local Vouchers** - Hanya HAVN vouchers (code starts with "HAVN-") yang dikirim ke transaction API
- ✅ **Local Vouchers** - Local vouchers tidak dikirim ke transaction API, hanya `referral_code` yang dikirim

**Mengapa Menggunakan Upline Referral Code?**

```
Project A (referral_code: HAVN-A-001)
    │
    │ (menggunakan upline_referral_code: HAVN-B-001)
    ▼
Project B (referral_code: HAVN-B-001)
    │
    │ (mendapatkan commission dari transaksi Project A)
    ▼
Transaction dari Project A → Commission ke Project B
```

---

### 4. Referral Project Lain

**Deskripsi:**
Project ini bisa mereferensikan project lain dengan menggunakan `referral_code` project ini sebagai `upline_referral_code` untuk project baru.

**Langkah-langkah:**

1. Project A ingin mereferensikan Project B
2. Saat Project B dibuat, gunakan `referral_code` dari Project A sebagai `upline_referral_code`
3. Ketika Project B melakukan transaction, commission akan masuk ke Project A

**Contoh Implementasi:**

```python
from havn import HAVNClient, HAVNError

client = HAVNClient(
    api_key=os.getenv('HAVN_API_KEY'),
    webhook_secret=os.getenv('HAVN_WEBHOOK_SECRET')
)

# ============================================
# Project A sudah ada
# ============================================
project_a = Project.objects.get(id=1)
# project_a.referral_code = "HAVN-A-001" (sudah ada dari step 2)

# ============================================
# Admin membuat Project B dan mereferensikan Project A
# ============================================
project_b = Project.objects.create(
    project_name="New SaaS Platform",
    upline_referral_code=project_a.referral_code  # "HAVN-A-001"
)

# ============================================
# Sync Project B user ke HAVN
# ============================================
owner_b = User.objects.get(project_id=project_b.id, role='owner')

try:
    result = client.users.sync(
        email=owner_b.email,
        name=owner_b.name,
        is_owner=True,  # Set role sebagai "owner"
        upline_code=project_b.upline_referral_code  # "HAVN-A-001"
    )

    # HAVN return referral_code untuk Project B
    project_b.referral_code = result.referral_code  # "HAVN-B-002"
    project_b.save()

    print(f"Project B referral_code: {project_b.referral_code}")
    print(f"Project B upline: {project_b.upline_referral_code}")

except HAVNError as e:
    print(f"Error syncing Project B: {e.message}")

# ============================================
# Ketika Project B melakukan transaction
# ============================================
# Transaction dari Project B akan menggunakan upline_referral_code
payment_from_b = Payment.objects.create(
    project_id=project_b.id,
    amount_cents=50000,
    currency="USD",
    status="completed"
)

result = client.transactions.send(
    amount=payment_from_b.amount_cents,
    currency=payment_from_b.currency,
    referral_code=project_b.upline_referral_code,  # "HAVN-A-001"
    # Commission akan masuk ke Project A
)

print(f"Commission distributed to Project A: {project_b.upline_referral_code}")
```

**Hierarchy Example:**

```
                    Project A (HAVN-A-001)
                           │
                           │ upline_referral_code: HAVN-A-001
                           ▼
                    Project B (HAVN-B-002)
                    │                           │
                    │ upline_referral_code     │ upline_referral_code
                    │ HAVN-B-002               │ HAVN-B-002
                    ▼                           ▼
            Project C (HAVN-C-003)     Project D (HAVN-D-004)
```

**Catatan Penting:**

- ✅ Project bisa memiliki multiple downline projects
- ✅ Setiap downline project menggunakan `referral_code` dari upline sebagai `upline_referral_code`
- ✅ Commission dari downline akan masuk ke upline
- ✅ Hierarki bisa lebih dari 2 level (A → B → C → D ...)

---

## Complete Code Examples

### Complete Integration Flow (Django Example)

```python
# models.py
from django.db import models

class Project(models.Model):
    project_name = models.CharField(max_length=255)
    upline_referral_code = models.CharField(max_length=50, null=True, blank=True)
    referral_code = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class User(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    email = models.EmailField()
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50)

class Payment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount_cents = models.IntegerField()
    currency = models.CharField(max_length=3)
    invoice_number = models.CharField(max_length=100)
    customer_id = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    havn_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

```python
# services/havn_service.py
from havn import HAVNClient, HAVNError
import os
import logging

logger = logging.getLogger(__name__)

class HAVNService:
    def __init__(self):
        self.client = HAVNClient(
            api_key=os.getenv('HAVN_API_KEY'),
            webhook_secret=os.getenv('HAVN_WEBHOOK_SECRET')
        )

    def sync_project_user(self, project, owner_email, owner_name):
        """
        Step 2: Sync project owner ke HAVN dan dapatkan referral_code
        """
        try:
            result = self.client.users.sync(
                email=owner_email,
                name=owner_name,
                is_owner=True,  # Set role sebagai "owner"
                upline_code=project.upline_referral_code
            )

            # Simpan referral_code ke project
            project.referral_code = result.referral_code
            project.save()

            logger.info(f"Project {project.id} synced with referral_code: {result.referral_code}")
            return result

        except HAVNError as e:
            logger.error(f"HAVN sync error for project {project.id}: {e.message}")
            raise

    def send_transaction(self, payment):
        """
        Step 3: Kirim transaction ke HAVN saat payment berhasil
        """
        if payment.status != 'completed':
            raise ValueError("Payment must be completed before sending to HAVN")

        try:
            # Ambil upline_referral_code dari project
            upline_code = payment.project.upline_referral_code

            result = self.client.transactions.send(
                amount=payment.amount_cents,
                currency=payment.currency,
                invoice_id=payment.invoice_number,
                customer_id=str(payment.customer_id),
                referral_code=upline_code,  # Gunakan upline!
                transaction_type="NEW_CUSTOMER",
                promo_code=getattr(payment, 'voucher_code', None),
                custom_fields={
                    'payment_id': str(payment.id),
                    'project_id': str(payment.project.id),
                }
            )

            # Simpan transaction ID
            payment.havn_transaction_id = result.transaction.transaction_id
            payment.save()

            logger.info(f"Transaction sent to HAVN: {result.transaction.transaction_id}")
            return result

        except HAVNError as e:
            logger.error(f"HAVN transaction error for payment {payment.id}: {e.message}")
            # Don't raise - log error but don't block payment
            return None
```

```python
# views.py atau tasks.py
from .models import Project, User, Payment
from .services.havn_service import HAVNService

havn_service = HAVNService()

# ============================================
# Step 1: Project Creation (by Admin)
# ============================================
def create_project(project_name, upline_referral_code=None):
    project = Project.objects.create(
        project_name=project_name,
        upline_referral_code=upline_referral_code,
        referral_code=None  # Belum ada
    )
    return project

# ============================================
# Step 2: User Sync (after project created)
# ============================================
def sync_project_to_havn(project_id, owner_email, owner_name):
    project = Project.objects.get(id=project_id)

    # Sync user ke HAVN dengan role "owner"
    result = havn_service.sync_project_user(project, owner_email, owner_name)

    # project.referral_code sudah di-update di havn_service
    return project

# ============================================
# Step 3: Payment Processing
# ============================================
def process_payment(payment_id):
    payment = Payment.objects.get(id=payment_id)

    if payment.status == 'completed':
        # Kirim ke HAVN
        havn_result = havn_service.send_transaction(payment)

        if havn_result:
            print(f"Transaction sent: {havn_result.transaction.transaction_id}")
        else:
            print("Failed to send transaction to HAVN (check logs)")

    return payment

# ============================================
# Step 4: Refer New Project
# ============================================
def refer_new_project(existing_project_id, new_project_name, new_owner_email, new_owner_name):
    existing_project = Project.objects.get(id=existing_project_id)

    # Buat project baru dengan upline_referral_code
    new_project = Project.objects.create(
        project_name=new_project_name,
        upline_referral_code=existing_project.referral_code
    )

    # Sync new project user
    result = havn_service.sync_project_user(new_project, new_owner_email, new_owner_name)

    return new_project
```

### Complete Integration Flow (Flask Example)

```python
# app.py
from flask import Flask, request, jsonify
from havn import HAVNClient, HAVNError
import os

app = Flask(__name__)

# Initialize SDK client
havn_client = HAVNClient(
    api_key=os.getenv('HAVN_API_KEY'),
    webhook_secret=os.getenv('HAVN_WEBHOOK_SECRET')
)

# Database models (simplified)
projects_db = {}
payments_db = {}

# ============================================
# Step 1: Project Creation
# ============================================
@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    project_id = len(projects_db) + 1

    project = {
        'id': project_id,
        'project_name': data['project_name'],
        'upline_referral_code': data.get('upline_referral_code'),
        'referral_code': None  # Belum ada
    }

    projects_db[project_id] = project
    return jsonify(project), 201

# ============================================
# Step 2: User Sync
# ============================================
@app.route('/api/projects/<int:project_id>/sync', methods=['POST'])
def sync_project(project_id):
    project = projects_db.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    data = request.json

    try:
        result = havn_client.users.sync(
            email=data['email'],
            name=data['name'],
            upline_code=project['upline_referral_code'],
            project_id=str(project_id)
        )

        # Update project dengan referral_code
        project['referral_code'] = result.referral_code
        projects_db[project_id] = project

        return jsonify({
            'success': True,
            'referral_code': result.referral_code
        })

    except HAVNError as e:
        return jsonify({'error': e.message}), 400

# ============================================
# Step 3: Payment/Transaction
# ============================================
@app.route('/api/payments', methods=['POST'])
def create_payment():
    data = request.json
    payment_id = len(payments_db) + 1
    project_id = data['project_id']

    project = projects_db.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    payment = {
        'id': payment_id,
        'project_id': project_id,
        'amount_cents': data['amount_cents'],
        'currency': data['currency'],
        'status': data.get('status', 'pending'),
        'havn_transaction_id': None
    }

    payments_db[payment_id] = payment

    # Jika payment completed, kirim ke HAVN
    if payment['status'] == 'completed':
        try:
            result = havn_client.transactions.send(
                amount=payment['amount_cents'],
                currency=payment['currency'],
                invoice_id=data.get('invoice_id'),
                customer_id=str(data.get('customer_id')),
                referral_code=project['upline_referral_code'],  # Gunakan upline!
                transaction_type="NEW_CUSTOMER"
            )

            payment['havn_transaction_id'] = result.transaction.transaction_id
            payments_db[payment_id] = payment

        except HAVNError as e:
            # Log error but don't block
            print(f"HAVN error: {e.message}")

    return jsonify(payment), 201

if __name__ == '__main__':
    app.run(debug=True)
```

---

## Best Practices

### 1. Error Handling

```python
from havn import HAVNClient, HAVNError
import logging

logger = logging.getLogger(__name__)

def safe_sync_user(client, email, name, upline_code, project_id):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = client.users.sync(
                email=email,
                name=name,
                upline_code=upline_code,
                project_id=project_id
            )
            return result

        except HAVNRateLimitError as e:
            # Rate limit exceeded dengan detailed info
            wait_time = e.retry_after or (2 ** attempt)
            time.sleep(wait_time)
            continue
        except HAVNError as e:
            logger.error(f"HAVN sync error: {e.message}")
            raise
```

### 2. Async Processing

```python
# Gunakan background task untuk transaction processing
from celery import Celery

celery_app = Celery('tasks')

@celery_app.task
def send_transaction_to_havn(payment_id):
    """Send transaction to HAVN in background"""
    payment = Payment.objects.get(id=payment_id)
    havn_service.send_transaction(payment)

# Di payment view
if payment.status == 'completed':
    send_transaction_to_havn.delay(payment.id)  # Async
```

### 3. Transaction Logging

```python
import logging

logger = logging.getLogger('havn_integration')

def send_transaction_with_logging(client, payment):
    logger.info(f"Attempting to send payment {payment.id} to HAVN")

    try:
        result = client.transactions.send(...)
        logger.info(f"Transaction {result.transaction.transaction_id} sent successfully")
        return result

    except HAVNError as e:
        logger.error(f"HAVN error for payment {payment.id}: {e.message}")
        raise
```

### 4. Validation

```python
def validate_referral_code(referral_code):
    """Validate referral code format before using"""
    if not referral_code:
        return False
    if not referral_code.startswith('HAVN-'):
        return False
    return True

# Before sending transaction
if payment.project.upline_referral_code:
    if not validate_referral_code(payment.project.upline_referral_code):
        logger.warning(f"Invalid upline_referral_code for project {payment.project.id}")
```

---

## Troubleshooting

### Issue: Referral Code Not Generated

**Problem:** `referral_code` tetap `null` setelah user sync.

**Solution:**

- Pastikan API key dan webhook secret valid
- Check error response dari HAVN
- Pastikan user data (email, name) valid
- Pastikan `upline_code` valid (jika ada)

```python
try:
    result = client.users.sync(...)
    if not result.referral_code:
        raise ValueError("Referral code not returned from HAVN")
except HAVNError as e:
    print(f"Error: {e.message}, Status: {e.status_code}")
```

### Issue: Commission Not Distributed

**Problem:** Transaction terkirim tapi commission tidak didistribusikan.

**Solution:**

- Pastikan menggunakan `upline_referral_code` sebagai `referral_code` di transaction
- Pastikan upline project valid dan active
- Check commission distribution status di response

```python
result = client.transactions.send(...)
print(f"Commission distributed: {result.commission_distributed}")
```

### Issue: Rate Limit Errors

**Problem:** Mendapatkan 429 (Rate Limit) error.

**Solution:**

- Use `HAVNRateLimitError` untuk proper handling dengan detailed info
- Implement exponential backoff
- Use async processing
- Batch requests jika memungkinkan (gunakan bulk sync)
- Monitor rate limit headers

```python
from havn import HAVNRateLimitError
import time

def send_with_backoff(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.transactions.send(...)
        except HAVNRateLimitError as e:
            # Rate limit exceeded dengan detailed info
            print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
            print(f"Limit: {e.limit}, Remaining: {e.remaining}")

            # Wait sesuai retry_after atau use exponential backoff
            wait_time = e.retry_after or (2 ** attempt)
            time.sleep(wait_time)
            continue
        except HAVNError as e:
            # Other HAVN errors
            raise
```

**Best Practices:**

- Gunakan bulk sync untuk mengurangi jumlah requests
- Monitor rate limit headers (X-RateLimit-\*) di setiap response
- Implement proper retry logic dengan exponential backoff

````

### Issue: Invalid Signature Error

**Problem:** Mendapatkan 401 (Unauthorized) error.

**Solution:**
- Pastikan webhook secret benar
- Pastikan tidak ada whitespace di API key atau secret
- Check SDK version (update jika perlu)

```python
# Verify credentials
print(f"API Key: {os.getenv('HAVN_API_KEY')[:10]}...")
print(f"Secret: {os.getenv('HAVN_WEBHOOK_SECRET')[:10]}...")
````

---

**Last Updated:** 2024  
**SDK Version:** 1.0.0
