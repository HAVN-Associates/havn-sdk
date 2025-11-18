"""
HAVN Python SDK

Official Python SDK for integrating with HAVN API.
"""

from .client import HAVNClient
from .exceptions import (
    HAVNError,
    HAVNAPIError,
    HAVNAuthError,
    HAVNValidationError,
    HAVNNetworkError,
    HAVNRateLimitError,
)
from .models import (
    TransactionPayload,
    TransactionResponse,
    UserSyncPayload,
    UserSyncResponse,
    BulkUserSyncPayload,
    BulkUserSyncResponse,
    BulkSyncSummary,
    VoucherValidationPayload,
    VoucherListFilters,
    VoucherData,
    VoucherListPagination,
    VoucherListResponse,
    is_havn_voucher_code,
)
from .utils.currency import (
    CurrencyConverter,
    convert_to_usd_cents,
    convert_from_usd_cents,
    get_exchange_rate,
)

__version__ = "1.1.5"
__author__ = "Bagus"
__email__ = "bagus@intelove.com"

__all__ = [
    "HAVNClient",
    "HAVNError",
    "HAVNAPIError",
    "HAVNAuthError",
    "HAVNValidationError",
    "HAVNNetworkError",
    "HAVNRateLimitError",
    "TransactionPayload",
    "TransactionResponse",
    "UserSyncPayload",
    "UserSyncResponse",
    "BulkUserSyncPayload",
    "BulkUserSyncResponse",
    "BulkSyncSummary",
    "VoucherValidationPayload",
    "VoucherListFilters",
    "VoucherData",
    "VoucherListPagination",
    "VoucherListResponse",
    "is_havn_voucher_code",
    "CurrencyConverter",
    "convert_to_usd_cents",
    "convert_from_usd_cents",
    "get_exchange_rate",
]
