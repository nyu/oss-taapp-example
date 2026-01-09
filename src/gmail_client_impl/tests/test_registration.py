"""Tests for explicit registration helpers exposed by ``gmail_client_impl``."""

import importlib

import mail_client_api
import pytest
from mail_client_api import message as message_protocol

import gmail_client_impl


def test_register_binds_factories(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure calling register wires the client and message factories."""
    client_protocol = importlib.import_module("mail_client_api.client")
    message_protocol_module = importlib.import_module("mail_client_api.message")

    # Reset to protocol defaults before invoking register.
    monkeypatch.setattr(mail_client_api, "get_client", client_protocol.get_client, raising=False)
    monkeypatch.setattr(
        message_protocol,
        "get_message",
        message_protocol_module.get_message,
        raising=False,
    )

    gmail_client_impl.register()

    assert mail_client_api.get_client is gmail_client_impl.get_client_impl
    assert message_protocol.get_message is gmail_client_impl.get_message_impl
