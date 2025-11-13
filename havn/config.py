"""
Configuration for HAVN SDK
"""

import os
from typing import Optional


class Config:
    """SDK Configuration with environment variable support"""

    # Default values
    DEFAULT_BASE_URL = "https://api.havn.com"
    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BACKOFF_FACTOR = 0.5  # seconds

    @staticmethod
    def get_api_key() -> Optional[str]:
        """Get API key from environment"""
        return os.getenv("HAVN_API_KEY")

    @staticmethod
    def get_webhook_secret() -> Optional[str]:
        """Get webhook secret from environment"""
        return os.getenv("HAVN_WEBHOOK_SECRET")

    @staticmethod
    def get_base_url() -> str:
        """Get base URL from environment with default"""
        return os.getenv("HAVN_BASE_URL", Config.DEFAULT_BASE_URL)

    @staticmethod
    def get_timeout() -> int:
        """Get timeout from environment with default"""
        try:
            return int(os.getenv("HAVN_TIMEOUT", Config.DEFAULT_TIMEOUT))
        except (ValueError, TypeError):
            return Config.DEFAULT_TIMEOUT

    @staticmethod
    def get_max_retries() -> int:
        """Get max retries from environment with default"""
        try:
            return int(os.getenv("HAVN_MAX_RETRIES", Config.DEFAULT_MAX_RETRIES))
        except (ValueError, TypeError):
            return Config.DEFAULT_MAX_RETRIES

    @staticmethod
    def get_backoff_factor() -> float:
        """Get backoff factor from environment with default"""
        try:
            return float(
                os.getenv("HAVN_BACKOFF_FACTOR", Config.DEFAULT_BACKOFF_FACTOR)
            )
        except (ValueError, TypeError):
            return Config.DEFAULT_BACKOFF_FACTOR
