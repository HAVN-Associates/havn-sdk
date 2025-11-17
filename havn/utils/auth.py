"""
Authentication utilities for HAVN SDK
"""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional


def calculate_hmac_signature(payload: Dict[str, Any], secret: str) -> str:
    """
    Calculate HMAC-SHA256 signature for webhook payload

    Args:
        payload: Dictionary payload to sign
        secret: Webhook secret key

    Returns:
        Hexadecimal signature string

    Example:
        >>> payload = {"amount": 10000}
        >>> signature = calculate_hmac_signature(payload, "secret")
    """
    # Serialize payload consistently (sorted keys, no spaces)
    payload_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)

    # Calculate HMAC-SHA256
    signature = hmac.new(
        secret.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    return signature


def build_auth_headers(
    payload: Optional[Dict[str, Any]] = None,
    api_key: str = None,
    webhook_secret: str = None,
) -> Dict[str, str]:
    """
    Build authentication headers for API request

    For GET requests without payload, signature is calculated from empty dict.
    For POST requests with payload, signature is calculated from payload.

    Args:
        payload: Request payload (optional, for GET requests can be None)
        api_key: API key
        webhook_secret: Webhook secret for signature

    Returns:
        Dictionary of headers

    Example:
        >>> # POST request with payload
        >>> headers = build_auth_headers(
        ...     payload={"amount": 10000},
        ...     api_key="key123",
        ...     webhook_secret="secret456"
        ... )
        >>> headers["X-API-Key"]
        'key123'

        >>> # GET request without payload
        >>> headers = build_auth_headers(
        ...     api_key="key123",
        ...     webhook_secret="secret456"
        ... )
    """
    # For GET requests, use empty dict for signature calculation
    # (matches backend behavior where request.get_data() returns empty bytes)
    signature_payload = payload if payload is not None else {}
    signature = calculate_hmac_signature(signature_payload, webhook_secret)

    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Key": api_key,
        "X-Signature": signature,
    }
