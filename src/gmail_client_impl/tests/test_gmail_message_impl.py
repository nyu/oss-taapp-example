"""Tests for GmailMessage implementation colocated with GmailClient."""

import base64
from email.message import EmailMessage

from gmail_client_impl.message_impl import GmailMessage


class TestGmailMessage:
    """Test cases for the GmailMessage class."""

    def test_basic_message_creation(self) -> None:
        """Test creating a GmailMessage with valid data."""
        email_content = (
            "From: sender@example.com\r\n"
            "To: recipient@example.com\r\n"
            "Subject: Test Subject\r\n"
            "Date: Wed, 30 Jul 2025 10:30:00 +0000\r\n"
            "\r\n"
            "This is the message body."
        )

        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        message = GmailMessage(msg_id="test123", raw_data=encoded_data)

        assert message.id == "test123"
        assert message.from_ == "sender@example.com"
        assert message.to == "recipient@example.com"
        assert message.subject == "Test Subject"
        assert message.date == "07/30/2025"
        assert message.body == "This is the message body."

    def test_message_with_encoded_subject(self) -> None:
        """Test message with RFC 2047 encoded subject."""
        email_content = (
            "From: sender@example.com\r\n"
            "To: recipient@example.com\r\n"
            "Subject: =?UTF-8?B?VGVzdCBTdWJqZWN0IGVuY29kZWQ=?=\r\n"
            "Date: Wed, 30 Jul 2025 10:30:00 +0000\r\n"
            "\r\n"
            "Message body"
        )

        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        message = GmailMessage(msg_id="test456", raw_data=encoded_data)

        assert message.subject == "Test Subject encoded"

    def test_multipart_message(self) -> None:
        """Test parsing a multipart message."""
        email_msg = EmailMessage()
        email_msg["From"] = "sender@example.com"
        email_msg["To"] = "recipient@example.com"
        email_msg["Subject"] = "Multipart Test"
        email_msg["Date"] = "Wed, 30 Jul 2025 10:30:00 +0000"

        email_msg.set_content("This is the plain text body.")
        email_msg.add_alternative(
            "<html><body><p>This is the HTML body.</p></body></html>",
            subtype="html",
        )

        raw_email = email_msg.as_bytes()
        encoded_data = base64.urlsafe_b64encode(raw_email).decode()

        message = GmailMessage(msg_id="multipart123", raw_data=encoded_data)

        assert message.id == "multipart123"
        assert message.from_ == "sender@example.com"
        assert "This is the plain text body." in message.body

    def test_date_parsing_fallback(self) -> None:
        """Test date parsing with invalid date format."""
        email_content = "From: sender@example.com\r\nDate: Invalid Date Format\r\n\r\nMessage body"

        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        message = GmailMessage(msg_id="baddate123", raw_data=encoded_data)

        assert message.date == "Invalid Date Format"

    def test_subject_without_encoding(self) -> None:
        """Test subject that doesn't need RFC 2047 decoding."""
        email_content = (
            "From: sender@example.com\r\nSubject: Plain Subject Line\r\n\r\nMessage body"
        )

        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        message = GmailMessage(msg_id="plain123", raw_data=encoded_data)

        assert message.subject == "Plain Subject Line"

    def test_message_with_attachment(self) -> None:
        """Test multipart message with attachment (should extract text body)."""
        email_msg = EmailMessage()
        email_msg["From"] = "sender@example.com"
        email_msg["Subject"] = "Message with Attachment"
        email_msg["Date"] = "Wed, 30 Jul 2025 10:30:00 +0000"

        email_msg.set_content("This is the main message body.")
        email_msg.add_attachment(
            b"fake attachment data",
            maintype="application",
            subtype="octet-stream",
            filename="attachment.txt",
        )

        raw_email = email_msg.as_bytes()
        encoded_data = base64.urlsafe_b64encode(raw_email).decode()

        message = GmailMessage(msg_id="attach123", raw_data=encoded_data)

        assert "This is the main message body." in message.body
        assert "fake attachment data" not in message.body

    def test_message_body_encoding(self) -> None:
        """Test message body with non-UTF-8 encoding."""
        body_text = "Café and naïve"
        email_content = (
            b"From: sender@example.com\r\nSubject: Encoding Test\r\nContent-Type: text/plain; charset=iso-8859-1\r\n\r\n"
        ) + body_text.encode("iso-8859-1")

        encoded_data = base64.urlsafe_b64encode(email_content).decode()
        message = GmailMessage(msg_id="encoding123", raw_data=encoded_data)

        assert message.id == "encoding123"
        assert message.subject == "Encoding Test"
        assert len(message.body) > 0

    def test_message_without_plain_text_body(self) -> None:
        """Test multipart message without plain text part."""
        email_msg = EmailMessage()
        email_msg["From"] = "sender@example.com"
        email_msg["Subject"] = "HTML Only"

        email_msg.set_content(
            "<html><body><h1>HTML Only Message</h1></body></html>",
            subtype="html",
        )

        raw_email = email_msg.as_bytes()
        encoded_data = base64.urlsafe_b64encode(raw_email).decode()

        message = GmailMessage(msg_id="htmlonly123", raw_data=encoded_data)

        assert "<h1>HTML Only Message</h1>" in message.body
