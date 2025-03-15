import os
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel

from uranus.schema.message import Message
from uranus.core.config import Config
from uranus.core.logger import logger


class LLMResponse(BaseModel):
    """Response from an LLM."""
    content: str
    tool_calls: Optional[List[Any]] = None


class LLM:
    """LLM client for Uranus."""
    
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    _instances: Dict[str, "LLM"] = {}
    
    def __new__(cls, config_name: str = "default"):
        """Singleton pattern implementation."""
        if config_name not in cls._instances:
            instance = super().__new__(cls)
            instance.__init__(config_name)
            cls._instances[config_name] = instance
        return cls._instances[config_name]
    
    def __init__(self, config_name: str = "default"):
        """Initialize the LLM with configuration."""
        if hasattr(self, "initialized"):
            return
            
        self.config = Config().llm.get(config_name, {})
        self.model = self.config.get("model", "gpt-3.5-turbo")
        self.api_key = self.config.get("api_key", os.environ.get("OPENAI_API_KEY", ""))
        self.api_base = self.config.get("base_url", "https://api.openai.com/v1")
        self.max_tokens = self.config.get("max_tokens", 4096)
        self.temperature = self.config.get("temperature", 0.7)
        
        # Initialize client based on configuration
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            self.initialized = True
            logger.info(f"LLM initialized with model: {self.model}")
        except ImportError:
            logger.error("Failed to import OpenAI. Please install it with 'pip install openai'")
            self.initialized = False
    
    async def ask(
        self, 
        messages: List[Message], 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Ask the LLM a question.
        
        Args:
            messages: List of messages to send to the LLM.
            system_prompt: Optional system prompt to prepend.
            temperature: Optional temperature override.
            
        Returns:
            str: The LLM's response.
        """
        if not self.initialized:
            return "LLM not initialized properly."
            
        formatted_messages = self._format_messages(messages, system_prompt)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in LLM.ask: {str(e)}")
            return f"Error: {str(e)}"
    
    def _format_messages(
        self, 
        messages: List[Message], 
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Format messages for the LLM API.
        
        Args:
            messages: List of messages to format.
            system_prompt: Optional system prompt to prepend.
            
        Returns:
            List[Dict[str, str]]: Formatted messages.
        """
        formatted = []
        
        # Add system prompt if provided
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
            
        # Add all other messages
        for message in messages:
            formatted.append(message.to_dict())
            
        return formatted