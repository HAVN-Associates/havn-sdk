"""
Custom exceptions for HAVN SDK
"""


class HAVNError(Exception):
    """Base exception for all HAVN SDK errors"""

    pass


class HAVNAPIError(HAVNError):
    """Exception raised for API errors"""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

    def __str__(self):
        if self.status_code:
            return f"HAVNAPIError (status {self.status_code}): {self.message}"
        return f"HAVNAPIError: {self.message}"


class HAVNAuthError(HAVNError):
    """Exception raised for authentication errors"""

    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)


class HAVNValidationError(HAVNError):
    """Exception raised for validation errors"""

    def __init__(self, message: str, errors: dict = None):
        self.message = message
        self.errors = errors or {}
        super().__init__(self.message)

    def __str__(self):
        if self.errors:
            return f"HAVNValidationError: {self.message}. Errors: {self.errors}"
        return f"HAVNValidationError: {self.message}"


class HAVNNetworkError(HAVNError):
    """Exception raised for network-related errors"""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self):
        if self.original_error:
            return f"HAVNNetworkError: {self.message}. Original: {str(self.original_error)}"
        return f"HAVNNetworkError: {self.message}"
