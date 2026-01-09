"""Public export surface for ``mail_client_api``."""

from mail_client_api import message
from mail_client_api.client import Client, get_client
from mail_client_api.message import Message, get_message

__all__ = ["Client", "Message", "get_client", "get_message", "message"]
