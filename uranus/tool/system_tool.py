import platform
import psutil
from typing import Dict, Any, Optional

from uranus.tool.tool_registry import BaseTool, ToolResult


class SystemInfoTool(BaseTool):
    """Tool for getting system information."""
    
    name: str = "system_info"
    description: str = "Get information about the system, such as CPU, memory, disk usage, etc."
    
    async def execute(
        self, 
        info_type: Optional[str] = "all"
    ) -> ToolResult:
        """
        Execute the tool with the given parameters.
        
        Args:
            info_type: Type of information to get (all, cpu, memory, disk, platform)
            
        Returns:
            ToolResult: The result of the execution.
        """
        result = {}
        
        if info_type in ["all", "platform"]:
            result["platform"] = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
            }
            
        if info_type in ["all", "cpu"]:
            result["cpu"] = {
                "physical_cores": psutil.cpu_count(logical=False),
                "total_cores": psutil.cpu_count(logical=True),
                "usage_percent": psutil.cpu_percent(interval=1),
                "frequency": {
                    "current": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                    "min": psutil.cpu_freq().min if psutil.cpu_freq() else None,
                    "max": psutil.cpu_freq().max if psutil.cpu_freq() else None,
                },
            }
            
        if info_type in ["all", "memory"]:
            memory = psutil.virtual_memory()
            result["memory"] = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
            }
            
        if info_type in ["all", "disk"]:
            disk = psutil.disk_usage("/")
            result["disk"] = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
            }
            
        # Format the output as a string
        output = "System Information:\n"
        for category, info in result.items():
            output += f"\n{category.upper()}:\n"
            for key, value in info.items():
                if isinstance(value, dict):
                    output += f"  {key}:\n"
                    for subkey, subvalue in value.items():
                        output += f"    {subkey}: {subvalue}\n"
                else:
                    output += f"  {key}: {value}\n"
                    
        return ToolResult(
            success=True,
            output=output,
            data=result
        )
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "info_type": {
                    "type": "string",
                    "enum": ["all", "cpu", "memory", "disk", "platform"],
                    "description": "Type of information to get"
                }
            },
            "required": []
        }