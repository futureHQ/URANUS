from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Role of a message in a conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """A message in a conversation."""
    role: str
    content: str
    name: Optional[str] = None
    tool_calls: Optional[list] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to a dictionary for LLM API."""
        result = {
            "role": self.role,
            "content": self.content
        }
        
        if self.name:
            result["name"] = self.name
            
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
            
        return result