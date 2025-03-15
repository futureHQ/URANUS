#!/usr/bin/env python3
"""
Test runner for Uranus.
"""
import os
import sys
import subprocess
import pytest


def ensure_dependencies():
    """Ensure all test dependencies are installed."""
    try:
        import pytest_asyncio
    except ImportError:
        print("Installing pytest-asyncio...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest-asyncio"])


def main():
    """Run all tests."""
    # Add the current directory to the path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Ensure dependencies
    ensure_dependencies()
    
    # Run pytest with asyncio plugin
    sys.exit(pytest.main(["-xvs", "tests"]))


if __name__ == "__main__":
    main()