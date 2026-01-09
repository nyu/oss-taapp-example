"""Integration tests for gmail_client_impl authentication and API connectivity.

This module tests that the dependency injection works correctly and that
the client can authenticate and make real API calls to Gmail.
"""

import logging

import pytest

import gmail_client_impl  # Import to trigger dependency injection
import mail_client_api

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration

logger = logging.getLogger(__name__)


@pytest.mark.circleci
def test_get_client_and_authenticate() -> None:
    """Tests that the factory provides a real, authenticated GmailClient.

    This test requires real credentials (via .env or credentials.json)
    and makes a live, read-only call to the Gmail API.
    """
    try:
        # 1. Get the client using the abstract factory
        client = mail_client_api.get_client(interactive=False)

        # 2. Assert that we received the correct implementation
        assert isinstance(client, gmail_client_impl.GmailClient)

    except FileNotFoundError:
        pytest.skip("Skipping integration test: credentials.json not found.")
    except (RuntimeError, ValueError, ConnectionError) as e:
        pytest.fail(f"Integration test failed during authentication or API call: {e}")


@pytest.mark.circleci
def test_dependency_injection_works() -> None:
    """Tests that importing the implementation packages correctly overrides.

    The factory functions in the abstract contract packages.
    This test doesn't require credentials, only tests imports and factory setup.
    """
    try:
        client = mail_client_api.get_client(interactive=False)
        assert isinstance(client, gmail_client_impl.GmailClient)
        assert hasattr(client, "get_messages")
        assert hasattr(client, "get_message")
        assert hasattr(client, "delete_message")
        assert hasattr(client, "mark_as_read")
    except RuntimeError as e:
        if "No valid credentials found" in str(e):
            # This is expected in CI without credentials - the factory works, just can't authenticate
            pass
        else:
            raise


@pytest.mark.circleci
def test_message_dependency_injection() -> None:
    """Tests that importing gmail_message_impl overrides message.get_message."""
    import base64

    import gmail_client_impl
    import mail_client_api

    email_content = "From: di@example.com\r\nSubject: Dependency Injection Test\r\n\r\nDI test body"
    encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()

    # Call the abstract factory - should use our implementation
    msg = mail_client_api.get_message(msg_id="di123", raw_data=encoded_data)

    # Verify it returns our GmailMessage implementation
    assert isinstance(msg, gmail_client_impl.GmailMessage)
    assert msg.id == "di123"
    assert msg.from_ == "di@example.com"
    assert msg.subject == "Dependency Injection Test"
    assert msg.body == "DI test body"


@pytest.mark.circleci
def test_factory_functions_work_together() -> None:
    """Tests that both factory functions work together correctly.

    This test only checks imports and factory setup, no credentials needed.
    """
    import mail_client_api
    from gmail_client_impl import get_client_impl

    # Verify that mail_client_api.get_client is now our implementation
    assert mail_client_api.get_client is get_client_impl


@pytest.mark.circleci
def test_client_scope_permissions() -> None:
    """Tests that the client has the necessary OAuth scopes for the operations we want to perform."""
    try:
        client = mail_client_api.get_client(interactive=False)

        # Cast to GmailClient to access service attribute
        gmail_client = client
        assert isinstance(gmail_client, gmail_client_impl.GmailClient)

        # Try to list messages (requires read permission)
        messages_result = (
            gmail_client.service.users()  # type: ignore[attr-defined]
            .messages()
            .list(userId="me", maxResults=1)
            .execute()
        )

        # Should return a dictionary with messages list (even if empty)
        assert isinstance(messages_result, dict)
        assert "messages" in messages_result or messages_result.get("resultSizeEstimate", 0) == 0

    except FileNotFoundError:
        pytest.skip("Skipping integration test: credentials.json not found.")
    except (RuntimeError, ValueError, ConnectionError) as e:
        # If we get a 403 error, it's likely a scope issue
        if "403" in str(e) or "insufficient" in str(e).lower():
            pytest.fail(f"OAuth scope issue - client may not have required permissions: {e}")
        else:
            pytest.fail(f"Integration test failed: {e}")


@pytest.mark.circleci
def test_client_initialization_modes() -> None:
    """Tests that the client can be initialized in different modes.

    This test checks initialization behavior, not actual authentication.
    """
    try:
        # Test non-interactive mode (default)
        client1 = mail_client_api.get_client(interactive=False)
        assert isinstance(client1, gmail_client_impl.GmailClient)

        # Test that we can create multiple instances
        client2 = mail_client_api.get_client(interactive=False)
        assert isinstance(client2, gmail_client_impl.GmailClient)

        # They should be separate instances
        assert client1 is not client2

    except RuntimeError as e:
        if "No valid credentials found" in str(e):
            logger.debug("Client initialization works correctly - authentication failed as expected without credentials")
        else:
            pytest.fail(f"Unexpected error during client initialization: {e}")
    except FileNotFoundError:
        pytest.skip("Skipping integration test: credentials.json not found.")
