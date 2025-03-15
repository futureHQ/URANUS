import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from uranus.tool.tool_registry import BaseTool, ToolResult, ToolError


class FileOperationsTool(BaseTool):
    """Tool for file system operations."""
    
    name: str = "file_operations"
    description: str = "Perform file operations like reading, writing, listing files, etc."
    
    # Set a safe base directory to prevent access to sensitive files
    base_dir: Path = Path.home() / "uranus_workspace"
    
    async def execute(
        self,
        operation: str,
        path: str,
        content: Optional[str] = None,
        recursive: bool = False
    ) -> ToolResult:
        """
        Execute a file operation.
        
        Args:
            operation: The operation to perform (read, write, list, exists, delete)
            path: The file or directory path (relative to base_dir)
            content: Content to write (for write operation)
            recursive: Whether to operate recursively (for list/delete operations)
            
        Returns:
            ToolResult: The result of the operation
        """
        # Ensure base directory exists
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Resolve the full path and ensure it's within base_dir
        full_path = (self.base_dir / path).resolve()
        if not str(full_path).startswith(str(self.base_dir)):
            raise ToolError(f"Access denied: Path must be within {self.base_dir}")
            
        try:
            if operation == "read":
                return await self._read_file(full_path)
            elif operation == "write":
                return await self._write_file(full_path, content)
            elif operation == "list":
                return await self._list_files(full_path, recursive)
            elif operation == "exists":
                return await self._check_exists(full_path)
            elif operation == "delete":
                return await self._delete_file(full_path, recursive)
            else:
                raise ToolError(f"Unknown operation: {operation}")
        except ToolError as e:
            raise e
        except Exception as e:
            raise ToolError(f"Error during file operation: {str(e)}")
    
    async def _read_file(self, path: Path) -> ToolResult:
        """Read a file."""
        if not path.exists():
            raise ToolError(f"File not found: {path}")
        if not path.is_file():
            raise ToolError(f"Not a file: {path}")
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            return ToolResult(
                success=True,
                output=f"File content:\n\n{content}",
                data={"content": content, "path": str(path)}
            )
        except UnicodeDecodeError:
            raise ToolError(f"Cannot read binary file: {path}")
    
    async def _write_file(self, path: Path, content: Optional[str]) -> ToolResult:
        """Write to a file."""
        if content is None:
            raise ToolError("Content is required for write operation")
            
        # Create parent directories if they don't exist
        os.makedirs(path.parent, exist_ok=True)
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return ToolResult(
            success=True,
            output=f"Successfully wrote {len(content)} characters to {path}",
            data={"path": str(path), "size": len(content)}
        )
    
    async def _list_files(self, path: Path, recursive: bool) -> ToolResult:
        """List files in a directory."""
        if not path.exists():
            raise ToolError(f"Directory not found: {path}")
        if not path.is_dir():
            raise ToolError(f"Not a directory: {path}")
            
        files = []
        
        if recursive:
            for item in path.glob("**/*"):
                files.append({
                    "path": str(item.relative_to(self.base_dir)),
                    "type": "file" if item.is_file() else "directory",
                    "size": item.stat().st_size if item.is_file() else None
                })
        else:
            for item in path.iterdir():
                files.append({
                    "path": str(item.relative_to(self.base_dir)),
                    "type": "file" if item.is_file() else "directory",
                    "size": item.stat().st_size if item.is_file() else None
                })
                
        # Format output
        output = f"Contents of {path}:\n\n"
        for item in files:
            type_indicator = "[DIR]" if item["type"] == "directory" else "[FILE]"
            size_info = f" ({item['size']} bytes)" if item["size"] is not None else ""
            output += f"{type_indicator} {item['path']}{size_info}\n"
            
        return ToolResult(
            success=True,
            output=output,
            data={"path": str(path), "files": files}
        )
    
    async def _check_exists(self, path: Path) -> ToolResult:
        """Check if a file or directory exists."""
        exists = path.exists()
        type_str = ""
        
        if exists:
            if path.is_file():
                type_str = "file"
            elif path.is_dir():
                type_str = "directory"
                
        return ToolResult(
            success=True,
            output=f"{'Path exists' if exists else 'Path does not exist'}: {path} {'(' + type_str + ')' if type_str else ''}",
            data={"exists": exists, "type": type_str, "path": str(path)}
        )
    
    async def _delete_file(self, path: Path, recursive: bool) -> ToolResult:
        """Delete a file or directory."""
        if not path.exists():
            raise ToolError(f"Path not found: {path}")
            
        if path.is_file():
            os.remove(path)
            return ToolResult(
                success=True,
                output=f"File deleted: {path}",
                data={"path": str(path), "type": "file"}
            )
        elif path.is_dir():
            if not recursive:
                raise ToolError(f"Cannot delete directory without recursive=True: {path}")
                
            import shutil
            shutil.rmtree(path)
            return ToolResult(
                success=True,
                output=f"Directory deleted: {path}",
                data={"path": str(path), "type": "directory"}
            )
        else:
            raise ToolError(f"Unknown file type: {path}")
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read", "write", "list", "exists", "delete"],
                    "description": "The operation to perform"
                },
                "path": {
                    "type": "string",
                    "description": "The file or directory path (relative to base_dir)"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write (for write operation)"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to operate recursively (for list/delete operations)",
                    "default": False
                }
            },
            "required": ["operation", "path"]
        }