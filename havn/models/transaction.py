"""
Transaction models for HAVN SDK
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict


@dataclass
class TransactionPayload:
    """
    Transaction payload for webhook

    Attributes:
        amount: Final transaction amount in cents (required)
        payment_gateway_transaction_id: Payment gateway transaction ID (required)
        payment_gateway: Payment gateway identifier/name (required)
        customer_email: Customer email (required, valid email format)
        referral_code: Associate referral code (required)
        promo_code: Voucher code (optional)
        currency: Currency code (default: USD)
        customer_type: Optional manual override (NEW_CUSTOMER/RECURRING). HAVN backend auto-determines per customer.
        subtotal_transaction: Original amount before discount (optional)
        acquisition_method: (Deprecated) Backend auto-determines. Leave as None.
        custom_fields: Custom metadata dict (max 3 entries) (optional)
        invoice_id: External invoice ID (optional)
        transaction_type: Transaction type (optional, untuk logging)
        description: Transaction description (optional)
        server_side_conversion: Flag to request backend-side currency conversion (optional)

    Example:
        >>> payload = TransactionPayload(
        ...     amount=10000,
        ...     referral_code="HAVN-MJ-001",
        ...     currency="USD"
        ... )
        >>> payload.to_dict()
    """

    amount: int
    payment_gateway_transaction_id: str  # Required: Payment gateway transaction ID
    payment_gateway: str  # Required: Payment gateway identifier
    customer_email: str  # Required: Customer email
    referral_code: Optional[str] = None
    promo_code: Optional[str] = None
    currency: str = "USD"
    customer_type: Optional[str] = None
    subtotal_transaction: Optional[int] = None
    acquisition_method: Optional[str] = (
        None  # Optional: Auto-determined<br>- REFERRAL_VOUCHER: Jika ada promo_code DAN referral_code (keduanya wajib)<br>- REFERRAL: Jika hanya ada referral_code
    )
    custom_fields: Optional[Dict[str, Any]] = None
    invoice_id: Optional[str] = None
    transaction_type: Optional[str] = None
    description: Optional[str] = None
    server_side_conversion: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, removing None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def validate(self) -> None:
        """
        Validate payload

        Raises:
            ValueError: If validation fails
        """
        from ..utils.validators import (
            validate_amount,
            validate_currency,
            validate_custom_fields,
            validate_referral_code,
        )

        # Validate amount
        validate_amount(self.amount)

        # Validate currency
        validate_currency(self.currency)

        # Validate custom_fields
        validate_custom_fields(self.custom_fields)

        # Validate referral_code
        if self.referral_code is None or not isinstance(self.referral_code, str):
            raise ValueError("referral_code is required and must be a string")

        referral_clean = self.referral_code.strip()
        if not referral_clean:
            raise ValueError("referral_code is required and cannot be empty")

        self.referral_code = referral_clean.upper()
        validate_referral_code(self.referral_code)

        # Validate customer_type (optional manual override)
        if self.customer_type is not None:
            normalized_type = self.customer_type.strip().upper()

            if not normalized_type:
                self.customer_type = None
            elif normalized_type not in ["NEW_CUSTOMER", "RECURRING"]:
                raise ValueError(
                    f"Invalid customer_type: {self.customer_type}. "
                    "Must be 'NEW_CUSTOMER' or 'RECURRING'"
                )
            else:
                self.customer_type = normalized_type

        # Validate subtotal_transaction
        if self.subtotal_transaction is not None:
            validate_amount(self.subtotal_transaction)
            if self.subtotal_transaction < self.amount:
                raise ValueError(
                    "subtotal_transaction must be greater than or equal to amount"
                )

        # Validate payment_gateway_transaction_id (required)
        if (
            not self.payment_gateway_transaction_id
            or not self.payment_gateway_transaction_id.strip()
        ):
            raise ValueError(
                "payment_gateway_transaction_id is required and cannot be empty"
            )

        if len(self.payment_gateway_transaction_id) > 200:
            raise ValueError(
                "payment_gateway_transaction_id cannot exceed 200 characters"
            )

        # Validate payment_gateway (required, <= 100 chars to match backend model)
        if not self.payment_gateway or not self.payment_gateway.strip():
            raise ValueError("payment_gateway is required and cannot be empty")

        gateway_clean = self.payment_gateway.strip().upper()
        if len(gateway_clean) > 100:
            raise ValueError("payment_gateway cannot exceed 100 characters")
        self.payment_gateway = gateway_clean

        # Validate customer_email (required, non-empty, valid format)
        if not self.customer_email or not self.customer_email.strip():
            raise ValueError("customer_email is required and cannot be empty")

        from ..utils.validators import validate_email

        try:
            validate_email(self.customer_email)
        except ValueError as e:
            raise ValueError(f"Invalid customer_email format: {e}")

        # Normalize invoice_id (optional, <= 100 chars)
        if self.invoice_id is not None:
            if not isinstance(self.invoice_id, str):
                raise ValueError("invoice_id must be a string if provided")

            invoice_clean = self.invoice_id.strip()
            if not invoice_clean:
                self.invoice_id = None
            elif len(invoice_clean) > 100:
                raise ValueError("invoice_id cannot exceed 100 characters")
            else:
                self.invoice_id = invoice_clean

        # Validate acquisition_method (optional, but must be valid if provided)
        if self.acquisition_method:
            valid_methods = ["REFERRAL", "REFERRAL_VOUCHER"]
            if self.acquisition_method.upper() not in valid_methods:
                raise ValueError(
                    f"Invalid acquisition_method: {self.acquisition_method}. "
                    f"Must be one of: {', '.join(valid_methods)}"
                )

        # Validate server_side_conversion flag type (if provided)
        if self.server_side_conversion is not None and not isinstance(
            self.server_side_conversion, bool
        ):
            raise ValueError("server_side_conversion must be a boolean if provided")


@dataclass
class CommissionData:
    """Commission data from response"""

    commission_id: str
    associate_id: str
    level: int
    amount: int
    percentage: float
    type: str
    direction: str
    status: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommissionData":
        """Create from dictionary"""
        return cls(
            commission_id=data.get("commission_id", ""),
            associate_id=data.get("associate_id", ""),
            level=data.get("level", 0),
            amount=data.get("amount", 0),
            percentage=data.get("percentage", 0.0),
            type=data.get("type", ""),
            direction=data.get("direction", ""),
            status=data.get("status", ""),
        )


@dataclass
class TransactionData:
    """Transaction data from response"""

    transaction_id: str
    amount: int
    currency: str
    status: str
    customer_type: str
    acquisition_method: Optional[str] = None
    subtotal_transaction: Optional[int] = None
    subtotal_discount: Optional[int] = None
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransactionData":
        """Create from dictionary"""
        return cls(
            transaction_id=data.get("transaction_id", ""),
            amount=data.get("amount", 0),
            currency=data.get("currency", "USD"),
            status=data.get("status", ""),
            customer_type=data.get("customer_type", ""),
            acquisition_method=data.get("acquisition_method"),
            subtotal_transaction=data.get("subtotal_transaction"),
            subtotal_discount=data.get("subtotal_discount"),
            created_at=data.get("created_at"),
        )


@dataclass
class TransactionResponse:
    """
    Transaction webhook response

    Attributes:
        success: Whether request was successful
        message: Response message
        transaction: Transaction data
        commissions: List of commission data
        raw_response: Raw response dictionary
    """

    success: bool
    message: str
    transaction: TransactionData
    commissions: List[CommissionData] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransactionResponse":
        """
        Create from API response dictionary

        Args:
            data: Response dictionary from API

        Returns:
            TransactionResponse instance
        """
        transaction_data = data.get("transaction", {})
        commissions_data = data.get("commissions", [])

        return cls(
            success=data.get("success", False),
            message=data.get("message", ""),
            transaction=TransactionData.from_dict(transaction_data),
            commissions=[CommissionData.from_dict(c) for c in commissions_data],
            raw_response=data,
        )
