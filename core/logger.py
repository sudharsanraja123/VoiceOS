import logging
import os
from datetime import datetime


class VoiceOSLogger:
    def __init__(self, name="VoiceOS"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)


# Global logger instance
logger = VoiceOSLogger()