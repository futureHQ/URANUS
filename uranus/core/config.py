import os
import threading
import tomllib
from pathlib import Path
from typing import Dict, Any, Optional

from pydantic import BaseModel


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent.parent


class LLMSettings(BaseModel):
    """Settings for LLM."""
    model: str
    base_url: str
    api_key: str
    max_tokens: int = 4096
    temperature: float = 0.7
    api_type: str = "openai"


class Config:
    """Configuration singleton for Uranus."""
    
    _instance: Optional["Config"] = None
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the configuration."""
        if self._initialized:
            return
            
        self._config = self._load_initial_config()
        self._initialized = True
    
    def _get_config_path(self) -> Path:
        """Get the configuration file path."""
        # Check for config in environment variable
        config_path_env = os.environ.get("URANUS_CONFIG")
        if config_path_env:
            return Path(config_path_env)
            
        # Check for config in project root
        project_root = get_project_root()
        config_path = project_root / "config" / "config.toml"
        if config_path.exists():
            return config_path
            
        # Fall back to example config
        return project_root / "config" / "config.example.toml"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        config_path = self._get_config_path()
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    
    def _load_initial_config(self) -> Dict[str, Any]:
        """Load initial configuration."""
        try:
            return self._load_config()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return {
                "llm": {
                    "default": {
                        "model": "gpt-3.5-turbo",
                        "base_url": "https://api.openai.com/v1",
                        "api_key": os.environ.get("OPENAI_API_KEY", ""),
                        "max_tokens": 4096,
                        "temperature": 0.7,
                        "api_type": "openai"
                    }
                }
            }
    
    @property
    def llm(self) -> Dict[str, Dict[str, Any]]:
        """Get LLM configuration."""
        return self._config.get("llm", {})