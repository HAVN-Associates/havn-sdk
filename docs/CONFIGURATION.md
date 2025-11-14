# Panduan Konfigurasi HAVN SDK

Dokumen ini menjelaskan berbagai cara mengkonfigurasi HAVN Python SDK, termasuk environment variables, custom configuration, dan best practices.

## Daftar Isi

- [Environment Variables](#environment-variables)
- [Programmatic Configuration](#programmatic-configuration)
- [Configuration Options](#configuration-options)
- [Best Practices](#best-practices)
- [Multi-Environment Setup](#multi-environment-setup)

---

## Environment Variables

### Required Variables

SDK dapat membaca konfigurasi dari environment variables. Ini adalah cara **terbaik** untuk production.

```bash
# Required
export HAVN_API_KEY="your_api_key_here"
export HAVN_WEBHOOK_SECRET="your_webhook_secret_here"

# Optional
export HAVN_BASE_URL="https://api.havn.com"
export HAVN_TIMEOUT="30"
export HAVN_MAX_RETRIES="3"
export HAVN_BACKOFF_FACTOR="0.5"
```

### Python Usage

```python
from havn import HAVNClient

# Initialize dari environment variables
client = HAVNClient()  # Otomatis membaca dari env vars
```

### Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HAVN_API_KEY` | ✅ Yes | - | API key untuk authentication |
| `HAVN_WEBHOOK_SECRET` | ✅ Yes | - | Secret untuk HMAC signature |
| `HAVN_BASE_URL` | ❌ No | `https://api.havn.com` | Base URL untuk HAVN API |
| `HAVN_TIMEOUT` | ❌ No | `30` | Request timeout dalam seconds |
| `HAVN_MAX_RETRIES` | ❌ No | `3` | Maximum retry attempts |
| `HAVN_BACKOFF_FACTOR` | ❌ No | `0.5` | Exponential backoff multiplier |

---

## Programmatic Configuration

### Basic Initialization

```python
from havn import HAVNClient

# Initialize dengan explicit parameters
client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret"
)
```

### Full Configuration

```python
client = HAVNClient(
    api_key="your_api_key",
    webhook_secret="your_webhook_secret",
    base_url="https://api.havn.com",
    timeout=30,
    max_retries=3,
    backoff_factor=0.5,
    test_mode=False
)
```

### Priority Order

Configuration diambil dengan urutan prioritas berikut:

1. **Explicit parameters** (highest priority)
2. **Environment variables**
3. **Default values** (lowest priority)

```python
# Example: Jika environment variable HAVN_TIMEOUT=60
# tapi Anda set timeout=30, maka timeout=30 yang digunakan

client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    timeout=30  # Ini override HAVN_TIMEOUT env var
)
```

---

## Configuration Options

### base_url

Base URL untuk HAVN API.

```python
# Production (default)
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    base_url="https://api.havn.com"
)

# Staging/Development
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    base_url="https://staging-api.havn.com"
)

# Custom endpoint
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    base_url="https://api.havn.com/v1"
)
```

**Default**: `https://api.havn.com`

---

### timeout

Request timeout dalam seconds. Setiap HTTP request akan timeout setelah waktu ini.

```python
# Default timeout (30 seconds)
client = HAVNClient(api_key="...", webhook_secret="...")

# Custom timeout (60 seconds)
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    timeout=60
)

# Short timeout untuk fast-fail (10 seconds)
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    timeout=10
)
```

**Default**: `30` seconds

**Recommendation**:
- **Production**: 30-60 seconds
- **High-frequency**: 10-15 seconds
- **Slow network**: 60-120 seconds

---

### max_retries

Maximum number of retry attempts untuk failed requests.

```python
# Default (3 retries)
client = HAVNClient(api_key="...", webhook_secret="...")

# No retries
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    max_retries=0
)

# More retries untuk unreliable network
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    max_retries=5
)
```

**Default**: `3`

**Retry Status Codes**: 429, 500, 502, 503, 504

**Recommendation**:
- **Normal**: 3 retries
- **Unreliable network**: 5 retries
- **Critical operations**: 0 retries (fail fast, handle manually)

---

### backoff_factor

Exponential backoff multiplier untuk retry. Delay = `backoff_factor * (2 ^ attempt_number)`

```python
# Default (0.5 seconds)
client = HAVNClient(api_key="...", webhook_secret="...")
# Retry delays: 0.5s, 1.0s, 2.0s

# Faster retries
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    backoff_factor=0.3
)
# Retry delays: 0.3s, 0.6s, 1.2s

# Slower retries
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    backoff_factor=1.0
)
# Retry delays: 1.0s, 2.0s, 4.0s
```

**Default**: `0.5`

**Formula**: `delay = backoff_factor * (2 ^ attempt_number)`

**Recommendation**:
- **Normal**: 0.5
- **High-frequency**: 0.3
- **Rate-limited APIs**: 1.0

---

### test_mode

Enable dry-run mode. Request akan diproses tapi data tidak disimpan ke database.

```python
# Production mode
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    test_mode=False
)

# Test mode (dry-run)
client = HAVNClient(
    api_key="...",
    webhook_secret="...",
    test_mode=True
)
```

**Default**: `False`

**Use Cases**:
- Development testing
- Integration testing
- Validation testing tanpa mengganggu production data

---

## Best Practices

### 1. Use Environment Variables untuk Production

```python
# ✅ Good: Use environment variables
import os
client = HAVNClient(
    api_key=os.getenv("HAVN_API_KEY"),
    webhook_secret=os.getenv("HAVN_WEBHOOK_SECRET")
)

# Atau lebih sederhana:
client = HAVNClient()  # Reads from env vars

# ❌ Bad: Hardcode credentials
client = HAVNClient(
    api_key="hardcoded-key-123",
    webhook_secret="hardcoded-secret-456"
)
```

### 2. Store Credentials Securely

```python
# ✅ Good: Use secret management service
import os
from azure.keyvault.secrets import SecretClient  # Example

# Atau use .env file dengan python-dotenv
from dotenv import load_dotenv
load_dotenv()

client = HAVNClient()

# ❌ Bad: Store in code atau plain text files
```

### 3. Use Context Manager

```python
# ✅ Good: Auto-close session
with HAVNClient(api_key="...", webhook_secret="...") as client:
    result = client.transactions.send(...)
# Session closed automatically

# ❌ Bad: Manual close (easy to forget)
client = HAVNClient(...)
result = client.transactions.send(...)
# Forgot to close!
```

### 4. Configuration per Environment

```python
import os

# Detect environment
env = os.getenv("ENVIRONMENT", "development")

if env == "production":
    client = HAVNClient(
        api_key=os.getenv("HAVN_API_KEY"),
        webhook_secret=os.getenv("HAVN_WEBHOOK_SECRET"),
        base_url="https://api.havn.com",
        timeout=30,
        max_retries=3,
        test_mode=False
    )
elif env == "staging":
    client = HAVNClient(
        api_key=os.getenv("HAVN_STAGING_API_KEY"),
        webhook_secret=os.getenv("HAVN_STAGING_WEBHOOK_SECRET"),
        base_url="https://staging-api.havn.com",
        timeout=30,
        max_retries=3,
        test_mode=True  # Test mode untuk staging
    )
else:  # development
    client = HAVNClient(
        api_key=os.getenv("HAVN_DEV_API_KEY", "dev-key"),
        webhook_secret=os.getenv("HAVN_DEV_WEBHOOK_SECRET", "dev-secret"),
        base_url="http://localhost:8000",  # Local development
        timeout=10,
        max_retries=1,
        test_mode=True
    )
```

---

## Multi-Environment Setup

### Using .env Files

**`.env.production`**:
```bash
HAVN_API_KEY=prod_api_key_here
HAVN_WEBHOOK_SECRET=prod_webhook_secret_here
HAVN_BASE_URL=https://api.havn.com
HAVN_TIMEOUT=30
HAVN_MAX_RETRIES=3
ENVIRONMENT=production
```

**`.env.staging`**:
```bash
HAVN_API_KEY=staging_api_key_here
HAVN_WEBHOOK_SECRET=staging_webhook_secret_here
HAVN_BASE_URL=https://staging-api.havn.com
HAVN_TIMEOUT=30
HAVN_MAX_RETRIES=3
ENVIRONMENT=staging
```

**`.env.development`**:
```bash
HAVN_API_KEY=dev_api_key_here
HAVN_WEBHOOK_SECRET=dev_webhook_secret_here
HAVN_BASE_URL=http://localhost:8000
HAVN_TIMEOUT=10
HAVN_MAX_RETRIES=1
ENVIRONMENT=development
```

**Python Code**:
```python
from dotenv import load_dotenv
import os

# Load environment-specific .env file
env = os.getenv("ENVIRONMENT", "development")
load_dotenv(f".env.{env}")

# Initialize client dari environment variables
client = HAVNClient()
```

### Using Config Class

```python
from havn import HAVNClient
import os

class HAVNConfig:
    """Configuration manager untuk HAVN SDK"""
    
    @staticmethod
    def get_client():
        """Get configured HAVN client berdasarkan environment"""
        env = os.getenv("ENVIRONMENT", "development")
        
        configs = {
            "production": {
                "api_key": os.getenv("HAVN_API_KEY"),
                "webhook_secret": os.getenv("HAVN_WEBHOOK_SECRET"),
                "base_url": "https://api.havn.com",
                "timeout": 30,
                "max_retries": 3,
                "test_mode": False
            },
            "staging": {
                "api_key": os.getenv("HAVN_STAGING_API_KEY"),
                "webhook_secret": os.getenv("HAVN_STAGING_WEBHOOK_SECRET"),
                "base_url": "https://staging-api.havn.com",
                "timeout": 30,
                "max_retries": 3,
                "test_mode": True
            },
            "development": {
                "api_key": os.getenv("HAVN_DEV_API_KEY", "dev-key"),
                "webhook_secret": os.getenv("HAVN_DEV_WEBHOOK_SECRET", "dev-secret"),
                "base_url": os.getenv("HAVN_BASE_URL", "http://localhost:8000"),
                "timeout": 10,
                "max_retries": 1,
                "test_mode": True
            }
        }
        
        config = configs.get(env, configs["development"])
        return HAVNClient(**config)

# Usage
client = HAVNConfig.get_client()
```

---

## Validation

### Validate Configuration

```python
from havn import HAVNClient

def validate_client_config(client: HAVNClient):
    """Validate client configuration"""
    errors = []
    
    if not client.api_key:
        errors.append("API key is required")
    
    if not client.webhook_secret:
        errors.append("Webhook secret is required")
    
    if client.timeout <= 0:
        errors.append("Timeout must be greater than 0")
    
    if client.max_retries < 0:
        errors.append("Max retries must be non-negative")
    
    if client.backoff_factor <= 0:
        errors.append("Backoff factor must be greater than 0")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True

# Usage
client = HAVNClient(api_key="...", webhook_secret="...")
validate_client_config(client)
```

---

## Troubleshooting

### Common Configuration Issues

1. **Missing Credentials**
   ```
   ValueError: API key is required...
   ```
   **Solution**: Set `HAVN_API_KEY` dan `HAVN_WEBHOOK_SECRET` environment variables

2. **Wrong Base URL**
   ```
   HAVNNetworkError: Connection error
   ```
   **Solution**: Check `base_url` configuration

3. **Timeout Issues**
   ```
   HAVNNetworkError: Request timeout after 30 seconds
   ```
   **Solution**: Increase `timeout` value

---

## Next Steps

- Baca [Quick Start Guide](QUICKSTART.md) untuk mulai menggunakan SDK
- Lihat [API Reference](API_REFERENCE.md) untuk dokumentasi lengkap
- Check [Examples](EXAMPLES.md) untuk contoh penggunaan
- Review [Troubleshooting Guide](TROUBLESHOOTING.md) jika ada masalah

