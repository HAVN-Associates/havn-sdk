"""
Simple tests for webhook handlers using client API
"""

import pytest
from unittest.mock import patch
from havn import HAVNClient


class TestWebhooksClientAPI:
    """Test webhook functionality through the client API"""

    def setup_method(self):
        """Setup test client"""
        self.client = HAVNClient(
            api_key="test_key",
            webhook_secret="test_secret", 
            test_mode=True
        )

    def test_transaction_webhook_send(self):
        """Test transaction webhook send method"""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "message": "Transaction processed",
                "transaction": {
                    "transaction_id": "txn_12345",
                    "amount": 10000,
                    "currency": "USD",
                    "status": "completed",
                    "customer_type": "NEW_CUSTOMER"
                },
                "commissions": []
            }

            result = self.client.transactions.send(
                amount=10000,
                payment_gateway_transaction_id="pg_txn_123",
                payment_gateway="STRIPE",
                customer_email="customer@example.com",
                referral_code="HAVN-MJ-001"
            )

            assert result.success is True
            assert result.transaction.transaction_id == "txn_12345"

    def test_transaction_webhook_with_voucher(self):
        """Test transaction webhook with voucher"""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "message": "Transaction processed with voucher",
                "transaction": {
                    "transaction_id": "txn_12345",
                    "amount": 8000,
                    "currency": "USD",
                    "status": "completed",
                    "customer_type": "NEW_CUSTOMER",
                    "subtotal_transaction": 10000,
                    "subtotal_discount": 2000
                },
                "commissions": [
                    {
                        "commission_id": "comm_123",
                        "associate_id": "assoc_123",
                        "level": 1,
                        "amount": 1000,
                        "percentage": 10.0,
                        "type": "REFERRAL",
                        "direction": "UP",
                        "status": "PENDING"
                    }
                ]
            }

            result = self.client.transactions.send(
                amount=8000,
                payment_gateway_transaction_id="pg_txn_123",
                payment_gateway="STRIPE",
                customer_email="customer@example.com",
                referral_code="HAVN-MJ-001",
                promo_code="VOUCHER123",
                subtotal_transaction=10000
            )

            assert result.success is True
            assert len(result.commissions) == 1
            assert result.commissions[0].amount == 1000

    def test_transaction_server_side_conversion(self):
        """Ensure SDK forwards raw currency when server_side_conversion enabled"""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "message": "Transaction processed",
                "transaction": {
                    "transaction_id": "txn_ssc_1",
                    "amount": 150000,
                    "currency": "IDR",
                    "status": "completed",
                    "customer_type": "NEW_CUSTOMER"
                },
                "commissions": []
            }

            self.client.transactions.send(
                amount=150000,
                payment_gateway_transaction_id="pg_txn_ssc",
                payment_gateway="MIDTRANS",
                customer_email="customer@example.com",
                referral_code="HAVN-MJ-001",
                currency="IDR",
                server_side_conversion=True,
            )

            _, kwargs = mock_request.call_args
            payload = kwargs["payload"]
            assert payload["currency"] == "IDR"
            assert payload["amount"] == 150000
            assert payload["server_side_conversion"] is True

    def test_user_sync_webhook_single(self):
        """Test user sync webhook single user"""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "message": "User synced successfully",
                "user_created": True,
                "associate_created": True,
                "user": {
                    "email": "user@example.com",
                    "name": "John Doe"
                },
                "associate": {
                    "associate_id": "assoc_123",
                    "referral_code": "HAVN-SYNC-123"
                }
            }

            result = self.client.users.sync(
                email="user@example.com",
                name="John Doe",
                create_associate=True,
                upline_code="HAVN-MJ-001"
            )

            assert result.success is True
            assert result.user_created is True
            assert result.associate_created is True

    def test_user_sync_webhook_bulk(self):
        """Test user sync webhook bulk users"""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "message": "Bulk sync completed",
                "summary": {
                    "total": 3,
                    "success": 3,
                    "failed": 0
                },
                "referral_code": "HAVN-BULK-123",
                "results": [
                    {
                        "email": "user1@example.com",
                        "success": True,
                        "user_created": True,
                        "associate_created": True
                    },
                    {
                        "email": "user2@example.com",
                        "success": True,
                        "user_created": True,
                        "associate_created": True
                    },
                    {
                        "email": "user3@example.com",
                        "success": True,
                        "user_created": True,
                        "associate_created": True
                    }
                ]
            }

            result = self.client.users.sync_bulk(
                users=[
                    {"email": "user1@example.com", "name": "User One"},
                    {"email": "user2@example.com", "name": "User Two", "is_owner": True},
                    {"email": "user3@example.com", "name": "User Three"}
                ],
                upline_code="HAVN-MJ-001"
            )

            assert result.success is True
            assert result.summary.total == 3
            assert result.summary.success == 3

    def test_voucher_webhook_skip(self):
        """Skip voucher webhook tests - these need more complex mocking"""
        # Skip voucher tests for now as they require complex API mocking
        pytest.skip("Voucher webhook tests need more complex setup")

    def test_auth_webhook_login(self):
        """Test auth webhook login"""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "data": {
                    "redirect_url": "https://havn.com/login?token=temp_token_123",
                    "token": "temp_token_123",
                    "expires_in": 300
                }
            }

            result = self.client.auth.login("user@example.com")

            assert result == "https://havn.com/login?token=temp_token_123"
