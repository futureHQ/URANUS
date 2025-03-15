import asyncio
import json
from typing import Optional, Dict, Any

from pydantic import Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from browser_use import Browser as BrowserUseBrowser
from browser_use import BrowserConfig
from browser_use.browser.context import BrowserContext, BrowserContextConfig
from browser_use.dom.service import DomService

from uranus.tool.tool_registry import BaseTool, ToolResult
from uranus.core.logger import logger


MAX_LENGTH = 2000

class BrowserUseTool(BaseTool):
    """Tool for advanced browser interactions."""
    
    name: str = "browser_use"
    description: str = """
    Interact with a web browser to perform various actions such as navigation, element interaction,
    content extraction, and tab management. Supported actions include:
    - 'navigate': Go to a specific URL
    - 'click': Click an element by index
    - 'input_text': Input text into an element
    - 'screenshot': Capture a screenshot
    - 'get_html': Get page HTML content
    - 'get_text': Get text content of the page
    - 'execute_js': Execute JavaScript code
    - 'scroll': Scroll the page
    - 'switch_tab': Switch to a specific tab
    - 'new_tab': Open a new tab
    - 'close_tab': Close the current tab
    - 'refresh': Refresh the current page
    """
    
    # Use Field with default_factory for lock to make it compatible with Pydantic
    lock: asyncio.Lock = Field(default_factory=asyncio.Lock)
    browser: Optional[BrowserUseBrowser] = Field(default=None, exclude=True)
    context: Optional[BrowserContext] = Field(default=None, exclude=True)
    dom_service: Optional[DomService] = Field(default=None, exclude=True)
    
    # Set model configuration to allow arbitrary types
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    async def _ensure_browser_initialized(self) -> BrowserContext:
        """Ensure browser and context are initialized."""
        if self.browser is None:
            browser_config_kwargs = {"headless": False, "disable_security": True}
            self.browser = BrowserUseBrowser(BrowserConfig(**browser_config_kwargs))

        if self.context is None:
            context_config = BrowserContextConfig()
            self.context = await self.browser.new_context(context_config)
            self.dom_service = DomService(await self.context.get_current_page())

        return self.context
    
    async def execute(
        self,
        action: str,
        url: Optional[str] = None,
        index: Optional[int] = None,
        text: Optional[str] = None,
        script: Optional[str] = None,
        scroll_amount: Optional[int] = None,
        tab_id: Optional[int] = None
    ) -> ToolResult:
        """
        Execute a browser action.
        
        Args:
            action: The action to perform (navigate, click, etc.)
            url: URL for navigation
            index: Element index for clicking or input
            text: Text for input
            script: JavaScript to execute
            scroll_amount: Amount to scroll
            tab_id: Tab ID for switching tabs
            
        Returns:
            ToolResult: The result of the execution
        """
        async with self.lock:
            try:
                logger.info(f"Executing browser action: {action}")
                
                context = await self._ensure_browser_initialized()
                
                if action == "navigate":
                    if not url:
                        return ToolResult(
                            success=False,
                            output="URL is required for 'navigate' action"
                        )
                    await context.navigate_to(url)
                    return ToolResult(
                        success=True,
                        output=f"Navigated to {url}"
                    )
                
                elif action == "click":
                    if index is None:
                        return ToolResult(
                            success=False,
                            output="Index is required for 'click' action"
                        )
                    element = await context.get_dom_element_by_index(index)
                    if not element:
                        return ToolResult(
                            success=False,
                            output=f"Element with index {index} not found"
                        )
                    download_path = await context._click_element_node(element)
                    output = f"Clicked element at index {index}"
                    if download_path:
                        output += f" - Downloaded file to {download_path}"
                    return ToolResult(
                        success=True,
                        output=output
                    )
                
                elif action == "input_text":
                    if index is None or not text:
                        return ToolResult(
                            success=False,
                            output="Index and text are required for 'input_text' action"
                        )
                    element = await context.get_dom_element_by_index(index)
                    if not element:
                        return ToolResult(
                            success=False,
                            output=f"Element with index {index} not found"
                        )
                    await context._input_text_element_node(element, text)
                    return ToolResult(
                        success=True,
                        output=f"Input '{text}' into element at index {index}"
                    )
                
                elif action == "get_html":
                    html = await context.get_page_html()
                    truncated = html[:MAX_LENGTH] + "..." if len(html) > MAX_LENGTH else html
                    return ToolResult(
                        success=True,
                        output=truncated
                    )
                
                elif action == "get_text":
                    text = await context.execute_javascript("document.body.innerText")
                    return ToolResult(
                        success=True,
                        output=text
                    )
                
                elif action == "execute_js":
                    if not script:
                        return ToolResult(
                            success=False,
                            output="Script is required for 'execute_js' action"
                        )
                    result = await context.execute_javascript(script)
                    return ToolResult(
                        success=True,
                        output=str(result)
                    )
                
                elif action == "scroll":
                    if scroll_amount is None:
                        return ToolResult(
                            success=False,
                            output="Scroll amount is required for 'scroll' action"
                        )
                    await context.execute_javascript(f"window.scrollBy(0, {scroll_amount});")
                    direction = "down" if scroll_amount > 0 else "up"
                    return ToolResult(
                        success=True,
                        output=f"Scrolled {direction} by {abs(scroll_amount)} pixels"
                    )
                
                else:
                    return ToolResult(
                        success=False,
                        output=f"Unsupported action: {action}"
                    )
                    
            except Exception as e:
                logger.error(f"Error executing browser action: {str(e)}")
                return ToolResult(
                    success=False,
                    output=f"Error executing browser action: {str(e)}"
                )
    
    async def cleanup(self):
        """Clean up browser resources."""
        async with self.lock:
            if self.context is not None:
                await self.context.close()
                self.context = None
                self.dom_service = None
            if self.browser is not None:
                await self.browser.close()
                self.browser = None

    def __del__(self):
        """Ensure cleanup when object is destroyed."""
        if self.browser is not None or self.context is not None:
            try:
                asyncio.run(self.cleanup())
            except RuntimeError:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self.cleanup())
                loop.close()
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "navigate",
                        "click",
                        "input_text",
                        "screenshot",
                        "get_html",
                        "get_text",
                        "execute_js",
                        "scroll",
                        "switch_tab",
                        "new_tab",
                        "close_tab",
                        "refresh",
                    ],
                    "description": "The browser action to perform"
                },
                "url": {
                    "type": "string",
                    "description": "URL for navigation or new tab"
                },
                "index": {
                    "type": "integer",
                    "description": "Element index for clicking or input"
                },
                "text": {
                    "type": "string",
                    "description": "Text for input"
                },
                "script": {
                    "type": "string",
                    "description": "JavaScript to execute"
                },
                "scroll_amount": {
                    "type": "integer",
                    "description": "Pixels to scroll (positive for down, negative for up)"
                },
                "tab_id": {
                    "type": "integer",
                    "description": "Tab ID for switching tabs"
                }
            },
            "required": ["action"],
            "dependencies": {
                "navigate": ["url"],
                "click": ["index"],
                "input_text": ["index", "text"],
                "execute_js": ["script"],
                "switch_tab": ["tab_id"],
                "new_tab": ["url"],
                "scroll": ["scroll_amount"]
            }
        }