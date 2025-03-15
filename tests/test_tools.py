import pytest
import asyncio
from uranus.tool.tool_registry import ToolRegistry, BaseTool, ToolResult
from uranus.tool.system_tool import SystemInfoTool
from uranus.tool.file_operations import FileOperationsTool


@pytest.mark.asyncio
async def test_system_info_tool():
    """Test the system info tool."""
    tool = SystemInfoTool()
    
    # Test with default parameters
    result = await tool.execute(info_type="all")
    
    assert result.success is True
    assert "System Information" in result.output
    assert "CPU" in result.output
    assert "MEMORY" in result.output
    assert "DISK" in result.output
    assert "PLATFORM" in result.output
    
    # Test with specific info type
    result = await tool.execute(info_type="cpu")
    
    assert result.success is True
    assert "CPU" in result.output
    assert "MEMORY" not in result.output


@pytest.mark.asyncio
async def test_file_operations_tool():
    """Test the file operations tool."""
    tool = FileOperationsTool()
    
    # Test write operation
    write_result = await tool.execute(
        operation="write",
        path="test_file.txt",
        content="Hello, world!"
    )
    
    assert write_result.success is True
    
    # Test read operation
    read_result = await tool.execute(
        operation="read",
        path="test_file.txt"
    )
    
    assert read_result.success is True
    assert "Hello, world!" in read_result.output
    
    # Test exists operation
    exists_result = await tool.execute(
        operation="exists",
        path="test_file.txt"
    )
    
    assert exists_result.success is True
    assert exists_result.data["exists"] is True
    
    # Test delete operation
    delete_result = await tool.execute(
        operation="delete",
        path="test_file.txt"
    )
    
    assert delete_result.success is True
    
    # Verify file is deleted
    exists_result = await tool.execute(
        operation="exists",
        path="test_file.txt"
    )
    
    assert exists_result.success is True
    assert exists_result.data["exists"] is False


@pytest.mark.asyncio
async def test_tool_registry():
    """Test the tool registry."""
    registry = ToolRegistry()
    
    # Register tools
    registry.register(SystemInfoTool())
    registry.register(FileOperationsTool())
    
    # Test listing tools
    tools = registry.list_tools()
    assert "system_info" in tools
    assert "file_operations" in tools
    
    # Test getting a tool
    system_tool = registry.get("system_info")
    assert system_tool is not None
    assert system_tool.name == "system_info"
    
    # Test executing a tool
    result = await registry.execute("system_info", info_type="platform")
    assert result.success is True
    assert "PLATFORM" in result.output