"""
Transaction webhook handler
"""

from typing import Dict, Any, Optional
from ..models.transaction import TransactionPayload, TransactionResponse
from ..models.voucher_list import is_havn_voucher_code
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
        payment_gateway_transaction_id: str,
        customer_email: str,
        referral_code: Optional[str] = None,
        promo_code: Optional[str] = None,
        currency: str = "USD",
        customer_type: str = "NEW_CUSTOMER",
        subtotal_transaction: Optional[int] = None,
        acquisition_method: Optional[str] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
        invoice_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        description: Optional[str] = None,
        server_side_conversion: bool = False,
    ) -> TransactionResponse:
        """
        Send transaction to HAVN API

        Important: If promo_code is a local voucher (not HAVN format),
        it will NOT be sent to HAVN API. Only referral_code will be sent.
        Local vouchers should be handled separately by SaaS company.

        **Currency Conversion:**
        - HAVN backend is the single source of truth for currency conversion.
        - SDK forwards the amount exactly as provided and relies on backend conversion
          when `server_side_conversion=True`.

        Args:
            amount: Final transaction amount (required)
                - If currency="USD": amount in USD cents
                - If currency != "USD": amount in that currency's smallest unit and set
                  `server_side_conversion=True` so backend converts it
            payment_gateway_transaction_id: Payment gateway transaction ID (required)
                - Must be non-empty string
                - Max 200 characters
            customer_email: Customer email (required, valid email format)
            referral_code: Associate referral code (optional)
            promo_code: Voucher code (HAVN or local).
                - If HAVN voucher (starts with "HAVN-"): will be sent to API (referral_code + promo_code)
                - If local voucher: will NOT be sent (only referral_code sent)
            currency: Currency code (default: USD)
            customer_type: NEW_CUSTOMER or RECURRING (default: NEW_CUSTOMER)
            subtotal_transaction: Original amount before discount (optional)
                - Same currency rules as amount
            acquisition_method: REFERRAL or REFERRAL_VOUCHER (optional, auto-determined)
                - REFERRAL_VOUCHER: Jika ada promo_code DAN referral_code (keduanya wajib)
                - REFERRAL: Jika hanya ada referral_code (tanpa promo_code)
                - Tidak ada "VOUCHER" standalone (voucher selalu dikaitkan dengan referral)
                - Jika tidak disediakan, akan auto-determined dari promo_code/referral_code
            custom_fields: Custom metadata (max 3 entries) (optional)
            invoice_id: External invoice ID (optional)
            transaction_type: Transaction type (optional, untuk logging)
            description: Transaction description (optional)
            server_side_conversion: If True, SDK sends original amount/currency and relies on
                HAVN backend to perform official conversion. If you're already sending USD cents,
                leave this False.

        Returns:
            TransactionResponse with transaction and commission data

        Raises:
            HAVNValidationError: If payload validation fails
            HAVNAPIError: If API request fails or currency conversion fails

        Example:
            >>> # Transaction with HAVN voucher (acquisition_method auto-determined)
            >>> result = client.transactions.send(
            ...     amount=8000,
            ...     payment_gateway_transaction_id="stripe_1234567890",
            ...     customer_email="customer@example.com",
            ...     referral_code="HAVN-MJ-001",
            ...     promo_code="HAVN-AQNEO-S08-ABC123",  # HAVN voucher
            ...     currency="USD"
            ...     # acquisition_method akan auto-determined sebagai REFERRAL_VOUCHER
            ... )
            >>>
            >>> # Transaction with local voucher (only referral_code sent)
            >>> result = client.transactions.send(
            ...     amount=8000,
            ...     payment_gateway_transaction_id="midtrans_9876543210",
            ...     customer_email="customer@example.com",
            ...     referral_code="HAVN-MJ-001",
            ...     promo_code="LOCAL123",  # Local voucher - not sent to HAVN
            ...     currency="USD"
            ...     # acquisition_method akan auto-determined sebagai REFERRAL
            ... )
            >>>
            >>> # Transaction with auto-conversion (IDR to USD)
            >>> result = client.transactions.send(
            ...     amount=150000,  # IDR rupiah
            ...     payment_gateway_transaction_id="stripe_111222333",
            ...     customer_email="customer@example.com",
            ...     currency="IDR",  # SDK auto-converts to USD cents
            ...     referral_code="HAVN-MJ-001"
            ...     # acquisition_method akan auto-determined sebagai REFERRAL
            ... )
            >>>
            >>> # Recurring transaction (customer_type="RECURRING")
            >>> result = client.transactions.send(
            ...     amount=10000,
            ...     payment_gateway_transaction_id="stripe_444555666",
            ...     customer_email="customer@example.com",
            ...     customer_type="RECURRING",
            ...     referral_code="HAVN-MJ-001"
            ... )
        """
        # Auto-determine acquisition_method if not provided (before voucher check)
        if not acquisition_method:
            if promo_code and is_havn_voucher_code(promo_code) and referral_code:
                # REFERRAL_VOUCHER requires both promo_code and referral_code
                acquisition_method = "REFERRAL_VOUCHER"
            elif referral_code:
                # REFERRAL: only referral_code (no promo_code)
                acquisition_method = "REFERRAL"
            else:
                acquisition_method = "FAIL"  # Will be validated by backend

        # Determine if promo_code is HAVN voucher
        # Only send promo_code to HAVN if it's a HAVN voucher
        promo_code_to_send = None
        if promo_code:
            if is_havn_voucher_code(promo_code):
                # HAVN voucher - send both referral_code and promo_code
                promo_code_to_send = promo_code
            # else: Local voucher - don't send promo_code, only referral_code

        # Handle currency conversion if needed
        amount_to_send = amount
        subtotal_to_send = subtotal_transaction
        currency_to_send = currency.upper().strip()
        custom_fields_with_metadata = custom_fields.copy() if custom_fields else {}

        # Build payload (required fields first)
        payload = TransactionPayload(
            amount=amount_to_send,
            payment_gateway_transaction_id=payment_gateway_transaction_id,
            customer_email=customer_email,
            referral_code=referral_code,
            promo_code=promo_code_to_send,  # Only HAVN vouchers are sent
            currency=currency_to_send,  # Uppercase original currency (backend handles conversion)
            customer_type=customer_type,
            subtotal_transaction=subtotal_to_send,
            acquisition_method=acquisition_method,  # Auto-determined if not provided
            custom_fields=custom_fields_with_metadata
            if custom_fields_with_metadata
            else None,
            invoice_id=invoice_id,
            transaction_type=transaction_type,
            description=description,
            server_side_conversion=server_side_conversion or None,
        )

        # Validate payload
        try:
            payload.validate()
        except ValueError as e:
            raise HAVNValidationError(str(e))

        # Make API request
        response_data = self.client._make_request(
            method="POST",
            endpoint="/api/v1/webhook/transaction",
            payload=payload.to_dict(),
        )

        # Parse response
        return TransactionResponse.from_dict(response_data)
