import os
from pathlib import Path
import aiofiles

from uranus.tool.tool_registry import BaseTool, ToolResult, ToolError
from uranus.core.logger import logger


class FileSaverTool(BaseTool):
    """Tool for saving content to files."""
    
    name: str = "file_saver"
    description: str = "Save content to a local file at a specified path."
    
    # Set a safe base directory to prevent access to sensitive files
    base_dir: Path = Path.home() / "uranus_workspace"
    
    async def execute(
        self,
        content: str,
        file_path: str,
        mode: str = "w"
    ) -> ToolResult:
        """
        Save content to a file at the specified path.
        
        Args:
            content: The content to save to the file
            file_path: The path where the file should be saved
            mode: The file opening mode (w for write, a for append)
            
        Returns:
            ToolResult: The result of the operation
        """
        # Ensure base directory exists
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Resolve the full path and ensure it's within base_dir
        full_path = (self.base_dir / file_path).resolve()
        if not str(full_path).startswith(str(self.base_dir)):
            return ToolResult(
                success=False,
                output=f"Access denied: Path must be within {self.base_dir}"
            )
            
        try:
            # Ensure the directory exists
            directory = os.path.dirname(full_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
                
            # Write the content to the file
            async with aiofiles.open(full_path, mode=mode) as file:
                await file.write(content)
                
            return ToolResult(
                success=True,
                output=f"Content saved to {file_path}",
                data={"path": str(full_path)}
            )
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return ToolResult(
                success=False,
                output=f"Error saving file: {str(e)}"
            )
    
    def get_parameters_schema(self) -> dict:
        """Get the parameters schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The content to save to the file."
                },
                "file_path": {
                    "type": "string",
                    "description": "The path where the file should be saved, including filename and extension."
                },
                "mode": {
                    "type": "string",
                    "description": "The file opening mode. Default is 'w' for write. Use 'a' for append.",
                    "enum": ["w", "a"],
                    "default": "w"
                }
            },
            "required": ["content", "file_path"]
        }