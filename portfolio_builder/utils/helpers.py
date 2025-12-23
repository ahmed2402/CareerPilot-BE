"""
General Helper Utilities for Portfolio Builder.
"""

import re
import json
import uuid
from typing import Any, Optional


def generate_project_id() -> str:
    """Generate a unique project ID."""
    return str(uuid.uuid4())[:8]


def safe_json_parse(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON from LLM responses.
    
    Handles common issues like markdown code blocks and control characters.
    
    Args:
        json_string: String that should contain JSON
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    if not json_string:
        return default
    
    # Try to extract JSON from markdown code blocks
    json_string = json_string.strip()
    
    # Check for ```json ... ``` blocks
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', json_string, re.DOTALL)
    if json_match:
        json_string = json_match.group(1).strip()
    
    # Remove control characters that can cause parsing issues
    json_string = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', json_string)
    
    # Try to find JSON object or array
    if not json_string.startswith(('{', '[')):
        # Try to find start of JSON
        start_obj = json_string.find('{')
        start_arr = json_string.find('[')
        
        if start_obj != -1 and (start_arr == -1 or start_obj < start_arr):
            json_string = json_string[start_obj:]
        elif start_arr != -1:
            json_string = json_string[start_arr:]
    
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Problematic string (first 200 chars): {json_string[:200]}")
        return default


def format_component_name(name: str) -> str:
    """
    Convert a string to PascalCase component name.
    
    Args:
        name: Input string (e.g., "hero_section", "about-me")
        
    Returns:
        PascalCase string (e.g., "HeroSection", "AboutMe")
    """
    # Replace separators with spaces
    name = re.sub(r'[-_\s]+', ' ', name)
    
    # Title case and remove spaces
    return ''.join(word.capitalize() for word in name.split())


def format_filename(component_name: str) -> str:
    """
    Format a component name as a filename.
    
    Args:
        component_name: PascalCase component name
        
    Returns:
        Filename with .jsx extension
    """
    return f"{component_name}.jsx"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix


def extract_code_from_response(response: str) -> Optional[str]:
    """
    Extract code from an LLM response that may contain markdown.
    
    Args:
        response: LLM response string
        
    Returns:
        Extracted code or None
    """
    response = response.strip()
    
    # Try to find code blocks
    patterns = [
        r'```(?:jsx|javascript|js|tsx|typescript)\s*\n(.*?)\n```',
        r'```\s*\n(.*?)\n```',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # If no code block found, return the whole response if it looks like code
    if response.startswith('import ') or response.startswith('const ') or response.startswith('export '):
        return response
    
    return None


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to slugify
        
    Returns:
        URL-friendly string
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    
    # Remove non-alphanumeric characters (except hyphens)
    text = re.sub(r'[^a-z0-9-]', '', text)
    
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text


def get_section_order(sections: list) -> list:
    """
    Sort sections in a logical display order.
    
    Args:
        sections: List of section names
        
    Returns:
        Ordered list of sections
    """
    order_map = {
        'hero': 0,
        'about': 1,
        'skills': 2,
        'experience': 3,
        'projects': 4,
        'education': 5,
        'certifications': 6,
        'contact': 7
    }
    
    return sorted(sections, key=lambda x: order_map.get(x.lower(), 99))


def validate_color_hex(color: str) -> bool:
    """
    Validate if a string is a valid hex color.
    
    Args:
        color: Color string to validate
        
    Returns:
        True if valid hex color
    """
    if not color:
        return False
    
    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    return bool(re.match(pattern, color))


def ensure_hex_color(color: str, default: str = "#000000") -> str:
    """
    Ensure a color string is a valid hex color.
    
    Args:
        color: Color string
        default: Default color if invalid
        
    Returns:
        Valid hex color
    """
    if validate_color_hex(color):
        return color
    
    # Try adding # if missing
    if re.match(r'^([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color):
        return f"#{color}"
    
    return default


def merge_dicts(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        override: Dictionary to merge on top
        
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
