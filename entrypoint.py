"""LiveKit agent entrypoint - works with any use case."""
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables BEFORE importing LiveKit
# LiveKit reads LIVEKIT_API_KEY and LIVEKIT_API_SECRET during initialization
env_file = Path(".env.local")
if not env_file.exists():
    env_file = Path(".env.prod")
if env_file.exists():
    load_dotenv(env_file, override=True)
else:
    # Fallback to default .env loading
    load_dotenv(override=True)

from livekit.agents import JobContext
from livekit.agents import cli, WorkerOptions
from livekit.plugins import silero

from config import ApplicationSettings
from modules.agent import GenericAssistant, HospitalityAssistant  # Backward compatibility
from utils.logger import LOGGER

async def entrypoint(ctx: JobContext):
    """
    Entrypoint function for LiveKit agent - works with any use case.
    This function is called when a new job starts.
    """
    try:
        # Load configuration
        settings = ApplicationSettings.from_cfg('config/config.yml')
        use_case = settings.use_case_settings.use_case
        use_case_name = settings.current_use_case.name
        
        LOGGER.info(f"Starting {use_case_name} for room: {ctx.room.name} (use case: {use_case})")
        
        # Initialize VAD (Voice Activity Detection) and store in userdata
        # This is required by the agent session
        vad = silero.VAD.load()
        ctx.proc.userdata["vad"] = vad
        
        # Create and start the assistant (works for any use case)
        assistant = GenericAssistant(cfg=settings, ctx=ctx)
        await assistant.start()
        
        LOGGER.info(f"{use_case_name} started successfully for room: {ctx.room.name}")
        
    except Exception as e:
        LOGGER.error(f"Failed to start assistant: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Run the agent with LiveKit CLI
    # The entrypoint function will be called for each new job
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

