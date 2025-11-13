"""
Tests for utility functions
"""

import pytest
from havn.utils.auth import calculate_hmac_signature, build_auth_headers
from havn.utils.validators import (
    validate_amount,
    validate_email,
    validate_currency,
    validate_custom_fields,
)


class TestAuthUtils:
    """Test authentication utilities"""

    def test_calculate_hmac_signature(self):
        """Test HMAC signature calculation"""
        payload = {"amount": 10000, "referral_code": "HAVN-MJ-001"}
        secret = "test_secret"

        signature = calculate_hmac_signature(payload, secret)

        # Signature should be 64 characters (SHA256 hex)
        assert len(signature) == 64
        assert isinstance(signature, str)

        # Same payload should produce same signature
        signature2 = calculate_hmac_signature(payload, secret)
        assert signature == signature2

    def test_build_auth_headers(self):
        """Test authentication headers building"""
        payload = {"amount": 10000}
        api_key = "test_key"
        webhook_secret = "test_secret"

        headers = build_auth_headers(payload, api_key, webhook_secret)

        assert headers["X-API-Key"] == api_key
        assert "X-Signature" in headers
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"


class TestValidators:
    """Test validation functions"""

    def test_validate_amount_valid(self):
        """Test valid amount validation"""
        validate_amount(10000)  # Should not raise
        validate_amount(1)  # Should not raise
        validate_amount(10_000_000_00)  # Max amount, should not raise

    def test_validate_amount_invalid(self):
        """Test invalid amount validation"""
        with pytest.raises(ValueError, match="Amount must be greater than 0"):
            validate_amount(0)

        with pytest.raises(ValueError, match="Amount must be greater than 0"):
            validate_amount(-100)

        with pytest.raises(ValueError, match="Amount exceeds maximum"):
            validate_amount(10_000_000_01)  # Over max

    def test_validate_email_valid(self):
        """Test valid email validation"""
        validate_email("user@example.com")
        validate_email("test.user+tag@example.co.uk")

    def test_validate_email_invalid(self):
        """Test invalid email validation"""
        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email("invalid-email")

        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email("@example.com")

    def test_validate_currency_valid(self):
        """Test valid currency validation"""
        validate_currency("USD")
        validate_currency("EUR")
        validate_currency("IDR")

    def test_validate_currency_invalid(self):
        """Test invalid currency validation"""
        with pytest.raises(ValueError, match="Unsupported currency code"):
            validate_currency("XYZ")

        with pytest.raises(ValueError, match="Currency code must be 3 characters"):
            validate_currency("US")

        with pytest.raises(ValueError, match="Currency code must be uppercase"):
            validate_currency("usd")

    def test_validate_custom_fields_valid(self):
        """Test valid custom fields validation"""
        validate_custom_fields({"key1": "value1", "key2": 123})
        validate_custom_fields({})
        validate_custom_fields(None)

    def test_validate_custom_fields_invalid(self):
        """Test invalid custom fields validation"""
        # Too many entries
        with pytest.raises(ValueError, match="cannot exceed 3 entries"):
            validate_custom_fields({"k1": "v1", "k2": "v2", "k3": "v3", "k4": "v4"})

        # Non-string key
        with pytest.raises(ValueError, match="keys must be strings"):
            validate_custom_fields({123: "value"})

        # Invalid value type
        with pytest.raises(ValueError, match="values must be string, number, or boolean"):
            validate_custom_fields({"key": []})
