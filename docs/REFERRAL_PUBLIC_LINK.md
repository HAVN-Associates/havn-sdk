# Public Referral Link Integration Guide

## 🎯 Konsep Sederhana

HAVN menyediakan **public referral link** yang bekerja seperti **UTM parameters** di marketing link:
- HAVN redirect ke login page Anda **dengan query params** (`?ref=XXX&vc=YYY`)
- SaaS **capture params** → **simpan sementara** → **attach setelah user login**
- **ZERO changes** ke login flow existing Anda

---

## 📊 Flow Overview

```
1. Associate share link
   https://havn.com/r/mycompany?ref=HAVN-MJ-001&vc=DISC50
   
2. HAVN validate & redirect
   → https://saascompany.com/login?ref=HAVN-MJ-001&vc=DISC50
   
3. SaaS capture params → store in session
   
4. User login dengan metode apapun
   (Google OAuth, Email, Facebook, Magic Link, dll)
   
5. After login success → attach referral dari session
   
6. First transaction → auto-apply voucher
```

**Key Point:** Login flow Anda **TIDAK PERLU DIUBAH**, cuma tambah capture params + attach after login!

---

## ⚙️ Setup (One-Time Configuration)

### 1. Konfigurasi di HAVN (Admin Setup)

Hubungi HAVN admin untuk konfigurasi:

```
public_redirect_slug: "mycompany"
public_auth_redirect_url: "https://saascompany.com/login"
                                                   ↑
                                    URL login page existing Anda
```

**Catatan:** `public_auth_redirect_url` langsung ke **login page existing** Anda, bukan OAuth callback!

### 2. Database Schema (SaaS Side)

```sql
-- Add 3 columns ke users table
ALTER TABLE users
ADD COLUMN referral_upline_code VARCHAR(50) NULL 
    COMMENT 'HAVN referral code dari upline associate',
ADD COLUMN voucher_code VARCHAR(50) NULL 
    COMMENT 'HAVN voucher code untuk first transaction',
ADD COLUMN is_first_transaction BOOLEAN DEFAULT true 
    COMMENT 'Flag untuk tracking first transaction';

-- Add indexes untuk performance
CREATE INDEX idx_users_referral_code ON users(referral_upline_code);
CREATE INDEX idx_users_first_transaction ON users(is_first_transaction) 
    WHERE is_first_transaction = true;
```

---

## 💻 Implementation (Minimal Changes)

### Step 1: Capture Query Params di Login Page

**Option A: Backend (Recommended - Server-side Session)**

```python
# Di login page route (Flask/Django/FastAPI)
@app.route("/login")
def login_page():
    """
    Login page - capture referral params dan simpan di session
    """
    # Capture params dari query string
    referral_code = request.args.get('ref')
    voucher_code = request.args.get('vc')
    
    # Simpan ke session (akan persist selama login flow)
    if referral_code:
        session['pending_referral'] = referral_code
        session['pending_voucher'] = voucher_code
        logger.info(f"Referral captured: {referral_code}")
    
    # Render login page seperti biasa (NO CHANGES!)
    return render_template('login.html')
```

**Option B: Frontend (Client-side Storage)**

```javascript
// Di login.html atau login.js
const urlParams = new URLSearchParams(window.location.search);
const refCode = urlParams.get('ref');
const vcCode = urlParams.get('vc');

if (refCode) {
    // Simpan ke sessionStorage (will persist across pages)
    sessionStorage.setItem('pending_referral', refCode);
    sessionStorage.setItem('pending_voucher', vcCode);
    console.log('Referral captured:', refCode);
}
```

**That's it!** User sekarang bisa login dengan metode apapun yang tersedia (Google, Email, Facebook, dll).

---

### Step 2: Helper Function untuk Attach Referral

Buat **1 helper function** yang akan dipanggil dari **semua login handlers**:

```python
def attach_pending_referral(user):
    """
    Universal helper: Attach referral data dari session ke user
    Call this function after ANY successful login method!
    
    Args:
        user: User object (must be saved to DB)
    """
    # Check session untuk pending referral
    pending_ref = session.get('pending_referral')
    
    if pending_ref and not user.referral_upline_code:
        # Attach referral data
        user.referral_upline_code = pending_ref
        user.voucher_code = session.get('pending_voucher')
        user.is_first_transaction = True
        
        # Clear session
        session.pop('pending_referral', None)
        session.pop('pending_voucher', None)
        
        logger.info(f"Referral attached: {user.email} → {pending_ref}")
```

---

### Step 3: Update Login Handlers (Minimal Changes)

Call `attach_pending_referral()` di **semua login handlers**:

#### **Google OAuth Handler**

```python
@app.route("/auth/google/callback")
def google_oauth_callback():
    """Google OAuth callback - standard flow"""
    # Complete OAuth (existing code, NO CHANGES)
    google_user = complete_google_oauth()
    
    # Create or get user (existing code, NO CHANGES)
    user = User.query.filter_by(email=google_user.email).first()
    if not user:
        user = User(email=google_user.email, name=google_user.name)
        db.session.add(user)
    
    # NEW: Attach referral if exists (1 line!)
    attach_pending_referral(user)
    
    # Save and login (existing code, NO CHANGES)
    db.session.commit()
    session['user_id'] = user.id
    return redirect('/dashboard')
```

