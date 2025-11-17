"""
Working tests for exception handling
"""

import pytest
from havn.exceptions import (
    HAVNError,
    HAVNAPIError,
    HAVNAuthError,
    HAVNValidationError,
    HAVNNetworkError,
    HAVNRateLimitError
)


class TestExceptionsWorking:
    """Test exception classes - working tests only"""

    def test_havn_error_base_class(self):
        """Test base HAVNError exception"""
        error = HAVNError("Base error")
        assert str(error) == "Base error"
        assert isinstance(error, Exception)

    def test_havn_api_error(self):
        """Test HAVNAPIError exception"""
        error = HAVNAPIError("API failed", status_code=400, response={"error": "Bad request"})
        assert str(error) == "HAVNAPIError (status 400): API failed"
        assert error.status_code == 400
        assert error.response == {"error": "Bad request"}
        assert isinstance(error, HAVNError)
        assert error.message == "API failed"

    def test_havn_api_error_no_status(self):
        """Test HAVNAPIError without status code"""
        error = HAVNAPIError("API failed")
        assert str(error) == "HAVNAPIError: API failed"
        assert error.status_code is None

    def test_havn_auth_error(self):
        """Test HAVNAuthError exception"""
        error = HAVNAuthError("Authentication failed")
        assert str(error) == "Authentication failed"
        assert isinstance(error, HAVNError)
        assert error.message == "Authentication failed"

    def test_havn_auth_error_default(self):
        """Test HAVNAuthError with default message"""
        error = HAVNAuthError()
        assert str(error) == "Authentication failed"
        assert error.message == "Authentication failed"

    def test_havn_validation_error(self):
        """Test HAVNValidationError exception"""
        error = HAVNValidationError("Invalid input")
        assert str(error) == "HAVNValidationError: Invalid input"
        assert isinstance(error, HAVNError)
        assert error.message == "Invalid input"
        assert error.errors == {}

    def test_havn_validation_error_with_errors(self):
        """Test HAVNValidationError with error details"""
        errors = {"field1": "cannot be blank", "field2": "must be positive"}
        error = HAVNValidationError("Validation failed", errors=errors)
        assert str(error) == f"HAVNValidationError: Validation failed. Errors: {errors}"
        assert error.errors == errors
        assert isinstance(error, HAVNError)

    def test_havn_network_error(self):
        """Test HAVNNetworkError exception"""
        error = HAVNNetworkError("Network timeout")
        assert str(error) == "HAVNNetworkError: Network timeout"
        assert isinstance(error, HAVNError)
        assert error.message == "Network timeout"
        assert error.original_error is None

    def test_havn_network_error_with_original(self):
        """Test HAVNNetworkError with original error"""
        original = ConnectionError("Connection refused")
        error = HAVNNetworkError("Network timeout", original_error=original)
        assert str(error) == f"HAVNNetworkError: Network timeout. Original: {str(original)}"
        assert error.original_error == original
        assert isinstance(error, HAVNError)

    def test_havn_rate_limit_error(self):
        """Test HAVNRateLimitError exception"""
        error = HAVNRateLimitError("Rate limit exceeded", retry_after=60, limit=1000, remaining=0)
        assert str(error) == "HAVNRateLimitError: Rate limit exceeded. Retry after 60 seconds"
        assert error.retry_after == 60
        assert error.limit == 1000
        assert error.remaining == 0
        assert error.message == "Rate limit exceeded"
        assert isinstance(error, HAVNError)

    def test_havn_rate_limit_error_no_retry(self):
        """Test HAVNRateLimitError without retry_after"""
        error = HAVNRateLimitError("Rate limit exceeded")
        assert str(error) == "HAVNRateLimitError: Rate limit exceeded"
        assert error.retry_after is None

    def test_custom_exception_inheritance(self):
        """Test that custom exceptions can be caught by parent classes"""
        
        # Should be caught by HAVNError
        try:
            raise HAVNAPIError("API error")
        except HAVNError:
            caught = True
        else:
            caught = False
        assert caught

        # Should be caught by HAVNError (HAVNAuthError doesn't inherit HAVNAPIError)
        try:
            raise HAVNAuthError("Auth error")
        except HAVNError:
            caught = True
        else:
            caught = False
        assert caught

        # Should not be caught by HAVNAuthError when it's HAVNValidationError
        try:
            raise HAVNValidationError("Validation error")
        except HAVNAuthError:
            caught = True
        except HAVNError:
            caught = False
        else:
            caught = False
        assert caught == False  # Should not be caught by HAVNAuthError
