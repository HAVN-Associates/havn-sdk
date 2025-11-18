"""
Currency conversion utilities for HAVN SDK

Handles currency conversion with exchange rate caching and error handling.
All amounts in HAVN are stored in USD cents (single source of truth).
"""

import warnings

import requests
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from ..config import Config
from ..constants import USD_CURRENCY

# Minor unit mapping (number of decimal places for each currency)
_CURRENCY_MINOR_UNITS = {
    # Zero-decimal currencies
    "IDR": 0,
    "JPY": 0,
    "KRW": 0,
    "VND": 0,
    "CLP": 0,
    "ISK": 0,
    # Three-decimal currencies commonly used in finance
    "BHD": 3,
    "JOD": 3,
    "KWD": 3,
    "OMR": 3,
    "TND": 3,
}
_DEFAULT_MINOR_UNIT = 2


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

    @staticmethod
    def _get_minor_unit(currency: str) -> int:
        """Return the number of minor units (decimal places) for a currency"""
        return _CURRENCY_MINOR_UNITS.get(currency.upper(), _DEFAULT_MINOR_UNIT)

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
        # Dinamis: cukup pastikan rate positif, bukan NaN/inf, dan tidak ekstrem besar.
        if rate.is_nan() or rate.is_infinite():
            return False

        if rate <= Decimal("0"):
            return False

        # Batasi upper bound secara longgar agar mencegah data API yang korup
        if rate > Decimal("1000000000"):
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

        minor_unit = self._get_minor_unit(from_currency)
        scale = Decimal("10") ** minor_unit
        amount_major = Decimal(str(amount)) / scale

        # Convert to USD major unit
        amount_usd = amount_major * rate

        # Convert to cents and round half up for accuracy
        amount_cents_decimal = (amount_usd * Decimal("100")).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        amount_cents = int(amount_cents_decimal)

        # Format currency string
        amount_formatted = self._format_currency(amount_usd, USD_CURRENCY)

        return {
            "amount_cents": amount_cents,
            "amount_decimal": float(amount_usd),
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

        # Convert to target currency major unit
        amount_target_major = amount_usd * rate

        minor_unit = self._get_minor_unit(to_currency)
        scale = Decimal("10") ** minor_unit

        amount_minor_decimal = (amount_target_major * scale).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        amount_minor = int(amount_minor_decimal)

        # Format currency string
        amount_formatted = self._format_currency(amount_target_major, to_currency)

        return {
            "amount": amount_minor,
            "amount_decimal": float(amount_target_major),
            "amount_formatted": amount_formatted,
            "currency": to_currency,
            "exchange_rate": float(rate),
            "original_amount_cents": amount_cents,
            "original_currency": USD_CURRENCY,
        }

    def _format_currency(self, amount: Decimal, currency: str) -> str:
        """
        Format currency amount as string respecting minor units

        Args:
            amount: Amount in major units as Decimal
            currency: Currency code

        Returns:
            Formatted string (e.g., "$10.00", "Rp 150.000")
        """
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
        minor_unit = self._get_minor_unit(currency)

        if minor_unit == 0:
            normalized = amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            amount_str = f"{int(normalized):,}"
        else:
            quant = Decimal("1") / (Decimal("10") ** minor_unit)
            normalized = amount.quantize(quant, rounding=ROUND_HALF_UP)
            amount_str = f"{normalized:,.{minor_unit}f}".rstrip("0").rstrip(".")

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
    warnings.warn(
        "convert_to_usd_cents is deprecated. HAVN backend kini yang melakukan konversi mata uang."
        " Gunakan server_side_conversion pada webhook transaksi, dan hanya pakai helper ini untuk"
        " kebutuhan tampilan/diagnostik sementara.",
        DeprecationWarning,
        stacklevel=2,
    )
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
    warnings.warn(
        "convert_from_usd_cents is deprecated. HAVN backend handle konversi resmi;"
        " helper ini hanya untuk tampilan/diagnostik sementara.",
        DeprecationWarning,
        stacklevel=2,
    )
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
