"""
Utility functions
"""

import logging
import sys
from typing import Dict, List


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def format_chat_history(history: List[Dict[str, str]]) -> str:
    """Format chat history as string"""
    if not history:
        return "No previous messages"

    formatted = []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        role_display = "User" if role == "user" else "Assistant"
        formatted.append(f"{role_display}: {content}")

    return "\n".join(formatted)


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_url(url: str) -> str:
    """Clean and normalize URL"""
    url = url.strip()
    if url.startswith(("http://", "https://")):
        return url
    return f"https://{url}"
