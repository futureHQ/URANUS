import json
from typing import Dict, Any, Optional, List
import aiohttp

from uranus.tool.tool_registry import BaseTool, ToolResult, ToolError


class WebSearchTool(BaseTool):
    """Tool for searching the web."""
    
    name: str = "web_search"
    description: str = "Search the web for information on a given query."
    
    async def execute(
        self, 
        query: str,
        num_results: Optional[int] = 5
    ) -> ToolResult:
        """
        Execute the web search with the given query.
        
        Args:
            query: The search query
            num_results: Number of results to return (default: 5)
            
        Returns:
            ToolResult: The search results
        """
        if not query:
            raise ToolError("Query parameter is required")
            
        try:
            # Using SerpAPI-like service (you'll need to replace with your actual API)
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": query,
                    "num": num_results,
                    "api_key": "your-serpapi-key-here"  # Replace with env var or config
                }
                
                async with session.get(
                    "https://serpapi.com/search", 
                    params=params
                ) as response:
                    if response.status != 200:
                        raise ToolError(f"Search API returned status code {response.status}")
                        
                    data = await response.json()
                    
            # Process results
            organic_results = data.get("organic_results", [])
            formatted_results = []
            
            for result in organic_results[:num_results]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
                
            # Create a readable output
            output = f"Search results for '{query}':\n\n"
            for i, result in enumerate(formatted_results, 1):
                output += f"{i}. {result['title']}\n"
                output += f"   {result['link']}\n"
                output += f"   {result['snippet']}\n\n"
                
            return ToolResult(
                success=True,
                output=output,
                data={"query": query, "results": formatted_results}
            )
            
        except ToolError as e:
            raise e
        except Exception as e:
            raise ToolError(f"Error during web search: {str(e)}")
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }