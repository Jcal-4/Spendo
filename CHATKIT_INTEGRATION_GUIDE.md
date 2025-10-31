# ChatKit SDK Integration Guide

This document provides a complete guide for integrating OpenAI's ChatKit SDK into the Spendo application, including all backend and frontend modifications required.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Configuration Details](#configuration-details)
6. [Troubleshooting](#troubleshooting)
7. [Code Reusability Guide](#code-reusability-guide)
8. [Summary of Files Created/Modified](#summary-of-files-createdmodified)
9. [Next Steps](#next-steps)
10. [Additional Resources](#additional-resources)

---

## Overview

The ChatKit SDK enables a custom backend integration where all chat requests are handled by your Django server. This guide provides step-by-step instructions for:

- Installing required packages (backend and frontend)
- Creating a memory store for thread persistence
- Implementing the ChatKit server with your AI workflow
- Setting up Django endpoints and routing
- Configuring CORS for ChatKit-specific headers
- Integrating the React ChatKit component
- Troubleshooting common issues
- Understanding code reusability across projects

**Expected Time:** 30-60 minutes for complete setup (depending on familiarity with Django and React)

---

## Prerequisites

- Django backend running
- React frontend with Vite
- OpenAI API key with ChatKit access
- Domain verification key from OpenAI (for production)

---

## Backend Setup

### Step 1: Install Required Python Packages

Add the following packages to `server/Spendo/requirements.txt`:

```txt
Django>=4.0
djangorestframework
gunicorn
psycopg2-binary
dj-database-url
python-dotenv
django-cors-headers
whitenoise
openai>=1.40
requests
openai-chatkit>=1.0.2,<2
```

**Install the packages:**

```bash
pip install openai-chatkit>=1.0.2,<2
```

**Note:** If you're using a virtual environment (recommended), activate it first:

```bash
# Activate virtual environment (if using one)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Then install
pip install openai-chatkit>=1.0.2,<2
```

### Step 2: Create Memory Store (`memory_store.py`)

Create a new file `server/Spendo/api/memory_store.py` to handle thread and message persistence:

```python
"""Memory store for ChatKit thread and message persistence."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from chatkit.types import ThreadItem, ThreadMetadata


def _gen_id(prefix: str) -> str:
    """Generate a unique ID with a prefix."""
    return f"{prefix}_{uuid4().hex[:8]}"


class SimpleMemoryStore:
    """Simple in-memory thread storage for ChatKit."""

    def __init__(self):
        self._threads: dict[str, ThreadMetadata] = {}
        self._items: dict[str, list[ThreadItem]] = {}

    def generate_thread_id(self, context: dict[str, Any] | None = None) -> str:
        """Generate a unique thread ID."""
        return _gen_id("thread")

    def generate_item_id(self, item_type: str, thread: Any, context: dict[str, Any] | None = None) -> str:
        """Generate a unique item ID (for messages, etc.)."""
        return _gen_id("msg")

    async def load_thread(
        self, thread_id: str, context: dict[str, Any]
    ) -> ThreadMetadata | None:
        return self._threads.get(thread_id)

    async def load_threads(
        self,
        limit: int | None = None,
        after: str | None = None,
        order: str = "desc",
        context: dict[str, Any] | None = None,
    ) -> Any:
        """Load multiple threads with optional pagination and ordering."""
        threads = list(self._threads.values())

        # Sort threads by created_at if available, otherwise by ID
        try:
            threads.sort(key=lambda t: getattr(t, 'created_at', t.id), reverse=(order == "desc"))
        except (AttributeError, TypeError):
            # If sorting fails, just use the current order
            pass

        if after:
            # Filter threads after the specified thread ID
            try:
                idx = next(i for i, thread in enumerate(threads) if thread.id == after)
                threads = threads[idx + 1:]
            except (StopIteration, ValueError):
                threads = []

        # Check if there are more items before limiting
        total_available = len(threads)
        has_more = False
        if limit and total_available > limit:
            threads = threads[:limit]
            has_more = True
        elif limit is None:
            # No limit specified, so no more items available
            has_more = False

        # Set 'after' to the ID of the last item if there are more items
        after_id = None
        if has_more and threads:
            after_id = threads[-1].id

        class Result:
            def __init__(self, data, has_more_flag, after_value=None):
                self.data = data
                self.has_more = has_more_flag
                self.after = after_value

        return Result(threads, has_more, after_id)

    async def save_thread(
        self, thread: ThreadMetadata, context: dict[str, Any]
    ) -> None:
        self._threads[thread.id] = thread

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None = None,
        limit: int = 50,
        order: str = "desc",
        context: dict[str, Any] | None = None,
    ) -> Any:
        items = self._items.get(thread_id, [])
        if after:
            # Simple implementation - find index of item after the 'after' ID
            try:
                idx = next(i for i, item in enumerate(items) if getattr(item, "id", None) == after)
                items = items[idx + 1:]
            except StopIteration:
                items = []

        # Check if there are more items before limiting
        total_available = len(items)
        has_more = False
        if limit and total_available > limit:
            items = items[:limit]
            has_more = True

        if order == "desc":
            items = list(reversed(items))

        # Set 'after' to the ID of the last item if there are more items
        after_id = None
        if has_more and items:
            after_id = getattr(items[-1], "id", None)

        class Result:
            def __init__(self, data, has_more_flag, after_value=None):
                self.data = data
                self.has_more = has_more_flag
                self.after = after_value

        return Result(items, has_more, after_id)

    async def add_thread_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict[str, Any],
    ) -> None:
        if thread_id not in self._items:
            self._items[thread_id] = []
        self._items[thread_id].append(item)
```

**Key Points:**

- `SimpleMemoryStore` implements the storage interface required by ChatKit
- Methods handle pagination with `limit`, `after`, and `order` parameters
- Result objects must have `data`, `has_more`, and `after` attributes
- Thread IDs are generated with `"thread"` prefix, message IDs with `"msg"` prefix

### Step 3: Create ChatKit Server (`chatkit_server.py`)

Create or update `server/Spendo/api/chatkit_server.py`:

```python
"""ChatKit server integration for Spendo backend."""

from __future__ import annotations

from datetime import datetime
from typing import Any, AsyncIterator

from chatkit.server import ChatKitServer
from chatkit.types import (
    AssistantMessageItem,
    ThreadItem,
    ThreadItemDoneEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
)

from .memory_store import SimpleMemoryStore, _gen_id
from .services.OpenAI_service import run_workflow, WorkflowInput


def _user_message_text(item: UserMessageItem) -> str:
    """Extract text content from a UserMessageItem."""
    parts: list[str] = []
    for part in item.content:
        text = getattr(part, "text", None)
        if text:
            parts.append(text)
    return " ".join(parts).strip()


class SpendoChatKitServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server wired up with the Spendo financial reasoning workflow."""

    def __init__(self) -> None:
        self.store = SimpleMemoryStore()
        super().__init__(self.store)

    async def respond(
        self,
        thread: ThreadMetadata,
        input: ThreadItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Handle user messages and generate assistant responses using the existing workflow."""
        if input is None:
            return

        if not isinstance(input, UserMessageItem):
            return

        # Extract user message text
        user_text = _user_message_text(input)
        if not user_text:
            return

        # Call the existing run_workflow function
        try:
            workflow_input = WorkflowInput(input_as_text=user_text)
            result = await run_workflow(workflow_input)

            # Extract the response text
            response_text = result.get("tentativeresponseee", "I'm sorry, I couldn't generate a response.")

            # Create assistant message item
            assistant_item = AssistantMessageItem(
                id=_gen_id("msg"),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=[
                    {
                        "type": "output_text",
                        "text": response_text,
                    }
                ],
            )

            # Stream the response
            yield ThreadItemDoneEvent(item=assistant_item)

            # Save the assistant message to thread history
            await self.store.add_thread_item(thread.id, assistant_item, context)

        except Exception as e:
            # Handle errors gracefully
            error_text = f"I encountered an error: {str(e)}"
            error_item = AssistantMessageItem(
                id=_gen_id("msg"),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=[
                    {
                        "type": "output_text",
                        "text": error_text,
                    }
                ],
            )
            yield ThreadItemDoneEvent(item=error_item)
            await self.store.add_thread_item(thread.id, error_item, context)

    async def to_message_content(self, _input: Any) -> Any:
        """Handle file attachments if needed."""
        raise NotImplementedError("File attachments are not yet supported.")


# Singleton instance
_chatkit_server: SpendoChatKitServer | None = None


def get_chatkit_server() -> SpendoChatKitServer:
    """Get or create the ChatKit server instance."""
    global _chatkit_server
    if _chatkit_server is None:
        _chatkit_server = SpendoChatKitServer()
    return _chatkit_server
```

**Key Points:**

- `SpendoChatKitServer` extends `ChatKitServer` and uses `SimpleMemoryStore`
- The `respond` method processes user messages and streams responses
- Integrates with your existing `run_workflow` function
- Uses singleton pattern to maintain server instance

### Step 4: Add ChatKit Endpoint (`views.py`)

Add the following to `server/Spendo/api/views.py`:

**At the top of the file, add imports:**

```python
from .chatkit_server import get_chatkit_server
from chatkit.server import StreamingResult
```

**Note:** Ensure these imports are added alongside your existing imports. If `StreamingHttpResponse` is not already imported, you may need to add:

```python
from django.http import StreamingHttpResponse
```

**Add the endpoint function:**

```python
@csrf_exempt
async def chatkit_endpoint(request):
    """ChatKit SDK endpoint for handling chat requests."""
    # Allow both GET (for health checks) and POST (for chat requests)
    if request.method not in ["GET", "POST"]:
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Handle GET requests (health check)
    if request.method == "GET":
        return JsonResponse({"status": "ok"})

    try:
        server = get_chatkit_server()
        payload = request.body

        if not payload:
            return JsonResponse({"error": "Empty payload"}, status=400)

        result = await server.process(payload, {"request": request})

        if isinstance(result, StreamingResult):
            # Return streaming response
            response = StreamingHttpResponse(
                result,
                content_type="text/event-stream"
            )
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response

        if hasattr(result, "json"):
            return JsonResponse(json.loads(result.json), safe=False)

        return JsonResponse(result, safe=False)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ChatKit endpoint error: {e}")
        print(f"Traceback: {error_details}")
        return JsonResponse(
            {"error": str(e), "details": error_details},
            status=500,
            safe=False
        )
```

**Important Notes:**

- `request.body` is a property, not a method - use `request.body` not `request.body()` or `await request.body()`
- The endpoint handles both streaming and non-streaming responses
- GET requests return a health check status
- The endpoint is decorated with `@csrf_exempt` since ChatKit handles authentication through its own headers

### Step 5: Add URL Route (`urls.py`)

In `server/Spendo/api/urls.py`, add the import and route:

**Add to imports:**

```python
from .views import create_chatkit_session, get_user_accounts, get_customusers, get_customuser_by_username, create_customuser, FrontendAppView, UserMeView, LoginView, LogoutView, chatkit_endpoint
```

**Add to urlpatterns:**

```python
urlpatterns = [
    # ... existing patterns ...
    path('chatkit/session/', create_chatkit_session, name='create_chatkit_session'),
    # ChatKit SDK endpoint for custom backend
    path('chatkit/', chatkit_endpoint, name='chatkit_endpoint'),
]
```

### Step 6: Configure CORS (`settings.py`)

In `server/Spendo/Spendo/settings.py`, add ChatKit-specific CORS headers:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://spendo-386e7e9da44d.herokuapp.com"
]

CORS_ALLOW_CREDENTIALS = True

# Allow ChatKit-specific headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    # ChatKit-specific headers
    'chatkit-frame-instance-id',
    'chatkit-session-id',
    'chatkit-user-id',
]
```

**Critical:** Without these headers, you'll get CORS errors when ChatKit tries to send requests with its custom headers. The error will typically be: `Request header field chatkit-frame-instance-id is not allowed by Access-Control-Allow-Headers in preflight response.`

**After making changes to `settings.py`, restart your Django server for the changes to take effect.**

---

## Frontend Setup

### Step 1: Install React Package

Add the ChatKit React package to `client/app/package.json`:

```json
{
  "dependencies": {
    "@openai/chatkit-react": "^1.1.1"
    // ... other dependencies
  }
}
```

**Install the package:**

```bash
cd client/app
npm install @openai/chatkit-react
```

### Step 2: Update HTML (`index.html`)

Add the ChatKit script and domain verification meta tag to `client/app/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <!-- OpenAI ChatKit domain verification -->
    <meta name="openai-domain-verify" content="your_domain_verification_key" />
    <script src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" async></script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Spendo</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**Important:** Replace `your_domain_verification_key` with your actual domain verification key from OpenAI.

### Step 3: Configure ChatKit Component (`MyChat.tsx`)

Update `client/app/src/components/chatbot/MyChat.tsx`:

```tsx
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useState } from 'react';
import styles from './Chatbot.module.css';

const apiUrl = import.meta.env.VITE_API_URL;

export function MyChat() {
  const [open, setOpen] = useState(false);

  const { control } = useChatKit({
    api: {
      url: `${apiUrl}/chatkit/`,
      domainKey: 'domain_pk_localhost_dev',
    },
    theme: {
      colorScheme: 'dark',
      radius: 'round',
      density: 'compact',
      typography: {
        baseSize: 16,
        fontFamily:
          '"OpenAI Sans", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif',
        fontFamilyMono:
          'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace',
        fontSources: [
          {
            family: 'OpenAI Sans',
            src: 'https://cdn.openai.com/common/fonts/openai-sans/v2/OpenAISans-Regular.woff2',
            weight: 400,
            style: 'normal',
            display: 'swap',
          },
        ],
      },
    },
    header: {
      rightAction: {
        icon: 'close',
        onClick: () => setOpen(false),
      },
    },
  });

  return (
    <div className={styles.openAIchatbotContainer}>
      {!open && (
        <button className={styles.fab} onClick={() => setOpen(true)} aria-label="Open chatbot">
          <img
            src="https://img.icons8.com/?size=100&id=kTuxVYRKeKEY&format=png&color=000000"
            alt="chatgpt"
            style={{ width: 40, height: 40 }}
          />
        </button>
      )}
      {open && (
        <div>
          <ChatKit control={control} className="min-h-[700px] w-[450px] " />
        </div>
      )}
    </div>
  );
}

export default MyChat;
```

**Key Configuration Points:**

- `api.url`: Points to your Django backend's ChatKit endpoint (`${apiUrl}/chatkit/`)
- `api.domainKey`: Your ChatKit domain key (use `domain_pk_localhost_dev` for local development)
- `theme`: Customizable appearance settings
- The component uses a floating action button (FAB) pattern for toggling visibility

**Note:** The simple `url` configuration approach is used here. If you need to send CSRF tokens, you would use the `getClientSecret` approach instead (see troubleshooting section).

### Step 4: Environment Variables

Ensure `client/app/.env` or environment configuration includes:

```env
VITE_API_URL=http://localhost:8000/api
```

For production, update to your production backend URL.

**Note:** Make sure the backend URL matches your Django server's base URL. The ChatKit endpoint will be accessed at `${VITE_API_URL}/chatkit/`.

---

## Configuration Details

### Domain Key Configuration

- **Development:** Use `domain_pk_localhost_dev` for local development
- **Production:** Replace with your actual production domain key from OpenAI

### API Endpoint Structure

The ChatKit SDK expects:

- **URL:** `${apiUrl}/chatkit/`
- **Methods:** GET (health check) and POST (chat requests)
- **Content-Type:** `application/json` or `text/event-stream` for streaming

### Memory Store Considerations

The current `SimpleMemoryStore` is an in-memory implementation:

- Threads and messages are stored in Python dictionaries
- Data is lost on server restart
- For production, consider implementing database-backed storage

**Important:** For production environments, you should implement persistent storage. See the [Code Reusability Guide](#code-reusability-guide) section for examples of how to create a database-backed memory store while maintaining the same interface.

To implement persistent storage:

1. Replace dictionary storage with database queries
2. Keep the same method signatures
3. Ensure pagination (`has_more`, `after`) works correctly
4. Consider thread archiving and cleanup strategies

---

## Troubleshooting

### Error: CORS Policy Blocking Requests

**Symptom:** `Request header field chatkit-frame-instance-id is not allowed`

**Solution:** Ensure `CORS_ALLOW_HEADERS` in `settings.py` includes all ChatKit headers:

```python
CORS_ALLOW_HEADERS = [
    # ... standard headers ...
    'chatkit-frame-instance-id',
    'chatkit-session-id',
    'chatkit-user-id',
]
```

### Error: 'bytes' object is not callable

**Symptom:** `TypeError: 'bytes' object is not callable` at `request.body()`

**Solution:** In `chatkit_endpoint`, use `request.body` (property) not `request.body()` (method):

```python
payload = request.body  # Correct
# NOT: payload = await request.body()  # Incorrect
```

### Error: AttributeError - Missing Methods

**Symptom:** `'SimpleMemoryStore' object has no attribute 'generate_thread_id'`

**Solution:** Ensure `SimpleMemoryStore` implements all required methods:

- `generate_thread_id()`
- `generate_item_id()`
- `load_thread()`
- `load_threads()` (with `has_more` and `after` in Result)
- `save_thread()`
- `load_thread_items()` (with `has_more` and `after` in Result)
- `add_thread_item()`

### Error: Result object missing attributes

**Symptom:** `'Result' object has no attribute 'has_more'`

**Solution:** Ensure Result objects have all three attributes:

```python
class Result:
    def __init__(self, data, has_more_flag, after_value=None):
        self.data = data
        self.has_more = has_more_flag
        self.after = after_value
```

### Error: generate_thread_id/generate_item_id is async

**Symptom:** `TypeError: 'bytes' object is not callable` or `ValidationError: Input should be a valid string [type=string_type, input_value=<coroutine object>]`

**Solution:** `generate_thread_id` and `generate_item_id` must be **synchronous** methods (not async):

```python
def generate_thread_id(self, context: dict[str, Any] | None = None) -> str:
    """Generate a unique thread ID."""
    return _gen_id("thread")
    # NOT: async def generate_thread_id(...)
```

**Also ensure `generate_item_id` is synchronous:**

```python
def generate_item_id(self, item_type: str, thread: Any, context: dict[str, Any] | None = None) -> str:
    """Generate a unique item ID."""
    return _gen_id("msg")
```

### Error: 500 Internal Server Error

**Common Causes:**

1. Missing required methods in `SimpleMemoryStore`
2. Incorrect Result object structure
3. Async/sync method mismatches
4. Missing imports in `views.py`

**Debug Steps:**

1. Check Django server logs for detailed error messages
2. Verify all imports are correct
3. Ensure `chatkit_endpoint` is properly decorated with `@csrf_exempt`
4. Confirm `get_chatkit_server()` is imported in `views.py`

### Frontend: ChatKit Not Loading

**Check:**

1. `index.html` includes the ChatKit script tag
2. Domain verification meta tag has correct key
3. `VITE_API_URL` environment variable is set
4. Backend endpoint is accessible from frontend origin

---

## Code Reusability Guide

This section explains which parts of the ChatKit implementation are reusable across projects and which need customization.

### `memory_store.py` - Highly Reusable ✅

The `SimpleMemoryStore` class implements the standard ChatKit storage interface and can be used as-is in most projects.

**What's Reusable:**

- All method signatures
- Pagination logic (`has_more`, `after` attributes)
- Thread and item ID generation
- Basic in-memory storage structure

**What You Might Want to Customize:**

#### Option 1: Keep In-Memory (Quick Start)

Use it as-is for development and simple projects.

#### Option 2: Database-Backed Storage (Production)

Replace dictionary storage with database queries while keeping the same interface:

```python
class DatabaseMemoryStore:
    """Database-backed thread storage for ChatKit."""

    def __init__(self):
        # Initialize database connection
        pass

    async def load_thread(self, thread_id: str, context: dict[str, Any]) -> ThreadMetadata | None:
        # Query database instead of self._threads.get(thread_id)
        return await db.get_thread(thread_id)

    async def save_thread(self, thread: ThreadMetadata, context: dict[str, Any]) -> None:
        # Save to database instead of self._threads[thread.id] = thread
        await db.save_thread(thread)

    # ... other methods with database queries instead of dictionary lookups
```

**The key:** Keep the same method signatures and return types - only change the implementation.

### `chatkit_server.py` - Partially Reusable ⚠️

The class structure is reusable, but the `respond` method needs customization for each project's specific workflow.

**What's Always Reusable:**

1. Class structure extending `ChatKitServer[dict[str, Any]]`
2. Store initialization: `self.store = SimpleMemoryStore()`
3. Message extraction: `_user_message_text()` function
4. Response streaming: The `ThreadItemDoneEvent` yield pattern
5. Error handling: Basic try/except structure
6. Singleton pattern: `get_chatkit_server()` function

**What Always Needs Customization:**

1. **AI/LLM Integration**: How you generate responses
2. **Response Format**: How you extract response text from your AI service
3. **Business Logic**: Any custom processing before/after AI calls
4. **Context Usage**: How you use the `context` parameter

#### Reusable Template Structure:

```python
"""ChatKit server integration template - Customize for your project."""

from __future__ import annotations
from datetime import datetime
from typing import Any, AsyncIterator

from chatkit.server import ChatKitServer
from chatkit.types import (
    AssistantMessageItem,
    ThreadItem,
    ThreadItemDoneEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
)

from .memory_store import SimpleMemoryStore, _gen_id


def _user_message_text(item: UserMessageItem) -> str:
    """Extract text content from a UserMessageItem."""
    parts: list[str] = []
    for part in item.content:
        text = getattr(part, "text", None)
        if text:
            parts.append(text)
    return " ".join(parts).strip()


class YourProjectChatKitServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server for YOUR PROJECT - Customize the respond method."""

    def __init__(self) -> None:
        self.store = SimpleMemoryStore()  # Or DatabaseMemoryStore
        super().__init__(self.store)

    async def respond(
        self,
        thread: ThreadMetadata,
        input: ThreadItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        CUSTOMIZE THIS METHOD for your project's specific workflow.

        This is where you integrate with:
        - Your LLM/AI service
        - Your business logic
        - Your response format
        """
        if input is None:
            return

        if not isinstance(input, UserMessageItem):
            return

        # Extract user message text (reusable)
        user_text = _user_message_text(input)
        if not user_text:
            return

        # ========================================
        # CUSTOMIZE THIS SECTION FOR YOUR PROJECT
        # ========================================

        try:
            # Option 1: Direct LLM call
            # response_text = await your_llm_service.generate(user_text)

            # Option 2: Custom workflow (like Spendo)
            # workflow_input = YourWorkflowInput(input_as_text=user_text)
            # result = await your_workflow_function(workflow_input)
            # response_text = result.get("your_response_key", "Default message")

            # Option 3: OpenAI API directly
            # from openai import AsyncOpenAI
            # client = AsyncOpenAI()
            # response = await client.chat.completions.create(...)
            # response_text = response.choices[0].message.content

            # For this example, using a placeholder:
            response_text = "Your AI response here"

        except Exception as e:
            # Error handling (customize message format if needed)
            response_text = f"I encountered an error: {str(e)}"

        # ========================================
        # END CUSTOMIZATION SECTION
        # ========================================

        # Create and stream assistant response (mostly reusable)
        assistant_item = AssistantMessageItem(
            id=_gen_id("msg"),
            thread_id=thread.id,
            created_at=datetime.now(),
            content=[
                {
                    "type": "output_text",
                    "text": response_text,
                }
            ],
        )

        yield ThreadItemDoneEvent(item=assistant_item)
        await self.store.add_thread_item(thread.id, assistant_item, context)

    async def to_message_content(self, _input: Any) -> Any:
        """Handle file attachments - customize if needed."""
        raise NotImplementedError("File attachments are not yet supported.")


# Singleton pattern (reusable)
_chatkit_server: YourProjectChatKitServer | None = None


def get_chatkit_server() -> YourProjectChatKitServer:
    """Get or create the ChatKit server instance."""
    global _chatkit_server
    if _chatkit_server is None:
        _chatkit_server = YourProjectChatKitServer()
    return _chatkit_server
```

#### Customization Examples:

**Example 1: Simple OpenAI Chat Completion**

```python
async def respond(...):
    # ... extract user_text ...

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_text}
        ]
    )

    response_text = response.choices[0].message.content

    # ... create and yield assistant_item ...
```

**Example 2: Custom Agent/Workflow (like Spendo)**

```python
async def respond(...):
    # ... extract user_text ...

    from .services.your_service import run_your_workflow, YourInputType

    workflow_input = YourInputType(input_text=user_text)
    result = await run_your_workflow(workflow_input)
    response_text = result.get("response_field", "Default message")

    # ... create and yield assistant_item ...
```

**Example 3: Multiple AI Services**

```python
async def respond(...):
    # ... extract user_text ...

    # Choose AI service based on context
    if context.get("use_anthropic"):
        response_text = await anthropic_client.generate(user_text)
    elif context.get("use_openai"):
        response_text = await openai_client.generate(user_text)
    else:
        response_text = await default_ai_service.generate(user_text)

    # ... create and yield assistant_item ...
```

### Reusability Summary

| Component                              | Reusability | Customization Needed              |
| -------------------------------------- | ----------- | --------------------------------- |
| `memory_store.py`                      | ~95%        | Storage backend (optional)        |
| `chatkit_server.py` structure          | ~80%        | None (copy structure)             |
| `chatkit_server.py` `respond()` method | ~20%        | AI integration, response format   |
| Endpoint (`views.py`)                  | ~90%        | Error handling (optional)         |
| CORS config                            | ~100%       | Domain-specific headers (minimal) |

### Reusability Checklist for New Projects:

- [ ] Copy `memory_store.py` (use as-is or modify storage backend)
- [ ] Copy `chatkit_server.py` structure
- [ ] Customize `respond()` method with your AI/LLM integration
- [ ] Update class name (`YourProjectChatKitServer`)
- [ ] Update imports (remove Spendo-specific imports)
- [ ] Update singleton function name if needed
- [ ] Test with your specific workflow

**Bottom Line:**

- `memory_store.py`: Copy and use (or swap storage backend)
- `chatkit_server.py`: Copy structure, customize `respond()` method
- Everything else: Mostly reusable with minimal changes

---

## Summary of Files Created/Modified

### Backend Files Created:

- `server/Spendo/api/memory_store.py` - Thread and message persistence
- `server/Spendo/api/chatkit_server.py` - ChatKit server implementation

### Backend Files Modified:

- `server/Spendo/requirements.txt` - Added `openai-chatkit>=1.0.2,<2`
- `server/Spendo/api/views.py` - Added `chatkit_endpoint` function
- `server/Spendo/api/urls.py` - Added `/chatkit/` route
- `server/Spendo/Spendo/settings.py` - Added `CORS_ALLOW_HEADERS`

### Frontend Files Modified:

- `client/app/package.json` - Added `@openai/chatkit-react`
- `client/app/index.html` - Added ChatKit script and meta tag
- `client/app/src/components/chatbot/MyChat.tsx` - Configured ChatKit component

---

## Next Steps

1. **Production Considerations:**

   - Replace in-memory storage with database-backed storage
   - Update domain key to production key
   - Configure proper error handling and logging
   - Set up monitoring for the ChatKit endpoint

2. **Enhanced Features:**

   - Implement file attachment handling in `to_message_content`
   - Add user authentication context to threads
   - Implement thread archiving/deletion
   - Add rate limiting for the endpoint

3. **Testing:**
   - Test streaming responses
   - Test pagination with multiple threads
   - Test error handling and edge cases
   - Load testing for concurrent users

---

## Additional Resources

- [OpenAI ChatKit Documentation](https://platform.openai.com/docs/chatkit)
- [ChatKit Python SDK](https://github.com/openai/chatkit-python)
- [ChatKit React SDK](https://github.com/openai/chatkit-js/tree/main/packages/react)
