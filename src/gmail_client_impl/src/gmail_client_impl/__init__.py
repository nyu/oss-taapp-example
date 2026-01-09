"""Public exports for the Gmail client implementation package."""

from gmail_client_impl.gmail_impl import (
    GmailClient,
    get_client_impl,
)
from gmail_client_impl.gmail_impl import (
    register as _register_client,
)
from gmail_client_impl.message_impl import (
    GmailMessage,
    get_message_impl,
)
from gmail_client_impl.message_impl import (
    register as _register_message,
)

__all__ = [
    "GmailClient",
    "GmailMessage",
    "get_client_impl",
    "get_message_impl",
    "register",
]


def register() -> None:
    """Register the Gmail client and message implementations."""
    _register_client()
    _register_message()


# Dependency Injection happens at import time
register()
