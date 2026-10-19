"""Jarvis personality: brief, confident, butler-like.

Replies are kept to 1-2 sentences — this is a voice interface, not a chat
window. The assistant addresses the user by name, but sparingly: greetings,
farewells, and the occasional confirmation. Never fluffy, never chatty.
"""

from datetime import datetime

from . import config


def greeting(now=None):
    """Time-of-day aware greeting, e.g. 'Good morning, Mohsin.'"""
    hour = (now or datetime.now()).hour
    if 5 <= hour < 12:
        part = "morning"
    elif 12 <= hour < 18:
        part = "afternoon"
    else:
        part = "evening"
    return f"Good {part}, {config.USER_NAME}."


def farewell():
    """Sign-off when the session ends."""
    return f"Goodbye, {config.USER_NAME}."
