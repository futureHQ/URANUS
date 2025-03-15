import asyncio
import argparse
import sys
from pathlib import Path

from uranus.agent.reactive_agent import ReactiveAgent
from uranus.tool.system_tool import SystemInfoTool
from uranus.tool.file_operations import FileOperationsTool
from uranus.tool.browser_tool import BrowserTool
from uranus.tool.file_saver import FileSaverTool
from uranus.tool.python_execute import PythonExecuteTool
from uranus.tool.terminal import TerminalTool
from uranus.tool.terminate import TerminateTool
from uranus.tool.web_search import WebSearchTool
from uranus.tool.browser_use_tool import BrowserUseTool
from uranus.core.logger import logger


async def interactive_cli(agent):
    """Run an interactive CLI session with the agent."""
    print("Welcome to Uranus! Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
                
            response = await agent.run(user_input)
            print(f"\nUranus: {response}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print(f"Error: {str(e)}")


async def main(input_text=None):
    """Main entry point for the application."""
    # Create a reactive agent
    agent = ReactiveAgent(
        name="Uranus",
        description="A helpful assistant that can perform various tasks.",
        system_prompt="You are Uranus, a helpful AI assistant that can perform various tasks including providing system information, file operations, web browsing, executing Python code, and more.",
        next_step_prompt="What would you like me to do next?"
    )
    
    # Register tools
    agent.tools.register(SystemInfoTool())
    agent.tools.register(FileOperationsTool())
    agent.tools.register(BrowserTool())
    agent.tools.register(FileSaverTool())
    agent.tools.register(PythonExecuteTool())
    agent.tools.register(TerminalTool())
    agent.tools.register(TerminateTool())
    
    # Register BrowserUseTool
    try:
        agent.tools.register(BrowserUseTool())
    except Exception as e:
        logger.warning(f"Could not register BrowserUseTool: {str(e)}")
    
    # Register WebSearchTool if it's implemented
    try:
        agent.tools.register(WebSearchTool())
    except Exception as e:
        logger.warning(f"Could not register WebSearchTool: {str(e)}")
    
    if input_text:
        # Run once with the provided input
        response = await agent.run(input_text)
        print(f"Uranus: {response}")
    else:
        # Run interactive CLI
        await interactive_cli(agent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Uranus CLI")
    parser.add_argument("--input", type=str, help="Input text to process")
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.input))
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)