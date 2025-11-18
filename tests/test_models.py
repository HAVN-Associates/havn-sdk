"""
Tests for data models
"""

import pytest
from havn.models.transaction import TransactionPayload
from havn.models.user_sync import UserSyncPayload
from havn.models.voucher import VoucherValidationPayload
from havn.exceptions import HAVNValidationError


class TestTransactionPayload:
    """Test TransactionPayload model"""

    def test_valid_transaction_payload(self):
        """Test valid transaction payload"""
        payload = TransactionPayload(
            amount=10000,
            payment_gateway_transaction_id="txn_12345",
            payment_gateway="STRIPE",
            customer_email="customer@example.com",
            referral_code="HAVN-MJ-001",
            currency="USD",
        )
        payload.validate()  # Should not raise

    def test_invalid_amount_negative(self):
        """Test validation fails for negative amount"""
        payload = TransactionPayload(
            amount=-100,
            payment_gateway_transaction_id="txn_12345",
            payment_gateway="STRIPE",
            customer_email="customer@example.com",
            referral_code="HAVN-MJ-001"
        )
        with pytest.raises(ValueError, match="Amount must be greater than 0"):
            payload.validate()

    def test_invalid_currency(self):
        """Test validation fails for invalid currency"""
        payload = TransactionPayload(
            amount=10000,
            payment_gateway_transaction_id="txn_12345",
            payment_gateway="STRIPE",
            customer_email="customer@example.com",
            referral_code="HAVN-MJ-001",
            currency="XYZ"
        )
        with pytest.raises(ValueError, match="Unsupported currency code"):
            payload.validate()

    def test_invalid_customer_type(self):
        """Test validation fails for invalid customer type"""
        payload = TransactionPayload(
            amount=10000,
            payment_gateway_transaction_id="txn_12345",
            payment_gateway="STRIPE",
            customer_email="customer@example.com",
            referral_code="HAVN-MJ-001",
            customer_type="INVALID",
        )
        with pytest.raises(ValueError, match="Invalid customer_type"):
            payload.validate()

    def test_missing_payment_gateway(self):
        """payment_gateway must be provided"""
        payload = TransactionPayload(
            amount=10000,
            payment_gateway_transaction_id="txn_12345",
            payment_gateway="",
            customer_email="customer@example.com",
            referral_code="HAVN-MJ-001",
        )
        with pytest.raises(ValueError, match="payment_gateway is required"):
            payload.validate()

    def test_to_dict_removes_none(self):
        """Test to_dict removes None values"""
        payload = TransactionPayload(
            amount=10000,
            payment_gateway_transaction_id="txn_12345",
            payment_gateway="STRIPE",
            customer_email="customer@example.com",
            referral_code="HAVN-MJ-001",
            promo_code=None,
        )
        data = payload.to_dict()
        assert "amount" in data
        assert "referral_code" in data
        assert "promo_code" not in data  # None values removed

    def test_server_side_conversion_flag(self):
        """server_side_conversion must be boolean when provided"""
        payload = TransactionPayload(
            amount=12000,
            payment_gateway_transaction_id="txn_flag",
            payment_gateway="MIDTRANS",
            customer_email="customer@example.com",
            referral_code="HAVN-MJ-001",
            currency="IDR",
            server_side_conversion=True,
        )
        payload.validate()  # Should not raise

        invalid_payload = TransactionPayload(
            amount=12000,
            payment_gateway_transaction_id="txn_flag",
            payment_gateway="MIDTRANS",
            customer_email="customer@example.com",
            referral_code="HAVN-MJ-001",
            server_side_conversion="yes",
        )
        with pytest.raises(ValueError, match="server_side_conversion must be a boolean"):
            invalid_payload.validate()

    def test_missing_referral_code(self):
        """referral_code is required"""
        payload = TransactionPayload(
            amount=10000,
            payment_gateway_transaction_id="txn_12345",
            payment_gateway="STRIPE",
            customer_email="customer@example.com",
        )

        with pytest.raises(ValueError, match="referral_code is required"):
            payload.validate()

    def test_invoice_id_trim_and_length(self):
        """invoice_id must be trimmed and <= 100 chars"""
        payload = TransactionPayload(
            amount=10000,
            payment_gateway_transaction_id="txn_trim",
            payment_gateway="STRIPE",
            customer_email="customer@example.com",
            referral_code="HAVN-MJ-001",
            invoice_id="  INV-001  ",
        )
        payload.validate()
        assert payload.invoice_id == "INV-001"

        too_long = "X" * 101
        payload_long = TransactionPayload(
            amount=10000,
            payment_gateway_transaction_id="txn_long",
            payment_gateway="STRIPE",
            customer_email="customer@example.com",
            referral_code="HAVN-MJ-001",
            invoice_id=too_long,
        )
        with pytest.raises(ValueError, match="invoice_id cannot exceed 100 characters"):
            payload_long.validate()


class TestUserSyncPayload:
    """Test UserSyncPayload model"""

    def test_valid_user_sync_payload(self):
        """Test valid user sync payload"""
        payload = UserSyncPayload(
            email="user@example.com",
            name="John Doe",
        )
        payload.validate()  # Should not raise

    def test_invalid_email(self):
        """Test validation fails for invalid email"""
        payload = UserSyncPayload(email="invalid-email", name="John Doe")
        with pytest.raises(ValueError, match="Invalid email format"):
            payload.validate()

    def test_empty_name(self):
        """Test validation fails for empty name"""
        payload = UserSyncPayload(email="user@example.com", name="")
        with pytest.raises(ValueError, match="Name cannot be empty"):
            payload.validate()

    def test_invalid_country_code(self):
        """Test validation fails for invalid country code"""
        payload = UserSyncPayload(
            email="user@example.com",
            name="John Doe",
            country_code="USA",  # Should be 2 letters
        )
        with pytest.raises(ValueError, match="Country code must be 2 characters"):
            payload.validate()


class TestVoucherValidationPayload:
    """Test VoucherValidationPayload model"""

    def test_valid_voucher_payload(self):
        """Test valid voucher validation payload"""
        payload = VoucherValidationPayload(
            voucher_code="VOUCHER123",
            amount=10000,
        )
        payload.validate()  # Should not raise

    def test_empty_voucher_code(self):
        """Test validation fails for empty voucher code"""
        payload = VoucherValidationPayload(voucher_code="")
        with pytest.raises(ValueError, match="Voucher code cannot be empty"):
            payload.validate()

    def test_invalid_amount(self):
        """Test validation fails for invalid amount"""
        payload = VoucherValidationPayload(voucher_code="VOUCHER123", amount=-100)
        with pytest.raises(ValueError, match="Amount must be greater than 0"):
            payload.validate()
