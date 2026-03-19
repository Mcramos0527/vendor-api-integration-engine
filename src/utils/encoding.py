"""
Character encoding utilities.

Handles Latin-1 encoding for customer names that may contain
special characters or symbols from European languages.
"""

import unicodedata
from typing import Optional


def encode_customer_name(name: str) -> str:
    """
    Encode a customer name for safe ERP transmission.

    The ERP system expects Latin-1 (ISO 8859-1) encoded strings.
    Characters outside the Latin-1 range are transliterated or
    replaced with safe equivalents.

    Args:
        name: Raw customer name that may contain special characters.

    Returns:
        Latin-1 safe customer name string.

    Examples:
        >>> encode_customer_name("Müller GmbH")
        'Müller GmbH'
        >>> encode_customer_name("Société Générale")
        'Société Générale'
        >>> encode_customer_name("日本語テスト")  # Japanese chars
        '????'  # Replaced with safe characters
    """
    if not name:
        return ""

    try:
        # Attempt Latin-1 encoding — if it works, the name is safe
        name.encode("latin-1")
        return name.strip()
    except UnicodeEncodeError:
        # Normalize unicode and attempt transliteration
        normalized = unicodedata.normalize("NFKD", name)

        # Build Latin-1 safe string
        safe_chars = []
        for char in normalized:
            try:
                char.encode("latin-1")
                safe_chars.append(char)
            except UnicodeEncodeError:
                # Replace non-Latin-1 characters with '?'
                if not unicodedata.combining(char):
                    safe_chars.append("?")

        return "".join(safe_chars).strip()


def sanitize_field(value: Optional[str], max_length: int = 255) -> str:
    """
    Sanitize a string field for safe storage and transmission.

    Strips whitespace, enforces max length, and removes control characters.
    """
    if not value:
        return ""

    # Remove control characters
    cleaned = "".join(
        char for char in value if not unicodedata.category(char).startswith("C")
    )

    return cleaned.strip()[:max_length]
