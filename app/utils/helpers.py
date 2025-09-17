"""
Helper utilities for the bot.
"""
from typing import Optional

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def format_user_mention(user_id: int, first_name: str, last_name: Optional[str] = None) -> str:
    """Format user mention for logging."""
    full_name = first_name
    if last_name:
        full_name += f" {last_name}"
    return f"{full_name} (ID: {user_id})"

def is_admin_command(text: str) -> bool:
    """Check if message is an admin command."""
    admin_commands = ["/stats", "/ban", "/kick", "/mute"]
    return any(text.startswith(cmd) for cmd in admin_commands)
