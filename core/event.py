import time

class Event:

    def __init__(self, type, payload=None, source=None):

        self.type = type
        self.payload = payload
        self.source = source
        self.timestamp = time.time()