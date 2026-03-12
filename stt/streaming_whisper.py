from faster_whisper import WhisperModel
from core.config import config
from core.logger import logger


class StreamingWhisper:

    def __init__(self):

        self.model = WhisperModel(
            config.whisper_model,
            device="cpu",
            compute_type="int8"
        )

    def transcribe_stream(self, audio_chunks):

        partial_text = ""

        for chunk in audio_chunks:

            segments, _ = self.model.transcribe(
                chunk,
                beam_size=1
            )

            for segment in segments:

                partial_text += segment.text

                yield partial_text