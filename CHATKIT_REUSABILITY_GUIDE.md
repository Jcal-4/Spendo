# ChatKit Server Reusability Guide

This document explains which parts of the ChatKit implementation are reusable and which need customization for each project.

## Overview

- **`memory_store.py`**: ~95% reusable across projects
- **`chatkit_server.py`**: Structure is reusable, but core logic needs customization

---

## `memory_store.py` - Highly Reusable ✅

The `SimpleMemoryStore` class implements the standard ChatKit storage interface and can be used as-is in most projects.

### What's Reusable:

- All method signatures
- Pagination logic (`has_more`, `after` attributes)
- Thread and item ID generation
- Basic in-memory storage structure

### What You Might Want to Customize:

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

---

## `chatkit_server.py` - Partially Reusable ⚠️

The class structure is reusable, but the `respond` method needs customization for each project's specific workflow.

### Reusable Template Structure:

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

### Customization Examples:

#### Example 1: Simple OpenAI Chat Completion

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

#### Example 2: Custom Agent/Workflow (like Spendo)

```python
async def respond(...):
    # ... extract user_text ...

    from .services.your_service import run_your_workflow, YourInputType

    workflow_input = YourInputType(input_text=user_text)
    result = await run_your_workflow(workflow_input)
    response_text = result.get("response_field", "Default message")

    # ... create and yield assistant_item ...
```

#### Example 3: Multiple AI Services

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

---

## What's Always Reusable:

1. **Class Structure**: `ChatKitServer[dict[str, Any]]` extension
2. **Store Initialization**: `self.store = SimpleMemoryStore()`
3. **Message Extraction**: `_user_message_text()` function
4. **Response Streaming**: The `ThreadItemDoneEvent` yield pattern
5. **Error Handling**: Basic try/except structure
6. **Singleton Pattern**: `get_chatkit_server()` function

## What Always Needs Customization:

1. **AI/LLM Integration**: How you generate responses
2. **Response Format**: How you extract response text from your AI service
3. **Business Logic**: Any custom processing before/after AI calls
4. **Context Usage**: How you use the `context` parameter

---

## Reusability Checklist for New Projects:

- [ ] Copy `memory_store.py` (use as-is or modify storage backend)
- [ ] Copy `chatkit_server.py` structure
- [ ] Customize `respond()` method with your AI/LLM integration
- [ ] Update class name (`YourProjectChatKitServer`)
- [ ] Update imports (remove Spendo-specific imports)
- [ ] Update singleton function name if needed
- [ ] Test with your specific workflow

---

## Summary

| Component                              | Reusability | Customization Needed              |
| -------------------------------------- | ----------- | --------------------------------- |
| `memory_store.py`                      | ~95%        | Storage backend (optional)        |
| `chatkit_server.py` structure          | ~80%        | None (copy structure)             |
| `chatkit_server.py` `respond()` method | ~20%        | AI integration, response format   |
| Endpoint (`views.py`)                  | ~90%        | Error handling (optional)         |
| CORS config                            | ~100%       | Domain-specific headers (minimal) |

**Bottom Line:**

- `memory_store.py`: Copy and use (or swap storage backend)
- `chatkit_server.py`: Copy structure, customize `respond()` method
- Everything else: Mostly reusable with minimal changes
