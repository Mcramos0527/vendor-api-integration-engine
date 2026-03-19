"""
Audit logging service.

Provides structured audit logging for all processing events,
ensuring full traceability of every transaction through the pipeline.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from collections import defaultdict


class AuditLogger:
    """
    Structured audit logger for transaction traceability.

    Logs processing events with timestamps, severity levels,
    and request correlation IDs. In production, this would
    write to a centralized logging system (e.g., ELK, Datadog).
    """

    def __init__(self, name: str = "vendor-api-engine"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)

        # Console handler with structured format
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

        # In-memory audit trail (production: database/external service)
        self._audit_trails: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def info(self, message: str, request_id: Optional[str] = None):
        """Log an informational event."""
        self._logger.info(message)
        if request_id:
            self._record(request_id, "INFO", message)

    def warning(self, message: str, request_id: Optional[str] = None):
        """Log a warning event."""
        self._logger.warning(message)
        if request_id:
            self._record(request_id, "WARNING", message)

    def error(self, message: str, request_id: Optional[str] = None):
        """Log an error event."""
        self._logger.error(message)
        if request_id:
            self._record(request_id, "ERROR", message)

    def debug(self, message: str, request_id: Optional[str] = None):
        """Log a debug event."""
        self._logger.debug(message)

    def _record(self, request_id: str, level: str, message: str):
        """Record an audit entry for a specific request."""
        self._audit_trails[request_id].append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": level,
                "message": message,
            }
        )

    def get_trail(self, request_id: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve the audit trail for a request ID."""
        trail = self._audit_trails.get(request_id)
        return trail if trail else None


# Singleton instance
audit_logger = AuditLogger()
