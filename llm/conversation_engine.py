from core.events import Events
from core.event import Event

from llm.llm_client import LLMClient
from llm.prompt_templates import SYSTEM_PROMPT
from llm.reasoning_parser import ReasoningParser


class ConversationEngine:

    def __init__(self, event_bus):

        self.event_bus = event_bus
        self.llm = LLMClient()
        self.parser = ReasoningParser()
        self.history = []

        event_bus.subscribe(
            Events.SPEECH_TRANSCRIBED,
            self.handle_user_input
        )

    async def handle_user_input(self, event):

        user_text = event.payload["text"]

        self.history.append(user_text)

        prompt = SYSTEM_PROMPT + "\nUser command:\n" + user_text

        llm_output = self.llm.generate(prompt)

        decision = self.parser.parse(llm_output)

        print("\nAssistant reasoning:")
        print(decision["reasoning"])

        await self.event_bus.publish(
            Event(
                Events.LLM_DECISION,
                decision,
                "conversation_engine"
            )
        )