"""
Voucher webhook handler
"""

from typing import Optional
from ..models.voucher import VoucherValidationPayload
from ..exceptions import HAVNValidationError, HAVNAPIError


class VoucherWebhook:
    """
    Voucher webhook handler

    Handles voucher validation via HAVN API.

    Example:
        >>> client = HAVNClient(api_key="...", webhook_secret="...")
        >>> try:
        ...     is_valid = client.vouchers.validate(
        ...         voucher_code="VOUCHER123",
        ...         amount=10000
        ...     )
        ...     print("✅ Voucher is valid")
        ... except Exception as e:
        ...     print(f"❌ Voucher invalid: {e}")
    """

    def __init__(self, client):
        """
        Initialize voucher webhook handler

        Args:
            client: HAVNClient instance
        """
        self.client = client

    def validate(
        self,
        voucher_code: str,
        amount: Optional[int] = None,
        currency: Optional[str] = None,
    ) -> bool:
        """
        Validate voucher code

        This endpoint returns only HTTP status code (no response body).
        - 200 OK: Voucher is valid
        - 400/404/422: Voucher is invalid

        Args:
            voucher_code: Voucher code to validate (required)
            amount: Transaction amount in cents (optional)
            currency: Currency code (optional)

        Returns:
            True if voucher is valid

        Raises:
            HAVNValidationError: If payload validation fails
            HAVNAPIError: If voucher is invalid or API request fails

        Example:
            >>> # Valid voucher
            >>> is_valid = client.vouchers.validate("VOUCHER123", amount=10000)
            >>> print(is_valid)  # True
            
            >>> # Invalid voucher (raises exception)
            >>> try:
            ...     client.vouchers.validate("INVALID", amount=10000)
            ... except HAVNAPIError as e:
            ...     print(f"Invalid: {e}")
        """
        # Build payload
        payload = VoucherValidationPayload(
            voucher_code=voucher_code, amount=amount, currency=currency
        )

        # Validate payload
        try:
            payload.validate()
        except ValueError as e:
            raise HAVNValidationError(str(e))

        # Make API request (this endpoint returns status code only, no body)
        try:
            self.client._make_request(
                method="POST",
                endpoint="/api/v1/webhook/voucher/validate",
                payload=payload.to_dict(),
            )
            return True
        except HAVNAPIError as e:
            # Re-raise with clearer message for voucher validation
            if e.status_code == 404:
                raise HAVNAPIError("Voucher not found", status_code=404)
            elif e.status_code == 400:
                raise HAVNAPIError(
                    "Voucher invalid (expired, used up, or inactive)", status_code=400
                )
            elif e.status_code == 422:
                raise HAVNAPIError(
                    "Amount does not meet voucher requirements", status_code=422
                )
            else:
                raise
