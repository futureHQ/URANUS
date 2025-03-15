"""Mock LLM implementation for testing."""
from typing import List, Optional, Dict, Any

from uranus.core.llm import LLM, LLMResponse
from uranus.schema.message import Message


class MockLLM:
    """Mock LLM for testing purposes."""
    
    def __init__(self, config_name: str = "default"):
        """Initialize the mock LLM."""
        # Skip the parent class initialization
        self.initialized = True
        self.responses = {
            "Say 'Test successful'": "Test successful",
            "What's the current system status?": "System Information:\n\nCPU: Mock CPU\nMEMORY: Mock Memory\nDISK: Mock Disk\nPLATFORM: Mock Platform",
            "Create a file called test_notes.txt with the content 'This is a test note'": "I've created the file test_notes.txt with the content 'This is a test note'.",
            "Read the content of test_notes.txt": "The content of test_notes.txt is: This is a test note",
            "Delete the test_notes.txt file": "I've deleted the file test_notes.txt."
        }
    
    async def ask(
        self, 
        messages: List[Message], 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Return a predefined response based on the last user message.
        
        Args:
            messages: List of messages to send to the LLM.
            system_prompt: Optional system prompt to prepend.
            temperature: Optional temperature override.
            
        Returns:
            str: The predefined response.
        """
        # Get the last user message
        user_messages = [m for m in messages if m.role == "user"]
        if not user_messages:
            return "No user message found."
        
        last_user_message = user_messages[-1].content
        
        # Return a predefined response or a default one
        return self.responses.get(
            last_user_message, 
            f"Mock response to: {last_user_message}"
        )