"""
Currency conversion utilities for HAVN SDK

Handles currency conversion with exchange rate caching and error handling.
All amounts in HAVN are stored in USD cents (single source of truth).
"""

import requests
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from ..config import Config
from ..constants import USD_CURRENCY


class CurrencyConverter:
    """
    Currency converter with exchange rate caching

    Converts amounts between currencies, with automatic caching of exchange rates.
    All HAVN amounts are stored in USD cents (single source of truth).

    Example:
        >>> converter = CurrencyConverter()
        >>> result = converter.convert_to_usd_cents(150000, "IDR")
        >>> print(result["amount_cents"])  # ~1000 (USD cents)
        >>> print(result["exchange_rate"])  # ~0.000067 (1 IDR = X USD)
    """

    BASE_CURRENCY = USD_CURRENCY  # HAVN stores all amounts in USD cents
    DEFAULT_EXCHANGE_RATE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
    DEFAULT_CACHE_DURATION_HOURS = 24  # Cache rates for 24 hours
    DEFAULT_API_TIMEOUT = 5  # API request timeout in seconds

    def __init__(
        self,
        exchange_rate_api_url: Optional[str] = None,
        cache_duration_hours: Optional[int] = None,
        api_timeout: Optional[int] = None,
    ):
        """
        Initialize currency converter

        Args:
            exchange_rate_api_url: Exchange rate API URL (default from config or env)
            cache_duration_hours: Cache duration in hours (default: 24)
            api_timeout: API request timeout in seconds (default: 5)
        """
        self.exchange_rate_api_url = (
            exchange_rate_api_url
            or Config.get_exchange_rate_api_url()
            or self.DEFAULT_EXCHANGE_RATE_API_URL
        )
        self.cache_duration_hours = (
            cache_duration_hours
            or Config.get_exchange_rate_cache_duration_hours()
            or self.DEFAULT_CACHE_DURATION_HOURS
        )
        self.api_timeout = (
            api_timeout or Config.get_currency_api_timeout() or self.DEFAULT_API_TIMEOUT
        )

        # In-memory cache: {currency: {"rate": Decimal, "fetched_at": datetime}}
        self._rate_cache: Dict[str, Dict[str, Any]] = {}

    def get_exchange_rate(
        self, to_currency: str, from_currency: str = BASE_CURRENCY
    ) -> Optional[Decimal]:
        """
        Get exchange rate from cache or API

        Args:
            to_currency: Target currency code (e.g., "IDR", "EUR")
            from_currency: Source currency code (default: "USD")

        Returns:
            Exchange rate as Decimal (1 from_currency = X to_currency), or None if not available

        Raises:
            ValueError: If currency code is invalid
        """
        to_currency = to_currency.upper().strip()
        from_currency = from_currency.upper().strip()

        # Validate currency codes
        if len(to_currency) != 3 or not to_currency.isalpha():
            raise ValueError(f"Invalid currency code: {to_currency}")
        if len(from_currency) != 3 or not from_currency.isalpha():
            raise ValueError(f"Invalid currency code: {from_currency}")

        # Same currency, return 1.0
        if from_currency == to_currency:
            return Decimal("1.0")

        # For USD -> other currency
        if from_currency == self.BASE_CURRENCY:
            return self._get_rate_from_usd(to_currency)

        # For other currency -> USD (inverse)
        if to_currency == self.BASE_CURRENCY:
            rate = self._get_rate_from_usd(from_currency)
            if rate:
                # Inverse: 1 / rate (1 IDR = 1/USD_rate USD)
                return Decimal("1.0") / rate
            return None

        # For conversion between two non-USD currencies
        # Convert: from_currency -> USD -> to_currency
        from_rate = self._get_rate_from_usd(from_currency)
        to_rate = self._get_rate_from_usd(to_currency)

        if from_rate and to_rate:
            # Rate = to_rate / from_rate
            # Example: IDR -> EUR = EUR_rate / IDR_rate
            return to_rate / from_rate

        return None

    def _get_rate_from_usd(self, currency: str) -> Optional[Decimal]:
        """
        Get exchange rate from USD to target currency (with caching)

        Args:
            currency: Target currency code

        Returns:
            Exchange rate as Decimal, or None if not available
        """
        # Check cache first
        if currency in self._rate_cache:
            cached = self._rate_cache[currency]
            fetched_at = cached["fetched_at"]
            cache_expires_at = fetched_at + timedelta(hours=self.cache_duration_hours)

            if datetime.now() < cache_expires_at:
                # Cache is still valid - validate rate before returning
                cached_rate = cached["rate"]
                if self._validate_exchange_rate(currency, cached_rate):
                    return cached_rate
                else:
                    # Invalid cached rate, remove from cache and fetch fresh
                    import logging

                    logging.warning(
                        f"Invalid cached exchange rate for {currency}: {cached_rate}. "
                        "Removing from cache and fetching fresh rate.",
                        extra={
                            "currency": currency,
                            "cached_rate": float(cached_rate),
                        },
                    )
                    del self._rate_cache[currency]

        # Cache expired or not found, fetch from API
        rate = self._fetch_exchange_rate_from_api(currency)
        if rate:
            # Update cache only if rate is valid (already validated in _fetch_exchange_rate_from_api)
            self._rate_cache[currency] = {
                "rate": rate,
                "fetched_at": datetime.now(),
            }

        return rate

    def _fetch_exchange_rate_from_api(self, currency: str) -> Optional[Decimal]:
        """
        Fetch exchange rate from external API

        Args:
            currency: Target currency code

        Returns:
            Exchange rate as Decimal, or None if fetch failed or rate is invalid

        Note:
            Validates exchange rate against expected ranges to catch API errors.
            Common rates: IDR ~15000, JPY ~150, EUR ~0.85, GBP ~0.75
        """
        try:
            response = requests.get(
                self.exchange_rate_api_url, timeout=self.api_timeout
            )
            response.raise_for_status()
            data = response.json()

            # API returns rates as: {"rates": {"IDR": 15000, "EUR": 0.85, ...}}
            # OR: {"data": {"rates": {...}}} (different API formats)
            rates_data = data.get("rates") or data.get("data", {}).get("rates", {})

            if currency in rates_data:
                rate_value = rates_data[currency]
                rate = Decimal(str(rate_value))

                # Validate rate is reasonable (catch API errors or wrong format)
                if not self._validate_exchange_rate(currency, rate):
                    import logging

                    logging.warning(
                        f"Exchange rate for {currency} seems invalid: {rate}. "
                        f"Expected range based on currency type. Skipping cache.",
                        extra={
                            "currency": currency,
                            "rate": float(rate),
                            "api_url": self.exchange_rate_api_url,
                            "response_format": "rates"
                            if "rates" in data
                            else "data.rates",
                        },
                    )
                    return None

                return rate

            # Log if currency not found
            import logging

            logging.warning(
                f"Currency {currency} not found in API response",
                extra={
                    "currency": currency,
                    "available_currencies": list(rates_data.keys())[:10]
                    if rates_data
                    else [],
                    "api_url": self.exchange_rate_api_url,
                },
            )
            return None

        except (requests.exceptions.RequestException, KeyError, ValueError) as e:
            # Log warning but don't raise (allows fallback behavior)
            import logging

            logging.warning(
                f"Failed to fetch exchange rate for {currency}: {e}",
                exc_info=False,
            )
            return None

    def _validate_exchange_rate(self, currency: str, rate: Decimal) -> bool:
        """
        Validate exchange rate is within reasonable range

        Args:
            currency: Currency code
            rate: Exchange rate to validate

        Returns:
            True if rate is valid, False otherwise
        """
        # Expected rate ranges (1 USD = X currency)
        # These are rough ranges to catch obvious errors
        rate_ranges = {
            "IDR": (1000, 50000),  # Usually ~15000
            "JPY": (50, 300),  # Usually ~150
            "KRW": (1000, 5000),  # Usually ~1300
            "VND": (20000, 50000),  # Usually ~25000
            "EUR": (0.5, 1.5),  # Usually ~0.85
            "GBP": (0.5, 1.5),  # Usually ~0.75
            "AUD": (0.5, 2.0),  # Usually ~1.5
            "CAD": (0.5, 2.0),  # Usually ~1.3
            "SGD": (0.8, 2.0),  # Usually ~1.35
            "MYR": (3.0, 6.0),  # Usually ~4.5
            "THB": (20, 60),  # Usually ~35
            "PHP": (40, 80),  # Usually ~55
            "INR": (60, 120),  # Usually ~83
            "CNY": (5, 10),  # Usually ~7
        }

        currency_upper = currency.upper()
        if currency_upper in rate_ranges:
            min_rate, max_rate = rate_ranges[currency_upper]
            if rate < Decimal(str(min_rate)) or rate > Decimal(str(max_rate)):
                return False

        # For currencies not in the list, basic sanity check:
        # Rate should be positive and not extremely large/small
        if rate <= Decimal("0") or rate > Decimal("1000000"):
            return False

        return True

    def convert_to_usd_cents(self, amount: int, from_currency: str) -> Dict[str, Any]:
        """
        Convert amount from any currency to USD cents

        Args:
            amount: Amount in source currency's smallest unit (e.g., IDR rupiah, EUR cents)
            from_currency: Source currency code (e.g., "IDR", "EUR")

        Returns:
            Dictionary with:
                - amount_cents: Amount in USD cents (int)
                - amount_decimal: Amount in USD dollars (float)
                - amount_formatted: Formatted string (e.g., "$10.00")
                - currency: "USD"
                - exchange_rate: Exchange rate used (float)
                - original_amount: Original amount (int)
                - original_currency: Source currency code

        Raises:
            ValueError: If currency is invalid or exchange rate not available
        """
        from_currency = from_currency.upper().strip()

        # Get exchange rate (from_currency -> USD)
        rate = self.get_exchange_rate(self.BASE_CURRENCY, from_currency)
        if not rate:
            raise ValueError(
                f"Exchange rate not available for {from_currency} to USD. "
                "Please ensure the currency is supported and API is accessible."
            )

        # Convert to USD
        # For currencies with same unit size as USD (e.g., EUR cents), direct conversion
        # For currencies with different unit sizes (e.g., IDR), assume amount is in smallest unit
        # Example: 150000 IDR = 150000 * rate = ~10 USD
        amount_decimal = Decimal(str(amount)) * rate

        # Convert to cents (multiply by 100)
        # Round to nearest cent
        amount_cents = int(round(amount_decimal * Decimal("100")))

        # Format currency string
        amount_formatted = self._format_currency(float(amount_decimal), USD_CURRENCY)

        return {
            "amount_cents": amount_cents,
            "amount_decimal": float(amount_decimal),
            "amount_formatted": amount_formatted,
            "currency": USD_CURRENCY,
            "exchange_rate": float(rate),
            "original_amount": amount,
            "original_currency": from_currency,
        }

    def convert_from_usd_cents(
        self, amount_cents: int, to_currency: str
    ) -> Dict[str, Any]:
        """
        Convert amount from USD cents to target currency

        Args:
            amount_cents: Amount in USD cents
            to_currency: Target currency code (e.g., "IDR", "EUR")

        Returns:
            Dictionary with:
                - amount: Amount in target currency's smallest unit (int)
                - amount_decimal: Amount in target currency (float)
                - amount_formatted: Formatted string (e.g., "Rp 150.000")
                - currency: Target currency code
                - exchange_rate: Exchange rate used (float)
                - original_amount_cents: Original USD cents (int)
                - original_currency: "USD"

        Raises:
            ValueError: If currency is invalid or exchange rate not available
        """
        to_currency = to_currency.upper().strip()

        # Get exchange rate (USD -> to_currency)
        rate = self.get_exchange_rate(to_currency, self.BASE_CURRENCY)
        if not rate:
            raise ValueError(
                f"Exchange rate not available for USD to {to_currency}. "
                "Please ensure the currency is supported and API is accessible."
            )

        # Convert from cents to dollars first
        amount_usd = Decimal(str(amount_cents)) / Decimal("100")

        # Convert to target currency
        amount_target = amount_usd * rate

        # Convert to target currency's smallest unit
        # Round to nearest integer for precision (important for large numbers like IDR)
        amount = int(round(amount_target))

        # Format currency string
        amount_formatted = self._format_currency(float(amount_target), to_currency)

        return {
            "amount": amount,
            "amount_decimal": float(amount_target),
            "amount_formatted": amount_formatted,
            "currency": to_currency,
            "exchange_rate": float(rate),
            "original_amount_cents": amount_cents,
            "original_currency": USD_CURRENCY,
        }

    @staticmethod
    def _format_currency(amount: float, currency: str) -> str:
        """
        Format currency amount as string

        Args:
            amount: Amount as float
            currency: Currency code

        Returns:
            Formatted string (e.g., "$10.00", "Rp 150.000")
        """
        # Basic formatting (can be enhanced with locale-specific formatting)
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "IDR": "Rp",
            "INR": "₹",
            "CNY": "¥",
            "KRW": "₩",
            "SGD": "S$",
            "MYR": "RM",
            "THB": "฿",
            "PHP": "₱",
            "VND": "₫",
        }

        symbol = currency_symbols.get(currency, currency)

        # Format number with thousands separator
        if amount >= 1000:
            amount_str = f"{amount:,.2f}".rstrip("0").rstrip(".")
        else:
            amount_str = f"{amount:.2f}".rstrip("0").rstrip(".")

        return f"{symbol} {amount_str}"


