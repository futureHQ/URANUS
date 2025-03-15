# 🍑🚀 URANUS (Unified Reasoning, Adaptive Neural-linguistic Understanding System)

URANUS (Unified Reasoning, Adaptive Neural-linguistic Understanding System) is a next-generation AI agent that doesn’t just think—it delivers tangible, real-world results. By harnessing advanced reasoning and language capabilities, URANUS excels at a wide array of tasks in both work and personal life, freeing you to focus on what truly matters. From automating your daily to-dos to driving complex decision-making, URANUS bridges the gap between thought and action—quietly executing behind the scenes so you can rest assured everything is getting done.

Inspired by Manus.im, ANUS (Autonomous Networked Utility System) and OpenManus.

WIP

## Features

- **Reactive Agent Architecture**: Respond to user inputs and execute appropriate actions
- **Tool Integration**: Seamlessly integrate with various tools including:
  - System information retrieval
  - File operations (create, read, write, list)
  - Web browsing and search
  - Terminal command execution
  - Python code execution
  - Advanced browser interactions via browser_use
- **Memory Management**: Maintain conversation history and context
- **Extensible Design**: Easily add new tools and capabilities

## Installation

1. Clone the repository:
```bash
git clone https://github.com/futurehq/uranus.git
cd uranus
```

2. Install dependencies:
```bash
pip install -r uranus/requirements.txt
```

3. Run the application:
```bash
python -m uranus.main
```

## Usage

### Basic Commands

- **System Information**: "system status", "system info"
- **Web Search**: "search [query]"
- **Web Navigation**: "navigate to [url]" or "go to [url]"
- **Terminal Commands**: Execute commands like "ls", "pwd", "echo hello", etc.
- **File Operations**: 
  - "list file [path]" or simply "ls"
  - "create file [filename]" or "make a file [filename]"
- **Browser Interactions**:
  - "browser.open_url [url]" - Open a URL in the browser

### Advanced Browser Interactions

OpenManus includes integration with the browser_use library for advanced browser automation:

```python
# Example of using browser_use tool
browser_use.navigate https://example.com
browser_use.click 5  # Click the 5th element on the page
browser_use.input_text 3 "Hello world"  # Input text into the 3rd element
```
