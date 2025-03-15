import pytest
import asyncio
import os
from pathlib import Path
from uranus.agent.reactive_agent import ReactiveAgent
from uranus.tool.system_tool import SystemInfoTool
from uranus.tool.file_operations import FileOperationsTool

# Fix the import path - use a relative import instead of an absolute one
from .mocks.mock_llm import MockLLM


@pytest.mark.asyncio
async def test_full_conversation():
    """Test a full conversation with the agent."""
    # Create a reactive agent
    agent = ReactiveAgent(
        name="Uranus",
        description="A helpful assistant that can perform various tasks.",
        system_prompt="You are Uranus, a helpful AI assistant that can perform various tasks.",
        next_step_prompt="What would you like me to do next?"
    )
    
    # Replace the LLM with our mock
    agent.llm = MockLLM()
    
    # Register tools
    agent.tools.register(SystemInfoTool())
    agent.tools.register(FileOperationsTool())
    
    # Create a test workspace
    test_dir = Path.home() / "uranus_workspace" / "test_conversation"
    os.makedirs(test_dir, exist_ok=True)
    
    # Run a series of commands
    responses = []
    
    # First command: Get system info
    response1 = await agent.run("What's the current system status?")
    responses.append(response1)
    assert "System Information" in response1
    
    # Second command: Create a file
    response2 = await agent.run("Create a file called test_notes.txt with the content 'This is a test note'")
    responses.append(response2)
    
    # Third command: Read the file
    response3 = await agent.run("Read the content of test_notes.txt")
    responses.append(response3)
    assert "This is a test note" in response3
    
    # Fourth command: Delete the file
    response4 = await agent.run("Delete the test_notes.txt file")
    responses.append(response4)
    
    # Print the full conversation for debugging
    print("\n".join(responses))