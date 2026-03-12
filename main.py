import asyncio

from core.event_bus import EventBus
from core.event import Event
from core.events import Events
from core.config import config
from core.logger import logger

from llm.conversation_engine import ConversationEngine
from permissions.permission_engine import PermissionEngine

from interrupt.speech_state import SpeechState
from interrupt.interrupt_controller import InterruptController
from interrupt.tts_controller import TTSController
from tts.coqui_engine import TTSEngine

from listener.backchannel_engine import BackchannelEngine

from tools.register_tools import register_tools
from tools.tool_executor import ToolExecutor
from core.response_builder import ResponseBuilder

from model_manager.model_manager import ModelManager


async def main():

    bus = EventBus()

    registry = register_tools()

    BackchannelEngine(bus)

    speech_state = SpeechState()

    tts_engine = TTSEngine()

    InterruptController(bus, speech_state)

    TTSController(bus, tts_engine, speech_state)

    ConversationEngine(bus)

    PermissionEngine(bus)

    ToolExecutor(bus, registry)

    ResponseBuilder(bus)

    manager = ModelManager()


    model_paths = manager.ensure_models()

    logger.info(f"Model paths: {model_paths}")

    logger.info("VoiceOS started.")

    while True:

        text = input("You: ")

        await bus.publish(
            Event(
                Events.SPEECH_TRANSCRIBED,
                {"text": text},
                "cli"
            )
        )


asyncio.run(main())