import webrtcvad


class SpeechActivityDetector:

    def __init__(self):

        self.vad = webrtcvad.Vad(2)

    def is_speech(self, audio_chunk, sample_rate=16000):

        return self.vad.is_speech(audio_chunk, sample_rate)