# ChatKit SDK Integration Guide

This document provides a complete guide for integrating OpenAI's ChatKit SDK into the Spendo application, including all backend and frontend modifications required.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Configuration Details](#configuration-details)
6. [User Identification and Context Integration](#user-identification-and-context-integration)
7. [Advanced Features](#advanced-features)
   - [Attachment Store](#attachment-store)
   - [Client Tools Usage](#client-tools-usage)
   - [Agents SDK Integration](#agents-sdk-integration)
   - [Widgets](#widgets)
   - [Thread Metadata](#thread-metadata)
   - [Automatic Thread Titles](#automatic-thread-titles)
   - [Progress Updates](#progress-updates)
   - [Server Context](#server-context)
8. [Troubleshooting](#troubleshooting)
9. [Code Reusability Guide](#code-reusability-guide)
10. [Summary of Files Created/Modified](#summary-of-files-createdmodified)
11. [Heroku Deployment](#heroku-deployment)
12. [Next Steps](#next-steps)
13. [Additional Resources](#additional-resources)

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

**Expected Time:** 30-60 minutes for basic setup (depending on familiarity with Django and React). Additional time for implementing advanced features as needed.

**Structure of This Guide:**

1. **Backend Setup** (Steps 1-6): Essential Django server configuration
2. **Frontend Setup** (Steps 1-4): React component integration
3. **Configuration Details**: Environment and key settings
4. **Advanced Features**: Optional enhancements (attachments, widgets, Agents SDK, etc.)
5. **Troubleshooting**: Common issues and solutions
6. **Code Reusability**: How to adapt this code for other projects

---

## Prerequisites

- Django backend running
- React frontend with Vite
- OpenAI API key with ChatKit access
- Domain verification key from OpenAI (for production)
- **Python 3.11 or higher** (required for `openai-chatkit>=1.0.2` which uses `assert_never` from `typing` module)

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

**Important: Python Version Requirement**

The `openai-chatkit>=1.0.2` package requires **Python 3.11 or higher** because it uses `assert_never` from the `typing` module, which was added in Python 3.11.

**For Heroku Deployment:**

Create a `.python-version` file in `server/Spendo/` directory:

```bash
# Create .python-version file
echo "3.11" > server/Spendo/.python-version
```

Or manually create `server/Spendo/.python-version` with:

```
3.11
```

**Note:** Heroku deprecated `runtime.txt` in favor of `.python-version`. The `.python-version` file should contain only the major version (e.g., `3.11`) to allow automatic security updates.

### Step 2: Create Memory Store (`memory_store.py`)

Create a new file `server/Spendo/api/memory_store.py` to handle thread and message persistence.

**Note**: This file implements the `Store` interface from ChatKit. The name "memory_store" refers to this specific implementation (an in-memory storage), while "Store" is the abstract interface it implements. You can name your file whatever you like, but it must implement the Store interface methods.

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
        """
        Generate a unique item ID (for messages, etc.).

        Note: In the full Store interface, item_type is StoreItemType, but this simple
        implementation accepts str for simplicity. For production, consider using StoreItemType.
        """
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
        # Store user ID in thread metadata if available in context and not already set
        # This helps with user identification when ChatKit doesn't send cookies
        if not hasattr(thread, 'metadata') or thread.metadata is None:
            thread.metadata = {}
        elif not isinstance(thread.metadata, dict):
            # If metadata is not a dict, convert it
            thread.metadata = dict(thread.metadata) if hasattr(thread.metadata, '__dict__') else {}

        # Note: We don't access request.user here because:
        # 1. It triggers SynchronousOnlyOperation errors in async contexts
        # 2. User identification is handled in chatkit_server.py using database models
        # 3. The user_id is already stored in thread.metadata by chatkit_server.py before calling save_thread

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

- `SimpleMemoryStore` implements the **essential** storage methods required for basic ChatKit functionality
- Methods handle pagination with `limit`, `after`, and `order` parameters
- Result objects must have `data`, `has_more`, and `after` attributes
- Thread IDs are generated with `"thread"` prefix, message IDs with `"msg"` prefix
- **Note**: This is a simplified implementation for development. For production, you should implement all methods from the complete Store interface (see below), including `delete_thread_item`, `save_item`, `load_item`, and attachment methods

### Complete Store Interface Reference

The `Store` interface from ChatKit is an abstract base class that defines all required methods for thread and message persistence. The `SimpleMemoryStore` shown above implements a subset suitable for basic use cases. For production, you may want to implement all methods.

**Source:** `chatkit/store.py`

```python
from abc import ABC, abstractmethod
from typing import Generic
from chatkit.store import Store, Page, StoreItemType
from chatkit.types import ThreadItem, ThreadMetadata, Attachment

class Store(ABC, Generic[TContext]):
    # ID generation (these have default implementations, override to customize)
    def generate_thread_id(self, context: TContext) -> str:
        """Return a new identifier for a thread. Override this method to customize thread ID generation."""
        return default_generate_id("thread")

    def generate_item_id(
        self, item_type: StoreItemType, thread: ThreadMetadata, context: TContext
    ) -> str:
        """Return a new identifier for a thread item. Override this method to customize item ID generation."""
        return default_generate_id(item_type)

    # Thread operations (abstract - must be implemented)
    @abstractmethod
    async def load_thread(self, thread_id: str, context: TContext) -> ThreadMetadata:
        """Load a thread by its ID."""
        pass

    @abstractmethod
    async def save_thread(self, thread: ThreadMetadata, context: TContext) -> None:
        """Save or update a thread."""
        pass

    @abstractmethod
    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: TContext,
    ) -> Page[ThreadMetadata]:
        """Load multiple threads with pagination and ordering."""
        pass

    @abstractmethod
    async def delete_thread(self, thread_id: str, context: TContext) -> None:
        """Delete a thread and all its items."""
        pass

    # Thread item operations (abstract - must be implemented)
    @abstractmethod
    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: TContext,
    ) -> Page[ThreadItem]:
        """Load thread items (messages, tool calls, etc.) with pagination."""
        pass

    @abstractmethod
    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: TContext
    ) -> None:
        """Add a new item to a thread."""
        pass

    @abstractmethod
    async def save_item(
        self, thread_id: str, item: ThreadItem, context: TContext
    ) -> None:
        """Save or update an existing thread item."""
        pass

    @abstractmethod
    async def load_item(
        self, thread_id: str, item_id: str, context: TContext
    ) -> ThreadItem:
        """Load a specific thread item by ID."""
        pass

    @abstractmethod
    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: TContext
    ) -> None:
        """Delete a specific thread item."""
        pass

    # Attachment operations (abstract - must be implemented)
    @abstractmethod
    async def save_attachment(self, attachment: Attachment, context: TContext) -> None:
        """Save attachment metadata to the store."""
        pass

    @abstractmethod
    async def load_attachment(
        self, attachment_id: str, context: TContext
    ) -> Attachment:
        """Load attachment metadata by ID."""
        pass

    @abstractmethod
    async def delete_attachment(self, attachment_id: str, context: TContext) -> None:
        """Delete attachment metadata from the store."""
        pass
```

**Important Notes:**

- **ID Generation Methods:** `generate_thread_id` and `generate_item_id` have default implementations that use `default_generate_id()` with prefixes like `"thread"` and `"message"`. Override these methods if your integration needs deterministic or pre-allocated identifiers
- **Default ID Format:** The default implementation prefixes identifiers using UUID4 strings (for example `thread_4f62d6a7f2c34bd084f57cfb3df9f6bd` or `msg_4f62d6a7f2c34bd084f57cfb3df9f6bd`)
- **StoreItemType:** The `item_type` parameter in `generate_item_id` is of type `StoreItemType`, which can be values like `"message"`, `"tool_call"`, `"task"`, `"workflow"`, or `"attachment"`
- **Database Implementation:** When implementing the store for relational databases, the recommended approach is to serialize models into JSON-typed columns instead of separating model fields across multiple columns. This allows for Thread/Attachment/ThreadItem type shapes to change between library versions
- **Missing Methods:** The `SimpleMemoryStore` example above doesn't implement `delete_thread_item`, `save_item`, `load_item`, and attachment methods. Add these for a complete implementation

#### Customizing ID Generation

You can override the ID generation methods to customize how IDs are created:

```python
from chatkit.store import Store, default_generate_id
from typing import Any

class CustomStore(Store[dict[str, Any]]):
    def generate_thread_id(self, context: dict[str, Any]) -> str:
        """Custom thread ID generation - e.g., use database sequence."""
        # Example: Use database sequence
        # return f"thread_{self.db.get_next_sequence('threads')}"

        # Example: Use timestamp + random suffix
        import time
        import random
        return f"thread_{int(time.time())}_{random.randint(1000, 9999)}"

        # Or use default implementation:
        # return default_generate_id("thread")

    def generate_item_id(
        self, item_type: StoreItemType, thread: ThreadMetadata, context: dict[str, Any]
    ) -> str:
        """Custom item ID generation - e.g., include thread ID prefix."""
        # Example: Include thread ID in item ID
        base_id = default_generate_id(item_type)
        return f"{thread.id}_{base_id}"

        # Or use default implementation:
        # return default_generate_id(item_type)
```

Similarly for `AttachmentStore`:

```python
class CustomAttachmentStore(AttachmentStore[dict[str, Any]]):
    def generate_attachment_id(self, mime_type: str, context: dict[str, Any]) -> str:
        """Custom attachment ID generation."""
        # Example: Include mime type in ID
        base_id = default_generate_id("attachment")
        mime_prefix = mime_type.split('/')[0] if '/' in mime_type else mime_type
        return f"{mime_prefix}_{base_id}"
```

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

        # Note: If you've enabled model or tool options in the composer,
        # they'll appear in input.inference_options. Your integration is
        # responsible for handling these values when performing inference.
        # Example:
        # inference_options = input.inference_options if hasattr(input, 'inference_options') else None
        # model = inference_options.model if inference_options else "gpt-4"

        # Call the existing run_workflow function
        try:
            workflow_input = WorkflowInput(input_as_text=user_text)
            result = await run_workflow(workflow_input)

            # Extract the response text - handle different return formats
            if isinstance(result, dict):
                # Check if result has tentativeresponse directly
                if "tentativeresponse" in result:
                    response_text = result["tentativeresponse"]
                # Check if result has output_parsed (from financial_reasoning_result)
                elif "output_parsed" in result and isinstance(result["output_parsed"], dict):
                    response_text = result["output_parsed"].get("tentativeresponse", "I'm sorry, I couldn't generate a response.")
                else:
                    response_text = "I'm sorry, I couldn't generate a response."
            else:
                response_text = "I'm sorry, I couldn't generate a response."

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

**Note:** This is a basic implementation. If you need to identify users and include user-specific data (like financial balances), see **Step 3.5** below for the complete implementation with user identification.

### Step 3.5: User Identification and Context Integration (Optional but Recommended)

**Problem:** ChatKit doesn't send user information (cookies, user ID, etc.) with its requests, making it difficult to identify which user is making a request. This section shows how to integrate user-specific data (like financial balances) into ChatKit responses.

**Solution:** Use a combination of database models to track active user sessions and thread-to-user mappings.

#### Step 3.5.1: Create Database Models

Add the following models to `server/Spendo/api/models.py`:

```python
class ChatKitThread(models.Model):
    """Store mapping of ChatKit thread_id to Django user_id for persistent user identification."""
    thread_id = models.CharField(max_length=255, unique=True, primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chatkit_threads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chatkit_threads'
        indexes = [
            models.Index(fields=['thread_id']),
            models.Index(fields=['user']),
        ]

class ChatKitUserSession(models.Model):
    """Store active user sessions for ChatKit - created on login, deleted on logout."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='chatkit_session')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chatkit_user_sessions'
        indexes = [
            models.Index(fields=['user']),
        ]
```

**Run migrations:**

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Step 3.5.2: Update Login/Logout Views

Modify your login and logout views in `server/Spendo/api/views.py` to track active sessions:

```python
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Store user session for ChatKit
            try:
                from .models import ChatKitUserSession
                ChatKitUserSession.objects.update_or_create(
                    user=user,
                    defaults={}  # Just update the updated_at timestamp
                )
            except Exception as e:
                print(f"DEBUG: Error storing ChatKit session: {e}")
            return Response({"detail": "Logged in"})
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

class LogoutView(APIView):
    def post(self, request):
        # Delete ChatKit session before logging out
        if request.user.is_authenticated:
            try:
                from .models import ChatKitUserSession
                ChatKitUserSession.objects.filter(user=request.user).delete()
            except Exception as e:
                print(f"DEBUG: Error deleting ChatKit session: {e}")
        logout(request)
        return Response({"detail": "Logged out"})
```

#### Step 3.5.3: Update ChatKit Server with User Context

Update `server/Spendo/api/chatkit_server.py` to identify users and fetch user-specific data:

```python
"""ChatKit server integration for Spendo backend."""

from __future__ import annotations

from datetime import datetime
from typing import Any, AsyncIterator
from asgiref.sync import sync_to_async  # Required for async Django ORM calls

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
from .services.user_service import get_accounts_by_userid  # Your user data service


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

        # ========================================
        # USER IDENTIFICATION SECTION
        # ========================================
        # ChatKit doesn't send user information with requests, so we rely on:
        # 1. Database lookup (thread_id -> user_id mapping) - persistent
        # 2. Thread metadata (stored from previous requests) - in-memory
        # 3. Active user sessions (created on login) - for new threads
        # 4. Request authentication (if cookies work) - fallback
        user_id = None

        # First try to get user ID from database (persistent storage)
        try:
            from .models import ChatKitThread

            @sync_to_async
            def get_thread_user_id(thread_id):
                chatkit_thread = ChatKitThread.objects.filter(thread_id=thread_id).first()
                if chatkit_thread:
                    return chatkit_thread.user.id
                return None

            user_id = await get_thread_user_id(thread.id)
        except Exception as e:
            print(f"DEBUG: Error looking up thread in database: {e}")

        # Fallback: try thread metadata (in-memory, from previous requests)
        if not user_id:
            if hasattr(thread, 'metadata') and thread.metadata and isinstance(thread.metadata, dict):
                user_id = thread.metadata.get('user_id')

        # If thread is new (no user_id found), try to get from active user sessions
        # Since ChatKit doesn't send cookies, we check if there's only one active session
        # This works for single-user development/testing
        if not user_id:
            try:
                from .models import ChatKitUserSession

                @sync_to_async
                def get_active_user():
                    active_sessions = ChatKitUserSession.objects.all()
                    count = active_sessions.count()
                    # If exactly one active session, use that user
                    if count == 1:
                        session = active_sessions.first()
                        return session.user.id
                    return None

                user_id = await get_active_user()
            except Exception as e:
                print(f"DEBUG: Error getting active user session: {e}")

            # Fallback: try to get from request (if cookies work)
            # Note: This may not work reliably in async contexts if request.user triggers a database query
            # It's included as a last resort fallback, but the database-backed approach above should handle most cases
            if not user_id:
                request = context.get("request")
                if request and hasattr(request, 'user') and request.user.is_authenticated:
                    # Accessing request.user can trigger database queries, but it's often cached
                    # If this causes SynchronousOnlyOperation errors, remove this fallback
                    try:
                        user_id = request.user.id
                    except Exception as e:
                        print(f"DEBUG: Error accessing request.user: {e}")
                        user_id = None

            # If we found a user_id, store it in database and thread metadata
            if user_id:
                try:
                    from .models import ChatKitThread, CustomUser

                    @sync_to_async
                    def store_thread_user(thread_id, user_id):
                        user = CustomUser.objects.get(pk=user_id)
                        ChatKitThread.objects.update_or_create(
                            thread_id=thread_id,
                            defaults={'user': user}
                        )

                    await store_thread_user(thread.id, user_id)
                except Exception as e:
                    print(f"DEBUG: Error storing thread in database: {e}")

                # Also store in thread metadata for faster access
                if not hasattr(thread, 'metadata') or thread.metadata is None:
                    thread.metadata = {}
                elif not isinstance(thread.metadata, dict):
                    thread.metadata = dict(thread.metadata) if hasattr(thread.metadata, '__dict__') else {}
                thread.metadata['user_id'] = user_id
                await self.store.save_thread(thread, context)

        # ========================================
        # FETCH USER-SPECIFIC DATA
        # ========================================
        # Example: Fetch user balance and merge into message
        user_balance = None
        if user_id:
            # Use sync_to_async to call Django ORM from async context
            @sync_to_async
            def fetch_user_balance(user_id):
                return get_accounts_by_userid(user_id)  # Your function to get user data

            user_balance = await fetch_user_balance(user_id)

        # Merge user data into user_text if available
        if user_balance:
            balance_context = (
                f"\n\nUser's current financial balances:\n"
                f"Cash balance: ${user_balance.get('cash_balance', 0):,.2f}\n"
                f"Savings balance: ${user_balance.get('savings_balance', 0):,.2f}\n"
                f"Investing/Retirement: ${user_balance.get('investing_retirement', 0):,.2f}\n"
                f"Total balance: ${user_balance.get('total_balance', 0):,.2f}"
            )
            user_text = user_text + balance_context

        # ========================================
        # CALL YOUR AI WORKFLOW
        # ========================================
        try:
            workflow_input = WorkflowInput(input_as_text=user_text)
            result = await run_workflow(workflow_input)

            # Extract the response text - handle different return formats
            if isinstance(result, dict):
                if "tentativeresponse" in result:
                    response_text = result["tentativeresponse"]
                elif "output_parsed" in result and isinstance(result["output_parsed"], dict):
                    response_text = result["output_parsed"].get("tentativeresponse", "I'm sorry, I couldn't generate a response.")
                else:
                    response_text = "I'm sorry, I couldn't generate a response."
            else:
                response_text = "I'm sorry, I couldn't generate a response."

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

- **`sync_to_async`**: Required for all Django ORM calls in async methods. Import from `asgiref.sync`
- **User Identification Strategy**:
  1. Check database for existing thread-to-user mapping (persistent)
  2. Check thread metadata (in-memory cache)
  3. Check active user sessions (works for single-user scenarios)
  4. Fallback to request authentication
- **Persistence**: Once a user is identified, store the mapping in both database and thread metadata
- **Single-User Limitation**: The active session approach works best when only one user is logged in. For production with multiple concurrent users, consider adding IP address matching or other heuristics

**Important Notes:**

- All Django ORM calls must be wrapped with `sync_to_async` when called from async methods
- The `ChatKitUserSession` model tracks who is currently logged in
- The `ChatKitThread` model stores persistent thread-to-user mappings
- User data is merged into the message text before sending to the AI, so the AI has context

### Step 4: Add ChatKit Endpoint (`views.py`)

Add the following to `server/Spendo/api/views.py`:

**At the top of the file, add imports:**

```python
import json
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatkit_server import get_chatkit_server
from chatkit.server import StreamingResult
```

**Note:** Adjust imports based on what's already in your file. You may need to add or remove imports depending on what's already imported in your `views.py` file.

**Add helper function and endpoint:**

```python
async def _collect_streaming_result(streaming_result):
    """Collect all items from a StreamingResult async iterator."""
    items = []
    # Check if it's an async iterator
    if hasattr(streaming_result, '__aiter__'):
        async_iter = streaming_result.__aiter__()
        try:
            while True:
                item = await async_iter.__anext__()
                items.append(item)
        except StopAsyncIteration:
            pass
    # Check if it's a regular iterator
    elif hasattr(streaming_result, '__iter__'):
        for item in streaming_result:
            items.append(item)
    else:
        # Try to iterate it directly
        try:
            async for item in streaming_result:
                items.append(item)
        except TypeError:
            # Not iterable, return as single item
            items = [streaming_result]
    return items


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

        # Note: We don't access request.session here because:
        # 1. It requires sync_to_async (sessions use database queries)
        # 2. We use database-backed user identification instead (ChatKitThread/ChatKitUserSession)
        # 3. ChatKit doesn't send cookies anyway, so sessions won't work
        # User identification happens in chatkit_server.py using database models

        result = await server.process(payload, {"request": request})

        if isinstance(result, StreamingResult):
            # Collect all items from the async iterator first
            items = await _collect_streaming_result(result)

            # Create a synchronous generator from collected items
            def sync_iterator():
                for item in items:
                    yield item

            # Return streaming response
            response = StreamingHttpResponse(
                sync_iterator(),
                content_type="text/event-stream"
            )
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            # Note: Do NOT set 'Connection: keep-alive' header - it's a hop-by-hop header
            # that causes errors with Django's development server (wsgiref).
            # SSE connections are kept alive by default, so this header is not needed.
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
- **Async Iterator Conversion:** The `_collect_streaming_result` helper function converts the async iterator from `StreamingResult` to a synchronous iterator for `StreamingHttpResponse`. This is necessary because Django's development server (wsgiref) doesn't fully support async streaming. In production with gunicorn, this conversion still works correctly.
- **No Session Access:** Do NOT access `request.session` in the async endpoint - it triggers synchronous database queries which cause `SynchronousOnlyOperation` errors. User identification is handled in `chatkit_server.py` using database models (`ChatKitThread` and `ChatKitUserSession`).
- **No Connection Header:** Do NOT set the `Connection: keep-alive` header - it's a hop-by-hop header that causes `AssertionError` with Django's development server (wsgiref). Server-Sent Events (SSE) connections are kept alive by default, so this header is not needed.

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
    path('chatkit/session/', create_chatkit_session, name='create_chatkit_session'),  # Optional: Only needed if using getClientSecret
    # ChatKit SDK endpoint for custom backend
    path('chatkit/', chatkit_endpoint, name='chatkit_endpoint'),
]
```

**Note:** The `create_chatkit_session` endpoint is optional. It's only needed if you're using `getClientSecret` in the frontend (see Step 3.5 for the recommended user identification approach that doesn't require this endpoint).

### Step 5.5: Create ChatKit Session Endpoint (Optional)

**When to use:** Only if you're using `getClientSecret` in the frontend. The recommended approach (Step 3.5) doesn't require this endpoint.

If you need to create ChatKit sessions manually, add this to `server/Spendo/api/views.py`:

```python
@api_view(["POST"])
def create_chatkit_session(request):
    import requests
    import os

    openai_api_key = os.getenv("OPENAI_API_KEY")
    workflow_id = "wf_your_workflow_id"  # Replace with your workflow ID
    url = "https://api.openai.com/v1/chatkit/sessions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "chatkit_beta=v1",
    }

    # Get user ID from request body or authenticated user
    user_id_from_body = request.data.get("user_id") if hasattr(request, 'data') else None
    django_user_id = None

    if user_id_from_body:
        try:
            from .models import CustomUser
            user = CustomUser.objects.get(pk=user_id_from_body)
            chatkit_user_id = user.username
            django_user_id = user_id_from_body
        except CustomUser.DoesNotExist:
            chatkit_user_id = "anonymous"
    elif request.user and request.user.is_authenticated:
        chatkit_user_id = request.user.username
        django_user_id = request.user.id
    else:
        chatkit_user_id = "anonymous"

    data = {
        "workflow": {"id": workflow_id},
        "user": chatkit_user_id
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        client_secret = response_data.get("client_secret")
        return Response({"client_secret": client_secret})
    else:
        return Response({"error": response.text}, status=response.status_code)
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

**Note:** The simple `url` configuration approach is used here. The recommended user identification approach (Step 3.5) doesn't require `getClientSecret` or the session endpoint - it uses database models to track active users.

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

## User Identification and Context Integration

### Overview

ChatKit doesn't send user information (cookies, user ID, etc.) with its requests, making it challenging to identify which user is making a request. This section explains how to integrate user-specific data into ChatKit responses.

### The Problem

- ChatKit requests don't include authentication cookies
- ChatKit doesn't send user ID in headers or payload
- You need to identify users to fetch personalized data (e.g., financial balances, preferences)

### The Solution

Use a combination of:

1. **Active Session Tracking**: Store active user sessions when users log in
2. **Thread-to-User Mapping**: Persist user ID with each thread in the database
3. **Fallback Strategies**: Multiple methods to identify users

### Implementation Steps

See **Step 3.5** in the Backend Setup section for complete implementation details.

### How It Works

1. **On Login**: Create `ChatKitUserSession` record
2. **On ChatKit Request**:
   - Check if thread already has user_id (from database)
   - If new thread, check active sessions (single-user scenario)
   - Store user_id with thread_id for future requests
3. **Fetch User Data**: Use identified user_id to fetch personalized data
4. **Merge into Message**: Add user data to message text before sending to AI

### Limitations

- **Single-User Scenarios**: Works best when only one user is logged in
- **Multiple Users**: For production with concurrent users, consider:
  - IP address matching
  - Session token validation
  - Additional identification heuristics

### Example Use Cases

- Financial applications: Include user's account balances
- E-commerce: Include user's purchase history
- Personalization: Include user preferences and settings
- Multi-tenant: Identify which organization/workspace the user belongs to

---

## Advanced Features

This section covers advanced ChatKit features that go beyond basic chat functionality. These features are **optional** and can be implemented as needed:

- **Attachment Store**: Handle file uploads and attachments
- **Client Tools**: Trigger client-side callbacks from server-side agents
- **Agents SDK Integration**: Integrate with OpenAI's Agents SDK for more powerful workflows
- **Widgets**: Display rich UI components in chat conversations
- **Thread Metadata**: Store custom data associated with threads
- **Automatic Thread Titles**: Generate conversation titles automatically
- **Progress Updates**: Show progress indicators for long-running operations
- **Server Context**: Pass custom context data through the request pipeline

**Note**: You can implement these features incrementally. Start with the basic setup from earlier sections, then add advanced features as your application requires them.

### Attachment Store

Users can upload attachments (files and images) to include with chat messages. You are responsible for providing a storage implementation and handling uploads. The `attachment_store` argument to `ChatKitServer` should implement the `AttachmentStore` interface. If not provided, operations on attachments will raise an error.

#### Attachment Store Interface

**Source:** `chatkit/store.py`

The `AttachmentStore` interface handles attachment metadata storage. Note that the actual file bytes are typically stored separately (e.g., in S3, GCS, or local filesystem).

```python
from abc import ABC, abstractmethod
from typing import Generic
from chatkit.store import AttachmentStore
from chatkit.types import Attachment, AttachmentCreateParams

class AttachmentStore(ABC, Generic[TContext]):
    @abstractmethod
    async def delete_attachment(self, attachment_id: str, context: TContext) -> None:
        """Delete attachment metadata from the store."""
        pass

    async def create_attachment(
        self, input: AttachmentCreateParams, context: TContext
    ) -> Attachment:
        """
        Create attachment metadata. This method must be overridden to support two-phase file upload.

        Raises NotImplementedError if not overridden.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must override create_attachment() to support two-phase file upload"
        )

    def generate_attachment_id(self, mime_type: str, context: TContext) -> str:
        """
        Return a new identifier for a file. Override this method to customize file ID generation.

        Default implementation uses default_generate_id("attachment").
        """
        return default_generate_id("attachment")
```

**Key Points:**

- **`generate_attachment_id`:** Has a default implementation that can be overridden for custom ID generation
- **`create_attachment`:** Must be overridden to support two-phase file upload. If not implemented, raises `NotImplementedError`
- **`delete_attachment`:** Abstract method that must be implemented to remove attachment metadata
- **File Storage:** The store does not have to persist bytes itself. It can act as a proxy that issues signed URLs for upload and preview (e.g., S3/GCS/Azure), while your separate upload endpoint writes to object storage

#### Upload Strategies

ChatKit supports both direct uploads and two‑phase upload, configurable client-side via `ChatKitOptions.composer.attachments.uploadStrategy`.

##### Direct Upload

The direct upload URL is provided client-side as a create option.

The client will POST `multipart/form-data` with a `file` field to that URL. The server should:

1. Persist the attachment metadata (`FileAttachment | ImageAttachment`) to the data store and the file bytes to your storage
2. Respond with JSON representation of `FileAttachment | ImageAttachment`

##### Two‑Phase Upload

- **Phase 1 (registration and upload URL provisioning):** The client calls `attachments.create`. ChatKit persists a `FileAttachment | ImageAttachment`, sets the `upload_url` and returns it. It's recommended to include the `id` of the `Attachment` in the `upload_url` so that you can associate the file bytes with the `Attachment`.

- **Phase 2 (upload):** The client POSTs the bytes to the returned `upload_url` with `multipart/form-data` field `file`.

#### Previews

To render thumbnails of an image attached to a user message, set `ImageAttachment.preview_url` to a renderable URL. If you need expiring URLs, do not persist the URL; generate it on demand when returning the attachment to the client.

#### Access Control

**Critical Security Consideration:** Attachment metadata and file bytes are not protected by ChatKit. Each `AttachmentStore` method receives your request context so you can enforce thread- and user-level authorization before handing out attachment IDs, bytes, or signed URLs. Deny access when the caller does not own the attachment, and generate download URLs that expire quickly. Skipping these checks can leak customer data.

Example implementation:

```python
class SecureAttachmentStore(AttachmentStore[dict[str, Any]]):
    async def load_attachment(self, attachment_id: str, context: dict[str, Any]) -> Attachment:
        user_id = context.get("userId")
        attachment = await self.db.get_attachment(attachment_id)

        # Check if user has access to this attachment
        if not await self.can_user_access(user_id, attachment):
            raise PermissionError("Access denied")

        return attachment
```

#### Attaching Files to Agent SDK Inputs

You are responsible for deciding how to attach attachments to Agent SDK inputs. You can store files in your own storage and attach them as base64-encoded payloads or upload them to the OpenAI Files API and provide the file ID to the Agent SDK.

Example of creating base64-encoded payloads for attachments by customizing a `ThreadItemConverter`:

```python
import base64
from chatkit.agents import ThreadItemConverter
from chatkit.types import Attachment, ImageAttachment
from agents import ResponseInputImageParam, ResponseInputFileParam

async def read_attachment_bytes(attachment_id: str) -> bytes:
    """Replace with your blob-store fetch (S3, local disk, etc.)."""
    # Your implementation to fetch attachment bytes
    ...

class MyConverter(ThreadItemConverter):
    async def attachment_to_message_content(
        self, input: Attachment
    ) -> ResponseInputContentParam:
        content = await read_attachment_bytes(input.id)
        data = (
            "data:"
            + str(input.mime_type)
            + ";base64,"
            + base64.b64encode(content).decode("utf-8")
        )

        if isinstance(input, ImageAttachment):
            return ResponseInputImageParam(
                type="input_image",
                detail="auto",
                image_url=data,
            )

        # Note: Agents SDK currently only supports pdf files as ResponseInputFileParam.
        # To send other text file types, either convert them to pdf on the fly or
        # add them as input text.
        return ResponseInputFileParam(
            type="input_file",
            file_data=data,
            filename=input.name or "unknown",
        )

# In respond(...):
from chatkit.agents import simple_to_agent_input

result = Runner.run_streamed(
    assistant_agent,
    await MyConverter().to_agent_input(input),
    context=context,
)
```

### Client Tools Usage

The ChatKit server implementation can trigger client-side tools. These are client-side callbacks invoked by the agent during server-side inference.

The tool must be registered both when initializing ChatKit on the client and when setting up Agents SDK on the server.

To trigger a client-side tool from Agents SDK, set `ctx.context.client_tool_call` in the tool implementation with the client-side tool name and arguments. The result of the client tool execution will be provided back to the model.

**Important Notes:**

- The agent behavior must be set to `tool_use_behavior=StopAtTools` with all client-side tools included in `stop_at_tool_names`. This causes the agent to stop generating new messages until the client tool call is acknowledged by the ChatKit UI
- Only one client tool call can be triggered per turn
- Client tools are client-side callbacks invoked by the agent during server-side inference. If you're interested in client-side callbacks triggered by a user interacting with a widget, refer to [client actions](https://platform.openai.com/docs/chatkit/actions#client)

Example implementation:

```python
from chatkit.agents import AgentContext, stream_agent_response
from chatkit.types import ClientToolCall
from agents import Agent, Runner, function_tool, RunContextWrapper, StopAtTools

@function_tool(description_override="Add an item to the user's todo list.")
async def add_to_todo_list(ctx: RunContextWrapper[AgentContext], item: str) -> None:
    ctx.context.client_tool_call = ClientToolCall(
        name="add_to_todo_list",
        arguments={"item": item},
    )

assistant_agent = Agent[AgentContext](
    model="gpt-4.1",
    name="Assistant",
    instructions="You are a helpful assistant",
    tools=[add_to_todo_list],
    tool_use_behavior=StopAtTools(stop_at_tool_names=[add_to_todo_list.name]),
)

class MyChatKitServer(ChatKitServer):
    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | None,
        context: Any,
    ) -> AsyncIterator[ThreadStreamEvent]:
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        result = Runner.run_streamed(
            self.assistant_agent,
            await simple_to_agent_input(input) if input else [],
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event
```

### Agents SDK Integration

The ChatKit server is independent of Agents SDK. As long as correct events are returned from the `respond` method, the ChatKit UI will display the conversation as expected.

The ChatKit library provides helpers to integrate with Agents SDK:

- **`AgentContext`** - The context type that should be used when calling Agents SDK. It provides helpers to stream events from tool calls, render widgets, and initiate client tool calls.

- **`stream_agent_response`** - A helper to convert a streamed Agents SDK run into ChatKit events.

- **`ThreadItemConverter`** - A helper class that you'll probably extend to convert ChatKit thread items to Agents SDK input items.

- **`simple_to_agent_input`** - A helper function that uses the default thread item conversions. The default conversion is limited, but useful for getting started quickly.

#### Basic Integration Pattern

```python
from chatkit.agents import AgentContext, stream_agent_response, simple_to_agent_input
from agents import Agent, Runner

class MyChatKitServer(ChatKitServer):
    assistant_agent = Agent[AgentContext](
        model="gpt-4.1",
        name="Assistant",
        instructions="You are a helpful assistant"
    )

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | None,
        context: Any,
    ) -> AsyncIterator[ThreadStreamEvent]:
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        result = Runner.run_streamed(
            self.assistant_agent,
            await simple_to_agent_input(input) if input else [],
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event
```

#### ThreadItemConverter

Extend `ThreadItemConverter` when your integration supports:

- Attachments
- @-mentions (entity tagging)
- `HiddenContextItem`
- Custom thread item formats

Example:

```python
from chatkit.agents import ThreadItemConverter
from chatkit.types import Attachment, HiddenContextItem, ImageAttachment, UserMessageTagContent
from agents import Message, ResponseInputTextParam, ResponseInputImageParam
import base64

class MyThreadConverter(ThreadItemConverter):
    async def attachment_to_message_content(
        self, attachment: Attachment
    ) -> ResponseInputContentParam:
        content = await attachment_store.get_attachment_contents(attachment.id)
        data_url = "data:%s;base64,%s" % (
            attachment.mime_type,
            base64.b64encode(content).decode("utf-8")
        )

        if isinstance(attachment, ImageAttachment):
            return ResponseInputImageParam(
                type="input_image",
                detail="auto",
                image_url=data_url,
            )

        # Handle other attachment types...

    def hidden_context_to_input(self, item: HiddenContextItem) -> Message:
        return Message(
            type="message",
            role="system",
            content=[
                ResponseInputTextParam(
                    type="input_text",
                    text=f"<HIDDEN_CONTEXT>{item.content}</HIDDEN_CONTEXT>",
                )
            ],
        )

    def tag_to_message_content(self, tag: UserMessageTagContent):
        tag_context = await retrieve_context_for_tag(tag.id)
        return ResponseInputTextParam(
            type="input_text",
            text=f"<TAG>Name:{tag.data.name}\nType:{tag.data.type}\nDetails:{tag_context}</TAG>"
        )

        # Handle other @-mentions...
```

### Widgets

Widgets are rich UI components that can be displayed in chat. You can return a widget either directly from the `respond` method (if you want to do so unconditionally) or from a tool call triggered by the model.

#### Basic Widget Example

Example of a widget returned directly from the `respond` method:

```python
from chatkit.types import Text
from chatkit.events import stream_widget

async def respond(
    self,
    thread: ThreadMetadata,
    input: UserMessageItem | None,
    context: Any,
) -> AsyncIterator[ThreadStreamEvent]:
    widget = Text(
        id="description",
        value="Text widget",
    )

    async for event in stream_widget(
        thread,
        widget,
        generate_id=lambda item_type: self.store.generate_item_id(
            item_type, thread, context
        ),
    ):
        yield event
```

Example of a widget returned from a tool call:

```python
from chatkit.types import Text
from agents import function_tool, RunContextWrapper

@function_tool(description_override="Display a sample widget to the user.")
async def sample_widget(ctx: RunContextWrapper[AgentContext]) -> None:
    widget = Text(
        id="description",
        value="Text widget",
    )
    await ctx.context.stream_widget(widget)
```

#### Streaming Widgets

You can also stream an updating widget by yielding new versions of the widget from a generator function. The ChatKit framework will send updates for the parts of the widget that have changed.

**Note:** Currently, only `<Text>` and `<Markdown>` components marked with an `id` have their text updates streamed.

Example:

```python
from chatkit.types import Text, Card, Widget
from chatkit.agents import accumulate_text
from agents import Runner, RunContextWrapper, AgentContext
from typing import AsyncGenerator

async def sample_widget(ctx: RunContextWrapper[AgentContext]) -> None:
    description_text = Runner.run_streamed(
        email_generator, "ChatKit is the best thing ever"
    )

    async def widget_generator() -> AsyncGenerator[Widget, None]:
        text_widget_updates = accumulate_text(
            description_text.stream_events(),
            Text(
                id="description",
                value="",
                streaming=True
            ),
        )

        async for text_widget in text_widget_updates:
            yield Card(
                children=[text_widget]
            )

    await ctx.context.stream_widget(widget_generator())
```

#### Defining Widgets from JSON

You may find it easier to write widgets in JSON. You can parse JSON widgets to `WidgetRoot` instances for your server to stream:

```python
from chatkit.types import WidgetRoot
from pydantic import ValidationError

try:
    widget = WidgetRoot.model_validate_json(WIDGET_JSON_STRING)
except ValidationError:
    # handle invalid json
    pass
```

For full widget reference, components, props, and examples, see the [ChatKit Widgets Documentation](https://platform.openai.com/docs/chatkit/widgets).

### Thread Metadata

ChatKit provides a way to store arbitrary information associated with a thread. This information is not sent to the UI.

One use case for the metadata is to preserve the [`previous_response_id`](https://platform.openai.com/docs/api-reference/responses/create#responses-create-previous_response_id) and avoid having to re-send all items for an Agent SDK run.

Example usage:

```python
previous_response_id = thread.metadata.get("previous_response_id")

# Run the Agent SDK run with the previous response id
result = Runner.run_streamed(
    agent,
    input=...,
    previous_response_id=previous_response_id,
)

# Save the previous response id for the next run
thread.metadata["previous_response_id"] = result.response_id
await self.store.save_thread(thread, context)
```

### Automatic Thread Titles

ChatKit does not automatically title threads, but you can easily implement your own logic to do so.

First, decide when to trigger the thread title update. A simple approach might be to set the thread title the first time a user sends a message.

Example implementation:

```python
import asyncio
from chatkit.agents import simple_to_agent_input
from agents import Runner, Agent

class MyChatKitServer(ChatKitServer):
    title_agent = Agent(
        model="gpt-4",
        instructions="Generate a short, descriptive title (3-5 words) for this conversation."
    )

    async def maybe_update_thread_title(
        self,
        thread: ThreadMetadata,
        input_item: UserMessageItem,
    ) -> None:
        if thread.title is not None:
            return

        agent_input = await simple_to_agent_input(input_item)
        run = await Runner.run(self.title_agent, input=agent_input)
        thread.title = run.final_output
        await self.store.save_thread(thread, {})

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | None,
        context: Any,
    ) -> AsyncIterator[ThreadStreamEvent]:
        if input is not None:
            asyncio.create_task(self.maybe_update_thread_title(thread, input))

        # Generate the model response
        ...
```

### Progress Updates

If your server-side tool takes a while to run, you can use the progress update event to display the progress to the user.

Example:

```python
from chatkit.types import ProgressUpdateEvent
from agents import function_tool, RunContextWrapper
import asyncio

@function_tool()
async def long_running_tool(ctx: RunContextWrapper[AgentContext]) -> str:
    await ctx.context.stream(
        ProgressUpdateEvent(text="Loading a user profile...")
    )

    await asyncio.sleep(1)

    await ctx.context.stream(
        ProgressUpdateEvent(text="Processing data...")
    )

    await asyncio.sleep(1)

    await ctx.context.stream(
        ProgressUpdateEvent(text="Finalizing results...")
    )

    return "Task completed!"
```

The progress update will be automatically replaced by the next assistant message, widget, or another progress update.

### Server Context

Sometimes it's useful to pass additional information (like `userId`) to the ChatKit server implementation. The `ChatKitServer.process` method accepts a `context` parameter that it passes to the `respond` method and all data store and file store methods.

**Note:** In the Spendo implementation, we don't rely on context for user identification because ChatKit doesn't send cookies. Instead, we use database models (`ChatKitUserSession` and `ChatKitThread`) to identify users. However, context can still be useful for other purposes.

Example usage:

```python
class MyChatKitServer(ChatKitServer):
    async def respond(..., context) -> AsyncIterator[ThreadStreamEvent]:
        # Access context information
        user_id = context.get("userId")
        # Use user_id for custom logic...

# When calling process:
server.process(..., context={"userId": "user_123"})
```

Server context may be used to implement permission checks in `AttachmentStore` and `Store`:

```python
class MyChatKitServer(ChatKitServer):
    async def load_attachment(..., context) -> Attachment:
        user_id = context.get("userId")
        # Check if user_id has access to the file
        if not await self.can_user_access(user_id, attachment_id):
            raise PermissionError("Access denied")
        return attachment
```

**Important:** For user identification in ChatKit, use the database-based approach (see Step 3.5) rather than relying on context, as ChatKit requests don't include authentication cookies.

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

### Error: ImportError: cannot import name 'assert_never' from 'typing'

**Symptom:** `ImportError: cannot import name 'assert_never' from 'typing'` when running on Python 3.10 or lower

**Solution:** The `openai-chatkit>=1.0.2` package requires Python 3.11 or higher.

1. **For Heroku:** Create `server/Spendo/.python-version` with `3.11`
2. **For local development:** Upgrade to Python 3.11+ and ensure your virtual environment uses it
3. **Verify Python version:** Run `python --version` to confirm you're using 3.11+

### Error: StreamingHttpResponse with async iterator warning

**Symptom:** Warning: `StreamingHttpResponse must consume asynchronous iterators in order to serve them synchronously`

**Solution:** This is handled by the `_collect_streaming_result` helper function in `views.py`. The function converts the async iterator to a synchronous one. The warning may still appear in development but functionality works correctly. In production with gunicorn, this works without warnings.

### Error: SynchronousOnlyOperation - Django ORM in async context

**Symptom:** `django.core.exceptions.SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async.`

**Solution:** All Django ORM calls in async methods must be wrapped with `sync_to_async`:

```python
from asgiref.sync import sync_to_async

# In an async method:
@sync_to_async
def fetch_user_data(user_id):
    return YourModel.objects.get(pk=user_id)

user_data = await fetch_user_data(user_id)
```

**Common places this is needed:**

- Database queries in `chatkit_server.py` `respond()` method
- Any Django ORM calls in async ChatKit methods
- User data fetching functions called from async context

### User Identification Not Working

**Symptom:** User balance or other user-specific data is not being included in ChatKit responses.

**Solution:** Ensure you've:

1. Created the `ChatKitThread` and `ChatKitUserSession` models
2. Run migrations: `python manage.py makemigrations && python manage.py migrate`
3. Updated `LoginView` to create `ChatKitUserSession` on login
4. Updated `LogoutView` to delete `ChatKitUserSession` on logout
5. Wrapped all Django ORM calls with `sync_to_async` in the `respond()` method

**For production with multiple concurrent users:** The single active session approach works for development but may need enhancement. Consider:

- IP address matching
- Session token validation
- More sophisticated user identification heuristics

### Error: 500 Internal Server Error

**Common Causes:**

1. Missing required methods in `SimpleMemoryStore`
2. Incorrect Result object structure
3. Async/sync method mismatches
4. Missing imports in `views.py`
5. Incorrect response extraction from workflow result (check for typos like "tentativeresponseee" vs "tentativeresponse")

**Debug Steps:**

1. Check Django server logs for detailed error messages
2. Verify all imports are correct
3. Ensure `chatkit_endpoint` is properly decorated with `@csrf_exempt`
4. Confirm `get_chatkit_server()` is imported in `views.py`
5. Verify the response extraction logic handles all return formats from your workflow

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
| User identification models             | ~90%        | Adapt to your user model          |
| Login/Logout integration               | ~85%        | Match your auth system            |
| Endpoint (`views.py`)                  | ~90%        | Error handling (optional)         |
| CORS config                            | ~100%       | Domain-specific headers (minimal) |

### Reusability Checklist for New Projects:

- [ ] Copy `memory_store.py` (use as-is or modify storage backend)
- [ ] Copy `chatkit_server.py` structure
- [ ] Customize `respond()` method with your AI/LLM integration
- [ ] Update class name (`YourProjectChatKitServer`)
- [ ] Update imports (remove Spendo-specific imports)
- [ ] Update singleton function name if needed
- [ ] **If you need user identification:**
  - [ ] Create `ChatKitThread` and `ChatKitUserSession` models (adapt to your user model)
  - [ ] Update login/logout views to track active sessions
  - [ ] Implement user identification logic in `respond()` method
  - [ ] Wrap all Django ORM calls with `sync_to_async`
- [ ] Test with your specific workflow

**Bottom Line:**

- `memory_store.py`: Copy and use (or swap storage backend)
- `chatkit_server.py`: Copy structure, customize `respond()` method
- User identification: Copy the pattern, adapt to your user model and data needs
- Everything else: Mostly reusable with minimal changes

---

## Summary of Files Created/Modified

### Backend Files Created:

- `server/Spendo/api/memory_store.py` - Thread and message persistence
- `server/Spendo/api/chatkit_server.py` - ChatKit server implementation

### Backend Files Modified:

- `server/Spendo/requirements.txt` - Added `openai-chatkit>=1.0.2,<2`
- `server/Spendo/api/models.py` - Added `ChatKitThread` and `ChatKitUserSession` models for user identification
- `server/Spendo/api/views.py` - Added `chatkit_endpoint` function, `_collect_streaming_result` helper, and updated `LoginView`/`LogoutView` to track active sessions
- `server/Spendo/api/urls.py` - Added `/chatkit/` route (and optionally `/chatkit/session/` if using getClientSecret)
- `server/Spendo/Spendo/settings.py` - Added `CORS_ALLOW_HEADERS`
- `server/Spendo/.python-version` - Created with `3.11` for Heroku deployment (Python 3.11+ required)

### Frontend Files Modified:

- `client/app/package.json` - Added `@openai/chatkit-react`
- `client/app/index.html` - Added ChatKit script and meta tag
- `client/app/src/components/chatbot/MyChat.tsx` - Configured ChatKit component

---

## Heroku Deployment

### Prerequisites

1. **Python Version**: Ensure `server/Spendo/.python-version` contains `3.11` (already set up in Step 1)
2. **Dependencies**: All required packages should be in `requirements.txt` (already added in Step 1)
3. **Database**: Heroku Postgres addon should be configured

### Deployment Steps

1. **Create and commit migrations locally:**

   ```bash
   python manage.py makemigrations
   git add server/Spendo/api/migrations/
   git commit -m "Add ChatKit user identification models"
   ```

2. **Deploy to Heroku:**

   ```bash
   git push heroku main
   ```

3. **Run migrations on Heroku:**

   ```bash
   heroku run python manage.py migrate
   ```

   **Important:** The new `ChatKitThread` and `ChatKitUserSession` models must be migrated on Heroku before the ChatKit integration will work correctly.

### Optional: Automatic Migrations on Deploy

To automatically run migrations on each deploy, add a `release` process to your `Procfile`:

```
web: gunicorn Spendo.wsgi
release: python manage.py migrate
```

**Note:** The `release` process runs before the `web` process starts, ensuring migrations are applied before the app serves requests.

### Verifying Deployment

After deployment, verify:

1. Check Heroku logs: `heroku logs --tail`
2. Test the ChatKit endpoint: `curl https://your-app.herokuapp.com/api/chatkit/` (should return `{"status": "ok"}`)
3. Verify database tables exist: `heroku run python manage.py dbshell` then `\dt` to list tables (should see `chatkit_threads` and `chatkit_user_sessions`)

### Troubleshooting Heroku Deployment

**Issue: Models not found**

- **Solution:** Run migrations: `heroku run python manage.py migrate`

**Issue: Python version error**

- **Solution:** Ensure `.python-version` file exists with `3.11` in `server/Spendo/` directory

**Issue: Import errors for `openai-chatkit`**

- **Solution:** Ensure `openai-chatkit>=1.0.2,<2` is in `requirements.txt` and dependencies are installed

**Issue: `SynchronousOnlyOperation` errors**

- **Solution:** All Django ORM calls are already wrapped with `sync_to_async` in the implementation - this should work correctly on Heroku with gunicorn

**Common causes:**

- Accessing `request.session` in async functions (sessions ALWAYS use database queries) - **This will always fail**
- Calling Django ORM methods directly without `sync_to_async` wrapper
- Accessing `request.user` in async context (may trigger database queries if user isn't cached) - **May fail depending on Django version and middleware**

**Fix:**

- **For sessions:** Never access `request.session` in async endpoints. Use the database-backed approach (ChatKitThread/ChatKitUserSession) instead.
- **For request.user:** Wrap with `sync_to_async` if needed, or rely on the database-backed approach which is more reliable.
- **For ORM calls:** Always wrap with `sync_to_async` when called from async methods.

**Issue: `AssertionError: Hop-by-hop header, 'Connection: keep-alive', not allowed`**

**Symptom:** `AssertionError: Hop-by-hop header, 'Connection: keep-alive', not allowed` when using ChatKit locally with Django's development server (wsgiref).

**Cause:** The `Connection: keep-alive` header is a hop-by-hop header that Django's development server (wsgiref) doesn't allow. This header was added to support Server-Sent Events (SSE), but it's not needed.

**Fix:** Remove the `Connection: keep-alive` header from your `StreamingHttpResponse`. SSE connections are kept alive by default, so this header is unnecessary.

```python
# ❌ Don't do this:
response['Connection'] = 'keep-alive'

# ✅ Do this instead:
response = StreamingHttpResponse(
    sync_iterator(),
    content_type="text/event-stream"
)
response['Cache-Control'] = 'no-cache'
response['X-Accel-Buffering'] = 'no'
# Connection header not needed - SSE keeps connection alive by default
```

**Note:** This error only occurs with Django's development server (wsgiref). Production servers (gunicorn, uvicorn) handle this differently, but it's still best practice to omit this header.

**Issue: ChatKit Refreshes Without Showing Response on Heroku**

**Symptom:** ChatKit interface keeps refreshing/loading but no response is displayed on Heroku.

**Debugging Steps:**

1. **Check Heroku logs for errors:**

   ```bash
   heroku logs --tail
   ```

   Look for:

   - `DEBUG:` messages showing the flow of execution
   - Error messages or tracebacks
   - Database connection errors
   - Import errors

2. **Verify migrations ran:**

   ```bash
   heroku run python manage.py migrate
   ```

   Ensure `chatkit_threads` and `chatkit_user_sessions` tables exist.

3. **Check if endpoint is accessible:**

   ```bash
   curl https://your-app.herokuapp.com/api/chatkit/
   ```

   Should return `{"status": "ok"}`

4. **Common Causes:**

   - **Database not migrated:** Run migrations (see above)
   - **Environment variables missing:** Check `OPENAI_API_KEY` and other required vars with `heroku config`
   - **Response serialization issue:** Check logs for serialization errors
   - **CORS issues:** Verify CORS headers are set correctly in `settings.py`
   - **Streaming format issue:** The `StreamingResult` items need proper serialization

5. **Check logs for these specific messages:**
   - `DEBUG: Processing StreamingResult` - confirms endpoint is called
   - `DEBUG: Collected X items` - confirms events are generated
   - `DEBUG: Yielding item` - confirms items are being sent
   - Any error messages or tracebacks

**Solution:** Based on the logs, the issue is usually one of:

- Missing database migrations (most common)
- Missing environment variables
- Response format not matching ChatKit's expectations
- Errors in the `respond()` method that aren't being caught

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
