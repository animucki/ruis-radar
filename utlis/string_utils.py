import re

def add_separator(description_item):
    """Add a separator between artist and piece if no space is present."""
    # Look for uppercase letters followed by another uppercase letter, add space between them
    return re.sub(r"([a-zA-Z])([A-Z])", r"\1 \2", description_item)