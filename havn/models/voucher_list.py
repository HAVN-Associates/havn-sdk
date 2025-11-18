"""
Voucher list models for HAVN SDK
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, fields


def is_havn_voucher_code(code: str) -> bool:
    """
    Check if voucher code is from HAVN

    HAVN voucher format: HAVN-{ASSOCIATE_CODE}-{SAAS_CODE}-{RANDOM}
    All HAVN vouchers start with "HAVN-"

    Args:
        code: Voucher code to check

    Returns:
        True if HAVN voucher, False otherwise

    Example:
        >>> from havn.models.voucher_list import is_havn_voucher_code
        >>> is_havn_voucher_code("HAVN-AQNEO-S08-ABC123")
        True
        >>> is_havn_voucher_code("LOCAL123")
        False
        >>> is_havn_voucher_code("havn-test")
        False  # Case sensitive for prefix check
    """
    # Early return for empty/invalid input (performance optimization)
    if not code:
        return False
    # Use isinstance check for type safety
    if not isinstance(code, str):
        return False
    # Case-insensitive check (HAVN prefix is always uppercase)
    return code.upper().startswith("HAVN-")


@dataclass
class VoucherData:
    """
    Voucher data model from API response

    Attributes:
        serial: Voucher serial ID
        saas_company_id: SaaS company ID
        associate_id: Associate ID
        code: Voucher code
        type: Voucher type (DISCOUNT_PERCENTAGE, DISCOUNT_FIXED)
        value: Voucher value (in cents/basis points)
        usage_limit: Maximum usage limit
        current_usage: Current usage count
        min_purchase: Minimum purchase amount (cents)
        max_purchase: Maximum purchase amount (cents, optional)
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        active: Active status
        client_type: Client type (NEW_CUSTOMER, RECURRING)
        description: Description
        creation_cost: Creation cost (cents)
        created_by: Creator user ID
        created_date: Created date (ISO format)
        updated_at: Updated date (ISO format)
        currency: Currency code
        configured_currency: Currency code yang dikonfigurasikan khusus untuk SaaS (opsional)
        display_currency: Currency yang digunakan untuk tampilan (opsional, dari backend)
        affiliates_url: Affiliate URL (optional)
        affiliates_qr_image: QR code image URL (optional)
        is_expired: Whether voucher is expired
        is_valid: Whether voucher is currently valid
        remaining_usage: Remaining usage count
        usage_percentage: Usage percentage (0-100)
        associate: Associate info (optional)
    """

    serial: str
    saas_company_id: int
    associate_id: str
    code: str
    type: str
    value: int
    usage_limit: int
    current_usage: int
    min_purchase: int
    max_purchase: Optional[int] = None
    start_date: str = ""
    end_date: str = ""
    active: bool = True
    client_type: Optional[str] = None
    description: Optional[str] = None
    creation_cost: int = 0
    created_by: str = ""
    created_date: str = ""
    updated_at: str = ""
    currency: str = "USD"
    configured_currency: Optional[str] = None
    display_currency: Optional[str] = None
    affiliates_url: Optional[str] = None
    affiliates_qr_image: Optional[str] = None
    is_expired: bool = False
    is_valid: bool = False
    remaining_usage: int = 0
    usage_percentage: float = 0.0
    associate: Optional[Dict[str, Any]] = None
    is_havn_voucher: bool = False  # Flag to identify HAVN vs local voucher
    raw_response: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoucherData":
        """
        Create VoucherData from dictionary

        Automatically detects if voucher is from HAVN based on code format.
        Performance: Creates new dict to avoid mutating input (best practice).
        """
        # Create copy to avoid mutating input dict (immutability best practice)
        voucher_data = dict(data)
        # Auto-detect HAVN voucher from code format
        code = voucher_data.get("code", "")
        voucher_data["is_havn_voucher"] = is_havn_voucher_code(code)
        allowed_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in voucher_data.items() if k in allowed_fields}
        filtered_data.setdefault("raw_response", voucher_data)
        return cls(**filtered_data)


@dataclass
class VoucherListPagination:
    """
    Pagination information for voucher list

    Attributes:
        page: Current page number
        limit: Items per page
        total: Total items
        total_pages: Total pages
        has_prev: Whether has previous page
        has_next: Whether has next page
    """

    page: int
    limit: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoucherListPagination":
        """Create VoucherListPagination from dictionary"""
        return cls(**data)


@dataclass
class VoucherListResponse:
    """
    Response model for voucher list endpoint

    Attributes:
        success: Whether request was successful
        message: Response message
        data: List of vouchers
        pagination: Pagination information
        raw_response: Raw response dictionary
    """

    success: bool
    message: str
    data: List[VoucherData] = field(default_factory=list)
    pagination: Optional[VoucherListPagination] = None
    raw_response: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoucherListResponse":
        """
        Create VoucherListResponse from API response

        Handles backend response format:
        {
            "success": true,
            "message": "Success",
            "data": [...],  # List directly at root level
            "pagination": {...}  # Pagination at root level
        }
        """
        # Extract vouchers list (directly from root "data" key)
        vouchers_list = data.get("data", [])
        # Type safety: ensure it's a list (early validation for performance)
        if not isinstance(vouchers_list, list):
            vouchers_list = []

        # Extract pagination (directly from root "pagination" key)
        pagination_dict = data.get("pagination")

        # Convert vouchers using list comprehension (optimal performance)
        # List comprehension is faster than map() or loops for this use case
        vouchers = [VoucherData.from_dict(v) for v in vouchers_list]

        # Lazy evaluation: only convert pagination if present (performance optimization)
        pagination = (
            VoucherListPagination.from_dict(pagination_dict)
            if pagination_dict
            else None
        )

        return cls(
            success=data.get("success", True),
            message=data.get("message", ""),
            data=vouchers,
            pagination=pagination,
            raw_response=data,
        )
