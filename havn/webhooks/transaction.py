"""
Transaction webhook handler
"""

from typing import Dict, Any, Optional
from ..models.transaction import TransactionPayload, TransactionResponse
from ..exceptions import HAVNValidationError


class TransactionWebhook:
    """
    Transaction webhook handler

    Handles sending transactions to HAVN API and processing commissions.

    Example:
        >>> client = HAVNClient(api_key="...", webhook_secret="...")
        >>> result = client.transactions.send(
        ...     amount=10000,
        ...     referral_code="HAVN-MJ-001"
        ... )
        >>> print(result.transaction.transaction_id)
    """

    def __init__(self, client):
        """
        Initialize transaction webhook handler

        Args:
            client: HAVNClient instance
        """
        self.client = client

    def send(
        self,
        amount: int,
        referral_code: Optional[str] = None,
        promo_code: Optional[str] = None,
        currency: str = "USD",
        customer_type: str = "NEW_CUSTOMER",
        subtotal_transaction: Optional[int] = None,
        acquisition_method: Optional[str] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
        invoice_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        transaction_type: Optional[str] = None,
        description: Optional[str] = None,
        payment_gateway_transaction_id: Optional[str] = None,
        is_recurring: Optional[bool] = None,
    ) -> TransactionResponse:
        """
        Send transaction to HAVN API

        Args:
            amount: Final transaction amount in cents (required)
            referral_code: Associate referral code (optional)
            promo_code: Voucher code (optional)
            currency: Currency code (default: USD)
            customer_type: NEW_CUSTOMER or RECURRING (default: NEW_CUSTOMER)
            subtotal_transaction: Original amount before discount (optional)
            acquisition_method: VOUCHER, REFERRAL, or REFERRAL_VOUCHER (optional)
            custom_fields: Custom metadata (max 3 entries) (optional)
            invoice_id: External invoice ID (optional)
            customer_id: External customer ID (optional)
            customer_email: Customer email (optional)
            transaction_type: Transaction type (optional)
            description: Transaction description (optional)
            payment_gateway_transaction_id: Payment gateway transaction ID (optional)
            is_recurring: Whether transaction is recurring (optional)

        Returns:
            TransactionResponse with transaction and commission data

        Raises:
            HAVNValidationError: If payload validation fails
            HAVNAPIError: If API request fails

        Example:
            >>> result = client.transactions.send(
            ...     amount=10000,  # $100.00
            ...     referral_code="HAVN-MJ-001",
            ...     currency="USD",
            ...     customer_type="NEW_CUSTOMER",
            ...     custom_fields={"order_id": "ORD123"}
            ... )
            >>> print(f"Transaction: {result.transaction.transaction_id}")
            >>> print(f"Commissions: {len(result.commissions)} levels")
        """
        # Build payload
        payload = TransactionPayload(
            amount=amount,
            referral_code=referral_code,
            promo_code=promo_code,
            currency=currency,
            customer_type=customer_type,
            subtotal_transaction=subtotal_transaction,
            acquisition_method=acquisition_method,
            custom_fields=custom_fields,
            invoice_id=invoice_id,
            customer_id=customer_id,
            customer_email=customer_email,
            transaction_type=transaction_type,
            description=description,
            payment_gateway_transaction_id=payment_gateway_transaction_id,
            is_recurring=is_recurring,
        )

        # Validate payload
        try:
            payload.validate()
        except ValueError as e:
            raise HAVNValidationError(str(e))

        # Make API request
        response_data = self.client._make_request(
            method="POST", endpoint="/api/v1/webhook/transaction", payload=payload.to_dict()
        )

        # Parse response
        return TransactionResponse.from_dict(response_data)
