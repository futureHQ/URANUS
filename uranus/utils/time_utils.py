"""Date and time utilities for Uranus."""
import datetime
from typing import Optional, Union


def get_current_timestamp() -> float:
    """
    Get the current timestamp in seconds since the epoch.
    
    Returns:
        Current timestamp
    """
    return datetime.datetime.now().timestamp()


def format_timestamp(
    timestamp: Optional[float] = None,
    format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Format a timestamp as a string.
    
    Args:
        timestamp: Timestamp to format (default: current time)
        format_str: Format string for strftime
        
    Returns:
        Formatted timestamp
    """
    if timestamp is None:
        dt = datetime.datetime.now()
    else:
        dt = datetime.datetime.fromtimestamp(timestamp)
    
    return dt.strftime(format_str)


def parse_datetime(
    date_str: str,
    formats: Optional[list] = None
) -> Optional[datetime.datetime]:
    """
    Parse a date string into a datetime object.
    
    Args:
        date_str: Date string to parse
        formats: List of format strings to try (default: common formats)
        
    Returns:
        Parsed datetime object, or None if parsing failed
    """
    if formats is None:
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y",
            "%b %d, %Y",
            "%B %d, %Y",
            "%d %b %Y",
            "%d %B %Y"
        ]
    
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def time_ago(timestamp: float) -> str:
    """
    Convert a timestamp to a human-readable "time ago" string.
    
    Args:
        timestamp: Timestamp to convert
        
    Returns:
        Human-readable time difference
    """
    now = datetime.datetime.now()
    dt = datetime.datetime.fromtimestamp(timestamp)
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours ago"
    elif seconds < 604800:
        return f"{int(seconds / 86400)} days ago"
    elif seconds < 2592000:
        return f"{int(seconds / 604800)} weeks ago"
    elif seconds < 31536000:
        return f"{int(seconds / 2592000)} months ago"
    else:
        return f"{int(seconds / 31536000)} years ago"