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

    # # Create function handler for booking
    # @function_tool
    # async def handle_book_room(
    #     self,
    #     context: RunContext,
    #     guest_name: str,
    #     check_in_date: str,
    #     check_out_date: str,
    #     number_of_guests: int,
    #     room_type: str = "Standard",
    #     contact_phone: str = "",
    #     contact_email: str = "",
    #     special_requests: str = ""
    # ) -> str:
    #     """Handle room booking function call."""
    #     LOGGER.info(f"Processing room booking for {guest_name}")
    #     result = book_room(
    #         guest_name=guest_name,
    #         check_in_date=check_in_date,
    #         check_out_date=check_out_date,
    #         number_of_guests=number_of_guests,
    #         room_type=room_type,
    #         contact_phone=contact_phone,
    #         contact_email=contact_email,
    #         special_requests=special_requests
    #     )
    #     if result["success"]:
    #         LOGGER.info(f"Booking successful: {result.get('booking_id')}")
    #         return result["message"]
    #     else:
    #         LOGGER.error(f"Booking failed: {result.get('error')}")
    #         return f"I apologize, but there was an issue: {result.get('error', 'Unknown error')}. Please try again."
        

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

            # Join the room and connect to the user
            await self.ctx.connect()
            LOGGER.info("Connected to room successfully")
        except Exception as e:
            LOGGER.error(f"Failed to start agent session: {e}", exc_info=True)
            raise
