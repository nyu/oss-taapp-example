"""Tests for the mail client API abstract base classes.

This module contains unit tests that verify the contracts and behavior
of the mail_client_api.Client and mail_client_api.Message abstractions.
These tests use mocks to demonstrate how implementations should behave
and serve as documentation for the expected API contracts.
"""

from unittest.mock import Mock

from mail_client_api import Client, Message


def test_client_get_messages() -> None:
    """Verifies and demonstrates the contract for the `get_messages` method.

    This test ensures that any implementation of the `Client` abstraction
    must have a `get_messages` method that returns an iterator of `Message` objects.
    """
    # ARRANGE: Create mocks that conform to our abstractions.
    mock_message = Mock(spec=Message)
    mock_message.id = "msg_1"
    mock_message.subject = "Test Subject"

    mock_client = Mock(spec=Client)
    mock_client.get_messages.return_value = iter([mock_message])

    # ACT: Use the client as a consumer would.
    messages = mock_client.get_messages()
    first_message = next(messages, None)

    # ASSERT: Verify the interaction and the result.
    mock_client.get_messages.assert_called_once_with()
    assert first_message is not None
    assert first_message.id == "msg_1"
    assert first_message.subject == "Test Subject"


def test_client_get_message() -> None:
    """Verifies and demonstrates the contract for the `get_message` method."""
    # ARRANGE
    mock_message = Mock(spec=Message)
    mock_message.id = "specific_msg_id"

    mock_client = Mock(spec=Client)
    mock_client.get_message.return_value = mock_message

    # ACT
    retrieved_message = mock_client.get_message(message_id="specific_msg_id")

    # ASSERT
    mock_client.get_message.assert_called_once_with(message_id="specific_msg_id")
    assert retrieved_message.id == "specific_msg_id"


def test_client_delete_message() -> None:
    """Verifies and demonstrates the contract for the `delete_message` method."""
    # ARRANGE
    mock_client = Mock(spec=Client)
    mock_client.delete_message.return_value = True

    # ACT
    success = mock_client.delete_message(message_id="msg_to_delete")

    # ASSERT
    mock_client.delete_message.assert_called_once_with(message_id="msg_to_delete")
    assert success is True


def test_client_mark_as_read() -> None:
    """Verifies and demonstrates the contract for the `mark_as_read` method."""
    # ARRANGE
    mock_client = Mock(spec=Client)
    mock_client.mark_as_read.return_value = True

    # ACT
    success = mock_client.mark_as_read(message_id="msg_to_mark_read")

    # ASSERT
    mock_client.mark_as_read.assert_called_once_with(message_id="msg_to_mark_read")
    assert success is True
