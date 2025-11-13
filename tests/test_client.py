"""
Tests for HAVNClient
"""

import pytest
from havn import HAVNClient
from havn.exceptions import HAVNAuthError, HAVNValidationError


class TestHAVNClient:
    """Test HAVNClient initialization and configuration"""

    def test_client_initialization_with_params(self):
        """Test client initialization with explicit parameters"""
        client = HAVNClient(
            api_key="test_key",
            webhook_secret="test_secret",
            base_url="https://test.api.com",
            timeout=60,
        )

        assert client.api_key == "test_key"
        assert client.webhook_secret == "test_secret"
        assert client.base_url == "https://test.api.com"
        assert client.timeout == 60

    def test_client_initialization_missing_api_key(self):
        """Test client raises error when API key is missing"""
        with pytest.raises(ValueError, match="API key is required"):
            HAVNClient(api_key=None, webhook_secret="secret")

    def test_client_initialization_missing_webhook_secret(self):
        """Test client raises error when webhook secret is missing"""
        with pytest.raises(ValueError, match="Webhook secret is required"):
            HAVNClient(api_key="key", webhook_secret=None)

    def test_client_base_url_strip_trailing_slash(self):
        """Test base URL trailing slash is removed"""
        client = HAVNClient(
            api_key="key",
            webhook_secret="secret",
            base_url="https://api.com/",
        )
        assert client.base_url == "https://api.com"

    def test_client_test_mode(self):
        """Test client test mode flag"""
        client = HAVNClient(
            api_key="key",
            webhook_secret="secret",
            test_mode=True,
        )
        assert client.test_mode is True

    def test_client_context_manager(self):
        """Test client can be used as context manager"""
        with HAVNClient(api_key="key", webhook_secret="secret") as client:
            assert client is not None
        # Session should be closed after context exit

    def test_client_repr(self):
        """Test client string representation"""
        client = HAVNClient(
            api_key="key",
            webhook_secret="secret",
            base_url="https://api.com",
            timeout=30,
        )
        repr_str = repr(client)
        assert "HAVNClient" in repr_str
        assert "https://api.com" in repr_str
        assert "timeout=30" in repr_str
