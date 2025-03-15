import pytest
import os
import asyncio
from uranus.agent.reactive_agent import ReactiveAgent
from uranus.tool.system_tool import SystemInfoTool
from uranus.core.llm import LLM
from uranus.core.config import Config


# Use a marker instead of skip to make it easier to run selectively
pytestmark = pytest.mark.skipif(
    "OPENAI_API_KEY" not in os.environ,
    reason="Requires OPENAI_API_KEY environment variable"
)


@pytest.mark.asyncio
async def test_with_real_api():
    """Test using a real OpenAI API key."""
    # Create a reactive agent
    agent = ReactiveAgent(
        name="TestAgent",
        description="A test agent using real OpenAI API",
        system_prompt="You are a helpful assistant. Answer briefly and concisely.",
        next_step_prompt="What else would you like to know?"
    )
    
    # Register a tool
    agent.tools.register(SystemInfoTool())
    
    # Run the agent with a simple query
    result = await agent.run("What's the current date and time?")
    
    # Print the result
    print(f"Response: {result}")
    
    # Check that we got a non-empty response
    assert result and len(result) > 0