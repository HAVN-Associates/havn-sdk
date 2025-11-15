"""
Example 5: Test Mode (Dry-Run)

This example demonstrates how to use test mode for testing without saving data.
"""

from havn import HAVNClient

# Initialize client in TEST MODE
# In test mode, API requests will succeed but won't save data to database
client = HAVNClient(test_mode=True)


def test_transaction_in_dry_run():
    """Send transaction in test mode"""
    print("=== Test Mode (Dry-Run) ===\n")
    print("🧪 Test mode enabled - no data will be saved\n")

    try:
        # Send transaction (won't be saved to database)
        result = client.transactions.send(
            amount=10000,  # $100.00
            payment_gateway_transaction_id="stripe_test_123",
            customer_email="test@example.com",
            referral_code="HAVN-MJ-001",
            currency="USD",
            customer_type="NEW_CUSTOMER",
        )

        # Response will be returned as normal
        print("✅ Test transaction successful!")
        print(f"Transaction ID: {result.transaction.transaction_id}")
        print(f"Amount: ${result.transaction.amount / 100:.2f}")
        print(f"Commissions: {len(result.commissions)} levels")
        print("\n⚠️  This transaction was NOT saved to database (test mode)")

    except Exception as e:
        print(f"❌ Error: {e}")


def test_user_sync_in_dry_run():
    """Sync user in test mode"""
    print("\n=== User Sync in Test Mode ===\n")

    try:
        # Sync user (won't be saved to database)
        result = client.users.sync(
            email="test@example.com",
            name="Test User",
            create_associate=True,
            upline_code="HAVN-MJ-001",
        )

        print("✅ Test user sync successful!")
        print(f"User: {result.user.email}")
        print(f"User Created: {result.user_created}")
        print("\n⚠️  This user was NOT saved to database (test mode)")

    except Exception as e:
        print(f"❌ Error: {e}")


def compare_test_vs_production():
    """Compare test mode vs production mode"""
    print("\n=== Test Mode vs Production Mode ===\n")

    # Test mode client
    test_client = HAVNClient(test_mode=True)

    # Production mode client
    prod_client = HAVNClient(test_mode=False)

    print("Test Mode Client:")
    print(f"  Base URL: {test_client.base_url}")
    print(f"  Test Mode: {test_client.test_mode}")
    print(f"  Behavior: API calls succeed but don't save data\n")

    print("Production Mode Client:")
    print(f"  Base URL: {prod_client.base_url}")
    print(f"  Test Mode: {prod_client.test_mode}")
    print(f"  Behavior: API calls save data to database\n")

    print("💡 Use test mode for:")
    print("  - Integration testing")
    print("  - Development environment")
    print("  - CI/CD pipelines")
    print("  - API validation without side effects")


if __name__ == "__main__":
    test_transaction_in_dry_run()
    test_user_sync_in_dry_run()
    compare_test_vs_production()