#### **Email/Password Handler**

```python
@app.route("/auth/email/login", methods=["POST"])
def email_login():
    """Email/Password login"""
    email = request.json['email']
    password = request.json['password']
    
    # Verify credentials (existing code, NO CHANGES)
    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user, password):
        return {"error": "Invalid credentials"}, 401
    
    # NEW: Attach referral if exists (1 line!)
    attach_pending_referral(user)
    
    # Save and login (existing code, NO CHANGES)
    db.session.commit()
    session['user_id'] = user.id
    return {"success": True}
```

#### **Magic Link Handler**

```python
@app.route("/auth/magic-link/verify/<token>")
def verify_magic_link(token):
    """Magic link verification"""
    # Verify token (existing code, NO CHANGES)
    email = verify_token(token)
    
    # Create or get user (existing code, NO CHANGES)
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
    
    # NEW: Attach referral if exists (1 line!)
    attach_pending_referral(user)
    
    # Save and login (existing code, NO CHANGES)
    db.session.commit()
    session['user_id'] = user.id
    return redirect('/dashboard')
```

**Pattern yang sama untuk Facebook OAuth, Twitter, Apple Sign In, dll!**

---

### Step 4: Auto-Apply Voucher pada First Transaction

Gunakan **HAVN SDK existing** untuk validate dan send transaction:

```python
from havn import HAVNClient
import os

# Initialize HAVN client (existing SDK, NO CHANGES)
havn_client = HAVNClient(
    api_key=os.getenv("HAVN_API_KEY"),
    webhook_secret=os.getenv("HAVN_WEBHOOK_SECRET")
)

@app.route("/api/checkout", methods=["POST"])
def checkout():
    """
    Checkout flow dengan auto-apply voucher
    """
    user = User.query.get(session['user_id'])
    amount_cents = request.json['amount']
    currency = request.json.get('currency', 'USD')
    
    discount = 0
    voucher_applied = None
    
    # Check first transaction flag
    if user.is_first_transaction and user.voucher_code:
        try:
            # Validate voucher menggunakan SDK existing (NO NEW METHOD!)
            validation = havn_client.vouchers.validate(
                code=user.voucher_code,
                amount=amount_cents,
                currency=currency
            )
            
            if validation.is_valid:
                # Calculate discount
                voucher = validation.voucher_data
                if voucher.type == "DISCOUNT_PERCENTAGE":
                    discount = int(amount_cents * voucher.value / 100)
                else:
                    discount = voucher.value
                
                discount = min(discount, amount_cents)
                voucher_applied = user.voucher_code
                
                logger.info(f"Voucher applied: {user.voucher_code}, discount: ${discount/100}")
        except Exception as e:
            # Voucher invalid/expired - proceed without discount
            logger.warning(f"Voucher validation failed: {e}")
    
    # Process payment
    final_amount = amount_cents - discount
    payment = process_payment(final_amount, currency, user)
    
    # Send transaction to HAVN menggunakan SDK existing (NO NEW METHOD!)
    try:
        result = havn_client.transactions.send(
            customer_email=user.email,
            amount=amount_cents,  # Original amount sebelum discount
            currency=currency,
            referral_code=user.referral_upline_code,
            promo_code=voucher_applied,  # Only if validated
            payment_gateway_transaction_id=payment.id
        )
        
        logger.info(f"Transaction sent to HAVN: {result.get('transaction_id')}")
    except Exception as e:
        # HAVN webhook failed - log tapi jangan block checkout
        logger.error(f"HAVN transaction webhook failed: {e}")
    
    # Mark first transaction as complete
    if user.is_first_transaction:
        user.is_first_transaction = False
        db.session.commit()
    
    return {
        "success": True,
        "discount": discount,
        "final_amount": final_amount,
        "voucher_applied": voucher_applied
    }
```

---

## 🔄 Complete Flow Example

### Scenario: User Signup via Google OAuth dengan Referral Link

```python
# 1. User clicks: https://havn.com/r/mycompany?ref=HAVN-MJ-001&vc=DISC50

# 2. HAVN redirects: https://saascompany.com/login?ref=HAVN-MJ-001&vc=DISC50

# 3. Login page captures params
@app.route("/login")
def login_page():
    session['pending_referral'] = request.args.get('ref')  # HAVN-MJ-001
    session['pending_voucher'] = request.args.get('vc')    # DISC50
    return render_template('login.html')

# 4. User clicks "Continue with Google" → OAuth flow

# 5. Google callback
@app.route("/auth/google/callback")
def google_callback():
    google_user = complete_google_oauth()
    
    user = User(email=google_user.email, name=google_user.name)
    db.session.add(user)
    
    # Attach referral dari session
    attach_pending_referral(user)  # ← Magic happens here!
    
    db.session.commit()
    return redirect('/dashboard')

# User sekarang punya:
# - referral_upline_code = "HAVN-MJ-001"
# - voucher_code = "DISC50"
# - is_first_transaction = True

# 6. First checkout
@app.route("/api/checkout", methods=["POST"])
def checkout():
    user = User.query.get(session['user_id'])
    
    # Validate voucher
    validation = havn_client.vouchers.validate(
        code=user.voucher_code,  # DISC50
        amount=10000,
        currency="USD"
    )
    
    if validation.is_valid:
        discount = calculate_discount(validation.voucher_data, 10000)
        final_amount = 10000 - discount
    
    # Process payment
    payment = stripe.charge(final_amount)
    
    # Send to HAVN
    havn_client.transactions.send(
        customer_email=user.email,
        amount=10000,
        referral_code=user.referral_upline_code,  # HAVN-MJ-001
        promo_code=user.voucher_code,             # DISC50
        payment_gateway_transaction_id=payment.id
    )
    
    # Mark done
    user.is_first_transaction = False
    db.session.commit()
    
    return {"success": True, "discount": discount}
```

