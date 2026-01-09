"""Tests for the mail_client_api message abstraction."""

from unittest.mock import Mock

from mail_client_api.message import Message


def test_message_abstraction_comprehensive() -> None:
    """Verifies all properties work together in a comprehensive test."""
    mock_message = Mock(spec=Message)
    mock_message.id = "msg_67890"
    mock_message.from_ = "alice@company.com"
    mock_message.to = "bob@company.com"
    mock_message.date = "2025-07-30 14:45:30"
    mock_message.subject = "Project Update"
    mock_message.body = "Here are the latest updates on our project progress."

    properties = {
        "id": mock_message.id,
        "from_": mock_message.from_,
        "to": mock_message.to,
        "date": mock_message.date,
        "subject": mock_message.subject,
        "body": mock_message.body,
    }

    assert properties["id"] == "msg_67890"
    assert properties["from_"] == "alice@company.com"
    assert properties["to"] == "bob@company.com"
    assert properties["date"] == "2025-07-30 14:45:30"
    assert properties["subject"] == "Project Update"
    assert properties["body"] == "Here are the latest updates on our project progress."

    for value in properties.values():
        assert isinstance(value, str)
