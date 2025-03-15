"""Validation utilities for Uranus."""
import re
from typing import Any, Dict, List, Optional, Union, Callable


def is_valid_email(email: str) -> bool:
    """
    Check if a string is a valid email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if the email is valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if the URL is valid, False otherwise
    """
    pattern = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, url))


def validate_dict(
    data: Dict[str, Any],
    schema: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Validate a dictionary against a schema.
    
    Args:
        data: Dictionary to validate
        schema: Schema to validate against
            {
                "field_name": {
                    "type": type or tuple of types,
                    "required": bool,
                    "validator": callable (optional)
                }
            }
            
    Returns:
        List of validation errors, empty if valid
    """
    errors = []
    
    # Check required fields
    for field_name, field_schema in schema.items():
        if field_schema.get("required", False) and field_name not in data:
            errors.append(f"Missing required field: {field_name}")
    
    # Validate fields
    for field_name, value in data.items():
        if field_name not in schema:
            continue
            
        field_schema = schema[field_name]
        
        # Validate type
        expected_type = field_schema.get("type")
        if expected_type and not isinstance(value, expected_type):
            errors.append(f"Field {field_name} has invalid type: expected {expected_type}, got {type(value)}")
        
        # Run custom validator
        validator = field_schema.get("validator")
        if validator and callable(validator):
            try:
                result = validator(value)
                if result is not True and result is not None:
                    errors.append(f"Field {field_name} failed validation: {result}")
            except Exception as e:
                errors.append(f"Field {field_name} validation error: {str(e)}")
    
    return errors


def is_valid_json_string(json_str: str) -> bool:
    """
    Check if a string is valid JSON.
    
    Args:
        json_str: JSON string to validate
        
    Returns:
        True if the string is valid JSON, False otherwise
    """
    import json
    
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False