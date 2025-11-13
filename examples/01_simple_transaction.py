"""
Example 1: Simple Transaction

This example demonstrates how to send a basic transaction to HAVN API.
"""

from havn import HAVNClient
from havn.exceptions import HAVNAPIError, HAVNAuthError, HAVNValidationError

# Initialize client
# You can either pass credentials explicitly or use environment variables
client = HAVNClient(
    api_key="your_api_key_here",
    webhook_secret="your_webhook_secret_here",
    base_url="https://api.havn.com",  # Optional, defaults to production
)

# Or use environment variables (HAVN_API_KEY, HAVN_WEBHOOK_SECRET)
# client = HAVNClient()


def send_simple_transaction():
    """Send a simple transaction"""
    try:
        # Send transaction
        result = client.transactions.send(
            amount=10000,  # $100.00 in cents
            referral_code="HAVN-MJ-001",  # Associate referral code
            currency="USD",
        )

        # Access response data
        print("✅ Transaction successful!")
        print(f"Transaction ID: {result.transaction.transaction_id}")
        print(f"Amount: ${result.transaction.amount / 100:.2f}")
        print(f"Status: {result.transaction.status}")
        print(f"Commissions distributed: {len(result.commissions)} levels")

        # Print commission details
        print("\n💰 Commission Distribution:")
        for comm in result.commissions:
            print(
                f"  Level {comm.level}: Associate {comm.associate_id} - "
                f"${comm.amount / 100:.2f} ({comm.percentage}%)"
            )

    except HAVNAuthError as e:
        print(f"❌ Authentication failed: {e}")
    except HAVNValidationError as e:
        print(f"❌ Validation error: {e}")
    except HAVNAPIError as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    send_simple_transaction()
