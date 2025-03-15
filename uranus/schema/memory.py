from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from uranus.schema.message import Message


class Memory(BaseModel):
    """Memory for an agent."""
    
    messages: List[Message] = Field(default_factory=list)
    max_messages: int = 100
    
    def add_message(self, message: Message) -> None:
        """Add a message to memory."""
        self.messages.append(message)
        self._trim_memory()
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to memory."""
        self.add_message(Message.user_message(content))
    
    def add_system_message(self, content: str) -> None:
        """Add a system message to memory."""
        self.add_message(Message.system_message(content))
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to memory."""
        self.add_message(Message.assistant_message(content))
    
    def add_tool_message(self, content: str, name: str) -> None:
        """Add a tool message to memory."""
        self.add_message(Message.tool_message(content, name))
    
    def get_messages(self) -> List[Message]:
        """Get all messages."""
        return self.messages
    
    def get_recent_messages(self, n: int) -> List[Message]:
        """Get the n most recent messages."""
        return self.messages[-n:] if n < len(self.messages) else self.messages
    
    def get_last_message(self) -> Optional[Message]:
        """Get the last message."""
        return self.messages[-1] if self.messages else None
    
    def get_last_user_message(self) -> Optional[Message]:
        """Get the last user message."""
        for message in reversed(self.messages):
            if message.role == "user":
                return message
        return None
    
    def get_last_assistant_message(self) -> Optional[Message]:
        """Get the last assistant message."""
        for message in reversed(self.messages):
            if message.role == "assistant":
                return message
        return None
    
    def clear(self) -> None:
        """Clear all messages."""
        self.messages = []
    
    def _trim_memory(self) -> None:
        """Trim memory to max_messages."""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]