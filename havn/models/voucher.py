"""
Voucher models for HAVN SDK
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


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
