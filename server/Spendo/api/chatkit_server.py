"""ChatKit server integration for Spendo backend."""

from __future__ import annotations

from datetime import datetime
from typing import Any, AsyncIterator
from asgiref.sync import sync_to_async

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
from .services.user_service import get_accounts_by_userid


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

        # Get user balance from database
        # ChatKit doesn't send user information with requests, so we rely on:
        # 1. Database lookup (thread_id -> user_id mapping)
        # 2. Thread metadata (stored from previous requests, in-memory)
        # 3. Django session (if cookies are sent)
        # 4. Request authentication (if cookies are sent)
        user_id = None
        
        # First try to get user ID from database (persistent storage)
        try:
            from .models import ChatKitThread
            
            # Use sync_to_async to call Django ORM from async context
            @sync_to_async
            def get_thread_user_id(thread_id):
                chatkit_thread = ChatKitThread.objects.filter(thread_id=thread_id).first()
                if chatkit_thread:
                    return chatkit_thread.user.id
                return None
            
            user_id = await get_thread_user_id(thread.id)
            if user_id:
                print(f"DEBUG: user_id from database (thread_id={thread.id}): {user_id}")
        except Exception as e:
            print(f"DEBUG: Error looking up thread in database: {e}")
        
        # Fallback: try thread metadata (in-memory, from previous requests)
        if not user_id:
            if hasattr(thread, 'metadata') and thread.metadata and isinstance(thread.metadata, dict):
                user_id = thread.metadata.get('user_id')
                if user_id:
                    print(f"DEBUG: user_id from thread metadata: {user_id}")
        
        # If thread is new (no user_id found), try to get from active user sessions
        # Since ChatKit doesn't send cookies, we'll check if there's only one active session
        # (for development) or use other heuristics
        if not user_id:
            try:
                from .models import ChatKitUserSession
                
                @sync_to_async
                def get_active_user():
                    # Get all active user sessions
                    active_sessions = ChatKitUserSession.objects.all()
                    count = active_sessions.count()
                    
                    # If there's exactly one active session, use that user
                    # This works for single-user development/testing
                    if count == 1:
                        session = active_sessions.first()
                        return session.user.id
                    # If multiple sessions, we can't determine which user
                    # In production, you might want to use IP address or other heuristics
                    return None
                
                user_id = await get_active_user()
                if user_id:
                    print(f"DEBUG: user_id from active ChatKit session: {user_id}")
            except Exception as e:
                print(f"DEBUG: Error getting active user session: {e}")
            
            # Fallback: try to get from request (if cookies work)
            if not user_id:
                request = context.get("request")
                if request:
                    # Try authenticated user
                    if hasattr(request, 'user') and request.user.is_authenticated:
                        user_id = request.user.id
                        print(f"DEBUG: user_id from request.user: {user_id}")
            
            # If we found a user_id, store it in database and thread metadata
            if user_id:
                try:
                    from .models import ChatKitThread, CustomUser
                    
                    # Use sync_to_async to call Django ORM from async context
                    @sync_to_async
                    def store_thread_user(thread_id, user_id):
                        user = CustomUser.objects.get(pk=user_id)
                        # Create or update the database record
                        ChatKitThread.objects.update_or_create(
                            thread_id=thread_id,
                            defaults={'user': user}
                        )
                    
                    await store_thread_user(thread.id, user_id)
                    print(f"DEBUG: Stored user_id in database for thread_id={thread.id}")
                except Exception as e:
                    print(f"DEBUG: Error storing thread in database: {e}")
                
                # Also store in thread metadata for faster access
                if not hasattr(thread, 'metadata') or thread.metadata is None:
                    thread.metadata = {}
                elif not isinstance(thread.metadata, dict):
                    thread.metadata = dict(thread.metadata) if hasattr(thread.metadata, '__dict__') else {}
                thread.metadata['user_id'] = user_id
                # Save the updated thread
                await self.store.save_thread(thread, context)
        
        if not user_id:
            print(f"DEBUG: No user_id found - user balance will not be included")
        
        # Fetch user balance if we have a user ID
        user_balance = None
        if user_id:
            # Use sync_to_async to call Django ORM from async context
            @sync_to_async
            def fetch_user_balance(user_id):
                return get_accounts_by_userid(user_id)
            
            user_balance = await fetch_user_balance(user_id)
            print(f"DEBUG: user_balance: {user_balance}")
        
        # Merge user balance into user_text if available
        if user_balance:
            balance_context = (
                f"\n\nUser's current financial balances:\n"
                f"Cash balance: ${user_balance.get('cash_balance', 0):,.2f}\n"
                f"Savings balance: ${user_balance.get('savings_balance', 0):,.2f}\n"
                f"Investing/Retirement: ${user_balance.get('investing_retirement', 0):,.2f}\n"
                f"Total balance: ${user_balance.get('total_balance', 0):,.2f}"
            )
            user_text = user_text + balance_context

        # Call the existing run_workflow function
        try:
            print(f"user_text: {user_text}")
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

