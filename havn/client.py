"""
Main HAVN client for API interactions
"""

import time
import json
from typing import Optional, Dict, Any, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config
from .exceptions import (
    HAVNAPIError,
    HAVNAuthError,
    HAVNNetworkError,
    HAVNRateLimitError,
)
from .webhooks import TransactionWebhook, UserSyncWebhook, VoucherWebhook, AuthWebhook
from .utils.auth import build_auth_headers
from .constants import (
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_METHOD_PUT,
    HTTP_METHOD_PATCH,
    HTTP_STATUS_OK,
    HTTP_STATUS_CREATED,
    HTTP_STATUS_UNAUTHORIZED,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    HEADER_RATE_LIMIT_RESET,
    HEADER_RATE_LIMIT_LIMIT,
    HEADER_RATE_LIMIT_REMAINING,
    HEADER_TEST_MODE,
    TEST_MODE_VALUE,
    DEFAULT_SUCCESS_RESPONSE,
    DEFAULT_ERROR_TYPE,
    DEFAULT_RATE_LIMIT_MESSAGE,
    DEFAULT_AUTH_FAILED_MESSAGE,
)


def _parse_error_response(
    response: requests.Response,
    default_message: str,
    default_error_type: str = DEFAULT_ERROR_TYPE,
) -> Tuple[str, str]:
    """
    Parse error response JSON (DRY helper)

    Args:
        response: requests.Response object
        default_message: Default error message
        default_error_type: Default error type

    Returns:
        Tuple of (message, error_type)
    """
    try:
        error_data = response.json()
        message = error_data.get("message", default_message)
        error_type = error_data.get("error", default_error_type)
        return message, error_type
    except (ValueError, KeyError):
        return default_message, default_error_type


def _extract_rate_limit_info(
    response: requests.Response,
) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Extract rate limit info from headers (DRY helper)

    Args:
        response: requests.Response object

    Returns:
        Tuple of (retry_after_seconds, limit, remaining)
    """
    retry_after = response.headers.get(HEADER_RATE_LIMIT_RESET)
    limit = response.headers.get(HEADER_RATE_LIMIT_LIMIT)
    remaining = response.headers.get(HEADER_RATE_LIMIT_REMAINING)

    retry_after_seconds = None
    if retry_after:
        try:
            reset_time = int(retry_after)
            current_time = int(time.time())
            retry_after_seconds = max(0, reset_time - current_time)
        except (ValueError, TypeError):
            pass

    return (
        retry_after_seconds,
        int(limit) if limit else None,
        int(remaining) if remaining else None,
    )


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
            backoff_factor
            if backoff_factor is not None
            else Config.get_backoff_factor()
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
        self.auth = AuthWebhook(self)

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
            status_forcelist=[
                HTTP_STATUS_TOO_MANY_REQUESTS,
                500,
                502,
                503,
                504,
            ],  # Retry on these status codes
            allowed_methods=[
                HTTP_METHOD_POST,
                HTTP_METHOD_GET,
            ],  # Retry POST requests (idempotent webhooks)
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

        **Important**: This method always makes a fresh HTTP request to backend.
        No response caching is used. Single source of truth is the backend.
        Each call ensures data consistency with backend state.

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
            Fresh response data as dictionary (always from backend)

        Raises:
            HAVNAuthError: If authentication fails
            HAVNAPIError: If API returns error
            HAVNNetworkError: If network error occurs
        """
        url = f"{self.base_url}{endpoint}"

        # For GET requests, signature is calculated from empty dict (matches backend)
        # Backend uses request.get_data() which returns empty bytes for GET requests
        # Query params are passed separately, not in signature calculation
        signature_payload = None if method == HTTP_METHOD_GET else payload

        # Build headers with authentication (always include signature for webhook endpoints)
        headers = build_auth_headers(
            payload=signature_payload,
            api_key=self.api_key,
            webhook_secret=self.webhook_secret,
        )

        # Add test mode header if enabled
        if self.test_mode:
            headers[HEADER_TEST_MODE] = TEST_MODE_VALUE

        # Serialize payload (only for POST/PUT/PATCH requests)
        data = None
        if method in [HTTP_METHOD_POST, HTTP_METHOD_PUT, HTTP_METHOD_PATCH]:
            data = json.dumps(payload) if payload else None

        try:
            response = self._session.request(
                method=method,
                url=url,
                data=data,
                params=payload
                if method == HTTP_METHOD_GET
                else None,  # For GET, use params
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
            HAVNRateLimitError: If rate limit exceeded (429)
            HAVNAPIError: If API returns error
        """
        # Rate limit error (429)
        if response.status_code == HTTP_STATUS_TOO_MANY_REQUESTS:
            # Extract rate limit info from headers
            retry_after_seconds, limit, remaining = _extract_rate_limit_info(response)

            # Parse error message
            message, _ = _parse_error_response(response, DEFAULT_RATE_LIMIT_MESSAGE)

            raise HAVNRateLimitError(
                message=message,
                retry_after=retry_after_seconds,
                limit=limit,
                remaining=remaining,
            )

        # Authentication error (401)
        if response.status_code == HTTP_STATUS_UNAUTHORIZED:
            message, _ = _parse_error_response(response, DEFAULT_AUTH_FAILED_MESSAGE)
            raise HAVNAuthError(message)

        # Success (200 OK or 201 Created)
        if response.status_code in [HTTP_STATUS_OK, HTTP_STATUS_CREATED]:
            try:
                return response.json()
            except ValueError:
                # No JSON body (e.g., voucher validation returns empty body)
                return DEFAULT_SUCCESS_RESPONSE

        # API error (4xx, 5xx)
        message, error_type = _parse_error_response(
            response, f"API error: {response.status_code}", DEFAULT_ERROR_TYPE
        )

        # Get error data if available
        error_data = None
        try:
            error_data = response.json()
        except (ValueError, KeyError):
            pass

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
