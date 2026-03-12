import time
from core.events import Events
from core.event import Event

from listener.response_selector import ResponseSelector


class BackchannelEngine:

    def __init__(self, event_bus):

        self.bus = event_bus

        self.selector = ResponseSelector()

        self.last_response = 0

        self.interval = 6

        event_bus.subscribe(
            Events.MIC_AUDIO,
            self.monitor_audio
        )

    async def monitor_audio(self, event):

        now = time.time()

        if now - self.last_response < self.interval:
            return

        response = self.selector.select()

        await self.bus.publish(
            Event(
                Events.TTS_SPEAK,
                {
                    "text": response,
                    "priority": "low"
                },
                "backchannel"
            )
        )

        self.last_response = now