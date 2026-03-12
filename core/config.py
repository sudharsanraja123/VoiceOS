import os
from pathlib import Path
from typing import Optional


class Config:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.load_env()
    
    def load_env(self):
        env_file = self.project_root / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    @property
    def llm_endpoint(self) -> str:
        return os.getenv('LLM_ENDPOINT', 'http://localhost:11434/api/generate')
    
    @property
    def llm_model(self) -> str:
        return os.getenv('LLM_MODEL', 'mistral')
    
    @property
    def tts_output_path(self) -> str:
        return os.getenv('TTS_OUTPUT_PATH', str(self.project_root / 'output' / 'response.wav'))
    
    @property
    def models_directory(self) -> str:
        return os.getenv('MODELS_DIRECTORY', str(self.project_root / 'models'))
    
    @property
    def log_level(self) -> str:
        return os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def whisper_model(self) -> str:
        return os.getenv('WHISPER_MODEL', 'base')
    
    @property
    def tts_model(self) -> str:
        return os.getenv('TTS_MODEL', 'tts_models/en/ljspeech/tacotron2-DDC')
    
    @property
    def max_ram_threshold(self) -> int:
        return int(os.getenv('MAX_RAM_THRESHOLD', '12'))
    
    def ensure_output_directory(self):
        output_dir = Path(self.tts_output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()