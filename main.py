import asyncio

from core.event_bus import EventBus

from llm.conversation_engine import ConversationEngine
from permissions.permission_engine import PermissionEngine


async def main():

    bus = EventBus()

    ConversationEngine(bus)

    PermissionEngine(bus)

    print("VoiceOS started.")

    while True:

        text = input("You: ")

        await bus.publish(
            Event(
                "speech_transcribed",
                {"text": text},
                "cli"
            )
        )


asyncio.run(main())