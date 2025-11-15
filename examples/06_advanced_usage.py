"""
Example 6: Advanced Usage

This example demonstrates advanced SDK features like context managers,
custom configuration, and batch operations.
"""

from havn import HAVNClient
from havn.exceptions import HAVNAPIError


def use_context_manager():
    """Use client as context manager (auto-cleanup)"""
    print("=== Context Manager Usage ===\n")

    # Client will automatically close session on exit
    with HAVNClient() as client:
        result = client.transactions.send(
            amount=10000,
            payment_gateway_transaction_id="stripe_001",
            customer_email="customer@example.com",
            referral_code="HAVN-MJ-001",
        )
        print(f"✅ Transaction: {result.transaction.transaction_id}")

    print("✅ Client session closed automatically\n")


def custom_configuration():
    """Use custom configuration"""
    print("=== Custom Configuration ===\n")

    # Create client with custom timeouts and retries
    client = HAVNClient(
        api_key="your_api_key",
        webhook_secret="your_webhook_secret",
        base_url="https://api.havn.com",
        timeout=60,  # 60 seconds timeout
        max_retries=5,  # 5 retry attempts
        backoff_factor=1.0,  # 1 second backoff between retries
        test_mode=False,
    )

    print(f"Client configuration:")
    print(f"  Base URL: {client.base_url}")
    print(f"  Timeout: {client.timeout} seconds")
    print(f"  Max Retries: {client.max_retries}")
    print(f"  Backoff Factor: {client.backoff_factor}")
    print(f"  Test Mode: {client.test_mode}\n")


def batch_transactions():
    """Send multiple transactions (simulated batch)"""
    print("=== Batch Transactions ===\n")

    client = HAVNClient()

    # List of transactions to send (with required fields)
    transactions = [
        {
            "amount": 5000,
            "payment_gateway_transaction_id": "stripe_001",
            "customer_email": "customer1@example.com",
            "referral_code": "HAVN-MJ-001",
        },
        {
            "amount": 7500,
            "payment_gateway_transaction_id": "stripe_002",
            "customer_email": "customer2@example.com",
            "referral_code": "HAVN-MJ-001",
        },
        {
            "amount": 10000,
            "payment_gateway_transaction_id": "stripe_003",
            "customer_email": "customer3@example.com",
            "referral_code": "HAVN-MJ-002",
        },
    ]

    results = []
    for i, txn in enumerate(transactions, 1):
        try:
            result = client.transactions.send(**txn)
            results.append(result)
            print(
                f"✅ Transaction {i}/{len(transactions)}: "
                f"${result.transaction.amount / 100:.2f} - "
                f"{result.transaction.transaction_id}"
            )
        except HAVNAPIError as e:
            print(f"❌ Transaction {i} failed: {e}")

    print(f"\n✅ Batch complete: {len(results)}/{len(transactions)} successful")


def use_environment_variables():
    """Use environment variables for configuration"""
    print("\n=== Environment Variables ===\n")

    # Set environment variables (in real app, set in shell or .env file)
    import os

    os.environ["HAVN_API_KEY"] = "your_api_key"
    os.environ["HAVN_WEBHOOK_SECRET"] = "your_webhook_secret"
    os.environ["HAVN_BASE_URL"] = "https://api.havn.com"
    os.environ["HAVN_TIMEOUT"] = "30"
    os.environ["HAVN_MAX_RETRIES"] = "3"

    # Client will read from environment variables
    client = HAVNClient()

    print("✅ Client initialized from environment variables")
    print(f"  Base URL: {client.base_url}")
    print(f"  Timeout: {client.timeout}")
    print(f"  Max Retries: {client.max_retries}\n")


def transaction_with_all_fields():
    """Send transaction with all optional fields"""
    print("=== Transaction with All Fields ===\n")

    client = HAVNClient()

    try:
        result = client.transactions.send(
            # Required
            amount=10000,  # $100.00 in cents
            payment_gateway_transaction_id="PG123456789",
            customer_email="customer@example.com",
            # Optional
            referral_code="HAVN-MJ-001",
            promo_code="VOUCHER123",
            currency="USD",
            customer_type="NEW_CUSTOMER",
            subtotal_transaction=12000,  # Before discount
            custom_fields={
                "order_id": "ORD123456",
                "payment_method": "credit_card",
                "customer_segment": "premium",
            },
            invoice_id="INV-2024-001",
            transaction_type="SUBSCRIPTION",
            description="Monthly subscription renewal",
            # acquisition_method akan auto-determined sebagai REFERRAL_VOUCHER (karena ada promo_code)
        )

        print("✅ Transaction with all fields successful!")
        print(f"Transaction ID: {result.transaction.transaction_id}")
        print(f"Amount: ${result.transaction.amount / 100:.2f}")
        print(f"Original: ${result.transaction.subtotal_transaction / 100:.2f}")
        print(f"Discount: ${result.transaction.subtotal_discount / 100:.2f}")

    except HAVNAPIError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    use_context_manager()
    custom_configuration()
    # batch_transactions()  # Uncomment to test
    use_environment_variables()
    # transaction_with_all_fields()  # Uncomment to test
