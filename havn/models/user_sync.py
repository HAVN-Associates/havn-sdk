"""
User sync models for HAVN SDK
"""

from typing import Optional, Dict, Any
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
                raise ValueError("Country code must be 2 characters (ISO 3166-1 alpha-2)")
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
