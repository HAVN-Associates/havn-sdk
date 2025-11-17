"""
Auth webhook handler for SaaS company login
"""

from typing import Optional
from ..exceptions import HAVNValidationError


class AuthWebhook:
    """
    Auth webhook handler for SaaS company login

    Handles user login flow via webhook with temporary token generation.

    Example:
        >>> client = HAVNClient(api_key="...", webhook_secret="...")
        >>> redirect_url = client.auth.login(email="user@example.com")
        >>> # Redirect user browser to: redirect_url
        >>> # Frontend will handle auto-login with temp token
    """

    def __init__(self, client):
        """
        Initialize auth webhook handler

        Args:
            client: HAVNClient instance
        """
        self.client = client

    def login(self, email: str) -> str:
        """
        Login user from SaaS company via webhook

        This method initiates the login flow for a user. The backend will:
        1. Validate user exists and is active
        2. Generate a temporary token
        3. Return redirect URL to HAVN frontend with token
        4. Frontend will auto-login the user

        Args:
            email: User email address (required)

        Returns:
            Redirect URL string to send user's browser to

        Raises:
            HAVNValidationError: If email is invalid
            HAVNAPIError: If login fails (user not found, inactive, etc.)
            HAVNAuthError: If API key/signature validation fails

        Example:
            >>> # Simple login
            >>> redirect_url = client.auth.login(email="user@example.com")
            >>> # In Flask: return redirect(redirect_url)
            >>> # In Django: return HttpResponseRedirect(redirect_url)
            >>> # In FastAPI: return RedirectResponse(url=redirect_url)

        Flow:
            1. SaaS company calls this method
            2. SDK sends webhook to HAVN backend with API key + HMAC signature
            3. Backend validates user exists and is active
            4. Backend generates temporary token
            5. Backend returns redirect URL: {FRONTEND_URL}/login?token={temp_token}
            6. SaaS redirects user browser to returned URL
            7. HAVN frontend auto-logins user with token
            8. User is logged in to HAVN

        Security:
            - API key authentication
            - HMAC signature validation
            - User existence validation
            - Active status check
            - Temporary token (single-use)
            - Rate limited: 20 requests/minute
        """
        # Validate email
        if not email or not isinstance(email, str) or "@" not in email:
            raise HAVNValidationError("Valid email address is required")

        # Prepare payload
        payload = {"email": email.strip().lower()}

        # Make request to login endpoint
        # Backend will return JSON response because we send Accept: application/json header
        response = self.client._make_request(
            method="POST", endpoint="/api/v1/webhook/login", payload=payload
        )

        # Extract redirect URL from response
        # Backend returns: {"data": {"redirect_url": "...", "token": "..."}, "success": true}
        data = response.get("data", {})
        redirect_url = data.get("redirect_url")

        if not redirect_url:
            raise HAVNValidationError(
                "Backend did not return redirect URL. Please check API response."
            )

        return redirect_url
