"""
Constants for HAVN SDK
Centralized constants to avoid magic strings and improve maintainability
"""

# Currency constants
USD_CURRENCY = "USD"
HAVN_VOUCHER_PREFIX = "HAVN-"

# HTTP methods
HTTP_METHOD_GET = "GET"
HTTP_METHOD_POST = "POST"
HTTP_METHOD_PUT = "PUT"
HTTP_METHOD_PATCH = "PATCH"

# HTTP status codes
HTTP_STATUS_OK = 200
HTTP_STATUS_CREATED = 201
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_UNPROCESSABLE_ENTITY = 422
HTTP_STATUS_TOO_MANY_REQUESTS = 429

# Rate limit headers
HEADER_RATE_LIMIT_RESET = "X-RateLimit-Reset"
HEADER_RATE_LIMIT_LIMIT = "X-RateLimit-Limit"
HEADER_RATE_LIMIT_REMAINING = "X-RateLimit-Remaining"

# Test mode
HEADER_TEST_MODE = "X-Test-Mode"
TEST_MODE_VALUE = "true"

# Default values
DEFAULT_SUCCESS_RESPONSE = {"success": True}
DEFAULT_ERROR_TYPE = "APIError"
DEFAULT_RATE_LIMIT_MESSAGE = "Rate limit exceeded. Please try again later."
DEFAULT_AUTH_FAILED_MESSAGE = "Authentication failed"

# Date format
DATE_FORMAT = "%Y-%m-%d"
