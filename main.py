"""Main entry point for the hospitality bot application."""
import argparse
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables before importing LiveKit
env_file = Path(".env.local")
if not env_file.exists():
    env_file = Path(".env.prod")
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()

from livekit.agents import cli, WorkerOptions

from config import ApplicationSettings
from utils.logger import LOGGER


def run_fastapi(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server for agent management."""
    LOGGER.info(f"Starting FastAPI server on {host}:{port}")
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        log_level="info",
        reload=False
    )


def run_agent():
    """Run the LiveKit agent entrypoint."""
    from entrypoint import entrypoint
    LOGGER.info("Starting LiveKit agent entrypoint")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


def main():
    """Main function with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Hospitality Bot - LiveKit Agent and API Server"
    )
    parser.add_argument(
        "mode",
        choices=["agent", "api"],
        help="Run mode: 'agent' for LiveKit agent, 'api' for FastAPI server"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for FastAPI server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for FastAPI server (default: 8000)"
    )
    
    args = parser.parse_args()
    
    try:
        # Validate configuration can be loaded
        settings = ApplicationSettings.from_cfg('config/config.yml')
        LOGGER.info("Configuration loaded successfully")
        
        if args.mode == "agent":
            run_agent()
        elif args.mode == "api":
            run_fastapi(host=args.host, port=args.port)
    except Exception as e:
        LOGGER.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()