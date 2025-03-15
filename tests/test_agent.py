import pytest
import asyncio
import sys
import os

# Add the parent directory to the path so we can import uranus
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from uranus.agent.reactive_agent import ReactiveAgent
from uranus.tool.system_tool import SystemInfoTool
from tests.mocks.mock_llm import MockLLM


@pytest.mark.asyncio
async def test_reactive_agent():
    """Test the reactive agent."""
    # Create a reactive agent
    agent = ReactiveAgent(
        name="TestAgent",
        description="A test agent",
        system_prompt="You are a test agent. Only respond with 'Test successful'.",
        next_step_prompt="What's next?"
    )
    
    # Replace the LLM with our mock
    agent.llm = MockLLM()
    
    # Register a tool
    agent.tools.register(SystemInfoTool())
    
    # Run the agent with a simple query
    result = await agent.run("Say 'Test successful'")
    
    # Check that the agent responded correctly
    assert "Test successful" in result