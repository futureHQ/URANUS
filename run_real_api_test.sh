#!/bin/bash

# Get the API key from the config file
API_KEY=$(grep -o 'api_key = "[^"]*"' config/config.example.toml | head -1 | cut -d'"' -f2)

# Run the test with the API key
OPENAI_API_KEY=$API_KEY python3 -m pytest tests/test_with_real_api.py -v