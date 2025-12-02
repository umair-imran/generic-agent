"""LiveKit agent entrypoint for the hospitality assistant."""
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
from modules.agent import HospitalityAssistant
from utils.logger import LOGGER

async def entrypoint(ctx: JobContext):
    """
    Entrypoint function for LiveKit agent.
    This function is called when a new job starts.
    """
    try:
        LOGGER.info(f"Starting hospitality assistant for room: {ctx.room.name}")
        
        # Load configuration
        settings = ApplicationSettings.from_cfg('config/config.yml')
        
        # Initialize VAD (Voice Activity Detection) and store in userdata
        # This is required by the agent session
        vad = silero.VAD.load()
        ctx.proc.userdata["vad"] = vad
        
        # Create and start the hospitality assistant
        assistant = HospitalityAssistant(cfg=settings, ctx=ctx)
        await assistant.start()
        
        LOGGER.info(f"Hospitality assistant started successfully for room: {ctx.room.name}")
        
    except Exception as e:
        LOGGER.error(f"Failed to start hospitality assistant: {e}")
        raise


if __name__ == "__main__":
    # Run the agent with LiveKit CLI
    # The entrypoint function will be called for each new job
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

