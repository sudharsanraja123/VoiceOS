import threading
from core.events import Events
from core.event import Event
from core.logger import logger


class TTSController:

    def __init__(self, bus, tts_engine, speech_state):

        self.bus = bus
        self.tts = tts_engine
        self.state = speech_state

        self.current_thread = None

        bus.subscribe(
            Events.TTS_SPEAK,
            self.handle_tts
        )

    async def handle_tts(self, event):

        text = event.payload["text"]
        priority = event.payload.get("priority", "high")

        # If user speaking, skip low priority responses
        if self.state.is_user_speaking() and priority == "low":
            return

        # Stop current speech if user started talking
        if self.state.is_user_speaking():
            self.stop()

        self.start(text)

    def start(self, text):

        def speak():
            self.tts.speak(text)

        self.current_thread = threading.Thread(target=speak)
        self.current_thread.start()

    def stop(self):

        if self.current_thread and self.current_thread.is_alive():

            # In real system you'd signal the TTS engine to stop
            logger.info("TTS interrupted due to user speech.")