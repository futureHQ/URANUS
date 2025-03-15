import os
import asyncio
import shlex
from typing import Optional, Dict, Any

from pydantic import Field
from uranus.tool.tool_registry import BaseTool, ToolResult, ToolError
from uranus.core.logger import logger


class TerminalTool(BaseTool):
    """Tool for executing terminal commands."""
    
    name: str = "terminal"
    description: str = "Execute terminal commands on the system."
    
    # Class variables to maintain state
    current_path: str = os.getcwd()
    # Define lock as a field with default_factory
    lock: asyncio.Lock = Field(default_factory=asyncio.Lock)
    
    # Set model configuration to allow arbitrary types
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    async def execute(
        self,
        command: str
    ) -> ToolResult:
        """
        Execute a terminal command.
        
        Args:
            command: The command to execute
            
        Returns:
            ToolResult: The result of the execution
        """
        async with self.lock:
            try:
                logger.info(f"Executing command: {command}")
                
                # Split the command by & to handle multiple commands
                commands = [cmd.strip() for cmd in command.split("&") if cmd.strip()]
                final_output = ""
                final_error = ""
                
                for cmd in commands:
                    # Handle cd command specially to maintain state
                    if cmd.startswith("cd "):
                        path = cmd[3:].strip()
                        try:
                            # Handle relative paths
                            if not os.path.isabs(path):
                                path = os.path.join(self.current_path, path)
                            
                            # Resolve the path
                            path = os.path.abspath(path)
                            
                            # Check if the path exists
                            if not os.path.exists(path):
                                final_error += f"Directory not found: {path}\n"
                                continue
                                
                            # Change the current directory
                            os.chdir(path)
                            self.current_path = path
                            final_output += f"Changed directory to {path}\n"
                        except Exception as e:
                            final_error += f"Error changing directory: {str(e)}\n"
                    else:
                        # Execute the command
                        process = await asyncio.create_subprocess_shell(
                            cmd,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                            cwd=self.current_path
                        )
                        
                        stdout, stderr = await process.communicate()
                        
                        if stdout:
                            final_output += stdout.decode() + "\n"
                        if stderr:
                            final_error += stderr.decode() + "\n"
                
                return ToolResult(
                    success=True,
                    output=final_output.strip(),
                    data={
                        "error": final_error.strip(),
                        "current_path": self.current_path
                    }
                )
            except Exception as e:
                logger.error(f"Error executing command: {str(e)}")
                return ToolResult(
                    success=False,
                    output=f"Error executing command: {str(e)}"
                )
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The terminal command to execute."
                }
            },
            "required": ["command"]
        }