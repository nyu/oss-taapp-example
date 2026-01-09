"""Gmail Client Implementation.

This module provides a concrete implementation of the mail client API using the Gmail API.
It handles OAuth2 authentication and provides methods to interact with Gmail messages.

The implementation supports multiple authentication modes:
    - Environment variables (for CI/CD environments)
    - Local token file (for development)
    - Interactive OAuth flow (for initial setup)
"""

import logging
import os
from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar

import mail_client_api
from google.auth.exceptions import GoogleAuthError, RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import-untyped]
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError
from mail_client_api import message

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # If python-dotenv is not available, check if .env file exists
    # and manually load it
    env_path = Path(".env")
    if env_path.exists():
        with env_path.open() as f:
            for raw_line in f:
                line = raw_line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


class GmailClient(mail_client_api.Client):
    """Concrete implementation of the Client abstraction using Gmail API.

    This class provides a complete implementation of the mail_client_api.Client abstraction
    using Google's Gmail API. It handles OAuth2 authentication automatically and provides
    methods to interact with Gmail messages.

    Attributes:
        SCOPES: List of OAuth2 scopes required for Gmail API access.
        FAILURE_TO_CRED: Error message for authentication failures.
        service: The authenticated Gmail API service object.

    Authentication Flow:
        1. If `interactive=True`, forces interactive OAuth flow
        2. Try environment variables (GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN)
        3. Try local token.json file
        4. Fallback to interactive OAuth flow

    Environment Variables:
        - GMAIL_CLIENT_ID: OAuth2 client ID
        - GMAIL_CLIENT_SECRET: OAuth2 client secret
        - GMAIL_REFRESH_TOKEN: OAuth2 refresh token
        - GMAIL_TOKEN_URI: OAuth2 token URI (optional, defaults to Google's endpoint)

    """

    TOKEN_PATH: ClassVar[str] = "token.json"  # noqa: S105
    CREDENTIALS_PATH: ClassVar[str] = "credentials.json"
    SCOPES: ClassVar[list[str]] = [
        "https://mail.google.com/",
    ]
    FAILURE_TO_CRED = "Failed to obtain credentials. Please check your setup."

    def __init__(self, service: Resource | None = None, *, interactive: bool = False) -> None:
        """Initialize the GmailClient, handling authentication."""
        self.logger = logging.getLogger(__name__)
        if service:
            self.service = service
            return  # Skip auth if service is provided

        creds: Credentials | None = None
        token_path = self.TOKEN_PATH
        creds_path = self.CREDENTIALS_PATH

        if interactive:
            creds = self._run_interactive_flow(creds_path)

        if not creds and not interactive:
            creds = self._auth_from_env()

        if not creds and not interactive:
            creds = self._auth_from_token_file(token_path)

        if not creds or (creds and not creds.valid and not creds.refresh_token):
            if not interactive:
                msg = (
                    "No valid credentials found and interactive mode is disabled. "
                    "Please provide valid credentials via environment variables or token file."
                )
                raise RuntimeError(msg)

            creds = self._run_interactive_flow(creds_path)
            if not creds:
                msg = "Interactive authentication failed."
                raise RuntimeError(msg)

        if not creds or not creds.valid:
            raise RuntimeError(self.FAILURE_TO_CRED)

        if interactive or (creds.refresh_token and not Path(token_path).exists()):
            self._save_token(creds, token_path)

        self.service = build("gmail", "v1", credentials=creds)

    def _run_interactive_flow(self, creds_path: str) -> Credentials | None:
        """Run the interactive OAuth flow.

        This method launches a local web server to handle the OAuth2 flow,
        opening the user's browser to complete authentication with Google.
        """
        if not Path(creds_path).exists():
            raise FileNotFoundError(f"'{creds_path}' not found. Cannot run interactive auth.")  # noqa: EM102 TRY003
        flow = InstalledAppFlow.from_client_secrets_file(
            creds_path,
            self.SCOPES,
        )
        return flow.run_local_server(port=0)  # type: ignore[no-any-return]

    def _auth_from_env(self) -> Credentials | None:
        """Attempt to authenticate using environment variables.

        Expected environment variables:
            GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN
            optional: GMAIL_TOKEN_URI

        Returns:
            A refreshed Credentials object on success, or None on failure.

        """
        client_id = os.environ.get("GMAIL_CLIENT_ID")
        client_secret = os.environ.get("GMAIL_CLIENT_SECRET")
        refresh_token = os.environ.get("GMAIL_REFRESH_TOKEN")
        token_uri = os.environ.get("GMAIL_TOKEN_URI", "https://oauth2.googleapis.com/token")

        if not (client_id and client_secret and refresh_token):
            return None

        try:
            creds = Credentials(  # type: ignore[no-untyped-call]
                None,
                refresh_token=refresh_token,
                token_uri=token_uri,
                client_id=client_id,
                client_secret=client_secret,
                scopes=self.SCOPES,
            )
            creds.refresh(Request())  # type: ignore[no-untyped-call]
            return creds  # noqa: TRY300
        except (GoogleAuthError, RefreshError, OSError, ValueError):
            return None

    def _auth_from_token_file(self, token_path: str) -> Credentials | None:
        """Attempt to load credentials from a token file and refresh if needed.

        Args:
            token_path: Path to token file.

        Returns:
            A valid Credentials object or None if loading/refresh fails.

        """
        try:
            if not Path(token_path).exists():
                return None

            creds = Credentials.from_authorized_user_file(  # type: ignore[no-untyped-call]
                token_path,
                self.SCOPES,
            )

            if creds and not creds.valid and creds.refresh_token:
                try:
                    creds.refresh(Request())  # type: ignore[no-untyped-call]
                except (GoogleAuthError, RefreshError, OSError, ValueError):
                    return None
        except (GoogleAuthError, RefreshError, OSError, ValueError):
            return None

        return creds  # type: ignore[no-any-return]

    def _save_token(self, creds: Credentials, token_path: str) -> None:
        """Save the credentials token to a file.

        Persists the OAuth2 credentials to a JSON file for future use,
        avoiding the need to re-authenticate on subsequent runs.

        Args:
            creds: The credentials object to save.
            token_path: Path where the token file should be saved.

        Note:
            The token file contains sensitive information and should be kept secure.
            It's automatically added to .gitignore in most project templates.

        """
        with Path(token_path).open("w") as token:
            token.write(creds.to_json())  # type: ignore[no-untyped-call]

    def get_message(self, message_id: str) -> message.Message:
        """Retrieve a specific message by its ID.

        Args:
            message_id: The unique identifier of the message to retrieve.

        Returns:
            A Message object containing the email data.

        Raises:
            Exception: If the message cannot be retrieved from the Gmail API.

        """
        msg_data = (
            self.service.users()  # type: ignore[attr-defined]
            .messages()
            .get(userId="me", id=message_id, format="raw")
            .execute()
        )

        raw_content = msg_data.get("raw")
        if not raw_content:
            msg = f"No raw content found for message {message_id}"
            raise ValueError(msg)

        return message.get_message(
            msg_id=message_id,
            raw_data=raw_content,
        )

    def delete_message(self, message_id: str) -> bool:
        """Delete a message from the mailbox.

        Args:
            message_id: The unique identifier of the message to delete.

        Returns:
            True if the message was successfully deleted, False otherwise.

        Note:
            This method permanently deletes the message from Gmail.
            The message cannot be recovered after deletion.

        """
        subject = "Unknown"
        try:
            msg = self.get_message(message_id)
            subject = msg.subject or "No subject"
            self.logger.info("Attempting to delete message %s w subject: %s", message_id, subject)

        except (HttpError, OSError, ValueError) as e:
            self.logger.warning("Could not retrieve %s details before deletion: %s", message_id, e)

        try:
            (
                self.service.users()  # type: ignore[attr-defined]
                .messages()
                .delete(userId="me", id=message_id)
                .execute()
            )
        except (HttpError, OSError, ValueError) as e:
            self.logger.exception("Failed to delete message %s (subject: %s)", message_id, subject)
            self.logger.debug("Error details: %s", e)
            return False
        else:
            return True

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read."""
        try:
            (
                self.service.users()  # type: ignore[attr-defined]
                .messages()
                .modify(
                    userId="me",
                    id=message_id,
                    body={"removeLabelIds": ["UNREAD"]},
                )
                .execute()
            )
        except (HttpError, OSError, ValueError):
            return False
        else:
            return True

    def get_messages(self, max_results: int = 10) -> Iterator[message.Message]:
        """Retrieve messages from the Gmail inbox.

        This method fetches a list of message summaries from the Gmail API,
        then retrieves the raw content for each message. It uses the
        `message.get_message` factory function to construct and yield
        a clean, contract-compliant Message object for each email.

        Args:
            max_results: The maximum number of messages to retrieve.

        Yields:
            An iterator of `message.Message` objects.

        """
        results = (
            self.service.users()  # type: ignore[attr-defined]
            .messages()
            .list(userId="me", maxResults=max_results)
            .execute()
        )
        messages_summary = results.get("messages", [])

        for msg_summary in messages_summary:
            if "id" not in msg_summary:
                continue

            msg_data = (
                self.service.users()  # type: ignore[attr-defined]
                .messages()
                .get(userId="me", id=msg_summary["id"], format="raw")
                .execute()
            )
            raw_content = msg_data.get("raw")
            if raw_content:
                yield message.get_message(
                    msg_id=msg_summary["id"],
                    raw_data=raw_content,
                )


def get_client_impl(*, interactive: bool = False) -> mail_client_api.Client:
    """Return a configured :class:`GmailClient` instance."""
    return GmailClient(interactive=interactive)


def register() -> None:
    """Register the Gmail client implementation with the mail client API."""
    mail_client_api.get_client = get_client_impl
