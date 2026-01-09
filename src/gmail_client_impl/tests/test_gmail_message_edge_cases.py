"""Edge case tests for the colocated GmailMessage implementation."""

import base64

from gmail_client_impl.message_impl import GmailMessage


class TestEdgeCases:
    """Test cases for edge cases and error conditions."""

    VERY_LONG_SUBJECT_MIN_LENGTH = 1000
    VERY_LONG_BODY_MIN_LENGTH = 30000

    def test_extremely_large_message_id(self) -> None:
        """Test handling of extremely large message IDs."""
        long_id = "x" * 1000
        simple_email = "Subject: Long ID Test\r\n\r\nBody"
        encoded_data = base64.urlsafe_b64encode(simple_email.encode()).decode()

        msg = GmailMessage(msg_id=long_id, raw_data=encoded_data)
        assert msg.id == long_id
        assert msg.subject == "Long ID Test"

    def test_unicode_in_message_content(self) -> None:
        """Test handling of Unicode characters in subject and body."""
        email_content = (
            "From: unicode@example.com\r\n"
            "Subject: 🎉 Unicode Test 测试 🌟\r\n"
            "\r\n"
            "Unicode body: こんにちは 世界! 🌍 Café naïve résumé"
        )

        encoded_data = base64.urlsafe_b64encode(email_content.encode("utf-8")).decode()
        msg = GmailMessage(msg_id="unicode123", raw_data=encoded_data)

        assert "Unicode Test" in str(msg.subject)
        assert "こんにちは 世界! 🌍" in msg.body
        assert "Café naïve résumé" in msg.body

    def test_very_long_subject_line(self) -> None:
        """Test handling of very long subject lines."""
        long_subject = "Very Long Subject " * 100
        email_content = f"Subject: {long_subject}\r\n\r\nShort body"

        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        msg = GmailMessage(msg_id="longsubj123", raw_data=encoded_data)

        assert msg.subject == long_subject
        assert len(msg.subject) > self.VERY_LONG_SUBJECT_MIN_LENGTH

    def test_very_long_message_body(self) -> None:
        """Test handling of very long message bodies."""
        long_body = "This is a very long message body. " * 1000
        email_content = f"Subject: Long Body Test\r\n\r\n{long_body}"

        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        msg = GmailMessage(msg_id="longbody123", raw_data=encoded_data)

        assert msg.subject == "Long Body Test"
        assert len(msg.body) > self.VERY_LONG_BODY_MIN_LENGTH
        assert "This is a very long message body." in msg.body

    def test_malformed_headers(self) -> None:
        """Test handling of messages with malformed headers."""
        malformed_email = (
            "From sender@example.com\r\n"
            "Subject: Malformed Headers\r\n"
            "Invalid-Header-Without-Value\r\n"
            "\r\n"
            "Body content"
        )

        encoded_data = base64.urlsafe_b64encode(malformed_email.encode()).decode()
        msg = GmailMessage(msg_id="malformed123", raw_data=encoded_data)

        assert msg.id == "malformed123"
        assert msg.body == "Invalid-Header-Without-Value\r\n\r\nBody content"

    def test_binary_data_in_raw_input(self) -> None:
        """Test handling of raw data that includes binary content."""
        binary_data = bytes(range(256))
        encoded_data = base64.urlsafe_b64encode(binary_data).decode()

        msg = GmailMessage(msg_id="binary123", raw_data=encoded_data)
        assert msg.id == "binary123"
        assert msg.subject == "Error Parsing Message"

    def test_empty_raw_data(self) -> None:
        """Test handling of completely empty raw data."""
        msg = GmailMessage(msg_id="empty123", raw_data="")

        assert msg.id == "empty123"
        assert msg.subject == "Error Parsing Message"
        assert msg.from_ == "Unknown Sender"

    def test_whitespace_only_raw_data(self) -> None:
        """Test raw data that is only whitespace characters."""
        whitespace_data = base64.urlsafe_b64encode(b"   \r\n\t  ").decode()
        msg = GmailMessage(msg_id="whitespace123", raw_data=whitespace_data)

        assert msg.id == "whitespace123"
        assert isinstance(msg.subject, str)
        assert isinstance(msg.body, str)

    def test_non_ascii_message_id(self) -> None:
        """Test non-ASCII characters in message ID."""
        unicode_id = "msg_测试_🎉_123"
        simple_email = "Subject: Unicode ID Test\r\n\r\nBody"
        encoded_data = base64.urlsafe_b64encode(simple_email.encode()).decode()

        msg = GmailMessage(msg_id=unicode_id, raw_data=encoded_data)
        assert msg.id == unicode_id
        assert msg.subject == "Unicode ID Test"

    def test_deeply_nested_multipart_message(self) -> None:
        """Test deeply nested multipart messages."""
        nested_email = (
            "Content-Type: multipart/mixed; boundary=outer\r\n"
            "Subject: Nested Test\r\n"
            "\r\n"
            "--outer\r\n"
            "Content-Type: multipart/alternative; boundary=inner\r\n"
            "\r\n"
            "--inner\r\n"
            "Content-Type: text/plain\r\n"
            "\r\n"
            "Plain text in nested structure\r\n"
            "--inner\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
            "<html><body>HTML content</body></html>\r\n"
            "--inner--\r\n"
            "--outer\r\n"
            "Content-Type: application/octet-stream\r\n"
            "\r\n"
            "Binary attachment data\r\n"
            "--outer--\r\n"
        )

        encoded_data = base64.urlsafe_b64encode(nested_email.encode()).decode()
        msg = GmailMessage(msg_id="nested123", raw_data=encoded_data)

        assert msg.id == "nested123"
        assert msg.subject == "Nested Test"
        assert "Plain text in nested structure" in msg.body

    def test_message_with_null_bytes(self) -> None:
        """Test message containing null bytes in headers and body."""
        email_with_nulls = (
            "From: null@example.com\r\nSubject: Null Test\r\n\r\nBody with\x00null\x00bytes"
        )

        encoded_data = base64.urlsafe_b64encode(
            email_with_nulls.encode("utf-8", errors="replace"),
        ).decode()
        msg = GmailMessage(msg_id="null123", raw_data=encoded_data)

        assert msg.id == "null123"
        assert msg.from_ == "null@example.com"
        assert "Body with" in msg.body

    def test_repeated_property_access(self) -> None:
        """Test that accessing properties multiple times yields consistent results."""
        email_content = "From: repeat@example.com\r\nSubject: Repeat Test\r\nDate: Wed, 30 Jul 2025 10:30:00 +0000\r\n\r\nConsistent body"

        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        msg = GmailMessage(msg_id="repeat123", raw_data=encoded_data)

        for _ in range(5):
            assert msg.id == "repeat123"
            assert msg.from_ == "repeat@example.com"
            assert msg.subject == "Repeat Test"
            assert msg.date == "07/30/2025"
            assert msg.body == "Consistent body"

    def test_message_with_only_headers_no_body(self) -> None:
        """Test message that contains only headers and no body."""
        headers_only = "From: headeronly@example.com\r\nSubject: Headers Only\r\nDate: Wed, 30 Jul 2025 10:30:00 +0000\r\n\r\n"

        encoded_data = base64.urlsafe_b64encode(headers_only.encode()).decode()
        msg = GmailMessage(msg_id="headers123", raw_data=encoded_data)

        assert msg.id == "headers123"
        assert msg.from_ == "headeronly@example.com"
        assert msg.subject == "Headers Only"
        assert msg.date == "07/30/2025"
        assert msg.body == ""
