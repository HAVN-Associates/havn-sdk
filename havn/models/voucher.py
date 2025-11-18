"""
Voucher models for HAVN SDK
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class VoucherListFilters:
    """
    Filters for voucher list query

    Attributes:
        page: Page number (default: 1)
        per_page: Items per page (default: 10, max: 100)
        active: Filter by active status
        type: Filter by voucher type (DISCOUNT_PERCENTAGE, DISCOUNT_FIXED)
        client_type: Filter by client type (NEW_CUSTOMER, RECURRING)
        currency: Filter by currency code
        search: Search in code, description
        start_date_from: Filter by start_date >= (YYYY-MM-DD)
        start_date_to: Filter by start_date <= (YYYY-MM-DD)
        end_date_from: Filter by end_date >= (YYYY-MM-DD)
        end_date_to: Filter by end_date <= (YYYY-MM-DD)
        created_from: Filter by created_date >= (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        created_to: Filter by created_date <= (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        min_value: Filter by value >=
        max_value: Filter by value <=
        min_purchase_from: Filter by min_purchase >=
        min_purchase_to: Filter by min_purchase <=
        usage_limit_from: Filter by usage_limit >=
        usage_limit_to: Filter by usage_limit <=
        is_valid: Filter by validity
        is_expired: Filter by expired status
        sort_by: Sort field (code, type, value, start_date, end_date, created_date, current_usage)
        sort_order: Sort direction (asc, desc)
        display_currency: Target currency untuk konversi tampilan (opsional, ditangani backend)
    """

    page: Optional[int] = None
    per_page: Optional[int] = None
    active: Optional[bool] = None
    type: Optional[str] = None
    client_type: Optional[str] = None
    currency: Optional[str] = None
    search: Optional[str] = None
    start_date_from: Optional[str] = None
    start_date_to: Optional[str] = None
    end_date_from: Optional[str] = None
    end_date_to: Optional[str] = None
    created_from: Optional[str] = None
    created_to: Optional[str] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    min_purchase_from: Optional[int] = None
    min_purchase_to: Optional[int] = None
    usage_limit_from: Optional[int] = None
    usage_limit_to: Optional[int] = None
    is_valid: Optional[bool] = None
    is_expired: Optional[bool] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None
    display_currency: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for query params"""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                if isinstance(value, bool):
                    result[key] = value  # Keep as boolean, requests will handle it
                elif isinstance(value, (int, float)):
                    result[key] = str(value)
                else:
                    result[key] = str(value)
        return result

    def validate(self) -> None:
        """
        Validate filters

        Raises:
            ValueError: If validation fails
        """
        # Validate page
        if self.page is not None and self.page < 1:
            raise ValueError("page must be >= 1")

        # Validate per_page
        if self.per_page is not None:
            if self.per_page < 1:
                raise ValueError("per_page must be >= 1")
            if self.per_page > 100:
                raise ValueError("per_page must be <= 100")

        # Validate type
        if self.type is not None:
            valid_types = ["DISCOUNT_PERCENTAGE", "DISCOUNT_FIXED"]
            type_upper = self.type.upper() if isinstance(self.type, str) else str(self.type)
            if type_upper not in valid_types:
                raise ValueError(f"type must be one of: {', '.join(valid_types)}")

        # Validate client_type
        if self.client_type is not None:
            valid_client_types = ["NEW_CUSTOMER", "RECURRING"]
            client_type_upper = self.client_type.upper() if isinstance(self.client_type, str) else str(self.client_type)
            if client_type_upper not in valid_client_types:
                raise ValueError(
                    f"client_type must be one of: {', '.join(valid_client_types)}"
                )

        # Validate sort_by
        if self.sort_by is not None:
            valid_sort_fields = [
                "code",
                "type",
                "value",
                "start_date",
                "end_date",
                "created_date",
                "current_usage",
                "usage_limit",
                "min_purchase",
            ]
            sort_by_lower = self.sort_by.lower() if isinstance(self.sort_by, str) else str(self.sort_by)
            if sort_by_lower not in valid_sort_fields:
                raise ValueError(
                    f"sort_by must be one of: {', '.join(valid_sort_fields)}"
                )

        # Validate sort_order
        if self.sort_order is not None:
            valid_orders = ["asc", "desc"]
            sort_order_lower = self.sort_order.lower() if isinstance(self.sort_order, str) else str(self.sort_order)
            if sort_order_lower not in valid_orders:
                raise ValueError(
                    f"sort_order must be one of: {', '.join(valid_orders)}"
                )

        # Validate date formats (basic check)
        date_fields = [
            "start_date_from",
            "start_date_to",
            "end_date_from",
            "end_date_to",
        ]
        for field in date_fields:
            value = getattr(self, field)
            if value:
                try:
                    from datetime import datetime

                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(
                        f"{field} must be in YYYY-MM-DD format, got: {value}"
                    )

        # Validate datetime formats (basic check)
        datetime_fields = ["created_from", "created_to"]
        for field in datetime_fields:
            value = getattr(self, field)
            if value:
                try:
                    from datetime import datetime

                    # Try datetime format first
                    try:
                        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        # Fallback to date format
                        datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(
                        f"{field} must be in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format, got: {value}"
                    )

        # Validate numeric ranges
        numeric_ranges = [
            ("min_value", "max_value"),
            ("min_purchase_from", "min_purchase_to"),
            ("usage_limit_from", "usage_limit_to"),
        ]
        for min_field, max_field in numeric_ranges:
            min_val = getattr(self, min_field)
            max_val = getattr(self, max_field)
            if min_val is not None and max_val is not None:
                if min_val < 0:
                    raise ValueError(f"{min_field} must be >= 0")
                if max_val < 0:
                    raise ValueError(f"{max_field} must be >= 0")
                if min_val > max_val:
                    raise ValueError(f"{min_field} must be <= {max_field}")


@dataclass
class VoucherValidationPayload:
    """
    Voucher validation payload

    Attributes:
        voucher_code: Voucher code to validate (required)
        amount: Transaction amount in cents (optional)
        currency: Currency code (optional)

    Example:
        >>> payload = VoucherValidationPayload(
        ...     voucher_code="VOUCHER123",
        ...     amount=10000,
        ...     currency="USD"
        ... )
    """

    voucher_code: str
    amount: Optional[int] = None
    currency: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, removing None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def validate(self) -> None:
        """
        Validate payload

        Raises:
            ValueError: If validation fails
        """
        from ..utils.validators import validate_amount, validate_currency

        # Validate voucher_code
        if not self.voucher_code or not self.voucher_code.strip():
            raise ValueError("Voucher code cannot be empty")

        if len(self.voucher_code) > 100:
            raise ValueError("Voucher code cannot exceed 100 characters")

        # Validate amount if provided
        if self.amount is not None:
            validate_amount(self.amount)

        # Validate currency if provided
        if self.currency is not None:
            validate_currency(self.currency)
