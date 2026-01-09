# Gmail Client Implementation

## Overview
`gmail_client_impl` ships a concrete `mail_client_api.Client` backed by the Gmail API. It handles OAuth2 authentication, makes Gmail API calls, and returns `gmail_client_impl.message_impl.GmailMessage` objects.

## Purpose

This package serves as the production-ready Gmail integration for the email assistant system:

- **Gmail API Integration**: Connects to Gmail using official Google APIs
- **OAuth2 Authentication**: Handles secure authentication with multiple modes (interactive/non-interactive)
- **ABC Implementation**: Provides concrete implementation of all Client operations
- **Message Integration**: Works seamlessly with GmailMessage implementation
- **Dependency Injection**: Automatically registers itself as the Client implementation

## Architecture

### Authentication Modes
- `interactive=True`: Launches the browser OAuth flow and persists `token.json`. Use for local setup.
- `interactive=False`: Reads environment variables or existing tokens. Preferred for CI/CD and production.

Credential priority: environment variables → `token.json` → `credentials.json` (interactive fallback).

### Dependency Injection
```python
import gmail_client_impl  # rebinds the factory

from mail_client_api import get_client
client = get_client(interactive=False)
```

## API Reference

### GmailClient
Implements the `mail_client_api.Client` abstract base class.

#### Methods
- `get_message(message_id: str) -> Message`: Fetches and decodes a single Gmail message.
- `delete_message(message_id: str) -> bool`: Removes the message using the Gmail API.
- `mark_as_read(message_id: str) -> bool`: Clears the `UNREAD` label via `messages().modify`.
- `get_messages(max_results: int = 10) -> Iterator[Message]`: Lists message IDs, hydrates them, and yields lazily.

### Factory Function
`get_client_impl(*, interactive: bool = False) -> mail_client_api.Client`: Creates a `GmailClient` and assigns it to `mail_client_api.get_client` during import.

## Usage Examples

### Basic Retrieval
```python
import gmail_client_impl
from mail_client_api import get_client

client = get_client(interactive=False)
for msg in client.get_messages(max_results=3):
    print(f"{msg.date}: {msg.subject}")
```

### Development Setup
```python
import gmail_client_impl
from mail_client_api import get_client

client = get_client(interactive=True)  # opens browser on first run
print(len(list(client.get_messages(max_results=5))))
```

### Message Management
```python
import gmail_client_impl
from mail_client_api import get_client

client = get_client()

# Process and manage messages
for message in client.get_messages(max_results=50):
    # Mark promotional emails as read
    if "promotion" in message.subject.lower():
        client.mark_as_read(message.id)
        print(f"Marked promotion as read: {message.subject}")
    
    # Delete obvious spam
    if message.from_.endswith("suspicious-domain.com"):
        client.delete_message(message.id)
        print(f"Deleted spam from: {message.from_}")
```

### Error Handling

```python
import gmail_client_impl
from mail_client_api import get_client

try:
    client = get_client(interactive=False)
    
    # Attempt to get a message
    message = client.get_message("potentially_invalid_id")
    print(f"Retrieved: {message.subject}")
    
except Exception as e:
    print(f"Error accessing Gmail: {e}")
    # Handle authentication errors, network issues, etc.
```

## Authentication Setup

### Development Setup (Interactive)

1. **Google Cloud Console Setup**:
   - Create a project and enable Gmail API
   - Create OAuth2 credentials (Desktop application type)
   - Download `credentials.json`

2. **Local Development**:
   ```python
   import gmail_client_impl
   from mail_client_api import get_client
   
   # First run - opens browser for consent
   client = get_client(interactive=True)
   ```

3. **Token Storage**:
   - OAuth2 tokens are saved to `token.json`
   - Subsequent runs use stored tokens
   - Tokens auto-refresh when expired

### Production Setup (Non-Interactive)

1. **Environment Variables**:
   ```bash
   export GMAIL_CLIENT_ID="your_client_id"
   export GMAIL_CLIENT_SECRET="your_client_secret"
   export GMAIL_REFRESH_TOKEN="your_refresh_token"
   ```

2. **Production Usage**:
   ```python
   import gmail_client_impl
   from mail_client_api import get_client
   
   # Uses environment variables
   client = get_client(interactive=False)
   ```

3. **CI/CD Integration**:
   - Set environment variables in CircleCI/GitHub Actions
   - No browser interaction required
   - Tokens refresh automatically

### Credential Sources (Priority Order)

1. **Environment Variables** (highest priority)
   - `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`

2. **Local Token File**
   - `token.json` (created by interactive flow)

3. **Local Credentials File**
   - `credentials.json` (downloaded from Google Cloud Console)

## Testing
```bash
uv run pytest src/gmail_client_impl/tests/ -q
uv run pytest src/gmail_client_impl/tests/ --cov=src/gmail_client_impl --cov-report=term-missing
```

- Unit tests rely on mocks—no real Gmail calls.
- Integration and e2e suites in `tests/` expect credentials or environment variables.

## Gmail API Integration

### Scopes Required

The client requests these Gmail API scopes:

```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read messages
    'https://www.googleapis.com/auth/gmail.modify'     # Mark as read, delete
]
```

### Response Handling

Gmail API responses are processed efficiently:

1. **List Messages**: Gets paginated list of message IDs
2. **Batch Requests**: Fetches multiple message details efficiently
3. **Raw Content**: Retrieves base64url-encoded email data
4. **Message Creation**: Converts to GmailMessage instances through dependency injection