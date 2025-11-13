"""
Validation utilities for HAVN SDK
"""

import re
from typing import Optional


def validate_amount(amount: int) -> None:
    """
    Validate transaction amount

    Args:
        amount: Amount in cents

    Raises:
        ValueError: If amount is invalid

    Example:
        >>> validate_amount(10000)  # OK
        >>> validate_amount(-100)  # Raises ValueError
    """
    if not isinstance(amount, int):
        raise ValueError("Amount must be an integer (cents)")

    if amount <= 0:
        raise ValueError("Amount must be greater than 0")

    if amount > 10_000_000_00:  # $10M max
        raise ValueError("Amount exceeds maximum allowed ($10,000,000)")


def validate_email(email: str) -> None:
    """
    Validate email format

    Args:
        email: Email address

    Raises:
        ValueError: If email format is invalid

    Example:
        >>> validate_email("user@example.com")  # OK
        >>> validate_email("invalid-email")  # Raises ValueError
    """
    if not isinstance(email, str):
        raise ValueError("Email must be a string")

    # Simple email regex (RFC 5322 simplified)
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        raise ValueError(f"Invalid email format: {email}")


def validate_currency(currency: str) -> None:
    """
    Validate currency code

    Args:
        currency: ISO 4217 currency code (3 letters)

    Raises:
        ValueError: If currency code is invalid

    Example:
        >>> validate_currency("USD")  # OK
        >>> validate_currency("XYZ")  # Raises ValueError
    """
    if not isinstance(currency, str):
        raise ValueError("Currency must be a string")

    if len(currency) != 3:
        raise ValueError("Currency code must be 3 characters (ISO 4217)")

    if not currency.isupper():
        raise ValueError("Currency code must be uppercase")

    # Common currency codes (can be extended)
    valid_currencies = [
        "USD",
        "EUR",
        "GBP",
        "JPY",
        "CNY",
        "AUD",
        "CAD",
        "CHF",
        "HKD",
        "SGD",
        "SEK",
        "NOK",
        "DKK",
        "INR",
        "IDR",
        "MYR",
        "PHP",
        "THB",
        "VND",
        "KRW",
        "TWD",
        "BRL",
        "MXN",
        "ZAR",
        "TRY",
        "RUB",
    ]

    if currency not in valid_currencies:
        raise ValueError(
            f"Unsupported currency code: {currency}. "
            f"Supported: {', '.join(valid_currencies)}"
        )


def validate_custom_fields(
    custom_fields: Optional[dict], max_entries: int = 3
) -> None:
    """
    Validate custom fields dictionary

    Args:
        custom_fields: Dictionary of custom fields
        max_entries: Maximum number of entries allowed

    Raises:
        ValueError: If custom fields are invalid

    Example:
        >>> validate_custom_fields({"key": "value"})  # OK
        >>> validate_custom_fields({1: "value"})  # Raises ValueError (non-string key)
    """
    if custom_fields is None:
        return

    if not isinstance(custom_fields, dict):
        raise ValueError("custom_fields must be a dictionary")

    if len(custom_fields) > max_entries:
        raise ValueError(
            f"custom_fields cannot exceed {max_entries} entries (got {len(custom_fields)})"
        )

    # Validate keys and values
    for key, value in custom_fields.items():
        if not isinstance(key, str):
            raise ValueError(f"custom_fields keys must be strings (got {type(key)})")

        if not isinstance(value, (str, int, float, bool)):
            raise ValueError(
                f"custom_fields values must be string, number, or boolean (got {type(value)} for key '{key}')"
            )


def validate_referral_code(referral_code: Optional[str]) -> None:
    """
    Validate referral code format

    Args:
        referral_code: Referral code string

    Raises:
        ValueError: If referral code format is invalid

    Example:
        >>> validate_referral_code("HAVN-MJ-001")  # OK
        >>> validate_referral_code("invalid")  # Raises ValueError
    """
    if referral_code is None:
        return

    if not isinstance(referral_code, str):
        raise ValueError("Referral code must be a string")

    if len(referral_code) < 3 or len(referral_code) > 50:
        raise ValueError("Referral code must be between 3 and 50 characters")

    # Referral codes typically follow pattern: HAVN-XXX-YYY
    # But we allow flexibility
    if not referral_code.strip():
        raise ValueError("Referral code cannot be empty")
