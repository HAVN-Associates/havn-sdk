"""
Example 2: Transaction with Voucher

This example demonstrates how to send a transaction with a voucher code.
"""

from havn import HAVNClient
from havn.exceptions import HAVNAPIError

# Initialize client (use environment variables)
client = HAVNClient()


def send_transaction_with_voucher():
    """Send transaction with voucher discount"""
    try:
        # First, validate the voucher (optional but recommended)
        print("🔍 Validating voucher...")
        is_valid = client.vouchers.validate(
            voucher_code="VOUCHER123", amount=10000, currency="USD"
        )
        print(f"✅ Voucher is valid: {is_valid}")

        # Send transaction with voucher
        print("\n📦 Sending transaction with voucher...")
        result = client.transactions.send(
            amount=8000,  # After discount: $80.00
            payment_gateway_transaction_id="stripe_9876543210",  # Required
            payment_gateway="STRIPE",
            customer_email="customer@example.com",  # Required
            subtotal_transaction=10000,  # Before discount: $100.00
            promo_code="VOUCHER123",  # Voucher code
            referral_code="HAVN-MJ-001",  # Associate referral code
            currency="USD",
            custom_fields={
                "order_id": "ORD123456",
                "payment_method": "credit_card",
            },
            # acquisition_method akan auto-determined sebagai REFERRAL_VOUCHER (karena ada promo_code DAN referral_code)
        )

        # Display results
        print("✅ Transaction with voucher successful!")
        print(f"Transaction ID: {result.transaction.transaction_id}")
        print(f"Original Amount: ${result.transaction.subtotal_transaction / 100:.2f}")
        print(f"Discount: ${result.transaction.subtotal_discount / 100:.2f}")
        print(f"Final Amount: ${result.transaction.amount / 100:.2f}")
        print(f"Acquisition Method: {result.transaction.acquisition_method}")

    except HAVNAPIError as e:
        if e.status_code == 404:
            print("❌ Voucher not found")
        elif e.status_code == 400:
            print("❌ Voucher invalid (expired, used up, or inactive)")
        else:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    send_transaction_with_voucher()
