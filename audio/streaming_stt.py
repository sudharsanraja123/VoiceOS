from faster_whisper import WhisperModel
from core.events import Events
from core.event import Event


class StreamingSTT:

    def __init__(self, event_bus):

        self.model = WhisperModel("base")
        self.event_bus = event_bus

    async def transcribe(self, audio_chunk):

        segments, _ = self.model.transcribe(audio_chunk)

        for segment in segments:

            text = segment.text

            await self.event_bus.publish(
                Event(
                    Events.SPEECH_TRANSCRIBED,
                    {"text": text},
                    "stt_engine"
                )
            )