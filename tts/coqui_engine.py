from TTS.api import TTS
from core.config import config
from core.logger import logger


class TTSEngine:

    def __init__(self):

        self.tts = TTS(model_name=config.tts_model)
        config.ensure_output_directory()

    def speak(self, text):

        self.tts.tts_to_file(text=text, file_path=config.tts_output_path)