---

## 🛡️ Error Handling

### HAVN Redirect Errors

| Error | Status | Meaning | User Experience |
|-------|--------|---------|-----------------|
| Missing ref param | 400 | Referral code missing | Show error page |
| Invalid slug | 404 | SaaS company not found | Show "Link invalid" |
| Invalid referral | 404 | Referral code not found | Show "Link expired" |
| Voucher expired | 410 | End date passed | Redirect tanpa voucher |
| Usage limit reached | 429 | Voucher fully used | Redirect tanpa voucher |

### Handling di SaaS Side

```python
@app.route("/login")
def login_page():
    ref = request.args.get('ref')
    vc = request.args.get('vc')
    
    if ref:
        # Validate format (optional)
        if not is_valid_referral_format(ref):
            logger.warning(f"Invalid referral format: {ref}")
            # Proceed tanpa referral
        else:
            session['pending_referral'] = ref
            session['pending_voucher'] = vc
    
    return render_template('login.html')
```

---

## 📊 URL Format

### Public Referral Link

```
https://havn.com/r/<saas_slug>?ref=<referral_code>&vc=<voucher_code>
```

**Parameters:**
- `saas_slug`: Company slug (configured by HAVN admin)
- `ref`: Referral code (required) - Format: `HAVN-XX-NNN`
- `vc`: Voucher code (optional) - Custom format

**Examples:**

```bash
# Referral only (no voucher)
https://havn.com/r/mycompany?ref=HAVN-MJ-001

# Referral + voucher
https://havn.com/r/mycompany?ref=HAVN-MJ-001&vc=DISC50

# After HAVN redirect (received by your login page)
https://saascompany.com/login?ref=HAVN-MJ-001&vc=DISC50
```

---

## ✅ Integration Checklist

### Configuration:
- [ ] Contact HAVN admin untuk setup `public_redirect_slug` dan `public_auth_redirect_url`
- [ ] Verify URL redirect menuju login page Anda yang correct

### Database:
- [ ] Run migration untuk add 3 columns ke users table
- [ ] Verify indexes created untuk performance

### Code Changes:
- [ ] Add param capture di login page route (1 place)
- [ ] Create `attach_pending_referral()` helper function (1 function)
- [ ] Call helper dari semua login handlers (Google, Email, Magic Link, dll)
- [ ] Update checkout flow untuk auto-apply voucher (1 place)

### Testing:
- [ ] Test referral link redirect ke login page dengan params
- [ ] Test params tersimpan di session
- [ ] Test attach referral setelah Google OAuth login
- [ ] Test attach referral setelah Email login
- [ ] Test voucher validation via SDK
- [ ] Test first transaction dengan auto-apply discount
- [ ] Test subsequent transactions (no voucher)

---

## 🎯 Summary

**Yang Perlu Anda Lakukan:**

1. **Database** (1x setup): Add 3 columns ke users table
2. **Configuration** (1x setup): Kasih tau HAVN URL login page Anda
3. **Code** (minimal changes):
   - Capture `?ref` & `?vc` params di login page → save to session
   - Create 1 helper function `attach_pending_referral()`
   - Call helper dari semua login handlers (1 line each)
   - Update checkout untuk auto-apply voucher

**Yang TIDAK Perlu Diubah:**
- ❌ Login flow existing Anda
- ❌ OAuth callback handlers (just add 1 line)
- ❌ HAVN SDK (sudah support semua method yang dibutuhkan)
- ❌ Frontend login UI

**SDK Methods Used (Already Exist):**
- ✅ `havn_client.vouchers.validate()` - untuk validate voucher
- ✅ `havn_client.transactions.send()` - untuk send transaction

---

## 💬 Support

**Documentation:**
- Backend API: [WEBHOOK_API.md](../../backend/docs/WEBHOOK_API.md)
- SDK Reference: [API_REFERENCE.md](API_REFERENCE.md)

**Contact:**
- Email: support@havn.com
- Slack: #havn-integration

---

## 📝 Changelog

### v1.0.0 (2024-11-21)
- Initial release public referral link feature
- Stateless design dengan query params (no Redis/session storage di HAVN side)
- Support untuk semua login gateways (Google, Email, Facebook, Magic Link, dll)
- Minimal integration requirements untuk SaaS companies
