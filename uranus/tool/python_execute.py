import sys
import asyncio
from io import StringIO
import multiprocessing
from typing import Dict, Any

from uranus.tool.tool_registry import BaseTool, ToolResult, ToolError
from uranus.core.logger import logger


class PythonExecuteTool(BaseTool):
    """Tool for executing Python code."""
    
    name: str = "python_execute"
    description: str = "Executes Python code string. Note: Only print outputs are visible, function return values are not captured. Use print statements to see results."
    
    def _run_code(self, code: str, result_dict: dict, safe_globals: dict) -> None:
        """Run Python code in a separate process with restricted globals."""
        original_stdout = sys.stdout
        try:
            output_buffer = StringIO()
            sys.stdout = output_buffer
            exec(code, safe_globals, safe_globals)
            result_dict["observation"] = output_buffer.getvalue()
            result_dict["success"] = True
        except Exception as e:
            result_dict["observation"] = str(e)
            result_dict["success"] = False
        finally:
            sys.stdout = original_stdout
    
    async def execute(
        self,
        code: str,
        timeout: int = 5
    ) -> ToolResult:
        """
        Execute Python code with safety restrictions.
        
        Args:
            code: The Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            ToolResult: The result of the execution
        """
        # Create a safe globals dictionary
        safe_globals = {
            "__builtins__": {
                name: getattr(__builtins__, name)
                for name in dir(__builtins__)
                if name not in [
                    "open", "exec", "eval", "compile", 
                    "__import__", "input", "memoryview"
                ]
            },
            "print": print,
        }
        
        # Add common modules
        for module_name in ["math", "random", "datetime", "json", "re"]:
            try:
                module = __import__(module_name)
                safe_globals[module_name] = module
            except ImportError:
                pass
        
        # Use multiprocessing to execute code with timeout
        manager = multiprocessing.Manager()
        result_dict = manager.dict()
        result_dict["observation"] = ""
        result_dict["success"] = False
        
        process = multiprocessing.Process(
            target=self._run_code,
            args=(code, result_dict, safe_globals)
        )
        
        try:
            process.start()
            process.join(timeout)
            
            if process.is_alive():
                process.terminate()
                process.join()
                return ToolResult(
                    success=False,
                    output=f"Execution timed out after {timeout} seconds"
                )
            
            if result_dict["success"]:
                return ToolResult(
                    success=True,
                    output=result_dict["observation"]
                )
            else:
                return ToolResult(
                    success=False,
                    output=f"Error executing code: {result_dict['observation']}"
                )
                
        except Exception as e:
            logger.error(f"Error in PythonExecuteTool: {str(e)}")
            return ToolResult(
                success=False,
                output=f"Error: {str(e)}"
            )
        finally:
            if process.is_alive():
                process.terminate()
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute."
                },
                "timeout": {
                    "type": "integer",
                    "description": "Maximum execution time in seconds.",
                    "default": 5
                }
            },
            "required": ["code"]
        }