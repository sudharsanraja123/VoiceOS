from core.events.events import Events
from listener.speech_activity import SpeechActivityDetector


class InterruptController:

    def __init__(self, event_bus, speech_state):

        self.bus = event_bus
        self.speech_state = speech_state

        self.vad = SpeechActivityDetector()

        event_bus.subscribe(
            Events.MIC_AUDIO,
            self.detect_user_speech
        )

    async def detect_user_speech(self, event):

        audio_chunk = event.payload["audio"]

        speaking = self.vad.is_speech(audio_chunk)

        if speaking:
            self.speech_state.set_user_speaking(True)
        else:
            self.speech_state.set_user_speaking(False)