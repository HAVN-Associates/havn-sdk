"""
User sync webhook handler

DEPRECATED: This module is no longer supported as of HAVN SDK v2.0.0

User management should now be handled on the SaaS company side.
Referral data is passed via public referral links using query parameters.

See docs/REFERRAL_PUBLIC_LINK.md for the new integration approach.

Migration Guide:
1. Remove all client.users.sync() and client.users.sync_bulk() calls
2. Implement referral param capture in your login page
3. Attach referral data to users after successful login
4. Use existing client.transactions.send() for transaction tracking

For more details, see: https://docs.havn.com/referral-public-link
"""

import warnings
from typing import Optional, List, Dict, Any
from ..models.user_sync import (
    UserSyncPayload,
    UserSyncResponse,
    BulkUserSyncPayload,
    BulkUserSyncResponse,
)
from ..exceptions import HAVNValidationError


class UserSyncWebhook:
    """
    User sync webhook handler
    
    .. deprecated:: 2.0.0
        User sync is no longer supported. Use public referral links instead.
        See docs/REFERRAL_PUBLIC_LINK.md for migration guide.

    Handles syncing user data from Google OAuth or other sources.

    Example (DEPRECATED):
        >>> # THIS NO LONGER WORKS - DO NOT USE
        >>> client = HAVNClient(api_key="...", webhook_secret="...")
        >>> result = client.users.sync(  # DEPRECATED
        ...     email="user@example.com",
        ...     name="John Doe",
        ...     google_id="google123"
        ... )
    """

    def __init__(self, client):
        """
        Initialize user sync webhook handler
        
        .. deprecated:: 2.0.0
            This class is deprecated and will be removed in v3.0.0

        Args:
            client: HAVNClient instance
        """
        warnings.warn(
            "UserSyncWebhook is deprecated and will be removed in v3.0.0. "
            "User management should be handled on SaaS company side. "
            "See docs/REFERRAL_PUBLIC_LINK.md for migration guide.",
            DeprecationWarning,
            stacklevel=2
        )
        self.client = client

    def sync(
        self,
        email: str,
        name: str,
        google_id: Optional[str] = None,
        picture: Optional[str] = None,
        avatar: Optional[str] = None,
        upline_code: Optional[str] = None,
        referral_code: Optional[str] = None,
        country_code: Optional[str] = None,
        create_associate: bool = True,
        is_owner: bool = False,
    ) -> UserSyncResponse:
        """
        Sync user data to HAVN API
        
        .. deprecated:: 2.0.0
            This method is deprecated. Handle user creation on your SaaS side.

        Args:
            email: User email (required)
            name: User full name (required)
            google_id: Google OAuth ID (optional)
            picture: Profile picture URL (optional)
            avatar: Avatar URL (optional)
            upline_code: Upline associate referral code (optional)
            referral_code: Referral code for associate creation (optional)
            country_code: Country code (2 letters, ISO 3166-1 alpha-2) (optional)
            create_associate: Whether to create associate (default: True)
            is_owner: Set role sebagai "owner" instead of "partner" (default: False)

        Returns:
            UserSyncResponse with user and associate data

        Raises:
            HAVNValidationError: If payload validation fails
            HAVNAPIError: If API request fails

        Example:
            >>> result = client.users.sync(
            ...     email="user@example.com",
            ...     name="John Doe",
            ...     google_id="google123",
            ...     picture="https://example.com/photo.jpg",
            ...     create_associate=True,
            ...     upline_code="HAVN-MJ-001",
            ...     is_owner=True
            ... )
            >>> print(f"User: {result.user.id}")
            >>> if result.associate:
            ...     print(f"Associate: {result.associate.referral_code}")
        """
        # Build payload
        payload = UserSyncPayload(
            email=email,
            name=name,
            google_id=google_id,
            picture=picture,
            avatar=avatar,
            upline_code=upline_code,
            referral_code=referral_code,
            country_code=country_code,
            create_associate=create_associate,
            is_owner=is_owner,
        )

        # Validate payload
        try:
            payload.validate()
        except ValueError as e:
            raise HAVNValidationError(str(e))

        # Make API request
        response_data = self.client._make_request(
            method="POST",
            endpoint="/api/v1/webhook/user-sync",
            payload=payload.to_dict(),
        )

        # Parse response
        return UserSyncResponse.from_dict(response_data)

    def sync_bulk(
        self,
        users: List[Dict[str, Any]],
        upline_code: Optional[str] = None,
        referral_code: Optional[str] = None,
        create_associate: Optional[bool] = None,
        is_owner: Optional[bool] = None,
    ) -> BulkUserSyncResponse:
        """
        Sync multiple users to HAVN API (bulk sync)
        
        .. deprecated:: 2.0.0
            This method is deprecated. Handle user creation on your SaaS side.

        Args:
            users: List of user data dictionaries (required, max 50)
            upline_code: Shared upline referral code (optional)
            referral_code: Shared referral code for linking to existing associate (optional)
            create_associate: Shared flag for associate creation (optional)
            is_owner: Shared flag untuk set role sebagai "owner" (optional, default: False)

        Returns:
            BulkUserSyncResponse with results and summary

        Raises:
            HAVNValidationError: If payload validation fails
            HAVNAPIError: If API request fails

        Example:
            >>> result = client.users.sync_bulk(
            ...     users=[
            ...         {"email": "user1@example.com", "name": "John Doe", "is_owner": True},
            ...         {"email": "user2@example.com", "name": "Jane Smith"},
            ...     ],
            ...     upline_code="HAVN-MJ-001",
            ...     referral_code="HAVN-SE-002"
            ... )
            >>> print(f"Success: {result.summary.success}/{result.summary.total}")
            >>> print(f"Referral code: {result.referral_code}")
        """
        # Build payload
        payload = BulkUserSyncPayload(
            users=users,
            upline_code=upline_code,
            referral_code=referral_code,
            create_associate=create_associate,
            is_owner=is_owner,
        )

        # Validate payload
        try:
            payload.validate()
        except ValueError as e:
            raise HAVNValidationError(str(e))

        # Make API request
        response_data = self.client._make_request(
            method="POST",
            endpoint="/api/v1/webhook/user-sync",
            payload=payload.to_dict(),
        )

        # Parse response
        return BulkUserSyncResponse.from_dict(response_data)
