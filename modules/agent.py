from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    AgentFalseInterruptionEvent,
    NOT_GIVEN,
    RoomInputOptions
)
from livekit.plugins import (
    openai,
    deepgram,
    cartesia,
    noise_cancellation
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from config import ApplicationSettings
from modules import prompts
from utils.logger import LOGGER

class HospitalityAssistant:
    def __init__(self, cfg: ApplicationSettings, ctx: JobContext) -> None:
        self.cfg = cfg
        self.agent = Agent(instructions=prompts.DEFAULT_ASSISTANT_PROMPT)
        self.ctx = ctx

        # Add any other context you want in all log entries here
        self.ctx.log_context_fields = {
            "room": ctx.room.name,
        }

        self.session = AgentSession(
            llm=openai.LLM(api_key=self.cfg.llm.API_KEY,
                           **self.cfg.llm.model_dump()),
            stt=deepgram.STT(api_key=self.cfg.stt.API_KEY,
                             **self.cfg.stt.model_dump()),
            tts=cartesia.TTS(api_key=self.cfg.tts.API_KEY,
                             **self.cfg.tts.model_dump()),
            turn_detection=MultilingualModel(),
            vad=ctx.proc.userdata["vad"],
            preemptive_generation=True,
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
