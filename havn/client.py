"""
Main HAVN client for API interactions
"""

import time
import json
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config
from .exceptions import HAVNAPIError, HAVNAuthError, HAVNNetworkError
from .webhooks import TransactionWebhook, UserSyncWebhook, VoucherWebhook
from .utils.auth import build_auth_headers


class HAVNClient:
    """
    HAVN API Client for SaaS integrations

    This client handles authentication, request signing, retry logic, and error handling
    for all HAVN API endpoints.

    Attributes:
        api_key: API key for authentication
        webhook_secret: Secret key for HMAC signature generation
        base_url: Base URL for HAVN API
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        test_mode: Whether to enable dry-run mode (no data saved)

    Example:
        >>> # Initialize with explicit parameters
        >>> client = HAVNClient(
        ...     api_key="your_api_key",
        ...     webhook_secret="your_webhook_secret",
        ...     base_url="https://api.havn.com"
        ... )
        
        >>> # Or use environment variables
        >>> client = HAVNClient()  # Reads HAVN_API_KEY, HAVN_WEBHOOK_SECRET, etc.
        
        >>> # Send transaction
        >>> result = client.transactions.send(
        ...     amount=10000,
        ...     referral_code="HAVN-MJ-001"
        ... )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        webhook_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        test_mode: bool = False,
    ):
        """
        Initialize HAVN client

        Args:
            api_key: API key (or uses HAVN_API_KEY env var)
            webhook_secret: Webhook secret (or uses HAVN_WEBHOOK_SECRET env var)
            base_url: Base URL (or uses HAVN_BASE_URL env var, default: https://api.havn.com)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts (default: 3)
            backoff_factor: Exponential backoff multiplier (default: 0.5)
            test_mode: Enable dry-run mode - requests succeed but don't save data (default: False)

        Raises:
            ValueError: If api_key or webhook_secret is not provided and not in environment
        """
        # Get configuration from params or environment
        self.api_key = api_key or Config.get_api_key()
        self.webhook_secret = webhook_secret or Config.get_webhook_secret()
        self.base_url = (base_url or Config.get_base_url()).rstrip("/")
        self.timeout = timeout if timeout is not None else Config.get_timeout()
        self.max_retries = (
            max_retries if max_retries is not None else Config.get_max_retries()
        )
        self.backoff_factor = (
            backoff_factor if backoff_factor is not None else Config.get_backoff_factor()
        )
        self.test_mode = test_mode

        # Validate required parameters
        if not self.api_key:
            raise ValueError(
                "API key is required. "
                "Provide api_key parameter or set HAVN_API_KEY environment variable."
            )

        if not self.webhook_secret:
            raise ValueError(
                "Webhook secret is required. "
                "Provide webhook_secret parameter or set HAVN_WEBHOOK_SECRET environment variable."
            )

        # Initialize HTTP session with retry logic
        self._session = self._create_session()

        # Initialize webhook handlers
        self.transactions = TransactionWebhook(self)
        self.users = UserSyncWebhook(self)
        self.vouchers = VoucherWebhook(self)

    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry logic

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["POST", "GET"],  # Retry POST requests (idempotent webhooks)
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _make_request(
        self, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to HAVN API

        This method handles:
        - Authentication header injection
        - HMAC signature generation
        - Request/response logging
        - Error handling
        - Retry logic (via session)

        Args:
            method: HTTP method (POST, GET, etc.)
            endpoint: API endpoint path (e.g., "/api/v1/webhook/transaction")
            payload: Request payload dictionary

        Returns:
            Response data as dictionary

        Raises:
            HAVNAuthError: If authentication fails
            HAVNAPIError: If API returns error
            HAVNNetworkError: If network error occurs
        """
        url = f"{self.base_url}{endpoint}"

        # Build headers with authentication
        if payload:
            headers = build_auth_headers(payload, self.api_key, self.webhook_secret)
        else:
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }

        # Add test mode header if enabled
        if self.test_mode:
            headers["X-Test-Mode"] = "true"

        # Serialize payload
        data = json.dumps(payload) if payload else None

        try:
            response = self._session.request(
                method=method,
                url=url,
                data=data,
                headers=headers,
                timeout=self.timeout,
            )

            # Handle response
            return self._handle_response(response)

        except requests.exceptions.Timeout as e:
            raise HAVNNetworkError(
                f"Request timeout after {self.timeout} seconds", original_error=e
            )
        except requests.exceptions.ConnectionError as e:
            raise HAVNNetworkError("Connection error", original_error=e)
        except requests.exceptions.RequestException as e:
            raise HAVNNetworkError(f"Request failed: {str(e)}", original_error=e)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response

        Args:
            response: requests.Response object

        Returns:
            Response data as dictionary

        Raises:
            HAVNAuthError: If authentication fails (401)
            HAVNAPIError: If API returns error
        """
        # Authentication error
        if response.status_code == 401:
            try:
                error_data = response.json()
                message = error_data.get("message", "Authentication failed")
            except (ValueError, KeyError):
                message = "Authentication failed"
            raise HAVNAuthError(message)

        # Success (200 OK or 201 Created)
        if response.status_code in [200, 201]:
            try:
                return response.json()
            except ValueError:
                # No JSON body (e.g., voucher validation returns empty body)
                return {"success": True}

        # API error (4xx, 5xx)
        try:
            error_data = response.json()
            message = error_data.get("message", f"API error: {response.status_code}")
            error_type = error_data.get("error", "APIError")
        except (ValueError, KeyError):
            message = f"API error: {response.status_code}"
            error_type = "APIError"
            error_data = None

        raise HAVNAPIError(
            message=f"[{error_type}] {message}",
            status_code=response.status_code,
            response=error_data,
        )

    def close(self):
        """Close HTTP session"""
        if hasattr(self, "_session"):
            self._session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False

    def __repr__(self):
        """String representation"""
        return (
            f"HAVNClient(base_url='{self.base_url}', "
            f"timeout={self.timeout}, "
            f"test_mode={self.test_mode})"
        )
