"""Text processing utilities for Uranus."""
import re
from typing import List, Dict, Any, Optional


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from markdown text.
    
    Args:
        text: The markdown text containing code blocks
        
    Returns:
        List of dictionaries with 'language' and 'code' keys
    """
    pattern = r"```(\w*)\n([\s\S]*?)```"
    matches = re.finditer(pattern, text)
    
    code_blocks = []
    for match in matches:
        language = match.group(1) or "text"
        code = match.group(2)
        code_blocks.append({
            "language": language,
            "code": code
        })
    
    return code_blocks


def extract_json_block(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract and parse a JSON block from text.
    
    Args:
        text: Text that may contain a JSON block
        
    Returns:
        Parsed JSON as a dictionary, or None if no valid JSON found
    """
    import json
    
    # Try to find JSON between triple backticks
    code_blocks = extract_code_blocks(text)
    for block in code_blocks:
        if block["language"].lower() in ["json", ""]:
            try:
                return json.loads(block["code"])
            except json.JSONDecodeError:
                continue
    
    # Try to find JSON between curly braces
    try:
        pattern = r"\{[\s\S]*\}"
        match = re.search(pattern, text)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        pass
    
    return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: The text to truncate
        max_length: Maximum length of the truncated text
        suffix: Suffix to add to truncated text
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_list(items: List[str], bullet: str = "•") -> str:
    """
    Format a list of items as a bulleted list.
    
    Args:
        items: List of items to format
        bullet: Bullet character to use
        
    Returns:
        Formatted bulleted list as a string
    """
    return "\n".join(f"{bullet} {item}" for item in items)