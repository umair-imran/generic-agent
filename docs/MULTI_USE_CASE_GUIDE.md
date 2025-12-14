# Multi-Use Case Guide

This guide explains how to use the dynamic, multi-use-case agent system that supports different domains like hospitality, medical, education, and HR.

## Overview

The system has been refactored to support multiple use cases through configuration. You can easily switch between different use cases by changing a single setting in the configuration file.

## Supported Use Cases

- **Hospitality**: Hotel booking and guest services
- **Medical**: Appointment scheduling and medical inquiries
- **Education**: Student enrollment and academic services
- **HR**: Leave requests and human resources services

## Quick Start

### 1. Switch Use Cases

Edit `config/config.yml` and change the `use_case` field:

```yaml
use_case_settings:
  use_case: hospitality  # Change to: medical, education, or hr
```

### 2. Configure Use Case Settings

Each use case has its own configuration in `config/config.yml`:

```yaml
use_cases:
  hospitality:
    name: "Hospitality Assistant"
    greeting: "Assalamu alaikum! Welcome to Al Faisaliah Grand Hotel..."
    mcp_servers:
      - url: "http://localhost:8001/sse"
        name: "booking_server"
    prompt_file: "config/prompts/hospitality.yaml"
```

### 3. Customize Prompts

Edit the prompt files in `config/prompts/`:
- `config/prompts/hospitality.yaml`
- `config/prompts/medical.yaml`
- `config/prompts/education.yaml`
- `config/prompts/hr.yaml`

Each file contains a `prompt` field with the system instructions for that use case.

## Architecture

### Key Components

1. **GenericAgent**: A generic agent class that works with any use case
2. **GenericAssistant**: A generic assistant that loads prompts and MCP servers dynamically
3. **PromptLoader**: Loads prompts from YAML files based on use case
4. **UseCaseConfig**: Configuration model for each use case

### File Structure

```
project/
├── config/
│   ├── config.yml              # Main config with use case selection
│   ├── prompts/
│   │   ├── hospitality.yaml     # Hospitality prompts
│   │   ├── medical.yaml         # Medical prompts
│   │   ├── education.yaml       # Education prompts
│   │   └── hr.yaml              # HR prompts
│   └── config.py                # Configuration models
├── modules/
│   ├── agent.py                 # GenericAgent, GenericAssistant
│   ├── prompt_loader.py         # Dynamic prompt loading
│   └── prompts.py               # Legacy (kept for backward compatibility)
├── mcp_server/
│   ├── booking_server.py        # Hospitality MCP server
│   └── [other use case servers] # Add more as needed
└── entrypoint.py                # Generic entrypoint
```

## Adding a New Use Case

### Step 1: Add Configuration

Edit `config/config.yml` and add your new use case:

```yaml
use_cases:
  your_use_case:
    name: "Your Use Case Name"
    greeting: "Your greeting message"
    mcp_servers:
      - url: "http://localhost:8005/sse"
        name: "your_server"
    prompt_file: "config/prompts/your_use_case.yaml"
```

### Step 2: Create Prompt File

Create `config/prompts/your_use_case.yaml`:

```yaml
prompt: |
  You are a helpful assistant for [your use case].
  
  Your instructions here...
```

### Step 3: Create MCP Server (Optional)

If your use case needs custom tools, create an MCP server:

```python
# mcp_server/your_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Your MCP", host="0.0.0.0", port=8005)

@mcp.tool()
def your_tool(param1: str, param2: int) -> str:
    """Your tool description."""
    # Your tool implementation
    return "Result"

if __name__ == "__main__":
    mcp.run(transport="sse")
```

### Step 4: Switch to Your Use Case

Update `config/config.yml`:

```yaml
use_case_settings:
  use_case: your_use_case
```

## MCP Server Configuration

Each use case can have multiple MCP servers. Configure them in `config.yml`:

```yaml
mcp_servers:
  - url: "http://localhost:8001/sse"
    name: "booking_server"
  - url: "http://localhost:8002/sse"
    name: "payment_server"
```

The agent will automatically connect to all configured MCP servers.

## Backward Compatibility

The old class names (`HospitalityAgent`, `HospitalityAssistant`) are still available as aliases for backward compatibility:

```python
from modules.agent import HospitalityAssistant  # Still works!
# This is actually GenericAssistant under the hood
```

## Configuration Options

### Use Case Settings

- `use_case`: The active use case (hospitality, medical, education, hr)
- `use_cases`: Dictionary of all use case configurations

### Use Case Config

- `name`: Display name for the use case
- `greeting`: Initial greeting message
- `mcp_servers`: List of MCP server configurations
- `prompt_file`: Path to the prompt YAML file

## Troubleshooting

### Prompt File Not Found

If you see an error about a missing prompt file:
1. Check that the file exists in `config/prompts/`
2. Verify the path in `config.yml` is correct
3. Ensure the YAML file has a `prompt` key

### MCP Server Connection Issues

If MCP servers fail to connect:
1. Ensure the MCP server is running
2. Check the URL in `config.yml` matches the server
3. Verify the server is accessible (check firewall/network)

### Use Case Not Found

If you get a "use case not found" error:
1. Verify the use case name in `config.yml` matches one in `use_cases`
2. Check for typos in the use case name
3. Ensure the use case is properly configured

## Examples

### Example 1: Switch to Medical Use Case

1. Edit `config/config.yml`:
   ```yaml
   use_case_settings:
     use_case: medical
   ```

2. Start your MCP server (if needed):
   ```bash
   python mcp_server/appointment_server.py
   ```

3. Start the agent:
   ```bash
   python entrypoint.py
   ```

### Example 2: Custom Use Case

1. Create `config/prompts/custom.yaml`:
   ```yaml
   prompt: |
     You are a custom assistant...
   ```

2. Add to `config/config.yml`:
   ```yaml
   use_cases:
     custom:
       name: "Custom Assistant"
       greeting: "Hello! I'm a custom assistant."
       mcp_servers: []
       prompt_file: "config/prompts/custom.yaml"
   ```

3. Set active use case:
   ```yaml
   use_case_settings:
     use_case: custom
   ```

## Best Practices

1. **Keep prompts focused**: Each prompt should be specific to its use case
2. **Use descriptive names**: Make use case names clear and meaningful
3. **Organize MCP servers**: Group related tools in the same MCP server
4. **Test configurations**: Verify each use case works before deploying
5. **Document custom use cases**: Add comments in config files for clarity

## Migration from Old System

If you're migrating from the old hospitality-only system:

1. Your existing code will continue to work (backward compatibility)
2. The old `HospitalityAssistant` class is now an alias for `GenericAssistant`
3. Prompts are now loaded from YAML files instead of Python files
4. MCP server URLs are now configured in `config.yml` instead of hardcoded

No code changes are required for existing implementations!





