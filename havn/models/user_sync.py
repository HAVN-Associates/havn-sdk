"""
User sync models for HAVN SDK
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class UserSyncPayload:
    """
    User sync payload for webhook

    Attributes:
        email: User email (required)
        name: User full name (required)
        google_id: Google OAuth ID (optional)
        picture: Profile picture URL (optional)
        avatar: Avatar URL (optional)
        upline_code: Upline associate referral code (optional)
        referral_code: Referral code for associate creation (optional)
        country_code: Country code (optional)
        create_associate: Whether to create associate (default: True)
        is_owner: Set role sebagai "owner" instead of "partner" (default: False)

    Example:
        >>> payload = UserSyncPayload(
        ...     email="user@example.com",
        ...     name="John Doe",
        ...     google_id="google123",
        ...     create_associate=True
        ... )
    """

    email: str
    name: str
    google_id: Optional[str] = None
    picture: Optional[str] = None
    avatar: Optional[str] = None
    upline_code: Optional[str] = None
    referral_code: Optional[str] = None
    country_code: Optional[str] = None
    create_associate: bool = True
    is_owner: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, removing None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def validate(self) -> None:
        """
        Validate payload

        Raises:
            ValueError: If validation fails
        """
        from ..utils.validators import validate_email, validate_referral_code

        # Validate email
        validate_email(self.email)

        # Validate name
        if not self.name or not self.name.strip():
            raise ValueError("Name cannot be empty")

        if len(self.name) > 200:
            raise ValueError("Name cannot exceed 200 characters")

        # Validate upline_code
        validate_referral_code(self.upline_code)

        # Validate referral_code
        validate_referral_code(self.referral_code)

        # Validate country_code
        if self.country_code is not None:
            if len(self.country_code) != 2:
                raise ValueError(
                    "Country code must be 2 characters (ISO 3166-1 alpha-2)"
                )
            if not self.country_code.isupper():
                raise ValueError("Country code must be uppercase")


@dataclass
class UserData:
    """User data from response"""

    id: str
    email: str
    name: str
    is_active: bool
    google_id: Optional[str] = None
    avatar: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserData":
        """Create from dictionary"""
        return cls(
            id=data.get("id", ""),
            email=data.get("email", ""),
            name=data.get("name", ""),
            is_active=data.get("is_active", False),
            google_id=data.get("google_id"),
            avatar=data.get("avatar"),
        )


@dataclass
class AssociateData:
    """Associate data from response"""

    associate_id: str
    associate_name: str
    referral_code: str
    type: str
    is_active: bool
    upline_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssociateData":
        """Create from dictionary"""
        return cls(
            associate_id=data.get("associate_id", ""),
            associate_name=data.get("associate_name", ""),
            referral_code=data.get("referral_code", ""),
            type=data.get("type", ""),
            is_active=data.get("is_active", False),
            upline_id=data.get("upline_id"),
        )


@dataclass
class UserSyncResponse:
    """
    User sync webhook response

    Attributes:
        success: Whether request was successful
        message: Response message
        user_created: Whether user was created (vs updated)
        associate_created: Whether associate was created
        user: User data
        associate: Associate data (if created)
        raw_response: Raw response dictionary
    """

    success: bool
    message: str
    user_created: bool
    associate_created: bool
    user: UserData
    associate: Optional[AssociateData] = None
    raw_response: Dict[str, Any] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSyncResponse":
        """
        Create from API response dictionary

        Args:
            data: Response dictionary from API

        Returns:
            UserSyncResponse instance
        """
        user_data = data.get("user", {})
        associate_data = data.get("associate")

        return cls(
            success=data.get("success", False),
            message=data.get("message", ""),
            user_created=data.get("user_created", False),
            associate_created=data.get("associate_created", False),
            user=UserData.from_dict(user_data),
            associate=AssociateData.from_dict(associate_data)
            if associate_data
            else None,
            raw_response=data,
        )


@dataclass
class BulkUserSyncPayload:
    """
    Bulk user sync payload for webhook

    Attributes:
        users: List of user data (required, max 50)
        upline_code: Shared upline referral code (optional)
        referral_code: Shared referral code for linking to existing associate (optional)
        create_associate: Shared flag for associate creation (optional)
        is_owner: Shared flag untuk set role sebagai "owner" (optional, default: False)

    Example:
        >>> payload = BulkUserSyncPayload(
        ...     users=[
        ...         {"email": "user1@example.com", "name": "John Doe"},
        ...         {"email": "user2@example.com", "name": "Jane Smith"},
        ...     ],
        ...     upline_code="HAVN-MJ-001",
        ...     referral_code="HAVN-SE-002"
        ... )
    """

    users: List[Dict[str, Any]]
    upline_code: Optional[str] = None
    referral_code: Optional[str] = None
    create_associate: Optional[bool] = None
    is_owner: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, removing None values"""
        result = {"users": self.users}
        if self.upline_code is not None:
            result["upline_code"] = self.upline_code
        if self.referral_code is not None:
            result["referral_code"] = self.referral_code
        if self.create_associate is not None:
            result["create_associate"] = self.create_associate
        if self.is_owner is not None:
            result["is_owner"] = self.is_owner
        return result

    def validate(self) -> None:
        """
        Validate payload

        Raises:
            ValueError: If validation fails
        """
        from ..utils.validators import validate_email, validate_referral_code

        # Validate users list
        if not isinstance(self.users, list):
            raise ValueError("'users' must be a list")

        if len(self.users) == 0:
            raise ValueError("'users' cannot be empty")

        if len(self.users) > 50:
            raise ValueError(f"Maximum 50 users per batch. Received {len(self.users)}")

        # Validate each user
        for idx, user in enumerate(self.users):
            if not isinstance(user, dict):
                raise ValueError(f"User at index {idx} must be a dictionary")

            email = user.get("email")
            name = user.get("name")

            if not email or not name:
                raise ValueError(
                    f"User at index {idx}: missing required field 'email' or 'name'"
                )

            validate_email(email)

            if not name.strip():
                raise ValueError(f"User at index {idx}: name cannot be empty")

            if len(name) > 200:
                raise ValueError(
                    f"User at index {idx}: name cannot exceed 200 characters"
                )

            # Validate optional fields per user
            validate_referral_code(user.get("upline_code"))
            validate_referral_code(user.get("referral_code"))

            country_code = user.get("country_code")
            if country_code is not None:
                if len(country_code) != 2:
                    raise ValueError(
                        f"User at index {idx}: country code must be 2 characters"
                    )
                if not country_code.isupper():
                    raise ValueError(
                        f"User at index {idx}: country code must be uppercase"
                    )

            # Validate is_owner per-user
            if "is_owner" in user:
                if not isinstance(user.get("is_owner"), bool):
                    raise ValueError(f"User at index {idx}: is_owner must be boolean")

        # Validate shared fields
        validate_referral_code(self.upline_code)
        validate_referral_code(self.referral_code)

        # Validate shared is_owner
        if self.is_owner is not None:
            if not isinstance(self.is_owner, bool):
                raise ValueError("is_owner must be boolean")


