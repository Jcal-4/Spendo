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
        # Store user ID in thread metadata if available in context and not already set
        if not hasattr(thread, 'metadata') or thread.metadata is None:
            thread.metadata = {}
        elif not isinstance(thread.metadata, dict):
            # If metadata is not a dict, convert it
            thread.metadata = dict(thread.metadata) if hasattr(thread.metadata, '__dict__') else {}
        
        # Get user ID from context if available
        request = context.get("request") if context else None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_id = request.user.id
            if 'user_id' not in thread.metadata:
                thread.metadata['user_id'] = user_id
        
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

