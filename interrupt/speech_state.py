import threading


class SpeechState:

    def __init__(self):

        self.user_speaking = False
        self.lock = threading.Lock()

    def set_user_speaking(self, value: bool):

        with self.lock:
            self.user_speaking = value

    def is_user_speaking(self):

        with self.lock:
            return self.user_speaking