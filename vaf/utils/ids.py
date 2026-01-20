"""ID generation utilities."""

from uuid import uuid4


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        A unique identifier string
    """
    uid = uuid4().hex[:12]
    if prefix:
        return f"{prefix}_{uid}"
    return uid
