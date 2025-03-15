import pytest
import os
import tempfile
from pathlib import Path
from uranus.core.config import Config


def test_config_singleton():
    """Test that Config is a singleton."""
    config1 = Config()
    config2 = Config()
    
    assert config1 is config2


def test_config_llm():
    """Test that Config.llm returns the LLM configuration."""
    config = Config()
    
    # The default config should have an LLM section
    llm_config = config.llm
    assert isinstance(llm_config, dict)
    
    # The default config should have a default LLM
    default_llm = llm_config.get("default")
    assert default_llm is not None
    assert "model" in default_llm
    assert "api_key" in default_llm