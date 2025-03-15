from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field

from uranus.core.llm import LLM
from uranus.schema.memory import Memory
from uranus.schema.state import AgentState
from uranus.tool.tool_registry import ToolRegistry


class BaseAgent(BaseModel, ABC):
    """Base class for all agents."""
    
    # Add model configuration to allow arbitrary types
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    name: str
    description: str
    system_prompt: str
    llm: LLM = Field(default_factory=LLM)
    memory: Memory = Field(default_factory=Memory)
    tools: ToolRegistry = Field(default_factory=ToolRegistry)
    state: AgentState = AgentState.IDLE
    max_iterations: int = 10
    current_iteration: int = 0
    
    @abstractmethod
    async def next_step(self, input_text: str) -> str:
        """Determine the next step for the agent.
        
        Args:
            input_text: The input text to process.
            
        Returns:
            str: The next step to take.
        """
        pass
    
    async def run(self, input_text: str) -> str:
        """Run the agent with the given input.
        
        Args:
            input_text: The input text to process.
            
        Returns:
            str: The final result after running the agent.
        """
        self.state = "RUNNING"
        
        try:
            # For direct tool calls like system status, we only need to call next_step once
            if any(keyword in input_text.lower() for keyword in ["system status", "system info", "system information"]):
                return await self.next_step(input_text)
            
            # For regular queries, use the iterative approach
            response = await self.next_step(input_text)
            self.state = "IDLE"
            return response
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}.run: {str(e)}")
            self.state = "ERROR"
            return f"Error: {str(e)}"