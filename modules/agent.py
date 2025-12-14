"""Generic agent implementation that works with any use case."""
import asyncio
from typing import List, Optional

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    AgentFalseInterruptionEvent,
    NOT_GIVEN,
    RoomInputOptions,
    mcp
)
from livekit.plugins import (
    openai,
    deepgram,
    cartesia,
    noise_cancellation
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from config import ApplicationSettings
from modules.prompt_loader import PromptLoader
from utils.logger import LOGGER


class GenericAgent(Agent):
    """Generic agent that can be configured for any use case."""
    
    def __init__(self, instructions: str, mcp_server_urls: Optional[List[str]] = None) -> None:
        """
        Initialize a generic agent.
        
        Args:
            instructions: The system instructions/prompt for the agent
            mcp_server_urls: Optional list of MCP server URLs to connect to
        """
        mcp_servers = []
        if mcp_server_urls:
            for url in mcp_server_urls:
                mcp_servers.append(mcp.MCPServerHTTP(url=url))
        
        super().__init__(
            instructions=instructions,
            mcp_servers=mcp_servers if mcp_servers else None
        )


class GenericAssistant:
    """Generic assistant that works with any use case configuration."""
    
    def __init__(self, cfg: ApplicationSettings, ctx: JobContext) -> None:
        """
        Initialize a generic assistant for any use case.
        
        Args:
            cfg: Application settings including use case configuration
            ctx: Job context from LiveKit
        """
        self.cfg = cfg
        self.ctx = ctx
        self.use_case_config = cfg.current_use_case
        
        # Load prompt dynamically based on use case
        try:
            prompt = PromptLoader.load_prompt(self.use_case_config.prompt_file)
            LOGGER.info(f"Loaded prompt from {self.use_case_config.prompt_file}")
        except Exception as e:
            LOGGER.error(f"Failed to load prompt, using fallback: {e}")
            # Fallback to a basic prompt if file loading fails
            prompt = f"You are a helpful assistant for {self.use_case_config.name}. {self.use_case_config.greeting}"
        
        # Get MCP server URLs from configuration
        mcp_urls = [server.url for server in self.use_case_config.mcp_servers]
        if mcp_urls:
            LOGGER.info(f"Connecting to {len(mcp_urls)} MCP server(s): {mcp_urls}")
        
        # Create generic agent with loaded prompt and MCP servers
        self.agent = GenericAgent(instructions=prompt, mcp_server_urls=mcp_urls)
        
        # Add context to logs
        self.ctx.log_context_fields = {
            "room": ctx.room.name,
            "use_case": cfg.use_case_settings.use_case,
            "use_case_name": self.use_case_config.name,
        }

        # Initialize session with LLM, STT, TTS
        self.session = AgentSession(
            llm=openai.LLM(api_key=self.cfg.llm.API_KEY,
                           **self.cfg.llm.model_dump()),
            stt=deepgram.STT(api_key=self.cfg.stt.API_KEY,
                             **self.cfg.stt.model_dump()),
            tts=cartesia.TTS(api_key=self.cfg.tts.API_KEY,
                             **self.cfg.tts.model_dump()),
            turn_detection=MultilingualModel(),
            vad=ctx.proc.userdata["vad"],
            preemptive_generation=True
        )

        # Add error handler for TTS errors
        @self.session.on("error")
        def _on_error(ev):
            if "no audio frames were pushed" in str(ev.error):
                LOGGER.warning(f"TTS error detected (likely first message): {ev.error}")
                # The session will retry automatically, so we just log it
            else:
                LOGGER.error(f"Session error: {ev.error}")
        
        # Handle false positive interruptions
        @self.session.on("agent_false_interruption")
        def _on_agent_false_interruption(ev: AgentFalseInterruptionEvent):
            LOGGER.warning("False positive interruption, Resuming...")
            self.session.generate_reply(instructions=ev.extra_instructions or NOT_GIVEN)

    async def start(self):
        """Start the agent session and connect to the room."""
        try:
            use_case_name = self.use_case_config.name
            LOGGER.info(f"Starting {use_case_name} for room: {self.ctx.room.name}")
            
            # Start the session, which initializes the voice pipeline and warms up the models
            await self.session.start(
                agent=self.agent,
                room=self.ctx.room,
                room_input_options=RoomInputOptions(
                    # LiveKit Cloud enhanced noise cancellation
                    # - If self-hosting, omit this parameter
                    # - For telephony applications, use `BVCTelephony` for best results
                    noise_cancellation=noise_cancellation.BVC(),
                ),
            )
            LOGGER.info(f"{use_case_name} session started successfully")

            # Small delay to allow TTS service to fully initialize
            # This prevents the first message TTS error
            await asyncio.sleep(1.0)  # 1 second delay to warm up TTS
            LOGGER.info("TTS warmup delay completed")

            # Join the room and connect to the user
            await self.ctx.connect()
            LOGGER.info("Connected to room successfully")
        except Exception as e:
            LOGGER.error(f"Failed to start {self.use_case_config.name}: {e}", exc_info=True)
            raise


# Backward compatibility: Keep old class names as aliases
HospitalityAgent = GenericAgent
HospitalityAssistant = GenericAssistant
