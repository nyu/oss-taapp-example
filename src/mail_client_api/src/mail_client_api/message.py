"""Message contract - Core message representation."""

from abc import ABC, abstractmethod


class Message(ABC):
    """Abstract base class representing an email message."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Return the unique identifier of the message."""
        raise NotImplementedError

    @property
    @abstractmethod
    def from_(self) -> str:
        """Return the sender's email address."""
        raise NotImplementedError

    @property
    @abstractmethod
    def to(self) -> str:
        """Return the recipient's email address."""
        raise NotImplementedError

    @property
    @abstractmethod
    def date(self) -> str:
        """Return the date the message was sent."""
        raise NotImplementedError

    @property
    @abstractmethod
    def subject(self) -> str:
        """Return the subject line of the message."""
        raise NotImplementedError

    @property
    @abstractmethod
    def body(self) -> str:
        """Return the plain text content of the message."""
        raise NotImplementedError


def get_message(msg_id: str, raw_data: str) -> Message:
    """Return an instance of a Message.

    Args:
        msg_id (str): The unique identifier for the message.
        raw_data (str): The raw data used to construct the message.

    Returns:
    Message: An instance conforming to the Message contract.

    Raises:
        NotImplementedError: If the function is not overridden by an implementation.

    """
    raise NotImplementedError
