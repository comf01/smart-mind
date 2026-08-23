"""
Helper utilities for the mind core.

Common utility functions used throughout the system.
"""

import hashlib
import uuid
from datetime import datetime
from typing import Any


def generate_id() -> str:
    """
    Generate a unique identifier.
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def format_timestamp(dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a timestamp.
    
    Args:
        dt: Datetime object (defaults to now)
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def calculate_hash(data: Any) -> str:
    """
    Calculate SHA-256 hash of data.
    
    Args:
        data: Data to hash
        
    Returns:
        Hex digest string
    """
    data_str = str(data).encode('utf-8')
    return hashlib.sha256(data_str).hexdigest()


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary.
    
    Args:
        dictionary: Dictionary to access
        key: Key to retrieve
        default: Default value if not found
        
    Returns:
        Value or default
    """
    try:
        return dictionary.get(key, default)
    except (AttributeError, TypeError):
        return default


def merge_dicts(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        override: Override dictionary
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max.
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))
