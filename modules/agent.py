import asyncio

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    AgentFalseInterruptionEvent,
    NOT_GIVEN,
    RoomInputOptions,
    RunContext,
    mcp
)
from livekit.agents.llm.tool_context import function_tool, ToolContext
from livekit.plugins import (
    openai,
    deepgram,
    cartesia,
    noise_cancellation
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from config import ApplicationSettings
from modules import prompts
# from mcp_server.tools import book_room, BOOK_ROOM_TOOL
from mcp_server import booking_server
from utils.logger import LOGGER

class HospitalityAgent(Agent):
    def __init__(self, instructions: str) -> None:
        super().__init__(instructions=instructions,
         mcp_servers=[mcp.MCPServerHTTP(url="http://localhost:8001/sse")]
         )

    async def on_enter(self):
        self.session.generate_reply()

class HospitalityAssistant:
    def __init__(self, cfg: ApplicationSettings, ctx: JobContext) -> None:
        self.cfg = cfg
        self.agent = HospitalityAgent(instructions=prompts.DEFAULT_ASSISTANT_PROMPT)
        self.ctx = ctx

        # Add any other context you want in all log entries here
        self.ctx.log_context_fields = {
            "room": ctx.room.name,
        }

        # Initialize LLM with function calling support
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
        # sometimes background noise could interrupt the agent session, these are considered false positive interruptions
        # when it's detected, you may resume the agent's speech
        @self.session.on("agent_false_interruption")
        def _on_agent_false_interruption(ev: AgentFalseInterruptionEvent):
            LOGGER.warning("False positive interruption, Resuming...")
            self.session.generate_reply(instructions=ev.extra_instructions or NOT_GIVEN)

    async def start(self):
        """Start the agent session and connect to the room."""
        try:
            LOGGER.info(f"Starting agent session for room: {self.ctx.room.name}")
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
            LOGGER.info("Agent session started successfully")

            # # Pre-warm TTS by generating a short test phrase
            # # This ensures TTS is ready before the first real message
            # try:
            #     LOGGER.info("Pre-warming TTS service...")
            #     # Generate a very short test phrase to warm up TTS
            #     await self.session.tts.synthesize("Hi")
            #     LOGGER.info("TTS service warmed up successfully")
            # except Exception as e:
            #     LOGGER.warning(f"TTS pre-warm failed (non-critical): {e}")
            #     # Don't fail the entire session if pre-warm fails
            
            # Small delay to allow TTS service to fully initialize
            # This prevents the first message TTS error
            await asyncio.sleep(1.0)  # 1 second delay to warm up TTS
            LOGGER.info("TTS warmup delay completed")

            # Join the room and connect to the user
            await self.ctx.connect()
            LOGGER.info("Connected to room successfully")
        except Exception as e:
            LOGGER.error(f"Failed to start agent session: {e}", exc_info=True)
            raise
