"""
Example 3: User Synchronization

This example demonstrates how to sync user data from Google OAuth.
"""

from havn import HAVNClient
from havn.exceptions import HAVNAPIError

# Initialize client
client = HAVNClient()


def sync_user_from_google_oauth():
    """Sync user data from Google OAuth"""
    try:
        # Sync user (typically called after Google OAuth callback)
        result = client.users.sync(
            email="user@example.com",
            name="John Doe",
            google_id="google_oauth_id_123",
            picture="https://lh3.googleusercontent.com/a/photo.jpg",
            create_associate=True,  # Auto-create associate
            upline_code="HAVN-MJ-001",  # Link to upline
            country_code="US",
        )

        # Display results
        print("✅ User sync successful!")
        print(f"User ID: {result.user.id}")
        print(f"Email: {result.user.email}")
        print(f"Name: {result.user.name}")
        print(f"User Created: {result.user_created}")
        print(f"Associate Created: {result.associate_created}")

        # Display associate info if created
        if result.associate:
            print(f"\n👤 Associate Information:")
            print(f"  Associate ID: {result.associate.associate_id}")
            print(f"  Referral Code: {result.associate.referral_code}")
            print(f"  Type: {result.associate.type}")
            print(f"  Active: {result.associate.is_active}")
            if result.associate.upline_id:
                print(f"  Upline ID: {result.associate.upline_id}")

    except HAVNAPIError as e:
        print(f"❌ Error: {e}")


def sync_existing_user():
    """Sync/update existing user"""
    try:
        # Update existing user (won't create new if email exists)
        result = client.users.sync(
            email="existing@example.com",
            name="Jane Smith",  # Updated name
            avatar="https://example.com/new-avatar.jpg",  # Updated avatar
            create_associate=False,  # Don't create associate if not exists
        )

        print("✅ User updated!")
        print(f"User Created: {result.user_created}")  # Should be False
        print(f"Name: {result.user.name}")

    except HAVNAPIError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("=== Sync New User from Google OAuth ===\n")
    sync_user_from_google_oauth()

    print("\n\n=== Update Existing User ===\n")
    sync_existing_user()
