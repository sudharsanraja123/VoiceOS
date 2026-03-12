from TTS.api import TTS


class StreamingTTS:

    def __init__(self):

        self.tts = TTS(
            model_name="tts_models/en/ljspeech/tacotron2-DDC"
        )

    def speak_stream(self, token_stream):

        sentence = ""

        for token in token_stream:

            sentence += token

            if token.endswith(".") or token.endswith("?"):

                self.tts.tts_to_file(
                    text=sentence,
                    file_path="temp.wav"
                )

                self.play_audio("temp.wav")

                sentence = ""

    def play_audio(self, file):

        import os

        os.system(f"aplay {file}")