@dataclass
class BulkSyncSummary:
    """Bulk sync summary"""

    total: int
    success: int
    errors: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BulkSyncSummary":
        """Create from dictionary"""
        return cls(
            total=data.get("total", 0),
            success=data.get("success", 0),
            errors=data.get("errors", 0),
        )


@dataclass
class BulkUserSyncResponse:
    """
    Bulk user sync webhook response

    Attributes:
        success: Whether request was successful
        message: Response message
        results: List of user sync results
        summary: Summary statistics
        referral_code: Referral code from first successful result (for next batch)
        errors: List of errors (if any)
        raw_response: Raw response dictionary
    """

    success: bool
    message: str
    results: List[UserSyncResponse]
    summary: BulkSyncSummary
    referral_code: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None
    raw_response: Dict[str, Any] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BulkUserSyncResponse":
        """
        Create from API response dictionary

        Args:
            data: Response dictionary from API

        Returns:
            BulkUserSyncResponse instance
        """
        results_data = data.get("results", [])
        summary_data = data.get("summary", {})

        return cls(
            success=data.get("success", False),
            message=data.get("message", ""),
            results=[UserSyncResponse.from_dict(result) for result in results_data],
            summary=BulkSyncSummary.from_dict(summary_data),
            referral_code=data.get("referral_code"),
            errors=data.get("errors"),
            raw_response=data,
        )
