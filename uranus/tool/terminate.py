from typing import Dict, Any

from uranus.tool.tool_registry import BaseTool, ToolResult


class TerminateTool(BaseTool):
    """Tool for terminating the agent interaction."""
    
    name: str = "terminate"
    description: str = "Terminate the interaction when the request is met or if the assistant cannot proceed further with the task."
    
    async def execute(
        self,
        status: str
    ) -> ToolResult:
        """
        Terminate the interaction.
        
        Args:
            status: The finish status of the interaction (success or failure)
            
        Returns:
            ToolResult: The result of the termination
        """
        return ToolResult(
            success=True,
            output=f"The interaction has been completed with status: {status}"
        )
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "The finish status of the interaction.",
                    "enum": ["success", "failure"]
                }
            },
            "required": ["status"]
        }