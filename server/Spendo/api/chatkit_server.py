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

