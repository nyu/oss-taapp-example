"""Gmail Message Implementation colocated with the Gmail client."""

import base64
import email
import email.header
import email.utils
from email.message import Message as EmailMessage

import mail_client_api
from mail_client_api import message


class GmailMessage(message.Message):
    """Concrete implementation of the Message abstraction for Gmail messages."""

    MAX_PRINTABLE_ASCII = 126
    BINARY_THRESHOLD_RATIO = 0.5

    TAB_ASCII = 9
    NEWLINE_ASCII = 10
    CARRIAGE_RETURN_ASCII = 13
    SPACE_ASCII = 32

    ERROR_PARSING_MESSAGE = "Error Parsing Message"
    UNKNOWN_SENDER = "Unknown Sender"
    UNKNOWN_RECIPIENT = "Unknown Recipient"
    UNKNOWN_DATE = "Unknown Date"

    DATE_FORMAT = "%m/%d/%Y"

    RFC2047_ENCODING_MARKER = "=?"
    DEFAULT_CHARSET = "utf-8"
    TEXT_PLAIN_CONTENT_TYPE = "text/plain"
    CONTENT_DISPOSITION_HEADER = "Content-Disposition"
    ATTACHMENT_DISPOSITION = "attachment"

    NON_BYTES_PAYLOAD_TEXT_PART = "[Non-bytes payload found in text/plain part]"
    COULD_NOT_DECODE_BODY_PART = "[Could not decode body part]"
    NO_PLAIN_TEXT_BODY = "[No plain text body found]"
    NON_BYTES_PAYLOAD = "[Non-bytes payload found]"
    COULD_NOT_DECODE_BODY = "[Could not decode body]"

    EMAIL_BODY_LINE_STARTS = ("\r\n", "\n")

    def __init__(self, msg_id: str, raw_data: str) -> None:
        """Decode the Gmail payload and hydrate message metadata."""
        self._id = msg_id
        self._raw_data = raw_data
        try:
            decoded_bytes = base64.urlsafe_b64decode(raw_data.encode("utf-8"))
            self._parsed: EmailMessage = email.message_from_bytes(decoded_bytes)

            payload = self._parsed.get_payload()
            if (
                not decoded_bytes
                or (
                    not any(self._parsed.keys())
                    and (
                        not payload
                        or (
                            isinstance(payload, str)
                            and not payload.startswith(self.EMAIL_BODY_LINE_STARTS)
                        )
                    )
                )
                or self._is_binary_garbage(decoded_bytes)
            ):
                self._parsed = EmailMessage()
                self._parsed["Subject"] = self.ERROR_PARSING_MESSAGE
                self._parsed["From"] = self.UNKNOWN_SENDER
                self._parsed["To"] = self.UNKNOWN_RECIPIENT
                self._parsed["Date"] = self.UNKNOWN_DATE

        except (TypeError, ValueError):
            self._parsed = EmailMessage()
            self._parsed["Subject"] = self.ERROR_PARSING_MESSAGE
            self._parsed["From"] = self.UNKNOWN_SENDER
            self._parsed["To"] = self.UNKNOWN_RECIPIENT
            self._parsed["Date"] = self.UNKNOWN_DATE

    # Fancy chatgpt made me do this:
    def _is_binary_garbage(self, data: bytes) -> bool:
        if not data:
            return False

        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            pass
        else:
            return False

        non_printable_count = 0
        for byte_val in data:
            if (
                byte_val < self.SPACE_ASCII
                and byte_val
                not in (
                    self.TAB_ASCII,
                    self.NEWLINE_ASCII,
                    self.CARRIAGE_RETURN_ASCII,
                )
            ) or byte_val > self.MAX_PRINTABLE_ASCII:
                non_printable_count += 1

        return (non_printable_count / len(data)) > self.BINARY_THRESHOLD_RATIO

    @property
    def id(self) -> str:
        """Get the unique message identifier."""
        return self._id

    @property
    def from_(self) -> str:
        """Get the email sender."""
        return self._parsed.get("From", "")

    @property
    def to(self) -> str:
        """Get the email recipient(s)."""
        return self._parsed.get("To", "")

    @property
    def date(self) -> str:
        """Get the email date, formatted as MM/DD/YYYY if possible."""
        raw_date = self._parsed.get("Date", "")
        if not raw_date:
            return self.UNKNOWN_DATE
        try:
            parsed_dt = email.utils.parsedate_to_datetime(raw_date)
            return parsed_dt.strftime(self.DATE_FORMAT)
        except (TypeError, ValueError):
            return raw_date

    @property
    def subject(self) -> str:
        """Get the email subject, decoding RFC 2047 if necessary."""
        subject_header = self._parsed.get("Subject", "")
        if not subject_header:
            return ""

        if hasattr(subject_header, "__str__"):
            subject_header = str(subject_header)

        try:
            if self.RFC2047_ENCODING_MARKER not in subject_header:
                return subject_header

            decoded_parts = email.header.decode_header(subject_header)
            subject_str = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    subject_str += part.decode(encoding or self.DEFAULT_CHARSET, errors="replace")
                else:
                    subject_str += part

            return subject_str if subject_str else subject_header  # noqa: TRY300
        except (UnicodeDecodeError, LookupError, ValueError, AttributeError):
            return subject_header

    @property
    def body(self) -> str:
        """Get the email body."""
        body_content = ""
        if self._parsed.is_multipart():
            for part in self._parsed.walk():
                content_type = part.get_content_type()
                content_disposition = part.get(self.CONTENT_DISPOSITION_HEADER, "")

                if (
                    content_type == self.TEXT_PLAIN_CONTENT_TYPE
                    and self.ATTACHMENT_DISPOSITION not in content_disposition
                ):
                    try:
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            charset = part.get_content_charset() or self.DEFAULT_CHARSET
                            body_content = payload.decode(charset, errors="replace")
                            break
                        body_content = self.NON_BYTES_PAYLOAD_TEXT_PART
                        break
                    except (UnicodeDecodeError, LookupError, AttributeError, TypeError):
                        body_content = self.COULD_NOT_DECODE_BODY_PART
                        break
            else:
                body_content = self.NO_PLAIN_TEXT_BODY
        else:
            try:
                payload = self._parsed.get_payload(decode=True)
                if isinstance(payload, bytes):
                    charset = self._parsed.get_content_charset() or self.DEFAULT_CHARSET
                    body_content = payload.decode(charset, errors="replace")
                else:
                    body_content = self.NON_BYTES_PAYLOAD
            except (UnicodeDecodeError, LookupError, AttributeError):
                body_content = self.COULD_NOT_DECODE_BODY

        return body_content


def get_message_impl(msg_id: str, raw_data: str) -> message.Message:
    """Return an instance of the concrete GmailMessage implementation."""
    return GmailMessage(msg_id=msg_id, raw_data=raw_data)


def register() -> None:
    """Register the Gmail message implementation with the message abstraction."""
    message.get_message = get_message_impl
    mail_client_api.get_message = get_message_impl
