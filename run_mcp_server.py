"""Run MCP server based on configuration."""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_file = Path(".env.local")
if not env_file.exists():
    env_file = Path(".env.prod")
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()

from config import ApplicationSettings
from utils.logger import LOGGER

# Mapping of server names to module names
SERVER_MODULE_MAP = {
    "booking_server": "booking_server",
    "appointment_server": "appointment_server",
    "enrollment_server": "enrollment_server",
    "hr_server": "hr_server",
}


def get_mcp_server_module(server_name: str):
    """Dynamically import and return the MCP server module."""
    if server_name not in SERVER_MODULE_MAP:
        raise ValueError(
            f"Unknown MCP server: {server_name}. "
            f"Available servers: {list(SERVER_MODULE_MAP.keys())}"
        )
    
    module_name = SERVER_MODULE_MAP[server_name]
    try:
        # Dynamically import the module
        module = __import__(f"mcp_server.{module_name}", fromlist=[module_name])
        return module
    except ImportError as e:
        raise ImportError(
            f"Failed to import MCP server module '{module_name}': {e}"
        )


if __name__ == "__main__":
    try:
        # Load configuration
        settings = ApplicationSettings.from_cfg('config/config.yml')
        current_use_case = settings.current_use_case
        
        # Get the MCP server name from the current use case
        if not current_use_case.mcp_servers:
            raise ValueError(
                f"No MCP servers configured for use case: {settings.use_case_settings.use_case}"
            )
        
        # Use the first MCP server (typically there's only one per use case)
        mcp_server_config = current_use_case.mcp_servers[0]
        server_name = mcp_server_config.name
        
        LOGGER.info(
            f"Starting MCP server '{server_name}' for use case: "
            f"{settings.use_case_settings.use_case}"
        )
        print(f"🚀 Starting MCP server: {server_name}")
        print(f"   Use case: {settings.use_case_settings.use_case}")
        print(f"   URL: {mcp_server_config.url}")
        
        # Get and run the appropriate MCP server
        server_module = get_mcp_server_module(server_name)
        server_module.mcp.run(transport="sse")
        
    except Exception as e:
        LOGGER.error(f"Failed to start MCP server: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)