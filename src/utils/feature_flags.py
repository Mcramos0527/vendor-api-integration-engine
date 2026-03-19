"""
Feature flag management.

Provides a simple feature flag system for enabling/disabling
functionality without code deployments.

The CTO (Configure-to-Order) flag is the primary use case:
it was designed to allow future activation when the procurement
team completes their process changes.
"""

from typing import Dict, Any, Optional
from src.config.settings import settings
from src.services.audit_logger import audit_logger


class FeatureFlags:
    """
    Feature flag manager.

    Reads flags from application settings (environment variables)
    and provides a clean interface for checking flag status.

    In production, this could be backed by a feature flag service
    (e.g., LaunchDarkly, Unleash, or a database table).
    """

    _flags: Dict[str, bool] = {
        "cto_flag": settings.CTO_FLAG_ENABLED,
        "batch_processing": settings.BATCH_PROCESSING_ENABLED,
        "webhook_notifications": settings.WEBHOOK_NOTIFICATIONS_ENABLED,
    }

    @classmethod
    def is_enabled(cls, flag_name: str) -> bool:
        """
        Check if a feature flag is enabled.

        Args:
            flag_name: The name of the feature flag.

        Returns:
            True if enabled, False otherwise (defaults to False for unknown flags).
        """
        enabled = cls._flags.get(flag_name, False)
        audit_logger.debug(f"Feature flag '{flag_name}': {'enabled' if enabled else 'disabled'}")
        return enabled

    @classmethod
    def get_all(cls) -> Dict[str, bool]:
        """Return all feature flags and their current status."""
        return dict(cls._flags)

    @classmethod
    def override(cls, flag_name: str, enabled: bool) -> None:
        """
        Override a feature flag at runtime.

        WARNING: This is for testing/debugging only.
        Production flag changes should go through environment variables.
        """
        previous = cls._flags.get(flag_name)
        cls._flags[flag_name] = enabled
        audit_logger.warning(
            f"Feature flag override: '{flag_name}' changed from {previous} to {enabled}"
        )


# Convenience functions
def is_cto_enabled() -> bool:
    """Check if Configure-to-Order processing is enabled."""
    return FeatureFlags.is_enabled("cto_flag")


def is_batch_enabled() -> bool:
    """Check if batch processing endpoint is enabled."""
    return FeatureFlags.is_enabled("batch_processing")
