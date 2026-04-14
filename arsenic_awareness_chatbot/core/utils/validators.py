"""Input validation utilities."""
import re
from typing import Optional


def sanitize_input(text: str, max_length: int = 2000) -> Optional[str]:
    """Sanitize user input."""
    if not text or not isinstance(text, str):
        return None
    cleaned = text.strip()[:max_length]
    return cleaned if cleaned else None
