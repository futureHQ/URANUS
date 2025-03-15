from typing import Dict, List, Optional, Any

from pydantic import Field

from uranus.agent.base_agent import BaseAgent
from uranus.schema.message import Message, MessageRole
from uranus.core.logger import logger


class ReactiveAgent(BaseAgent):
    """A reactive agent that can reason, act, and observe."""
    
    next_step_prompt: str = "What would you like me to do next?"
    
    async def next_step(self, input_text: str) -> str:
        """Determine the next step for the agent.
        
        Args:
            input_text: The input text to process.
            
        Returns:
            str: The next step to take.
        """
        # Add the input to memory
        self.memory.add_message(Message(role=MessageRole.USER, content=input_text))
        
        # Get available tools
        tools_params = self.tools.to_params()
        
        try:
            # Directly handle system status queries
            if any(keyword in input_text.lower() for keyword in ["system status", "system info", "system information"]):
                logger.info("Detected system status query, using SystemInfoTool directly")
                system_tool = self.tools.get("system_info")
                if system_tool:
                    tool_result = await system_tool.execute()
                    if tool_result.success:
                        tool_response = f"Here's the current system status:\n\n{tool_result.output}"
                        self.memory.add_message(Message(role=MessageRole.ASSISTANT, content=tool_response))
                        return tool_response
            
            # Handle browser search queries
            if input_text.lower().startswith("search "):
                logger.info("Detected browser search query")
                browser_tool = self.tools.get("browser")
                if browser_tool:
                    search_term = input_text[7:].strip()  # Remove "search " prefix
                    logger.info(f"Searching for: {search_term}")
                    tool_result = await browser_tool.execute(action="search", query=search_term)
                    if tool_result.success:
                        tool_response = f"I've searched for '{search_term}' in the browser."
                        self.memory.add_message(Message(role=MessageRole.ASSISTANT, content=tool_response))
                        return tool_response
                    else:
                        return f"Failed to search: {tool_result.output}"
                else:
                    return "Browser tool is not available. Please make sure it's properly registered."
            
            # Handle browser navigate commands
            if input_text.lower().startswith("navigate to ") or input_text.lower().startswith("go to "):
                logger.info("Detected browser navigation request")
                browser_tool = self.tools.get("browser")
                if browser_tool:
                    # Extract URL from command
                    if input_text.lower().startswith("navigate to "):
                        url = input_text[11:].strip()
                    else:  # "go to "
                        url = input_text[6:].strip()
                    
                    logger.info(f"Navigating to: {url}")
                    tool_result = await browser_tool.execute(action="navigate", url=url)
                    if tool_result.success:
                        tool_response = f"I've opened {url} in the browser."
                        self.memory.add_message(Message(role=MessageRole.ASSISTANT, content=tool_response))
                        return tool_response
                    else:
                        return f"Failed to navigate: {tool_result.output}"
                else:
                    return "Browser tool is not available. Please make sure it's properly registered."
            
            # Handle browser.open_url commands
            if input_text.lower().startswith("browser.open_url"):
                logger.info("Detected browser.open_url command")
                browser_tool = self.tools.get("browser_use")
                if browser_tool:
                    # Extract URL from command
                    parts = input_text.split(" ", 1)
                    if len(parts) > 1:
                        url = parts[1].strip()
                        logger.info(f"Opening URL in browser: {url}")
                        
                        # Use the browser_use tool to navigate to the URL
                        tool_result = await browser_tool.execute(action="navigate", url=url)
                        if tool_result.success:
                            tool_response = f"Navigated to {url} in the browser."
                            self.memory.add_message(Message(role=MessageRole.ASSISTANT, content=tool_response))
                            return tool_response
                        else:
                            return f"Failed to open URL: {tool_result.output}"
                    else:
                        return "Please specify a URL to open."
                else:
                    return "Browser_use tool is not available. Please make sure it's properly registered."
            
            # Handle terminal commands like ls, echo, etc.
            if (input_text.lower() in ["ls", "pwd", "whoami", "date", "hostname"] or 
                input_text.lower().startswith(("echo ", "cat ", "grep ", "find ", "ps ", "mkdir ", "touch "))):
                logger.info(f"Detected terminal command: {input_text}")
                terminal_tool = self.tools.get("terminal")
                if terminal_tool:
                    tool_result = await terminal_tool.execute(command=input_text)
                    if tool_result.success:
                        tool_response = tool_result.output
                        if not tool_response:
                            tool_response = "(Command executed successfully with no output)"
                        self.memory.add_message(Message(role=MessageRole.ASSISTANT, content=tool_response))
                        return tool_response
                    else:
                        return f"Failed to execute command: {tool_result.output}"
                else:
                    return "Terminal tool is not available. Please make sure it's properly registered."
            
            # Handle file creation commands
            if input_text.lower().startswith(("create file", "make a file", "make file")):
                logger.info("Detected file creation request")
                file_tool = self.tools.get("file_operations")
                if file_tool:
                    # Extract filename from command
                    parts = input_text.lower().split(" file ", 1)
                    if len(parts) > 1:
                        filename = parts[1].strip()
                        logger.info(f"Creating file: {filename}")
                        
                        # Create the file
                        tool_result = await file_tool.execute(action="create", name=filename, content="")
                        if tool_result.success:
                            tool_response = f"Created file: {filename}"
                            self.memory.add_message(Message(role=MessageRole.ASSISTANT, content=tool_response))
                            return tool_response
                        else:
                            return f"Failed to create file: {tool_result.output}"
                    else:
                        return "Please specify a filename."
                else:
                    return "File operations tool is not available. Please make sure it's properly registered."
            
            # Handle file operations commands
            if input_text.lower().startswith(("list file", "list directory")) or input_text.lower() == "ls":
                logger.info("Detected file listing request")
                file_tool = self.tools.get("file_operations")
                if file_tool:
                    # Default to current directory if no path specified
                    path = "."
                    if " " in input_text and not input_text.lower() == "ls":
                        # Extract path from command
                        parts = input_text.split(" ", 2)
                        if len(parts) > 2:
                            path = parts[2].strip()
                    
                    tool_result = await file_tool.execute(action="list", path=path)
                    if tool_result.success:
                        files = tool_result.data.get("files", [])
                        if files:
                            file_list = "\n".join(files)
                            tool_response = f"Files in {path}:\n\n{file_list}"
                        else:
                            tool_response = f"No files found in {path}"
                        self.memory.add_message(Message(role=MessageRole.ASSISTANT, content=tool_response))
                        return tool_response
                    else:
                        return f"Failed to list files: {tool_result.output}"
                else:
                    return "File operations tool is not available. Please make sure it's properly registered."
            
            # Create a system prompt that includes tool information
            enhanced_system_prompt = f"{self.system_prompt}\n\nYou have access to the following tools:\n{self.tools.get_tools_description()}\n\nTo use a tool, respond with the tool name and parameters in a structured format."
            
            # Call the LLM with the current memory and tools
            response = await self.llm.ask(
                messages=self.memory.messages,
                system_prompt=enhanced_system_prompt
            )
            
            # Add the response to memory
            self.memory.add_message(Message(role=MessageRole.ASSISTANT, content=response))
            
            # Return the response
            return response
            
        except Exception as e:
            logger.error(f"Error in ReactiveAgent.next_step: {str(e)}")
            self.state = "ERROR"
            return f"Error: {str(e)}"