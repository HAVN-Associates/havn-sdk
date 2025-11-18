"""Tests for currency conversion utilities"""

from datetime import datetime
from decimal import Decimal

from havn.utils import currency as currency_module
from havn.utils.currency import (
    CurrencyConverter,
    convert_from_usd_cents,
    convert_to_usd_cents,
)


def _prime_global_converter() -> CurrencyConverter:
    """Seed the global converter cache with deterministic exchange rates."""
    converter = CurrencyConverter()
    now = datetime.now()

    # Cache USD -> EUR rate (0.9) and USD -> IDR rate (15000)
    converter._rate_cache["EUR"] = {"rate": Decimal("0.9"), "fetched_at": now}
    converter._rate_cache["IDR"] = {"rate": Decimal("15000"), "fetched_at": now}

    currency_module._global_converter = converter  # type: ignore[attr-defined]
    return converter


def test_convert_to_usd_cents_fractional_currency():
    _prime_global_converter()

    result = convert_to_usd_cents(850, "EUR")  # €8.50

    assert result["amount_cents"] == 944  # ~$9.44
    assert result["currency"] == "USD"
    assert result["original_currency"] == "EUR"


def test_convert_to_usd_cents_zero_decimal_currency():
    _prime_global_converter()

    result = convert_to_usd_cents(150000, "IDR")  # Rp 150.000

    assert result["amount_cents"] == 1000  # $10.00
    assert result["amount_decimal"] == 10.0


def test_convert_from_usd_cents_fractional_currency():
    _prime_global_converter()

    result = convert_from_usd_cents(944, "EUR")  # ~$9.44 USD

    assert result["amount"] == 850  # back to €8.50 in cents
    assert result["currency"] == "EUR"


def test_convert_from_usd_cents_zero_decimal_currency():
    _prime_global_converter()

    result = convert_from_usd_cents(1000, "IDR")  # $10.00 USD

    assert result["amount"] == 150000  # Rp 150.000
    assert result["currency"] == "IDR"
