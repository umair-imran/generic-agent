from typing import Optional, Literal
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import BaseModel, model_validator, Field

from utils.logger import LOGGER
from utils import load_yaml

def load():    
    LOGGER.info("Attempting to load from .env.{PROD | LOCAL} file")
    # 1. Try local .env
    env_file_prod = Path(".env.prod")
    env_file_local = Path(".env.local")
    if env_file_prod.exists() | env_file_local.exists():
        return

    raise Exception('Unable to load secrets')

class OpenAISettings(BaseSettings):
    OPENAI_API_KEY: str
    class Config:
        env_file = '.env.prod', '.env.local'
        extra = "ignore"

    @classmethod
    def load(cls) -> "OpenAISettings":
        secrets = load()
        if secrets:
            return cls(**secrets)
        else:
            return cls()

class DeepGramSettings(BaseSettings):
    DEEPGRAM_API_KEY: str
    class Config:
        env_file = '.env.prod', '.env.local'
        extra = "ignore"

    @classmethod
    def load(cls) -> "DeepGramSettings":
        secrets = load()
        if secrets:
            return cls(**secrets)
        else:
            return cls()
        
class CartesiaSettings(BaseSettings):
    CARTESIA_API_KEY: str
    class Config:
        env_file = '.env.prod', '.env.local'
        extra = "ignore"

    @classmethod
    def load(cls) -> "CartesiaSettings":
        secrets = load()
        if secrets:
            return cls(**secrets)
        else:
            return cls()

class LLMSettings(BaseModel):
    type: Literal['openai'] = Field(..., exclude=True)
    model: str
    temperature: float = Field(default=0.3)
    __settings: Optional[OpenAISettings] = None
    # verbose: bool = True

    @model_validator(mode="after")
    def check_keys(self):
        if not self.API_KEY:
            raise ValueError("OPENAI_API_KEY is required!")
        return self

    @property
    def API_KEY(self):
        if not self.__settings:
            self.__settings = OpenAISettings.load()
        return self.__settings.OPENAI_API_KEY


class STTDeepGramSettings(BaseModel):
    type: Literal["deepgram"] = Field(..., exclude=True)
    model: str
    language: Literal["en", "multi"]
    base_url: str = Field(default="https://api.deepgram.com/v1/listen")
    __settings: Optional[DeepGramSettings] = None

    @model_validator(mode="after")
    def check_keys(self):
        if not self.API_KEY:
            raise ValueError("DEEPGRAM_API_KEY is required!")
        return self

    @property
    def API_KEY(self):
        if not self.__settings:
            self.__settings = DeepGramSettings.load()
        return self.__settings.DEEPGRAM_API_KEY
    
class TTSCartesiaSettings(BaseModel):
    type: Literal["cartesia"] = Field(..., exclude=True)
    model: str
    language: Literal["en"]
    voice: str = Field(default="6f84f4b8-58a2-430c-8c79-688dad597532")
    base_url: str = Field(default="https://api.cartesia.ai")
    __settings: Optional[CartesiaSettings] = None

    @model_validator(mode="after")
    def check_keys(self):
        if not self.API_KEY:
            raise ValueError("CARTESIA_API_KEY is required!")
        return self

    @property
    def API_KEY(self):
        if not self.__settings:
            self.__settings = CartesiaSettings.load()
        return self.__settings.CARTESIA_API_KEY


class LiveKitSettings(BaseSettings):
    """LiveKit server configuration."""
    LIVEKIT_URL: str = Field(..., description="LiveKit server WebSocket URL")
    LIVEKIT_API_KEY: str = Field(..., description="LiveKit API key")
    LIVEKIT_API_SECRET: str = Field(..., description="LiveKit API secret")
    
    class Config:
        env_file = '.env.prod', '.env.local'
        extra = "ignore"
    
    @classmethod
    def load(cls) -> "LiveKitSettings":
        """Load LiveKit settings from environment."""
        return cls()


class ApplicationSettings(BaseModel):
    llm: LLMSettings
    stt: STTDeepGramSettings
    tts: TTSCartesiaSettings
    livekit: Optional[LiveKitSettings] = None
    
    @classmethod
    def from_cfg(cls, cfg: str | dict) -> "ApplicationSettings":
        if isinstance(cfg, str):
            cfg = load_yaml(cfg)
        settings = cls(**cfg)
        # Load LiveKit settings from environment
        try:
            settings.livekit = LiveKitSettings.load()
        except Exception as e:
            LOGGER.warning(f"Failed to load LiveKit settings: {e}")
        return settings