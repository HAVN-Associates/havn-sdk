"""
Transaction webhook handler
"""

from typing import Dict, Any, Optional
from ..models.transaction import TransactionPayload, TransactionResponse
from ..models.voucher_list import is_havn_voucher_code
from ..exceptions import HAVNValidationError
from ..utils.currency import get_currency_converter
from ..constants import USD_CURRENCY


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
        auto_convert: bool = True,
    ) -> TransactionResponse:
        """
        Send transaction to HAVN API

        Important: If promo_code is a local voucher (not HAVN format),
        it will NOT be sent to HAVN API. Only referral_code will be sent.
        Local vouchers should be handled separately by SaaS company.

        **Currency Conversion:**
        - If currency != "USD" and auto_convert=True (default), SDK will automatically
          convert amount to USD cents before sending to HAVN.
        - Original amount and currency info are preserved in custom_fields for audit.
        - HAVN always stores amounts in USD cents (single source of truth).

        Args:
            amount: Final transaction amount (required)
                - If currency="USD": amount in USD cents
                - If currency != "USD" and auto_convert=True: amount in source currency's smallest unit
                - If currency != "USD" and auto_convert=False: amount in USD cents (conversion handled by backend)
            referral_code: Associate referral code (optional)
            promo_code: Voucher code (HAVN or local).
                - If HAVN voucher (starts with "HAVN-"): will be sent to API (referral_code + promo_code)
                - If local voucher: will NOT be sent (only referral_code sent)
            currency: Currency code (default: USD)
            customer_type: NEW_CUSTOMER or RECURRING (default: NEW_CUSTOMER)
            subtotal_transaction: Original amount before discount (optional)
                - Same currency rules as amount
            acquisition_method: VOUCHER, REFERRAL, or REFERRAL_VOUCHER (optional)
            custom_fields: Custom metadata (max 3 entries) (optional)
            invoice_id: External invoice ID (optional)
            customer_id: External customer ID (optional)
            customer_email: Customer email (optional)
            transaction_type: Transaction type (optional)
            description: Transaction description (optional)
            payment_gateway_transaction_id: Payment gateway transaction ID (optional)
            is_recurring: Whether transaction is recurring (optional)
            auto_convert: Whether to automatically convert non-USD amounts to USD cents (default: True)
                - If True: SDK converts to USD cents before sending
                - If False: Amount sent as-is (backend will handle conversion)

        Returns:
            TransactionResponse with transaction and commission data

        Raises:
            HAVNValidationError: If payload validation fails
            HAVNAPIError: If API request fails or currency conversion fails

        Example:
            >>> # Transaction with HAVN voucher (both referral_code and promo_code sent)
            >>> result = client.transactions.send(
            ...     amount=8000,
            ...     referral_code="HAVN-MJ-001",
            ...     promo_code="HAVN-AQNEO-S08-ABC123",  # HAVN voucher
            ...     currency="USD"
            ... )
            >>>
            >>> # Transaction with local voucher (only referral_code sent)
            >>> result = client.transactions.send(
            ...     amount=8000,
            ...     referral_code="HAVN-MJ-001",
            ...     promo_code="LOCAL123",  # Local voucher - not sent to HAVN
            ...     currency="USD"
            ... )
            >>>
            >>> # Transaction with auto-conversion (IDR to USD)
            >>> result = client.transactions.send(
            ...     amount=150000,  # IDR rupiah
            ...     currency="IDR",  # SDK auto-converts to USD cents
            ...     referral_code="HAVN-MJ-001"
            ... )
            >>>
            >>> # Transaction with auto-conversion disabled (let backend handle)
            >>> result = client.transactions.send(
            ...     amount=10000,  # Already in USD cents
            ...     currency="IDR",  # Info only, backend will convert
            ...     auto_convert=False,
            ...     referral_code="HAVN-MJ-001"
            ... )
        """
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

        # Auto-convert non-USD currencies to USD cents if enabled
        if auto_convert and currency_to_send != USD_CURRENCY:
            try:
                converter = get_currency_converter()

                # Convert amount
                converted_amount = converter.convert_to_usd_cents(amount, currency)
                amount_to_send = converted_amount["amount_cents"]

                # Store original amount and conversion metadata in custom_fields
                custom_fields_with_metadata["original_currency"] = currency
                custom_fields_with_metadata["original_amount"] = amount
                custom_fields_with_metadata["exchange_rate"] = converted_amount[
                    "exchange_rate"
                ]

                # Convert subtotal_transaction if provided
                if subtotal_transaction is not None:
                    converted_subtotal = converter.convert_to_usd_cents(
                        subtotal_transaction, currency
                    )
                    subtotal_to_send = converted_subtotal["amount_cents"]
                    custom_fields_with_metadata["original_subtotal"] = (
                        subtotal_transaction
                    )

                # Update currency to USD after conversion
                currency_to_send = USD_CURRENCY

            except ValueError as e:
                # Currency conversion failed (invalid currency or exchange rate unavailable)
                raise HAVNValidationError(
                    f"Currency conversion failed: {str(e)}. "
                    "If you want to send amount already in USD cents, set auto_convert=False."
                )

        # Build payload
        payload = TransactionPayload(
            amount=amount_to_send,
            referral_code=referral_code,
            promo_code=promo_code_to_send,  # Only HAVN vouchers are sent
            currency=currency_to_send,  # USD after conversion, or original if auto_convert=False
            customer_type=customer_type,
            subtotal_transaction=subtotal_to_send,
            acquisition_method=acquisition_method,
            custom_fields=custom_fields_with_metadata
            if custom_fields_with_metadata
            else None,
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
            method="POST",
            endpoint="/api/v1/webhook/transaction",
            payload=payload.to_dict(),
        )

        # Parse response
        return TransactionResponse.from_dict(response_data)
