from typing import Dict, List, Optional, Any, Callable, Type
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    """Result of a tool execution."""
    success: bool = True
    output: str = ""
    data: Optional[Dict[str, Any]] = None

class ToolError(Exception):
    """Error raised by tools."""
    pass

class BaseTool(BaseModel):
    """Base class for all tools."""
    name: str
    description: str
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with the given parameters."""
        raise NotImplementedError("Tool must implement execute method")
    
    def to_param(self) -> Dict[str, Any]:
        """Convert tool to a parameter dict for LLM API."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema()
            }
        }
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for this tool."""
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

class ToolRegistry(BaseModel):
    """Registry of available tools."""
    tools: Dict[str, BaseTool] = Field(default_factory=dict)
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool
    
    def get_tools_description(self) -> str:
        """Get a formatted description of all registered tools."""
        descriptions = []
        for tool_name, tool in self.tools.items():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    def get(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())
    
    def to_params(self) -> List[Dict[str, Any]]:
        """Convert all tools to parameters for LLM API."""
        return [tool.to_param() for tool in self.tools.values()]
    
    async def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get(name)
        if not tool:
            return ToolResult(
                success=False,
                output=f"Tool '{name}' not found. Available tools: {', '.join(self.list_tools())}"
            )
        
        try:
            return await tool.execute(**kwargs)
        except ToolError as e:
            return ToolResult(success=False, output=str(e))
        except Exception as e:
            return ToolResult(success=False, output=f"Error executing tool '{name}': {str(e)}")