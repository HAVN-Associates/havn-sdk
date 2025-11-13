"""
Authentication utilities for HAVN SDK
"""

import hmac
import hashlib
import json
from typing import Dict, Any


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
    payload: Dict[str, Any], api_key: str, webhook_secret: str
) -> Dict[str, str]:
    """
    Build authentication headers for API request

    Args:
        payload: Request payload
        api_key: API key
        webhook_secret: Webhook secret for signature

    Returns:
        Dictionary of headers

    Example:
        >>> headers = build_auth_headers(
        ...     payload={"amount": 10000},
        ...     api_key="key123",
        ...     webhook_secret="secret456"
        ... )
        >>> headers["X-API-Key"]
        'key123'
    """
    signature = calculate_hmac_signature(payload, webhook_secret)

    return {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
        "X-Signature": signature,
    }
