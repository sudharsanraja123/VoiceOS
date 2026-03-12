from TTS.api import TTS


class TTSEngine:

    def __init__(self):

        self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

    def speak(self, text):

        self.tts.tts_to_file(text=text, file_path="response.wav")