# Global converter instance (singleton pattern for caching)
_global_converter: Optional[CurrencyConverter] = None


def get_currency_converter() -> CurrencyConverter:
    """
    Get global currency converter instance (singleton)

    Returns:
        CurrencyConverter instance
    """
    global _global_converter
    if _global_converter is None:
        _global_converter = CurrencyConverter()
    return _global_converter


# Convenience functions
def convert_to_usd_cents(amount: int, from_currency: str) -> Dict[str, Any]:
    """
    Convert amount from any currency to USD cents (convenience function)

    Args:
        amount: Amount in source currency's smallest unit
        from_currency: Source currency code

    Returns:
        Dictionary with conversion result (see CurrencyConverter.convert_to_usd_cents)

    Example:
        >>> result = convert_to_usd_cents(150000, "IDR")
        >>> print(result["amount_cents"])  # ~1000 (USD cents)
    """
    converter = get_currency_converter()
    return converter.convert_to_usd_cents(amount, from_currency)


def convert_from_usd_cents(amount_cents: int, to_currency: str) -> Dict[str, Any]:
    """
    Convert amount from USD cents to target currency (convenience function)

    Args:
        amount_cents: Amount in USD cents
        to_currency: Target currency code

    Returns:
        Dictionary with conversion result (see CurrencyConverter.convert_from_usd_cents)

    Example:
        >>> result = convert_from_usd_cents(1000, "IDR")
        >>> print(result["amount_formatted"])  # "Rp 150.000"
    """
    converter = get_currency_converter()
    return converter.convert_from_usd_cents(amount_cents, to_currency)


def get_exchange_rate(
    to_currency: str, from_currency: str = USD_CURRENCY
) -> Optional[Decimal]:
    """
    Get exchange rate between currencies (convenience function)

    Args:
        to_currency: Target currency code
        from_currency: Source currency code (default: "USD")

    Returns:
        Exchange rate as Decimal, or None if not available

    Example:
        >>> rate = get_exchange_rate("IDR", "USD")
        >>> print(rate)  # Decimal('15000.00')
    """
    converter = get_currency_converter()
    return converter.get_exchange_rate(to_currency, from_currency)
