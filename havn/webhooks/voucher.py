"""Voucher webhook handler"""

import warnings
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime, date
from ..models.voucher import VoucherValidationPayload, VoucherListFilters
from ..models.voucher_list import (
    VoucherListResponse,
    VoucherData,
    VoucherListPagination,
)
from ..exceptions import HAVNValidationError, HAVNAPIError
from ..constants import (
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_UNPROCESSABLE_ENTITY,
)


def _build_voucher_error_message(status_code: int) -> str:
    """Build error message for voucher validation (DRY helper)"""
    if status_code == HTTP_STATUS_NOT_FOUND:
        return "Voucher not found"
    elif status_code == HTTP_STATUS_BAD_REQUEST:
        return "Voucher invalid (expired, used up, or inactive)"
    elif status_code == HTTP_STATUS_UNPROCESSABLE_ENTITY:
        return "Amount does not meet voucher requirements"
    return "Voucher validation failed"


class VoucherWebhook:
    """
    Voucher webhook handler

    Handles voucher validation via HAVN API.

    Example:
        >>> client = HAVNClient(api_key="...", webhook_secret="...")
        >>> try:
        ...     is_valid = client.vouchers.validate(
        ...         voucher_code="VOUCHER123",
        ...         amount=10000
        ...     )
        ...     print("✅ Voucher is valid")
        ... except Exception as e:
        ...     print(f"❌ Voucher invalid: {e}")
    """

    def __init__(self, client):
        """
        Initialize voucher webhook handler

        Args:
            client: HAVNClient instance
        """
        self.client = client

    def validate(
        self,
        voucher_code: str,
        amount: Optional[int] = None,
        currency: Optional[str] = None,
        auto_convert: Optional[bool] = None,
    ) -> bool:
        """
        Validate voucher code

        This endpoint returns only HTTP status code (no response body).
        - 200 OK: Voucher is valid
        - 400/404/422: Voucher is invalid

        **Currency Conversion:**
        - HAVN backend sekarang menangani seluruh konversi berdasarkan currency
          yang dikirimkan. SDK cukup meneruskan nilai asli.

        Args:
            voucher_code: Voucher code to validate (required)
            amount: Transaction amount (optional)
                - If `auto_convert=True`: amount in source currency (will be converted to voucher currency)
                - If `auto_convert=False`: amount in voucher currency (must match)
            currency: Source currency code (optional)
                - Used only if `auto_convert=True` to convert amount to voucher currency
            auto_convert: (Deprecated) Sudah tidak digunakan; backend melakukan
                konversi otomatis. Parameter ini hanya dipertahankan demi kompatibilitas.

        Returns:
            True if voucher is valid

        Raises:
            HAVNValidationError: If payload validation fails
            HAVNAPIError: If voucher is invalid or API request fails

        Example:
            >>> # Valid voucher (backend handles conversion)
            >>> is_valid = client.vouchers.validate(
            ...     "HAVN-123",
            ...     amount=150000,
            ...     currency="IDR",
            ... )
        """
        if auto_convert is not None:
            warnings.warn(
                "Parameter auto_convert sudah tidak digunakan. HAVN backend kini"
                " melakukan konversi otomatis berdasarkan currency yang dikirimkan.",
                DeprecationWarning,
                stacklevel=2,
            )

        # Build payload
        payload = VoucherValidationPayload(
            voucher_code=voucher_code,
            amount=amount,
            currency=currency,
        )

        # Validate payload
        try:
            payload.validate()
        except ValueError as e:
            raise HAVNValidationError(str(e))

        # Make API request (this endpoint returns status code only, no body)
        try:
            self.client._make_request(
                method="POST",
                endpoint="/api/v1/webhook/voucher/validate",
                payload=payload.to_dict(),
            )
            return True
        except HAVNAPIError as e:
            # Re-raise with clearer message for voucher validation
            error_message = _build_voucher_error_message(e.status_code)
            raise HAVNAPIError(error_message, status_code=e.status_code)

    def get_all(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        active: Optional[bool] = None,
        type: Optional[str] = None,
        client_type: Optional[str] = None,
        currency: Optional[str] = None,
        search: Optional[str] = None,
        start_date_from: Optional[str] = None,
        start_date_to: Optional[str] = None,
        end_date_from: Optional[str] = None,
        end_date_to: Optional[str] = None,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        min_purchase_from: Optional[int] = None,
        min_purchase_to: Optional[int] = None,
        usage_limit_from: Optional[int] = None,
        usage_limit_to: Optional[int] = None,
        is_valid: Optional[bool] = None,
        is_expired: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        display_currency: Optional[str] = None,
    ) -> VoucherListResponse:
        """
        Get all vouchers for SaaS company with pagination, filtering, and search

        **Important**: This method always fetches fresh data from HAVN backend.
        No client-side caching is used. Single source of truth is the backend.
        Each call makes a new HTTP request to ensure data consistency.

        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 10, max: 100)
            active: Filter by active status (true/false)
            type: Filter by voucher type (DISCOUNT_PERCENTAGE, DISCOUNT_FIXED)
            client_type: Filter by client type (NEW_CUSTOMER, RECURRING)
            currency: Filter by currency code (USD, IDR, etc.)
            search: Search in voucher code, description
            start_date_from: Filter by start_date >= (YYYY-MM-DD)
            start_date_to: Filter by start_date <= (YYYY-MM-DD)
            end_date_from: Filter by end_date >= (YYYY-MM-DD)
            end_date_to: Filter by end_date <= (YYYY-MM-DD)
            created_from: Filter by created_date >= (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
            created_to: Filter by created_date <= (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
            min_value: Filter by value >= (integer, in cents/basis points)
            max_value: Filter by value <= (integer, in cents/basis points)
            min_purchase_from: Filter by min_purchase >= (integer, in cents)
            min_purchase_to: Filter by min_purchase <= (integer, in cents)
            usage_limit_from: Filter by usage_limit >= (integer)
            usage_limit_to: Filter by usage_limit <= (integer)
            is_valid: Filter by validity (true/false) - checks active, dates, usage
            is_expired: Filter by expired status (true/false)
            sort_by: Sort field (code, type, value, start_date, end_date, created_date, current_usage)
            sort_order: Sort direction (asc, desc) - default: desc
            display_currency: Target currency untuk ditampilkan (opsional)
                - HAVN backend otomatis mengkonversi semua nilai voucher ke currency ini
                - Jika None: backend mengembalikan currency asli (USD untuk HAVN vouchers)
                - Local vouchers yang digabungkan via callback tetap memakai currency yang diberikan callback

        Returns:
            VoucherListResponse with paginated voucher data

        Raises:
            HAVNValidationError: If filters validation fails
            HAVNAPIError: If API request fails

        Example:
            >>> # Get all active vouchers
            >>> result = client.vouchers.get_all(active=True, page=1, per_page=20)
            >>> print(f"Total: {result.pagination.total}")
            >>> for voucher in result.data:
            ...     print(f"{voucher.code}: {voucher.is_valid}")

            >>> # Search and filter
            >>> result = client.vouchers.get_all(
            ...     search="DISCOUNT",
            ...     type="DISCOUNT_PERCENTAGE",
            ...     is_valid=True,
            ...     sort_by="created_date",
            ...     sort_order="desc"
            ... )

            >>> # Filter by date range
            >>> result = client.vouchers.get_all(
            ...     start_date_from="2024-01-01",
            ...     end_date_to="2024-12-31",
            ...     active=True
            ... )
        """
        # Build filters
        filters = VoucherListFilters(
            page=page,
            per_page=per_page,
            active=active,
            type=type,
            client_type=client_type,
            currency=currency,
            search=search,
            start_date_from=start_date_from,
            start_date_to=start_date_to,
            end_date_from=end_date_from,
            end_date_to=end_date_to,
            created_from=created_from,
            created_to=created_to,
            min_value=min_value,
            max_value=max_value,
            min_purchase_from=min_purchase_from,
            min_purchase_to=min_purchase_to,
            usage_limit_from=usage_limit_from,
            usage_limit_to=usage_limit_to,
            is_valid=is_valid,
            is_expired=is_expired,
            sort_by=sort_by,
            sort_order=sort_order,
            display_currency=display_currency,
        )

        # Validate filters
        try:
            filters.validate()
        except ValueError as e:
            raise HAVNValidationError(str(e))

        # Make GET request with query params
        # For GET requests, signature is calculated from empty dict (handled by client)
        try:
            response_data = self.client._make_request(
                method="GET",
                endpoint="/api/v1/webhook/vouchers",
                payload=filters.to_dict(),  # Pass as query params
            )
            return VoucherListResponse.from_dict(response_data)
        except HAVNAPIError:
            raise

    def get_combined(
        self,
        local_vouchers_callback: Optional[Callable[[], List[Dict[str, Any]]]] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        active: Optional[bool] = None,
        type: Optional[str] = None,
        client_type: Optional[str] = None,
        currency: Optional[str] = None,
        search: Optional[str] = None,
        start_date_from: Optional[str] = None,
        start_date_to: Optional[str] = None,
        end_date_from: Optional[str] = None,
        end_date_to: Optional[str] = None,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        min_purchase_from: Optional[int] = None,
        min_purchase_to: Optional[int] = None,
        usage_limit_from: Optional[int] = None,
        usage_limit_to: Optional[int] = None,
        is_valid: Optional[bool] = None,
        is_expired: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        display_currency: Optional[str] = None,
    ) -> VoucherListResponse:
        """
        Get combined vouchers (HAVN + local SaaS company vouchers)

        **Important**: This method always fetches fresh HAVN voucher data from backend.
        No client-side caching is used. Single source of truth for HAVN vouchers is the backend.
        Each call makes a new HTTP request to ensure data consistency with backend.

        This method combines vouchers from HAVN with local vouchers from
        SaaS company. Only HAVN vouchers are returned from API, local vouchers
        are provided via callback.

        Args:
            local_vouchers_callback: Callback function that returns list of local vouchers.
                Each voucher dict should have: code, type, value, min_purchase, max_purchase,
                start_date, end_date, active, currency, description, etc.
                If None, only HAVN vouchers will be returned (same as get_all()).
            **filters: Same filters as get_all() method (page, per_page, active, type, etc.)

        Returns:
            VoucherListResponse with combined vouchers (HAVN + local).
            Each voucher has is_havn_voucher flag to identify source.

        Raises:
            HAVNValidationError: If filters validation fails
            HAVNAPIError: If API request fails

        Example:
            >>> def get_local_vouchers():
            ...     # Your logic to get local vouchers from SaaS company
            ...     return [
            ...         {
            ...             "code": "LOCAL123",
            ...             "type": "DISCOUNT_PERCENTAGE",
            ...             "value": 2000,  # 20%
            ...             "min_purchase": 5000,
            ...             "max_purchase": None,
            ...             "start_date": "2024-01-01",
            ...             "end_date": "2024-12-31",
            ...             "active": True,
            ...             "currency": "USD",
            ...             "usage_limit": 1,
            ...             "current_usage": 0,
            ...         }
            ...     ]
            >>>
            >>> result = client.vouchers.get_combined(
            ...     local_vouchers_callback=get_local_vouchers,
            ...     active=True,
            ...     page=1,
            ...     per_page=20
            ... )
            >>>
            >>> for voucher in result.data:
            ...     if voucher.is_havn_voucher:
            ...         print(f"HAVN: {voucher.code}")
            ...     else:
            ...         print(f"Local: {voucher.code}")
        """
        # Get HAVN vouchers using existing method
        # Performance: Always fetch fresh data from backend (no caching)
        # Single source of truth is the backend - each call makes new HTTP request
        filters_dict = {
            "page": page,
            "per_page": per_page,
            "active": active,
            "type": type,
            "client_type": client_type,
            "currency": currency,
            "search": search,
            "start_date_from": start_date_from,
            "start_date_to": start_date_to,
            "end_date_from": end_date_from,
            "end_date_to": end_date_to,
            "created_from": created_from,
            "created_to": created_to,
            "min_value": min_value,
            "max_value": max_value,
            "min_purchase_from": min_purchase_from,
            "min_purchase_to": min_purchase_to,
            "usage_limit_from": usage_limit_from,
            "usage_limit_to": usage_limit_to,
            "is_valid": is_valid,
            "is_expired": is_expired,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "display_currency": display_currency,
        }

        havn_result = self.get_all(
            **{k: v for k, v in filters_dict.items() if v is not None}
        )

        # Get local vouchers if callback provided
        local_vouchers = []
        if local_vouchers_callback:
            try:
                local_raw = local_vouchers_callback()
                # Performance: Filter local vouchers early before conversion
                # Only convert vouchers that pass basic filters
                if local_raw:
                    # Apply basic filters to raw data before conversion (performance)
                    filtered_raw = self._filter_local_vouchers_raw(
                        local_raw,
                        active=active,
                        search=search,
                    )
                    # Performance: Cache today() once for all conversions
                    # Note: This is local date caching only (not backend data caching)
                    # Backend data is always fresh from API request above
                    today_cached = date.today()
                    # Convert only filtered vouchers (reduces processing)
                    local_vouchers = [
                        self._convert_local_voucher_to_havn_format(
                            v, today=today_cached
                        )
                        for v in filtered_raw
                    ]
            except Exception as e:
                # Log error but continue with HAVN vouchers only
                import logging

                logging.warning(f"Error getting local vouchers: {e}")

        # Combine vouchers (HAVN + local)
        combined_vouchers = list(havn_result.data) + local_vouchers

        # Apply remaining filters to combined vouchers (is_valid, is_expired need computed fields)
        if is_valid is not None or is_expired is not None:
            combined_vouchers = self._filter_combined_vouchers(
                combined_vouchers,
                active=None,  # Already filtered
                search=None,  # Already filtered
                is_valid=is_valid,
                is_expired=is_expired,
            )

        # Sort combined list if sort_by specified
        if sort_by:
            combined_vouchers = self._sort_vouchers(
                combined_vouchers,
                sort_by=sort_by,
                sort_order=sort_order or "desc",
            )

        # Paginate combined list (performance: slice directly, no copy)
        page_num = page or 1
        per_page_num = per_page or 10
        total = len(combined_vouchers)
        start_idx = (page_num - 1) * per_page_num
        end_idx = start_idx + per_page_num
        # Performance: Direct slice, no list() conversion needed
        paginated_vouchers = combined_vouchers[start_idx:end_idx]

        # Create pagination object
        total_pages = (total + per_page_num - 1) // per_page_num if total > 0 else 0
        pagination = VoucherListPagination(
            page=page_num,
            limit=per_page_num,
            total=total,
            total_pages=total_pages,
            has_prev=page_num > 1,
            has_next=page_num < total_pages,
        )

        return VoucherListResponse(
            success=True,
            message="Combined vouchers retrieved successfully",
            data=paginated_vouchers,
            pagination=pagination,
            raw_response=havn_result.raw_response,
        )

    def _filter_local_vouchers_raw(
        self,
        local_vouchers: List[Dict[str, Any]],
        active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter local vouchers before conversion (performance optimization)

        Filters raw voucher data to reduce conversion overhead.

        Args:
            local_vouchers: List of raw local voucher dicts
            active: Filter by active status
            search: Search in code/description

        Returns:
            Filtered list of raw vouchers
        """
        filtered = local_vouchers

        # Active filter (fast - no conversion needed)
        if active is not None:
            filtered = [
                v
                for v in filtered
                if v.get("active") is not None
                and (v.get("active") == active)
                or (v.get("active") is None and active is True)
            ]

        # Search filter (fast - no conversion needed)
        if search:
            search_lower = search.lower()
            filtered = [
                v
                for v in filtered
                if search_lower
                in (v.get("code") or v.get("voucher_code") or "").lower()
                or search_lower in (v.get("description") or v.get("name") or "").lower()
            ]

        return filtered

    def _convert_local_voucher_to_havn_format(
        self, local_voucher: Dict[str, Any], today: Optional[date] = None
    ) -> VoucherData:
        """
        Convert local voucher to HAVN VoucherData format (DRY principle)

        Handles different field names/structures from local voucher systems.

        Args:
            local_voucher: Local voucher dictionary from SaaS company
            today: Optional today date (cached for performance)

        Returns:
            VoucherData instance with is_havn_voucher=False
        """
        # Performance: Cache today() to avoid repeated calls
        if today is None:
            today = date.today()

        # Extract dates (optimized - single get per field)
        end_date = (
            local_voucher.get("end_date") or local_voucher.get("expires_at") or ""
        )
        start_date = (
            local_voucher.get("start_date") or local_voucher.get("valid_from") or ""
        )
        created_date = (
            local_voucher.get("created_date") or local_voucher.get("created_at") or ""
        )
        updated_at_value = local_voucher.get("updated_at")
        if not updated_at_value:
            updated_at_value = created_date  # Fallback to created_date

        # Check if expired (use cached today)
        is_expired = self._check_expired(end_date, today=today)

        # Check if valid (use cached today)
        is_valid = self._check_local_valid(local_voucher, today=today)

        # Calculate usage stats (optimized - single calculation)
        usage_limit = (
            local_voucher.get("usage_limit") or local_voucher.get("max_uses") or 1
        )
        current_usage = (
            local_voucher.get("current_usage") or local_voucher.get("uses_count") or 0
        )
        remaining_usage = max(0, usage_limit - current_usage)
        usage_percentage = (
            (current_usage / usage_limit * 100) if usage_limit > 0 else 0.0
        )

        return VoucherData(
            serial="",  # Local vouchers don't have HAVN serial
            saas_company_id=0,  # Unknown for local
            associate_id="",  # Local vouchers don't have associate
            code=local_voucher.get("code") or local_voucher.get("voucher_code") or "",
            type=local_voucher.get("type") or "DISCOUNT_PERCENTAGE",
            value=local_voucher.get("value")
            or local_voucher.get("discount_value")
            or 0,
            usage_limit=usage_limit,
            current_usage=current_usage,
            min_purchase=local_voucher.get("min_purchase")
            or local_voucher.get("minimum_amount")
            or 0,
            max_purchase=local_voucher.get("max_purchase")
            or local_voucher.get("maximum_amount"),
            start_date=start_date,
            end_date=end_date,
            active=local_voucher.get("active", True)
            if local_voucher.get("active") is not None
            else True,
            client_type=local_voucher.get("client_type"),
            description=local_voucher.get("description") or local_voucher.get("name"),
            creation_cost=0,  # Local vouchers don't have creation cost
            created_by="",  # Unknown for local
            created_date=created_date,
            updated_at=updated_at_value,
            currency=local_voucher.get("currency") or "USD",
            affiliates_url=None,
            affiliates_qr_image=None,
            # Computed fields
            is_expired=is_expired,
            is_valid=is_valid,
            remaining_usage=remaining_usage,
            usage_percentage=usage_percentage,
            associate=None,
            is_havn_voucher=False,  # Mark as local voucher
        )

    def _check_expired(self, end_date: str, today: Optional[date] = None) -> bool:
        """
        Check if voucher is expired (DRY helper)

        Args:
            end_date: End date string (YYYY-MM-DD format)
            today: Optional today date (cached for performance)

        Returns:
            True if expired, False otherwise
        """
        if not end_date:
            return False
        try:
            end = datetime.strptime(end_date.split("T")[0], "%Y-%m-%d").date()
            # Performance: Use cached today if provided
            if today is None:
                today = date.today()
            return today > end
        except (ValueError, AttributeError):
            return False

    def _check_local_valid(
        self, local_voucher: Dict[str, Any], today: Optional[date] = None
    ) -> bool:
        """
        Check if local voucher is currently valid (DRY helper)

        Args:
            local_voucher: Local voucher dictionary
            today: Optional today date (cached for performance)

        Returns:
            True if valid, False otherwise
        """
        # Performance: Use cached today if provided
        if today is None:
            today = date.today()

        # Check active status (fast - early return)
        if local_voucher.get("active") is False:
            return False

        # Check date range
        start_date = local_voucher.get("start_date") or local_voucher.get("valid_from")
        end_date = local_voucher.get("end_date") or local_voucher.get("expires_at")

        if start_date and end_date:
            try:
                start = datetime.strptime(start_date.split("T")[0], "%Y-%m-%d").date()
                end = datetime.strptime(end_date.split("T")[0], "%Y-%m-%d").date()
                if today < start or today > end:
                    return False
            except (ValueError, AttributeError):
                pass

        # Check usage limit
        usage_limit = (
            local_voucher.get("usage_limit") or local_voucher.get("max_uses") or 1
        )
        current_usage = (
            local_voucher.get("current_usage") or local_voucher.get("uses_count") or 0
        )
        if current_usage >= usage_limit:
            return False

        return True

    def _filter_combined_vouchers(
        self,
        vouchers: List[VoucherData],
        active: Optional[bool] = None,
        search: Optional[str] = None,
        is_valid: Optional[bool] = None,
        is_expired: Optional[bool] = None,
    ) -> List[VoucherData]:
        """
        Apply filters to combined voucher list (DRY principle)

        Args:
            vouchers: List of vouchers to filter
            active: Filter by active status
            search: Search in code/description
            is_valid: Filter by validity
            is_expired: Filter by expired status

        Returns:
            Filtered list of vouchers
        """
        filtered = vouchers

        # Active filter
        if active is not None:
            filtered = [v for v in filtered if v.active == active]

        # Search filter
        if search:
            search_lower = search.lower()
            filtered = [
                v
                for v in filtered
                if search_lower in v.code.lower()
                or (v.description and search_lower in v.description.lower())
            ]

        # Valid filter
        if is_valid is not None:
            filtered = [v for v in filtered if v.is_valid == is_valid]

        # Expired filter
        if is_expired is not None:
            filtered = [v for v in filtered if v.is_expired == is_expired]

        return filtered

    def _sort_vouchers(
        self, vouchers: List[VoucherData], sort_by: str, sort_order: str
    ) -> List[VoucherData]:
        """
        Sort vouchers by specified field (DRY helper)

        Performance: Uses optimized sorting with cached key function.

        Args:
            vouchers: List of vouchers to sort
            sort_by: Field to sort by
            sort_order: "asc" or "desc"

        Returns:
            Sorted list of vouchers
        """
        if not vouchers:
            return vouchers

        reverse = sort_order.lower() == "desc"

        # Map sort_by to attribute name (cached for performance)
        sort_map = {
            "code": "code",
            "type": "type",
            "value": "value",
            "start_date": "start_date",
            "end_date": "end_date",
            "created_date": "created_date",
            "current_usage": "current_usage",
            "usage_limit": "usage_limit",
            "min_purchase": "min_purchase",
        }

        sort_key = sort_map.get(sort_by.lower(), "created_date")

        # Performance: Pre-compile key function for faster sorting
        try:
            # For numeric fields, convert to int for proper sorting
            if sort_key in ("value", "current_usage", "usage_limit", "min_purchase"):

                def key_func(v):
                    return getattr(v, sort_key, 0) or 0
            else:
                # For string/date fields, use default comparison
                def key_func(v):
                    return getattr(v, sort_key, "") or ""

            return sorted(vouchers, key=key_func, reverse=reverse)
        except (AttributeError, TypeError):
            # Fallback to original order if sorting fails
            return vouchers

