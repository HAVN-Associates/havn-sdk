"""
Example 4: Error Handling

This example demonstrates proper error handling with HAVN SDK.
"""

from havn import HAVNClient
from havn.exceptions import (
    HAVNError,
    HAVNAPIError,
    HAVNAuthError,
    HAVNValidationError,
    HAVNNetworkError,
)

# Initialize client
client = HAVNClient()


def handle_validation_errors():
    """Example: Handling validation errors"""
    print("=== Validation Error Example ===\n")

    try:
        # This will raise validation error (negative amount)
        result = client.transactions.send(
            amount=-100,  # Invalid: negative amount
            referral_code="HAVN-MJ-001",
        )
    except HAVNValidationError as e:
        print(f"✅ Caught validation error: {e}")
        print(f"   Error type: {type(e).__name__}")


def handle_authentication_errors():
    """Example: Handling authentication errors"""
    print("\n=== Authentication Error Example ===\n")

    try:
        # Create client with invalid credentials
        bad_client = HAVNClient(
            api_key="invalid_api_key", webhook_secret="invalid_secret"
        )

        # This will raise authentication error
        result = bad_client.transactions.send(
            amount=10000, referral_code="HAVN-MJ-001"
        )
    except HAVNAuthError as e:
        print(f"✅ Caught authentication error: {e}")
        print(f"   Error type: {type(e).__name__}")


def handle_api_errors():
    """Example: Handling API errors"""
    print("\n=== API Error Example ===\n")

    try:
        # Validate non-existent voucher
        client.vouchers.validate(voucher_code="NONEXISTENT123", amount=10000)
    except HAVNAPIError as e:
        print(f"✅ Caught API error: {e}")
        print(f"   Status code: {e.status_code}")
        print(f"   Error type: {type(e).__name__}")


def handle_network_errors():
    """Example: Handling network errors"""
    print("\n=== Network Error Example ===\n")

    try:
        # Create client with invalid URL
        bad_client = HAVNClient(
            api_key="key", webhook_secret="secret", base_url="https://invalid-url-that-does-not-exist.com"
        )

        # This will raise network error
        result = bad_client.transactions.send(
            amount=10000, referral_code="HAVN-MJ-001"
        )
    except HAVNNetworkError as e:
        print(f"✅ Caught network error: {e}")
        print(f"   Error type: {type(e).__name__}")
        if e.original_error:
            print(f"   Original error: {e.original_error}")


def handle_all_errors():
    """Example: Comprehensive error handling"""
    print("\n=== Comprehensive Error Handling ===\n")

    try:
        result = client.transactions.send(
            amount=10000,
            referral_code="HAVN-MJ-001",
            custom_fields={"key": "value"},
        )
        print(f"✅ Success: {result.transaction.transaction_id}")

    except HAVNValidationError as e:
        print(f"❌ Validation Error: {e}")
        # Handle validation errors (fix data and retry)

    except HAVNAuthError as e:
        print(f"❌ Authentication Error: {e}")
        # Handle auth errors (check credentials)

    except HAVNNetworkError as e:
        print(f"❌ Network Error: {e}")
        # Handle network errors (retry with backoff)

    except HAVNAPIError as e:
        print(f"❌ API Error: {e} (status: {e.status_code})")
        # Handle API errors (check response)

    except HAVNError as e:
        print(f"❌ HAVN Error: {e}")
        # Handle generic HAVN errors

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        # Handle unexpected errors


if __name__ == "__main__":
    handle_validation_errors()
    handle_authentication_errors()
    handle_api_errors()
    # handle_network_errors()  # Uncomment to test (will be slow)
    handle_all_errors()
