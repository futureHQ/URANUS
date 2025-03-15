"""System utilities for Uranus."""
import os
import platform
import subprocess
from typing import Dict, Any, List, Optional, Tuple, Union


def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information.
    
    Returns:
        Dictionary with system information
    """
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
    }


def run_command(
    command: Union[str, List[str]],
    shell: bool = False,
    timeout: Optional[int] = None,
    cwd: Optional[str] = None
) -> Tuple[int, str, str]:
    """
    Run a system command and return the result.
    
    Args:
        command: Command to run (string or list of arguments)
        shell: Whether to run the command in a shell
        timeout: Timeout in seconds
        cwd: Working directory for the command
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=shell,
            cwd=cwd,
            universal_newlines=True
        )
        
        stdout, stderr = process.communicate(timeout=timeout)
        return_code = process.returncode
        
        return return_code, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def is_command_available(command: str) -> bool:
    """
    Check if a command is available in the system PATH.
    
    Args:
        command: Command to check
        
    Returns:
        True if the command is available, False otherwise
    """
    try:
        subprocess.run(
            ["which", command] if platform.system() != "Windows" else ["where", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_environment_variables() -> Dict[str, str]:
    """
    Get all environment variables.
    
    Returns:
        Dictionary of environment variables
    """
    return dict(os.environ)


def get_memory_usage() -> Dict[str, Any]:
    """
    Get memory usage information for the current process.
    
    Returns:
        Dictionary with memory usage information
    """
    import psutil
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "rss": memory_info.rss,  # Resident Set Size
        "vms": memory_info.vms,  # Virtual Memory Size
        "rss_mb": memory_info.rss / (1024 * 1024),  # RSS in MB
        "vms_mb": memory_info.vms / (1024 * 1024),  # VMS in MB
    }