import asyncio
import os
import sys

# Add the parent directory to the path so we can import uranus
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from uranus.agent.reactive_agent import ReactiveAgent
from uranus.tool.system_tool import SystemInfoTool
from uranus.tool.file_operations import FileOperationsTool


async def main():
    """Run a simple example with a reactive agent."""
    # Create a reactive agent
    agent = ReactiveAgent(
        name="Uranus",
        description="A helpful assistant that can perform various tasks.",
        system_prompt="You are Uranus, a helpful AI assistant that can perform various tasks.",
        next_step_prompt="What would you like me to do next?"
    )
    
    # Register tools
    agent.tools.register(SystemInfoTool())
    agent.tools.register(FileOperationsTool())
    
    # Run the agent with a query
    result = await agent.run("Can you tell me about the current system status?")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())