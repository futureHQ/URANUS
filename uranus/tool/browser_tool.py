import asyncio
from typing import Optional, Dict, Any, List
import webbrowser
from urllib.parse import quote_plus

from uranus.tool.tool_registry import BaseTool, ToolResult, ToolError
from uranus.core.logger import logger

class BrowserTool(BaseTool):
    """Tool for browser operations."""
    
    name: str = "browser"
    description: str = "A tool for performing browser operations like searching the web, navigating to URLs, and more."
    
    async def execute(
        self, 
        action: str, 
        url: Optional[str] = None, 
        query: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        """Execute browser operations.
        
        Args:
            action: The action to perform (navigate, search)
            url: The URL to navigate to
            query: The search query for search action
            **kwargs: Additional arguments
            
        Returns:
            ToolResult: The result of the operation
        """
        try:
            logger.info(f"Executing browser action: {action}")
            
            if action == "navigate":
                if not url:
                    return ToolResult(success=False, output="URL is required for navigation")
                
                # Add http:// prefix if missing
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                
                # Open URL in default browser
                webbrowser.open(url)
                return ToolResult(
                    success=True,
                    output=f"Opened {url} in browser"
                )
                
            elif action == "search":
                if not query:
                    return ToolResult(success=False, output="Query is required for search")
                
                # Encode the query for URL
                encoded_query = quote_plus(query)
                search_url = f"https://www.google.com/search?q={encoded_query}"
                
                # Open search URL in default browser
                webbrowser.open(search_url)
                return ToolResult(
                    success=True,
                    output=f"Searched for '{query}' in browser"
                )
                
            else:
                return ToolResult(
                    success=False,
                    output=f"Unknown action: {action}. Supported actions: navigate, search"
                )
                
        except Exception as e:
            logger.error(f"Error executing browser tool: {str(e)}")
            return ToolResult(
                success=False,
                output=f"Error executing browser tool: {str(e)}"
            )
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["navigate", "search"],
                    "description": "The browser action to perform"
                },
                "url": {
                    "type": "string",
                    "description": "URL for navigation action"
                },
                "query": {
                    "type": "string",
                    "description": "Search query for search action"
                }
            },
            "required": ["action"]
        }