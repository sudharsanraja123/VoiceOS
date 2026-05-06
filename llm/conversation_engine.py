from core.events.events import Events
from core.event import Event
from core.logger import logger

from llm.llm_client import LLMClient
from llm.prompt_templates import SYSTEM_PROMPT
from llm.reasoning_parser import ReasoningParser
from memory.memory_manager import MemoryManager
from environment.context_detector import ContextDetector


class ConversationEngine:

    def __init__(self, event_bus):

        self.event_bus = event_bus
        self.llm = LLMClient()
        self.parser = ReasoningParser()
        self.history = []
        self.memory = MemoryManager()
        self.context = ContextDetector()


        event_bus.subscribe(
            Events.SPEECH_TRANSCRIBED,
            self.handle_user_input
        )

    async def handle_user_input(self, event):

        user_text = event.payload["text"]

        self.history.append(user_text)
        self.memory.store(user_text)
        context = self.context.get_context()

        prompt = SYSTEM_PROMPT + "\nUser command:\n" + user_text

        memories = self.memory.retrieve(user_text)

        llm_output = self.llm.generate(prompt)

        decision = self.parser.parse(llm_output)

        logger.info("\nAssistant reasoning:")
        logger.info(decision["reasoning"])

        await self.event_bus.publish(
            Event(
                Events.LLM_DECISION,
                decision,
                "conversation_engine"
            )
        )