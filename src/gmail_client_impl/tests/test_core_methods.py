"""Unit tests for GmailClient core methods.

This module contains comprehensive unit tests for the core business logic
of the GmailClient class, mocking all external dependencies.
"""

from unittest.mock import Mock, patch

import pytest
from googleapiclient.errors import HttpError

from gmail_client_impl.gmail_impl import GmailClient

# Constants for Gmail API values
GMAIL_USER_ID = "me"
GMAIL_FORMAT_RAW = "raw"
GMAIL_LABEL_UNREAD = "UNREAD"
DEFAULT_MAX_RESULTS = 10
EXPECTED_MESSAGES_COUNT = 2


class TestGmailClientCoreMethods:
    """Test cases for GmailClient core methods with mocked dependencies."""

    def setup_method(self) -> None:
        """Create a GmailClient with mocked service."""
        self.mock_service = Mock()
        self.client = GmailClient(service=self.mock_service)

    def test_get_message_success(self) -> None:
        """Test successful message retrieval."""
        # ARRANGE
        message_id = "test_msg_123"
        raw_content = "fake_raw_email_data"

        # Mock the Gmail API call chain
        mock_users = Mock()
        mock_messages = Mock()
        mock_get = Mock()
        Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.get.return_value = mock_get
        mock_get.execute.return_value = {"raw": raw_content}

        # Mock the message factory
        mock_message = Mock()
        with patch(
            "gmail_client_impl.gmail_impl.message.get_message",
            return_value=mock_message,
        ) as mock_factory:
            # ACT
            result = self.client.get_message(message_id)

            # ASSERT
            assert result is mock_message
            mock_messages.get.assert_called_once_with(
                userId=GMAIL_USER_ID,
                id=message_id,
                format=GMAIL_FORMAT_RAW,
            )
            mock_get.execute.assert_called_once()
            mock_factory.assert_called_once_with(msg_id=message_id, raw_data=raw_content)

    def test_get_message_no_raw_content(self) -> None:
        """Test get_message when API returns no raw content."""
        # ARRANGE
        message_id = "test_msg_123"

        mock_users = Mock()
        mock_messages = Mock()
        mock_get = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.get.return_value = mock_get
        mock_get.execute.return_value = {}  # No 'raw' key

        # ACT & ASSERT
        with pytest.raises(ValueError, match="No raw content found for message test_msg_123"):
            self.client.get_message(message_id)

    def test_get_message_api_exception(self) -> None:
        """Test get_message when Gmail API raises an exception."""
        # ARRANGE
        message_id = "test_msg_123"

        mock_users = Mock()
        mock_messages = Mock()
        mock_get = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.get.return_value = mock_get
        mock_get.execute.side_effect = Exception("API Error")

        # ACT & ASSERT
        with pytest.raises(Exception, match="API Error"):
            self.client.get_message(message_id)

    def test_delete_message_success(self) -> None:
        """Test successful message deletion."""
        # ARRANGE
        message_id = "test_msg_123"

        mock_users = Mock()
        mock_messages = Mock()
        mock_delete = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.delete.return_value = mock_delete
        mock_delete.execute.return_value = None

        # ACT
        result = self.client.delete_message(message_id)

        # ASSERT
        assert result is True
        mock_messages.delete.assert_called_once_with(userId=GMAIL_USER_ID, id=message_id)
        mock_delete.execute.assert_called_once()

    def test_delete_message_api_exception(self) -> None:
        """Test delete_message when Gmail API raises an exception."""
        # ARRANGE
        message_id = "test_msg_123"

        mock_users = Mock()
        mock_messages = Mock()
        mock_delete = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.delete.return_value = mock_delete
        error_response = Mock(status=500, reason="Internal Server Error")
        mock_delete.execute.side_effect = HttpError(error_response, b"Delete failed")

        # ACT
        result = self.client.delete_message(message_id)

        # ASSERT
        assert result is False

    def test_mark_as_read_success(self) -> None:
        """Test successful marking message as read."""
        # ARRANGE
        message_id = "test_msg_123"

        mock_users = Mock()
        mock_messages = Mock()
        mock_modify = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.modify.return_value = mock_modify
        mock_modify.execute.return_value = None

        # ACT
        result = self.client.mark_as_read(message_id)

        # ASSERT
        assert result is True
        mock_messages.modify.assert_called_once_with(
            userId=GMAIL_USER_ID,
            id=message_id,
            body={"removeLabelIds": [GMAIL_LABEL_UNREAD]},
        )
        mock_modify.execute.assert_called_once()

    def test_mark_as_read_api_exception(self) -> None:
        """Test mark_as_read when Gmail API raises an exception."""
        # ARRANGE
        message_id = "test_msg_123"

        mock_users = Mock()
        mock_messages = Mock()
        mock_modify = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.modify.return_value = mock_modify
        error_response = Mock(status=500, reason="Internal Server Error")
        mock_modify.execute.side_effect = HttpError(error_response, b"Modify failed")

        # ACT
        result = self.client.mark_as_read(message_id)

        # ASSERT
        assert result is False

    def test_get_messages_success(self) -> None:
        """Test successful message listing."""
        # ARRANGE
        max_results = 5
        mock_messages_list = [
            {"id": "msg1"},
            {"id": "msg2"},
            {"id": "msg3"},
        ]

        # Mock the list call
        mock_users = Mock()
        mock_messages = Mock()
        mock_list = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.list.return_value = mock_list
        mock_list.execute.return_value = {"messages": mock_messages_list}

        # Mock the individual message get calls
        mock_get = Mock()
        mock_messages.get.return_value = mock_get
        mock_get.execute.side_effect = [
            {"raw": "raw_data_1"},
            {"raw": "raw_data_2"},
            {"raw": "raw_data_3"},
        ]

        # Mock the message factory
        mock_message_1 = Mock()
        mock_message_2 = Mock()
        mock_message_3 = Mock()

        with patch(
            "gmail_client_impl.gmail_impl.message.get_message",
            side_effect=[
                mock_message_1,
                mock_message_2,
                mock_message_3,
            ],
        ) as mock_factory:
            # ACT
            messages = list(self.client.get_messages(max_results))

            # ASSERT
            assert len(messages) == len(mock_messages_list)
            assert messages == [mock_message_1, mock_message_2, mock_message_3]

            # Verify list call
            mock_messages.list.assert_called_once_with(userId=GMAIL_USER_ID, maxResults=max_results)

            # Verify individual get calls
            assert mock_messages.get.call_count == len(mock_messages_list)
            mock_messages.get.assert_any_call(
                userId=GMAIL_USER_ID,
                id="msg1",
                format=GMAIL_FORMAT_RAW,
            )
            mock_messages.get.assert_any_call(
                userId=GMAIL_USER_ID,
                id="msg2",
                format=GMAIL_FORMAT_RAW,
            )
            mock_messages.get.assert_any_call(
                userId=GMAIL_USER_ID,
                id="msg3",
                format=GMAIL_FORMAT_RAW,
            )

            # Verify factory calls
            assert mock_factory.call_count == len(mock_messages_list)
            mock_factory.assert_any_call(msg_id="msg1", raw_data="raw_data_1")
            mock_factory.assert_any_call(msg_id="msg2", raw_data="raw_data_2")
            mock_factory.assert_any_call(msg_id="msg3", raw_data="raw_data_3")

    def test_get_messages_empty_inbox(self) -> None:
        """Test get_messages when inbox is empty."""
        # ARRANGE
        mock_users = Mock()
        mock_messages = Mock()
        mock_list = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.list.return_value = mock_list
        mock_list.execute.return_value = {"messages": []}

        # ACT
        messages = list(self.client.get_messages())

        # ASSERT
        assert len(messages) == 0
        mock_messages.list.assert_called_once_with(
            userId=GMAIL_USER_ID,
            maxResults=DEFAULT_MAX_RESULTS,
        )

    def test_get_messages_no_messages_key(self) -> None:
        """Test get_messages when API response has no 'messages' key."""
        # ARRANGE
        mock_users = Mock()
        mock_messages = Mock()
        mock_list = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.list.return_value = mock_list
        mock_list.execute.return_value = {}  # No 'messages' key

        # ACT
        messages = list(self.client.get_messages())

        # ASSERT
        assert len(messages) == 0

    def test_get_messages_message_without_id(self) -> None:
        """Test get_messages skips messages without ID."""
        # ARRANGE
        mock_messages_list = [
            {"id": "msg1"},
            {},  # Message without ID
            {"id": "msg3"},
        ]

        mock_users = Mock()
        mock_messages = Mock()
        mock_list = Mock()
        mock_get = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.list.return_value = mock_list
        mock_list.execute.return_value = {"messages": mock_messages_list}

        mock_messages.get.return_value = mock_get
        mock_get.execute.side_effect = [
            {"raw": "raw_data_1"},
            {"raw": "raw_data_3"},
        ]

        mock_message_1 = Mock()
        mock_message_3 = Mock()

        with patch(
            "gmail_client_impl.gmail_impl.message.get_message",
            side_effect=[
                mock_message_1,
                mock_message_3,
            ],
        ):
            # ACT
            messages = list(self.client.get_messages())

            # ASSERT
            assert len(messages) == EXPECTED_MESSAGES_COUNT
            assert messages == [mock_message_1, mock_message_3]
            assert mock_messages.get.call_count == EXPECTED_MESSAGES_COUNT

    def test_get_messages_message_without_raw_content(self) -> None:
        """Test get_messages skips messages without raw content."""
        # ARRANGE
        mock_messages_list = [
            {"id": "msg1"},
            {"id": "msg2"},
        ]

        mock_users = Mock()
        mock_messages = Mock()
        mock_list = Mock()
        mock_get = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.list.return_value = mock_list
        mock_list.execute.return_value = {"messages": mock_messages_list}

        mock_messages.get.return_value = mock_get
        mock_get.execute.side_effect = [
            {"raw": "raw_data_1"},
            {},  # No raw content
        ]

        mock_message_1 = Mock()

        with patch(
            "gmail_client_impl.gmail_impl.message.get_message",
            return_value=mock_message_1,
        ) as mock_factory:
            # ACT
            messages = list(self.client.get_messages())

            # ASSERT
            assert len(messages) == 1
            assert messages == [mock_message_1]

            mock_factory.assert_called_once_with(msg_id="msg1", raw_data="raw_data_1")

    def test_get_messages_default_max_results(self) -> None:
        """Test get_messages uses default max_results."""
        # ARRANGE
        mock_users = Mock()
        mock_messages = Mock()
        mock_list = Mock()

        self.mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.list.return_value = mock_list
        mock_list.execute.return_value = {"messages": []}

        # ACT
        list(self.client.get_messages())

        # ASSERT
        mock_messages.list.assert_called_once_with(
            userId=GMAIL_USER_ID,
            maxResults=DEFAULT_MAX_RESULTS,
        )
